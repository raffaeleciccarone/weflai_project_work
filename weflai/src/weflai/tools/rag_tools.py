import os
from crewai_tools import PDFSearchTool
from dotenv import load_dotenv

load_dotenv()



pdf_tool = PDFSearchTool(
    config=dict(
        llm=dict(
            provider="ollama",
            config=dict(
                model="qwen2.5:7b"
            ),
        ),
        embedder = dict(
            provider="ollama",
            config=dict(
                model="bge-m3"
            )
        )
    ),pdf = "knowledge_base/regolamento.pdf"
)