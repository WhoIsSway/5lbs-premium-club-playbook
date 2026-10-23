#!/usr/bin/env python3
"""Research update runner for the +5LBS Premium Club Playbook.

Requires OPENAI_API_KEY. The model must return source-linked, structured cases.
No substantive change means no data commit; deployment can still validate the site.
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "research.json"
API_URL = "https://api.openai.com/v1/responses"

def fail(message):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)

def get_output_text(response):
    pieces = []
    for item in response.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                pieces.append(content.get("text", ""))
    return "\n".join(pieces).strip()

def main():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        fail("OPENAI_API_KEY repository secret is missing. Add it in Settings > Secrets and variables > Actions.")
    current = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    today = datetime.now(timezone.utc).date().isoformat()
    prompt = f"""
You are the research analyst maintaining the +5LBS Premium Club Playbook.
Today (UTC): {today}.
Return ONLY valid JSON with this exact top-level structure:
{{
 "substantive_update": true or false,
 "change_summary": "short string",
 "cases": [case objects],
 "research_log_entry": {{"date":"YYYY-MM-DD","title":"...","summary":"..."}}
}}
Use the existing structured database as the starting point and preserve all useful existing cases and tracked brands. Add or revise only cases with a material, source-supported change. Search the web for current evidence. Prioritize official brand pages, reliable reporting, and public member/customer evidence. Never invent facts, URLs, opening dates, prices or member outcomes. Distinguish open/operating from announced/planned, and identify evidence limits.
Track and deepen Equinox, Third Space, Life Time; also research The Real Gym, SHARPN TURF, SHARPN MASS and Space/SpaceCycle as separate entities, verifying exact identity before making claims. Proactively discover international Performance Clubs, running/trail-running clubs, Athletic Country Clubs, recovery/health clubs, community-led sports clubs, and hospitality x performance concepts.
Every case object should include: id, brand, city, type, core_model, target_members, investment_modules (array), service_mechanism, community_mechanism, why_it_may_work, plus5lbs_takeaway, avoid_copying, investment_decision, evidence_status, sources (array of {{"label":"...","url":"https://..."}}), last_verified (YYYY-MM-DD).
investment_decision should distinguish build / partner / pilot / defer. A case is not a substantive update merely because its review date changed. If no useful new evidence or new case exists, set substantive_update=false and return the existing cases unchanged. Keep the response concise and do not add unsupported claims.
Existing research database:
{json.dumps(current, ensure_ascii=False)}
"""
    payload = {
        "model": os.environ.get("OPENAI_RESEARCH_MODEL", "gpt-4.1"),
        "tools": [{"type": "web_search_preview"}],
        "input": prompt,
        "text": {"format": {"type": "json_object"}}
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=240) as resp:
            response = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        fail(f"OpenAI Responses API request failed: {exc}")
    raw = get_output_text(response)
    if not raw:
        fail("Responses API returned no output_text.")
    try:
        result = json.loads(raw)
    except json.JSONDecodeError as exc:
        fail(f"Model output was not valid JSON: {exc}")
    if not isinstance(result.get("substantive_update"), bool) or not isinstance(result.get("cases"), list):
        fail("Model output does not match expected JSON shape.")
    if not result["substantive_update"]:
        print("No substantive research update. Keeping the published research database unchanged.")
        return
    # Guard against malformed or unsupported records.
    required = {"id","brand","city","type","core_model","target_members","investment_modules",
                "service_mechanism","community_mechanism","why_it_may_work","plus5lbs_takeaway",
                "avoid_copying","investment_decision","evidence_status","sources","last_verified"}
    ids = set()
    for case in result["cases"]:
        if not isinstance(case, dict) or not required.issubset(case):
            fail("A case is missing required fields; refusing to publish.")
        if case["id"] in ids:
            fail("Duplicate case id; refusing to publish.")
        ids.add(case["id"])
        if not isinstance(case["sources"], list) or not case["sources"]:
            fail(f"Case {case['id']} has no sources; refusing to publish.")
        for source in case["sources"]:
            if not str(source.get("url","")).startswith("https://"):
                fail(f"Case {case['id']} has a non-HTTPS source; refusing to publish.")
    current["cases"] = result["cases"]
    current["updated_at"] = today
    current["last_research_run"] = today
    entry = result.get("research_log_entry") or {
        "date": today, "title": "Research updated", "summary": result.get("change_summary", "Source-backed research update.")
    }
    current.setdefault("research_log", []).insert(0, entry)
    current["research_log"] = current["research_log"][:30]
    current["decision_note"] = result.get("change_summary", "Updated with source-backed research.")
    DATA_PATH.write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Updated research database: {len(current['cases'])} cases. Summary: {current['decision_note']}")

if __name__ == "__main__":
    main()
