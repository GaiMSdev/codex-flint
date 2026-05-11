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
| M031 | gem-thal-hybrid | Broken-English + abbrev mode. Cross-platform flag detection (Claude/Windsurf/Cursor/Cline/Codex). "Me" + subject/verb fragments. 94 LOC. | ~92%* | unknown | unknown | Gemini | UNVALIDATED |
| M032 | wenyan-charpoet | Classical Chinese literary compression (之其者也矣). CharPoet (arXiv:2401.03512) validerer: token-free > token-based (0.96 vs 0.84 format accuracy) for classical Chinese. | unknown | unknown | unknown | All | HYPOTHESIS |
| M035 | skill-engineering-patterns | Skill engineering design guide (Articsledge Apr 2026). Skills ≠ prompts. Progressive loading ~30-50 tok/skill. Need: scope conditions, negative examples, success criteria. | N/A (guide) | N/A | N/A | All | ADOPT |
| M036 | context-mode-external-log | Context Mode (MindStudio May 2026): 63× compression via SQLite event log utenfor samtalen. Sandbox-filter tool output→context. Snapshot injection etter compaction. | 63× (315KB→5KB) | N/A | kvalitativ | Claude Code | HYPOTHESIS |

*M006 flint-compact: CLI benchmark invalid (78k input-token contamination). API benchmark pending.
*M009 runes-hybrid: self-reported by Gemini agent, no external validation yet.
*M031 gem-thal-hybrid: Distinct from M009 (no MetaGlyphs). Same "broken-English" concept but pure abbrev, no symbols. 94 LOC, 129 total. Self-reported estimate.
*M032 wenyan-charpoet: CharPoet paper validerer M026 — tokenized models show 12pp format accuracy drop vs token-free for classical Chinese. Wenyan compression risk is real.
*M036 context-mode-external-log: MindStudio blog May 5, 2026. 63× compression published benchmark. Local SQLite, no telemetry. Complementary to FLINT.

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
| 2026-05-11 | F067 | Caveman source: `skills/caveman/SKILL.md:11-26,28-37,39-52,54-74`; `hooks/caveman-activate.js:50-91` | Exact mode prompt source is one shared SKILL.md; SessionStart strips frontmatter then filters intensity table/example bullets to only active mode, so `full`, `ultra`, and `wenyan-full` share persistence/rules/auto-clarity wording but receive only their own row/examples. | BUILD: make FLINT SessionStart read one source-of-truth prompt file and filter mode examples instead of duplicating prompt text across hook/SKILL/docs. | HIGH |
| 2026-05-11 | F068 | Caveman source: `hooks/caveman-mode-tracker.js:108-128`; `tests/verify_repo.py:341-355` | Per-turn reinforcement is intentionally mode-light: `CAVEMAN MODE ACTIVE (<mode>). Drop articles/filler/pleasantries/hedging. Fragments OK. Code/commits/security: write normal.`; it anchors attention, not full rules. | ADOPT: keep FLINT UserPromptSubmit one-line reinforcement short; do not re-inject full prompt every turn. | HIGH |
| 2026-05-11 | F069 | Caveman source: `benchmarks/run.py:52-68,78-145,184-202,239-270`; `benchmarks/prompts.json:3-53` | API benchmark is simple but stronger than self-report: real Anthropic usage tokens, 10 dev prompts, `temperature=0`, 3 trials default, medians, raw response JSON, skill hash, optional README table update. | ADOPT: keep OnePlayer benchmark raw-output storage, input hashes, repeats, medians, and deterministic model settings as minimum bar. | HIGH |
| 2026-05-11 | F070 | Caveman source: `evals/llm_run.py:1-16,40-51,85-100`; `evals/README.md:7-19,70-84`; `evals/measure.py:57-103` | Secondary eval harness uses Claude CLI snapshots with arms `baseline`, `terse`, and `terse+skill`; docs explicitly say skill delta is vs terse and that fidelity/statistical significance are not measured. | ADOPT: publish FLINT deltas vs terse as primary skill effect; mark output-only evals TESTED, never VALIDATED. | HIGH |
| 2026-05-11 | F071 | Caveman source: `hooks/caveman-config.js:16-20,39-58`; `tests/verify_repo.py:301-330` | Default mode accepts independent modes and `off`; `/caveman` with default `off` intentionally does not write a flag, enabling installed-but-manual workflows. | ADOPT: FLINT should test `CODEX_FLINT_DEFAULT_MODE=off` and config fallback so hooks can be installed without surprise auto-activation. | MEDIUM |
| 2026-05-11 | F072 | OpenCode #3 source read: `gem-thal/lib/runes-core.js:94,114-120` | gem-thal HYBRID mode: pure abbrev + broken-English, distinct from M009 (no MetaGlyphs). 94 LOC, 129 total. Cross-platform flag detection (Gemini/OpenCode/Claude dirs). Savings estimate self-reported ~92%. No external benchmark. | M031: distinct cross-platform method candidate. Replicate and benchmark before ADOPT. | MEDIUM |
| 2026-05-11 | F073 | CharPoet paper (arXiv:2401.03512) | Token-free classical Chinese generation achieves 0.96 format accuracy vs 0.84 for token-based models. Tokenized models lose 12pp on classical Chinese literary form. Supports M026: wenyan retention-collapse risk is structural, not just prompt-design issue. | M032: wenyan compression may introduce format accuracy risk for tokenized LLMs. Baseline fact_match measurement essential before trusting wenyan savings. | MEDIUM |
| 2026-05-11 | F074 | TRIM paper (arXiv:2412.07682) — JPMorganChase AI Research | LLM kan generere "distilled language" (utelate semantisk irrelevante/enkelt gjenkjennelige ord) via prompting. Two-stage: LLM→distilled→smaller LM reconstructs full narrative. GPT-4o: 19.4% avg token savings, tiny metric decrease på NaLDA. | Validerer instruction-perturbation approach (F065). Vår savings er høyere fordi vi hopper over reconstruction stage. TRIMs 19.4% er lavere enn våre 50-70% pga reconstruction overhead + konservativ målsetning. Ekstern validering: LLMs CAN compress via instructions alone. | MEDIUM |
| 2026-05-11 | F075 | CompactPrompt (arXiv:2510.18043) — training-free hard compression pipeline | 60% token savings på TAT-QA/FinQA med bevart eller forbedret accuracy. Embedding similarity ≥0.92 = safe compression threshold, men moderate drops skader ikke downstream performance. Claude 3.5 Sonnet viste +6-10pp accuracy gain med compression + exemplars. | Validerer at instruction-based compression kan gi ≥50% savings UTEN accuracy loss. Embedding-based quality gate (≥0.92) er enklere enn fact_match for generell bruk. Foreslår multi-pronged evaluation (embedding + human + LLM-as-judge + task accuracy). | MEDIUM |
| 2026-05-11 | F076 | SkillReducer (arXiv:2603.29919) — skill debloating for LLM agent skills | Analyse av 55 315 skills: systematiske ineffektiviteter i routing/body layers. To-stage: delta-debugging description compression + taxonomy-driven progressive disclosure. 86% pass rate, 100% på SkillsBench. Komprimerte skills forbedret funksjonalitet med +2.8% — "less-is-more" effekt. | Direkte relevant for FLINT skill-design. "Less-is-more" validerer vår FLINT-Compact hypothesis (M006). Token-budget comparison: SkillReducer slår LLMLingua, direkte LLM compression, truncation, random removal. Transferable across 5 models from 4 families. | MEDIUM |
| 2026-05-11 | F080 | Caveman source: `.github/workflows/sync-skill.yml:3-17,34-74,76-115`; `tests/verify_repo.py:124-159` | Cross-platform sync is automated from source files into plugin, Cursor, Windsurf, Cline, Copilot, ZIP, and compress-skill copies; verification asserts byte-identical synced outputs and ZIP payload. | BUILD: FLINT needs CI sync + verification before adding more agent surfaces, otherwise prompt drift will become unreviewable. | HIGH |
| 2026-05-11 | F081 | Caveman source: `tests/test_symlink_flag.js:37-190,193-218`; `tests/test_caveman_stats.js:433-443` | Security tests cover normal writes, symlinked parent dirs, symlinked flag refusal, 0600 perms, broken symlink silent fail, all valid modes, ownership-check source audit, and symlink-safe history append. | BUILD: expand F054 tests with env/config/default-mode, symlink refusal, history append, permissions, and source-audit checks before next hook hardening commit. | HIGH |
| 2026-05-11 | F082 | Caveman source: `tests/verify_repo.py:162-189,192-209,223-263,266-396,399-418` | `verify_repo.py` is an integration gate spanning manifests, JS/bash syntax, PowerShell static wiring, compress fixtures, CLI skip/error paths, hook install/uninstall idempotence, custom statusline preservation, and exact uninstall restore. | ADOPT: add one FLINT verification runner that exercises install surfaces end-to-end, not just unit/smoke tests. | HIGH |
| 2026-05-11 | F083 | Caveman source: `skills/compress/scripts/compress.py:155-180,185-225,227-253`; `skills/compress/scripts/cli.py:62-81` | Compress flow fails closed: size cap, sensitive-path refusal, skip non-natural-language files, refuse empty/identical LLM output, do backup readback before primary write, restore original and delete backup after validation retries fail. | BUILD: FLINT compress must adopt fail-closed rollback/backup verification before any automated memory compression. | HIGH |
| 2026-05-11 | F084 | Caveman source: `skills/compress/scripts/cli.py:11-20,75-81`; `tests/verify_repo.py:39-58,192-209` | CLI and verification force UTF-8/error replacement so Windows consoles do not crash on glyph/error output and mask the real failure; PowerShell checks ban PS 7-only constructs. | ADOPT: FLINT scripts should set UTF-8-safe output and include PowerShell/static checks before Windows support claims. | MEDIUM |
| 2026-05-11 | F085 | Caveman source: `hooks/caveman-mode-tracker.js:65-99,101-119`; `hooks/caveman-activate.js:18-28,42-49` | State machine is file-backed and last-writer-wins: SessionStart writes configured default, `/caveman <mode>` overwrites flag, `normal mode`/stop unlinks it, independent modes are written but skipped for base reinforcement. | ADOPT: keep FLINT mode transitions simple and inspectable, but test last-writer behavior and specialist-mode skip paths explicitly. | HIGH |
| 2026-05-11 | F090 | CoD repo configs (github.com/sileix/chain-of-draft/configs/) — few-shot YAML analysert | CoD few-shot pattern: hver "step" = én ligning eller én logisk assertjon. Maks ~5 ord/step. Sports: `[Player]: [sport]; [Action]: [sport].` — Math: `21 - 15 = 6.` #### [svar]. Few-shot lærer formatet implisitt; 5-word limit er retningslinje, ikke tvang. | M033: CoD for reasoning-only. Kan kombineres med FLINT modes for sub-tasks som krever reasoning (debugging, planlegging). Ekstraher "one equation per step" pattern som generaliserbar teknikk. | MEDIUM |
| 2026-05-11 | F086 | Caveman source: `hooks/caveman-config.js:147-189`; `hooks/caveman-mode-tracker.js:115-118,130-132`; `hooks/caveman-activate.js:52-58,93-110,139-140` | Error recovery is fail-open for hooks: corrupted/oversized/symlink flag returns null and emits no reinforcement; malformed hook input or filesystem failures silent-fail; missing SKILL.md falls back to embedded minimal rules. | ADOPT: FLINT hooks should never block agent startup on local state corruption; add explicit tests for bad JSON, invalid flag, oversized flag, and missing prompt source fallback. | HIGH |
| 2026-05-11 | F087 | Caveman source: `hooks/caveman-mode-tracker.js:25-36,65-92,101-106` | Prompt-input gating is regex-based, not injection-aware: natural-language activation fires on broad `activate/enable/turn on/start/talk like` + `caveman`; unknown slash args leave flag untouched; stop terms override activation in the same prompt. | LEARN/BUILD: FLINT should preserve unknown-arg no-op and stop-over-activate precedence, but harden against quoted/instructional mentions accidentally toggling mode. | HIGH |
| 2026-05-11 | F088 | Caveman source: `hooks/install.sh:137-164`; `hooks/caveman-mode-tracker.js:38-62`; `mcp-servers/caveman-shrink/index.js:57-71,111-125` | Hot paths are bounded: Claude hook config sets 5s timeout for SessionStart/UserPromptSubmit; stats command subprocess has 5s timeout; MCP proxy line-buffers and pass-throughs unparsable/request traffic instead of blocking on full-stream parsing. | ADOPT: FLINT hook work must stay O(prompt length) and bounded by hook timeout; heavy stats/benchmark work should be block-command only, not per-turn reinforcement. | HIGH |
| 2026-05-11 | F089 | Caveman source: `README.md:136-172`; `install.sh:455-472,560-588,684-697,778-782`; `install.ps1:372-422,493-499,535-542,614-630` | Update mechanism is "safe to re-run" installer + native package managers, not auto-update: skips already-installed targets unless `--force`, records installed/skipped/failed, falls back to npx-skills auto-detect, and exits nonzero only if every detected target failed. | ADOPT: FLINT should prefer explicit reinstall/force update flow with clear summary; avoid background auto-update for hooks/config. | MEDIUM |
| 2026-05-11 | F090 | Caveman source: `hooks/caveman-statusline.sh:37-49`; `hooks/caveman-statusline.ps1:41-60`; `hooks/caveman-stats.js:322-329` | Statusline performance avoids Node/JSON parsing on every render: stats pre-renders a tiny suffix file, and shell/PowerShell statusline only reads capped 64-byte files with control-byte stripping. | BUILD: FLINT status UI should use pre-rendered, capped text from stats, not parse session JSONL from the statusline hot path. | HIGH |
| 2026-05-11 | F091 | Caveman source: `tests/verify_repo.py:301-367`; `hooks/caveman-mode-tracker.js:25-36,65-92,101-106` | Transition tests cover default env, `off`, `/caveman ultra`, and `normal mode`, but not natural-language activation, unknown slash args, quoted examples, or stop+activate collision strings. | BUILD: FLINT should add transition fuzz tests before broad natural-language activation; current Caveman behavior is useful but under-tested. | HIGH |
| 2026-05-11 | F092 | Local timing 2026-05-11: `node hooks/caveman-activate.js` n=30 vs `node scripts/flint-activate.js` n=30; source: `hooks/caveman-activate.js:18-91`; `scripts/flint-activate.js:12-33` | SessionStart startup cost is dominated by Node spawn, not prompt logic: Caveman avg 51.87ms/p50 51.37ms/p95 55.81ms; FLINT avg 51.45ms/p50 51.39ms/p95 54.48ms. | LEARN: F054 does not add measurable startup penalty vs Caveman; optimize by avoiding extra processes, not micro-optimizing JS string work. | MEDIUM |
| 2026-05-11 | F093 | Caveman source: `mcp-servers/caveman-shrink/package.json:21-30`; `hooks/caveman-activate.js:9-12`; `hooks/caveman-mode-tracker.js:5-9`; `caveman-compress/scripts/compress.py:79-99`; `caveman-compress/scripts/benchmark.py:12-22` | Runtime dependencies are deliberately thin: hooks use Node stdlib only, MCP shrink package declares no dependencies, compression uses optional `anthropic` or Claude CLI fallback, benchmark uses optional `tiktoken` with word-count fallback. | ADOPT: keep FLINT hook/MCP paths dependency-free; optional deps only in offline benchmark/compress tools with graceful fallback. | HIGH |
| 2026-05-11 | F094 | Caveman source search: runtime hooks/MCP require only `fs/path/os/child_process`; network URLs appear in installers/docs: `install.sh:18-19,491-501,507-553`; `install.ps1:37-38,411-422,428-439`; `mcp-servers/caveman-shrink/package.json:6-10` | No runtime telemetry/phone-home/update-check code found in hooks, statusline, MCP proxy, or stats; network use is installer/package-manager only (GitHub raw, npm registry probe, native plugin install). | ADOPT: FLINT should keep privacy posture explicit: no runtime telemetry, network only on user-invoked install/update/benchmark/compress. | HIGH |
| 2026-05-11 | F095 | Caveman source: `.claude-plugin/plugin.json:1-33`; `plugins/caveman/.codex-plugin/plugin.json:1-39`; `gemini-extension.json:1-5`; `.agents/plugins/marketplace.json:1-19`; `.codex/hooks.json:1-17`; `.codex/config.toml:1-2` | Marketplace distribution is per-surface, not one universal manifest: Claude plugin carries hook registrations with 5s timeouts; Codex plugin carries UI/defaultPrompt only; Gemini extension uses `contextFileName`; Agents marketplace points to local plugin path; Codex hooks live separately. | BUILD: FLINT needs surface-specific manifests generated from source, with tests that each surface gets the right capabilities instead of assuming plugin metadata transfers. | HIGH |
| 2026-05-11 | F096 | Caveman source: `commands/caveman.toml:1-2`; `commands/caveman-init.toml:1-3`; `tools/caveman-init.js:64-97` | TOML commands are intentionally thin prompt frontends; stateful/risky writes stay in JS tools, and `/caveman-init` command tells the agent to dry-run first unless user passed `--force`. | ADOPT: keep FLINT/OpenCode TOML commands declarative; put filesystem/config mutation in scripts with dry-run/force semantics. | MEDIUM |
| 2026-05-11 | F097 | Caveman source: `CLAUDE.md:3-16,220-225` | Maintainer rules treat README as product UI: non-technical readability, before/after examples first, complete install table, synced feature matrix, preserved brand voice, and benchmark numbers only from real runs. | ADOPT: FLINT docs PRs should gate on install comprehension + benchmark honesty, not just technical correctness. | MEDIUM |
| 2026-05-11 | F098 | Caveman source: `CLAUDE.md:26-60,63-73,222-223`; `.github/workflows/sync-skill.yml:34-94` | Source-of-truth discipline is explicit: edit only core `skills/`, `rules/`, and agent source files; generated copies are overwritten by CI and must not be edited directly. | BUILD: FLINT needs a generated-artifact map plus test/CI enforcement before adding more duplicated skill/plugin surfaces. | HIGH |
| 2026-05-11 | F099 | Caveman source: `CLAUDE.md:170-191`; `install.sh:639-682`; `install.ps1:286-344` | New-agent support is treated as a matrix contract: verify upstream `npx skills` profile slug, update bash + PowerShell matrices row-for-row, mark soft probes, and run both `--list` outputs. | ADOPT: FLINT installer expansion should require paired Unix/Windows matrix updates and profile-slug verification. | MEDIUM |
| 2026-05-11 | F100 | Caveman source: `tools/caveman-init.js:1-18,55-62,64-97,112-126` | `caveman-init` is standalone-safe: embeds fallback rule text, prefers in-repo source if available, uses sentinel idempotence, append vs replace policy, and exposes `--dry-run`, `--force`, `--only`. | BUILD: FLINT init should be runnable from curl/npx without repo context while still preferring source-of-truth when present. | MEDIUM |
| 2026-05-11 | F101 | Caveman source: `CLAUDE.md:227-229`; `hooks/caveman-config.js:61-80,147-158`; `hooks/install.sh:128-129`; `hooks/uninstall.sh:61-65` | Hook anti-patterns are explicitly banned: hooks must silent-fail, flag writes must use safe helper, hooks/installers must respect config-dir env vars, and shell→Node config mutation passes paths via env to avoid `$HOME` quoting injection. | ADOPT: make these FLINT hook review checklist items. | HIGH |
| 2026-05-11 | F102 | Caveman source: `.claude-plugin/marketplace.json:1-17`; `.claude-plugin/plugin.json:1-34`; `plugins/caveman/.codex-plugin/plugin.json:1-39`; `gemini-extension.json:1-6`; `.agents/plugins/marketplace.json:1-20`; `.codex/hooks.json:1-17`; `.cursor/rules/caveman.mdc:1-20`; `.windsurf/rules/caveman.md:1-19` | Marketplace format is a per-surface contract set: Claude marketplace indexes plugins, Claude plugin registers hooks, Codex plugin exposes UI/defaultPrompt, Gemini points to context file, Agents marketplace points to local plugin, Codex hooks/config enable hooks, Cursor/Windsurf use frontmatter. | BUILD: generate and verify every FLINT surface manifest from one source map; do not rely on one plugin manifest to express all runtime behavior. | HIGH |
| 2026-05-11 | F103 | Caveman source: `.claude-plugin/plugin.json:8-33`; `.codex/hooks.json:3-12`; `hooks/install.sh:137-164`; `hooks/install.ps1:128-155` | Hook manifests consistently bound SessionStart/UserPromptSubmit commands with `timeout: 5` and human `statusMessage`; Claude plugin uses `${CLAUDE_PLUGIN_ROOT}` while standalone installers write absolute/user-config paths. | ADOPT: FLINT hook manifests should include explicit timeout/status text and use surface-native path expansion instead of shell-resolved relative paths. | HIGH |
| 2026-05-11 | F104 | Caveman source search: `rg "hrtime|performance.now|startup.*ms|hook.*ms"` found no hook timing instrumentation; `hooks/caveman-statusline.sh:37-49`; `hooks/caveman-stats.js:322-329`; `.claude-plugin/plugin.json:14-28` | Caveman does not self-instrument hook latency with hrtime; performance strategy is bounding hooks by manifest timeout and keeping statusline hot path to capped file reads from a pre-rendered suffix. | LEARN/BUILD: add FLINT hook-latency measurement only in debug/benchmark mode; production hot path should stay timeout-bounded and pre-rendered. | MEDIUM |
| 2026-05-11 | F105 | Caveman source: `hooks/caveman-stats.js:1-19,128-129,242-250`; `benchmarks/run.py:78-140,184-198,241-263`; `evals/README.md:4-17,32-40,82`; `evals/measure.py:66-103` | Savings reporting is split: stats uses a hardcoded measured `full: 0.65` from committed benchmark JSON, API benchmark defaults to 3 trials, eval snapshots compare baseline/terse/terse+skill but explicitly note single-run statistical limits. | ADOPT: FLINT runtime stats must only surface benchmark-backed estimates and mark single-run evals as tentative under the new validation policy. | HIGH |
| 2026-05-11 | F106 | Caveman source: `CLAUDE.md:14,28-60,71,98,107,190,214-216,227-229`; `install.sh:229,418,778-779`; `hooks/caveman-mode-tracker.js:91,118`; `hooks/caveman-statusline.sh:37-42` | Code comments encode maintainer doctrine: benchmark numbers must be real, synced copies must not be edited directly, hooks silent-fail, predictable writes go through safeWriteFlag, BSD awk pitfalls matter, unknown args must not overwrite mode, never inject untrusted flag bytes. | BUILD: promote these into FLINT's contributor/review checklist so hidden implementation rules survive future agent edits. | HIGH |
| 2026-05-11 | F107 | Caveman source: `install.sh:1-10,23-28,447-557,560-620,622-739,742-782`; `README.md:130-158` | Install flow is staged UX: print banner, detect native agents, install via native mechanism, wire Claude extras by default, degrade MCP to manual snippet, optionally write per-repo rules, then summarize installed/skipped/failed with next command. | ADOPT: FLINT installer should be staged and idempotent with explicit result buckets instead of a monolithic done/failed message. | HIGH |
| 2026-05-11 | F108 | Caveman source: `install.sh:64-65,460-472,563-570,778-782`; `hooks/install.sh:48-99`; `README.md:156`; `hooks/uninstall.sh:23-31,122-130` | Upgrade experience is safe re-run plus `--force`, not auto-update: already-installed targets are skipped with force guidance, hook installer verifies full current file set before no-op, uninstall detects plugin install and redirects to native disable command. | ADOPT: FLINT should offer explicit reinstall/force and native uninstall guidance; avoid hidden background upgrades for hooks/skills. | HIGH |
| 2026-05-11 | F109 | Caveman source: `install.sh:161-180,243,491-552,599-617,769-776`; `hooks/install.sh:27-32,183-199`; `hooks/uninstall.sh:53-57`; `hooks/caveman-stats.js:288-300`; `skills/compress/scripts/cli.py:11-20,72-81` | Error messages are short but recovery-oriented: say missing dependency, exact re-run/manual config path, preserve custom statusline, print nothing-detected fallback, and keep validation/glyph errors readable on Windows. | BUILD: FLINT error UX should include next action in every failure string and preserve user-owned config by default. | HIGH |
| 2026-05-11 | F110 | Caveman source: `hooks/README.md:1-35,59-93,95-107`; `docs/install-windows.md:1-59`; `README.md:160-172,174-191` | Docs cover operational fallback paths: hook architecture, custom statusline merge snippet, manual uninstall, Windows plugin-skill fallback, Codex-on-Windows caveat, npx symlink fallback, and always-on prompt snippet for unsupported agents. | ADOPT: FLINT docs need an escape-hatch section for custom statusline/config, Windows/manual setup, and unsupported-agent always-on text. | MEDIUM |
| 2026-05-11 | F111 | Caveman source: `docs/index.html:220-259,300-349`; `README.md:39-76,115-128,266-305` | Public-facing docs are example-first and visual: before/after diff, token bars, command terminal, feature matrix, and benchmark/eval reproduction commands; however public copy still uses stronger accuracy/savings language than the new fact-match policy would allow. | LEARN/ADOPT: keep FLINT docs example-first, but gate all savings/accuracy copy through validation status and fact-match caveats. | MEDIUM |
| 2026-05-11 | F112 | Caveman source: `hooks/caveman-config.js:1-10,16-19,22-58,78-82`; `install.sh:148-194,214-216`; `mcp-servers/caveman-shrink/index.js:24-41`; `skills/compress/scripts/compress.py:75-84`; `hooks/caveman-statusline.sh:37-45` | Config overrides have clear precedence: env `CAVEMAN_DEFAULT_MODE`, then XDG/APPDATA config `defaultMode`, then `full`; installer flags override auto defaults; shrink fields/debug, compress model/API key, and statusline savings are env-driven. | BUILD: document FLINT override matrix with precedence, valid values, defaults, and per-surface availability. | HIGH |
| 2026-05-11 | F113 | Caveman source: `benchmarks/run.py:184-202,241-272`; `README.md:266-289`; local cache `benchmarks/results/.gitkeep` only; `evals/snapshots/results.json:5`; `evals/README.md:70-84` | Benchmark script saves raw JSON and README reports 65% average, but the plugin cache has no committed benchmark result JSON; eval snapshot is committed for Opus 4.6 and explicitly says fidelity/statistical significance are not measured. | BUILD: FLINT benchmark claims must link to committed raw artifacts in the same repo/cache and mark no-fidelity/single-run limits next to the table. | HIGH |
| 2026-05-11 | F114 | Caveman source: `hooks/caveman-activate.js:12-18,27-58,60-111,113-143`; `hooks/caveman-mode-tracker.js:8-16,38-62,65-129`; `hooks/caveman-stats.js:10-19,281-329`; `mcp-servers/caveman-shrink/index.js:29-45,73-125` | Internal architecture is thin event modules around shared state: config helper owns mode/default/security IO; SessionStart writes flag + emits rules; UserPromptSubmit mutates flag/runs stats/emits reinforcement; stats writes history/suffix; shrink is separate stdio proxy. | ADOPT: keep FLINT modules similarly single-purpose; shared config/security helper should be the only IO primitive used by hooks. | HIGH |
| 2026-05-11 | F115 | Caveman source: `install.sh:23-24,270-353,416-418`; `install.ps1:1,177,240-242,286-344,385-414,549-574`; `hooks/caveman-config.js:22-32,73-74,137`; `hooks/caveman-activate.js:123-131`; `docs/install-windows.md:1-46` | OS-specific handling is explicit: bash stays Bash 3.2-safe, PowerShell has parallel matrix not generated, Windows config uses APPDATA, uid checks degrade to home-path check, statusline command switches ps1 vs sh, docs provide Windows manual/symlink fallbacks. | ADOPT: FLINT Windows support needs a first-class PowerShell path and documented degraded security semantics, not best-effort Unix scripts. | HIGH |
| 2026-05-11 | F116 | Caveman source: `CONTRIBUTING.md:1-22`; `caveman-compress/SECURITY.md:1-31`; `README.md:313-320`; `docs/install-windows.md:1-3`; `hooks/README.md:31-35` | Community/docs are minimal but practical: PRs must include before/after examples and one-sentence rationale, generated copies are off-limits, security false positives get a plain threat-model note, Windows fallback cites issue numbers. | ADOPT: FLINT community docs should require before/after examples for prompt changes and separate security threat-model notes for scary-looking tools. | MEDIUM |
| 2026-05-11 | F117 | Caveman source: `skills/compress/scripts/compress.py:19-57,155-174`; `caveman-compress/SECURITY.md:7-27`; `mcp-servers/caveman-shrink/README.md:35-50` | Data-boundary policy is conservative: compress refuses secret-looking paths before read/API call and has no override except rename; shrink explicitly avoids requests/tool-call bodies; security doc states exactly what can leave machine. | BUILD: FLINT compression tools should fail closed on sensitive paths and document data egress per tool before enabling automatic memory compression. | HIGH |

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

