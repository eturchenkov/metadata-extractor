import asyncio
from langchain_core.runnables import Runnable
from dataset import link_list
from model import llm
from extractor import extract_metadata
from pprint import pprint


class BatchHandler:
    def __init__(
        self,
        llm: Runnable,
        max_retries: int = 3,
        retry_delay: int = 2,
        max_concurrent: int = 5,
    ):
        self.llm = llm
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def _handle_drawing_with_retry(self, image_url: str) -> dict:
        last_err = None
        for attempt in range(1, self.max_retries + 1):
            try:
                async with self.semaphore:
                    md = await extract_metadata(self.llm, image_url)
                    return {
                        "url": image_url,
                        "status": "successful",
                        "result": md.model_dump(),
                    }
            except Exception as e:
                last_err = str(e)
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay * (2**attempt))
        return {"url": image_url, "status": "fail", "error": last_err}

    async def handle_drawings(self, image_urls: list[str]) -> list[dict]:
        tasks = [self._handle_drawing_with_retry(url) for url in image_urls]
        results = await asyncio.gather(*tasks)
        return results


async def start_handler():
    handler = BatchHandler(llm)
    pprint(await handler.handle_drawings(link_list))


if __name__ == "__main__":
    asyncio.run(start_handler())
