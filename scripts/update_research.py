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
        fail("OPENAI_API_KEY is not configured; refusing to report a successful research run.")
    current = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    today = datetime.now(timezone.utc).date().isoformat()
    prompt = f"""
You maintain the +5LBS Research & Innovation Lab. Today (UTC): {today}.
Return ONLY valid JSON:
{{
  "substantive_update": true or false,
  "change_summary": "what changed in our understanding, not a case count",
  "cases": [complete preserved case database],
  "research_lab": {{complete preserved-and-updated research_lab object}},
  "research_log_entry": {{"date":"YYYY-MM-DD","title":"...","summary":"..."}},
  "learning_log_entry": {{
    "date":"YYYY-MM-DD","run_id":"scheduled-YYYY-MM-DD",
    "topic_id":"...", "delta_type":"new_evidence|revised_conclusion|counter_evidence|new_experiment|no_change",
    "added_zh":[],"added_en":[],"corrected_zh":[],"corrected_en":[],"no_change_zh":[],"no_change_en":[]
  }}
}}
Preserve all useful existing records. Never delete or replace an existing case or topic unless new evidence explicitly corrects it.
A substantive update must deepen knowledge, revise a conclusion, add counter-evidence, answer/open a research question, or create/revise an executable experiment. A new brand card alone is not sufficient.
Every run must connect brand evidence to at least one cross-brand topic and advance at least one of WHAT, HOW, WHY, WHAT IF, APPLICATION.
Prioritize: group-training productization, coach mechanisms, training progression, community and cross-sport innovation.
APPLICATION must distinguish Standard, PLUS, Premium, and planned 1788 Flagship. Do not present the planned flagship as open.
For every causal interpretation include supporting evidence and counter-evidence or evidence limits. Distinguish official claims, independent reporting, user evidence and our hypotheses.
Every experiment needs audience, duration, steps, success metrics, guardrails and a decision rule.
Do not change dates merely to create activity. If no material evidence exists, set substantive_update=false, preserve cases and research_lab unchanged, and use a no_change learning entry.
Prevent duplicates by stable case id, normalized brand/city/type identity and overlapping source URLs. Never invent URLs, outcomes, opening status, prices or member results.
Priority sources: official pages, filings, reliable reporting, then clearly labelled public member evidence.
Current database:
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
    if (not isinstance(result.get("substantive_update"), bool)
            or not isinstance(result.get("cases"), list)
            or not isinstance(result.get("research_lab"), dict)):
        fail("Model output does not match Research Lab v2 shape.")
    if not result["substantive_update"]:
        print("No substantive research update. Keeping the published research database unchanged.")
        return
    # Guard against malformed or unsupported records.
    required = {"id","brand","city","type","core_model","target_members","investment_modules",
                "service_mechanism","community_mechanism","why_it_may_work","plus5lbs_takeaway",
                "avoid_copying","investment_decision","evidence_status","sources","last_verified"}
    ids = set()
    fingerprints = set()
    source_urls = set()
    for case in result["cases"]:
        if not isinstance(case, dict) or not required.issubset(case):
            fail("A case is missing required fields; refusing to publish.")
        if case["id"] in ids:
            fail("Duplicate case id; refusing to publish.")
        ids.add(case["id"])
        fp = "|".join(str(case.get(k, "")).strip().lower() for k in ("brand", "city", "type"))
        if fp in fingerprints:
            fail(f"Duplicate normalized case identity: {fp}")
        fingerprints.add(fp)
        if not isinstance(case["sources"], list) or not case["sources"]:
            fail(f"Case {case['id']} has no sources; refusing to publish.")
        for source in case["sources"]:
            url = str(source.get("url", "")).strip()
            if not url.startswith("https://"):
                fail(f"Case {case['id']} has a non-HTTPS source; refusing to publish.")
            source_urls.add(url)

    lab = result["research_lab"]
    topics = lab.get("topics")
    if not isinstance(topics, list) or not topics:
        fail("Research Lab must contain at least one cross-brand topic.")
    topic_ids = set()
    for topic in topics:
        topic_id = topic.get("id")
        if not topic_id or topic_id in topic_ids:
            fail("Research topic ids must be present and unique.")
        topic_ids.add(topic_id)
        layers = topic.get("layers", {})
        for key in ("what", "how", "why", "what_if", "application"):
            if not isinstance(layers.get(key), list) or not layers[key]:
                fail(f"Topic {topic_id} is missing required layer: {key}")
        conclusion = topic.get("conclusion", {})
        if not conclusion.get("version") or not conclusion.get("date"):
            fail(f"Topic {topic_id} needs a versioned conclusion.")
        if not topic.get("evidence", {}).get("counter_evidence_zh"):
            fail(f"Topic {topic_id} needs counter-evidence.")
        for experiment in topic.get("experiments", []):
            required_experiment = {"id","duration","success_metrics","guardrails","decision_rule_zh","decision_rule_en"}
            if not required_experiment.issubset(experiment):
                fail(f"Experiment in {topic_id} is incomplete.")
    current["cases"] = result["cases"]
    current["research_lab"] = result["research_lab"]
    learning = result.get("learning_log_entry")
    if not isinstance(learning, dict) or not learning.get("delta_type"):
        fail("Missing learning_log_entry; refusing to publish.")
    current["research_lab"].setdefault("learning_log", []).insert(0, learning)
    current["research_lab"]["learning_log"] = current["research_lab"]["learning_log"][:50]
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
