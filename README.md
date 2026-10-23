# +5LBS Premium Club Playbook

Living benchmark and concept research for the future +5LBS Premium Club.

## Live site

Published through GitHub Pages from `index.html`. The site preserves Chinese/English switching and loads its case radar and research log from `data/research.json`.

## Research system

Anchor benchmarks: Equinox / Third Space / Life Time.

China references: The Real Gym, SHARPN TURF, SHARPN MASS, and Space / SpaceCycle. Keep TURF and MASS separate; verify exact entity/location before attributing claims.

Adjacent radar includes luxury fitness and hospitality, performance clubs, running/trail-running training clubs, athletic country clubs, recovery/social wellness, community-led sports clubs, and hospitality x performance concepts.

Decision lens: Training Outcome / Premium Perception / Retention / Dwell Time / ARPU / Community / Identity.

Investment lens: build core capabilities in-house; partner for specialist clinical/medical services where appropriate; pilot recovery and ancillary services before committing to high-complexity capex; defer expensive modules until member demand is evidenced.

## Automated research and publishing

The workflow `.github/workflows/research-update.yml` is scheduled for Mondays and Thursdays at 09:17 China Standard Time and can also be started manually from the repository's **Actions** tab.

**One-time setup required:** add an Actions repository secret named `OPENAI_API_KEY` (Settings → Secrets and variables → Actions → New repository secret). The workflow uses the OpenAI Responses API with web search to propose source-backed case updates. The key is not stored in this repository. API usage may incur charges according to the account's API pricing.

Without this secret, the workflow will still attempt to publish/validate the site but will skip automated research. ChatGPT's own scheduled task does not automatically write its conversation results to GitHub; the workflow is a separate pipeline.

The update script validates required fields and HTTPS source links. If no substantive change is found, it leaves `data/research.json` unchanged and creates no content commit. When new evidence is found, it commits the structured research data and deploys the site in the same workflow run.

## Files

- `index.html`: bilingual site presentation.
- `data/research.json`: structured case database, tracking list, investment framework, and research log.
- `scripts/update_research.py`: API-driven research update and validation.
- `.github/workflows/research-update.yml`: schedule, commit, and Pages deployment.

## Research integrity

Distinguish operating clubs from announced/planned concepts. Preserve source URLs and evidence status. Do not treat brand claims, early presales, or proposed facilities as proof of long-term operating performance. Revalidate details before operational decisions.
