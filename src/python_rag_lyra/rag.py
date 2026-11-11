from pathlib import Path
import os
import requests
import chromadb
from dotenv import load_dotenv
from python_rag_lyra.embedding import OllamaEmbedder 
from tqdm import tqdm
import re


load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST")
CHROMA_PATH = os.getenv("CHROMA_PATH")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

CHAPTER = re.compile(r"^\d+\.\s+[ⅠⅡⅢIVX]+[：:]")


class rag:
    def __init__(self, doc_file:str, model = "qwen3-embedding:4b", chunk_size:int = 500, overlap:int = 80, chunks_model:int = 1):
        self.doc_file = doc_file
        self.model = model
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.embedder = OllamaEmbedder(model=model)
        self.chunks_model = chunks_model

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

    def split_fixed(self, doc_file:str, chunk_size=200, overlap=80):
        """按固定长度切分文本，返回切分后的列表。"""
        chunks, start = [], 0
        content = Path(doc_file).read_text(encoding="utf-8")
        while start < len(content):
            end = start + chunk_size
            chunks.append(content[start:end])
            start = end - overlap
            #print(chunks)
        return chunks

    def split_into_chunks_pro(self, doc_file: str, max_chars: int = 500, overlap_chars: int = 80):
        """按段落切分文档，超长段落按句子切分。"""
        content = Path(doc_file).read_text(encoding="utf-8").replace("\r\n", "\n").strip()
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]

        chunks, buf = [], ""
        for p in paragraphs:
            # 超长段落先按句子降级切
            if len(p) > max_chars:
                if buf:
                    chunks.append(buf)
                    buf = ""
                sents = [s for s in re.split(r"(?<=[。！？!?…])", p) if s.strip()]
                cur = ""
                for s in sents:
                    if len(cur) + len(s) > max_chars and cur:
                        chunks.append(cur)
                        cur = cur[-overlap_chars:]
                    cur += s
                if cur.strip():
                    chunks.append(cur)
                continue

            if len(buf) + len(p) + 2 <= max_chars:
                buf = f"{buf}\n\n{p}" if buf else p
            else:
                chunks.append(buf)
                buf = buf[-overlap_chars:] + "\n\n" + p
        if buf.strip():
            chunks.append(buf)
        return chunks

 

    def build_collection(self, batch_size:int = 1000):
        """切块 → 向量化 → 存入 Chroma，返回 collection。"""
        try:
            collection = self.get_collection()
            match self.chunks_model:
                case 1:
                    document_chunks = self.split_into_chunks_pro(self.doc_file)
                case 2:
                    document_chunks = self.split_into_chunks(self.doc_file)
                case 3:
                    document_chunks = self.split_fixed(self.doc_file)
                case _:
                    raise ValueError(f"无效的 chunks_model: {self.chunks_model}")

            #分批向量化
            vectors = []
            total = len(document_chunks) 
            batch = 64
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

    
