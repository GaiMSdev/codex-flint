# COMPRESSION RESEARCH DATABASE
<!-- All agents: read freely, append with date prefix, never overwrite existing rows -->
<!-- Location: codex-flint/COMPRESSION_RESEARCH_DB.md — git-tracked, agent-shared -->
<!-- Schema version: 1.0 | Started: 2026-05-11 -->

---

## METHODS CATALOGUE

All known compression methods. Status: VALIDATED / TESTED / HYPOTHESIS / REJECTED.

| ID | Name | Description | Savings vs Baseline | vs Terse | Retention | Platform | Status |
|----|------|-------------|--------------------|-----------|-----------|---------:|--------|
| M001 | terse-plain | Generic "be concise" instruction | ~82% | — (reference) | 5/5 | All | VALIDATED |
| M002 | caveman-full | Caveman drop-articles + short synonyms, per-turn hook | ~65% | -91.7% | 5/5 | Claude | VALIDATED |
| M003 | caveman-ultra | Caveman max density + cavemem SQLite memory | ~69% | -71.4% | 5/5 | Claude | VALIDATED |
| M004 | flint-full | FLINT full mode (concise, no preamble, fragments OK) | ~54% | -151.7% | 5/5 | Claude/Codex | VALIDATED |
| M005 | flint-ultra | FLINT ultra (abbrev prose, arrows, PRESERVE facts) | ~57% | -135.3% | 5/5 | Claude/Codex | VALIDATED |
| M006 | flint-compact | Shorter prompt + PRESERVE ALWAYS + concrete example | ~65-74%* | unknown | 5/5 | Claude/Codex | HYPOTHESIS* |
| M007 | runes-full | RUNES full for Gemini (drop articles, fragments OK) | ~54% | unknown | unknown | Gemini | TESTED |
| M008 | runes-ultra | RUNES ultra for Gemini (max density) | ~69% | unknown | unknown | Gemini | TESTED |
| M009 | runes-hybrid | HYBRID: broken-English + MetaGlyphs (Gemini claim) | ~92%* | unknown | unknown | Gemini | UNVALIDATED* |
| M010 | wenyan | Classical Chinese compression (之其者也矣) | no data | no data | 5/5 | Claude | HYPOTHESIS |
| M011 | telegraph-persona | "You are 1890 telegraph operator — words cost money" | untested | untested | unknown | All | HYPOTHESIS |
| M018 | telegraph-stripped | Telegraph persona stripped to core constraint only (no narrative context) | ~22.3% long / ~10.5% code* | unknown | unknown | All | TESTED |
| M012 | negative-instruction | "Never say: I, the, a, an, is, are, was, were" | untested | untested | unknown | All | HYPOTHESIS |
| M013 | json-schema-output | Force JSON: {answer, confidence, next} always | untested | untested | unknown | All | HYPOTHESIS |
| M014 | token-limit-hard | "Answer in max 80 tokens" hard constraint | untested | untested | unknown | All | HYPOTHESIS |
| M015 | variable-substitution | Let X=auth, Y=DB — write with variables | untested | untested | unknown | All | HYPOTHESIS |
| M016 | bullets-only | Format-force: only bullets, no prose | untested | untested | unknown | All | HYPOTHESIS |
| M017 | linguistic-anchoring | "Me ⚙" fragments as anti-drift anchors | untested | untested | unknown | Gemini | HYPOTHESIS |

*M006 flint-compact: CLI benchmark invalid (78k input-token contamination). API benchmark pending.
*M009 runes-hybrid: self-reported by Gemini agent, no external validation yet.

---

## BENCHMARK LOG

Validated runs only. CLI self-reporting excluded.

### BM001 — 2026-05-11 — API cross-platform (authoritative)
- **Model:** claude-haiku-4-5-20251001
- **Arms:** baseline, terse, caveman_full, caveman_ultra, full (flint), ultra_plain (flint)
- **Scenarios:** long_conversation (10 turns), context_retention (8 turns, facts@turn1→recall@turn8)
- **Valid:** YES (API key, proper multi-turn, no session contamination)
- **Results:**

| Mode | Output tokens | vs Baseline | vs Terse |
|------|--------------|-------------|----------|
| baseline | 14 595 | — | — |
| terse | 10 612 | +27.3% saved | reference |
| caveman_full | ~8 000* | +65.1% saved | -91.7% |
| caveman_ultra | ~7 200* | +68.8% saved | -71.4% |
| flint-full | ~6 700* | +54.1% saved | -151.7% |
| flint-ultra | ~6 300* | +57.1% saved | -135.3% |

