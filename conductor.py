import ast
import json
import re

from pyparsing import Optional
from common_util.memory import set_entity_memory_long_cache, warm_cache, get_entities
from queryDB import get_conductor_key, tools, set_seed_query, get_latest_ai_research
from langchain_experimental.plan_and_execute import (
    PlanAndExecute,
    load_agent_executor,
    load_chat_planner,
)
import langchain
from langchain.chains import LLMChain
from datetime import datetime
from common_util.get_content_from_db import get_research_source_doc
from common_util.customPrompts import (
    DOC_FORMAT_PROMPT,
    DOC_ORDER_PROMT,
    FEEDBACK_PARSER_PROMT,
    TECH_EDITOR_PROMT,
    SOLUTION_REVIEW_PROMT,
    SOLUTION_DESIGN_SKELETON_PROMPT,
    SOLUTION_REQUIREMENTS_PROMPT,
    BRAINSTORMER_PROMPT,
    OUTPUT_PARSER_PROMPT,
    IDEA_ENRICH_COMBINE_PROMPT,
    IDEA_SELECTOR_PROMPT,
    ALEX_PERSONA_PROMPT,
)
from common_util.llms import (
    LLM_BRAINSTORM,
    LLM_FACT_4,
    LLM_FACT,
    EMBEDDINGS,
    LLM_FACT_DAV,
    LLM_CHAT_4,
)
from common_util.searchWeb import (
    run_search_conflict_agent,
    run_judge_idea_agent,
    SEARCH_TOOL,
)
from queryDB import (
    ENTITY_TOOL,
    AI_ENGINEERING_TOOL,
    VIDEO_STREAMING_RESEARCH_TOOL,
    AI_RESEARCH_TOOL,
    add_to_research_file,
    set_conductor_key,
    get_reserach_from_file,
)
from langchain.agents import initialize_agent, AgentType
from baby_agi_pm.baby_agi import BabyAGI
from baby_agi_pm.task_execution import TaskExecutionAgent
from langchain import LLMChain
from langchain.vectorstores import FAISS
from langchain.docstore import InMemoryDocstore
from langchain.agents import Tool

import faiss

langchain.debug = True


# %%
def load_global_vars(hist_obj):
    global doc_format_obj, tech_edit, ordered_doc_sections, feedback_reference, solution_feedback, baby_results, choice_number, ideas_obj, enrich, idea_of_choice, requirements, solution_skeleton
    choice_number = hist_obj["idea_choice"]
    ideas_obj = hist_obj["ideas_obj"]
    enrich = ideas_obj[choice_number]["enrichment"]
    idea_of_choice = ideas_obj[choice_number]["idea"]
    requirements = ideas_obj[choice_number]["requirements"]
    solution_skeleton = ideas_obj[choice_number]["solution_skeleton"]
    baby_results = hist_obj["baby_results"]
    solution_feedback = ideas_obj[choice_number]["solution_feedback"]
    feedback_reference = ideas_obj[choice_number]["feedback_reference"]
    ordered_doc_sections = ideas_obj[choice_number]["ordered_doc_sections"]
    tech_edit = ideas_obj[choice_number]["tech_edit"]
    doc_format_obj = ideas_obj[choice_number]["doc_format_obj"]

def get_historical_variable(key):
    global CONDUCTOR_KEY
    CONDUCTOR_KEY = key
    set_conductor_key(key)
    set_seed_query("AI, analytics, video streaming crossover")
    set_entity_memory_long_cache([])
    return get_reserach_from_file(key=key)


# %%


CONDUCTOR_KEY = datetime.now().strftime("%Y%m%d%H%M%S")
set_conductor_key(CONDUCTOR_KEY)
set_seed_query("AI, analytics, video streaming crossover")
set_entity_memory_long_cache([])


# new research
latest_research = get_latest_ai_research()
entities = get_entities()
add_to_research_file(
    property="latest_research", value=latest_research, key=CONDUCTOR_KEY
)
# %%
llm_chain = LLMChain(prompt=BRAINSTORMER_PROMPT, llm=LLM_BRAINSTORM)
ideas = llm_chain.run(
    {
        "concepts": latest_research,
        "domain": "OTT video streaming analytics",
        "output": "",
        "instruct": "",
    }
)
add_to_research_file(property="seed_ideas", value=ideas, key=CONDUCTOR_KEY)
# %%
# overkill refining these doesnt help much
# refined = llm_chain.run({'concepts':entities, 'domain':"OTT video streaming analytics",'output':ideas,'instruct':"USER: ***ENHANCE ENRICH REFINE***"})
# add_to_research_file(property="refined_seed_ideas", value=refined, key=CONDUCTOR_KEY)
# %%
parse_chain = LLMChain(prompt=OUTPUT_PARSER_PROMPT, llm=LLM_FACT_4)
ideas_parsed = parse_chain.run(
    {
        "copy": ideas,
        "parse": """
                                Copy contains ideas. Extract FINAL ideas into an array.
                                Extract each idea in full detail. An Idea may span multiple lines and contain formatting.
                                Expected ourput format: ["idea1_title: idea1_description", "idea2_title: idea2_description", "idea3_title: idea3_description"]
                                """,
    }
)
add_to_research_file(
    property="parsed_seed_ideas", value=ideas_parsed, key=CONDUCTOR_KEY
)