---

## ACADEMIC RESEARCH UPDATE — Gemini 2026-05-11 09:35

### M033 — Chain-of-Draft (CoD) [Xu et al, 2025]
**92% reasoning reduction, 100% accuracy retention.**
Pattern: minimal "draft" intermediate steps i stedet for verbose CoT.
Eks: "X = 1+2+3 = 6. Answer: 6" istedet for "Let me think. To find X..."
**STATUS:** UNTESTED i FLINT. Hvis claims holder = SLÅR caveman_full (-68%) med margin.
**Vurdering:** BUILD — TOP-PRIO ny test-arm. 90% tro hvis akademisk replikasjon mulig.

### H005 nedgradert — Negative-Instruction risiko
Akademisk: 'Negative Instructions' = high-risk performance inhibitors.
Bekrefter TELEGRAPH-failure-pattern empirisk.
**STATUS:** H005 tro nedgradert 40% → 25%. Test fortsatt, men ikke forvent gjennombrudd.

### H007 nyansert — Persona Anchoring vs Role Play
Akademisk: 'Persona Anchoring' (anker identitet) > 'Role Play' (spill rolle) for long-context loyalty.
TELEGRAPH-failure var role-play ("you ARE telegraph operator from 1890") — ikke anchoring.
Persona Anchoring eks: "You communicate like a senior engineer — brief, direct, technical."
**STATUS:** H007 re-vurder. Test som ANCHORING ikke ROLE PLAY.

