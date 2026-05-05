import asyncio
from langchain_core.messages import HumanMessage
from langchain_core.runnables import Runnable
from model import llm
from dataset import link_list
from pprint import pprint

prompt = """
Extract page id, page name, project name and architect
from left side of the document
"""


async def extract_metadata(llm: Runnable, image_url: str):
    message = HumanMessage(
        content=[
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": image_url}},
        ]
    )
    return await llm.ainvoke([message])


async def print_metadata_once(url):
    print(url)
    metadata = await extract_metadata(llm, url)
    pprint(metadata.model_dump())


if __name__ == "__main__":
    asyncio.run(print_metadata_once(link_list[0]))