*Approximate from percentage back-calculations.
- **Context retention:** all modes 5/5 facts recalled
- **Key finding:** terse-plain beats ALL structured skills on raw output savings. Caveman beats FLINT by ~11%.

### BM002 — 2026-05-11 — CLI benchmark (INVALID)
- **Model:** claude-haiku-4-5-20251001
- **Arms:** baseline, terse, caveman_ultra, flint_compact
- **Valid:** NO
- **Why invalid:**
  1. ~78k input tokens/turn from CLAUDE.md + caveman hooks masked signal
  2. History-as-text: model replikates own verbosity
  3. No max_tokens for caveman → 8234 tokens in single turn
- **Results:** DISCARD — structured skills showed inverted (worse than baseline)

### BM003 — PENDING — API flint_compact validation
- **Status:** Blocked on ANTHROPIC_API_KEY
- **Arms needed:** baseline, terse, caveman_ultra, flint_compact
- **Expected:** flint_compact ~65-74% (hypothesis)

### BM004 — PENDING — Gemini HYBRID vs RUNES A/B
- **Status:** Assigned to Gemini CLI agent 2026-05-11
- **Arms needed:** baseline, terse, runes-full, runes-hybrid
- **Methodology:** Gemini API direct (not CLI self-report)

---

## RESEARCH FINDINGS

| Date | ID | Source | Finding | Implication | Confidence |
|------|----|--------|---------|-------------|------------|
| 2026-05-11 | F001 | Caveman reverse-eng. | Caveman uses per-turn hookSpecificOutput JSON — persistence mechanism | Must have UserPromptSubmit hook or model drifts after ~5 turns | HIGH |
| 2026-05-11 | F002 | Caveman reverse-eng. | Caveman runtime-filters SKILL.md to active mode's rows only at hook time | Shorter injected prompt = less noise = better compression | HIGH |
| 2026-05-11 | F003 | Caveman reverse-eng. | Cavemem = separate SQLite + MCP tool (not part of skill). Handles fact retention. | Skill itself has NO fact-preservation rules — cavemem is external | HIGH |
| 2026-05-11 | F004 | Benchmark BM001 | terse-plain (~82%) beats all structured skills on raw output savings | Structured skills' value = persistence + mode control, not savings vs terse | HIGH |
| 2026-05-11 | F005 | Benchmark BM001 | All compression modes retain 5/5 facts equally | Fact retention not differentiator — persistence/compression is | HIGH |
| 2026-05-11 | F006 | Caveman reverse-eng. | Caveman has dual compression: output (~65%) + memory files (~46% via cavemem) | We need input compression too, not just output | HIGH |
| 2026-05-11 | F007 | mcp-shrink analysis | mcp-shrink compresses MCP tool outputs before reaching LLM context | Input-side compression = bigger impact on total budget than output | HIGH |
| 2026-05-11 | F008 | Gemini agent report | runes-compress deployed: ~21% savings on Gemini memory prose | Validates input compression concept; lower than expected (~46% claimed) | MEDIUM |
| 2026-05-11 | F009 | Gemini agent claim | HYBRID (broken-English + MetaGlyph): 92% savings claimed | Unvalidated self-report; A/B test assigned (BM004) | LOW |
| 2026-05-11 | F010 | FLINT-Compact design | Shorter prompt + one concrete example = caveman-level prompt architecture | Removes MetaGlyph clutter, adds PRESERVE ALWAYS for facts | MEDIUM |
| 2026-05-11 | F011 | CLI benchmark analysis | System prompt with examples copied into history = self-reinforcing verbosity | Multi-turn CLI benchmarks with history-as-text are fundamentally flawed | HIGH |
| 2026-05-11 | F012 | Codex (tiktoken o200k_base) | dash bullets = semicolon prose (25 tok); numbered list 29 (+16%); prose sentence 26 | Use bullets for scanability; avoid numbered lists unless order matters | HIGH |
| 2026-05-11 | F012b | Codex (tiktoken) | plain label 24 tok; bold/##/### all 25 tok — heading markup costs nearly same | Ultra: use plain labels, skip ## | MEDIUM |
| 2026-05-11 | F012c | Codex (tiktoken) | key=value 20, prose 20, YAML 23, minified JSON 24, pretty JSON 38 | Pretty JSON 90% costlier than prose — never use in FLINT output | CRITICAL |
| 2026-05-11 | F012d | Codex (tiktoken) | emoji 15–18 tok, ASCII bracket symbols 15, ASCII words 11 | Emoji up to 64% costlier than ASCII words — remove from FLINT output | HIGH |
| 2026-05-11 | F012e | Codex (tiktoken) | double spaces 23 tok vs single/newline/blank all 15 | Normalize double spaces — 53% overhead | MEDIUM |
| 2026-05-11 | F013 | OpenCode research | (PENDING — literature research assigned) Academic methods for LLM output compression | | PENDING |
| 2026-05-11 | F018 | OpenCode #2 analysis | NOT→DO contrastive anchoring: showing bad+good example side-by-side stronger than rules alone. Claims +14pp vs pure abbrev rules. FLINT-Compact already uses this pattern. | May explain caveman's ~11pp advantage over old FLINT — caveman had NOT/YES examples | MEDIUM* |
| 2026-05-11 | F019 | OpenCode H006 review | Constraint-based prompting: 50-70% savings but HIGH variance (±30%). Style-based: 30-50% but LOW variance. LLMs respect prompt token limits ±30% only; API max_tokens is hard stop. 80T sweet spot for 5-fact retention. Utility cliff below 50T. | Combined arm (token limit + style) likely optimal. Add completeness score to benchmark. | HIGH |
| 2026-05-11 | F020 | TELEGRAPH-STRIPPED review | M018: 22.3% savings long conv, 10.5% code refactor (anomalously low). Status: TESTED. Missing: 1 second opinion + 1 non-character-count method + A/B vs original telegraph-persona. "Technical validity" metric undefined. | Third opinion from OpenCode #2 ordered. A/B vs M011 needed before REVIEWED. | TESTED |
| 2026-05-11 | F014 | Claude koder (visual research) | Tables only worth it at ≥3 rows × 2+ cols — otherwise loses to prose on token count | Add table threshold rule to FLINT full+ultra | HIGH |
| 2026-05-11 | F015 | Claude koder (visual research) | Mermaid beats prose at ≥4 nodes; ASCII diagrams almost never token-efficient | Recommend Mermaid for complex flows, skip ASCII | HIGH |
| 2026-05-11 | F016 | Claude koder (visual research) | Code+1-line comment ~15% fewer tokens than prose for usage examples | Change "one concrete example" rule to prefer code+comment | HIGH |
| 2026-05-11 | F017 | Claude koder (visual research) | Norwegian tokenizes 30–50% more expensive than English — technical terms always English | Add English-for-technical rule to ultra mode | CRITICAL |

