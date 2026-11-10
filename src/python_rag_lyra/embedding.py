import os
import requests
from dotenv import load_dotenv
"""向量化"""
load_dotenv()

class OllamaEmbedder:
    def __init__(self, model = os.getenv("EMBED_MODEL")):
            self.model = model

    def embed(self, texts: list[str]) -> list[list[float]]:
            """调用本地 Ollama，把一批文本转成向量。"""
            print("向量化中...")
            response = requests.post(
                f"{os.getenv("OLLAMA_HOST")}/api/embed",
                json={
                    "model": self.model, 
                    "input": texts
                },
            )
            response.raise_for_status()        # HTEMBED_MODELTP 出错时抛异常，而不是静默失败
            return response.json()["embeddings"]