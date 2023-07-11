import pinecone
import os
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.vectorstores import Pinecone
from langchain.llms import OpenAI
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")

openai = OpenAI(
    model_name="text-davinci-003",
    openai_api_key=OPENAI_API_KEY
)

pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENV"))
index_name = "langchain-demo"
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

def get_content_from_db(namespace, db_query, k=4):
    db = Pinecone.from_existing_index(index_name, embeddings, namespace=namespace)
    docs = db.similarity_search(db_query,k=k)
    docs_page_content = " ".join([d.page_content for d in docs])
    # print(docs_page_content)
    return docs_page_content