from flask import jsonify, request
from flask_restful import Resource

from langchain_google_genai import GoogleGenerativeAI
from langchain.chains import QAGenerationChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.chains import RetrievalQA
from langchain_community.docstore.document import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceBgeEmbeddings

from getpass import getpass

def loadLLM():
    llm = GoogleGenerativeAI(
        model = "gemini-pro",
        google_api_key = "AIzaSyAiIh4uO1L9EcD-jqb4D9cn6BwggbcZwwM"
    )

    return llm

def fileProcessing(file):
    loader = PyPDFLoader(file)
    data = loader.load()

    question_gen = ''

    for page in data:
        question_gen += page.page_content

    splitter_ques_gen = RecursiveCharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap = 100
    )

    chunk_ques_gen = splitter_ques_gen.split_text(question_gen)
    document_ques_gen = [Document(page_content = t) for t in chunk_ques_gen]

    splitter_ques_gen = RecursiveCharacterTextSplitter(
        chunk_size = 300,
        chunk_overlap = 30
    )

    document_answer_gen = splitter_ques_gen.split_documents(
        document_ques_gen
    )

    return document_ques_gen, document_answer_gen

class GenerateQuestionAnswers(Resource):
    @staticmethod
    def post(bloom_level):
        file = request.files.get('file')
        file.save('temp.pdf')

        return jsonify({ 'data': 'OK' })