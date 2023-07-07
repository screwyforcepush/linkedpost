from queryDB import tools, set_seed_query, set_entity_memory_long_cache, get_seed_query
from langchain.experimental.plan_and_execute import PlanAndExecute, load_agent_executor, load_chat_planner
from langchain.agents import AgentType, initialize_agent
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI

import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")

openai = OpenAI(
    model_name="text-davinci-003",
    openai_api_key=OPENAI_API_KEY
)

LLM_FACT = ChatOpenAI(
    model_name='gpt-3.5-turbo',
    temperature=0.0
)

LLM_PLAN = ChatOpenAI(
    model_name='gpt-4',
    temperature=0.1
)

LLM_CHAT = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.2)

# %%
set_seed_query("What is a unique AI prompting strategy? How can it be applied to video streaming analytics?")
PLANNER_INSTRUCTION="Create a short tutorial including an implementation example."
PLANNER_QUERY=f"""{get_seed_query()}
{PLANNER_INSTRUCTION}
"""
set_entity_memory_long_cache([])
agent_executor = initialize_agent(tools, LLM_CHAT, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True, max_iterations=5)
# agent_executor.run(get_seed_query())
# %%

planner = load_chat_planner(LLM_PLAN)
executor = load_agent_executor(LLM_PLAN, tools, verbose=True)
agent = PlanAndExecute(planner=planner, executor=executor, verbose=True)
agent.run(PLANNER_QUERY)
# %%
