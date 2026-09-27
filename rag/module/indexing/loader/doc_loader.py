
from langchain_community.document_loaders import UnstructuredFileLoader
from typing import List
import tqdm

from docx.table import _Cell, Table
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.text.paragraph import Paragraph
from docx import Document, ImagePart
from PIL import Image
from io import BytesIO
from rag.module.indexing.loader.ocr import get_rapid_ocr
import numpy as np


class CustomizedOcrDocLoader(UnstructuredFileLoader):

    # def _get_elements(self) -> List:
    #     def doc2text(filepath):
    #
    #         ocr = RapidOCR()
    #         doc = Document(filepath)
    #         resp = ""
    #
    #         def iter_block_items(parent):
    #             from docx.document import Document
    #             if isinstance(parent, Document):
    #                 parent_elm = parent.element.body
    #             elif isinstance(parent, _Cell):
    #                 parent_elm = parent._tc
    #             else:
    #                 raise ValueError("CustomizedOcrDocLoader parse fail")
    #
    #             for child in parent_elm.iterchildren():
    #                 if isinstance(child, CT_P):
    #                     yield Paragraph(child, parent)
    #                 elif isinstance(child, CT_Tbl):
    #                     yield Table(child, parent)
    #
    #         b_unit = tqdm.tqdm(total=len(doc.paragraphs)+len(doc.tables),
    #                            desc="CustomizedOcrDocLoader block index: 0")
    #         for i, block in enumerate(iter_block_items(doc)):
    #             b_unit.set_description(
    #                 "CustomizedOcrDocLoader block index: {}".format(i))
    #             b_unit.refresh()
    #             if isinstance(block, Paragraph):
    #                 # resp += block.text.strip() + "\n"
    #                 resp += block.text.strip()
    #                 images = block._element.xpath('.//pic:pic')  # 获取所有图片
    #                 for i, image in enumerate(images):
    #                     for img_id in image.xpath('.//a:blip/@r:embed'):  # 获取图片id
    #                         part = doc.part.related_parts[img_id]  # 根据图片id获取对应的图片
    #                         if isinstance(part, ImagePart):
    #                             image = Image.open(BytesIO(part._blob))
    #
    #                             result, _ = ocr(np.array(image))
    #                             if result:
    #                                 ocr_result = [line[1] for line in result]
    #                                 # resp += "\n".join(ocr_result)
    #                                 resp += "".join(ocr_result)
    #
    #             elif isinstance(block, Table):
    #                 for row in block.rows:
    #                     for cell in row.cells:
    #                         for paragraph in cell.paragraphs:
    #                             resp += paragraph.text.strip() + "\n"
    #             b_unit.update(1)
    #         return resp
    #
    #     text = doc2text(self.file_path)
    #     from unstructured.partition.text import partition_text
    #     return partition_text(text=text, **self.unstructured_kwargs)

    def _is_paragraph_end(self, text):
        if text.strip()[-1] in ["。", "？"]: return True
        else: return False

    def _get_elements(self) -> List:
        def doc2text(filepath):

            rapid_ocr = get_rapid_ocr()
            doc = Document(filepath)
            resp = ""
            resp_list = []

            def iter_block_items(parent):
                from docx.document import Document
                if isinstance(parent, Document):
                    parent_elm = parent.element.body
                elif isinstance(parent, _Cell):
                    parent_elm = parent._tc
                else:
                    raise ValueError("CustomizedOcrDocLoader parse fail")

                for child in parent_elm.iterchildren():
                    if isinstance(child, CT_P):
                        yield Paragraph(child, parent)
                    elif isinstance(child, CT_Tbl):
                        yield Table(child, parent)

            b_unit = tqdm.tqdm(total=len(doc.paragraphs)+len(doc.tables),
                               desc="CustomizedOcrDocLoader block index: 0")
            for i, block in enumerate(iter_block_items(doc)):
                b_unit.set_description(
                    "CustomizedOcrDocLoader block index: {}".format(i))
                b_unit.refresh()
                if isinstance(block, Paragraph):
                    resp += block.text
                    images = block._element.xpath('.//pic:pic')  # 获取所有图片
                    for i, image in enumerate(images):
                        for img_id in image.xpath('.//a:blip/@r:embed'):  # 获取图片id
                            part = doc.part.related_parts[img_id]  # 根据图片id获取对应的图片
                            if isinstance(part, ImagePart):
                                image = Image.open(BytesIO(part._blob))

                                # rapid ocr识别文本内容
                                rapid_ocr_result, _ = rapid_ocr(np.array(image))
                                if not rapid_ocr_result: continue
                                rapid_ocr_result = [line[1] for line in rapid_ocr_result]

                                for text in rapid_ocr_result:
                                    if self._is_paragraph_end(text):
                                        resp_list.append(resp + text)
                                        resp = ""
                                    else:
                                        resp += text.strip()

                b_unit.update(1)
            return "\n".join(resp_list)

        text = doc2text(self.file_path)
        from unstructured.partition.text import partition_text
        return partition_text(text=text, **self.unstructured_kwargs)


if __name__ == '__main__':
    import nltk, os
    nltk.data.path = [os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), "nltk_data")] \
                     + nltk.data.path
    loader = CustomizedOcrDocLoader(file_path="xxx.docx")
    docs = loader.load()
    print(docs[0].page_content)
    print("\n\n======================================")
    print(docs[0])
