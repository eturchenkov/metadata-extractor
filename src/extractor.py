import asyncio
from langchain_core.messages import HumanMessage
from langchain_core.runnables import Runnable
from model import llm
from dataset import link_list
from pprint import pprint

prompt = """
You are a highly precise document parsing system specialized in architectural drawings.

Your task is to extract specific metadata fields from the provided architectural drawing image.

You MUST follow these rules strictly:

---------------------
OUTPUT FORMAT (STRICT)
---------------------
Return ONLY valid JSON. No explanations, no comments, no extra text.

The JSON schema must be EXACTLY:

{
  "page_id": "string",
  "page_name": "string",
  "project_name": "string",
  "architect": "string"
}

---------------------
EXTRACTION RULES
---------------------

1. General:
- Extract only what is explicitly visible in the image.
- DO NOT guess or infer missing values.
- If a field is not found, return an empty string "".
- Preserve original capitalization as seen in the document.
- Trim leading/trailing whitespace.
- Do not include line breaks in values.

2. page_id:
- Typically labeled as identifier: "E211", "ID-100", "A-101", etc.
- Usually located in the title block (bottom-right corner most of the time).
- Prefer alphanumeric codes like: A-101, A1.01, A-101.00.
- It contains letters, digits, "-", "." only.

3. page_name:
- Typically the drawing title.
- Examples: "1ST FLOOR PLAN", "ROOF PLAN", "ELEVATION", etc.
- Usually located near or above the page_id.

4. project_name:
- Usually appears in the title block.
- May include address or building name.
- Examples: "1356 1st AVENUE", "RESIDENTIAL BUILDING AT ..."

5. architect:
- Typically a company or firm name.
- Look for labels like: "Architect", "Designed by", or firm logos.
- Extract the firm/company name only (e.g., "ODA NEW YORK").

---------------------
DISAMBIGUATION PRIORITY
---------------------

If multiple candidates exist:
- Prefer values inside the title block.
- Prefer larger or bold text for page_name.
- Prefer text closest to relevant labels (e.g., "Architect").

---------------------
FINAL CHECK
---------------------

Before returning:
- Ensure valid JSON (no trailing commas, proper quotes).
- Ensure all 4 keys are present.
- Ensure no additional keys exist.

Now analyze the provided image and return the JSON.
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
