from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

def load_rag_chain(pdf_path: str, model: str = "gpt-4o-mini"):
    # 1. PDF 로딩
    loader = PyPDFLoader("data/Samsung_Card_Manual_Korean_1.3.pdf")
    pages = loader.load()  # List[Document] 형태로 반환 

    # 2. 텍스트 분할
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    docs = splitter.split_documents(pages)
    # 3. 임베딩 + 벡터 DB
    embeddings = OpenAIEmbeddings()
    vectordb = FAISS.from_documents(docs, embeddings)
    vectordb.save_local("faiss_index")
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})
    # 4. 프롬프트
    msg = """
너는 삼성전자 메모리카드 매뉴얼에 대한 전문 어시스턴트이다.
다음의 참고 문서를 바탕으로 질문에 정확하게 답하라.

[참고문서]
{context}

[질문]
{question}

한글로 간결하고 정확하게 답변하라."""
    # 5. RAG 체인
    prompt = ChatPromptTemplate.from_template(msg)
    llm=ChatOpenAI(model="gpt-4o-mini")
    rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
   )
    return rag_chain
