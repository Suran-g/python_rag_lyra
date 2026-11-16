# python-rag-lyra

一个基于 **RAG（检索增强生成）** 的角色扮演对话助手：把小说文本切分、向量化后存入本地向量库，聊天时先检索与问题最相关的原文片段，再交给大模型模仿原作文风进行角色扮演。

以《背景小马》中的角色 **天琴心弦** 为默认示例，角色设定保存在 [data/tianqin.md](data/tianqin.md)，可替换成任意角色与任意知识库文本。

---

## 功能特性

- **本地向量化**：通过 Ollama 调用 Embedding 模型，文本不出本机
- **三种切片策略**：段落合并 + 长段句切、按空行切分、固定长度切分
- **向量检索**：Chroma 持久化 .env_example 向量库，余弦距离，可调 `top_k`
- **角色扮演**：检索原文注入 Prompt，让模型模仿资料的文风与语气
- **流式对话**：Streamlit 网页界面，逐字输出
- **会话管理**：新建 / 切换 / 删除会话，历史自动保存为 JSON
- **双入口**：命令行菜单 或 Streamlit 网页

---

## 工作原理

```mermaid
flowchart LR
    A["知识库文档<br/>data/*.txt"] --> B["切分<br/>chunk_size / overlap"]
    B --> C["Ollama Embedding<br/>qwen3-embedding:4b"]
    C --> D[("Chroma 向量库<br/>cosine")]

    E[用户提问] --> F[问题向量化]
    F --> G["Top-K 相似检索"]
    D --> G
    G --> H["拼接 Prompt<br/>角色设定 + 参考资料 + 问题"]
    H --> I["DeepSeek 生成回答"]
    I --> J["Streamlit 流式输出"]
    J --> K["sessions/*.json"]
```

1. **建库**：读取文档 → 按所选策略切块 → 批量调用 Ollama Embedding → 写入 Chroma（附 `source`、`chunk_index` 元数据）
2. **检索**：用户问题向量化 → 在 Chroma 中取余弦距离最近的 `top_k` 个片段
3. **生成**：把片段编号后拼进 Prompt，连同角色设定一起发送给 DeepSeek
4. **保存**：对话记录写入 `sessions/`，可随时恢复

---

## 技术栈

