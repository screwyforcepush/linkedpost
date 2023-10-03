import ast
import json
import re
import os

from common_util.memory import set_entity_memory_long_cache
from common_util.researchAssistant import get_latest_ai_research
from queryDB import tools
import langchain
from langchain.chains import LLMChain
from datetime import datetime
from common_util.customPrompts import (
    BRAINSTORMER_PROMPT,
    OUTPUT_PARSER_PROMPT,
    IDEA_SELECTOR_PROMPT,
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
    LLM_FACT
)

from common_util.diagramCreator import (
    DIAGRAM_DESIGN_PROMPT,
    DIAGRAM_CODE_PROMPT,
    IMG_GEN_PROMPT,
    gen_fetch_img
)

from common_util.searchWeb import (
    run_judge_idea_agent,
    SEARCH_TOOL
)
from queryDB import (
    add_to_research_file,
    set_conductor_key,
    get_reserach_from_file,
)
from langchain.agents import initialize_agent, AgentType
from langchain import LLMChain


langchain.debug = True
global CONDUCTOR_KEY, domain, article_critique_obj, full_article, article_obj,article_structure, latest_research, choice_number, ideas_obj, enrich, idea_of_choice, article, post
# %%
def load_global_vars(hist_obj):
    global article_critique_obj, full_article, article_obj,article_structure, latest_research, choice_number, ideas_obj, enrich, idea_of_choice, article, post
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
        post = hist_obj["post"]
    except KeyError as e:
        print("stopped at", e)

def get_historical_variable(key):
    global CONDUCTOR_KEY
    CONDUCTOR_KEY = key
    set_conductor_key(key)
    set_entity_memory_long_cache([])
    return get_reserach_from_file(key=key)

# %%
## LOADS completed vars for step
def set_key_load_vars(key = "20230921134237"):
    global CONDUCTOR_KEY
    CONDUCTOR_KEY = key
    hist_var = get_reserach_from_file(CONDUCTOR_KEY)
    load_global_vars(hist_var)

# %%
def init_key_research():
    global latest_research
    global CONDUCTOR_KEY
    CONDUCTOR_KEY = datetime.now().strftime("%Y%m%d%H%M%S")
    set_conductor_key(CONDUCTOR_KEY)
    set_entity_memory_long_cache([])


    # new research
    #TODO need to include authors and published date
    latest_research = get_latest_ai_research(tokens=6000)
    # entities = get_entities()
    add_to_research_file(
        property="latest_research", value=latest_research, key=CONDUCTOR_KEY
    )
# %%
def idea_gen():
    global ideas_obj
    llm_chain = LLMChain(prompt=BRAINSTORMER_PROMPT, llm=LLM_BRAINSTORM)
    ideas = llm_chain.run(
        {
            "concepts": latest_research,
            "domain": domain,
        }
    )
    add_to_research_file(property="seed_ideas", value=ideas, key=CONDUCTOR_KEY)

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
    parsed_ideas_list = ast.literal_eval(ideas_parsed)
    ideas_obj = {}
    i = 1
    for idea in parsed_ideas_list:
        ideas_obj[i] = {"idea": idea}
        i += 1
        print(json.dumps(idea))
    add_to_research_file(property="ideas_obj", value=ideas_obj, key=CONDUCTOR_KEY)

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

    # select idea
    idea_select_chain = LLMChain(prompt=IDEA_SELECTOR_PROMPT, llm=LLM_FACT_4)
    selected_response = idea_select_chain.run({"ideas": ideas_obj})
    ideas_obj["selection"] = selected_response
    add_to_research_file(property="ideas_obj", value=ideas_obj, key=CONDUCTOR_KEY)

    # Extract the choice number using regex
    choice_match = re.search(r"Choice: (\d+)", selected_response)
    choice_number = (choice_match.group(1)) if choice_match else None
    return choice_number

# %%
#
# !! MANUAL VS AUTO SELECT NEED TO SET VARIABLE
#

