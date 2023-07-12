import pinecone
import os
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI

from langchain.vectorstores import Pinecone
from langchain.llms import OpenAI
from langchain.document_transformers import EmbeddingsRedundantFilter,EmbeddingsClusteringFilter
from langchain.retrievers.document_compressors import DocumentCompressorPipeline
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.merger_retriever import MergerRetriever
from custom.multi_query import MultiQueryRetriever

import tiktoken
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")

openai = OpenAI(
    model_name="text-davinci-003",
    openai_api_key=OPENAI_API_KEY
)
llm = ChatOpenAI(temperature=0)
import logging
logging.basicConfig()
logging.getLogger('custom.multi_query').setLevel(logging.INFO)
pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENV"))
index_name = "langchain-demo"
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
filter = EmbeddingsRedundantFilter(embeddings=embeddings)

# This filter will divide the documents vectors into clusters or "centers" of meaning.
# Then it will pick the closest document to that center for the final results.
# By default the result document will be ordered/grouped by clusters.
filter_ordered_cluster = EmbeddingsClusteringFilter(
            embeddings=embeddings,
            num_clusters=10,
            num_closest=1,
        )

pipeline = DocumentCompressorPipeline(transformers=[filter_ordered_cluster])



from typing import List
from langchain import LLMChain
from pydantic import BaseModel, Field
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser  
#%% 
tokenizer = tiktoken.get_encoding("cl100k_base")
# create the length function
def tiktoken_len(text:str):
    tokens = tokenizer.encode(text, disallowed_special=())
    return len(tokens)

max_doc_content_tokens=2000
def get_docs_content(docs):
    joined_content = ""
    temp_joined = ""
    docs_page_content = []
    for d in docs:
        docs_page_content.append(d.page_content)
        temp_joined = "\n".join(docs_page_content)
        if tiktoken_len(temp_joined)>max_doc_content_tokens:
            break
        joined_content = "\n".join(docs_page_content)
    print("max tokens reached ->",tiktoken_len(joined_content),tiktoken_len(temp_joined))
    return joined_content

def get_content_from_db(namespace, db_query, entities={}, k=20):
    db = Pinecone.from_existing_index(index_name, embeddings, namespace=namespace)
    # Define 2 diff retrievers with 2 diff embeddings and diff search type.
    retriever_all = db.as_retriever(
        search_type="similarity", search_kwargs={"k": k}
    )
    retriever_multi_qa = db.as_retriever(
        search_type="mmr", search_kwargs={"k": k}
    )
    # The Lord of the Retrievers will hold the ouput of boths retrievers and can be used as any other
    # retriever on different types of chains.
    lotr = MergerRetriever(retrievers=[retriever_all, retriever_multi_qa])

    retriever_from_llm = MultiQueryRetriever.from_llm(retriever=lotr,llm=llm,entities=entities)
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=pipeline, base_retriever=retriever_from_llm)
    docs = compression_retriever.get_relevant_documents(db_query)
    return get_docs_content(docs)


# %%
#TODO TRIM ENTITIES function TO MOST RELEVANT for query BEFORE SENDING THEM.
#TODO function needs to be used also for get final answer,
# #get final answer should be used for question like    "question": "What are the benefits and challenges of applying Chain of Thought Prompting to video streaming analytics?",

