import os
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

# ==============================
# 初始化应用
# ==============================
app = FastAPI(title="行业知识问答助手 🚀")

# 跨域配置（允许前端访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================
# 基础配置
# ==============================
UPLOAD_DIR = "uploads"
VECTOR_DIR = "vectorstore"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(VECTOR_DIR, exist_ok=True)

# 初始化 OpenAI 客户端
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"),
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
# 存储用户对话历史
conversation_histories = {}
# 初始化向量化模型（DashScope 的 embedding 模型）
embeddings = DashScopeEmbeddings(
    model="text-embedding-v1", dashscope_api_key=os.getenv("OPENAI_API_KEY"))

# ==============================
# 文件上传接口
# ==============================


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    上传文件 -> 解析 -> 切分 -> 向量化 -> 存储
    """
    file_path = os.path.join(UPLOAD_DIR, str(file.filename))
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # 根据文件类型选择加载器
    filename = file.filename or ""
    if filename.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif filename.endswith(".docx"):
        loader = Docx2txtLoader(file_path)
    else:
        loader = TextLoader(file_path, encoding="utf-8")

    # 读取文档
    docs = loader.load()
    # 分块
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_documents(docs)
    # 建立或更新向量库
    if os.path.exists(VECTOR_DIR) and os.listdir(VECTOR_DIR):
        # 已存在向量库 -> 追加新文档
        db = FAISS.load_local(VECTOR_DIR, embeddings,
                              allow_dangerous_deserialization=True)
        db.add_documents(chunks)
    else:
        # 第一次创建向量库
        db = FAISS.from_documents(chunks, embeddings)
    db.save_local(VECTOR_DIR)

    return {"message": f"{file.filename} 上传成功并已入库！", "chunks": len(chunks)}

# ==============================
# QA 问答接口
# ==============================


@app.post("/qa")
async def qa(query: str = Form(...), session_id: str = Form(...)):
    """
    从向量库中检索最相似内容 -> 结合上下文生成回答
    session_id: 用户会话ID，用于保存多轮对话上下文
    """
    # 获取会话历史
    history = conversation_histories.get(session_id, [])
    # 加入本轮用户问题
    history.append({"role": "user", "content": query})
    # 检查是否已有向量库
    if not os.path.exists(VECTOR_DIR) or not os.listdir(VECTOR_DIR):
        return {"error": "当前暂无知识库，请先上传文档！"}
    # 加载向量库
    db = FAISS.load_local(VECTOR_DIR, embeddings,
                          allow_dangerous_deserialization=True)
    # 检索相似内容
    docs = db.similarity_search(query, k=3)
    context = "\n\n".join([d.page_content for d in docs])
    # 构造提示
    prompt = f"""
你是一位专业的行业知识助手。请严格根据下列参考资料回答用户的问题。
要求：
1. 仅使用参考资料中的信息回答，不得凭空推测。
2. 如果资料中没有相关信息，请明确回答“资料中未提及”。
3. 回答尽量简明、直接，避免无关信息。

参考资料：
{context}

用户问题：
{query}

请给出答案：
"""
    prompt_messages = [
        {"role": "user", "content": prompt}
    ] + history
    completion = client.chat.completions.create(
        model="qwen-plus",
        messages=prompt_messages
    )

    answer = completion.choices[0].message.content
    # 保存模型回答到历史
    history.append({"role": "assistant", "content": answer})
    conversation_histories[session_id] = history  # 更新会话
    return {"query": query, "answer": answer, "source_count": len(docs), "session_id": session_id}

# 返回当前上传的文件列表


@app.get("/files")
async def list_files():
    """
    返回已上传的文件列表
    """
    files = os.listdir(UPLOAD_DIR)
    return {"files": files}

# ==============================
# 首页测试
# ==============================


@app.get("/")
async def root():
    return {"message": "行业知识问答助手已启动 🚀", "functions": ["upload", "qa"]}
