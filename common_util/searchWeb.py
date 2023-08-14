from aiohttp import ClientResponseError
from langchain.retrievers.web_research import WebResearchRetriever

import pinecone
import os
from langchain.vectorstores import Pinecone
from langchain.utilities import GoogleSearchAPIWrapper
from common_util.llms import LLM_FACT, EMBEDDINGS, LLM_FACT_4
from dotenv import load_dotenv
from common_util.namespaceEnum import PineconeNamespaceEnum
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.agents import initialize_agent, AgentType
import nest_asyncio
nest_asyncio.apply()

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

WEB_SEARCH_QA_CHAIN = RetrievalQAWithSourcesChain.from_chain_type(llm,retriever=web_research_retriever)

# usage
# user_input = "List the latest generative AI research developments."
# result = WEB_SEARCH_QA_CHAIN({"question": user_input})
# result
#%%
from langchain.tools import StructuredTool
def search_func(term:str):
    """Search the web
    Args:
        term: search term used in the search engine
    """
    try:
        return WEB_SEARCH_QA_CHAIN(term)
    except ClientResponseError:
        return "Bad response from search. Try different search term"
web_tools = [
    StructuredTool.from_function(
        name='Web search',
        func=search_func,
        description=(
            'useful to search for existing published materials'
        )
    )
]

web_agent_executor = initialize_agent(web_tools, LLM_FACT_4, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True, max_iterations=5)
# %%
def run_judge_idea_agent(idea:str):

    web_agent_query=f"""
    System {{
    You are the Idea Judge. You critically assess and Score Ideas on a scale of 1-10.
    You Search for *existing published materials* that will inform idea assessment.
    Brutally and critically Score every Criteria with brief unambiguous explanation.
    }}

    Score criteria {{
    Relevance: Ensure the idea addresses market gap.
    Innovativeness: Seek novelty or unique approaches.
    Feasibility: Evaluate practicality and possible constraints.
    Scalability: Assess adaptability and growth potential.
    Customer Perspective: Gauge delightful experience.
    Technical Perspective: Assess development challenges and infrastructure needs.
    Business Perspective: Calculate potential ROI and costs.
    }}

    Idea {{
    {idea}
    }}

    Task{{
    Search > Judge
    }}
    """
    return web_agent_executor.run(web_agent_query)
#%%