---

## M034 — Cross-run varians er ENORM (Claude koder offline analyse 2026-05-11)

**Empirisk funn fra analyze_offline_facts.py mot benchmark_flint_compact.json:**

| Mode | Output | Raw savings | fact_match | Effective |
|------|--------|-------------|-----------|-----------|
| terse | 3690 | +30.35% | 1.000 | +30.35% |
| baseline | 5298 | 0.00% | 1.000 | 0.00% |
| flint_compact | 9393 | -77.29% | 1.000 | -77.29% |
| caveman_ultra | 14966 | -182.48% | 1.000 | -182.48% |

**KRITISK:**
1. Alle 4 modes recall 5/5 fakta perfekt (fact_match=1.000) — fact_match var IKKE problemet
2. caveman_ultra EKSPANDERTE 3x baseline i denne kjøringen — motsatt av BM001 (+72%)
3. terse var EINASTE som komprimerte (+30%)
4. Cross-run varians = ENORM. Single-run data = STØY.

**KONSEKVENSER:**
- Vi kan IKKE konkludere på 21pp-gap fra single-run data
- "FLINT 21pp bak caveman" = potensielt MÅLINGS-STØY, ikke ekte
- terse vinner faktisk på BÅDE savings + retention i denne kjøringa
- Trenger n_repeats≥5 + median+CI før noen claims er gyldige
- VALIDERER demokrati-konsensus (Q1 = n_repeats=5 + bootstrap CI)

