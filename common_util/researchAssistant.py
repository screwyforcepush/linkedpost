import json
import langchain
from common_util.llms import LLM_FACT_4
from langchain.chains import LLMChain
from langchain import PromptTemplate
from common_util.memory import tiktoken_len

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

# %%