# %%
# %%
parsed_ideas_list = ast.literal_eval(ideas_parsed)

ideas_obj = {}
i = 1
for idea in parsed_ideas_list:
    # enrich with ai research prompt
    score = run_judge_idea_agent(idea)
    print(idea)
    ideas_obj[i] = {"idea": idea, "score": score}
    i = i + 1

# %%
idea_select_chain = LLMChain(prompt=IDEA_SELECTOR_PROMPT, llm=LLM_FACT_4)
selected_response = idea_select_chain.run({"ideas": ideas_obj})
ideas_obj["selection"] = selected_response
add_to_research_file(property="ideas_obj", value=ideas_obj, key=CONDUCTOR_KEY)

# %%
# Extract the choice number using regex
choice_match = re.search(r"Choice: (\d+)", selected_response)
choice_number = (choice_match.group(1)) if choice_match else None

# %%

# %%
add_to_research_file(property="idea_choice", value=choice_number, key=CONDUCTOR_KEY)
idea_of_choice = ideas_obj[choice_number]["idea"]
# %%
# %%

agent_executor = initialize_agent(
    tools,
    LLM_FACT_4,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    max_iterations=5,
)

agent_query = f"""
System {{
You are the Idea Enricher. You take an Idea and Enrich it with researched information.
You focus on the How and Why an Idea will work *end to end*. Your final response informs execution of the Idea.
}}  

Idea {{
{idea_of_choice}
}}

Task{{
Enrich
}}
"""

enrich = agent_executor.run(agent_query)
# %%

ideas_obj[choice_number]["enrichment"] = enrich
add_to_research_file(property="ideas_obj", value=ideas_obj, key=CONDUCTOR_KEY)

# %%
# %%
requirements_chain = LLMChain(prompt=SOLUTION_REQUIREMENTS_PROMPT, llm=LLM_BRAINSTORM)
requirements = requirements_chain.run({"idea": idea_of_choice, "enrich": enrich})
ideas_obj[choice_number]["requirements"] = requirements
add_to_research_file(property="ideas_obj", value=ideas_obj, key=CONDUCTOR_KEY)

# %%
solution_skeleton_chain = LLMChain(
    prompt=SOLUTION_DESIGN_SKELETON_PROMPT, llm=LLM_BRAINSTORM
)
solution_skeleton = solution_skeleton_chain.run(
    {"idea": idea_of_choice, "enrich": enrich, "requirements": requirements}
)

# %%
ideas_obj[choice_number]["solution_skeleton"] = solution_skeleton
add_to_research_file(property="ideas_obj", value=ideas_obj, key=CONDUCTOR_KEY)

# %%


def get_solution_skeleton(input):
    return solution_skeleton


SOLUTION_SKELETON_TOOL = Tool.from_function(
    name="Solution Skeleton",
    func=get_solution_skeleton,
    description="useful for when you need the solution skeleton.",
)

embedding_size = 1536
index = faiss.IndexFlatL2(embedding_size)
vectorstore = FAISS(EMBEDDINGS.embed_query, index, InMemoryDocstore({}), {})

baby_tools = [
    AI_ENGINEERING_TOOL,
    VIDEO_STREAMING_RESEARCH_TOOL,
    AI_RESEARCH_TOOL,
    SOLUTION_SKELETON_TOOL,
    ENTITY_TOOL,
]

baby_agent_executor = TaskExecutionAgent.from_agent_and_tools(
    llm=LLM_FACT_4, tools=baby_tools, verbose=True, max_iterations=5
)

# Run the BabyAGI

OBJECTIVE = f"Solution architect: {idea_of_choice}"

# If None, will keep on going forever
max_iterations = 15
baby_agi = BabyAGI.from_llm(
    llm=LLM_FACT_4,
    vectorstore=vectorstore,
    task_execution_chain=baby_agent_executor,
    verbose=True,
    max_iterations=max_iterations,
)

baby_agi({"objective": OBJECTIVE})

# %%

# Factchecking does not work well as it is Novel
# solution_arr=[]
# for res in baby_results:
#     result = res["result"]
#     task = res["task"]

#     factcheck=run_search_conflict_agent(result, task)
#     res["factcheck"]=factcheck
#     solution_arr.append(res)

# add_to_research_file(property="solution_arr", value=solution_arr, key=CONDUCTOR_KEY)

# %%
solution_critic_chain = LLMChain(prompt=SOLUTION_REVIEW_PROMT, llm=LLM_BRAINSTORM)
solution_feedback = solution_critic_chain.run(
    {
        "idea": idea_of_choice,
        "enrich": enrich,
        "requirements": requirements,
        "solution": baby_results,
    }
)

