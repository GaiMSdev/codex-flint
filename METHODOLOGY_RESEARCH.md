# Methodology Research — LLM Compression Evaluation Standards

## Status: COMPLETE (2026-05-11, 11:20)

## Sources
- LLMCBench (NeurIPS 2024) — rigorous LLM compression benchmark design
- MT-Bench + Chatbot Arena (Zheng et al., NeurIPS 2023) — LLM-as-judge gold standard
- RAND Judge Reliability Harness (Mar 2026) — stress-testing LLM judges
- JudgeBiasBench (Mar 2026) — 12 bias types documented
- Anthropic "Quantifying infrastructure noise in agentic coding evals" (Feb 2026)
- JETTS Benchmark (ICML 2026) — LLM-judge evaluation for test-time scaling
- LMSYS-Chat-1M dataset (ICLR 2024) — 1M real conversations
- WildChat (AI2, 2024) — 1M ChatGPT interactions

## Key Findings

### What Professionals Do

| Practice | Our Status | Gap |
|----------|-----------|-----|
| n_repeats=5+ | ✅ n=5 default | Anthropic recommends more for high-variance modes |
| Bootstrap CI | ✅ seed=42 bootstrap | Validated by infra-noise research |
| Diverse models | ✅ Haiku + Sonnet | Consider adding 3rd model family |
| Real-world data | ❌ Synthetic scenarios | Use LMSYS-Chat-1M prompts |
| Blind LLM-as-judge | ❌ Not implemented | Critical for avoiding self-preference bias |
| Variance per mode tracked | ❌ Not tracked | Each mode may need different n |

### LLM-as-Judge Biases (Must Mitigate)
1. **Position bias**: judges prefer first/last presented response
2. **Length bias**: judges prefer longer responses (irrespective of quality)
3. **Self-preference bias**: judges favor outputs from their own model family
4. **Framing bias**: wording of judge prompt changes scores
5. **Overlap bias**: judges prefer LLM-generated summaries over human-written (even when worse)

## Top 3 Changes to Our Eval Setup

### 1. Add LMSYS-Chat-1M as replay dataset
Replace synthetic scenarios with real user prompts from LMSYS-Chat-1M. Extract the first user turn from each conversation as input. Gives us 1M real-world, multi-lingual, diverse prompts — not synthetic. Available at `lmsys/lmsys-chat-1m` on HuggingFace.

### 2. Cross-model blind LLM-as-judge
Use a DIFFERENT model family as judge to score compressed outputs. E.g., GPT-4.1 to judge Claude outputs (avoids self-preference). Implement pairwise comparison with position randomization (A/B → B/A → average). Score fact_match, readability, and completeness.

### 3. Per-mode variance tracking + adaptive n_repeats
Log infra context (CPU/RAM/disk IO) per run. Track variance per (scenario, mode, model) combo. High-variance modes get n=10, stable modes get n=3. Set `min_repeats = 3 + int(variance_coefficient * 10)`.

## 1 Recommended Real-World Dataset: LMSYS-Chat-1M
- **1M real conversations**, 25 models, 210K unique users
- **Multi-turn** (avg 2.0 turns/sample), **154 languages**
- **Natural tasks**: coding, writing, analysis, Q&A — not synthetic
- **Proven**: used in MT-Bench / Chatbot Arena (NeurIPS 2023, 2688+ citations)
- **Access**: `huggingface.co/datasets/lmsys/lmsys-chat-1m` (MIT license for non-commercial)

## Backlogged for Next Session
- Implement LMSYS-Chat-1M extractor script in benchmark pipeline
- Build cross-model blind judge module
- Add infra_context field to benchmark JSON output
- Adaptive n_repeats based on per-mode variance
