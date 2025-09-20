# ui/app.py

# ---------------- Imports ----------------
import streamlit as st
import pandas as pd
import numpy as np
import time
import os
import sys
import json
import duckdb
import re
import uuid

# ---------------- Optional import path (for recommenders/) ----------------
CURRENT_DIR = os.path.dirname(__file__)
PARENT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
RECOMMENDERS_DIR = os.path.join(PARENT_DIR, "recommenders")
if RECOMMENDERS_DIR not in sys.path:
    sys.path.append(RECOMMENDERS_DIR)

# ---------------- Name -> ID map (safe if DuckDB missing) ----------------
def load_name_to_id():
    try_paths = [
        os.path.join(PARENT_DIR, "users.db"),
        os.path.join(PARENT_DIR, "data", "users.db"),
    ]
    for p in try_paths:
        if os.path.exists(p):
            try:
                con = duckdb.connect(p, read_only=True)
                rows = con.execute('SELECT id, "Full Name" FROM users').fetchall()
                con.close()
                return {name.strip(): uid for uid, name in rows}
            except Exception:
                pass
    return {}

name_to_id = load_name_to_id()

# ---------------- Feedback logging ----------------
def save_feedback(entry, filepath=os.path.join(PARENT_DIR, "feedback", "feedback_log.jsonl")):
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

# ---------------- Text helpers ----------------
NUM_LINE = re.compile(r"^\s*\d+[\.\)]\s+")

def extract_recommendation_lines(text: str, max_items: int = 3):
    """Keep only numbered lines like '1. ...', fallback to first non-empty lines."""
    lines = [ln.strip() for ln in (text or "").splitlines() if ln.strip()]
    numbered = [ln for ln in lines if NUM_LINE.match(ln)]
    base = numbered if numbered else lines
    return base[:max_items]

def parse_target_name(query: str) -> str:
    """Extract person name from prompts like 'find someone similar to Allison Hill'."""
    m = re.search(r"(?:like|similar to)\s+([A-Za-z][A-Za-z\.\- ]+)$", query.strip(), re.IGNORECASE)
    return (m.group(1).strip() if m else "")

def filter_out_original(lines, target_name):
    """Remove any line that mentions the original person's name."""
    if not target_name:
        return lines
    pat = re.compile(rf"\b{re.escape(target_name)}\b", re.IGNORECASE)
    return [ln for ln in lines if not pat.search(ln)]

def looks_like_person(line: str) -> bool:
    """Exclude meta notes like '(No third valid ...)' and keep person-like entries."""
    bad = [
        r"\bno third\b",
        r"\bno valid\b",
        r"\bexcluding\b",
        r"^\(?no\b",
        r"\bnot provided\b",
    ]
    return not any(re.search(pat, line, re.IGNORECASE) for pat in bad)

# ---------------- Feedback UI ----------------
def feedback_ui(query, results, name_to_id, recommended_ids=None):
    st.markdown("## Query Results & Feedback")
    recommended_ids = recommended_ids or []

    query_name = parse_target_name(query) or "Unknown"
    user_id = name_to_id.get(query_name, "unknown")

    for idx, row in enumerate(results, start=1):
        st.markdown(f"### Result {idx}")
        st.write(row)

        col1, col2 = st.columns([1, 3])
        with col1:
            thumbs = st.radio(f"Feedback_{idx}", ["👍", "👎"], key=f"thumbs_{idx}", horizontal=True)
        with col2:
            comment = st.text_input(f"Comment_{idx}", placeholder="Optional comment...", key=f"comment_{idx}")

        safe_query = query.replace(" ", "_").replace("?", "").replace(":", "").lower()
        submit_key = f"submit_{safe_query}_{idx}"
        submitted_key = f"submitted_{safe_query}_{idx}"

        if submitted_key not in st.session_state:
            st.session_state[submitted_key] = False

        if not st.session_state[submitted_key]:
            if st.button(f"Submit Feedback {idx}", key=f"submit_{idx}"):
                # Try to parse "Name — ..." or "Name - ..." for nicer reason extraction
                name_part = row.split("—", 1)[0].split("-", 1)[0].strip()
                description = (
                    row.split("—", 1)[1].strip() if "—" in row
                    else (row.split("-", 1)[1].strip() if "-" in row else "")
                )
                sentences = description.split(". ")
                reason = sentences[-1].strip() if len(sentences) > 1 else description

                rec_id = (
                    recommended_ids[idx - 1]
                    if (idx - 1) < len(recommended_ids)
                    else name_to_id.get(name_part, "unknown")
                )

                feedback_entry = {
                    "query": query,
                    "recommended_id": rec_id,
                    "rating": 1 if thumbs == "👍" else -1,
                    "reason": reason,
                    "comment": comment,
                }

                save_feedback(feedback_entry)
                st.session_state[submitted_key] = True
                st.success(f"Feedback submitted for {idx}. {name_part if name_part else ''}")
        else:
            st.button("Feedback Submitted ✅", key=submit_key, disabled=True)

# ---------------- Session init ----------------
if "query_counter" not in st.session_state:
    st.session_state.query_counter = 0
if "run_id" not in st.session_state:
    st.session_state.run_id = str(uuid.uuid4())
if "last_query" not in st.session_state:
    st.session_state.last_query = None
if "last_result" not in st.session_state:
    st.session_state.last_result = ""
