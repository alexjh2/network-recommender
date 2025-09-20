from langchain.tools import Tool
from langchain.agents import initialize_agent
from langchain_openai import ChatOpenAI

import sys
import os
from dotenv import load_dotenv

# Load .env and environment variables
load_dotenv()
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from retrievers.sql import find_by_field_and_location
from retrievers.sql import run_duckdb_query
from retrievers.vector import find_similar_bios
from retrievers.graph import find_connections_2_hops

def parse_occupation_and_location(query):
    """
    Extracts occupation and location from a prompt like:
    "Find Software Engineers in San Jose"
    """
    import re
    match = re.search(r"(.*?)\s+in\s+(.*)", query, re.IGNORECASE)
    if match:
        occupation = match.group(1).strip().strip('"\'')
        location = match.group(2).strip().strip('"\'')
        return occupation, location
    else:
        raise ValueError("Query does not match expected format: 'Find [Occupation] in [Location]'")

duckdb_tool = Tool(
    name="DuckDBTool",
    func=lambda query: run_duckdb_query(query),
    description=(
        "Use this tool to run any SQL query on the DuckDB users database. "
        "These are available fields: ID,Full Name,Email,Location,Occupation,Company,School,Resume File,LinkedIn Bio"
        "Use singular noun form for the search, and allow ILIKE query"
    )
)

tools = [
    duckdb_tool,
    Tool(
        name="SQLTool",
        func=lambda query: find_by_field_and_location("data/users.db", *parse_occupation_and_location(query)),
        description="Use this to find most relevant 3 people when the both job title and location are specified. (e.g., 'Software Engineers in San Jose')"
    ),
    Tool(
        name="VectorTool",
        func=lambda query: find_similar_bios("data/tmp/my_qdrant_data", "user_embeddings", query),
        description="Use this when the user wants to find most relevant 3 people similar in background or experience. Useful for queries like 'someone like X' or 'similar bio to a person at company Y'."
    ),
    Tool(
        name="GraphTool",
        func=lambda query: find_connections_2_hops(
            uri="neo4j+s://773bb327.databases.neo4j.io",
            user="neo4j",
            password="9wWybaxJYJgvj2FeW4TIzPEGyOQzSSjU6tr-U-gOxUc",
            user_id=query.split()[-1].strip("'\"")
        ),
        description="Use this to find most relevant 3 people connected to a given user ID (e.g., '1') via shared schools or companies, up to 2 hops."
    )
]

llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)

agent = initialize_agent(
    tools,
    llm,
    agent="zero-shot-react-description",
    verbose=True,
    handle_parsing_errors=True,
    return_intermediate_steps=True
)

if __name__ == "__main__":
    while True:
        user_query = input("\nEnter query (or 'quit' to exit): ")
        if user_query.lower() == "quit":
            break
        response = agent.invoke(user_query)
        print("Agent:", response)
