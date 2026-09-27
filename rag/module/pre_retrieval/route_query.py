import os
from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from rag.connector.base import llm
from rag.connector.database.repository.knowledge_file_repository import list_files_from_db


# llm = ChatOpenAI(model='gpt-4',
#                 openai_api_key="",
#                 temperature=0)

def route_query_to_files(question, knowledge_base_name):

    exist_files = [os.path.basename(f) for f in list_files_from_db(knowledge_base_name)]
    double_check_keys = ["重庆"]

    prompt = PromptTemplate(
        template="""你是一个擅长将问题路由到文件的专家。\n
        已知有一个包含数据库中的所有文件名称的列表，请根据用户输入的问题，判断回答该问题需要使用哪个文件中的知识。\n
        判断的主要依据是问题中是否与文件名称有完全相同的关键词。\n
        注意如果文件名称中有明确的地域名称，那么只有当问题中出现完全相同的地域名称词才能将它们路由，“市级”不算地域名。\n
        注意你不需要将关键词返回，注意不需要做假设和解释，而是直接以JSON格式返回结果，并且以 "datasource"作为关键词给出路由的文件名称。\n
        若问题中的关键词在多个文件中都出现，请不要进行文件路由，请返回空JSON。 \n
        如果无法根据关键词判断问题应该和哪个文件路由，请返回空JSON。 \n
        下面是包含所有文件名称的列表: {file_list} \n
        需要路由的问题: {question}""",
        input_variables=["file_list", "question"]
    )

    # question_router = prompt | llm | JsonOutputParser()
    # res = question_router.invoke({"file_list": str(exist_files), "question": question})

    try:
        question_router = prompt | llm | JsonOutputParser()
        res = question_router.invoke({"file_list": str(exist_files), "question": question})
        if isinstance(res, dict):
            file_name = res["datasource"]
            if file_name in exist_files:
                for key in double_check_keys:
                    if key in file_name and key not in question:
                        return []
                return [file_name]
        else:
            return []
    except Exception as e:
        return []

#
# question_list = [
#         "阿蓬江流域一级水功能区划有哪些？区划依据是什么？",
#         "阿蓬江流域水资源保护还存在哪些问题？",
#         "阿蓬江现阶段影响健康最为突出的问题有哪些？什么原因导致的？",
#         "阿蓬江面源污染控制目标有哪些？",
#         "阿蓬江管理保护有哪些具体目标，为达成这些目标制定了哪些具体任务？",
#
#         "关于全面推行河长制的意见主要提出了哪些基本原则，保障措施是什么",
#
#         "重庆市全面推行河长制工作方案中主要目标有哪些？",
#         "重庆市全面推行河长制工作方案中市级责任单位主要职责有哪些？",
#
#         "河长制市级责任单位有哪些？",
#         "市级河长体系设置中市级河流有哪些？",
#
#         "市总河长巡查和区县级总河长巡查每年不少于多少次？",
#         "工作督查具体有哪些类别？",
#         "河长制信息通过哪些方式进行分开与共享？",
#
#         "2020 年，城市、乡镇生活污水集中处理率是多少，处理排放的污染物是否达到相应排放标准？",
#
#         "河流评价指标体系中有哪些准则层，对应的指标层和指标类型是什么？",
#         "河湖健康评价指南中评价河段按照哪些方法确定？",
#         "河湖健康评价赋分计算方法是什么？如何确定各项评价指标的权重，以确保赋分计算能够准确反映河湖健康状态的关键因素？",
#         "河湖健康评价报告中，除了基本的评价指标得分与总评分外，还包含哪些内容？",
#         "参考点确定方法中具体有哪些参考点，主要确定依据是什么？",
#         "河湖健康评价专题图具体有哪些内容？",
#         "河湖“四乱”分为哪些问题类型，具体的问题认定和严重程度如何判断？",
#
#         "重庆市幸福河湖评价有哪些主要特征，基本原则是什么？",
#         "重庆市幸福河湖评价指标体系中准入评价指标有哪些，有什么具体含义？"
#     ]
#
#
# for question in question_list:
#     res = route_query_to_files(question, "shuili_demo")
#     print(question, res)