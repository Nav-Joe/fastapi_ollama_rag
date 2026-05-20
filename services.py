from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
import shutil
import os
#OLLAMA_URL = "http://host.docker.internal:11434"
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
app = FastAPI()

vectorstore = None
retriever = None

class AskRequest(BaseModel):
    question: str


# 启动时自动加载已有向量库
@app.on_event("startup")
async def load_existing_vectorstore():
    global vectorstore, retriever
    if os.path.exists("./chroma_db"):
        embeddings = OllamaEmbeddings(model="qwen2.5:3b")
        vectorstore = Chroma(
            persist_directory="./chroma_db",
            embedding_function=embeddings
        )
        retriever = vectorstore.as_retriever()
        print(f"加载已有向量库，共 {vectorstore._collection.count()} 条记录")
    else:
        print("没有已有向量库，等待上传")

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    global vectorstore, retriever
    
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    with open(temp_path, "r", encoding="utf-8") as f:
        text = f.read()
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.create_documents([text])
    
    # 向量化存储
    embeddings = OllamaEmbeddings(model="qwen2.5:3b")
    # 如果已有向量库，追加；没有就创建
    if vectorstore is not None:
        vectorstore.add_documents(chunks)
    else:
        vectorstore = Chroma.from_documents(
            chunks, 
            embeddings,
            persist_directory="./chroma_db"
        )
    retriever = vectorstore.as_retriever()
    
    os.remove(temp_path)
    
    return {"message": f"上传成功，处理了{len(chunks)}个段落"}

@app.post("/ask")
async def ask(req: AskRequest):
    global retriever
    
    if retriever is None:
        raise HTTPException(status_code=400, detail="请先上传文档")
    
    # 检索相关段落
    docs = retriever.invoke(req.question)
    context = "\n".join([d.page_content for d in docs])
    
    llm = OllamaLLM(model="qwen2.5:3b")
    prompt = f"基于以下信息回答问题：\n{context}\n\n问题：{req.question}"
    answer = llm.invoke(prompt)
    
    return {"answer": answer, "context": context}

def ask_local_model(message: str) -> str:
    response = requests.post(
        f"{OLLAMA_HOST}/api/generate",
        json={"model": "qwen2.5:3b", "prompt": message, "stream": False}
    )
    return response.json()["response"]

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        reply = ask_local_model(req.message)
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/clear")
async def clear(confirm: str = ""):
    if confirm != "yes":
        raise HTTPException(status_code=400, detail="请传入 confirm=yes 确认清空")
    
    global vectorstore, retriever
    if os.path.exists("./chroma_db"):
        shutil.rmtree("./chroma_db")
    vectorstore = None
    retriever = None
    return {"message": "向量库已清空"}
