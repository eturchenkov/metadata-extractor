# metadata-extractor

Extracts structured metadata from architectural drawing images using a multimodal LLM.

Given an image URL, it reads the title block on the left side of the drawing and returns:

| Field | Example |
|---|---|
| `page_id` | `A1.01` |
| `page_name` | `Ground Floor Plan` |
| `project_name` | `City Library` |
| `architect` | `Jane Doe` |

## Setup

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

Create a `.env.local` file with your API key:

```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

To switch between models, edit `src/model.py` — `ChatOpenAI` (gpt-4o) and `ChatAnthropic` (claude-opus-4-7) are both wired up, one commented out.

## Usage

**Single image:**

```bash
uv run python src/extractor.py
```

**Batch (concurrent, with retry):**

```bash
uv run python src/batch_handler.py
```

Or use `BatchHandler` directly:

```python
from batch_handler import BatchHandler
from model import llm

handler = BatchHandler(llm, max_retries=3, retry_delay=2, max_concurrent=5)
results = await handler.handle_drawings(image_urls)
```

Each result is either:

```python
{"url": "...", "status": "successful", "result": {...}}
{"url": "...", "status": "fail", "error": "..."}
```

## Tests

```bash
uv run pytest
```
