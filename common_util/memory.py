# %%
import ast
import json
import re

from langchain import PromptTemplate
from langchain.chains import LLMChain
from common_util.customClasses import CUSTOM_ENTITY_EXTRACTION_PROMPT, SQLiteEntityStore
from common_util.llms import LLM_FACT
from langchain.memory import ConversationEntityMemory
import tiktoken
import time

tokenizer = tiktoken.get_encoding("cl100k_base")
# create the length function
def tiktoken_len(text:str):
    global tokenizer
    tokens = tokenizer.encode(text, disallowed_special=())
    return len(tokens)

entity_store=SQLiteEntityStore()
print(entity_store.conn)

ENTITY_MEMORY = ConversationEntityMemory(llm=LLM_FACT, entity_store=entity_store, entity_extraction_prompt=CUSTOM_ENTITY_EXTRACTION_PROMPT, k=0)
entity_memory_long_cache=[]

def set_entity_memory_long_cache(cache):
    global entity_memory_long_cache
    entity_memory_long_cache=cache

def get_entity_memory_long_cache():
    global entity_memory_long_cache
    return entity_memory_long_cache


def save_entities_to_long_cach():
    global ENTITY_MEMORY, entity_memory_long_cache
    for entity in ENTITY_MEMORY.entity_cache:
        if entity not in entity_memory_long_cache:
            entity_memory_long_cache.append(entity)


def get_entities(use_long_cache:bool=False, entity_tokens:int=2000, query:str=None):
    global ENTITY_MEMORY, entity_memory_long_cache
    cache = ENTITY_MEMORY.entity_cache
    if use_long_cache:
        cache = entity_memory_long_cache
    entity_summaries = {}
    for entity in cache:
        if ENTITY_MEMORY.entity_store.get(entity):
            entity_summaries[entity] = ENTITY_MEMORY.entity_store.get(entity, "")
    if query:
        entities= get_filtered_entities(entity_summaries, entity_tokens, query)
        override_long_cache(entities)
        return entities
    else:
        print("Full summary as no query for get_entities")
        return entity_summaries
def override_long_cache(entities):
    cache=[]
    for key, value in entities.items():
        cache.append(key)
    set_entity_memory_long_cache(cache)

def split_json(json_obj):
    keys = list(json_obj.keys())
    half = len(keys)//2

    json_obj_1 = {k: json_obj[k] for k in keys[:half]}
    json_obj_2 = {k: json_obj[k] for k in keys[half:]}

    return json_obj_1, json_obj_2

def get_filtered_entities(entities, entity_tokens, query):
    if tiktoken_len(json.dumps(entities))<entity_tokens:
        return entities
    #too much to reduce in one go
    if tiktoken_len(json.dumps(entities))>3000:
        ent1, ent2 = split_json(entities)
        print(ent1)
        print(ent2)
        filtered_ent1 = get_filtered_entities(ent1,entity_tokens/2,query)
        filtered_ent2 = get_filtered_entities(ent2,entity_tokens/2,query)
        return {**filtered_ent1, **filtered_ent2}
    else:
        cost = {}
        totalcost=0
        for key, value in entities.items():
            cost[key]= tiktoken_len(key + ' ' + value)*2
            totalcost=totalcost+cost[key]
        print(totalcost,cost)

        prompt_template = """Act as a cost effeciency expert.
        Your task is to select which entities would proove most valuable.
        Value is measured as relevance to the Query.
        Your Response must be formated as an array.

        # Example response 
        ["entity key 1", "entity key 4", "entity key 3"]

        # Constraints
        You have a budget of {budget}.
        Each entity has an associated cost - entityKey:cost
        totalSelectedEntityCost must not exceed your budget.
        Use the /entityCalculator to calculate totalSelectedEntityCost.
        Prioritise entity selection from most relevant to least relevant.
        Only select relevant entities.
        You do not need to use the entire budget.

        # Query
        {query}

        # Entity cost
        {cost}

        # Entity value
        {entities}

        """

        prompt_template = """
        Cst effncy exprt. Task: slct vluable entities. Vlu = rlvnce 2 Query. Rspns in arry.

        # Example response 
        ["entity key 1", "entity key 4", "entity key 3"]

        # Cnstrnts
        Budget of {budget}.
        Entity cost - entityKey:cost
        Entity value - entityKey:value
        Total selected entity cost ≤ budget.
        Prioritise entity slctn by rlvnce.
        Slct only rlvnt entities.
        No need to use entire budget.
        Include execution output


        # Query
        {query}

        # Entity cost
        {cost}

        # Entity value
        {entities}
        """


        prompt = PromptTemplate(template=prompt_template, input_variables=["query","entities", "budget", "cost"])

        entity_reduce = LLMChain(
            prompt=prompt,
            llm=LLM_FACT
        )
        entity_keys_arr=None
        for i in range(3):

            try:
                entity_keys = entity_reduce.run(query=query,entities=entities,cost=cost,budget=entity_tokens)
                print(entity_keys)
                match = re.search(r'\[.*?\]', entity_keys)
                array_str = match.group(0) if match else None
                
                # Converting the extracted string to an actual array
                #TODO this is too brittle. did a try catch for now
                # ValueError: malformed node or string on line 1: 
                entity_keys_arr = ast.literal_eval(array_str) if array_str else None
                break
            except ValueError:
                if i < 3 - 1:  # i is zero indexed
                    print("ValueError parsing llm output to array for entitites... retrying")
                    continue
        if entity_keys_arr:
            filtered_json = {k: entities[k] for k in entity_keys_arr if k in entities}
        else:
            filtered_json={}
        return filtered_json