# %%
ideas_obj[choice_number]["solution_feedback"] = solution_feedback
add_to_research_file(property="ideas_obj", value=ideas_obj, key=CONDUCTOR_KEY)


# %%
feedback_parser_chain = LLMChain(prompt=FEEDBACK_PARSER_PROMT, llm=LLM_FACT_4)
feedback_queries = feedback_parser_chain.run(
    {"idea": idea_of_choice, "solution_feedback": solution_feedback}
)

# %%
feedback_queries_list = ast.literal_eval(feedback_queries)
ideas_obj[choice_number]["feedback_queries"] = feedback_queries_list
add_to_research_file(property="ideas_obj", value=ideas_obj, key=CONDUCTOR_KEY)

# %%
agent_query_tools = tools
agent_query_tools.append(SEARCH_TOOL)


agent_executor = initialize_agent(
    tools,
    LLM_FACT_4,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    max_iterations=5,
)
feedback_reference = []
for query in feedback_queries_list:
    agent_query = f"""
    System {{
    You are an AI assistant that answeres a single Query. You utilise tools to pull factual relevant information.
    Final Answer: the final answer to the original input question is the full detailed explanation from the Observation provided as bullet points.
    }}  

    Tool Prioritisation {{
    search_database_for_term_definition > get_new_learnings > web_search
    }}

    Query{{
    {query}
    }}

    Answer:
    """

    ref = agent_executor.run(agent_query)
    feedback_reference.append(ref)
# %%
ideas_obj[choice_number]["feedback_reference"] = feedback_reference
add_to_research_file(property="ideas_obj", value=ideas_obj, key=CONDUCTOR_KEY)
# %%

i = 0
document_sections = []
for baby in baby_results:
    if i > 0:
        document_sections.append({"ID": i, "Section": baby["task"]})
    i = i + 1
document_sections
# %%
doc_order_chain = LLMChain(prompt=DOC_ORDER_PROMT, llm=LLM_FACT_4)
doc_order = doc_order_chain.run(
    {"solution_skeleton": solution_skeleton, "document_sections": document_sections}
)
doc_order_list = ast.literal_eval(doc_order)
# %%
ordered_doc_sections = []
for n in doc_order_list:
    ordered_doc_sections.append(
        {"purpose": baby_results[n]["task"], "content": baby_results[n]["result"]}
    )
ordered_doc_sections
ideas_obj[choice_number]["ordered_doc_sections"] = ordered_doc_sections
add_to_research_file(property="ideas_obj", value=ideas_obj, key=CONDUCTOR_KEY)
# %%
tech_editor_chain = LLMChain(prompt=TECH_EDITOR_PROMT, llm=LLM_FACT_4)
# split into 3 secions chunks
doc_sec_split = []
for i in range(0, len(ordered_doc_sections), 3):
    doc_sec_split.append(ordered_doc_sections[i : i + 3])
outline = []
for n in ordered_doc_sections:
    outline.append(n["purpose"])

tech_edit = []
previous_section = ""
for chunk in doc_sec_split:
    sections_edit = tech_editor_chain.run(
        {
            "idea": idea_of_choice,
            "outline": outline,
            "feedback_reference": feedback_reference,
            "previous_section": previous_section,
            "edit_sections": chunk,
        }
    )
    previous_section = sections_edit
    tech_edit.append(sections_edit)

ideas_obj[choice_number]["tech_edit"] = tech_edit
add_to_research_file(property="ideas_obj", value=ideas_obj, key=CONDUCTOR_KEY)

# %%
## LOADS completed vars for step
CONDUCTOR_KEY = "20230814160057"
hist_var = get_reserach_from_file(CONDUCTOR_KEY)
load_global_vars(hist_var)

# %%
joined_tech_edit = '\n'.join(tech_edit)
doc_format_chain = LLMChain(prompt=DOC_FORMAT_PROMPT, llm=LLM_FACT_4)
doc_format = doc_format_chain.run(
    {"idea": idea_of_choice, "doc_source": joined_tech_edit}
)

# %%
doc_format_obj = json.loads(doc_format)
ideas_obj[choice_number]["doc_format_obj"] = doc_format_obj
add_to_research_file(property="ideas_obj", value=ideas_obj, key=CONDUCTOR_KEY)

# %%
alex_content_chain = LLMChain(prompt=ALEX_PERSONA_PROMPT, llm=LLM_CHAT_4)
previous_section = ""
alex_doc_content = [doc_format_obj['title']]
for current_section in doc_format_obj['content']:
    alex_content_section = alex_content_chain.run(
        {"idea": idea_of_choice, "feedback_reference": feedback_reference,
        "doc_format_obj": doc_format_obj,
        "doc_source": tech_edit,
        "previous_section": previous_section,
        "current_section": current_section,}
    )
    previous_section = alex_content_section
    alex_doc_content.append(alex_content_section)


# %%
ideas_obj[choice_number]["alex_doc_content"] = alex_doc_content
add_to_research_file(property="ideas_obj", value=ideas_obj, key=CONDUCTOR_KEY)

# %%
idea_of_choice