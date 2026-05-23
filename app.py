import gradio as gr
import requests

API_URL = "http://localhost:8000"

def upload_file(file):
    with open(file.name, "rb") as f:
        response = requests.post(f"{API_URL}/upload", files={"file": f})
    return response.json()["message"]

def chat(message):
    response = requests.post(f"{API_URL}/ask", json={"question": message})
    return response.json()["answer"]

with gr.Blocks() as demo:
    gr.Markdown("# AI 知识库问答系统")
    
    with gr.Row():
        with gr.Column():
            file_input = gr.File(label="上传文档")
            upload_btn = gr.Button("上传")
            upload_status = gr.Textbox(label="状态")
        
        with gr.Column():
            msg_input = gr.Textbox(label="输入问题")
            send_btn = gr.Button("发送")
            answer_output = gr.Textbox(label="回答", lines=5)
    
    upload_btn.click(upload_file, inputs=file_input, outputs=upload_status)
    send_btn.click(chat, inputs=msg_input, outputs=answer_output)

demo.launch(server_name="0.0.0.0", server_port=7861)
