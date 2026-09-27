# LLM-RAG应用构建方案

## 代码架构
- conf: 配置文件
- nltk_data: 预下载的数据包
- rag: rag应用的核心代码
- server: 服务层的代码实现
- requirements.txt: 整个应用的依赖包列表
- start.py: 一键启动整个服务的脚本

## 新建虚拟环境
```shell
conda create -n llm-rag python=3.10 -y
conda activate llm-rag
pip install -r requirements.txt
```

## 核心功能/应用架构

### 流程定义

- Indexing：负责构建知识库
- Retrieval：当用户和大模型进行对话的时候，它使用用户的输入问题，到知识库中进行检索，得到和问题相关的知识片段
- Generate：利用Retrieval流程给出的检索结果，负责生成最终的答案

### 组件

Modules

### 第三方服务依赖

- 大模型（以在线api服务形式接入）
- 向量数据库：Milvus 
- Embedding Model


## 部署

### 启动向量数据服务

使用的是milvus向量数据库，启动的话直接在本地启动一个milvus容器：https://milvus.io/docs/v2.4.x/install_standalone-docker.md

启动完成后，将参数配置到config.yaml文件中

### 下载模型：Embedding & Rerank

可以选择 https://hf-mirror.com/ 或者 https://modelscope.cn/ 进行下载

把各自的路径配置到config.yaml文件中

### 启动后端服务

```shell
python server/main.py --create_tables
```
在浏览器里输入：127.0.0.1:7861/docs，就可以看到我们应用已经发布的api

### 启动WebUI

```shell
streamlit run server/web_app.py
```
在浏览器里输入：127.0.0.1:8501 即可体验相应功能

