import ast
import re
from common_util.memory import set_entity_memory_long_cache, warm_cache, get_entities
from queryDB import tools, set_seed_query, get_latest_ai_research
from langchain_experimental.plan_and_execute import PlanAndExecute, load_agent_executor, load_chat_planner
import langchain
from langchain.chains import LLMChain
from datetime import datetime
from common_util.customPrompts import BRAINSTORMER_PROMPT, OUTPUT_PARSER_PROMPT, IDEA_ENRICH_COMBINE_PROMPT, IDEA_SELECTOR_PROMPT
from common_util.llms import LLM_BRAINSTORM, LLM_FACT_4, LLM_FACT
from common_util.searchWeb import WEB_SEARCH_QA_CHAIN, run_judge_idea_agent
from queryDB import add_to_research_file, set_conductor_key, get_reserach_from_file
from langchain.agents import initialize_agent, AgentType

langchain.debug = True
#%%
CONDUCTOR_KEY = datetime.now().strftime("%Y%m%d%H%M%S")
set_conductor_key(CONDUCTOR_KEY)
set_seed_query("AI, analytics, video streaming crossover")
set_entity_memory_long_cache([])

def get_historical_variable(key):
    global CONDUCTOR_KEY
    CONDUCTOR_KEY = key
    set_conductor_key(key)
    set_seed_query("AI, analytics, video streaming crossover")
    set_entity_memory_long_cache([])
    return get_reserach_from_file(key=key)

#%%
#new research
latest_research = get_latest_ai_research()
entities = get_entities()
add_to_research_file(property="latest_research", value=latest_research, key=CONDUCTOR_KEY)
#%%
llm_chain = LLMChain(prompt=BRAINSTORMER_PROMPT, llm=LLM_BRAINSTORM)
ideas = llm_chain.run({'concepts':latest_research, 'domain':"OTT video streaming analytics",'output':"",'instruct':""})
add_to_research_file(property="seed_ideas", value=ideas, key=CONDUCTOR_KEY)
#%%
#overkill refining these doesnt help much
# refined = llm_chain.run({'concepts':entities, 'domain':"OTT video streaming analytics",'output':ideas,'instruct':"USER: ***ENHANCE ENRICH REFINE***"})
# add_to_research_file(property="refined_seed_ideas", value=refined, key=CONDUCTOR_KEY)
#%%
parse_chain = LLMChain(prompt=OUTPUT_PARSER_PROMPT, llm=LLM_FACT_4)
ideas_parsed = parse_chain.run({'copy':ideas,
                                'parse':"""
                                Copy contains ideas. Extract FINAL ideas into an array.
                                Extract each idea in full detail. An Idea may span multiple lines and contain formatting.
                                Expected ourput format: ["idea1_title: idea1_description", "idea2_title: idea2_description", "idea3_title: idea3_description"]
                                """})
add_to_research_file(property="parsed_seed_ideas", value=ideas_parsed, key=CONDUCTOR_KEY)

#%%
#%%
parsed_ideas_list = ast.literal_eval(ideas_parsed)

ideas_obj={}
i=1
for idea in parsed_ideas_list:
    #enrich with ai research prompt
    score=run_judge_idea_agent(idea)
    print(idea)
    ideas_obj[i]={"idea":idea,
                  "score":score}
    i = i+1

#%%
idea_select_chain = LLMChain(prompt=IDEA_SELECTOR_PROMPT, llm=LLM_FACT_4)
selected_response = idea_select_chain.run({'ideas':ideas_obj})
ideas_obj["selection"]=selected_response
add_to_research_file(property="ideas_obj", value=ideas_obj, key=CONDUCTOR_KEY)

#%%
# Extract the choice number using regex
choice_match = re.search(r"Choice: (\d+)", selected_response)
choice_number = (choice_match.group(1)) if choice_match else None

#%%

#%%
add_to_research_file(property="idea_choice", value=choice_number, key=CONDUCTOR_KEY)
idea_of_choice=ideas_obj[choice_number]['idea']
#%%
# %%
hist_vars =get_historical_variable("20230814160057")

ideas_obj=hist_vars["ideas_obj"]
idea_of_choice=ideas_obj[hist_vars["idea_choice"]]['idea']

agent_executor = initialize_agent(tools, LLM_FACT_4, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True, max_iterations=5)

agent_query=f"""
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
enrich=agent_executor.run(agent_query)
# %%
ideas_obj[hist_vars["idea_choice"]]['enrichment']=enrich
add_to_research_file(property="ideas_obj", value=ideas_obj, key=CONDUCTOR_KEY)


# %%