if "rec_lines" not in st.session_state:
    st.session_state.rec_lines = []
if "target_name" not in st.session_state:
    st.session_state.target_name = ""
if "raw_results" not in st.session_state:
    st.session_state.raw_results = []
if "recommended_ids" not in st.session_state:
    st.session_state.recommended_ids = []

# ---------------- UI ----------------
st.title("Network recommendation")
st.write("Find people that you want from your network!")
st.markdown("---")

st.sidebar.header("AI network recommender")
sidebar_query = st.sidebar.text_input("Enter your query here:", placeholder="Type something...")
st.sidebar.write(f"Your query: {sidebar_query}")

st.header("Agent Response")

# ---------------- Agent call ----------------
if sidebar_query and sidebar_query != "Type something..." and sidebar_query != st.session_state.get("last_query"):
    with st.spinner(f"Asking the agent about: '{sidebar_query}'..."):
        try:
            # Import your agent from recommenders/
            from router_agent import agent  # file: recommenders/router_agent.py

            target_name = parse_target_name(sidebar_query)
            st.session_state["target_name"] = target_name

            # Nudge agent: 3 numbered lines, exclude the target person
            prompt = (
                sidebar_query
                + " | Return exactly 3 numbered lines in the format "
                  "'1. Full Name — Rationale: ...'. No headers or extra text. "
                  f"Exclude the original person '{target_name}' from the list."
            )
            agent_response = agent.invoke(prompt)
            st.session_state["last_query"] = sidebar_query

        except ImportError:
            st.error("Could not import router_agent. Please ensure 'recommenders/router_agent.py' exists and is correctly structured.")
            agent_response = {"output": "Error: Agent not found."}
        except Exception as e:
            st.error(f"An error occurred during agent invocation: {e}")
            agent_response = {"output": f"Error: {e}"}

    st.success("Agent processing complete!")

    # --- Start of corrected logic ---
    recommended_ids = []
    output_rows = []
    
    # Check if the agent's response is a dict and has intermediate steps.
    if isinstance(agent_response, dict):
        output = agent_response.get("output", "")
        # This handles the case where the agent returns a final answer as a string
        if "Final Answer:" in output:
            final_answer_text = output.split("Final Answer:", 1)[-1].strip()
            raw_lines = [line.strip() for line in final_answer_text.split("\n") if line.strip()]
        else:
            raw_lines = extract_recommendation_lines(output)

        # Extract IDs from raw results if available
        if "intermediate_steps" in agent_response:
            all_observations = []
            for action, observation in agent_response["intermediate_steps"]:
                if hasattr(action, "tool") and action.tool == "VectorTool" and isinstance(observation, list):
                    all_observations.extend(observation)
                    
            if all_observations:
                # Create a mapping from name to ID
                name_to_id_map = {
                    (p.payload.get('user_name', '') or '').strip(): (p.payload.get('user_id', '') or '').strip()
                    for p in all_observations if p.payload
                }
                
                # Align the IDs with the recommendation lines
                recommended_ids = []
                for line in raw_lines:
                    name_part = line.split("—")[0].split(".")[1].strip()
                    recommended_ids.append(name_to_id_map.get(name_part, "unknown"))
    else:
        # Fallback to the old method if intermediate steps aren't available.
        raw_lines = extract_recommendation_lines(str(agent_response))
        recommended_ids = []

    # Filter out the original person one more time, just in case the agent failed to do so.
    target_name = st.session_state.get("target_name", "")
    if target_name:
        filtered_lines = []
        filtered_ids = []
        for line, rec_id in zip(raw_lines, recommended_ids):
            if not re.search(rf"\b{re.escape(target_name)}\b", line, re.IGNORECASE):
                filtered_lines.append(line)
                filtered_ids.append(rec_id)
        output_rows = filtered_lines
        recommended_ids = filtered_ids
    else:
        output_rows = raw_lines

    final_lines = [ln for ln in output_rows if looks_like_person(ln)][:3]

    st.session_state["rec_lines"] = final_lines
    st.session_state["recommended_ids"] = recommended_ids
    st.session_state["last_result"] = "\n".join(final_lines)

    # --- End of corrected logic ---

    # Optional: show tools used if available
    if isinstance(agent_response, dict) and agent_response.get("intermediate_steps"):
        for action, _ in agent_response["intermediate_steps"]:
            if hasattr(action, "tool"):
                st.write(f"- Used tool: **{action.tool}**")
    else:
        st.info("No tools were explicitly used for this query, or intermediate steps are not available in this output.")

# ---------------- Render results + feedback ----------------
if st.session_state.get("last_result"):  # render whenever we have an agent result
    # Show the agent's raw answer text (so user sees the recommendations)
    st.markdown(st.session_state["last_result"])

    # Use cleaned, numbered lines (top 3) after filtering out the original person & notes
    output_rows = st.session_state.get("rec_lines", [])
    if len(output_rows) < 3:
        tn = st.session_state.get("target_name", "")
        st.info(
            f"Only {len(output_rows)} match(es){' after removing ' + tn if tn else ''}. "
            "Index more bios to improve coverage."
        )

    # Use the recommended_ids list from session state
    recommended_ids = st.session_state.get("recommended_ids", [])
    if output_rows:
        feedback_ui(
            st.session_state.get("last_query", sidebar_query),
            output_rows,
            name_to_id,
            recommended_ids=recommended_ids
        )

st.markdown("---")