# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Run a single extractor script directly
uv run python src/extractor.py
uv run python src/batch_handler.py
uv run python src/evaluation.py

# Add a dependency
uv add <package>
```

All source files use relative imports within `src/` (e.g. `from model import llm`) — run them from the `src/` directory or via `uv run python src/<file>.py` from the repo root.

## Architecture

This project extracts structured metadata (page ID, page name, project name, architect) from architectural drawing images hosted at remote URLs.

**Data flow:**
1. `dataset.py` — `link_list` (list of image URLs) and `target` (dict keyed by URL → expected metadata dict with `page_id`, `page_name`, `project_name`, `architect`).
2. `model.py` — `models` dict of raw LLM instances (`gpt-4o`, `opus`); module-level `llm` is the env-selected model wrapped with `.with_structured_output(MetadataModel)`. `MetadataModel` defines the extraction schema. Active model is selected via `CURRENT_MLLM` env var (default: `gpt-4o`).
3. `extractor.py` — `extract_metadata(llm, image_url)` sends the image URL + prompt to the LLM via LangChain's multimodal message format and returns a `MetadataModel` instance.
4. `batch_handler.py` — `BatchHandler` class wraps concurrent async execution with retry/backoff. Constructor takes `llm` plus optional `max_retries`, `retry_delay`, `max_concurrent`. Results include `.model_dump()` output per URL.
5. `evaluation.py` — iterates over all models in `models`, runs extraction on `link_list[:1]`, and scores each field (`page_id`, `page_name`, `project_name`, `architect`) using cosine similarity of OpenAI `text-embedding-3-small` embeddings against `target`. Reports average score per model. Requires `OPENAI_API_KEY`.

**Key design points:**
- `extract_metadata` returns a structured `MetadataModel` via LangChain's `.with_structured_output()` — callers must pass a structured-output-wrapped LLM, not a raw model from `models`.
- `BatchHandler` uses `asyncio.Semaphore` to cap concurrent LLM calls and exponential backoff (`retry_delay * 2^attempt`) to handle rate limits.
- The `llm` object from `model.py` is the single shared LangChain runnable used across all modules.
- Evaluation scores are cosine similarity (0–1) averaged across 4 fields, then across all processed URLs.