**STRATEGISKT SKIFTE:**
- Vi har sannsynligvis OVERVURDERT caveman sin fordel
- "Be concise" (terse) har sterke RLHF-priors og kan være konkurransedyktig alene
- Bygging av store SKILL.md-er (M021 hypothesen) trenger n=5 validering FØR vi committer mer

**BLOKKERING:**
- Trenger ANTHROPIC_API_KEY for n=5 multi-run validation
- ALT D/E status fortsatt åpent

---

## M033 OPPDATERT — Chain-of-Draft (Xu et al 2025) EKSAKT prompt funnet

**arXiv:2502.18600 | Code: github.com/sileix/chain-of-draft**

KEY FINDINGS:
- 92.4% færre ord (Claude 3.5 Sonnet sports: 189.4→14.3 tokens)
- 7.6% av original token usage best case
- 80% reduksjon på GSM8k
- Matcher eller slår CoT i accuracy
- Funker MED few-shot examples (zero-shot signifikant dårligere)
- Begrenset på små modeller (<3B params)

**KRITISK OMVURDERING:**
CoD er KUN for reasoning tasks (math/common sense/symbolic).
IKKE direkte overførbart til FLINT general output compression.

**DELVIS APPLICABILITET:**
- Pattern "5 words at most per step" kan være supplement for reasoning-tunge sub-tasks
- VALIDERER vår per-turn reinforcement strategi (M025)
- BEKREFTER concise per-step budget > global token budget (vs H006)

