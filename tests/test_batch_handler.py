from unittest.mock import AsyncMock, patch
from model import MetadataModel
from batch_handler import BatchHandler


URLS = [
    "https://example.com/drawing_1.png",
    "https://example.com/drawing_2.png",
]
FAKE_METADATA = MetadataModel(
    page_id="A1.01",
    page_name="Ground Floor Plan",
    project_name="City Library",
    architect="Jane Doe",
)


def make_handler(**kwargs):
    defaults = {"max_retries": 3, "retry_delay": 0}
    return BatchHandler(AsyncMock(), **{**defaults, **kwargs})


async def test_successful_result_shape():
    handler = make_handler()
    with patch("batch_handler.extract_metadata", AsyncMock(return_value=FAKE_METADATA)):
        result = await handler.handle_drawing_with_retry(URLS[0])

    assert result == {"url": URLS[0], "status": "successful", "result": FAKE_METADATA.model_dump()}


async def test_failure_after_all_retries():
    handler = make_handler(max_retries=3)
    with patch("batch_handler.extract_metadata", AsyncMock(side_effect=RuntimeError("api error"))):
        result = await handler.handle_drawing_with_retry(URLS[0])

    assert result == {"url": URLS[0], "status": "fail", "error": "api error"}


async def test_retries_then_succeeds():
    handler = make_handler(max_retries=3)
    extract = AsyncMock(side_effect=[RuntimeError("timeout"), RuntimeError("timeout"), FAKE_METADATA])
    with patch("batch_handler.extract_metadata", extract):
        result = await handler.handle_drawing_with_retry(URLS[0])

    assert result["status"] == "successful"
    assert extract.call_count == 3


async def test_handle_drawings_processes_all_urls():
    handler = make_handler()
    with patch("batch_handler.extract_metadata", AsyncMock(return_value=FAKE_METADATA)):
        results = await handler.handle_drawings(URLS)

    assert len(results) == len(URLS)
    assert all(r["status"] == "successful" for r in results)
    assert [r["url"] for r in results] == URLS


async def test_handle_drawings_independent_failures():
    handler = make_handler(max_retries=1)
    extract = AsyncMock(side_effect=[FAKE_METADATA, RuntimeError("bad")])
    with patch("batch_handler.extract_metadata", extract):
        results = await handler.handle_drawings(URLS)

    statuses = {r["url"]: r["status"] for r in results}
    assert statuses[URLS[0]] == "successful"
    assert statuses[URLS[1]] == "fail"


async def test_concurrency_limit():
    max_concurrent = 2
    handler = make_handler(max_concurrent=max_concurrent)
    active = 0
    peak = 0

    async def tracked_extract(llm, url):
        nonlocal active, peak
        active += 1
        peak = max(peak, active)
        await asyncio.sleep(0)
        active -= 1
        return FAKE_METADATA

    import asyncio
    with patch("batch_handler.extract_metadata", tracked_extract):
        await handler.handle_drawings(URLS * 4)

    assert peak <= max_concurrent