def load_memory_vars(from_text:str):
    global ENTITY_MEMORY
    _input = {"input": from_text}
    ENTITY_MEMORY.load_memory_variables(_input)
    #TODO infinite loop?

    # Define save_context_with_timeout function
    def save_context_with_timeout(_input, _output, timeout):
        start_time = time.time()

        # Assuming ENTITY_MEMORY.save_context() involves a loop or repeated operations
        # You'll need to replace the following loop with the actual implementation
        for i in range(1000000):  # Some large number
            # Check if more than timeout seconds have passed
            if time.time() - start_time > timeout:
                print('ENTITY_MEMORY.save_context took too long to run.')
                return
            # The actual operation would go here
            ENTITY_MEMORY.save_context(_input, _output)
        pass

    save_context_with_timeout(_input, {"output": ""}, 10.0)
    ENTITY_MEMORY.chat_memory.clear()
    save_entities_to_long_cach()


def key_words(query):
    prompt_template = """Act as a an SEO expert. 
    Your task is to extract key words from the given text. Output a capitalised array.
    
    # EXAMPLE
    ## Text
    What is a unique AI prompting strategy? How can it be applied to video streaming analytics?
    ## Output
    ["AI Prompting", "AI Prompting Strategy", "Video Streaming", Video Streaming Analytics"]
    END OF EXAMPLE

    # EXAMPLE
    ## Text
    How can chain of thought prompting be used to increase video ad revenue?
    ## Output
    ["Chain of Thought", "Chain of Thought Prompting", "Video Ads", "Video Ad Revenue", "Ad Revenue"]
    END OF EXAMPLE

    ## Text
    {query}
    ## Output
    """
    prompt = PromptTemplate(template=prompt_template, input_variables=["query"])

    key_words_chain = LLMChain(
        prompt=prompt,
        llm=LLM_FACT,
        verbose=True
    )
    return(key_words_chain.run(query=query))


def warm_cache(query):
    global ENTITY_MEMORY
    entities = json.loads(key_words(query))
    ENTITY_MEMORY.entity_cache = entities
    save_entities_to_long_cach()
    return get_entities()


def get_entity_def(term:str)->str:
    """Look up definition of a term in entity database.
    Args:
        term: The entity key to query from the database.
    """
    global ENTITY_MEMORY
    return ENTITY_MEMORY.entity_store.get(term, "Not in Database")

