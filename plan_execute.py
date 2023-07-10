from queryDB import tools, set_seed_query, set_entity_memory_long_cache, get_seed_query, warm_cache
from langchain.experimental.plan_and_execute import PlanAndExecute, load_agent_executor, load_chat_planner
from langchain.agents import AgentType, initialize_agent
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
import langchain
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
LLM_FUNCTION = ChatOpenAI(
    model_name='gpt-4-0613',
    temperature=0.1
)

LLM_CHAT = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.2)

# %%

set_seed_query("How does Chain of thought prompting work? How can it be applied to video streaming analytics?")
set_entity_memory_long_cache([])
entities = warm_cache(get_seed_query())

PLANNER_INSTRUCTION=f"Create a short tutorial including an implementation example."
PLANNER_QUERY=f"""{get_seed_query()}
{PLANNER_INSTRUCTION}
"""

PLANNER_SYSTEM_PROMPT = (
    "Let's first understand the problem and devise a plan to solve the problem."
    "While forming a plan, consider the following entity context: {entities}"
    "Please output the plan starting with the header 'Plan:' "
    "and then followed by a numbered list of steps. "
    "Please make the plan the minimum number of steps required "
    "to accurately complete the task. If the task is a question, "
    "the final step should almost always be 'Given the above steps taken, "
    "please respond to the users original question'. "
    "At the end of your plan, say '<END_OF_PLAN>'"
)
# %%
langchain.debug = True

planner = load_chat_planner(LLM_PLAN, system_prompt=PLANNER_SYSTEM_PROMPT)
executor = load_agent_executor(LLM_PLAN, tools, verbose=True)
openexecutor = initialize_agent(tools, LLM_FUNCTION, agent=AgentType.OPENAI_MULTI_FUNCTIONS, verbose=True)
agent_executor = initialize_agent(tools, LLM_PLAN, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True, max_iterations=5)
agent = PlanAndExecute(planner=planner, executor=executor, verbose=True)
# agent.run(PLANNER_QUERY)
# %%
executor.run(
    "Explain some video streaming metrics."
)
# %%
