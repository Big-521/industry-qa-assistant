import streamlit as st
import requests
import uuid

# 页面配置
st.set_page_config(page_title="行业知识问答助手 🚀", page_icon="📘", layout="wide")
API_URL = "http://127.0.0.1:8000"  # FastAPI 地址
# 会话 ID
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
# 聊天历史初始化
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 页面标题和说明
st.title("行业知识问答助手 🚀")
st.write("上传文档，AI 根据知识库回答你的问题。")

# 已入库文件展示
st.subheader("📂 已入库文件")


@st.cache_data
def get_file_list():
    resp = requests.get(f"{API_URL}/files")
    return resp  # 返回 Response 对象


try:
    response = get_file_list()
    if response.status_code == 200:
        data = response.json()
        files = data.get("files", [])
        if files:
            for f in files:
                st.write(f"✅ {f}")
        else:
            st.info("当前没有已入库文件")
    else:
        st.error("获取文件列表失败")
except Exception as e:
    st.error(f"请求出错：{e}")

# 上传文件并入库
st.subheader("📁 上传文档")
with st.form("upload_form"):
    uploaded_file = st.file_uploader(
        "选择文件 (PDF / DOCX / TXT)", type=["pdf", "docx", "txt"])
    submit_upload = st.form_submit_button("上传并入库")
    if submit_upload and uploaded_file is not None:
        with st.spinner("正在上传并处理文件..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            try:
                response = requests.post(f"{API_URL}/upload", files=files)
                if response.status_code == 200:
                    data = response.json()
                    st.success(f"{data['message']}，共分成 {data['chunks']} 块内容")
                else:
                    st.error(f"上传失败：{response.text}")
            except Exception as e:
                st.error(f"请求出错：{e}")
# CSS 样式
st.markdown("""
<style>
.user-msg {
    background-color:#DCF8C6;
    padding:10px;
    border-radius:10px;
    text-align:right;
    margin:5px 0;
    max-width:70%;
    float:right;
    clear:both;
}
.ai-msg {
    background-color:#F1F0F0;
    padding:10px;
    border-radius:10px;
    text-align:left;
    margin:5px 0;
    max-width:70%;
    float:left;
    clear:both;
}
.clearfix::after {
    content: "";
    clear: both;
    display: table;
}
</style>
""", unsafe_allow_html=True)

# 展示聊天记录（左右气泡）
st.subheader("💬 聊天问答")
for chat in st.session_state.chat_history:
    if chat["role"] == "user":
        st.markdown(
            f'<div class="clearfix"><div class="user-msg">{chat["content"]}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="clearfix"><div class="ai-msg">{chat["content"]}</div></div>', unsafe_allow_html=True)


# 聊天式问答
def send_question():
    q = st.session_state.current_query.strip()
    if not q:
        st.warning("请输入问题！")
        return

    try:
        response = requests.post(
            f"{API_URL}/qa",
            data={"query": q, "session_id": st.session_state.session_id}
        )
        if response.status_code == 200:
            data = response.json()
            # 保存聊天记录
            st.session_state.chat_history.append({
                "role": "user",
                "content": data["query"]
            })
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": data["answer"]
            })
            # 清空输入框
            st.session_state.current_query = ""  # ✅ 可以安全清空
        else:
            st.error(f"请求失败：{response.text}")
    except Exception as e:
        st.error(f"请求出错：{e}")


# 表单
with st.form("chat_form"):
    st.text_input("请输入你的问题", key="current_query")
    st.form_submit_button("发送", on_click=send_question)
