# AI Chat Service

基于 FastAPI 的 AI 对话服务，本地大模型（Ollama）私有化部署，以及 RAG 知识库问答(本代码以qwen2.5:3b为例)。

## 技术栈

- Python + FastAPI
- Docker
- Ollama（本地大模型部署）
- LangChain + ChromaDB（RAG 向量检索）
- Linux

## 功能特性

- **REST API 对话**：POST /chat
- **本地模型部署**：集成 Ollama，支持离线运行
- **RAG 知识库**：上传文档 → 向量化存储 → 基于文档问答
- Docker 一键部署
- 自动异常处理与日志记录
- 一个简易的gradio前端界面

## 快速开始

### 1. Docker 部署

bash

docker build -t ai-service-rag .

docker run -p 8000:8000 -p 7861:7861 -e OLLAMA_HOST=http://host.docker.internal:11434 ai-service-rag
### 2.RAG知识库使用

bash

curl -X POST "http://localhost:8000/upload" -F "file=@你的文档.txt"

curl -X POST "http://localhost:8000/ask" -H "Content-Type: application/json" -d "{\"question\":\"文档里说了什么？\"}"
### 3.项目结构
ai-chat-service/                    # 项目根目录

├── ai_service.py                   # FastAPI后端核心（API接口 + RAG逻辑）

├── app.py                          # Gradio前端界面

├── Dockerfile                      # Docker配置（双服务：FastAPI + Gradio）

├── supervisord.conf                # Supervisor进程管理配置

├── requirements.txt                # Python依赖列表

├── README.md                       # 项目文档

├── chroma_db/                      # ChromaDB向量库持久化目录（运行后生成）

│   └── ...

├── fastapi.log                     # FastAPI运行日志（运行后生成）

├── fastapi_err.log                 # FastAPI错误日志（运行后生成）

├── gradio.log                      # Gradio运行日志（运行后生成）

└── gradio_err.log                  # Gradio错误日志（运行后生成）
### 4.技术亮点
完整的 RAG 流程：文档切分 → 向量化 → ChromaDB 存储 → 检索生成

全部功能 Docker 化，支持跨环境一键部署
