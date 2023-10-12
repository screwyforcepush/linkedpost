import ast
import json
import langchain
from common_util.llms import LLM_BRAINSTORM, LLM_FACT_4
from langchain.chains import LLMChain
from langchain import PromptTemplate
from common_util.memory import tiktoken_len
from customPrompts import PERPSONA_AVERY_AI, PERSONA_BENJI_INNOVATE, PERSONA_OCEANSMITH_MARKETGAP

# %%          
RESEARCH_PAPERS_FILENAME = './json/ai_research_papers.json'

def concept_condence(content):
    prompt_template = """
    [System][Temperature=0][Persona]You are the Research Purifier. 
    You love to deeply understand the inner workings behind Research, then distill the applicable essence. You maximally compress the meaningful takeaways, while staying unambiguous to the model in a bare context.
    [TASK]
    Concisely summarise the underlying principles and facts from the Research provided.
    Include specifics about how and why the concept, method, technique works.
    Include an application execution example if applicable.
    Your Purified Distilation will be used to apply this research to business use cases.
    *Distill* *Summarise* *Purify*
    [/TASK]

    # Research 
    {content}

    # Purified Distillation

    """
    prompt = PromptTemplate(template=prompt_template, input_variables=["content"])

    summary_chain = LLMChain(
        prompt=prompt,
        llm=LLM_FACT_4
    )
    return(summary_chain.run(content=content)) 
# %%

def research_condense(content):
    print(tiktoken_len(content))
    while tiktoken_len(content)>7000:
        content = content[:int(len(content) * 0.9)]
    print(tiktoken_len(content))
    return concept_condence(content)


# %%
    
def get_latest_ai_research(tokens=6000):
    with open(RESEARCH_PAPERS_FILENAME, 'r') as f:
            data = json.load(f)
    i=0
    while tiktoken_len(json.dumps(data))>tokens:
        data = data[i:]
        i+=1
    print(tiktoken_len(json.dumps(data)), "research tokens")
    print(len(data), "latest research included")
    return data

# %%
def select_papers(topic, papers, persona):
    prompt_template = """
    {persona}

    
    [Task]Select the 20 most relevant Research Papers that could be utilised for the Idea.
    Provide your Paper Selection in an array format, sorted from most to least relevance.[/Task]

    Paper Selection Format: ["Explaining AI", "Optimizing LLMs", "Chain of thought prompting"]

    Idea:{{
        {topic}
    }}

    Research Papers: {{ 
        {papers}
    }}

    Paper Selection:
    """
    prompt = PromptTemplate(template=prompt_template, input_variables=["persona","topic","papers"])

    summary_chain = LLMChain(
        prompt=prompt,
        llm=LLM_BRAINSTORM
    )
    return(summary_chain.run({"persona": persona, "papers":papers, "topic":topic})) 


def get_relevant_ai_research(topic, tokens=5000):
    with open(RESEARCH_PAPERS_FILENAME, 'r') as f:
        data = json.load(f)
    keys_array = [item['key'] for item in data]
    i=0
    while tiktoken_len(json.dumps(keys_array))>tokens:
        keys_array = keys_array[i:]
        i+=1
    top_papers1=select_papers(topic=topic,papers=keys_array,persona=PERPSONA_AVERY_AI)
    top_papers1=ast.literal_eval(top_papers1)
    top_papers3=select_papers(topic=topic,papers=keys_array,persona=PERSONA_BENJI_INNOVATE)
    top_papers3=ast.literal_eval(top_papers3)

    common_items = list(set(top_papers3) & set(top_papers1))
    print("relevant research", common_items)
    research=[]
    for item in data:
        for title in common_items:
            if item["key"] == title:
                research.append(item)
    i=len(research)
    while tiktoken_len(json.dumps(research))>tokens:
        research = research[:i]
        i-=1
    return research
 
# %%
get_relevant_ai_research("Incorporating gen AI in MarTech stack for customer lifecycle management.")
# %%
