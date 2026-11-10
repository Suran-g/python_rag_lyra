from pathlib import Path
import os
import requests
import chromadb
from dotenv import load_dotenv
from python_rag_lyra.embedding import OllamaEmbedder 
from tqdm import tqdm


load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST")
CHROMA_PATH = os.getenv("CHROMA_PATH")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")



class rag:
    def __init__(self, doc_file:str, model = "qwen3-embedding:4b"):
        self.doc_file = doc_file
        self.model = model
        self.embedder = OllamaEmbedder(model=model)

    def run_rag():
        pass

    def get_collection(self):

        client = chromadb.PersistentClient(path=CHROMA_PATH)
        return client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )


    def split_into_chunks(self, doc_file:str)->list[str]:
        """按空行(段落)切分文档。"""
        content = Path(doc_file).read_text(encoding="utf-8")

        content = content.replace("\r\n", "\n").strip()

        results = []
        for part in content.split("\n\n"):
            if part.strip():
                results.append(part.strip()) 
        return results    

    def build_collection(self, batch_size:int = 1000):
        """切块 → 向量化 → 存入 Chroma，返回 collection。"""
        try:
            collection = self.get_collection()
            document_chunks = self.split_into_chunks(self.doc_file)

            #分批向量化
            vectors = []
            total = len(document_chunks) 
            batch = 128
            for start in tqdm(range(0, total, batch), desc="向量化"):
                end = min(start + batch, total)
                vectors.extend(self.embedder.embed(document_chunks[start:end]))
            print("向量化完成")
    
            doc_name = Path(self.doc_file).stem

            total = len(document_chunks) 
            for start in range(0, total, batch_size):
                end = min(start + batch_size, total)

                collection.upsert(
                    #需分批导入数据库
                    ids = [f"{doc_name}-{i}" for i in range(start,end)],
                    documents=document_chunks[start:end],
                    embeddings=vectors[start:end],
                    metadatas = [
                        {
                            "source": Path(self.doc_file).name, 
                            "chunk_index": i
                        }
                        for i in range(start,end)],
                )
        except Exception as e:
            raise RuntimeError(f"构建知识库失败：{e}") from e
        print(f"向量库记录数：{collection.count()}")
        return collection

    