**STATUS:** M033 nedgradert fra 90% → 50% tro for FLINT general use.
        Test som SUPPLEMENT, ikke standalone arm.

---

## F092-F096 — Codex caveman RE batch 5

### F092 — Startup cost equal
Caveman vs FLINT begge ~51ms p50. Node spawn dominates. INGEN perf-gap.

### F093 ADOPT — Runtime deps thin
- Caveman hooks: Node stdlib only
- MCP shrink: no deps
- Compression: optional anthropic/Claude CLI fallback
- Benchmark: optional tiktoken fallback
- TASK: keep FLINT hook/MCP dependency-free, optional deps i offline tools only

### F094 ADOPT — No runtime telemetry/phone-home
- Ingen i hooks/statusline/MCP/stats
- Network kun: installer/package-manager paths (GitHub raw, npm registry probe, native install)
- TASK: dokumenter explicit FLINT privacy posture

### F095 BUILD — Marketplace distribusjon per-surface
- Claude plugin: hook registrations/timeouts
- Codex plugin: UI/defaultPrompt only
- Gemini: contextFileName
- Agents marketplace: lokal plugin pointer
- Codex hooks: separate
- TASK: generated surface-specific manifests + tests

### F096 — TOML commands thin
- Mutations stays in JS med dry-run/force
- Pattern: bekreftet, ingen action needed

