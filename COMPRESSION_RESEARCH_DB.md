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
| M019 | response-deduplication | LZ77-inspired: detect+compress repeated phrases mid-conversation | est ~30-50% | unknown | unknown | All | HYPOTHESIS |
| M020 | syntactic-tree-pruning | Computational linguistics: prune optional syntactic branches (adj/adv/relative clauses) | est ~20-40% | unknown | unknown | All | HYPOTHESIS |

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
| 2026-05-11 | F020 | 2-agent review (Big Pickle + OpenCode #2) | M018 TELEGRAPH-STRIPPED: TESTED, NOT REVIEWED. Blockers: token count method missing, A/B vs M011 missing, break-even analysis missing, FULL@10.5% anomalous. 2x APPROVE FOR TESTED only. | Needs: token-count method + A/B + break-even before REVIEWED. No result upgradeable to VALIDATED without ≥2 benchmarks + ≥2 reviews + proxy. | TESTED |
| 2026-05-11 | F021 | OpenCode caveman deep-dive | caveman-shrink: MCP middleware that wraps ANY upstream MCP server, compresses description fields. npm published. We have nothing equivalent. | Highest priority port: gives input compression on all MCP tool descriptions automatically | CRITICAL |
| 2026-05-11 | F022 | OpenCode caveman deep-dive | caveman TOML commands: 4 TOML files (caveman.toml, -init, -review, -commit) with description+prompt. Simpler than Zod-schema tools. | Simpler tool definition format — adopt for flint tools | MEDIUM |
| 2026-05-11 | F023 | OpenCode caveman deep-dive | Multi-IDE: WindSurf (.windsurf/rules/), Cursor (.cursor/rules/), Cline (.clinerules/), Codex (.codex/hooks.json). We only have Claude/Gemini/OpenCode. | Expand flint to Cursor/Windsurf for broader reach | LOW |
| 2026-05-11 | F024 | OpenCode caveman deep-dive | Marketplace: .claude-plugin/plugin.json + marketplace.json for formal distribution. We have none. | Distribution infrastructure needed for ecosystem adoption | LOW |
| 2026-05-11 | F025 | OpenCode caveman deep-dive | Cavecrew: multi-agent skills (cavecrew-reviewer, cavecrew-investigator, cavecrew-builder) with strict output contracts. Agent-specific skills missing in our system. | Build flint-crew equivalents for specialized agent roles | MEDIUM |
| 2026-05-11 | F026 | OpenCode caveman deep-dive | Security: caveman-config.js uses O_NOFOLLOW, atomic temp+rename, uid verification, size caps, VALID_MODES whitelist. Our flag.ts is naive. | Harden flag.ts with same security patterns | HIGH |
| 2026-05-11 | F027 | OpenCode caveman deep-dive | History tracking: caveman-stats appends to .caveman-history.jsonl for lifetime usage tracking. Our stats only read current session. | Add jsonl history append to flint-stats | MEDIUM |
| 2026-05-11 | F028 | OpenCode caveman deep-dive | CI/CD: .github/workflows/sync-skill.yml for auto-updates across IDEs. We have no automation. | Add sync workflow for codex-flint | LOW |
| 2026-05-11 | F029 | OpenCode caveman deep-dive | Python compression pipeline: skills/compress/scripts/ with compress.py, detect.py, validate.py, benchmark.py. Full pipeline vs our single flint_compress.py. | Add detect.py (auto-detect compressible content) + validate.py to flint-compress | MEDIUM |
| 2026-05-11 | F030 | OpenCode caveman deep-dive | Wenyan variants: caveman has 4 levels (wenyan-lite, wenyan, wenyan-full, wenyan-ultra). We have 1. | Expand wenyan to 4 levels after benchmarking base mode | LOW |
| 2026-05-11 | F014 | Claude koder (visual research) | Tables only worth it at ≥3 rows × 2+ cols — otherwise loses to prose on token count | Add table threshold rule to FLINT full+ultra | HIGH |
| 2026-05-11 | F015 | Claude koder (visual research) | Mermaid beats prose at ≥4 nodes; ASCII diagrams almost never token-efficient | Recommend Mermaid for complex flows, skip ASCII | HIGH |
| 2026-05-11 | F016 | Claude koder (visual research) | Code+1-line comment ~15% fewer tokens than prose for usage examples | Change "one concrete example" rule to prefer code+comment | HIGH |
| 2026-05-11 | F017 | Claude koder (visual research) | Norwegian tokenizes 30–50% more expensive than English — technical terms always English | Add English-for-technical rule to ultra mode | CRITICAL |
| 2026-05-11 | F031 | Caveman source: `hooks/caveman-statusline.sh:13-28,37-49`; `tests/test_caveman_stats.js:401-430` | Statusline is hardened as a hostile input surface: refuse symlink flag, cap read at 64 bytes, strip control bytes, whitelist modes, default-on savings suffix only after real stats file exists. | BUILD: FLINT status UI must use same symlink/control-byte/no-fake-number pattern before exposing visible stats. | HIGH |
| 2026-05-11 | F032 | Caveman source: `hooks/caveman-stats.js:15-19,134-143,230-250` | Savings estimates are deliberately mode-scoped: only `full` has measured ratio; other modes report "No savings estimate" instead of extrapolating. | ADOPT: remove unbenchmarked FLINT per-mode savings claims; show measured modes only. | HIGH |
| 2026-05-11 | F033 | Caveman source: `hooks/caveman-stats.js:95-132,255-260,334-336` | Stats also scan compressed memory pairs (`*.original.md` + `.md`) and report approximate passive input-token savings per session start. | BUILD: FLINT stats should combine output savings + local memory compression savings instead of output-only reporting. | HIGH |
| 2026-05-11 | F034 | Caveman source: `hooks/caveman-stats.js:154-176,306-328`; `hooks/caveman-config.js:192-249` | Lifetime stats append JSONL snapshots but aggregate latest entry per session_id, avoiding double-count when `/caveman-stats` runs repeatedly. Appends use O_APPEND + O_NOFOLLOW. | BUILD: FLINT stats history should dedupe by session and append symlink-safely. | HIGH |
| 2026-05-11 | F035 | Caveman source: `benchmarks/run.py:52-68,78-145,184-202,239-270`; `benchmarks/prompts.json:3-53` | Main benchmark uses real Anthropic usage tokens, 10 dev-task prompts, 3 trials default, medians per task, raw JSON storage, skill hash, and optional README marker update. | ADOPT: OnePlayer benchmark should store raw full responses + hash prompt/skill inputs + median over repeats. | HIGH |
| 2026-05-11 | F036 | Caveman source: `evals/README.md:7-19,70-84`; `evals/measure.py:1-13,57-103` | Evals explicitly compare skills against a terse control, not only unguided baseline, and label limits: no fidelity, no exact Claude token count, no statistical significance. | ADOPT: report FLINT results vs both unguided and terse; keep TESTED until fidelity + repeats + proxy exist. | HIGH |
| 2026-05-11 | F037 | Caveman source: `install.sh:23-28,63-82,699-739` | Installer keeps per-repo rule writes opt-in because writing into `$PWD` from curl-pipe is surprising; `--all` enables it, `--minimal` disables hooks/MCP/init. | ADOPT: FLINT installer/init should not write repo rules by default; make input-compression wiring explicit and reversible. | MEDIUM |
| 2026-05-11 | F038 | Caveman source: `install.sh:507-553` | MCP shrink registration probes npm first; if registry/package missing, it skips and prints manual config instead of installing a broken spawn entry. | BUILD: FLINT mcp-shrink wiring should validate local/server path before config mutation and give manual snippet fallback. | HIGH |
| 2026-05-11 | F039 | Caveman source: `install.sh:416-445` | Compound provider detection avoids BSD awk `RS='||'` bug by parsing `||` with bash parameter expansion; previous awk version silently detected zero agents on macOS. | LEARN: keep installer probes POSIX/macOS-safe; add tests for compound detection parsing. | MEDIUM |
| 2026-05-11 | F040 | Caveman source: `install.sh:760-782` | Installer exits nonzero only if every detected target failed; skips and partial success are reported but do not fail the whole install. | ADOPT: FLINT multi-target installer should track installed/skipped/failed separately, not binary success/fail. | MEDIUM |
| 2026-05-11 | F041 | Caveman source: `tools/caveman-init.js:16-35,37-53,64-97` | `caveman-init` embeds fallback rule body, prefers source-of-truth rule file, uses sentinel idempotence, appends to shared instruction files, replaces IDE-local rule files only with `--force`. | BUILD: FLINT init should use same sentinel + append/replace policy for AGENTS/Copilot vs IDE-local rules. | HIGH |
| 2026-05-11 | F042 | Caveman source: `skills/compress/scripts/compress.py:15-17,104-120`; `tests/test_compress_safety.py:1-9,39-67` | Compression strips whole-output markdown fences and tells the model not to add outer fences; guards reject empty/identical output before any backup/write. | BUILD: FLINT compress should strip LLM wrapper fences and reject no-op/empty responses before touching disk. | HIGH |
| 2026-05-11 | F043 | Caveman source: `mcp-servers/caveman-shrink/index.js:16-28,73-124`; `README.md:264` | `caveman-shrink` intentionally compresses only MCP metadata/list fields; request payloads and `tools/call` response content pass through unchanged to avoid breaking parsers or data semantics. | ADOPT: keep FLINT shrink v1 metadata-only; do not compress tool outputs until separate validation. | HIGH |
| 2026-05-11 | F044 | Caveman source: `mcp-servers/caveman-shrink/compress.js:47-72` | Caveman shrink protects segments with sequential sentinel replacement; sentinels can be re-matched by later protected regexes. FLINT's single-pass protected regex fixes this class. | LEARN/REJECT upstream pattern: keep FLINT single-pass sentinel protection and add regression tests. | HIGH |
| 2026-05-11 | F045 | Caveman source: `mcp-servers/caveman-shrink/index.js:39-41,81-107`; `tests/test_mcp_shrink.js:103-124` | Shrink fields are env-configurable (`CAVEMAN_SHRINK_FIELDS`), but recursion only runs if no top-level tools/prompts/resources matched; avoids double-processing nested schemas. | BUILD: FLINT shrink should expose field allowlist + avoid duplicate traversal/compression. | MEDIUM |
| 2026-05-11 | F046 | Caveman source: `hooks/install.sh:120-190`; `tests/verify_repo.py:278-294,376-394` | Hook installer merges JSON via Node, backs up settings, preserves existing statusline instead of clobbering, and tests uninstall restores non-caveman settings exactly. | BUILD: FLINT hook/config installer must preserve user hooks/statusline and prove uninstall restores baseline. | HIGH |
| 2026-05-11 | F047 | Caveman source: `hooks/install.sh:128-134`; `hooks/uninstall.sh:62-65` | Installer passes settings/hooks paths via environment variables into Node snippets to avoid shell quoting/injection bugs from `$HOME` or paths containing quotes. | ADOPT: all FLINT shell→Node config mutation should pass paths via env, not interpolate shell strings into JS. | HIGH |
| 2026-05-11 | F048 | Caveman source: `hooks/caveman-config.js:4-10,39-58`; `skills/caveman-help/SKILL.md:39-55`; `tests/verify_repo.py:301-330` | Default mode resolution supports env var, config file, then `full`; `off` disables session auto-activation while leaving manual `/caveman` available. | BUILD: FLINT should add config defaultMode with `off` for users who want manual activation only. | HIGH |
| 2026-05-11 | F049 | Caveman source: `caveman-compress/scripts/detect.py:8-18,37-59,76-107` | Compress detection skips code/config by extension, JSON/YAML heuristics, and >40% code-like extensionless content; backup `.original.md` never recompressed. | BUILD: FLINT compress should auto-detect natural-language files before API/LLM calls and skip backups. | HIGH |
| 2026-05-11 | F050 | Caveman source: `caveman-compress/scripts/validate.py:41-82,154-168` | Validator handles CommonMark variable-length fences and validates inline-code multiplicity with Counters, catching lost duplicate inline code occurrences. | BUILD: FLINT validate.py should use line-based fence parser + Counter-based inline code preservation. | HIGH |
| 2026-05-11 | F051 | Caveman source: `skills/cavecrew/SKILL.md:16-32,60-79`; `agents/cavecrew-builder.md:14-43` | Cavecrew is not generic delegation; it defines routing thresholds and terminal refusal tokens (`too-big`, `needs-confirm`, `ambiguous`, `regressed`) so main thread can branch cheaply. | BUILD: FLINT delegation agents should return machine-parseable terminal tokens, not prose status. | MEDIUM |
| 2026-05-11 | F052 | Caveman source: `skills/caveman-commit/SKILL.md:22-34,59-65` | Commit skill compresses only safe parts: subject/body rules are terse, but breaking changes/security/data migrations/reverts always get body; no AI attribution or emoji. | ADOPT: keep FLINT commit terse but never subject-only for high-risk commit classes. | MEDIUM |
| 2026-05-11 | F053 | Caveman source: `CLAUDE.md:28-73,220-229`; `.github/workflows/sync-skill.yml:34-115`; `tests/verify_repo.py:124-159` | Caveman treats skill/rule copies as generated artifacts: edit only source-of-truth files, CI syncs copies/ZIP/frontmatter, tests verify byte-identical synced outputs. | BUILD: FLINT needs source-of-truth + sync/test workflow before adding more agent surfaces. | HIGH |
| 2026-05-11 | F054 | Caveman source: `.codex/hooks.json:1-17`; `.codex/config.toml:1-2`; `CLAUDE.md:176-178` | Caveman's Codex surface is much thinner than Claude: static SessionStart echo via codex hooks, no mode flag, no UserPromptSubmit JSON reinforcement, no stats/statusline. | BUILD: FLINT can outperform Caveman on Codex by implementing real mode state + per-turn reinforcement. | HIGH |
| 2026-05-11 | F055 | Caveman source: `evals/plot.py:31-68,71-89,91-146`; `evals/README.md:36-40` | Evals generate boxplots with every prompt point, median, mean, IQR, and zero-control line; this exposes variance instead of hiding behind one average. | ADOPT: FLINT benchmark reports should include per-prompt distribution plots or tables, not only global savings. | MEDIUM |
| 2026-05-11 | F056 | Caveman source: `CLAUDE.md:3-17,220-225` | Caveman explicitly treats README as product UI: non-technical readability, before/after examples first, install table completeness, and benchmark numbers only from real runs. | LEARN: FLINT docs should make benchmark honesty and 60-second install comprehension a review gate. | MEDIUM |
| 2026-05-11 | F057 | Caveman source: `hooks/README.md:59-73`; `hooks/caveman-statusline.sh:13-28,37-49` | Docs' custom statusline snippet reads flag with `cat` and no symlink/whitelist/control-byte hardening, unlike the real statusline script. | REJECT copy-paste snippet: FLINT docs should point users to hardened script or include hardened snippet only. | HIGH |
| 2026-05-11 | F058 | Caveman source: `hooks/package.json:1-3`; `CLAUDE.md:90-91`; `tests/verify_repo.py:176-182` | Hooks directory carries local `{"type":"commonjs"}` and syntax checks so `require()` survives ancestor ESM package configs. | BUILD: FLINT hooks must include package.json CJS marker + syntax checks in verification. | HIGH |
| 2026-05-11 | F059 | Caveman source: `hooks/caveman-mode-tracker.js:11-13,108-128` | Per-turn reinforcement deliberately skips independent modes (`commit`, `review`, `compress`) so base terse style does not conflict with specialized skill behavior. | ADOPT: FLINT per-turn reinforcement should be mode-aware and skip tool/specialist modes. | HIGH |
| 2026-05-11 | F060 | Caveman source: `hooks/caveman-mode-tracker.js:38-62`; `skills/caveman-stats/SKILL.md:1-10`; `tests/test_caveman_stats.js:98-128,445-459` | `/caveman-stats` is hook-executed and returns `decision:"block"` with real script output; model never computes numbers, and stats command preserves current mode flag. | BUILD: FLINT stats should be command/hook-rendered, not model-rendered, to eliminate self-report bias. | HIGH |
| 2026-05-11 | F061 | Caveman source: `skills/caveman-review/SKILL.md:14-33,49-55` | Review mode compresses comments but explicitly drops terse mode for CVE-class/security findings, architecture disagreements, and onboarding contexts. | ADOPT: FLINT review compression must include safety escape hatches for high-context review feedback. | MEDIUM |
| 2026-05-11 | F062 | Caveman source: `install.ps1:175-193,548-581,629-634`; `tests/verify_repo.py:192-209` | Windows installer has separate PowerShell-specific safeguards: avoid `$Args` collision, download remote init to temp file instead of direct pipe, PS 5.1 compatibility check (`-AsHashtable` banned), same partial-failure exit policy. | LEARN: if FLINT supports Windows installers, test PowerShell statically instead of assuming bash logic ports cleanly. | MEDIUM |
| 2026-05-11 | F063 | Caveman source: `tests/verify_repo.py:223-237`; `tests/caveman-compress/todo-list.original.md:1-31`; `tests/caveman-compress/mixed-with-code.original.md:1-90` | Compression validation uses realistic memory fixtures: sprint task lists with names/dates/blockers and mixed prose+TypeScript API docs, not toy strings only. | ADOPT: FLINT compression tests need real-world proxy fixtures with facts, deadlines, code blocks, and security-sensitive prose. | HIGH |
| 2026-05-11 | F064 | Caveman source: `caveman-compress/SKILL.md:48-64`; `caveman-compress/scripts/validate.py:106-184`; `caveman-compress/README.md:139-153` | Compress docs promise exact preservation for dates/numbers/proper nouns/env vars/tables and even "100%" information preserved, but validator only checks headings/code/URLs/paths/bullets/inline code. | REJECT claims; BUILD fact_match validator for dates, numbers, IDs, names, env vars, and table structure before making preservation claims. | HIGH |
| 2026-05-11 | F065 | Caveman source: `README.md:35,117-127,295-297`; `evals/README.md:70-84`; `COMPRESSION_RESEARCH_DB.md:320-335` | Public README still frames output-shortening as proven token compression with 100% technical accuracy, while eval docs admit no fidelity measurement and new DB reframes this as instruction-perturbation. | REJECT current claim style; FLINT docs must say "output-shortening" until fact_match/cosine validates preservation. | HIGH |
| 2026-05-11 | F066 | Caveman source: `tests/test_caveman_init.js:33-109`; `tools/caveman-init.js:64-97` | `caveman-init` has fixture tests for greenfield, idempotence, append-vs-replace, force, dry-run, only-filter, and sentinel detection. | ADOPT: FLINT init must ship fixture tests for every write policy before installer expansion. | MEDIUM |

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
| 2026-05-11 | D010 | opencode-runes ultra: MetaGlyph → NOT→DO contrastive anchoring | A/B data: symbols 54.1% vs NOT→DO 68.8%. Commit 6e83243 → GaiMSdev/opencode-runes main | DONE |
| 2026-05-11 | D011 | 6 experimental arms added to compression_benchmark.py | x_token_budget/50/combined, x_bullets_only, x_negation, x_telegraph, x_schema, x_variable + completeness scoring | DONE — awaits API key |

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

---

## NEXT SESSION: START HERE (prioritert)

1. **caveman-shrink port → flint-shrink MCP proxy** (F021 CRITICAL) — input compression på alle MCP tool descriptions
2. **flag.ts security hardening** (F026 HIGH) — O_NOFOLLOW + atomic + uid verify + size cap
3. **API key → kjør alle 8 nye benchmark arms** — x_token_budget/50/combined/negation/telegraph/schema/variable/bullets
4. **H005 negative-instruction peer review** — arm klar, trenger ≥2 reviews
5. **detect.py + validate.py** (F029) — fullfør flint-compress pipeline
6. **FLINT visible status/stats hardening** (F031/F034 HIGH) — no symlink reads, control-byte strip, no fabricated savings badge, JSONL dedupe by session
7. **FLINT stats memory-savings scan** (F033 HIGH) — report `*.original.md` passive input savings alongside output savings
8. **mcp-shrink config validation** (F038 HIGH) — validate local/server path before TOML mutation; print manual fallback on failure
9. **flint-init sentinel + write policy** (F041 HIGH) — append shared files, replace IDE-local rules only with force
10. **flint-compress no-op/fence guards** (F042 HIGH) — strip outer wrapper fences; abort on empty/identical output before disk writes
11. **flint-shrink metadata-only contract** (F043/F045 HIGH) — compress list metadata only; configurable field allowlist; no tool-call output mutation
12. **flint hook installer merge/uninstall tests** (F046/F047 HIGH) — env-passed paths, preserve existing statusline/hooks, exact uninstall restore
13. **FLINT defaultMode config** (F048 HIGH) — env/config/off resolution with manual activation available
14. **flint-compress detector + stronger validator** (F049/F050 HIGH) — skip code/config/backups; CommonMark fence parser; inline-code Counter preservation
15. **FLINT source-of-truth sync workflow** (F053 HIGH) — generated copies/ZIP/frontmatter sync + byte-identity verification
16. **Codex-native mode state** (F054 HIGH) — use FLINT's Codex surface to beat Caveman static echo with state + reinforcement
17. **Benchmark variance visualization** (F055 MEDIUM) — per-prompt dots/median/IQR or equivalent table for every reported result
18. **Harden statusline docs/snippets** (F057 HIGH) — no unsafe `cat` snippets; docs must reuse hardened statusline reader
19. **CJS hook package marker** (F058 HIGH) — add `hooks/package.json` + syntax verification for every JS hook
20. **Hook-rendered FLINT stats** (F060 HIGH) — `/flint-stats` should block prompt and return script output, never model-estimated numbers
21. **Real-world proxy compression fixtures** (F063 HIGH) — task lists + mixed prose/code docs with fact_match scoring, not toy strings

---

## MECHANISM HYPOTHESES (M021-M030) — Codex/OpenCode caveman absorption 2026-05-11

**Empiriske mønstre fra reverse-engineering. Ikke 100% bevist, men sterkt observert.**

### M021 — Anchor-strength via prompt-storrelse
Caveman 1915c persisterer bedre enn FLINT 160c. Tette regelsett overlever context-kompaktering.
**Implikasjon:** Større, tettere FLINT SKILL.md kan lukke deler av 21pp-gap.
**TESTABLE:** Bygg FLINT-large variant (~2000c), sammenlign retention over 20 turns.

### M022 — Compression vs fact-preservation = antagonistic
Ultra_glyph hadde 9-82% varians fordi attention-budget er fast. Kompresjon vinn over bevaring uten eksplisitt fact-rule.
**Implikasjon:** Trenger eksplisitt "PRESERVE: numbers, IDs, exact strings" linje.

### M023 — NOT→DO contrastive lærer transformasjon
+14pp savings fordi modellen ser hele verbose→terse vegen, ikke bare constraint.
**Implikasjon:** Legg NOT→DO eksempler i SKILL.md (allerede delvis i ultra).

### M024 — Token-priors over symbol-rarity
→ vinn over ∈∀∃∴ fordi pretraining-priors. Vanlige symboler = stabil output. MetaGlyph sjeldne → varians.
**Implikasjon:** IKKE introdusere eksotiske symboler. Hold til ASCII + → arrows.

### M025 — Per-turn reinforcement = anti-drift
Context vokser → SessionStart-attention krymper → reinforcement re-anchorer.
**Implikasjon:** Vår UserPromptSubmit-hook gjør dette riktig. Behold.

### M026 — Wenyan retention-kollaps mistenkt
75% savings-claim, men sannsynlig retention-kollaps på tall/IDs. IKKE TESTET.
**TESTABLE:** Kjør wenyan med fact_match_score på tall-tunge prompts.

### M027 — Hard budget H006 = kort-cut + risiko
Vinner fordi fjerner "hvor mye"-avgjørelse. Risiko: trunkering.
**STATUS:** H006 arms i v2 nå, klar for test.

### M028 — Long conversation amortiserer system-prompt
Fast kost (system prompt) deles på flere turns → bedre relativ savings.
**Implikasjon:** Vårt long_conversation-scenario er korrekt val.

### M029 — Terse vinner over strukturerte modus
"Be concise" har sterke RLHF-priors. Strukturerte regelsett trigger "hvordan-følge"-CoT før svar.
**Implikasjon:** Mindre regler kan paradoksalt gi MER savings. Test "FLINT minimal" variant.

### M030 — Norsk 30-50% dyrere (tokenizer)
Engelsk-dominert vokabular. Norsk-tokens er multibyte.
**Implikasjon:** Vår "ultra: English for technical" regel er korrekt.

---

## STØRSTE INSIGHT — REFRAME

**Vi måler ikke "kompresjon" — vi måler "hva modellen velger å skrive".**

Caveman er IKKE kompressor. Det er instruction-perturbation som flytter output-distribusjon mot kortere svar med RISIKO for faktatap.

**Konsekvenser:**
1. "Savings %" alene er villedende metrikk — krever fact_preservation
2. 21pp-gap til caveman er kanskje illusorisk — caveman bytter savings mot faktatap
3. fact_match + cosine_sim må være FØRSTEKLASSES metrikker, ikke afterthoughts
4. Ny baseline: "savings/fact_loss ratio" = ekte effektivitet

**STRATEGISK SKIFTE:**
- Stopp jakten på max savings %
- Mål: max savings/(fact_loss + cosine_drop) ratio
- Test caveman med fact_match — kanskje deres -68% er -50% faktisk-effektiv