TEST = {
    "Chain of Thought": "Chain of Thought is a prompt implemented using language models to enable complex reasoning, which involves sequentially exploring different lines of reasoning to arrive at a solution and can be used in conjunction with the tree-of-thought prompting technique to guide the thought process and reasoning behind answering a question or solving a problem.",
    "Chain of Thought Prompting": "Chain of Thought Prompting (CoTP) is a technique that can be applied to video streaming analytics to improve the accuracy and efficiency of data analysis. CoTP involves using a series of prompts or questions to guide the thought process of the analyst, helping them to explore different aspects of the data and uncover valuable insights. It can be implemented using various tools and techniques, such as data visualization, statistical analysis, and machine learning algorithms. By applying CoTP, organizations can make data-driven decisions and optimize their video streaming services.",
    "Video Streaming Analytics": "Video Streaming Analytics involves tracking and analyzing user engagement and behavior on video streaming platforms, collecting data on metrics such as video views, play rate, and engagement to gain insights into audience preferences and optimize content delivery. It also includes tactics for increasing video views, such as optimizing impressions through channel selection, and strategies for play rate and engagement optimization, such as autoplay, clear copy, custom thumbnails, trimming intros, adding subtitles, and incorporating interactivity. Additionally, Chain of Thought Prompting (CoTP) can be applied to video streaming analytics to improve the accuracy and efficiency of data analysis. CoTP involves using a series of prompts or questions to guide the thought process of the analyst, helping them to explore different aspects of the data and uncover valuable insights.",
    "Language Models": "Language models are improved using the Chain of Thought prompting technique, which involves providing prompts or cues in the form of sentences or questions to guide the model's thinking process and generate coherent and relevant text. The effectiveness of Chain of Thought Prompting can be evaluated by measuring the accuracy of the generated text through metrics such as accuracy or similarity.",
    "Accuracy": "Accuracy is a measure used to evaluate the effectiveness of Chain of Thought Prompting in generating text with different levels of complexity and specificity. It involves comparing the generated text with a reference or ground truth text and calculating metrics such as accuracy or similarity.",
    "Similarity": "Similarity is a metric that can be used to evaluate the effectiveness of Chain of Thought Prompting in generating text by comparing the generated text with a reference or ground truth text.",
    "ML": "ML, or machine learning, can be utilized in video streaming analytics to attract, acquire, and retain subscribers in over-the-top (OTT) video services. ML enables personalized recommendations based on user consumption habits, predicts user behavior, and optimizes marketing activities, customer acquisition, retention, and engagement.",
    "AI": "AI research at Microsoft focuses on developing and improving artificial intelligence technologies, particularly in the areas of code generation, language understanding, and video streaming analytics. They are involved in evaluating AI models for code suggestions, training language models to follow human instructions, and utilizing machine learning and smart data to optimize user engagement and behavior on video streaming platforms.",
    "OTT": "OTT (Over-the-Top) services can utilize video streaming analytics, machine learning, and smart data to optimize various aspects of their video service, including content discovery, acquisition, engagement, monetization, and churn analysis. By leveraging data effectively, businesses can enhance their marketing effectiveness, improve conversion rates, and increase customer lifetime value.",
    "Content Discovery": "Content Discovery is a process in video streaming analytics that involves optimizing impressions through selecting channels that align with the behaviors of the target audience, using tactics such as autoplay, clear and concise copy, custom thumbnails, trimming the intro, adding subtitles, and incorporating interactivity to improve engagement levels and capture and retain the audience's attention.",
    "Acquisition": "Acquisition in the context of video streaming analytics involves utilizing machine learning and smart data to attract, acquire, and retain subscribers in over-the-top (OTT) video services. ML and AI enable personalized recommendations based on user consumption habits, increasing user satisfaction and engagement. ML models can also predict user behavior, such as identifying potential paying customers and predicting churn, which can be used to optimize marketing activities, customer acquisition, retention, and engagement.",
    "Engagement": "Engagement optimization in video streaming involves tactics such as trimming the intro, adding subtitles, and incorporating interactivity to enhance engagement levels and capture and retain the audience's attention.",
    "Monetization": "Monetization in video streaming involves optimizing impressions through selecting channels that align with the behaviors of the target audience, using tactics such as autoplay, clear copy, custom thumbnails, and engagement optimization strategies to improve content experience and encourage viewer engagement.",
    "Churn Analysis": "Churn analysis involves using machine learning models to predict user behavior, such as identifying potential paying customers and predicting churn, in order to optimize marketing activities, customer acquisition, retention, and engagement in video streaming platforms.",
    "User Engagement": "User Engagement is the process of tracking and analyzing metrics such as video views, play rate, and engagement on video streaming platforms to gain insights into audience preferences and optimize content delivery. Tactics such as optimizing impressions, play rate, and engagement can be employed to increase user engagement. Machine learning and smart data can also be utilized to attract, acquire, and retain subscribers in video streaming services.",
    "Behavior": "Behavior refers to the actions and engagement of users on video streaming platforms, which can be tracked and analyzed through video streaming analytics. By collecting data on metrics such as video views, play rate, and engagement, businesses can gain insights into audience preferences and optimize content delivery. Tactics such as optimizing impressions, play rate, and engagement can be employed to increase video views and improve the content experience. Machine learning and smart data can also be utilized to personalize recommendations and predict user behavior, enabling businesses to optimize marketing activities, customer acquisition, retention, and engagement in the context of video streaming services.",
    "Video Views": "Video Views are a metric that can be tracked using online video platforms or native social platforms, and optimizing them involves serving the right content to the right audience, using tactics such as optimizing impressions, play rate, and engagement. It is important to measure and optimize all metrics related to views, not just video views, to see meaningful growth. Video views measure how many times a video is played, indicating that a play request was sent to the player and the video started playing. Video views are important for product managers and engineers to track. Additionally, video streaming analytics involves collecting data on metrics such as video views, play rate, and engagement to gain insights into audience preferences and optimize content delivery.",
    "Play Rate": "Play Rate optimization involves tactics such as setting landing page videos to autoplay, using clear and concise copy, and creating custom thumbnails to improve the content experience and encourage viewers to engage with the video.",
    "Impressions": "Impressions are important for optimizing video views by selecting channels that align with the behaviors of the target audience, such as high-volume, low-intent channels for awareness goals and low-volume, high-intent channels like email for bottom-of-funnel content.",
    "Channels": "Channels play a crucial role in video streaming analytics, as optimizing impressions and play rate involves selecting channels that align with the behaviors of the target audience, such as high-volume, low-intent channels for awareness goals, medium-volume, medium-intent channels for consideration stage targeting, and low-volume, high-intent channels like email for bottom-of-funnel content.",
    "Awareness Goals": "Awareness goals in video streaming analytics involve optimizing impressions through selecting channels that align with the behaviors of the target audience, with high-volume, low-intent channels being suitable for this purpose.",
    "Consideration Stage Targeting": "Consideration Stage Targeting is a strategy in video streaming analytics that involves selecting medium-volume, medium-intent channels to serve content to the target audience, with the goal of optimizing engagement and encouraging viewers to consider the content further.",
    "Bottom-of-Funnel Content": "Bottom-of-Funnel Content refers to content that is effective for low-volume, high-intent channels like email in video streaming analytics. It aims to engage viewers and encourage them to take action, such as making a purchase or subscribing to a service.",
    "Email": "Email is a low-volume, high-intent channel that is effective for bottom-of-funnel content in video streaming analytics.",
    "Landing Page Videos": "Landing page videos can be optimized for play rate by setting them to autoplay, using clear copy, creating custom thumbnails, and benchmarking play rates by video location before making changes to campaign messaging. These strategies aim to improve the content experience and encourage viewers to engage with the video.",
    "Autoplay": "Autoplay is an optimization technique in video streaming analytics that involves setting landing page videos to autoplay, using clear copy, and creating custom thumbnails to improve play rate and overall engagement. It is a tactic used to improve the content experience and encourage viewers to engage with the video.",
    "Copy": "Copy involves tactics such as setting landing page videos to autoplay, using clear and concise copy, and creating custom thumbnails to improve the content experience and encourage viewers to engage with the video.",
    "Custom Thumbnails": "Custom thumbnails are an important aspect of play rate optimization in video streaming analytics, along with setting landing page videos to autoplay and using clear copy. These strategies aim to improve the content experience and encourage viewers to engage with the video.",
    "Social Engagement Optimization": "Social Engagement Optimization involves tactics such as trimming the intro, adding subtitles, and incorporating interactivity to enhance engagement levels in video streaming.",
    "Intro Trimming": "Intro Trimming is a tactic used in video streaming analytics to enhance engagement levels by trimming the introduction of videos.",
    "Subtitles": "Subtitles can be added to videos as a way to optimize engagement and increase viewer retention, along with other tactics such as trimming the intro and considering interactivity. They are one of the strategies used in engagement optimization in video streaming, aiming to capture and retain the audience's attention.",
    "Interactivity": "Interactivity in video streaming analytics involves incorporating features such as trimming the intro, adding subtitles, and providing interactive elements in videos to enhance engagement levels and capture the audience's attention.",
    "Machine Learning": "Machine Learning (ML) is a technology that can be utilized in video streaming analytics to optimize various aspects of an OTT video service, including content discovery, acquisition, engagement, monetization, and churn analysis. ML enables personalized recommendations based on user consumption habits, predicts user behavior, and can be used to optimize marketing activities, customer acquisition, retention, and engagement.",
    "Smart Data": "Smart Data is a term used in the context of video streaming analytics and machine learning (ML) to refer to the utilization of data collected on metrics such as video views, play rate, and engagement to gain insights into audience preferences and optimize content delivery.",
    "Personalized Recommendations": "Personalized Recommendations in video streaming analytics involve utilizing machine learning and smart data to provide tailored content suggestions based on user consumption habits, increasing user satisfaction and engagement. ML models can also predict user behavior, such as identifying potential paying customers and predicting churn, enabling businesses to optimize marketing activities, customer acquisition, retention, and engagement.",
    "User Satisfaction": "User Satisfaction in video streaming analytics can be improved through tactics such as optimizing impressions, play rate, and engagement. Machine learning and smart data can also be utilized to personalize recommendations and predict user behavior, leading to increased satisfaction and engagement.",
    "User Behavior": "User Behavior refers to the actions and preferences exhibited by individuals while engaging with video streaming platforms. It involves tracking and analyzing metrics such as video views, play rate, and engagement to gain insights into audience preferences and optimize content delivery. Tactics such as optimizing impressions, play rate, and engagement can be employed to increase video views and enhance user engagement. Machine learning and smart data can also be utilized to attract, acquire, and retain subscribers, as well as predict user behavior for optimization purposes.",
    "Paying Customers": "Paying customers can be identified and predicted using machine learning models based on user behavior, which can help optimize marketing activities, customer acquisition, retention, and engagement in video streaming platforms.",
    "Predicting Churn": "Predicting churn involves using machine learning models to identify potential paying customers and predict customer behavior in order to optimize marketing activities, customer acquisition, retention, and engagement.",
    "Marketing Activities": "Marketing activities involve optimizing impressions through selecting channels that align with the behaviors of the target audience, utilizing tactics such as play rate optimization and engagement optimization to improve content experience and encourage viewer engagement, and leveraging machine learning and smart data to attract, acquire, and retain subscribers in video streaming platforms.",
    "Customer Acquisition": "Customer Acquisition involves optimizing impressions through selecting channels that align with the behaviors of the target audience, such as high-volume, low-intent channels for awareness goals and low-volume, high-intent channels like email for bottom-of-funnel content. Play rate optimization and engagement optimization strategies can also be employed to improve content experience and capture audience attention. Additionally, machine learning and smart data can be utilized to attract, acquire, and retain subscribers in video streaming services.",
    "Retention": "Retention is an important aspect of video streaming analytics, as it involves strategies to attract, acquire, and retain subscribers in over-the-top (OTT) video services. Machine learning (ML) and smart data can be utilized to optimize retention by predicting user behavior, identifying potential paying customers, and optimizing marketing activities.",
    "Data": "Data is collected and analyzed in video streaming analytics to track user engagement and behavior on video streaming platforms, including metrics such as video views, play rate, and engagement. This data is used to gain insights into audience preferences and optimize content delivery, as well as to increase video views by serving the right content to the right audience through channel optimization and play rate optimization tactics.",
    "Conversion Rates": "Conversion Rates are an important metric in video streaming analytics that can be optimized through tactics such as serving the right content to the right audience, play rate optimization strategies, and engagement optimization tactics. Leveraging machine learning and smart data can also contribute to improving conversion rates and increasing customer lifetime value.",
    "Customer Lifetime Value": "Customer Lifetime Value (CLV) is a metric that measures the total value a customer brings to a business over their entire relationship. It can be optimized by leveraging video streaming analytics, machine learning, and smart data to enhance marketing effectiveness, improve conversion rates, and increase customer satisfaction and engagement.",
    "CoTP": "Chain of Thought Prompting (CoTP) is a technique that can be applied to video streaming analytics to improve the accuracy and efficiency of data analysis. CoTP involves using a series of prompts or questions to guide the thought process of the analyst, helping them to explore different aspects of the data and uncover valuable insights. It can be implemented using various tools and techniques, such as data visualization, statistical analysis, and machine learning algorithms. By applying CoTP, organizations can make data-driven decisions and optimize their video streaming services.",
    "Data Analysis": "Data analysis is a process that involves using prompts or questions, such as those in Chain of Thought Prompting (CoTP), to guide analysts in exploring different aspects of the data and uncovering valuable insights. CoTP can enhance the effectiveness of video streaming analytics by providing a structured approach to data analysis, helping analysts ask the right questions and make data-driven decisions.",
    "Data Exploration": "Data Exploration is a crucial step in the application of Chain of Thought Prompting (CoTP) in video streaming analytics, as it involves using prompts or questions to guide analysts in exploring different aspects of the data and uncovering valuable insights. Analysts can use various tools and techniques, such as data visualization and statistical analysis, to answer the prompts and identify patterns, trends, and anomalies in the data. CoTP enhances the effectiveness of video streaming analytics by providing a structured approach to data analysis, enabling organizations to make data-driven decisions and optimize their services.",
    "Hypothesis Testing": "Hypothesis testing is a statistical analysis technique that can be applied in video streaming analytics to validate findings and uncover valuable insights.",
    "Data Visualization Tools": "Data Visualization Tools are used in the application of Chain of Thought Prompting (CoTP) in video streaming analytics to explore and analyze data visually. Analysts can use these tools to answer prompts and identify patterns, trends, and anomalies in the data, helping them uncover valuable insights and make data-driven decisions.",
    "Statistical Analysis Techniques": "Statistical analysis techniques can be used in video streaming analytics to test hypotheses and validate findings, helping analysts explore data and uncover valuable insights.",
    "Machine Learning Algorithms": "Machine Learning Algorithms can be applied in video streaming analytics to analyze large volumes of data and uncover hidden patterns, helping analysts to explore different aspects of the data and uncover valuable insights.",
    "Patterns": "Patterns in video streaming analytics refer to trends, correlations, and recurring behaviors identified through the application of Chain of Thought Prompting (CoTP). CoTP involves using a series of prompts or questions to guide the thought process of the analyst, helping them to explore different aspects of the data and uncover valuable insights. These prompts can assist analysts in identifying patterns, trends, and anomalies in the data, guiding them to ask further questions and dig deeper into the data. By applying CoTP, organizations can make data-driven decisions and optimize their video streaming services.",
    "Trends": "Trends in video streaming analytics can be identified and analyzed using the Chain of Thought Prompting (CoTP) technique, which involves using a series of prompts or questions to guide the thought process of analysts and help them explore different aspects of the data, including patterns, trends, and anomalies. CoTP can be implemented through various tools and techniques, such as data visualization, statistical analysis, and machine learning algorithms, to uncover valuable insights and optimize video streaming services.",
    "Anomalies": "Anomalies in video streaming analytics can be identified through the application of Chain of Thought Prompting (CoTP), which involves using prompts or questions to guide analysts in exploring data and uncovering valuable insights.",
    "Data-Driven Decisions": "Data-Driven Decisions involve using metrics and insights to optimize various aspects of video streaming analytics, such as engagement, impressions, play rate, and overall growth. It is important to measure and optimize all relevant metrics to achieve meaningful growth and compete in the long term. Chain of Thought Prompting (CoTP) is a technique that can be applied to video streaming analytics to improve the accuracy and efficiency of data analysis. CoTP involves using a series of prompts or questions to guide the thought process of the analyst, helping them to explore different aspects of the data and uncover valuable insights. By applying CoTP, organizations can make data-driven decisions and optimize their video streaming services.",
    "Optimization": "Optimization is a process that can be enhanced by applying Chain of Thought Prompting (CoTP) in video streaming analytics. CoTP involves using prompts or questions to guide analysts in exploring different aspects of the data and uncovering valuable insights. It provides a structured approach to data analysis, helping analysts ask the right questions, identify patterns, and optimize video streaming services.",
    "Video Streaming Services": "Video Streaming Services can benefit from the application of Chain of Thought Prompting (CoTP) in their analytics process, as it improves the accuracy and efficiency of data analysis. CoTP involves using prompts or questions to guide analysts in exploring different aspects of the data and uncovering valuable insights. By implementing CoTP, organizations can make data-driven decisions and optimize their video streaming services."
  }
tiktoken_len(TEST)
# %%