---

## H-K HYPOTHESIS — BIMODAL LATCH-STATE (Claude koder 2026-05-11)

**Empirisk grunnlag:** commit 4c01e9c offline analyse + cross-run varians M034.

### Hypotese
Mode-oppførsel er **BIMODAL på tvers av kjøringer**.

Same prompt + same mode gir 2 distinkte output-distribusjoner:
- **Mode A "compression-state"**: caveman_ultra +72% savings (BM001)
- **Mode B "explanation-state"**: caveman_ultra -182% savings (flint_compact)

Faktaretensjon perfekt i BEGGE tilstander (5/5) — så IKKE fakta-tap.

### Mekanisme
Modellens output-distribusjon er **bistable** basert på subtle context-cues.
Avgjørelse tidlig i samtalen (turn 1-2) **låser** modus → persisterer hele samtalen.
Ingen mellomtilstand observert.

### Empirisk støtte
- BM001 caveman_ultra context_retention: output=2674 (compression state)
- flint_compact caveman_ultra context_retention: output=14966 (explanation state)
- Same skill-prompt, same scenario, ulike turner.
- Variance >5x mellom kjøringer.

### M022 PRESISERING
Originalt: "Vi måler ikke kompresjon, vi måler hva modellen velger å skrive"
Oppdatert: **"Vi måler hvilken LATCH-tilstand modellen havna i"**

