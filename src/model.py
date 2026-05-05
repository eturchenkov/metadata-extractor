from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel, Field
from typing import Annotated
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.local")


class MetadataModel(BaseModel):
    page_id: Annotated[str, Field(pattern=r"[\w.-]+")]
    page_name: str
    project_name: str
    architect: str


llm = ChatOpenAI(model="gpt-4o").with_structured_output(MetadataModel)
# llm = ChatAnthropic(model="claude-opus-4-7").with_structured_output(MetadataModel)
