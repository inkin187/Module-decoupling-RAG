import os
import sys

sys.path.append(os.getcwd())

import requests
import streamlit as st

from rag.common.configuration import settings
from server.utils import ApiRequest

log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
if not os.path.exists(log_dir):
    os.mkdir(log_dir)

VECTOR_STORE_TYPE = settings.vector_store.type


def web():
    base_url = f"http://127.0.0.1:{settings.server.api_server_port}"

    try:
        resp = requests.get(base_url + "/docs", timeout=3)
        if resp.status_code == 200:
            api = ApiRequest(base_url=base_url)
        else:
            st.error("API 服务未正确启动")
            return
    except requests.exceptions.RequestException:
        st.error("请先启动 API 服务")
        return

    from rag.connector.database.repository.knowledge_file_repository import list_files_from_db
    from rag.connector.database.repository.knowledge_base_repository import list_kbs_from_db

    st.set_page_config(page_title="RAG 知识库助手", layout="wide")
    st.title("RAG 知识库助手")
    st.caption("上传知识文件，选择知识库后即可开始对话。")

    with st.sidebar:
        st.header("知识库管理")
        knowledge_base_list = list_kbs_from_db()[::-1]

        if (
            "selected_kb_name" in st.session_state
            and st.session_state["selected_kb_name"] in knowledge_base_list
        ):
            selected_kb_index = knowledge_base_list.index(st.session_state["selected_kb_name"])
        else:
            selected_kb_index = 0

        selected_kb = st.selectbox(
            "请选择或新建知识库",
            knowledge_base_list + ["新建知识库"],
            index=selected_kb_index,
        )
        st.session_state["selected_kb_name"] = selected_kb

        if selected_kb == "新建知识库":
            with st.form("create_kb", clear_on_submit=True, border=False):
                kb_name = st.text_input(
                    "请输入知识库名称",
                    placeholder="新知识库名称，不支持中文命名",
                    key="kb_name",
                )
                submit_create_kb = st.form_submit_button("新建", use_container_width=True)

            if submit_create_kb:
                if not kb_name or not kb_name.strip():
                    st.error("知识库名称不能为空")
                elif kb_name in knowledge_base_list:
                    st.error(f"名为 {kb_name} 的知识库已经存在")
                else:
                    resp = api.create_knowledge_base(
                        knowledge_base_name=kb_name,
                        vector_store_type=VECTOR_STORE_TYPE,
                    )
                    if resp.get("code") == 200:
                        st.rerun()
                    else:
                        st.error(f"知识库 {kb_name} 创建失败")

        elif selected_kb:
            with st.form("upload_files_to_kb", clear_on_submit=True):
                st.subheader("上传文件到知识库")
                uploaded_files = st.file_uploader("选择一个或多个文件", accept_multiple_files=True)
                submitted = st.form_submit_button("上传")

            placeholder = st.empty()
            exist_files = [os.path.basename(f) for f in list_files_from_db(selected_kb)]
            with placeholder.container():
                if exist_files:
                    st.subheader("知识库中已有文件")
                    for file_name in exist_files:
                        st.write(file_name)
                else:
                    st.subheader("当前知识库为空")

            if uploaded_files and submitted:
                st.info(f"正在上传 {len(uploaded_files)} 个文件到知识库 {selected_kb}")
                resp = api.upload_kb_docs(uploaded_files, selected_kb)

                if resp.get("code") == 200:
                    failed_files = resp.get("failed_files")
                    if failed_files:
                        msg = "下列文件上传失败：" + "\n".join(
                            [os.path.basename(f_name) for f_name in list(failed_files.keys())]
                        )
                        st.error(msg)
                    else:
                        st.success("所有文件上传成功")
                else:
                    st.error("文件上传失败")

                exist_files = [os.path.basename(f) for f in list_files_from_db(selected_kb)]
                with placeholder.container():
                    if exist_files:
                        st.subheader("知识库中已有文件")
                        for file_name in exist_files:
                            st.write(file_name)
                    else:
                        st.subheader("当前知识库为空")

            cols = st.columns(2)
            if cols[0].button("清空知识库", use_container_width=True):
                res = api.clear_knowledge_base(selected_kb)
                if res.get("code") == 200:
                    placeholder.subheader("当前知识库为空")
                else:
                    st.error(f"清空当前知识库 {selected_kb} 失败")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["context"])

    if prompt := st.chat_input("请输入您的问题"):
        if selected_kb not in knowledge_base_list:
            st.error("对话前请选择一个知识库")
        else:
            st.chat_message("user").markdown(prompt)
            st.session_state.messages.append({"role": "user", "context": prompt})
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                for res in api.knowledge_base_chat(prompt, knowledge_base_name=selected_kb):
                    full_response = res
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "context": full_response})


if __name__ == "__main__":
    web()
