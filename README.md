# Metadata AI Extractor

Extracts structured metadata from architectural drawing images using a multimodal LLM.

Given an image URL, it reads the title block of the drawing and returns:

| Field | Example |
|---|---|
| `page_id` | `A1.01` |
| `page_name` | `Ground Floor Plan` |
| `project_name` | `City Library` |
| `architect` | `ODA NEW YORK` |

## Setup

Requires Python 3.13+ and uv.

```bash
uv sync
```

Create a `.env` file with your API key(s):

```
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
```

## Model selection

Set `CURRENT_MLLM` to choose the model (defaults to `gpt-4o`):

| Value | Model |
|---|---|
| `gpt-4o` | OpenAI GPT-4o (default) |
| `opus` | Anthropic Claude Opus 4.7 |

```bash
CURRENT_MLLM=opus uv run python src/extractor.py
```

## Usage

**Single image:**

```bash
uv run python src/extractor.py
```

**Batch (concurrent, with retry):**

```bash
uv run python src/batch_handler.py
```

Or use `BatchHandler` directly in your own code:

```python
from batch_handler import BatchHandler
from model import llm

handler = BatchHandler(llm, max_retries=3, retry_delay=2, max_concurrent=5)
results = await handler.handle_drawings(image_urls)
```

Each result is either:

```python
{"url": "...", "status": "successful", "result": {"page_id": ..., "page_name": ..., "project_name": ..., "architect": ...}}
{"url": "...", "status": "fail", "error": "..."}
```

`BatchHandler` uses `asyncio.Semaphore` to cap concurrent LLM calls and exponential backoff (`retry_delay * 2^attempt`) between retries.

## Evaluation

Runs all models against a labeled dataset and scores each field using cosine similarity of OpenAI embeddings (`text-embedding-3-small`). Requires `OPENAI_API_KEY`.

```bash
uv run python src/evaluation.py
```

Output is an average similarity score (0–1) per model across `page_id`, `page_name`, `project_name`, and `architect`.

## Tests

```bash
uv run pytest
```
