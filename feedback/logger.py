from __future__ import annotations
import json, os, datetime
from pathlib import Path
from typing import Dict, Any, List

FEEDBACK_DIR = Path("feedback")
FEEDBACK_FILE = FEEDBACK_DIR / "feedback_log.jsonl"

def _ensure_paths():
    FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)
    if not FEEDBACK_FILE.exists():
        FEEDBACK_FILE.touch()

def save_feedback(entry: Dict[str, Any]) -> None:
    _ensure_paths()
    with open(FEEDBACK_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def load_recent_feedback(n: int = 50) -> List[Dict[str, Any]]:
    _ensure_paths()
    lines = FEEDBACK_FILE.read_text(encoding="utf-8").splitlines()
    out: List[Dict[str, Any]] = []
    for line in lines[-n:]:
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out

def now_iso() -> str:
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