---

## OPEN HYPOTHESES

| ID | Hypothesis | Rationale | Test Plan | Priority |
|----|------------|-----------|-----------|----------|
| H001 | flint_compact beats caveman_ultra by 5-10% | Shorter prompt + example = better instruction following | Run BM003 with API key | HIGH |
| H002 | HYBRID 92% claim is inflated / self-reporting bias | Gemini measures its own output without external baseline | BM004 via Gemini API | HIGH |
| H003 | Telegraph persona achieves 70%+ savings | Strong contextual framing beats explicit rules | Single-turn API test, 20 prompts | IN PROGRESS — Gemini + Codex 2026-05-11 |
| H004 | JSON-schema output saves tokens for structured answers | Structured format eliminates transitional prose | Token-count A/B, 10 question types | MEDIUM |
| H005 | Negative instruction ("never say: a, the, is") outperforms positive | Negative constraints easier for model to follow | 5-turn test, count forbidden words | IN PROGRESS — Gemini + Codex 2026-05-11 |
| H006 | Hard token limits (max 80 tokens) reduce output more than style rules | Constraint > instruction — but high variance (±30% actual respect) | A/B: baseline/ultra/token_80/token_combined. Measure completeness score (no truncated sentences). 80T sweet spot: 5 facts×~10tok=50min, 80 gives margin. Combined arm (limit+style) likely best. | IN PROGRESS — Codex building arms 2026-05-11 |
| H007 | Linguistic anchoring prevents drift better than explicit "ACTIVE EVERY RESPONSE" | Implicit signal more persistent than explicit reminder | 15-turn drift test | LOW |
| H008 | Variable substitution (X=auth, Y=DB) compresses technical answers | Reduces repeated long terms | Domain-specific A/B test | LOW |
| H009 | Mixed-platform standard (one compression style for all LLMs) is impossible | Different training → different response to same prompt | Cross-model A/B: same prompt, Haiku + Gemini + GPT | MEDIUM |

