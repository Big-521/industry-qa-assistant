# 🚀 行业知识问答助手（Industry QA Assistant）

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)]()
[![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-red)]()
[![LangChain](https://img.shields.io/badge/LangChain-Embeddings-orange)]()
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)]()

一个基于 **FastAPI + Streamlit + OpenAI 向量检索** 架构的智能知识问答系统。
支持 **多文件上传、向量化入库、上下文问答、多轮对话**，可本地快速部署，轻量易扩展。

---

## 📘 功能特性

### ✅ 文件上传与知识入库
- 支持上传 **PDF、DOCX、TXT** 等多种文件类型；
- 自动提取文本并进行 **向量化处理**；
- 存入本地知识库，用于后续问答检索。

### 💬 智能问答
- 基于 **OpenAI Embeddings + 向量数据库检索**；
- 支持 **上下文记忆、多轮对话**；
- 若资料中未提及，模型会明确说明。

### 🧠 后端（FastAPI）
- 文件上传接口：`/upload_files`
- 问答接口：`/qa`
- 聊天接口：`/chat`
- 文件列表接口：`/list_files`
- 支持跨域访问，前后端可独立运行

### 🎨 前端（Streamlit）
- 左侧知识库文件展示区
- 右侧问答区（气泡式 UI，美观简洁）
- 自动与后端交互，实现实时问答响应

---

## 🧩 项目结构

```
📁 项目根目录
│
├── app.py            # FastAPI 后端（上传、向量化、QA接口等）
├── ui_app.py            # Streamlit 前端（上传+聊天界面）
├── uploads/            # 上传文件存储目录（自动创建）
├── vectorstore/        # 向量数据库目录（自动创建）
└── README.md           # 项目说明文件
```

---

## ⚙️ 环境依赖

### 1️⃣ 安装依赖

```bash
pip install fastapi uvicorn streamlit openai langchain langchain-community faiss-cpu requests
```

> 💡 如果使用 DashScope 的向量化模型（阿里通义），请确保安装：
```bash
pip install dashscope
```

---

## 🔑 环境变量配置

在系统环境变量或 `.env` 文件中设置以下内容：

```bash
OPENAI_API_KEY=你的_DashScope_API_KEY
```

> 可在 [阿里云 DashScope 控制台](https://dashscope.console.aliyun.com/) 获取。

---

## 🚀 启动项目

### 1️⃣ 启动 FastAPI 后端

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

启动后访问测试接口：
👉 [http://127.0.0.1:8000](http://127.0.0.1:8000)

返回：
```json
{"message": "行业知识问答助手已启动 🚀", "functions": ["upload", "qa"]}
```

---

### 2️⃣ 启动 Streamlit 前端

```bash
streamlit run ui_app.py
```

访问：
👉 [http://localhost:8501](http://localhost:8501)

---

---

## 🧠 使用说明

1. 打开前端页面；
2. 在左侧上传 PDF/DOCX/TXT 文件；
3. 系统自动入库并显示知识文件；
4. 在右侧输入问题即可得到基于资料的精准回答；
5. 聊天记录自动保存（同一 session_id 内）；
6. 若资料中未提及，系统会提示“资料中未提及相关内容”。

---

## 💬 使用流程

1️⃣ **上传文档**
　支持 PDF、DOCX、TXT，系统会自动解析、分块、向量化并入库。

2️⃣ **查看已入库文件**
　页面展示当前知识库中所有已上传文件。

3️⃣ **输入问题**
　向 AI 提问（例如：“文档中提到的主要技术是什么？”）
　AI 将基于知识库内容回答。

---

## 🧠 技术说明

| 模块 | 说明 |
|------|------|
| **FastAPI** | 后端接口服务 |
| **Streamlit** | 前端界面 |
| **FAISS** | 向量数据库（本地存储） |
| **LangChain** | 文档解析与向量化 |
| **DashScope Embeddings** | 向量模型，用于语义检索 |
| **Qwen-plus** | 问答生成模型（兼容 OpenAI 接口） |

---

## 🧰 常见问题（FAQ）

**Q1:** 上传文件后提示 “当前暂无知识库”？
➡️ 请确保已成功上传文件，并确认 `vectorstore/` 下存在索引文件。

**Q2:** 模型请求报错？
➡️ 检查 `OPENAI_API_KEY` 是否正确配置。

**Q3:** Streamlit 前端无法连接后端？
➡️ 确保 FastAPI 已运行，且 `API_URL` 在文件2.py 中设置为正确地址（默认 http://127.0.0.1:8000）。

---

## 🧑‍💻 作者

**Yanz**
📘 个人实验项目，旨在构建一个轻量级本地行业知识问答助手。

---

## 🧾 License

MIT License

---

### 🌟 Star 支持
如果该项目对你有帮助，欢迎点亮 ⭐️ Star！
👉 [GitHub 项目地址](https://github.com/Big-521/industry-qa-assistant)
