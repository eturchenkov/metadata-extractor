import asyncio
import numpy as np
from openai import AsyncOpenAI
from model import models, MetadataModel
from dataset import link_list, target
from batch_handler import BatchHandler

client = AsyncOpenAI()


async def eval(links: list[str]):
    for llm_name, llm in models.items():
        print(f"=== Eval of {llm_name} ===")
        handler = BatchHandler(llm.with_structured_output(MetadataModel))
        md_list = await handler.handle_drawings(links)
        total = 0
        for i, res in enumerate(md_list):
            subtotal = 0
            if res["status"] == "successful":
                md = res["result"]
                url = res["url"]
                for key, value in md.items():
                    subtotal += cos_dist(
                        await calc_emb(value), await calc_emb(target[url][key])
                    )
                total += subtotal / len(md)
            print(f"{i}  {round(subtotal / 4, 2)}")
        print(f"total score: {round(total / len(md_list), 2)}")


async def calc_emb(text: str) -> np.ndarray:
    response = await client.embeddings.create(
        model="text-embedding-3-small", input=text, encoding_format="float"
    )
    return np.array(response.data[0].embedding)


def cos_dist(vec1: np.ndarray, vec2: np.ndarray) -> float:
    cos_d = float(np.dot(vec1, vec2))
    return round(cos_d, 2) if cos_d > 0 else 0


if __name__ == "__main__":
    asyncio.run(eval(link_list))
