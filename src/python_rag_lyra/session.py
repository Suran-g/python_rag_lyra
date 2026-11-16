from python_rag_lyra.embedding import OllamaEmbedder
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv 
load_dotenv()

import os

class session:

    def __init__(self, 
                 collection,
                 DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL"),
                 DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL")
        ):
        prompt_path = os.getenv("SYSTEM_PROMPT_PATH", "data/tianqin.md")
        self.SYSTEM_PROMPT = Path(prompt_path).read_text(encoding="utf-8")

        self.collection = collection
        self.DEEPSEEK_BASE_URL = DEEPSEEK_BASE_URL
        self.DEEPSEEK_MODEL = DEEPSEEK_MODEL

    def get(self):
          return self.SYSTEM_PROMPT
        

    def retrieve(self,question: str, top_k: int = 5):
        """把问题向量化，在库里找最相似的 top_k 个 chunk。"""
        embedder = OllamaEmbedder()
        query_vector = embedder.embed([question])[0]

        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )
        print("问题向量化成功 ")
        #print(results["documents"][0])
        return results

    def build_prompt(self, question: str, context_chunks) -> str:
        """把检索到的片段编号后拼进 Prompt。"""
        context = "\n\n".join(
            f"[片段 {i}]\n{chunk}" for i, chunk in enumerate(context_chunks, start=1)
        )
        print(context)
        return f"""资料：{context}问题：{question}"""

    


    def generate_answer(self, question: str, context_chunks: list[str]) -> str:
        """调用 DeepSeek 生成最终回答。"""
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise RuntimeError("没有找到 DEEPSEEK_API_KEY，请检查项目根目录的 .env 文件")

        client = OpenAI(
            api_key=api_key,
            base_url=self.DEEPSEEK_BASE_URL,
            timeout=120,
        )

        response = client.chat.completions.create(
            model=self.DEEPSEEK_MODEL,
            messages=[
                {
                    "role": "system", 
                    "content": self.SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": self.build_prompt(question, context_chunks)
                },
            ],
            temperature=2.0,
            max_tokens=1000,
            top_p=1.0,
        )

        return response.choices[0].message.content

    def ask(self,question,top_k: int = 3):
            """结合回传chunks与qustion，调用大模型"""
            results = self.retrieve(question, top_k)
            context_chunks = results["documents"][0]
            return self.generate_answer(question, context_chunks)

    def context_chunks(self,question,top_k: int = 50):
                """结合回传chunks"""
                results = self.retrieve(question, top_k)
                context_chunks = results["documents"][0]
                return self.build_prompt(question, context_chunks)





    

# if __name__ == "__main__":

#     from pythonragtest.ragtest import ragtest
    


#     rag = ragtest("data/doc.md")
#     collection = rag.get_collection()
#     print(collection.count())
#     print("向量库记录数：", collection.count())
    
#     s = session(collection, "你是一个严谨的知识库助手 ……")
#     question = "哆啦A梦有多少个秘密道具？"
#     print(s.retrieve(question, top_k=3)["documents"][0])

#     print(s.ask(question))
