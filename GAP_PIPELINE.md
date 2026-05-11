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
| G004 | TOML command format | F022 | ADOPT (simple) + BUILD (migrate) | MEDIUM | READY — se research under |
| G005 | Multi-IDE support | F023 | BUILD | LOW | QUEUED |
| G006 | Marketplace distribution | F024 | BUILD | LOW | QUEUED |
| G007 | Cavecrew agent skills | F025 | BUILD (1 compressed delegation tool) | MEDIUM | READY — se research under |
| G008 | CI/CD sync workflow | F028 | BUILD | LOW | QUEUED |
| G009 | Python compress pipeline (detect+validate) | F029 | BUILD | MEDIUM | QUEUED |
| G010 | Wenyan variants (4 nivåer) | F030 | BUILD | LOW | QUEUED |
| G011 | cavemem SQLite+MCP memory | F003 | LEARN_ONLY | LOW | Claude Code native memory tilstrekkelig |
| G012 | Marketplace.json distribusjon | F024 | RESEARCH | LOW | Trenger dyp research |

---

## RESEARCH QUEUE (OpenCode jobber her)

Prioritert liste over gaps som trenger dypere research før vurdering:

### G004 — TOML command format ✅ RESEARCHED
**Vurdering:** ADOPT for simple commands, BUILD for migration.

**Hva det er:** 2-3 linjer TOML med `description` + `prompt`. Eksempel:
```toml
description = "Switch caveman intensity level (lite/full/ultra/wenyan)"
prompt = "Switch to caveman {{args}} mode..."
```
Ingen kode, ingen Zod, ingen TypeScript-kompilering. Claude Code parser TOML og injecter prompt til LLM.

**Styrker vs våre tools:**
- Zero kode — endre command uten rebuild
- Raskere å lage nye commands
- Fungerer cross-platform (TOML parse av Claude Code selv)

**Svakheter vs våre tools:**
- Ingen logikk — kan ikke kjøre SQLite queries, git diff, image shrink
- Ingen params-validering — `{{args}}` er eneste template
- Ingen streaming eller tool-result manipulation

**Anbefaling:** 
- Migrer `/runes`, `/runes-help` til TOML — disse er rene prompt-injection uten logikk
- Behold `rune_stats`, `rune_commit`, `rune_shrink` som TS tools — de trenger faktisk kode
- Lag `commands/` directory i flint-plugin med TOML-filer for simple commands

### G007 — Cavecrew agent skills ✅ RESEARCHED
**Vurdering:** BUILD — but simplified. 1 compressed delegation tool, ikke 3 presets.

**Hva det er:** Tre subagent-presets (investigator, builder, reviewer) med caveman-compressed output (~60% færre tokens returnert til main context). Hver har:
- Definert output-kontrakt (eksakt format main thread kan forvente)
- Begrensede tools (investigator: Read/Grep/Glob/Bash, builder: Read/Edit/Write, reviewer: Read/Grep/Bash)
- Refusal patterns (builder nekter 3+ files, investigator nekter edits)
- Model routing (alle bruker Haiku — billigere)
- Auto-clarity (drop compression for security warnings)

**Hvorfor de fungerer:**
- Subagent tool results injectes verbatim i main context
- Vanilla `Explore` som returnerer 2K tokens koster 2K main-context budget
- `cavecrew-investigator` returnerer ~700 tokens for samme jobb
- Over 20 delegations: 40K vs 14K — forskjellen mellom context exhaustion og å fullføre

**Anbefaling:** Bygg 1 compressed delegation tool (ikke 3 presets):
- `flint_delegate` tool med parameter `task_type: investigate | build | review`
- Samme output-kontrakt som cavecrew
- Haiku model, compressed output, auto-clarity
- Chaining patterns: locate→fix→verify kan styres av orchestrator i main thread

**Kritisk detalj:** Output-kontrakten er det som gjør cavecrew verdifull, ikke subagent-konseptet. Uenige output-formater = verdiløse verktøy. Må defineres eksakt.

### G012 — Cross-platform rule files ✅ RESEARCHED
**Vurdering:** BUILD — `flint-init` tool som genererer rule-filer for alle plattformer.

**Hva det er:** Hvert IDE/verktøy har sitt eget rule-filformat. Caveman har `.clinerules`. Flint bør kunne generere rule-filer for:
- Cursor: `.cursor/rules/*.mdc`
- Windsurf: `.windsurf/rules/*.md`
- GitHub Copilot: `.github/copilot-instructions.md`
- Cline: `.clinerules/*.md`
- Claude Code: `CLAUDE.md`
- Codex CLI: `AGENTS.md`

**Nøkkelinnsikt:** Cline er mest kompatibel — leser andres formater automatisk. Cursor/Windsurf beveger seg bort fra single-file rot. Aider har ikke rule-filer (bruker YAML-konfig).
Ingen common standard — AGENTS.md er nærmest, men støttes ikke av Windsurf/Cursor native.

**Anbefaling:** Bygg `flint-init` (task T007-relatert) som:
1. Detekterer hvilke IDEs som brukes i repoet
2. Genererer rule-filer i riktig format for hver
3. Deler felles innhold via en `flint-rules/` kilde-mappe
4. Cross-reference: Dette henger sammen med G005 (multi-IDE support)

**Kilder:** cursor.com/docs, docs.cline.bot, docs.github.com, design.dev, aider.chat, agents.md

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
| T006 | Migrer /runes + /runes-help til TOML commands | G004 | ingen | QUEUED |
| T007 | Bygg flint_delegate tool (compressed subagent) | G007 | output-kontrakt definert | PREP — Big Pickle

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
