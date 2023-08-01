from langchain.retrievers.web_research import WebResearchRetriever

import pinecone
import os
from langchain.vectorstores import Pinecone
from langchain.utilities import GoogleSearchAPIWrapper
from common_util.llms import LLM_FACT, EMBEDDINGS
from dotenv import load_dotenv
from common_util.namespaceEnum import PineconeNamespaceEnum

load_dotenv()
index_name = "langchain-demo"

pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENV"))

# Vectorstore
vectorstore = Pinecone.from_existing_index(index_name, EMBEDDINGS, namespace=PineconeNamespaceEnum.WEB_SEARCH.value)


# LLM
llm = LLM_FACT

# Search 
os.environ["GOOGLE_CSE_ID"] = os.getenv("GOOGLE_CSE_ID")
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
search = GoogleSearchAPIWrapper()

web_research_retriever = WebResearchRetriever.from_llm(
    vectorstore=vectorstore,
    llm=llm, 
    search=search, 
)

from langchain.chains import RetrievalQAWithSourcesChain
user_input = "How do LLM Powered Autonomous Agents work?"
qa_chain = RetrievalQAWithSourcesChain.from_chain_type(llm,retriever=web_research_retriever)
result = qa_chain({"question": user_input})
result
#%%

#%%