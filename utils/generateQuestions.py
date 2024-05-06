from langchain_google_genai import GoogleGenerativeAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain_community.docstore.document import Document
from langchain_community.document_loaders import PyPDFLoader

file_content = ""

def loadLLM():
    llm = GoogleGenerativeAI(
        model="gemini-pro",
        google_api_key="AIzaSyAiIh4uO1L9EcD-jqb4D9cn6BwggbcZwwM"
    )

    return llm

def fileProcessing(file):
    global file_content
    loader = PyPDFLoader(file)
    data = loader.load()

    question_gen = ''

    for page in data:
        question_gen += page.page_content

    file_content = question_gen

    splitter_ques_gen = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )

    chunk_ques_gen = splitter_ques_gen.split_text(question_gen)
    document_ques_gen = [Document(page_content=t) for t in chunk_ques_gen]

    splitter_ans_gen = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=30
    )

    document_answer_gen = splitter_ans_gen.split_documents(
        document_ques_gen
    )

    return document_ques_gen, document_answer_gen

def llm_pipeline(file):
    document_ques_gen, document_ans_gen = fileProcessing(file)

    llm_ques_gen_pipeline = loadLLM()

    prompt_template = """
        You are an expert at creating questions based on technical documents and materials.
        Your goal is to prepare an engineering student for their examinations.
        You do this by asking questions about the text below:

        ------------
        {text}
        ------------

        Generate questions based on the specifications of bloom's taxonomy level 3 (apply) on this text.
        Make sure you generate only level 3 (apply) questions and not anything else.
        Make sure not to lose any important information.

        QUESTIONS:
    """

    PROMPT_QUESTIONS = PromptTemplate(template=prompt_template, input_variables=["text"])

    ques_gen_chain = load_summarize_chain(
        llm=llm_ques_gen_pipeline,
        chain_type="stuff",
        verbose=True,
        prompt=PROMPT_QUESTIONS
    )

    ques = ques_gen_chain.run(document_ques_gen)

    quesList = ques.split("\n")

    filteredQuesList = [element for element in quesList if element.endswith('?') or element.endswith('.')]
    return filteredQuesList

def generateQuestions(file):
    quesList = llm_pipeline(file)
    return file_content, quesList
