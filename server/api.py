from fastapi import FastAPI
import uvicorn
from server.utils import BaseResponse, ListResponse
from server.knowledge import (
    create_knowledge_base,
    delete_knowledge_base,
    clear_knowledge_base,
    upload_docs,
    list_kbs,
)
from server.chat import knowledge_base_chat
from server.trace import trace_rag_pipeline

VERSION = "v1.0"


def create_app(run_mode: str = None):
    app = FastAPI(
        title="RAG 接口服务",
        description="RAG 知识库管理与问答接口",
        version=VERSION,
    )
    mount_app_routes(app, run_mode=run_mode)
    return app


def mount_app_routes(app: FastAPI, run_mode: str = None):
    app.post(
        "/knowledge_base/list_knowledge_bases",
        tags=["知识库管理"],
        response_model=ListResponse,
        summary="获取知识库列表",
    )(list_kbs)
    app.post(
        "/knowledge_base/create_knowledge_base",
        tags=["知识库管理"],
        response_model=BaseResponse,
        summary="创建知识库",
    )(create_knowledge_base)
    app.post(
        "/knowledge_base/delete_knowledge_base",
        tags=["知识库管理"],
        response_model=BaseResponse,
        summary="删除知识库",
    )(delete_knowledge_base)
    app.post(
        "/knowledge_base/clear_knowledge_base",
        tags=["知识库管理"],
        response_model=BaseResponse,
        summary="清空知识库",
    )(clear_knowledge_base)
    app.post(
        "/knowledge_base/upload_docs",
        tags=["知识库管理"],
        response_model=BaseResponse,
        summary="上传文件到知识库并/或进行向量化",
    )(upload_docs)

    app.post(
        "/chat/knowledge_base_chat",
        tags=["对话"],
        summary="与知识库对话",
    )(knowledge_base_chat)


def run_api(host, port, **kwargs):
    app = create_app()
    if kwargs.get("ssl_keyfile") and kwargs.get("ssl_certfile"):
        uvicorn.run(
            app,
            host=host,
            port=port,
            ssl_keyfile=kwargs.get("ssl_keyfile"),
            ssl_certfile=kwargs.get("ssl_certfile"),
        )
    else:
        uvicorn.run(app, host=host, port=port)
