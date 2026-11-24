from python_rag_lyra.rag import rag
from python_rag_lyra.session import session
import subprocess, sys
import os
from pathlib import Path

def handle_web():
    app = Path(__file__).parent / "app.py"
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(app)])


def build_rag(c:int = 1):
    r = rag("data/BCPONY.txt", chunks_model=c,model = os.getenv("EMBED_MODEL"))
    r.reset_collection()
    collection = r.build_collection()
   
    print(f"建库完成：{collection.name}，共 {collection.count()} 条")

while True:
    p = int(input(
"""===== 知识库助手 =====
1. 构建 / 重建知识库
2. 提问
3. 查看库状态
0. 退出
=====================
"""))
    try:
        match p:
            case 1:
                mod = int(input("选择切块方式：1.按文档段落切分,长段按句子切 2.按换行切分 3.按固定长度切分\n"))
                if input("会删除现有向量库，确认？(y/n): ").lower() != "y":
                    continue
                build_rag(mod)
            case 2:
                handle_web()
            case 3:
                rag = rag("data/BCPONY.txt")
                collection = rag.get_collection()
                print(f"库名: {collection.name}, 文档数: {collection.count()}")
            case 4:
                print("退出")
            case _:
                break
    except Exception as e:
                raise RuntimeError(f"运行失败：{e}") from e











