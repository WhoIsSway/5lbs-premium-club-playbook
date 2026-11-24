# +5LBS Premium Club Playbook

Living Research & Innovation Lab for +5LBS Standard, PLUS, Premium and the planned 1788 flagship formats.

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

The update script now fails visibly when `OPENAI_API_KEY` is missing; a repeated deployment can no longer masquerade as a successful research update. It validates Research Lab v2, required five-layer topic research, versioned conclusions, counter-evidence, executable experiments, duplicate identities and HTTPS sources. If no substantive learning delta exists, it leaves the database unchanged.

## Research Lab v2

Brand cases are evidence inputs, not the end product. Cross-brand topics must advance through:

1. **WHAT** — verified facts.
2. **HOW** — product and operating mechanism.
3. **WHY** — causal hypothesis with evidence and counter-evidence.
4. **WHAT IF** — clearly labelled cross-brand and cross-sport possibilities.
5. **APPLICATION** — differentiated translation for Standard, PLUS, Premium and the planned 1788 flagship.

Every topic carries a research question, versioned conclusion, open questions, evidence limits, learning delta and executable experiment card. The first deep topic is group-training productization, linking progressive programming, coach ownership, peer identity, community rituals and cross-sport pathways.

## Files

- `index.html`: bilingual site presentation.
- `data/research.json`: structured case database, tracking list, investment framework, and research log.
- `scripts/update_research.py`: API-driven research update and validation.
- `.github/workflows/research-update.yml`: schedule, commit, and Pages deployment.

## Research integrity

Distinguish operating clubs from announced/planned concepts. Preserve source URLs and evidence status. Do not treat brand claims, early presales, or proposed facilities as proof of long-term operating performance. Revalidate details before operational decisions.
