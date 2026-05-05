import asyncio
import numpy as np
from openai import AsyncOpenAI
from model import models, MetadataModel
from dataset import link_list, target
from batch_handler import BatchHandler

client = AsyncOpenAI()


async def eval():
    for llm_name, llm in models.items():
        print(f"Eval of {llm_name}")
        handler = BatchHandler(llm.with_structured_output(MetadataModel))
        md_list = await handler.handle_drawings(link_list[:1])
        total = 0
        for res in md_list:
            if res["status"] == "successful":
                md = res["result"]
                url = res["url"]
                subtotal = 0
                subtotal += cos_dist(
                    await calc(md["page_id"]), await calc(target[url]["page_id"])
                )
                subtotal += cos_dist(
                    await calc(md["page_name"]), await calc(target[url]["page_name"])
                )
                subtotal += cos_dist(
                    await calc(md["project_name"]),
                    await calc(target[url]["project_name"]),
                )
                subtotal += cos_dist(
                    await calc(md["architect"]), await calc(target[url]["architect"])
                )
                total += subtotal / 4
        print(f"{total / len(md_list)}")


async def calc(text: str) -> None:
    response = await client.embeddings.create(
        model="text-embedding-3-small", input=text, encoding_format="float"
    )
    return np.array(response.data[0].embedding)


def cos_dist(vec1: np.ndarray, vec2: np.ndarray) -> float:
    cos_d = float(np.dot(vec1, vec2))
    return round(cos_d, 2) if cos_d > 0 else 0


if __name__ == "__main__":
    asyncio.run(eval())
