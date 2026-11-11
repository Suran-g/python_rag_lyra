from python_rag_lyra.rag import rag
from python_rag_lyra.session import session
import subprocess, sys
from pathlib import Path

def handle_web():
    app = Path(__file__).parent / "app.py"
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(app)])


def build_rag():
    r = rag("data/BCPONY.txt")
    collection = r.get_collection()

    if collection.count() == 0:          # 库是空的才建
        collection = r.build_collection()
        print("建库成功")
    else:
        print("已有数据库")

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
        if p == 1:
            build_rag()
        elif p == 2:
            handle_web()
        elif p == 3:
            rag = rag("data/BCPONY.txt")
            collection = rag.get_collection()
            print(f"库名: {collection.name}, 文档数: {collection.count()}")
        elif p == 0:
            print("退出")
            break
    except Exception as e:
                raise RuntimeError(f"运行失败：{e}") from e











