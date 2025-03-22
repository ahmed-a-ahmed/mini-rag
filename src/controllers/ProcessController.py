from .BaseController import BaseController
from .projectController import Projectcontroller
from models import ProcessingEnum
import os
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

class ProcessController(BaseController):
    def __init__(self, project_id: str):
        super().__init__()
        
        self.project_id = project_id
        self.project_path = Projectcontroller().get_project_path(project_id=project_id)
    
    def get_file_extension(self, file_name: str):
        return os.path.splitext(file_name)[-1]
    
    def get_file_loader(self, file_name: str):
        file_extension = self.get_file_extension(file_name)
        file_path = os.path.join(self.project_path, file_name)

        if file_extension == ProcessingEnum.TXT.value:
            return TextLoader(file_path=file_path,
                              encoding='utf-8')
        elif file_extension == ProcessingEnum.PDF.value:
            return PyPDFLoader(file_path=file_path)
        else:
            return None
    
    def get_file_content(self, file_name: str):
        loader = self.get_file_loader(file_name)
        return loader.load()
    
    def process_file_conent(self, file_content: list, file_name: str,
                            chunk_size: int, chunk_overlap: int):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = chunk_size,
            chunk_overlap = chunk_overlap,
            length_function = len,
        )
        file_content_texts = [
            rec.page_content
            for rec in file_content
        ]
        file_content_metadata = [
            rec.metadata
            for rec in file_content
        ]
        chunks = text_splitter.create_documents(
            file_content_texts,
            metadatas=file_content_metadata,
        )
        return chunks