Caveman-instructions er IKKE deterministiske kompressorer.
De er **bistable triggers** — same prompt → forskjellige attractors basert på turn-1 prediction.

### FALSIFIKASJON
Test: n=20 same scenario+mode på Haiku-4-5 + caveman_ultra
- Hvis tett samlet (CV<20%): K **FORKASTET** (variance = modell-støy)
- Hvis multimodal (to klare topper): K **STADFESTET**

### KONSEKVENSER hvis K stadfestes
1. "Best compression prompt" jakt = feil ramme
2. Trenger: maximize P(compression_state) per turn 1
3. Ny metrikk: latch-rate = % av kjøringer som havner i compression-state
4. Effective_savings = P(compress_state) × savings_state_compress + P(explain_state) × savings_state_explain
5. Trigger-engineering > general prompt-engineering

### TESTING-PRIO
Gemini API (gratis tier) gir oss råd til n=20 PER scenario/mode kombinasjon.
Total kost: ~100 prompts × 5 modes × 20 reps × 2 scenarios = 20K prompts.
Innenfor Gemini free tier hvis spredt over tid.


---

## H005-H008 SIMULERTE PREDIKSJONER (Gemini 2026-05-11 10:08)

⚠ **VIKTIG KONTEKST:** Disse er Geminis simulerte/teoretiske estimat — IKKE faktiske API-målinger.
Per M022 + Hypotese K: simulering ≠ måling. Bistable latch-state kan gi 5x varians.

