from common_util.memory import set_entity_memory_long_cache, warm_cache, get_entities
from queryDB import tools, set_seed_query, get_seed_query, get_latest_ai_research
from langchain_experimental.plan_and_execute import PlanAndExecute, load_agent_executor, load_chat_planner
import langchain
from common_util.llms import LLM_CHAT, LLM_FACT, LLM_PLAN

# %%
langchain.debug = True

set_seed_query("Find an interesting and unique connection between different Generative AI research findings and techniques. Include all information that would aid in the application of the connected techniques to Video Streaming Analytics.")
set_entity_memory_long_cache([])
latest_research = get_latest_ai_research()
entities = get_entities()

PLANNER_INSTRUCTION=f"""# Latest AI Research Rummary to be used as a thought starter
{latest_research}
"""
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


# %%

executor = load_agent_executor(LLM_PLAN, tools, verbose=True)
planner = load_chat_planner(LLM_PLAN, system_prompt=PLANNER_SYSTEM_PROMPT)
agent = PlanAndExecute(planner=planner, executor=executor, verbose=True)
# 
# %%
agent.run(PLANNER_QUERY)


##cant be used as executor
# prompt_msgs = [
#         SystemMessage(
#             content=f"You are a helpful AI assistant. You can use tools to obtain information about the namespaces: {get_all_namespaces()}"
#         ),
#         HumanMessage(content="Call the relevant function to get information the following input:"),
#     HumanMessagePromptTemplate.from_template("{input}"),
#     HumanMessage(content="Tips: Make sure to answer in the correct format"),
#     ]
# prompt = ChatPromptTemplate(messages=prompt_msgs)

# funk_chain = create_openai_fn_chain(open_funk, LLM_FUNCTION, prompt, verbose=True)
# # funk_chain.run("Explain some video streaming metrics.")
# from langchain.tools import BaseTool, Tool, tool

# chain_tools = [
#         Tool.from_function(
#         func=funk_chain.run,
#         name="Assistant",
#         description="useful for when you need additional research information"
#    )
# ]
# # %%

# %%