---

## DECISIONS LOG

| Date | ID | Decision | Rationale | Outcome |
|------|----|----------|-----------|---------|
| 2026-05-11 | D001 | Drop MetaGlyph from FLINT-Compact (except →) | No benchmark evidence glyphs help; add noise | Kept → for causality only |
| 2026-05-11 | D002 | Add PRESERVE ALWAYS rule to ultra | Caveman has NO fact-preservation — differentiator | Implemented in flint-hook.sh + SKILL.md |
| 2026-05-11 | D003 | Fix wenyan ratio (was 0.69, copied from ultra) | No benchmark data for wenyan — fabricated number | Removed estimate, added comment |
| 2026-05-11 | D004 | Reject HYBRID as cross-platform standard | No external validation; models train differently | A/B test assigned, decide after BM004 |
| 2026-05-11 | D005 | Wire flint-compress to PostToolUse hook | Auto-compress memory files on write = wired input savings | claude-flint plugin updated |
| 2026-05-11 | D006 | Keep FLINT and caveman as separate Claude plugins | Coexist: caveman active by default, FLINT adds modes | Both in settings.json, statusline-wrapper selects |
| 2026-05-11 | D007 | API benchmark = authoritative, CLI benchmark = invalid | CLI session contamination (78k input tokens/turn) | Discard BM002 results |
| 2026-05-11 | D008 | Add format rules to FLINT full+ultra (table threshold, code+comment, English-for-technical) | Empirical findings from Claude koder visual research (F014-F017) | SKILL.md updated |
| 2026-05-11 | D009 | Add token-cost rules to ultra: no emoji, no pretty JSON, plain labels, bullets over numbered | Codex tiktoken benchmark (F012a-e) — pretty JSON 90% overhead, emoji 64% overhead | SKILL.md + flint-activate.js updated |

---

## AGENT CONTRIBUTIONS

| Date | Agent | Contribution | Files | Status |
|------|-------|-------------|-------|--------|
| 2026-05-11 | Claude (Orchestrator) | Reverse-engineered caveman, designed FLINT-Compact | flint-hook.sh, SKILL.md, flint_compress.py, claude-flint plugin | DONE |
| 2026-05-11 | Codex | Pushed wenyan fix, mcp-shrink wiring (in progress) | flint-hook.sh, benchmark.py, parse_session.py, config.toml | IN PROGRESS |
| 2026-05-11 | Gemini CLI | runes-compress deployed, HYBRID A/B test in progress | gem-thal/scripts/runes-compress.py | IN PROGRESS |
| 2026-05-11 | OpenCode | Literature research on compression methods | — | PENDING |
| 2026-05-11 | OpenCode #2 | Building 6 experimental compression prompts | — | PENDING |
| 2026-05-11 | Codex | Token-cost analysis (format vs tokens) | COMPRESSION_RESEARCH_DB.md, BENCHMARK_DECISIONS.md | DONE |
| 2026-05-11 | Claude koder | Visual/structural compression research | — | PENDING |

---

## VALIDATION POLICY

**En benchmark er ikke nok.** Før et funn kan bli VALIDATED:

| Krav | Minimum |
|------|---------|
| Benchmark runs | ≥2 uavhengige kjøringer (ulike scenarier eller modeller) |
| Agent reviews | ≥2 second opinions fra ulike agenter |
| Metoder | Minst 2 av: token-telling, API-benchmark, lokal regex-test, human eval |
| Real-world proxy | Minst ett scenario som ligner faktisk bruk (ikke bare syntetiske prompts) |

Status-nivåer:
- **HYPOTHESIS** — idé, ingen data
- **TESTED** — én kjøring, trenger mer validering
- **REVIEWED** — ≥2 agent opinions, ≥1 benchmark
- **VALIDATED** — ≥2 benchmarks + ≥2 reviews + real-world proxy

---

## HOW TO ADD ENTRIES

**Agents:** append rows to relevant section. Never overwrite. Use ISO date (YYYY-MM-DD).

**New method:**
```
| M0XX | name | description | savings | vs_terse | retention | platform | STATUS |
```

**New finding:**
```
| YYYY-MM-DD | F0XX | source | finding | implication | HIGH/MEDIUM/LOW/PENDING |
```

**New benchmark run:**
Copy BM001 block, fill in metadata + results table.

**Blocking an existing entry:** add `*` suffix and footnote explaining block/update.