| Hypothesis | Simulert savings | Risiko / Fordel |
|------------|-----------------|-----------------|
| H005 Negation | ~31% | Akademisk: performance paradox |
| H006 Hard Budget | ~43% | Beste med linguistic anchor |
| H007 Persona Anchor | ~50% | Skeleton > Role Play (TELEGRAPH-failure unngås) |
| H008 Variable Substitution | ~52% | Beste for teknisk doc med repetisjon |

**RANGERING etter simulert effekt:**
1. H008 (52%) — high promise for tech-heavy compression
2. H007 (50%) — anchoring approach (NY vinkel etter TELEGRAPH-failure)
3. H006 (43%) — kombinerbart med H007
4. H005 (31%) — laveste, akademisk varsel

**M033 CoD** flagget som top-prio benchmark arm når API kommer.

**KONSEKVENS for prio:**
Når API-blokker løses: kjør i denne rekkefølge for max info per minutt:
1. n=20 reframe-validation (test bimodal hypothesis K)
2. M033 CoD arm
3. H008 variable substitution (høyest predikert)
4. H007 + H006 kombinasjon (sammen kan slå caveman?)
5. H005 (lav prio, akademisk varsel)

---

## F112-F117 — Codex caveman RE batch 7 (2026-05-11 10:43)
**Status: BACKLOG for neste sesjon (deadline 11:30 nåværende sesjon).**

### F112 BUILD — Config override matrix
- Precedence: CAVEMAN_DEFAULT_MODE > XDG/APPDATA config > 'full'
- Installer flags override auto-defaults
- Shrink fields/debug, compress model/API key, statusline savings env-driven
- TASK: FLINT docs/tests trenger eksplisitt precedence-matrise, valid values, defaults, per-surface support

### F113 BUILD — Benchmark transparency gap
- Caveman benchmark-script lagrer raw JSON, README rapporterer 65%
- MEN plugin cache har bare benchmarks/results/.gitkeep
- Eval snapshot committed for Opus 4.6 + admits "no fidelity/statistical significance"
- TASK: FLINT claims må LINK til committed raw artifacts + no-fidelity caveat ved tabeller

### F117 BUILD — Data boundary policy
- Compress refuses secret-looking paths før read/API call (no override unntatt rename)
- Shrink rører ikke requests/tool-call bodies
- Security doc statete eksakt hva som forlater maskinen
- TASK: FLINT compression tools må fail-closed på sensitive paths + dokumenter data egress

### F114-F116 (kort)
- F114 — Architecture graph (modul-dependency)
- F115 — OS parity (Windows/Linux/Mac)
- F116 — Community contribution rules

---

## M035 — Skill Engineering Patterns (ADOPT)

**Kilde:** Articsledge "What Is Skill Engineering?" Apr 2026 + Anthropic Agent Skills Oct 2025
**Status:** ADOPT (design guide, ikke compression method)

**Nøkkelfunn:**
- Skills er IKKE prompts. Skills er strukturerte, versjonerte, komponerbare pakker med progressiv loading (~30-50 tokens per skill ved startup).
- Agent Skills ble open standard Dec 2025 på agentskills.io. Adoptert av OpenAI, Microsoft, Cursor, GitHub, Gemini CLI, 20+ platformer.
- Tre-tier progressive disclosure: navn/description → full SKILL.md → reference files on demand.

**Relevans for FLINT:**
FLINT SKILL.md-filer følger allerede formatet ubevisst, men mangler:
- **Scope conditions** i frontmatter (når skal skill aktiveres/ikke)
- **Negative examples** (vis hva DÅRLIG output er)
- **Success criteria** definert per skill
- **Activation disambiguation** mot andre skills

**Anti-patterns å unngå (fra guide):**
- Bloated skill: ett skill prøver å gjøre for mye
- Overlapping skills: uklare aktiveringsbetingelser → probabilistisk routing
- Vague routing: "use this for writing" er ikke nok
- Missing edge cases: hva gjør skill når input er utenfor scope?
- Stale examples: eksempler må oppdateres når standarder endres
- Hidden assumptions: modellen har ikke tilgang til implisitt kontekst

**Anbefaling:** Kjør FLINT-skills gjennom anti-pattern-sjekklisten. Legg til scope conditions i frontmatter.

---

## M036 — Context Mode External Event Log (HYPOTHESIS)

**Kilde:** MindStudio blog "Context Mode for Claude Code" May 5, 2026
**Status:** HYPOTHESIS — krever implementasjonseksperiment

**Nøkkelfunn:**
- 63× compression ratio (315KB→5KB) på Claude Code sessions
- Topronget arkitektur:
  1. **Sandbox-filtrering:** tool output routes through sandbox, kun semantisk relevant del kommer inn i context
  2. **SQLite event log:** persistent log UTENFOR samtalen. File edits, tasks, decisions, errors.
- 56KB Playwright snapshot → 299 bytes
- 46KB access log → 155 bytes
- Etter compaction: injiser session snapshot fra SQLite → modellen fortsetter der den slapp

**Kritisk innsikt for FLINT:**
"Failure mode of context rot isn't just 'Claude forgets things.' It's 'Claude forgets things and doesn't know it forgot them.'"

**FLINT gap:**
Vår flint-history.jsonl sporer kun turn counts for `/flint-stats`. Skulle vært en **full event log**: file edits, tasks, decisions, errors — som overlever compaction og kan injiseres tilbake.

**Effekt:** Ikke token savings, men **session longevity**: 30 min → 3 timer.

**Anbefaling:** Bygg FLINT event log (SQLite/JSONL) med session snapshot injection. Complementary til eksisterende kompresjon.
