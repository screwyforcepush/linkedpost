import ast
import json
import re

from pyparsing import Optional
from common_util.memory import set_entity_memory_long_cache, warm_cache, get_entities
from common_util.researchAssistant import get_latest_ai_research
from queryDB import get_conductor_key, tools, set_seed_query
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
    EXTRACT_IDEA_CONCEPTS_PROMPT,
    EXTRACT_SOURCE_CONTENT_PROMPT,
    LINKEDIN_POST_PROMPT,
    ARTICLE_STRUCTURE_PROMPT,
    ALEX_PRO_PERSONA_PROMPT,
    ALEX_PRO_PERSONA_INTRO_CONCLUSION_PROMPT,
    ARTICLE_CRITIQUE_PROMPT,
    ALEX_PRO_EDIT_PROMPT,
    ALEX_PRO_EDIT_INTRO_CONCLUSION_PROMPT,
    LINKEDIN_POST_PRO_PROMPT,
)
from common_util.llms import (
    LLM_BRAINSTORM,
    LLM_FACT_4,
    LLM_FACT,
    EMBEDDINGS,
    LLM_FACT_DAV,
    LLM_CHAT_4,
    LLM_4_01,
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
    global article_critique_obj, full_article, article_obj,article_structure, alex_doc_content, latest_research, doc_format_obj, tech_edit, ordered_doc_sections, feedback_reference, solution_feedback, baby_results, choice_number, ideas_obj, enrich, idea_of_choice, requirements, solution_skeleton
    try:
        choice_number = hist_obj["idea_choice"]
        ideas_obj = hist_obj["ideas_obj"]
        latest_research = hist_obj["latest_research"]
        idea_of_choice = json.dumps(ideas_obj[choice_number]["idea"])
        enrich = ideas_obj[choice_number]["enrichment"]
        article_structure = ideas_obj[choice_number]["article_structure"]
        article_obj = hist_obj["article_obj"]
        full_article = hist_obj["full_article"]
        article_critique_obj = hist_obj["feedback"]
        requirements = ideas_obj[choice_number]["requirements"]
        solution_skeleton = ideas_obj[choice_number]["solution_skeleton"]
        baby_results = hist_obj["baby_results"]
        solution_feedback = ideas_obj[choice_number]["solution_feedback"]
        feedback_reference = ideas_obj[choice_number]["feedback_reference"]
        ordered_doc_sections = ideas_obj[choice_number]["ordered_doc_sections"]
        tech_edit = ideas_obj[choice_number]["tech_edit"]
        doc_format_obj = ideas_obj[choice_number]["doc_format_obj"]
        alex_doc_content = ideas_obj[choice_number]["alex_doc_content"]
    except KeyError as e:
        print("stopped at", e)

def get_historical_variable(key):
    global CONDUCTOR_KEY
    CONDUCTOR_KEY = key
    set_conductor_key(key)
    set_seed_query("AI, analytics, video streaming crossover")
    set_entity_memory_long_cache([])
    return get_reserach_from_file(key=key)

DOMAINS = ["OTT video streaming", "Ecommerce", "FinTech", "HealthTech", "eLearning", "property tech", "stockmarket trading tech"]
domain= "OTT video streaming analytics"
# /TODO add exclusions from past ideas
domain={"industry":"OTT video streaming",
        "domains":["streaming platform", "ad products for AVOD clients", "marketing", "content creation/pocurement"],
        "exclude": "personalised content discovery"}
# %%
###

#### UP HERE !!!!!!!

###

# %%
## LOADS completed vars for step
CONDUCTOR_KEY = "20230921134237"
hist_var = get_reserach_from_file(CONDUCTOR_KEY)
load_global_vars(hist_var)

# %%

CONDUCTOR_KEY = datetime.now().strftime("%Y%m%d%H%M%S")
set_conductor_key(CONDUCTOR_KEY)
set_seed_query("AI, analytics, video streaming crossover")
set_entity_memory_long_cache([])


# new research
#TODO need to include authors and published date
latest_research = get_latest_ai_research(tokens=6000)
# entities = get_entities()
add_to_research_file(
    property="latest_research", value=latest_research, key=CONDUCTOR_KEY
)
# %%
llm_chain = LLMChain(prompt=BRAINSTORMER_PROMPT, llm=LLM_BRAINSTORM)
ideas = llm_chain.run(
    {
        "concepts": latest_research,
        "domain": domain,
    }
)
add_to_research_file(property="seed_ideas", value=ideas, key=CONDUCTOR_KEY)

# %%
parse_chain = LLMChain(prompt=OUTPUT_PARSER_PROMPT, llm=LLM_FACT)
ideas_parsed = parse_chain.run(
    {
        "copy": ideas,
        "parse": """
            Copy contains ideas. Extract ideas into an array of objects.
            Extract Title, Concept Keys and ideas in full detail including working mechanics and business benefits.
            Title extraction excludes "Idea #" 
            An Idea may span multiple lines and contain formatting.

            # Example input: {{
                "# Idea 1: Customized Language Learning Assistant

                **Concept Keys:** 'FLM-101B: An Open LLM and How to Train It with $100K Budget', 'The Rise and Potential of Large Language Model Based Agents: A Survey'

                **Working Mechanics:** Leveraging the power of LLMs such as FLM-101B, we can create a language learning assistant integrated into our OTT streaming platform.

                **Business Benefits:** This idea can attract a larger global audience to our OTT platform by eliminating language barriers. It also provides an added benefit of language learning to users, making our platform more appealing and competitive in the market.

                # Idea 2 - Personalized Ad Creation Using LLMs

                **Concept Keys:** 'RAIN: Your Language Models Can Align Themselves without Finetuning'

                **Working Mechanics:** Using the RAIN inference method, the model can adjust its outputs to align with the preferences of the audience. It also prevents hallucination, ensuring the generated content is based on factual information.

                **Business Benefits:** This idea can enable the creation of highly personalized and effective ads that resonate with the audience, leading to higher conversions and revenues for our clients. It also helps our platform stand out as a preferred advertising platform."
                }}
            # Example output: 
            [{{"Title":"Customized Language Learning Assistant", 
            "Concept Keys": "FLM-101B: An Open LLM and How to Train It with $100K Budget", "The Rise and Potential of Large Language Model Based Agents: A Survey"],
            "Idea": "**Working Mechanics:** Leveraging the power of LLMs such as FLM-101B, we can create a language learning assistant integrated into our OTT streaming platform.

                **Business Benefits:** This idea can attract a larger global audience to our OTT platform by eliminating language barriers. It also provides an added benefit of language learning to users, making our platform more appealing and competitive in the market."}},
            {{"Title":"Personalized Ad Creation Using LLMs", 
            "Concept Keys": "RAIN: Your Language Models Can Align Themselves without Finetuning"],
            "Idea": "**Working Mechanics:** Using the RAIN inference method, the model can adjust its outputs to align with the preferences of the audience. It also prevents hallucination, ensuring the generated content is based on factual information.

                **Business Benefits:** This idea can enable the creation of highly personalized and effective ads that resonate with the audience, leading to higher conversions and revenues for our clients. It also helps our platform stand out as a preferred advertising platform."}}]           
                                """,
    }
)

# %%
parsed_ideas_list = ast.literal_eval(ideas_parsed)
# /TODO should probably create the ideas obj here instead
add_to_research_file(
    property="parsed_seed_ideas", value=parsed_ideas_list, key=CONDUCTOR_KEY
)
# %%
def judge_and_select(parsed_ideas_list):
    #judge ideas
    ideas_obj = {}
    i = 1
    for idea in parsed_ideas_list:
        # enrich with ai research prompt
        score = run_judge_idea_agent(idea)
        print(idea)
        ideas_obj[i] = {"idea": idea, "score": score}
        i = i + 1

    # %%
    # select idea
    idea_select_chain = LLMChain(prompt=IDEA_SELECTOR_PROMPT, llm=LLM_FACT_4)
    selected_response = idea_select_chain.run({"ideas": ideas_obj})
    ideas_obj["selection"] = selected_response
    add_to_research_file(property="ideas_obj", value=ideas_obj, key=CONDUCTOR_KEY)

    # %%
    # Extract the choice number using regex
    choice_match = re.search(r"Choice: (\d+)", selected_response)
    choice_number = (choice_match.group(1)) if choice_match else None
    return choice_number
    # %%

# %%
#
# !! MANUAL VS AUTO SELECT NEED TO SET VARIABLE
#
manual_select=True
choice_number="0"
if manual_select == True:
# !! SELECT IDEA NUMBER HERE MANUAL
    choice_number="2"
    ideas_obj = {}
    i = 1
    for idea in parsed_ideas_list:
        ideas_obj[i] = {"idea": idea}
        i += 1
    add_to_research_file(property="ideas_obj", value=ideas_obj, key=CONDUCTOR_KEY)
else:
    choice_number=judge_and_select(parsed_ideas_list)

# %%
choice_number="2"
add_to_research_file(property="idea_choice", value=choice_number, key=CONDUCTOR_KEY)
# %%
idea_of_choice = json.dumps(ideas_obj[choice_number]["idea"])

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
You focus on how the Idea will be technically implemented *end to end*. Your final response informs execution of the Idea.
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
#
# Will provide doc outline instead
#
# requirements_chain = LLMChain(prompt=SOLUTION_REQUIREMENTS_PROMPT, llm=LLM_BRAINSTORM)
# requirements = requirements_chain.run({"idea": idea_of_choice, "enrich": enrich})
# ideas_obj[choice_number]["requirements"] = requirements
# add_to_research_file(property="ideas_obj", value=ideas_obj, key=CONDUCTOR_KEY)

# # %%
# solution_skeleton_chain = LLMChain(
#     prompt=SOLUTION_DESIGN_SKELETON_PROMPT, llm=LLM_BRAINSTORM
# )
# solution_skeleton = solution_skeleton_chain.run(
#     {"idea": idea_of_choice, "enrich": enrich, "requirements": requirements}
# )

# # %%
# ideas_obj[choice_number]["solution_skeleton"] = solution_skeleton
# add_to_research_file(property="ideas_obj", value=ideas_obj, key=CONDUCTOR_KEY)

# # %%


# def get_solution_skeleton(input):
#     return solution_skeleton


# SOLUTION_SKELETON_TOOL = Tool.from_function(
#     name="Solution Skeleton",
#     func=get_solution_skeleton,
#     description="useful for when you need the solution skeleton.",
# )

# %%
article_structure_chain = LLMChain(prompt=ARTICLE_STRUCTURE_PROMPT, llm=LLM_BRAINSTORM)
article_structure = article_structure_chain.run({"idea": idea_of_choice, "enrich": enrich})
ideas_obj[choice_number]["article_structure"] = article_structure
add_to_research_file(property="ideas_obj", value=ideas_obj, key=CONDUCTOR_KEY)

# %%
parse_chain = LLMChain(prompt=OUTPUT_PARSER_PROMPT, llm=LLM_FACT)
article_obj = parse_chain.run(
    {
        "copy": article_structure,
        "parse": """
            Copy contains document concept structure. Extract into object.
            Extract Title, introduction, headings H1 H2 as needed, dot-point content to be flesh out, conclusion, Textually represent UML to be vizualised.
            Study and apply the Example in Expected out Parse.

            # Example input:
                "Title: \"Revolutionizing Ad Products with AI: A New Dawn for Audience Engagement\"

  Introduction:
  - Briefly introduce the power of Artificial Intelligence (AI) in transforming advertising.

  1. Aligning Ad Content with User Preferences: The RAIN Model
  - Introduction to the RAIN model.
  - Overcoming challenges: Potential harmful or misleading outputs.

  Section 2: The Business Benefits: Why AI in Advertising?
  - Increased ad engagement and effectiveness due to personalized content.
  - Quick generation and modification of ad content: Staying ahead in a fast-paced market.
  - The competitive edge through creative, standout ads.

  Conclusion:
  - Reiterate the potential of AI in transforming ad products.
  - Final thoughts on the business benefits and the future potentials of AI in advertising.

  UML C4 Diagram Representation:
  1. System Context Diagram: The overall system where the AI techniques are being implemented (Ad products for AVOD clients).
  2. Container Diagram: The different AI techniques being used (RAIN model, combatting hallucination, Robot Parkour Learning, Algorithm of Thoughts).
  3. Component Diagram: The individual functionalities of each technique (align ad content, ensure accuracy, train models, generate ideas).
  4. Code Diagram: Detailed view of the implementation of each technique.
                "

            # Expected output: 
                {{
        "Title": "Revolutionizing Ad Products with AI: A New Dawn for Audience Engagement",
        "Introduction": "- Briefly introduce the power of Artificial Intelligence (AI) in transforming advertising.",
        "Sections": [
            {"heading": "Aligning Ad Content with User Preferences: The RAIN Model",
            "content" : "  - Introduction to the RAIN model.
      - Overcoming challenges: Potential harmful or misleading outputs."},
        {"heading": "The Business Benefits: Why AI in Advertising?",
        "content" : "  - Increased ad engagement and effectiveness due to personalized content.
  - Quick generation and modification of ad content: Staying ahead in a fast-paced market.
  - The competitive edge through creative, standout ads."}],
        "Conclusion":"  - Reiterate the potential of AI in transforming ad products.
  - Final thoughts on the business benefits and the future potentials of AI in advertising.",
        "UML":"  1. System Context Diagram: The overall system where the AI techniques are being implemented (Ad products for AVOD clients).
  2. Container Diagram: The different AI techniques being used (RAIN model, combatting hallucination, Robot Parkour Learning, Algorithm of Thoughts).
  3. Component Diagram: The individual functionalities of each technique (align ad content, ensure accuracy, train models, generate ideas).
  4. Code Diagram: Detailed view of the implementation of each technique."
    }}      
                                """,
    }
)


# %%
article_obj = ast.literal_eval(article_obj)
add_to_research_file(property="article_obj", value=article_obj, key=CONDUCTOR_KEY)

# %%

# %%
#TRY This instead of baby
#
agent_query_tools = tools
agent_query_tools.append(SEARCH_TOOL)


agent_executor = initialize_agent(
    tools,
    LLM_FACT_4,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    max_iterations=7,
)
article_sections = []
for section in article_obj["Sections"]:
    agent_query = f"""
    System {{
    You are an AI research assistant with expertise in the Article Topic. You create a Knowledge Base to be used as reference for the full article. 
    You utilise tools to pull factual relevant information.
    Final Answer: the final answer to the original input question is the full detailed explanation from the Observation provided as bullet points.
    }}  

    Tool Prioritisation: {{
        search_database_for_term_definition > get_new_learnings > web_search
    }}

    Article Topic: {idea_of_choice}

    Article Section: {section}


    Task: {{
        Create the Knowledge Base focesed on Article Section 
    }}

    Knowledge Base:
    """

    research = agent_executor.run(agent_query)
    section["research"]=research
    article_sections.append(section)


# %%
article_obj["Sections"]=article_sections
add_to_research_file(property="article_obj", value=article_obj, key=CONDUCTOR_KEY)

#%%
#%%
alex_pro_content_chain = LLMChain(prompt=ALEX_PRO_PERSONA_PROMPT, llm=LLM_BRAINSTORM)
previous_section_content = ""
article_sections = []
for current_section in article_obj["Sections"]:
    alex_content_section = alex_pro_content_chain.run(
        {"idea": idea_of_choice, 
         "domains": domain["domains"], 
         "industry": domain["industry"], 
         "previous_section_content": previous_section_content, 
         "current_section": f"""{{"heading": {current_section["heading"]},
                            "content":{current_section["content"]},
                            "research": {current_section["research"]}}}""", 
         "section_heading": current_section["heading"],
         "structure":article_structure
        }
    )
    previous_section_content = f"""{current_section['heading']}\n{alex_content_section}"""
    current_section["content_full"]=alex_content_section
    article_sections.append(current_section)

article_obj["Sections"]=article_sections
add_to_research_file(property="article_obj", value=article_obj, key=CONDUCTOR_KEY)

#%%
article_obj = hist_var["article_obj"]
article = []
for current_section in article_obj["Sections"]:
    article.append({"heading":current_section["heading"],"content":current_section["content_full"]})
article

#%%
alex_pro_intro_conclusion_chain = LLMChain(prompt=ALEX_PRO_PERSONA_INTRO_CONCLUSION_PROMPT, llm=LLM_BRAINSTORM)
alex_intro = alex_pro_intro_conclusion_chain.run(
        {"domains": domain["domains"], 
         "industry": domain["industry"], 
         "article": article,
         "intro_conclusion": "Introduction"
        }
    )

alex_conclusion = alex_pro_intro_conclusion_chain.run(
        {"domains": domain["domains"], 
         "industry": domain["industry"], 
         "article": article,
         "intro_conclusion": "Conclusion"
        }
    )
#%%

article_obj["Introduction"]=alex_intro
article_obj["Conclusion"]=alex_conclusion
add_to_research_file(property="article_obj", value=article_obj, key=CONDUCTOR_KEY)

full_article=[{"heading":"Introduction","content":alex_intro}]
for current_section in article_obj["Sections"]:
    full_article.append({"heading":current_section["heading"],"content":current_section["content_full"]})
full_article.append({"heading":"Conclusion","content":alex_conclusion})
add_to_research_file(property="full_article", value=full_article, key=CONDUCTOR_KEY)

#%%
article_critique_chain = LLMChain(prompt=ARTICLE_CRITIQUE_PROMPT, llm=LLM_BRAINSTORM)
article_critique = article_critique_chain.run({"article": full_article})
article_critique_obj = ast.literal_eval(article_critique)

#%%
add_to_research_file(property="feedback", value=article_critique_obj, key=CONDUCTOR_KEY)

#%%
agent_query_tools = tools
agent_query_tools.append(SEARCH_TOOL)


agent_executor = initialize_agent(
    tools,
    LLM_FACT_4,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    max_iterations=7,
)
article_sections = []
for section in article_obj["Sections"]:
    agent_query = f"""
    System {{
    You are an AI research assistant with expertise in the Article Topic. You supplement the research Knowledge Base to be used as reference for final article edit. 
    You utilise tools to pull factual relevant information.
    Final Answer: the final answer to the original input question is the full detailed explanation from the Observation provided as bullet points.
    }}  

    Tool Prioritisation: {{
        search_database_for_term_definition > get_new_learnings > web_search
    }}

    Article Topic: {idea_of_choice}

    Article Section: {section}

    Feedback: {article_critique_obj[section["heading"]]}


    Task: {{
        Address the feedback by providing the Supplemental Knowledge Base. If sufficient knowledge exists, respond with "N/A"
    }}

    Supplemental Knowledge Base:
    """

    research = agent_executor.run(agent_query)
    section["additional_research"]=research
    article_sections.append(section)

# %%
article_obj["Sections"]=article_sections
add_to_research_file(property="article_obj", value=article_obj, key=CONDUCTOR_KEY)
# %%
alex_pro_edit_chain = LLMChain(prompt=ALEX_PRO_EDIT_PROMPT, llm=LLM_BRAINSTORM)
article_sections = []
for i in range(len(article_obj["Sections"])):
    section = article_obj["Sections"][i]
    alex_content_section = alex_pro_edit_chain.run(
        {"domains": domain["domains"], 
         "industry": domain["industry"], 
         #Brittle as assumes inro and conclusion index
         "previous_section_content": full_article[i], 
         "current_section_content": full_article[i+1], 
         "next_section_content": full_article[i+2], 
         "knowledge": f""""[{section["research"]},\n{section["additional_research"]}]""", 
         "overall": article_critique_obj["Overall"],
         "section_feedback":article_critique_obj[section["heading"]],
         "section_heading":section["heading"]
        }
    )
    for sec in full_article:
        if sec["heading"]==section["heading"]:
            sec["content"]=alex_content_section
    section["content_full"]=alex_content_section
    article_sections.append(section)
#%%
article_obj["Sections"]=article_sections
add_to_research_file(property="article_obj", value=article_obj, key=CONDUCTOR_KEY)
add_to_research_file(property="full_article", value=full_article, key=CONDUCTOR_KEY)

#%%
# TODO introduction feedback to reference papers title, author, source
alex_pro_intro_conclusion_edit_chain = LLMChain(prompt=ALEX_PRO_EDIT_INTRO_CONCLUSION_PROMPT, llm=LLM_BRAINSTORM)
alex_intro = alex_pro_intro_conclusion_edit_chain.run(
        {"domains": domain["domains"], 
         "industry": domain["industry"], 
         "article": full_article,
         "intro_conclusion": "Introduction",
         "overall": article_critique_obj["Overall"],
         "section_feedback":article_critique_obj["Introduction"]
        }
    )

alex_conclusion = alex_pro_intro_conclusion_edit_chain.run(
        {"domains": domain["domains"], 
         "industry": domain["industry"], 
         "article": full_article,
         "intro_conclusion": "Conclusion",
         "overall": article_critique_obj["Overall"],
         "section_feedback":article_critique_obj["Conclusion"]
        }
    )

article_obj["Introduction"]=alex_intro
article_obj["Conclusion"]=alex_conclusion
add_to_research_file(property="article_obj", value=article_obj, key=CONDUCTOR_KEY)

full_article=[{"heading":"Introduction","content":alex_intro}]
for current_section in article_obj["Sections"]:
    full_article.append({"heading":current_section["heading"],"content":current_section["content_full"]})
full_article.append({"heading":"Conclusion","content":alex_conclusion})
add_to_research_file(property="full_article", value=full_article, key=CONDUCTOR_KEY)
# %%
# TODO Edit introduction to reference papers
#%%
def old_baby():
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
    joined_tech_edit = '\n'.join(tech_edit)
    doc_format_chain = LLMChain(prompt=DOC_FORMAT_PROMPT, llm=LLM_BRAINSTORM)
    doc_format = doc_format_chain.run(
        {"idea": idea_of_choice, "doc_source": joined_tech_edit}
    )
    #Run twice to clean it up
    doc_format = doc_format_chain.run(
        {"idea": idea_of_choice, "doc_source": joined_tech_edit}
    )
    # %%
    doc_format_obj = json.loads(doc_format)
    ideas_obj[choice_number]["doc_format_obj"] = doc_format_obj
    add_to_research_file(property="ideas_obj", value=ideas_obj, key=CONDUCTOR_KEY)

    # %%

    # pull out chunks of content as source_content section based on doc format reference sources
    extract_source = LLMChain(prompt=EXTRACT_SOURCE_CONTENT_PROMPT, llm=LLM_FACT_4)
    for current_section in doc_format_obj['content']:
        if 'reference sources' in current_section:
            source_content = extract_source.run(
                {"doc_source":tech_edit, 
                "reference_sources_section":current_section['reference sources']}
            )
            current_section['source_content']=source_content

    ideas_obj[choice_number]["doc_format_obj"] = doc_format_obj
    add_to_research_file(property="ideas_obj", value=ideas_obj, key=CONDUCTOR_KEY)

    # %%
    # TEMP to get sources
    extract_concept_chain = LLMChain(prompt=EXTRACT_IDEA_CONCEPTS_PROMPT, llm=LLM_FACT)
    concepts = extract_concept_chain.run(
        {"idea": idea_of_choice, "latest_research": latest_research}
    )

    sources_needed = parsed_ideas_list = ast.literal_eval(concepts)

    source_metadata=[]
    for concept in sources_needed:
        doc = get_research_source_doc(concept)
        source_metadata.append(doc[0].metadata)

    source_metadata
    # %%

    # Transforming the object array to only include heading and subheadings
    transformed_array = [
        {key: obj[key] for key in obj if key in ["heading", "subheadings"]}
        for obj in doc_format_obj['content']
    ]

    filtered_doc_format_obj = doc_format_obj
    filtered_doc_format_obj['content'] = transformed_array
    filtered_doc_format_obj
    # %%

    alex_content_chain = LLMChain(prompt=ALEX_PERSONA_PROMPT, llm=LLM_CHAT_4)
    previous_section = ""
    alex_doc_content = [doc_format_obj['title']]
    for current_section in doc_format_obj['content']:
        if 'source_content' in current_section:
            source_content = current_section['source_content']
            print("doing source content section")
        additional_info = feedback_reference
        # introduction - provide full doc source
        # introduction - provide metadata title and link with instruction as feedback
        if current_section['heading'] == "Introduction":
            source_content = tech_edit
            additional_info = f"Reference research papers Title and Source in Introduction \n {source_metadata}"
            print("doing intro")
        # conclusion - provide all alex_doc_content (no new_doc_source or feedback_reference)
        elif current_section['heading'] == "Conclusion":
            source_content = alex_doc_content
            additional_info = "none"
            print("doing conclusion")

        alex_content_section = alex_content_chain.run(
            {"idea": idea_of_choice, "feedback_reference": additional_info,
            "doc_format_obj": filtered_doc_format_obj,
            "doc_source": source_content,
            "previous_section": previous_section,
            "current_section": {key: current_section[key] for key in current_section if key in ["heading", "subheadings"]},
            "domain": domain}
        )
        previous_section = alex_content_section
        alex_doc_content.append(alex_content_section)

    # %%
    ideas_obj[choice_number]["alex_doc_content"] = alex_doc_content
    add_to_research_file(property="ideas_obj", value=ideas_obj, key=CONDUCTOR_KEY)

    # %%
    # should include something about applying research to business in prompt instruction
    doc_source = '\n'.join(alex_doc_content)
    doc_source

# %%
article = ""
for item in full_article:
    article += item["heading"] + "\n"
    article += item["content"] + "\n\n"

# Remove the extra newlines at the end
article = article.rstrip()

article
# %%
post_chain = LLMChain(prompt=LINKEDIN_POST_PRO_PROMPT, llm=LLM_BRAINSTORM)
post = post_chain.run(
    {"article": article}
)
print(post)

# %%
#NEEDS TO BE ABSTRACTED - subfolder
CONTENT_FILENAME = './content/2/copy.json'
add_to_research_file(property="post", value=post, key=CONDUCTOR_KEY, filename=CONTENT_FILENAME)
add_to_research_file(property="article", value=article, key=CONDUCTOR_KEY, filename=CONTENT_FILENAME)


# %%


# %%