def enrich_idea(manual_select=True,choice_number="1"):
    global idea_of_choice, enrich
    if manual_select == True:
    # !! SELECT IDEA NUMBER HERE MANUAL
        add_to_research_file(property="idea_choice", value=choice_number, key=CONDUCTOR_KEY)
    else:
        #Auto judge has broken scope var
        choice_number=judge_and_select(parsed_ideas_list)

    idea_of_choice = ideas_obj[choice_number]["idea"]


    agent_executor = initialize_agent(
        tools,
        LLM_FACT_4,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        max_iterations=7,
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

    ideas_obj[choice_number]["enrichment"] = enrich
    add_to_research_file(property="ideas_obj", value=ideas_obj, key=CONDUCTOR_KEY)

# %%
def stucture():
    global article_obj, article_structure
    article_structure_chain = LLMChain(prompt=ARTICLE_STRUCTURE_PROMPT, llm=LLM_BRAINSTORM)
    article_structure = article_structure_chain.run({"idea": idea_of_choice, "enrich": enrich})
    ideas_obj[choice_number]["article_structure"] = article_structure
    add_to_research_file(property="ideas_obj", value=ideas_obj, key=CONDUCTOR_KEY)

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

    article_obj = ast.literal_eval(article_obj)
    add_to_research_file(property="article_obj", value=article_obj, key=CONDUCTOR_KEY)


# %%

def section_knowledge():
    global article_obj
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

    article_obj["Sections"]=article_sections
    add_to_research_file(property="article_obj", value=article_obj, key=CONDUCTOR_KEY)

#%%
def content_gen():
    global article_obj, full_article
    alex_pro_content_chain = LLMChain(prompt=ALEX_PRO_PERSONA_PROMPT, llm=LLM_BRAINSTORM)
    previous_section_content = ""
    article_sections = []
    for current_section in article_obj["Sections"]:
        alex_content_section = alex_pro_content_chain.run(
            {"idea": idea_of_choice, 
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

    article = []
    for current_section in article_obj["Sections"]:
        article.append({"heading":current_section["heading"],"content":current_section["content_full"]})
    article

    alex_pro_intro_conclusion_chain = LLMChain(prompt=ALEX_PRO_PERSONA_INTRO_CONCLUSION_PROMPT, llm=LLM_BRAINSTORM)
    alex_intro = alex_pro_intro_conclusion_chain.run(
            {"industry": domain["industry"], 
            "article": article,
            "intro_conclusion": "Introduction"
            }
        )

    alex_conclusion = alex_pro_intro_conclusion_chain.run(
            {"industry": domain["industry"], 
            "article": article,
            "intro_conclusion": "Conclusion"
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

#%%
def critique_learn():
    global article_obj, article_critique_obj
    article_critique_chain = LLMChain(prompt=ARTICLE_CRITIQUE_PROMPT, llm=LLM_BRAINSTORM)
    article_critique = article_critique_chain.run({"article": full_article})
    article_critique_obj = ast.literal_eval(article_critique)

    add_to_research_file(property="feedback", value=article_critique_obj, key=CONDUCTOR_KEY)

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


    article_obj["Sections"]=article_sections
    add_to_research_file(property="article_obj", value=article_obj, key=CONDUCTOR_KEY)

def get_citation_feedback():
    sources = []
    citation_feedback = "Include citation of research papers: "
    # If file exists, load existing data
    metajsnfile = "./json/metadata.json"
    if os.path.exists(metajsnfile):
        with open(metajsnfile, 'r') as f:
            data = json.load(f)
    if isinstance(idea_of_choice["Concept Keys"], str):
        idea_of_choice["Concept Keys"]=[idea_of_choice["Concept Keys"]]

    for paper in idea_of_choice["Concept Keys"]:
        for item in data:
            if 'Title' in item and item['Title'] == paper:
                sources.append({
                    "Title": item["Title"],
                    "Authors": item["Authors"],
                    "Published": item["Published"],
                    "source": item["source"]
                })
    return f"{citation_feedback}{sources}"

    
def final_edit(citation_feedback=""):
    global article_obj, full_article
    article_critique_obj
    alex_pro_edit_chain = LLMChain(prompt=ALEX_PRO_EDIT_PROMPT, llm=LLM_BRAINSTORM)
    article_sections = []
    for i in range(len(article_obj["Sections"])):
        section = article_obj["Sections"][i]
        alex_content_section = alex_pro_edit_chain.run(
            {"industry": domain["industry"], 
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

    article_obj["Sections"]=article_sections

    alex_pro_intro_conclusion_edit_chain = LLMChain(prompt=ALEX_PRO_EDIT_INTRO_CONCLUSION_PROMPT, llm=LLM_BRAINSTORM)
    alex_intro = alex_pro_intro_conclusion_edit_chain.run(
            {"industry": domain["industry"], 
            "article": full_article,
            "intro_conclusion": "Introduction",
            "overall": article_critique_obj["Overall"],
            "section_feedback":f"""{article_critique_obj["Introduction"]}\n{citation_feedback}"""
            }
        )

    alex_conclusion = alex_pro_intro_conclusion_edit_chain.run(
            {"industry": domain["industry"], 
            "article": full_article,
            "intro_conclusion": "Conclusion",
            "overall": article_critique_obj["Overall"],
            "section_feedback":article_critique_obj["Conclusion"]
            }
        )

    article_obj["Introduction"]=alex_intro
    article_obj["Conclusion"]=alex_conclusion
    add_to_research_file(property="article_obj", value=article_obj, key=CONDUCTOR_KEY)

    full_article=[{"Title":article_obj["Title"]},{"heading":"Introduction","content":alex_intro}]
    for current_section in article_obj["Sections"]:
        full_article.append({"heading":current_section["heading"],"content":current_section["content_full"]})
    full_article.append({"heading":"Conclusion","content":alex_conclusion})
    add_to_research_file(property="full_article", value=full_article, key=CONDUCTOR_KEY)

# %%
def gen_post():
    global post
    post=[]
    post_chain = LLMChain(prompt=LINKEDIN_POST_PRO_PROMPT, llm=LLM_BRAINSTORM)
    post1 = post_chain.run(
        {"article": full_article}
    )
    post_chain = LLMChain(prompt=LINKEDIN_POST_PRO_PROMPT, llm=LLM_BRAINSTORM)
    post2 = post_chain.run(
        {"article": full_article}
    )
    post=[post1,post2]

def gen_diagram():
    design_diagram_chain = LLMChain(prompt=DIAGRAM_DESIGN_PROMPT, llm=LLM_BRAINSTORM)
    design = design_diagram_chain.run(
        {"article": full_article}
    )
    code_diagram_chain = LLMChain(prompt=DIAGRAM_CODE_PROMPT, llm=LLM_BRAINSTORM)
    code_response = code_diagram_chain.run(
        {"design": design}
    )
    print("DIAGRAM CODE RESPONSE: ", code_response)
    # Extract python code between the triple backticks
    python_script = re.search(r'```python\n(.*?)\n```', code_response, re.DOTALL)

    # Extracted script
    extracted_script = python_script.group(1) if python_script else None
    extracted_script
    exec(extracted_script)


def gen_img():
    img_chain = LLMChain(prompt=IMG_GEN_PROMPT, llm=LLM_BRAINSTORM)
    valentine_response = img_chain.run(
        {"post": post}
    )
    # Extract array between the square brackets
    array_match = re.search(r'\[\s*"(.*?)"\s*,\s*"(.*?)"\s*\]', valentine_response, re.DOTALL)

    # Extracted array
    extracted_array = eval(array_match.group(0)) if array_match else None
    gen_fetch_img(extracted_array)

def move_imgs(path):
    import shutil

    source_directory = './'

    # Loop through the range of file numbers
    for i in range(1, 11):
        file_name = f"img{i}.png"
        shutil.move(source_directory + file_name, path + file_name)
    shutil.move(source_directory + "sol_arch.png", path + "sol_arch.png")

def mkdir_content_sub():
    # Get a list of all existing directories under './content/'
    dir_list = sorted([d for d in os.listdir('./content/') if os.path.isdir(os.path.join('./content/', d)) and d.isdigit()])

    # Get the last directory in the sorted list and increment its number
    highest_dir = dir_list[-1]
    next_dir_num = int(highest_dir) + 1

    # Create the directory for the next number
    new_dir_path = './content/' + str(next_dir_num) + '/'
    os.makedirs(new_dir_path, exist_ok=True)

    return new_dir_path


def create_copy_json(path):
    article = ""
    for item in full_article:
        if "Title" in item:
            article += item["Title"] + "\n"
        else:    
            article += item["heading"] + "\n"
            article += item["content"] + "\n\n"

    # Remove the extra newlines at the end
    article = article + "*This article was conceptualized and crafted by an advanced AI system designed by Alex Savage - a leader and innovator at the nexus of data and artificial intelligence. Leveraging state-of-the-art algorithms and deep learning, this AI system embodies Alex's commitment to driving forward the knowledge economy, fostering innovation, and carving new pathways in the tech landscape.* \n\n*Connect with Alex to explore synergies and be a part of the future where technology meets foresight and creativity.*"
    filename = "copy.json"
    add_to_research_file(property="post", value=post, key=CONDUCTOR_KEY, filename=path+filename)
    add_to_research_file(property="article", value=article, key=CONDUCTOR_KEY, filename=path+filename)

    print("POST:\n")
    print(post)
    print("ARTICLE:\n")
    print(article)


# %%

DOMAINS = ["OTT video streaming", "Ecommerce", "FinTech", "HealthTech", "eLearning", "property tech", "stockmarket trading tech"]
domain= "OTT video streaming analytics"
# /TODO add exclusions from past ideas
domain={"industry":"OTT video streaming",
        "domains":["streaming platform", "ad products for AVOD clients", "marketing", "content creation/pocurement"],
        "exclude": "personalised content discovery"}
domain={"industry":"Digital product analytics",
        "domains":["Augmented Visualization", "Automated Feature Feedback Loop", "Predictive A/B Testing", "Suggested business actions for great impact"]}

# %%
init_key_research()
idea_gen()
#%%
enrich_idea(manual_select=True,choice_number="2")
stucture()
section_knowledge()
content_gen()
critique_learn()
citation_feedback=get_citation_feedback()
final_edit(citation_feedback=citation_feedback)
gen_post()
gen_diagram()

gen_img()
content_path=mkdir_content_sub()
#%%
create_copy_json(content_path)
move_imgs(content_path)
# %%
set_key_load_vars(key="20230928174613")

# %%
