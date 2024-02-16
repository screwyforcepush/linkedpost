# LinkedPost
This notebook builds a knowledge base, brainstorms novel applications of knowledge, crafts a solution design with UML diagrams, generates a promotional social post and images.  
Some examples of the final output can be found [here](https://medium.com/@alexsavagedata)


## Features
This was project based learning across a variety of AI tech, which led me to experiment in some key areas.  


### AI Agent Workflow

1. Build Knowledge Base  
Document processing filters out documents that have been processed in the past:
* pdfs
* Queries arxiv, downloads papers, filters out papers not relevant to the namespace
* Scrapes github urls for .md files.
* Scrapes web urls for page content.
* Auto pull arxiv research papers that feature in "top papers of the week" github repo.
2. Brainstorms Applications of Knowledge to your domain of choice.  
Multiple brainstorming prompts for a diverse selection of ideas to choose from.  
Includes a web search flow to confirm ideas are novel.
3. Searches the web to accept or reject idea as novel.
3. Performs additional research around the selected idea
4. Creates a skeleton of the solution design
5. **Iteratively** researches and generates content for each section of the solution design.
6. Provides critical feedback on the solution design sections and holistically.
7. Additional research based on feedback.
8. **Iteratively** edits the solution design based on feedback and additional research.
9. Describes the system architecture through a UML diagram.
10. Generates some images and a promotional social post for the article.


**Workflow Object**
* All progress within the workflow is stored to disk.
* A workflow can be stopped and resumed later
* A workflow object can be edited manually the change trajectory of the workflow.

### Memory

Multiple methods of utilising memory, implemented as a waterfall in the following order:

**Entities DB**
* Cheapest, fastest, shared between all agents
* Contains an updated list of defined Entities.
* New entities are added and existing are updated as new research is processed
* Relevant entities costed, stack ranked, and budgeted for Agent context  


**Knowledge summaries**
* Cheap and fast, accessible by research and brainstorming agents.
* Used before raw knowledge RAG
* Informs RAG queries for deep dives, and supplemental research.  


**RAG**
* Costly workflow, used last, and only by research Agent.
* For the raw source knowledge.
* This proves useful for supplementing solution research but needs a larger workflow to achieve quality results.
* Multi query. When using RAG, multiple versions of the similarity search query are generated to pull in a more diverse result set.
* Document sorting so that the most relevant RAG docs are supplied as context
* Document compression to reduce the tokens of documents supplied to the research Agent  


## How to use

Install requirements.txt  
You will need some API keys for the system to function. Set them as environment variables

### Set your environment Variables

* OPENAI_API_KEY

**Vector DB**
* PINECONE_API_KEY
* PINECONE_ENV

**Required for github scraping**  
* DIFFBOT_API_KEY

**Required for web scraping**  
* OOGLE_CSE_ID  
* GOOGLE_API_KEY  

### Add Knowledge

**./input_knowledge is used to build the the vector db knowledge base**  
* drop in pdfs
* list of arxiv_queries that will be used to pull relevant papers
* list git_urls to scrape for .md files
* list website urls to scrape

### Vectorise Knowledge
Run document_processing.py to chunk and vectorise of all input_knowledge.  
**Document vectors are stored in the pinecone DB within the namespace. Namespace is a variable you can set for each document type, and change between runs as needed.**  


### Generate content
**Run conductor.py, your article, images, and social post will be generated and stored in /content**

Variables of note are set in the execution section down the bottom of the monolithic file. I know, it needs a refactor...
* domain: The domain you would like the knowledge to be applied to
* CONTENT_PERSONA:The persona prompt that will craft the content, impacting style
* edit_instruction: Additional instructions for the final edit of the content
* HUMAN_CHOOSE_IDEA: if you want to choose the content idea or you want the AI to judge and select the idea.
* max_iterations: this is set in a couple of functions to limit the iterations of the AI agent.
* CONDUCTOR_KEY: This key is generated each workflow. A workflow can be stopped and resumed later by using the function set_key_load_vars(key="your workflow key")