| 组件 | 用途 |
| --- | --- |
| Python 3.14 + [uv](https://github.com/astral-sh/uv) | 运行环境与依赖管理 |
| [ChromaDB](https://www.trychroma.com/) | 本地持久化向量数据库（HNSW + 余弦距离） |
| [Ollama](https://ollama.com/) | 本地 Embedding 服务（默认 `qwen3-embedding:4b`） |
| [DeepSeek](https://www.deepseek.com/) | 对话生成（OpenAI 兼容接口） |
| [Streamlit](https://streamlit.io/) | 网页聊天界面 |
| tqdm | 向量化进度条 |

---

## 目录结构

```text
python_rag_lyra/
├── data/
│   ├── tianqin.md            # 角色设定（System Prompt，随仓库提供）
│   └── BCPONY.txt            # 知识库原文（需自备）
├── sessions/                 # 对话历史，运行时自动生成
├── src/python_rag_lyra/
│   ├── rag.py                # 切分 → 向量化 → 写入 Chroma
│   ├── embedding.py          # Ollama Embedding 客户端
│   ├── session.py            # 检索 + Prompt 拼接 + 调用 DeepSeek
│   ├── app.py                # Streamlit 聊天界面
│   └── main.py               # 命令行菜单入口
├── .env_example              # 配置模板
├── pyproject.toml
└── uv.lock
```

---

## 快速开始

### 1. 环境要求

- Python 3.14+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- 本地已安装并启动 [Ollama](https://ollama.com/download)
- 一个 DeepSeek API Key（[申请地址](https://platform.deepseek.com/)）

### 2. 拉取 Embedding 模型

```bash
ollama pull qwen3-embedding:4b
ollama list   # 确认模型已就绪
```

### 3. 安装依赖

```bash
git clone https://github.com/Suran-g/python_rag_lyra.git
cd python_rag_lyra
uv sync
```

### 4. 配置环境变量

```bash
cp .env
```

编辑 `.env`，至少填入 API Key：

```dotenv
DEEPSEEK_API_KEY="sk-xxxxxxxx"
```

完整配置项：

| 变量 | 说明 | 默认示例 |
| --- | --- | --- |
| `DEEPSEEK_API_KEY` | DeepSeek API Key（**必填**） | — |
| `DEEPSEEK_BASE_URL` | 对话接口地址 | `https://api.deepseek.com` |
| `DEEPSEEK_MODEL` | 对话模型 | `deepseek-chat` |
| `OLLAMA_HOST` | Ollama 服务地址 | `http://localhost:11434` |
| `EMBED_MODEL` | Embedding 模型 | `qwen3-embedding:4b` |
| `CHROMA_PATH` | 向量库存储路径 | `data/chroma_db` |
| `COLLECTION_NAME` | 集合名称 | `doraemon` |
| `SYSTEM_PROMPT_PATH` | 角色设定文件路径 | `data/tianqin.md` |

### 5. 准备知识库文本

仓库**不包含**小说原文。把你要检索的文本放到 `data/` 下，并重命名
例如：

```text
data/BCPONY.txt
```


### 6. 构建知识库并启动

```bash
uv run python -m python_rag_lyra.main
```

按菜单提示操作：

```text
===== 知识库助手 =====
1. 构建 / 重建知识库
2. 提问
3. 查看库状态
0. 退出
=====================
```

选择 `1` 后可以指定切块方式：

| 编号 | 策略 | 参数 | 说明 |
| --- | --- | --- | --- |
| `1` | 段落合并 + 长段句切 | `chunk_size=500`, `overlap=80` | 优先按空行合并段落，超长段落再按中文句号等切分（推荐） |
| `2` | 按空行切分 | 无 | 保留原段落，块大小不固定 |
| `3` | 固定长度切分 | `chunk_size=200`, `overlap=80` | 按字符数硬切，可能有句子被截断 |

切块完成后，选择 `2` 启动网页界面；也可以直接运行：

```bash
uv run streamlit run src/python_rag_lyra/app.py
```

---

## 参数说明

### 检索参数

| 参数 | 位置 | 当前默认值 | 说明 |
| --- | --- | --- | --- |
| `top_k` | `session.retrieve()` | `5` | 检索返回的片段数 |
| `top_k` | `session.ask()` | `3` | 命令行问答使用 |
| `top_k` | `session.context_chunks()` | `50` | 网页版注入的片段数 |
| `hnsw:space` | `rag.get_collection()` | `cosine` | 距离度量，建库时固定 |

> `top_k` 越大召回越全，但无关片段也会混入 Prompt；文本问答一般 3~6 条即可，配合更细的切片再适当增大。

### 生成参数

| 参数 | `session.py` | `app.py` | 说明 |
| --- | --- | --- | --- |
| `model` | `DEEPSEEK_MODEL` | `deepseek-flash` | 生成模型 |
| `temperature` | `2.0` | `1.1` | 随机性，角色扮演可偏高 |
| `top_p` | `1.0` | `0.5` | 核采样 |
| `max_tokens` | `1000` | `10000` | 回答长度上限 |
| `stream` | `False` | `True` | 流式输出 |
| `thinking` | — | `disabled` | DeepSeek 思考模式开关 |

### 切片参数

`rag` 构造函数支持自定义：

```python
rag("data/BCPONY.txt", chunk_size=500, overlap=80, chunks_model=1)
```

| 参数 | 说明 |
| --- | --- |
| `chunk_size` | 目标块大小（字符数） |
| `overlap` | 相邻块重叠字符数，防止答案被切断 |
| `chunks_model` | 切分策略：`1` 段落合并 / `2` 空行 / `3` 固定长度 |

---

## 数据与隐私

- `.env`、`sessions/`、`data/` 下的文档均已在 [.gitignore](.gitignore) 中排除，不会被提交
- Embedding 在本地 Ollama 完成，原文不会上传
- 只有检索到的片段与对话内容会发送给 DeepSeek
- 知识库原文版权归原作者所有，本项目仅用于学习与个人用途

---

## 其他

- 角色设定与示例文本来源于同人作品《背景小马》，版权归原作者所有
