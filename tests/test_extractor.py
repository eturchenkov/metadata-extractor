from unittest.mock import AsyncMock
from langchain_core.messages import HumanMessage
from model import MetadataModel
from extractor import extract_metadata, prompt


FAKE_URL = "https://example.com/drawing.png"
FAKE_METADATA = MetadataModel(
    page_id="A1.01",
    page_name="Ground Floor Plan",
    project_name="City Library",
    architect="Jane Doe",
)


def make_llm(return_value=FAKE_METADATA):
    llm = AsyncMock()
    llm.ainvoke = AsyncMock(return_value=return_value)
    return llm


async def test_returns_metadata_model():
    llm = make_llm()
    result = await extract_metadata(llm, FAKE_URL)
    assert result == FAKE_METADATA


async def test_sends_correct_message():
    llm = make_llm()
    await extract_metadata(llm, FAKE_URL)

    [message] = llm.ainvoke.call_args[0][0]
    assert isinstance(message, HumanMessage)
    text_part, image_part = message.content
    assert text_part == {"type": "text", "text": prompt}
    assert image_part == {"type": "image_url", "image_url": {"url": FAKE_URL}}
