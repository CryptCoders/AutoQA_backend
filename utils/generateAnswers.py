from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.vectorstores.faiss import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
import google.generativeai as genai


def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks


def get_vector_store(text_chunks, api_key):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")


def get_conversation_chain(api_key):
    prompt_template = """
        You are an expert at creating answers based on technical documents and questions.
        Your goal is to prepare an engineering student for their examinations.
        You need to answer the question based on the context below:

        ------------
        QUESTION: {question}\n
        CONTEXT: {context}
        ------------

        Answer the question as detailed as possible.
        If the answer is not in provided context, generate an answer by yourself starting with GEMINI_GENERATED.
        If you cannot still answer a question, say "I am unable to answer this question", do not give wrong answers.
        Make sure to provide all the details.

        ANSWER:
    """

    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=1, google_api_key=api_key)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain

def get_conversation_chain1(api_key):
    prompt_template = """
        You are an expert at identifying keywords based on technical documents and questions.
        Your goal is to prepare an engineering student for their examinations.
        You need to give the most important core keywords from the provided answer for the question based on the context below:

        ------------
        CONTEXT: {context}\n
        QUESTION: {question}\n
        ANSWER: {answer}\n
        ------------


        Give the list of most important core keywords from the answer above.
        If there are no important keywords, just say "No important keywords".

        KEYWORDS:
    """

    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=1, google_api_key=api_key)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question", "answer"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain

def user_input(user_question, api_key):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)

    docs = new_db.similarity_search(user_question)
    chain = get_conversation_chain(api_key)

    response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)

    docs = new_db.similarity_search(user_question)
    chain = get_conversation_chain1(api_key)

    keywords_response = chain({"input_documents": docs, "question": user_question, "answer": response["output_text"]}, return_only_outputs=True)
    return response['output_text'], keywords_response['output_text']

def generateAnswer(context, question, api_key):
    genai.configure(api_key=api_key)

    chunks = get_text_chunks(context)
    get_vector_store(chunks, api_key)

    return user_input(question, api_key)