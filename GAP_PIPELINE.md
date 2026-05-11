# GAP PIPELINE
<!-- Vedlikeholdes av: OpenCode (research agent) -->
<!-- Formål: for hvert gap vi finner — research, vurder, og feed implementasjonsoppgaver -->
<!-- Schema version: 1.0 | Started: 2026-05-11 -->

---

## PIPELINE LOGIC

For hvert gap:
1. **Research** — forstå hva det er, hvordan det fungerer, alternativer
2. **Vurder** — BUILD / ADOPT / LEARN_ONLY / REJECT
3. **Feed** — legg implementasjonsoppgave i READY-kolonnen hvis BUILD
4. **Track** — oppdater status når agent tar oppgaven

```
Gap funnet → Research → Vurdering → BUILD? → Implementasjonsoppgave → Agent → Done
                                  → ADOPT? → Integrasjonsoppgave → Agent → Done
                                  → LEARN?  → Finn-mønster → DB-entry
                                  → REJECT  → Dokumenter hvorfor
```

---

## GAP REGISTRY

| ID | Gap | Kilde | Vurdering | Prioritet | Status |
|----|-----|-------|-----------|-----------|--------|
| G001 | caveman-shrink MCP proxy | F021 | BUILD | CRITICAL | IN PROGRESS — Claude koder |
| G002 | flag.ts security hardening | F026 | BUILD | HIGH | PREP — OpenCode #2 → Codex |
| G003 | History tracking (.jsonl) | F027 | BUILD | MEDIUM | QUEUED |
| G004 | TOML command format | F022 | LEARN+ADOPT | MEDIUM | RESEARCH NEEDED |
| G005 | Multi-IDE support | F023 | BUILD | LOW | QUEUED |
| G006 | Marketplace distribution | F024 | BUILD | LOW | QUEUED |
| G007 | Cavecrew agent skills | F025 | BUILD | MEDIUM | QUEUED |
| G008 | CI/CD sync workflow | F028 | BUILD | LOW | QUEUED |
| G009 | Python compress pipeline (detect+validate) | F029 | BUILD | MEDIUM | QUEUED |
| G010 | Wenyan variants (4 nivåer) | F030 | BUILD | LOW | QUEUED |
| G011 | cavemem SQLite+MCP memory | F003 | LEARN_ONLY | LOW | Claude Code native memory tilstrekkelig |
| G012 | Marketplace.json distribusjon | F024 | RESEARCH | LOW | Trenger dyp research |

---

## RESEARCH QUEUE (OpenCode jobber her)

Prioritert liste over gaps som trenger dypere research før vurdering:

### G004 — TOML command format
**Spørsmål:** Hva er nøyaktig syntaksen? Kan vi erstatte våre Zod-schema tools med TOML? Hva mister vi?
**Kilde:** caveman.toml, caveman-init.toml, caveman-review.toml, caveman-commit.toml
**Research needed:** Les filene, forstå format, sammenlign med vår tools/

### G007 — Cavecrew agent skills
**Spørsmål:** Nøyaktig output-kontrakt for reviewer/investigator/builder? Hvordan styres de? Hva gjør dem bedre enn generalist?
**Kilde:** ~/.claude/plugins/cache/caveman/caveman/ef6050c5e184/skills/cavecrew*/
**Research needed:** Les alle SKILL.md-filer, forstå agent-routing

### G012 — Marketplace distribution
**Spørsmål:** Hva er marketplace.json-formatet? Hvem kan publisere? Er det claude.ai/marketplace?
**Research needed:** Web research + les plugin.json-formater

---

## IMPLEMENTASJONSOPPGAVER (READY)

Oppgaver klare til å tildeles agent:

| Task | Gap | Forutsetning | Estimert tid | Tildelt |
|------|-----|-------------|-------------|---------|
| T001 | Bygg flint-shrink MCP proxy | G001 | arkitektur-review av OpenCode #2 | Claude koder |
| T002 | Harden flint-config.js + flag.ts | G002 | security-prep fra OpenCode #2 | Codex (04:55) |
| T003 | Legg til .flint-history.jsonl append i flint-stats | G003 | ingen | QUEUED |
| T004 | detect.py for flint-compress | G009 | ingen | QUEUED |
| T005 | validate.py for flint-compress | G009 | T004 | QUEUED |

---

## DONE

| Task | Gap | Resultat | Commit |
|------|-----|---------|--------|
| Research caveman internals | alle gaps | F021-F030 funnet | ea5ed8b |
| Peer review policy | — | Multi-method validation, status tiers | 814d27d |
| Format rules i SKILL.md | — | no emoji, no pretty JSON, EN for tech | 61a9413 |

---

## REGLER FOR OPENCODE

1. Når nytt gap oppdages: legg i GAP REGISTRY med vurdering
2. Når research fullføres: oppdater status + legg READY-oppgave
3. Når agent tar oppgave: oppdater Tildelt-kolonne
4. Når ferdig: flytt til DONE med commit-hash
5. Aldri overskriv eksisterende rader — append og oppdater Status-felt
