# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Run a single extractor script directly
uv run python src/extractor.py
uv run python src/batch_handler.py

# Add a dependency
uv add <package>
```

All source files use relative imports within `src/` (e.g. `from model import llm`) — run them from the `src/` directory or via `uv run python src/<file>.py` from the repo root.

## Architecture

This project extracts structured metadata (page ID, page name, project name, architect) from architectural drawing images hosted at remote URLs.

**Data flow:**
1. `dataset.py` — static list of image URLs (`link_list`)
2. `model.py` — instantiates the LLM with structured output bound to `MetadataModel` (Pydantic). Currently uses `ChatAnthropic(claude-opus-4-7)`; a `ChatOpenAI` option is commented out. `MetadataModel` defines the extraction schema.
3. `extractor.py` — `extract_metadata(llm, image_url)` sends the image URL + prompt to the LLM via LangChain's multimodal message format and returns a `MetadataModel` instance.
4. `batch_handler.py` — `BatchHandler` class wraps concurrent async execution with retry/backoff. Constructor takes `llm` plus optional `max_retries`, `retry_delay`, `max_concurrent`. Results include `.model_dump()` output per URL.

**Key design points:**
- `extract_metadata` returns a structured `MetadataModel` via LangChain's `.with_structured_output()` — callers receive a Pydantic model, not raw text.
- `BatchHandler` uses `asyncio.Semaphore` to cap concurrent LLM calls and exponential backoff (`retry_delay * 2^attempt`) to handle rate limits.
- The `llm` object from `model.py` is the single shared LangChain runnable used across all modules.
