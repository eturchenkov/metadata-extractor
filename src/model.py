import os
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel, Field
from typing import Annotated
from dotenv import load_dotenv

load_dotenv()


class MetadataModel(BaseModel):
    page_id: Annotated[str, Field(pattern=r"^[\w.-]+$")]
    page_name: str
    project_name: str
    architect: str


models = {
    "gpt-4o": ChatOpenAI(model="gpt-4o"),
    "opus": ChatAnthropic(model="claude-opus-4-7"),
}

llm = models[os.environ.get("CURRENT_MLLM", "gpt-4o")]
llm = llm.with_structured_output(MetadataModel)