#%%
# TEST = {
#     "Chain of Thought": "Chain of Thought is a prompt implemented using language models to enable complex reasoning, which involves sequentially exploring different lines of reasoning to arrive at a solution and can be used in conjunction with the tree-of-thought prompting technique to guide the thought process and reasoning behind answering a question or solving a problem.",
#     "Chain of Thought Prompting": "Chain of Thought Prompting (CoTP) is a technique that can be applied to video streaming analytics to improve the accuracy and efficiency of data analysis. CoTP involves using a series of prompts or questions to guide the thought process of the analyst, helping them to explore different aspects of the data and uncover valuable insights. It can be implemented using various tools and techniques, such as data visualization, statistical analysis, and machine learning algorithms. By applying CoTP, organizations can make data-driven decisions and optimize their video streaming services.",
#     "Video Streaming Analytics": "Video Streaming Analytics involves tracking and analyzing user engagement and behavior on video streaming platforms, collecting data on metrics such as video views, play rate, and engagement to gain insights into audience preferences and optimize content delivery. It also includes tactics for increasing video views, such as optimizing impressions through channel selection, and strategies for play rate and engagement optimization, such as autoplay, clear copy, custom thumbnails, trimming intros, adding subtitles, and incorporating interactivity. Additionally, Chain of Thought Prompting (CoTP) can be applied to video streaming analytics to improve the accuracy and efficiency of data analysis. CoTP involves using a series of prompts or questions to guide the thought process of the analyst, helping them to explore different aspects of the data and uncover valuable insights.",
#     "Language Models": "Language models are improved using the Chain of Thought prompting technique, which involves providing prompts or cues in the form of sentences or questions to guide the model's thinking process and generate coherent and relevant text. The effectiveness of Chain of Thought Prompting can be evaluated by measuring the accuracy of the generated text through metrics such as accuracy or similarity.",
#     "Accuracy": "Accuracy is a measure used to evaluate the effectiveness of Chain of Thought Prompting in generating text with different levels of complexity and specificity. It involves comparing the generated text with a reference or ground truth text and calculating metrics such as accuracy or similarity.",
#     "Similarity": "Similarity is a metric that can be used to evaluate the effectiveness of Chain of Thought Prompting in generating text by comparing the generated text with a reference or ground truth text.",
#     "ML": "ML, or machine learning, can be utilized in video streaming analytics to attract, acquire, and retain subscribers in over-the-top (OTT) video services. ML enables personalized recommendations based on user consumption habits, predicts user behavior, and optimizes marketing activities, customer acquisition, retention, and engagement.",
#     "AI": "AI research at Microsoft focuses on developing and improving artificial intelligence technologies, particularly in the areas of code generation, language understanding, and video streaming analytics. They are involved in evaluating AI models for code suggestions, training language models to follow human instructions, and utilizing machine learning and smart data to optimize user engagement and behavior on video streaming platforms.",
#     "OTT": "OTT (Over-the-Top) services can utilize video streaming analytics, machine learning, and smart data to optimize various aspects of their video service, including content discovery, acquisition, engagement, monetization, and churn analysis. By leveraging data effectively, businesses can enhance their marketing effectiveness, improve conversion rates, and increase customer lifetime value.",
#     "Content Discovery": "Content Discovery is a process in video streaming analytics that involves optimizing impressions through selecting channels that align with the behaviors of the target audience, using tactics such as autoplay, clear and concise copy, custom thumbnails, trimming the intro, adding subtitles, and incorporating interactivity to improve engagement levels and capture and retain the audience's attention.",
#     "Acquisition": "Acquisition in the context of video streaming analytics involves utilizing machine learning and smart data to attract, acquire, and retain subscribers in over-the-top (OTT) video services. ML and AI enable personalized recommendations based on user consumption habits, increasing user satisfaction and engagement. ML models can also predict user behavior, such as identifying potential paying customers and predicting churn, which can be used to optimize marketing activities, customer acquisition, retention, and engagement.",
#     "Engagement": "Engagement optimization in video streaming involves tactics such as trimming the intro, adding subtitles, and incorporating interactivity to enhance engagement levels and capture and retain the audience's attention.",
#     "Monetization": "Monetization in video streaming involves optimizing impressions through selecting channels that align with the behaviors of the target audience, using tactics such as autoplay, clear copy, custom thumbnails, and engagement optimization strategies to improve content experience and encourage viewer engagement.",
#     "Churn Analysis": "Churn analysis involves using machine learning models to predict user behavior, such as identifying potential paying customers and predicting churn, in order to optimize marketing activities, customer acquisition, retention, and engagement in video streaming platforms.",
#     "User Engagement": "User Engagement is the process of tracking and analyzing metrics such as video views, play rate, and engagement on video streaming platforms to gain insights into audience preferences and optimize content delivery. Tactics such as optimizing impressions, play rate, and engagement can be employed to increase user engagement. Machine learning and smart data can also be utilized to attract, acquire, and retain subscribers in video streaming services.",
#     "Behavior": "Behavior refers to the actions and engagement of users on video streaming platforms, which can be tracked and analyzed through video streaming analytics. By collecting data on metrics such as video views, play rate, and engagement, businesses can gain insights into audience preferences and optimize content delivery. Tactics such as optimizing impressions, play rate, and engagement can be employed to increase video views and improve the content experience. Machine learning and smart data can also be utilized to personalize recommendations and predict user behavior, enabling businesses to optimize marketing activities, customer acquisition, retention, and engagement in the context of video streaming services.",
#     "Video Views": "Video Views are a metric that can be tracked using online video platforms or native social platforms, and optimizing them involves serving the right content to the right audience, using tactics such as optimizing impressions, play rate, and engagement. It is important to measure and optimize all metrics related to views, not just video views, to see meaningful growth. Video views measure how many times a video is played, indicating that a play request was sent to the player and the video started playing. Video views are important for product managers and engineers to track. Additionally, video streaming analytics involves collecting data on metrics such as video views, play rate, and engagement to gain insights into audience preferences and optimize content delivery.",
#     "Play Rate": "Play Rate optimization involves tactics such as setting landing page videos to autoplay, using clear and concise copy, and creating custom thumbnails to improve the content experience and encourage viewers to engage with the video.",
#     "Impressions": "Impressions are important for optimizing video views by selecting channels that align with the behaviors of the target audience, such as high-volume, low-intent channels for awareness goals and low-volume, high-intent channels like email for bottom-of-funnel content.",
#     "Channels": "Channels play a crucial role in video streaming analytics, as optimizing impressions and play rate involves selecting channels that align with the behaviors of the target audience, such as high-volume, low-intent channels for awareness goals, medium-volume, medium-intent channels for consideration stage targeting, and low-volume, high-intent channels like email for bottom-of-funnel content.",
#     "Awareness Goals": "Awareness goals in video streaming analytics involve optimizing impressions through selecting channels that align with the behaviors of the target audience, with high-volume, low-intent channels being suitable for this purpose.",
#     "Consideration Stage Targeting": "Consideration Stage Targeting is a strategy in video streaming analytics that involves selecting medium-volume, medium-intent channels to serve content to the target audience, with the goal of optimizing engagement and encouraging viewers to consider the content further.",
#     "Bottom-of-Funnel Content": "Bottom-of-Funnel Content refers to content that is effective for low-volume, high-intent channels like email in video streaming analytics. It aims to engage viewers and encourage them to take action, such as making a purchase or subscribing to a service.",
#     "Email": "Email is a low-volume, high-intent channel that is effective for bottom-of-funnel content in video streaming analytics.",
#     "Landing Page Videos": "Landing page videos can be optimized for play rate by setting them to autoplay, using clear copy, creating custom thumbnails, and benchmarking play rates by video location before making changes to campaign messaging. These strategies aim to improve the content experience and encourage viewers to engage with the video.",
#     "Autoplay": "Autoplay is an optimization technique in video streaming analytics that involves setting landing page videos to autoplay, using clear copy, and creating custom thumbnails to improve play rate and overall engagement. It is a tactic used to improve the content experience and encourage viewers to engage with the video.",
#     "Copy": "Copy involves tactics such as setting landing page videos to autoplay, using clear and concise copy, and creating custom thumbnails to improve the content experience and encourage viewers to engage with the video.",
#     "Custom Thumbnails": "Custom thumbnails are an important aspect of play rate optimization in video streaming analytics, along with setting landing page videos to autoplay and using clear copy. These strategies aim to improve the content experience and encourage viewers to engage with the video.",
#     "Social Engagement Optimization": "Social Engagement Optimization involves tactics such as trimming the intro, adding subtitles, and incorporating interactivity to enhance engagement levels in video streaming.",
#     "Intro Trimming": "Intro Trimming is a tactic used in video streaming analytics to enhance engagement levels by trimming the introduction of videos.",
#     "Subtitles": "Subtitles can be added to videos as a way to optimize engagement and increase viewer retention, along with other tactics such as trimming the intro and considering interactivity. They are one of the strategies used in engagement optimization in video streaming, aiming to capture and retain the audience's attention.",
#     "Interactivity": "Interactivity in video streaming analytics involves incorporating features such as trimming the intro, adding subtitles, and providing interactive elements in videos to enhance engagement levels and capture the audience's attention.",
#     "Machine Learning": "Machine Learning (ML) is a technology that can be utilized in video streaming analytics to optimize various aspects of an OTT video service, including content discovery, acquisition, engagement, monetization, and churn analysis. ML enables personalized recommendations based on user consumption habits, predicts user behavior, and can be used to optimize marketing activities, customer acquisition, retention, and engagement.",
#     "Smart Data": "Smart Data is a term used in the context of video streaming analytics and machine learning (ML) to refer to the utilization of data collected on metrics such as video views, play rate, and engagement to gain insights into audience preferences and optimize content delivery.",
#     "Personalized Recommendations": "Personalized Recommendations in video streaming analytics involve utilizing machine learning and smart data to provide tailored content suggestions based on user consumption habits, increasing user satisfaction and engagement. ML models can also predict user behavior, such as identifying potential paying customers and predicting churn, enabling businesses to optimize marketing activities, customer acquisition, retention, and engagement.",
#     "User Satisfaction": "User Satisfaction in video streaming analytics can be improved through tactics such as optimizing impressions, play rate, and engagement. Machine learning and smart data can also be utilized to personalize recommendations and predict user behavior, leading to increased satisfaction and engagement.",
#     "User Behavior": "User Behavior refers to the actions and preferences exhibited by individuals while engaging with video streaming platforms. It involves tracking and analyzing metrics such as video views, play rate, and engagement to gain insights into audience preferences and optimize content delivery. Tactics such as optimizing impressions, play rate, and engagement can be employed to increase video views and enhance user engagement. Machine learning and smart data can also be utilized to attract, acquire, and retain subscribers, as well as predict user behavior for optimization purposes.",
#     "Paying Customers": "Paying customers can be identified and predicted using machine learning models based on user behavior, which can help optimize marketing activities, customer acquisition, retention, and engagement in video streaming platforms.",
#     "Predicting Churn": "Predicting churn involves using machine learning models to identify potential paying customers and predict customer behavior in order to optimize marketing activities, customer acquisition, retention, and engagement.",
#     "Marketing Activities": "Marketing activities involve optimizing impressions through selecting channels that align with the behaviors of the target audience, utilizing tactics such as play rate optimization and engagement optimization to improve content experience and encourage viewer engagement, and leveraging machine learning and smart data to attract, acquire, and retain subscribers in video streaming platforms.",
#     "Customer Acquisition": "Customer Acquisition involves optimizing impressions through selecting channels that align with the behaviors of the target audience, such as high-volume, low-intent channels for awareness goals and low-volume, high-intent channels like email for bottom-of-funnel content. Play rate optimization and engagement optimization strategies can also be employed to improve content experience and capture audience attention. Additionally, machine learning and smart data can be utilized to attract, acquire, and retain subscribers in video streaming services.",
#     "Retention": "Retention is an important aspect of video streaming analytics, as it involves strategies to attract, acquire, and retain subscribers in over-the-top (OTT) video services. Machine learning (ML) and smart data can be utilized to optimize retention by predicting user behavior, identifying potential paying customers, and optimizing marketing activities.",
#     "Data": "Data is collected and analyzed in video streaming analytics to track user engagement and behavior on video streaming platforms, including metrics such as video views, play rate, and engagement. This data is used to gain insights into audience preferences and optimize content delivery, as well as to increase video views by serving the right content to the right audience through channel optimization and play rate optimization tactics.",
#     "Conversion Rates": "Conversion Rates are an important metric in video streaming analytics that can be optimized through tactics such as serving the right content to the right audience, play rate optimization strategies, and engagement optimization tactics. Leveraging machine learning and smart data can also contribute to improving conversion rates and increasing customer lifetime value.",
#     "Customer Lifetime Value": "Customer Lifetime Value (CLV) is a metric that measures the total value a customer brings to a business over their entire relationship. It can be optimized by leveraging video streaming analytics, machine learning, and smart data to enhance marketing effectiveness, improve conversion rates, and increase customer satisfaction and engagement.",
#     "CoTP": "Chain of Thought Prompting (CoTP) is a technique that can be applied to video streaming analytics to improve the accuracy and efficiency of data analysis. CoTP involves using a series of prompts or questions to guide the thought process of the analyst, helping them to explore different aspects of the data and uncover valuable insights. It can be implemented using various tools and techniques, such as data visualization, statistical analysis, and machine learning algorithms. By applying CoTP, organizations can make data-driven decisions and optimize their video streaming services.",
#     "Data Analysis": "Data analysis is a process that involves using prompts or questions, such as those in Chain of Thought Prompting (CoTP), to guide analysts in exploring different aspects of the data and uncovering valuable insights. CoTP can enhance the effectiveness of video streaming analytics by providing a structured approach to data analysis, helping analysts ask the right questions and make data-driven decisions.",
#     "Data Exploration": "Data Exploration is a crucial step in the application of Chain of Thought Prompting (CoTP) in video streaming analytics, as it involves using prompts or questions to guide analysts in exploring different aspects of the data and uncovering valuable insights. Analysts can use various tools and techniques, such as data visualization and statistical analysis, to answer the prompts and identify patterns, trends, and anomalies in the data. CoTP enhances the effectiveness of video streaming analytics by providing a structured approach to data analysis, enabling organizations to make data-driven decisions and optimize their services.",
#     "Hypothesis Testing": "Hypothesis testing is a statistical analysis technique that can be applied in video streaming analytics to validate findings and uncover valuable insights.",
#     "Data Visualization Tools": "Data Visualization Tools are used in the application of Chain of Thought Prompting (CoTP) in video streaming analytics to explore and analyze data visually. Analysts can use these tools to answer prompts and identify patterns, trends, and anomalies in the data, helping them uncover valuable insights and make data-driven decisions.",
#     "Statistical Analysis Techniques": "Statistical analysis techniques can be used in video streaming analytics to test hypotheses and validate findings, helping analysts explore data and uncover valuable insights.",
#     "Machine Learning Algorithms": "Machine Learning Algorithms can be applied in video streaming analytics to analyze large volumes of data and uncover hidden patterns, helping analysts to explore different aspects of the data and uncover valuable insights.",
#     "Patterns": "Patterns in video streaming analytics refer to trends, correlations, and recurring behaviors identified through the application of Chain of Thought Prompting (CoTP). CoTP involves using a series of prompts or questions to guide the thought process of the analyst, helping them to explore different aspects of the data and uncover valuable insights. These prompts can assist analysts in identifying patterns, trends, and anomalies in the data, guiding them to ask further questions and dig deeper into the data. By applying CoTP, organizations can make data-driven decisions and optimize their video streaming services.",
#     "Trends": "Trends in video streaming analytics can be identified and analyzed using the Chain of Thought Prompting (CoTP) technique, which involves using a series of prompts or questions to guide the thought process of analysts and help them explore different aspects of the data, including patterns, trends, and anomalies. CoTP can be implemented through various tools and techniques, such as data visualization, statistical analysis, and machine learning algorithms, to uncover valuable insights and optimize video streaming services.",
#     "Anomalies": "Anomalies in video streaming analytics can be identified through the application of Chain of Thought Prompting (CoTP), which involves using prompts or questions to guide analysts in exploring data and uncovering valuable insights.",
#     "Data-Driven Decisions": "Data-Driven Decisions involve using metrics and insights to optimize various aspects of video streaming analytics, such as engagement, impressions, play rate, and overall growth. It is important to measure and optimize all relevant metrics to achieve meaningful growth and compete in the long term. Chain of Thought Prompting (CoTP) is a technique that can be applied to video streaming analytics to improve the accuracy and efficiency of data analysis. CoTP involves using a series of prompts or questions to guide the thought process of the analyst, helping them to explore different aspects of the data and uncover valuable insights. By applying CoTP, organizations can make data-driven decisions and optimize their video streaming services.",
#     "Optimization": "Optimization is a process that can be enhanced by applying Chain of Thought Prompting (CoTP) in video streaming analytics. CoTP involves using prompts or questions to guide analysts in exploring different aspects of the data and uncovering valuable insights. It provides a structured approach to data analysis, helping analysts ask the right questions, identify patterns, and optimize video streaming services.",
#     "Video Streaming Services": "Video Streaming Services can benefit from the application of Chain of Thought Prompting (CoTP) in their analytics process, as it improves the accuracy and efficiency of data analysis. CoTP involves using prompts or questions to guide analysts in exploring different aspects of the data and uncovering valuable insights. By implementing CoTP, organizations can make data-driven decisions and optimize their video streaming services."
#   }
# print(tiktoken_len(json.dumps(TEST)))
# fil = get_filtered_entities(TEST, 2000, "How does chain of thought prompting work?")
# tiktoken_len(json.dumps(fil))
# #%%
# fil
# %%
