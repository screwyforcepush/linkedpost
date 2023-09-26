# %%
from langchain.prompts.prompt import PromptTemplate
import graphviz
import openai
ARCHITECTURE_GUIDE_TEMPLATE = """
System {{
    You are a seasoned System Analysts with expertise in translating descriptive Solution Designs into a well structured System Context.
    Analyze the Solution Design, which utilises the latest advancements in AI research to address a business need.
    Your task is to dissect the Solution Design meticulously, to create a System Context in accordance with the Guidlines provided.
    This information will serve as the foundation for creating a System Context Diagram visualization.
}}

Guidelines {{
    Identification of Primary System:
        Clear depiction of the system under discussion.
        Definition and demarcation of system boundaries to indicate what is inside and outside of the system.
    External Entities:
        Identification of external entities interacting with the system, which could be individuals, organizations, or other systems.
        Clear labeling of external entities to facilitate understanding.
    Interfaces and Interactions:
        Description of the nature of interactions between the system and external entities.
        Indication of data flow or information exchange points.
    Clarity and Simplicity:
        Avoidance of overly complex representations.
        Use of clear and simple notation to make the diagram easily understandable.
    Data Flow and Information Channels:
        Indication of the direction of data or information flow between the system and external entities.
        Representation of different kinds of data flows (if any) using distinct notations or legends.
}}

Solution Design {{
    {doc_source}
}}
"""

ARCHITECTURE_GUIDE_PROMPT = PromptTemplate(
    input_variables=["doc_source"], template=ARCHITECTURE_GUIDE_TEMPLATE
)


ARCHITECTURE_GUIDE_CRITIC_TEMPLATE = """
System {{
    You are the System Context Critic. Your expertise is evaluating how accurately and thoroughly a Proposed System Context represents the Solution Design.
    You give detailed constructive Feedback enabling itterative emprovement.
}}

Solution Design {{
    {doc_source}
}}

Proposed System Context {{
    {guidance}
}}

Feedback:
"""

ARCHITECTURE_GUIDE_CRITIC_PROMPT = PromptTemplate(
    input_variables=["doc_source","guidance"], template=ARCHITECTURE_GUIDE_CRITIC_TEMPLATE
)

ARCHITECTURE_GUIDE_ITTERATION_TEMPLATE = """
System{{
    You are the Solution Architect. You skilled at analysing a list of Attempted System Context and corresponding Feedback, and creating the Final System Context.
    You adhear to standards and guidelines for creating System Context Diagrams.
    Your Final System Context is the last itteration before being transformed into a System Context Diagram visualization.
}}

Attempts {{
    {arch_list}
}}

Final System Context:
"""

ARCHITECTURE_GUIDE_ITTERATION_PROMPT = PromptTemplate(
    input_variables=["arch_list"], template=ARCHITECTURE_GUIDE_ITTERATION_TEMPLATE
)

ARCHITECTURE_SCRIPT_TEMPLATE = """
System{{
    You are a seasoned Python programmer with expertise in generating visually appealing System Context Diagrams using the 'diagrams' library.
    Analyze the System Context, which focuses on using AI to address a business need.
    Your mission is to create a Python script that, when executed, autonomously craft a detailed and aesthetically appealing System Context Diagram representing the System Context.
    You Python script adhears to the *Script Requirements*, and the resulting Diagram image meets the *Diagram Requirements*.
}} 

Diagram Requirements {{
The generated image named "sol_arch" is 1920 x 1080 pixels.

Identification of Primary System:
    Clear depiction of the system under discussion.
    Definition and demarcation of system boundaries to indicate what is inside and outside of the system.
External Entities:
    Identification of external entities interacting with the system, which could be individuals, organizations, or other systems.
    Clear labeling of external entities to facilitate understanding.
Interfaces and Interactions:
    Description of the nature of interactions between the system and external entities.
    Indication of data flow or information exchange points.
Clarity and Simplicity:
    Avoidance of overly complex representations.
    Use of clear and simple notation to make the diagram easily understandable.
Data Flow and Information Channels:
    Indication of the direction of data or information flow between the system and external entities.
    Representation of different kinds of data flows (if any) using distinct notations or legends.
Legend and Notations:
    Inclusion of a legend to explain symbols, notations, or abbreviations used in the diagram.
    Consistency in the use of symbols and notations throughout the diagram. 
Visual Appeal:
    Utilizing appropriate visual design principles to make the diagram aesthetically appealing.
    Ensuring that the diagram is neatly organized to avoid visual clutter.
Title and Identification:
    Including a descriptive title that clearly indicates what the diagram represents.
    Adding necessary identification information like version number, date of creation, and author details.
}}

Script Requirements{{
    Imports from "diagram" must exist in the "Diagram as Code" documentation. Refer to 'Diagram Modules'.
    The script must be ready-to-use without requiring any manual review or modifications.  
}}

Diagram Modules {{
    {diagram_modules}
}}

System Context {{
    {architecture_final}
}}

```python
"""

ARCHITECTURE_SCRIPT_PROMPT = PromptTemplate(
    input_variables=["architecture_final","diagram_modules"], template=ARCHITECTURE_SCRIPT_TEMPLATE
)

CODE_REVIEW_TEMPLATE = """
System{{
    You are a seasoned Python engineer with expertise in generating visually appealing System Context Diagrams using the 'diagrams' library.
    You review code and suggest improvements. You pay special attention to appropriate icon usage, syntax, and *all* Requirements are met.
    Suggest an alternate icon or basic shape when there are missing icons in 'diagrams'.
}} 

Diagram Requirements {{
The generated image named "sol_arch" is 1920 x 1080 pixels.

Identification of Primary System:
    Clear depiction of the system under discussion.
    Definition and demarcation of system boundaries to indicate what is inside and outside of the system.
External Entities:
    Identification of external entities interacting with the system, which could be individuals, organizations, or other systems.
    Clear labeling of external entities to facilitate understanding.
Interfaces and Interactions:
    Description of the nature of interactions between the system and external entities.
    Indication of data flow or information exchange points.
Clarity and Simplicity:
    Avoidance of overly complex representations.
    Use of clear and simple notation to make the diagram easily understandable.
Data Flow and Information Channels:
    Indication of the direction of data or information flow between the system and external entities.
    Representation of different kinds of data flows (if any) using distinct notations or legends.
Legend and Notations:
    Inclusion of a legend to explain symbols, notations, or abbreviations used in the diagram.
    Consistency in the use of symbols and notations throughout the diagram. 
Visual Appeal:
    Utilizing appropriate visual design principles to make the diagram aesthetically appealing.
    Ensuring that the diagram is neatly organized to avoid visual clutter.
Title and Identification:
    Including a descriptive title that clearly indicates what the diagram represents.
    Adding necessary identification information like version number, date of creation, and author details.
}}

Script Requirements{{
    Imports from "diagram" must exist in the "Diagram as Code" documentation. Refer to 'Diagram Modules'.
    The script must be ready-to-use without requiring any manual review or modifications.  
}}

Diagram Modules {{
    {diagram_modules}
}}

Compiler Result {{
    {modules_check}
    {compiler_check}
}}

Code to Review {{
    {architecture_diagram_script}
}}

Suggestions:
"""

CODE_REVIEW_PROMPT = PromptTemplate(
    input_variables=["diagram_modules","architecture_diagram_script","modules_check","compiler_check"], template=CODE_REVIEW_TEMPLATE
)

DIAGRAM_DESIGNER_TEMPLATE = """
System{{
    You are the Beauty Engineer. You are uniquely skilled at percieving the visual output of Python 'diagrams' Code.
    You create a clear and specific Style Guide for the engineer, that once implemented, will pleasently style the diagram into a visually appealing masterpiece.
    THe final diagram using your Style Guide can be interpreted with a single glance, and hooks the viewer immediatly. 
    You adhere to Best Practices when creating your Style Guide, and *always* provide exact colors, weights, positioning and more!
}} 

Best Practices {{
Color Scheme:
    Background: As shown above, use attributes like background to set a neutral background color.
    Entities/Systems: Use distinct, complementary colors to differentiate between various entities or systems. Assign colors using node attributes.
    Data Flow: Use different shades to represent data flows. This might involve using different types of connectors or labels to indicate different data flows.
Shapes and Icons:
    Systems: Use appropriate icons or shapes to represent systems/entities (usually, the built-in icons in the diagrams module denote systems adequately).
    External Entities: Represent external entities with different icons or shapes to distinguish them from internal systems.
    Data Stores: Utilize appropriate icons or shapes (like cylinders) to denote databases or data stores.
    Consistency: Maintain consistency in the representation of similar entities or processes throughout the diagram.
Lines and Arrows:
    Direction: Use connectors with arrows to indicate the direction of data flow.
    Thickness: Adjust the thickness of lines (if the feature is available in the module) to represent the volume or importance of the data flow.
    Style: Differentiate between types of data flows using various line styles like dashed or solid lines.
Layout:
    Spacing: Manually organize the nodes to ensure sufficient spacing between elements, avoiding clutter.
    Alignment: Align elements neatly, possibly by organizing them within clusters or using attributes to set positions.
    Flow: Arrange components logically, either from top to bottom or left to right, based on the system's nature.

Implementing the Diagram
    Defining Nodes and Clusters:
    Define nodes using appropriate classes from the module and group related nodes within clusters for better organization and alignment.
    Connecting Nodes:
    Connect nodes using connectors that adhere to the guidelines mentioned in "Lines and Arrows".
}}

Code {{
    {architecture_diagram_script}
}}

Style Guide:
"""

DIAGRAM_DESIGNER_PROMPT = PromptTemplate(
    input_variables=["architecture_diagram_script"], template=DIAGRAM_DESIGNER_TEMPLATE
)

ARCHITECTURE_SCRIPT_PROMPT = PromptTemplate(
    input_variables=["architecture_final","diagram_modules"], template=ARCHITECTURE_SCRIPT_TEMPLATE
)

CODE_FEEDBACK_IMPLIMENTATION_TEMPLATE = """
System{{
    You are a seasoned Python engineer with expertise in generating visually appealing System Context Diagrams using the 'diagrams' module.
    A Python Script has been developed to generate the SCD based on the System Context.
    Your mission is to modify the Python Script that, when executed, autonomously craft a detailed and aesthetically appealing System Context Diagram representing the System Context.
    You apply the feasible Designer Feedback and Code Review to generate a script ready for *production release*. 
    You Python script adhears to the *Script Requirements*, and the resulting Diagram image meets the *Diagram Requirements*.
    Use a basic shape when there is no appropriate icon name to import from 'diagrams'.
}} 

Diagram Requirements {{
    The generated image named "sol_arch" is 1920 x 1080 pixels.
    Minimise Overlapping lines.
    No text overflow
}}

Script Requirements{{
    Imports from "diagram" must exist in the "Diagram as Code" documentation.
    The script must be ready-to-use without requiring any manual review or modifications.
    Your response is *only the script*.

}}

System Context {{
    {architecture_final}
}}

Python Script {{
    {architecture_diagram_script}
}}

Code Review {{
    {code_review}
}}

Designer Feedback {{
    {style_guide}
}}

```python
"""

CODE_FEEDBACK_IMPLIMENTATION_PROMPT = PromptTemplate(
    input_variables=["architecture_final","architecture_diagram_script","code_review","style_guide"], template=CODE_FEEDBACK_IMPLIMENTATION_TEMPLATE
)

CODE_FIX_TEMPLATE = """
System{{
    You are Python Script Fix. You have extensive knowledge and experience with the 'diagrams' library.
    A Python Script has been developed to generate an SDC but it has Errors.
    You only modify the Python Script to address the Errors. You make no other changes and only respond with the Modified Script.
    Use an alternate icon or basic shape when there are missing icons in 'diagrams'.
}} 

Python Script {{
    {architecture_diagram_script}
}}

Errors {{
    {modules_check}
    {compiler_check}
}}

ScriptFix()
```python
"""

CODE_FIX_PROMPT = PromptTemplate(
    input_variables=["architecture_diagram_script","modules_check","compiler_check"], template=CODE_FIX_TEMPLATE
)
# %%
doc_source ="""
Personalized Content Discovery Engine Leveraging Length-Extrapolatable Transformer and Retentive Network\n# Introduction\n\nWelcome to the future of OTT video streaming, where the paradox of choice is a thing of the past. With the explosion of content available on OTT platforms, it\'s easy for users to feel overwhelmed. But what if we could transform this vast ocean of content into a personalized stream, tailored to each user\'s unique tastes and preferences? That\'s exactly what we\'re aiming to do with our latest innovation: a personalized content discovery engine leveraging Length-Extrapolatable Transformer and Retentive Network.\n\nThe concept might sound like a mouthful, but let\'s break it down. The Length-Extrapolatable Transformer is a powerful tool that can handle longer sequences of data, making it perfect for processing vast amounts of user data. This includes watched history, search queries, and interaction patterns. By analyzing this data, the transformer can understand individual user preferences, paving the way for personalized content recommendations.\n\nOn the other hand, the Retentive Network is a marvel in its own right. Its ability to retain more information from the input means it can remember users\' past preferences. This is crucial in the context of evolving tastes over time, allowing the network to make highly relevant recommendations even as users\' preferences change.\n\nThe combination of these two technologies promises to revolutionize the way users discover content on OTT platforms. But don\'t just take my word for it. This concept is backed by cutting-edge research, including "Learning to Reason and Memorize with Self-Notes" by Jack Lanchantin et al. [^1^] and "Retentive Network: A Successor to Transformer for Large Language Models" by Yutao Sun et al. [^2^].\n\nIn the following sections, we\'ll delve deeper into the intricacies of data management, integration and scalability, evaluation and metrics, and the key technologies powering this innovation. So, grab a cup of tea (or coffee, if that\'s your poison) and join me on this journey into the future of OTT video streaming.\n\n[^1^]: Lanchantin, J., Toshniwal, S., Weston, J., Szlam, A., & Sukhbaatar, S. (2023). Learning to Reason and Memorize with Self-Notes. Retrieved from http://arxiv.org/abs/2305.00833v1\n[^2^]: Sun, Y., Dong, L., Huang, S., Ma, S., Xia, Y., Xue, J., Wang, J., & Wei, F. (2023). Retentive Network: A Successor to Transformer for Large Language Models. Retrieved from http://arxiv.org/abs/2307.08621v2\n# Data Management\n\nData management is the backbone of our personalized content discovery engine. It involves collecting, processing, and retaining user data to understand individual preferences and make relevant recommendations. Let\'s dive into each of these aspects.\n\n## Data Collection and Security\n\nThe first step in developing a personalized content discovery engine is to collect user data. This includes watched history, search queries, and interaction patterns. However, collecting user data is not just about gathering as much information as possible. It\'s about respecting user privacy and ensuring data security.\n\nOur system employs robust data collection techniques, such as RandomHorizontalFlip, RandomErase, RandAugment, and Color Jitter Frequency masking, to enhance the quality and diversity of the collected data. It also combines disparate modalities, such as audio and video, to provide a richer set of data for the model to learn from. Joint embedding models like IMAGEBIND are used to enable cross-modal search and retrieval applications.\n\nBut what about data privacy and security? We\'ve got that covered too. Our system protects against poisoning attacks by identifying and removing training samples that significantly impact models. We also use privacy-enhancing techniques like differential privacy to reduce the impact of individual (poisoned) training samples. Robust techniques like Distributionally Robust Optimization (DRO) are employed to further enhance security.\n\n## Data Processing and User Understanding\n\nOnce we\'ve collected the data, it\'s time to process it. This is where the Length-Extrapolatable Transformer comes into play. It processes the collected user data into manageable chunks, similar to how YouTube video transcriptions are resampled into 3-minute parts in the research.\n\nOnce the data is processed, embeddings are generated for each chunk of data. These embeddings serve as a numerical representation of the user data that can be easily processed by the transformer. The generated embeddings are stored in a vector store, which serves as a database for the transformer to search through when making recommendations.\n\nThe stored embeddings are used to understand user preferences. This is done by searching the vector store for similar documents or chunks based on the embeddings. The results of this search provide insights into the user\'s preferences.\n\n## Data Retention\n\nRemembering previous interactions with users is crucial for making contextually relevant recommendations. That\'s why we\'ve implemented a memory system to remember previous interactions. This system, powered by the Retentive Network, retains important information over long sequences and remembers users\' past preferences.\n\nWe\'ve also implemented Chain of Thought Prompting to improve the reasoning and decision-making capabilities of the transformer. This technique helps the transformer make more accurate predictions about user preferences.\n\nIn conclusion, data management is a critical component of our personalized content discovery engine. By collecting, processing, and retaining user data, we can understand individual preferences and make highly relevant recommendations. But remember, this is just the beginning. The real magic happens when we integrate this engine with existing OTT platforms and scale it to accommodate a growing user base. But we\'ll save that for the next section. Stay tuned!\n# Integration and Scalability\n\nNow that we\'ve covered the data management aspect of our personalized content discovery engine, let\'s delve into the next critical phase: integration and scalability. This stage involves integrating our engine with existing OTT platforms and ensuring it can scale to accommodate a growing user base. \n\n## Platform Integration\n\nThe integration of our personalized content discovery engine with existing OTT platforms is a delicate process. It requires careful planning and execution to ensure that the integration does not disrupt existing services or succumb to competitive pressures that may lead to risky decisions. \n\nOur objective is clear: to enhance digital strategy and monetization by providing users with personalized content recommendations. To achieve this, we need to understand the collective impact of the Length-Extrapolatable Transformer and Retentive Network on the overall system. This includes understanding how these AI components interact with each other and with the existing systems on the OTT platform.\n\nWe believe in trustworthy and inclusive development. Our engine respects user privacy and provides personalized recommendations that cater to diverse user preferences. We also ensure that the integration of the content discovery engine with existing OTT platforms complies with relevant regulations. \n\nTo make the integration process smooth and efficient, we leverage advanced technologies and techniques, such as the Length-Extrapolatable Transformer and Retentive Network. These AI components are properly configured and optimized to work effectively with the existing systems on the OTT platform. We also utilize multi-fidelity modelling for efficient data processing. \n\n## Scalability and Resilience\n\nScalability and resilience are two critical factors that determine the success of our personalized content discovery engine in the long run. Our system is designed to handle a growing data and user base and provide consistent performance under high loads. \n\nWe\'ve built our system to be scalable from the ground up. As the amount of user data increases, our system can scale to accommodate this growth without compromising performance. This is achieved through the efficient parallelizable training of Transformers and the efficient inference of Recurrent Neural Networks (RNNs) in our Length-Extrapolatable Transformer and Retentive Network models.\n\nResilience is another key factor that we\'ve taken into account. Our system is designed to be robust and reliable, capable of handling high loads and recovering quickly from any potential failures. We\'ve implemented robust techniques like Distributionally Robust Optimization (DRO) to enhance the security and reliability of our system.\n\nIn conclusion, the integration and scalability phase is a critical step in the development of our personalized content discovery engine. By integrating our engine with existing OTT platforms and ensuring it can scale to accommodate a growing user base, we\'re setting the stage for a revolution in content discovery and user engagement. But the journey doesn\'t end here. In the next section, we\'ll delve into the evaluation and metrics tracking phase, where we\'ll discuss how we measure the success of our engine and continually improve it based on these metrics. Stay tuned!\n# Evaluation and Metrics\n\nAfter successfully integrating our personalized content discovery engine with existing OTT platforms and ensuring its scalability, the next crucial step is to evaluate its performance and track key metrics. This process allows us to measure the success of our engine, identify areas for improvement, and make data-driven decisions to continually enhance its performance.\n\n## Understanding and Utilizing Datasets\n\nOur evaluation process begins with a deep understanding of the datasets we use. One such dataset is the LVD-142M, a large corpus of data collected from 2 billion web pages, filtered to ensure quality and relevance. This dataset is used for training various models, particularly in the field of language and image processing. By understanding the structure and characteristics of this dataset, we can effectively train our models to generate highly relevant and personalized content recommendations.\n\n## Continual Model Performance Assessment\n\nWe believe in the power of continuous learning and improvement. To this end, we regularly assess the performance of our models and make necessary adjustments to improve their accuracy and reliability. Techniques like prompt engineering and prompt ensembles are employed to enhance the performance of our models. We also leverage advanced techniques like Chain of Thought prompting and Knowledge Augmentation to improve the reasoning and decision-making capabilities of our models.\n\n## Data Security Measures\n\nIn an era where data privacy and security are of paramount importance, we have implemented robust measures to protect user data. Techniques like Fully Homomorphic Encryption are used to perform computations on encrypted data without ever decrypting it, ensuring the privacy and security of the data. We also protect against poisoning attacks by identifying and removing training samples that significantly impact models.\n\n## Addressing High-Dimensional Data and the Cold Start Problem\n\nOur personalized content discovery engine is designed to handle high-dimensional data and address the cold start problem, where the model has difficulty making accurate predictions for new users or items. We use embedding-based models to predict user preferences based on past behavior. These models can handle high-dimensional data but may struggle with the cold start problem. To address this, we apply self-supervised learning techniques to understand the underlying structure of the data and make accurate predictions for new users or items.\n\n## Implementing Advanced Techniques and Cognitive Entities\n\nWe leverage advanced techniques and cognitive entities like Artificial Cognitive Entities (ACEs) and Large Language Models (LLMs) to track and analyze user engagement rates, user retention rates, and platform revenues. These tools evaluate their past performance and label their memories based on the success or failure of their actions, creating datasets for updating models.\n\n## Interactive Decision-Making and Text Generation\n\nOur engine uses pre-trained language models for interactive decision-making, improving the ability of AI to respond to user inputs in a meaningful and contextually appropriate manner. This can improve user engagement and retention rates on the platform. We also implement controllable text generation to generate more targeted and relevant content, potentially increasing platform revenues.\n\n## Understanding Risks in AI Development\n\nUnderstanding the potential risks associated with AI development can inform business decisions. This could include the allocation of resources towards AI safety research and the implementation of measures to manage AI growth. We are committed to conducting our AI research and development responsibly, with a focus on safety, transparency, and accountability.\n\nIn conclusion, the evaluation and metrics tracking phase is a critical part of our development process. It allows us to measure the success of our personalized content discovery engine, identify areas for improvement, and make data-driven decisions to continually enhance its performance. In the next section, we\'ll delve into the key technologies that power our engine: the Length-Extrapolatable Transformer and Retentive Network. Stay tuned!\n# Key Technologies: Length-Extrapolatable Transformer and Retentive Network\n\nIn our quest to create a personalized content discovery engine, we leverage two key technologies: the Length-Extrapolatable Transformer (LET) and the Retentive Network (RN). These technologies form the backbone of our engine, enabling it to process vast amounts of user data, understand individual preferences, generate diverse outputs, and improve the reliability and accuracy of recommendations.\n\n## Processing Vast Amounts of User Data\n\nThe LET is a powerful tool that can handle longer sequences of data, making it particularly useful in processing large amounts of user data, including watched history, search queries, and interaction patterns. By efficiently processing this data, the LET allows our engine to gain a comprehensive understanding of each user\'s preferences and behavior, which is crucial for generating personalized content recommendations.\n\n## Understanding Individual Preferences\n\nThe LET doesn\'t just process user data; it also uses this data to understand individual user preferences. By analyzing the patterns in the data, the LET can identify the types of content that each user prefers, the times they are most likely to watch, and other key factors that influence their viewing behavior. This deep understanding of individual preferences allows our engine to generate highly relevant and personalized content recommendations.\n\n## Generating Diverse Outputs\n\nThe LET is also capable of generating a diverse set of outputs for a particular problem. This diversity allows our engine to cater to a wide range of user preferences and ensures that our recommendations are not limited to a narrow set of content. By generating diverse outputs, the LET helps our engine to continually surprise and delight users with new and interesting content recommendations.\n\n## Improving Reliability and Accuracy of Recommendations\n\nTo improve the reliability and accuracy of our recommendations, we employ techniques like DiVeRSE and AMA. These techniques enhance the performance of the LET, allowing it to generate more accurate and reliable content recommendations. By continually improving the reliability and accuracy of our recommendations, we aim to enhance user satisfaction and engagement.\n\n## Real-World Application and Performance Improvement\n\nThe LET is not just a theoretical concept; it has been successfully applied in real-world applications. For instance, we have used prompt ensembles to generate multiple responses for every prompt and then used complex techniques to aggregate these responses into a final, high-quality result. This real-world application of the LET demonstrates its practicality and effectiveness.\n\n## Secure Memory Storage, Retrieval, and Data Compression\n\nThe RN, on the other hand, is a component of an Artificial Cognitive Entity (ACE) that can learn and remember information. We use blockchain technology and data compression techniques for secure memory storage and retrieval in ACEs. This ensures that our engine can remember users\' past preferences and make highly relevant recommendations even in the context of evolving tastes over time.\n\n## Utilization of Metadata and Distillation Techniques\n\nIn addition to remembering past preferences, the RN also utilizes metadata, timestamps, and vector search to help machines build knowledge webs. These webs can be used to reconstruct topics and fetch appropriate memories. We also implement summarization and distillation techniques to remove superfluous information and distill the data down to its most crucial elements.\n\n## Implementation of Preventive Measures\n\nFinally, we implement preventive measures to ensure the safety of our AI. This includes keeping it in a secure location, deleting all copies of the source code after the experiment, and diligently monitoring its activity. By implementing these measures, we aim to mitigate potential risks and ensure the safe and responsible use of our AI.\n\nIn conclusion, the Length-Extrapolatable Transformer and Retentive Network are key technologies that power our personalized content discovery engine. By leveraging these technologies, we aim to deliver a superior user experience, enhance user engagement, and drive higher revenues for streaming platforms.\n# Conclusion\n\nIn the realm of OTT video streaming, the paradox of choice is a real challenge. With a plethora of content available, users often find themselves overwhelmed, leading to decision fatigue and, in some cases, disengagement. However, with the advent of our personalized content discovery engine leveraging the Length-Extrapolatable Transformer and Retentive Network, we\'re turning this challenge into an opportunity.\n\nOur engine, powered by these two groundbreaking technologies, is designed to process vast amounts of user data, understand individual preferences, generate diverse outputs, and improve the reliability and accuracy of recommendations. It\'s not just about recommending content; it\'s about understanding the user, their preferences, their viewing habits, and their evolving tastes. It\'s about creating a personalized streaming experience that keeps users engaged and coming back for more.\n\nBut, as with any technology, it\'s not just about what it can do; it\'s about how it\'s implemented. We\'ve taken great care to ensure our engine integrates seamlessly with existing OTT platforms, scales to accommodate a growing user base, and respects user privacy and data security. We\'ve also put measures in place to continually evaluate its performance and make data-driven improvements.\n\nWhile we\'re excited about the potential of our personalized content discovery engine, we\'re also aware of the responsibilities that come with it. We\'re committed to conducting our AI research and development responsibly, with a focus on safety, transparency, and accountability. We\'re not just building a technology; we\'re building trust.\n\nIn the end, our goal is simple: to revolutionize the way users discover content on OTT platforms. By delivering a superior user experience, enhancing user engagement, and driving higher revenues for streaming platforms, we believe our personalized content discovery engine is a game-changer in the OTT video streaming landscape.\n\nSo, as we wrap up this journey into the future of OTT video streaming, remember this: the future is personalized, and it\'s closer than you think.
"""
diagrams_hierarchy_obj={
    "alibabacloud": {
        "analytics": [
            "AnalyticDb",
            "ClickHouse",
            "DataLakeAnalytics",
            "ElaticMapReduce",
            "OpenSearch"
        ],
        "application": [
            "ApiGateway",
            "BeeBot",
            "BlockchainAsAService",
            "CloudCallCenter",
            "CodePipeline",
            "DirectMail",
            "LogService",
            "MNS",
            "MessageNotificationService",
            "NodeJsPerformancePlatform",
            "OpenSearch",
            "PTS",
            "PerformanceTestingService",
            "RdCloud",
            "SCA",
            "SLS",
            "SmartConversationAnalysis",
            "Yida"
        ],
        "communication": [
            "DirectMail",
            "MobilePush"
        ],
        "compute": [
            "AutoScaling",
            "BatchCompute",
            "ContainerRegistry",
            "ContainerService",
            "ECI",
            "ECS",
            "EHPC",
            "ESS",
            "ElasticComputeService",
            "ElasticContainerInstance",
            "ElasticHighPerformanceComputing",
            "ElasticSearch",
            "FC",
            "FunctionCompute",
            "OOS",
            "OperationOrchestrationService",
            "ROS",
            "ResourceOrchestrationService",
            "SAE",
            "SAS",
            "SLB",
            "ServerLoadBalancer",
            "ServerlessAppEngine",
            "SimpleApplicationServer",
            "WAS",
            "WebAppService"
        ],
        "database": [
            "ApsaradbCassandra",
            "ApsaradbHbase",
            "ApsaradbMemcache",
            "ApsaradbMongodb",
            "ApsaradbOceanbase",
            "ApsaradbPolardb",
            "ApsaradbPostgresql",
            "ApsaradbPpas",
            "ApsaradbRedis",
            "ApsaradbSqlserver",
            "DBS",
            "DMS",
            "DRDS",
            "DTS",
            "DataManagementService",
            "DataTransmissionService",
            "DatabaseBackupService",
            "DisributeRelationalDatabaseService",
            "GDS",
            "GraphDatabaseService",
            "HybriddbForMysql",
            "RDS",
            "RelationalDatabaseService"
        ],
        "iot": [
            "IotInternetDeviceId",
            "IotLinkWan",
            "IotMobileConnectionPackage",
            "IotPlatform"
        ],
        "network": [
            "CEN",
            "Cdn",
            "CloudEnterpriseNetwork",
            "EIP",
            "ElasticIpAddress",
            "ExpressConnect",
            "NatGateway",
            "SLB",
            "ServerLoadBalancer",
            "SmartAccessGateway",
            "VPC",
            "VirtualPrivateCloud",
            "VpnGateway"
        ],
        "security": [
            "ABS",
            "AS",
            "AntiBotService",
            "AntiDdosBasic",
            "AntiDdosPro",
            "AntifraudService",
            "BastionHost",
            "CFW",
            "CM",
            "CloudFirewall",
            "CloudSecurityScanner",
            "ContentModeration",
            "CrowdsourcedSecurityTesting",
            "DES",
            "DataEncryptionService",
            "DbAudit",
            "GameShield",
            "IdVerification",
            "ManagedSecurityService",
            "SecurityCenter",
            "ServerGuard",
            "SslCertificates",
            "WAF",
            "WebApplicationFirewall"
        ],
        "storage": [
            "CloudStorageGateway",
            "FileStorageHdfs",
            "FileStorageNas",
            "HBR",
            "HDFS",
            "HDR",
            "HybridBackupRecovery",
            "HybridCloudDisasterRecovery",
            "Imm",
            "NAS",
            "OSS",
            "OTS",
            "ObjectStorageService",
            "ObjectTableStore"
        ],
        "web": [
            "Dns",
            "Domain"
        ]
    },
    "aws": {
        "analytics": [
            "Analytics",
            "Athena",
            "Cloudsearch",
            "CloudsearchSearchDocuments",
            "DataLakeResource",
            "DataPipeline",
            "EMR",
            "EMRCluster",
            "EMREngine",
            "EMREngineMaprM3",
            "EMREngineMaprM5",
            "EMREngineMaprM7",
            "EMRHdfsCluster",
            "ES",
            "ElasticsearchService",
            "Glue",
            "GlueCrawlers",
            "GlueDataCatalog",
            "Kinesis",
            "KinesisDataAnalytics",
            "KinesisDataFirehose",
            "KinesisDataStreams",
            "KinesisVideoStreams",
            "LakeFormation",
            "ManagedStreamingForKafka",
            "Quicksight",
            "Redshift",
            "RedshiftDenseComputeNode",
            "RedshiftDenseStorageNode"
        ],
        "ar": [
            "ArVr",
            "Sumerian"
        ],
        "blockchain": [
            "Blockchain",
            "BlockchainResource",
            "ManagedBlockchain",
            "QLDB",
            "QuantumLedgerDatabaseQldb"
        ],
        "business": [
            "A4B",
            "AlexaForBusiness",
            "BusinessApplications",
            "Chime",
            "Workmail"
        ],
        "compute": [
            "AMI",
            "AppRunner",
            "ApplicationAutoScaling",
            "AutoScaling",
            "Batch",
            "Compute",
            "ComputeOptimizer",
            "EB",
            "EC2",
            "EC2Ami",
            "EC2AutoScaling",
            "EC2ContainerRegistry",
            "EC2ContainerRegistryImage",
            "EC2ContainerRegistryRegistry",
            "EC2ElasticIpAddress",
            "EC2ImageBuilder",
            "EC2Instance",
            "EC2Instances",
            "EC2Rescue",
            "EC2SpotInstance",
            "ECR",
            "ECS",
            "EKS",
            "ElasticBeanstalk",
            "ElasticBeanstalkApplication",
            "ElasticBeanstalkDeployment",
            "ElasticContainerService",
            "ElasticContainerServiceContainer",
            "ElasticContainerServiceService",
            "ElasticKubernetesService",
            "Fargate",
            "Lambda",
            "LambdaFunction",
            "Lightsail",
            "LocalZones",
            "Outposts",
            "SAR",
            "ServerlessApplicationRepository",
            "ThinkboxDeadline",
            "ThinkboxDraft",
            "ThinkboxFrost",
            "ThinkboxKrakatoa",
            "ThinkboxSequoia",
            "ThinkboxStoke",
            "ThinkboxXmesh",
            "VmwareCloudOnAWS",
            "Wavelength"
        ],
        "cost": [
            "Budgets",
            "CostAndUsageReport",
            "CostExplorer",
            "CostManagement",
            "ReservedInstanceReporting",
            "SavingsPlans"
        ],
        "database": [
            "Aurora",
            "AuroraInstance",
            "DAX",
            "DB",
            "DDB",
            "DMS",
            "Database",
            "DatabaseMigrationService",
            "DatabaseMigrationServiceDatabaseMigrationWorkflow",
            "DocumentDB",
            "DocumentdbMongodbCompatibility",
            "Dynamodb",
            "DynamodbAttribute",
            "DynamodbAttributes",
            "DynamodbDax",
            "DynamodbGSI",
            "DynamodbGlobalSecondaryIndex",
            "DynamodbItem",
            "DynamodbItems",
            "DynamodbTable",
            "ElastiCache",
            "Elasticache",
            "ElasticacheCacheNode",
            "ElasticacheForMemcached",
            "ElasticacheForRedis",
            "KeyspacesManagedApacheCassandraService",
            "Neptune",
            "QLDB",
            "QuantumLedgerDatabaseQldb",
            "RDS",
            "RDSInstance",
            "RDSMariadbInstance",
            "RDSMysqlInstance",
            "RDSOnVmware",
            "RDSOracleInstance",
            "RDSPostgresqlInstance",
            "RDSSqlServerInstance",
            "Redshift",
            "RedshiftDenseComputeNode",
            "RedshiftDenseStorageNode",
            "Timestream"
        ],
        "devtools": [
            "CLI",
            "Cloud9",
            "Cloud9Resource",
            "CloudDevelopmentKit",
            "Codebuild",
            "Codecommit",
            "Codedeploy",
            "Codepipeline",
            "Codestar",
            "CommandLineInterface",
            "DevTools",
            "DeveloperTools",
            "ToolsAndSdks",
            "XRay"
        ],
        "enablement": [
            "CustomerEnablement",
            "Iq",
            "ManagedServices",
            "ProfessionalServices",
            "Support"
        ],
        "enduser": [
            "Appstream20",
            "DesktopAndAppStreaming",
            "Workdocs",
            "Worklink",
            "Workspaces"
        ],
        "engagement": [
            "Connect",
            "CustomerEngagement",
            "Pinpoint",
            "SES",
            "SimpleEmailServiceSes",
            "SimpleEmailServiceSesEmail"
        ],
        "game": [
            "GameTech",
            "Gamelift"
        ],
        "general": [
            "Client",
            "Disk",
            "Forums",
            "General",
            "GenericDatabase",
            "GenericFirewall",
            "GenericOfficeBuilding",
            "GenericSDK",
            "GenericSamlToken",
            "InternetAlt1",
            "InternetAlt2",
            "InternetGateway",
            "Marketplace",
            "MobileClient",
            "Multimedia",
            "OfficeBuilding",
            "SDK",
            "SamlToken",
            "SslPadlock",
            "TapeStorage",
            "Toolkit",
            "TraditionalServer",
            "User",
            "Users"
        ],
        "integration": [
            "ApplicationIntegration",
            "Appsync",
            "ConsoleMobileApplication",
            "EventResource",
            "Eventbridge",
            "EventbridgeCustomEventBusResource",
            "EventbridgeDefaultEventBusResource",
            "EventbridgeSaasPartnerEventBusResource",
            "ExpressWorkflows",
            "MQ",
            "SF",
            "SNS",
            "SQS",
            "SimpleNotificationServiceSns",
            "SimpleNotificationServiceSnsEmailNotification",
            "SimpleNotificationServiceSnsHttpNotification",
            "SimpleNotificationServiceSnsTopic",
            "SimpleQueueServiceSqs",
            "SimpleQueueServiceSqsMessage",
            "SimpleQueueServiceSqsQueue",
            "StepFunctions"
        ],
        "iot": [
            "FreeRTOS",
            "Freertos",
            "InternetOfThings",
            "Iot1Click",
            "IotAction",
            "IotActuator",
            "IotAlexaEcho",
            "IotAlexaEnabledDevice",
            "IotAlexaSkill",
            "IotAlexaVoiceService",
            "IotAnalytics",
            "IotAnalyticsChannel",
            "IotAnalyticsDataSet",
            "IotAnalyticsDataStore",
            "IotAnalyticsNotebook",
            "IotAnalyticsPipeline",
            "IotBank",
            "IotBicycle",
            "IotBoard",
            "IotButton",
            "IotCamera",
            "IotCar",
            "IotCart",
            "IotCertificate",
            "IotCoffeePot",
            "IotCore",
            "IotDesiredState",
            "IotDeviceDefender",
            "IotDeviceGateway",
            "IotDeviceManagement",
            "IotDoorLock",
            "IotEvents",
            "IotFactory",
            "IotFireTv",
            "IotFireTvStick",
            "IotGeneric",
            "IotGreengrass",
            "IotGreengrassConnector",
            "IotHardwareBoard",
            "IotHouse",
            "IotHttp",
            "IotHttp2",
            "IotJobs",
            "IotLambda",
            "IotLightbulb",
            "IotMedicalEmergency",
            "IotMqtt",
            "IotOverTheAirUpdate",
            "IotPolicy",
            "IotPolicyEmergency",
            "IotReportedState",
            "IotRule",
            "IotSensor",
            "IotServo",
            "IotShadow",
            "IotSimulator",
            "IotSitewise",
            "IotThermostat",
            "IotThingsGraph",
            "IotTopic",
            "IotTravel",
            "IotUtility",
            "IotWindfarm"
        ],
        "management": [
            "AutoScaling",
            "Chatbot",
            "Cloudformation",
            "CloudformationChangeSet",
            "CloudformationStack",
            "CloudformationTemplate",
            "Cloudtrail",
            "Cloudwatch",
            "CloudwatchAlarm",
            "CloudwatchEventEventBased",
            "CloudwatchEventTimeBased",
            "CloudwatchRule",
            "Codeguru",
            "CommandLineInterface",
            "Config",
            "ControlTower",
            "LicenseManager",
            "ManagedServices",
            "ManagementAndGovernance",
            "ManagementConsole",
            "Opsworks",
            "OpsworksApps",
            "OpsworksDeployments",
            "OpsworksInstances",
            "OpsworksLayers",
            "OpsworksMonitoring",
            "OpsworksPermissions",
            "OpsworksResources",
            "OpsworksStack",
            "Organizations",
            "OrganizationsAccount",
            "OrganizationsOrganizationalUnit",
            "ParameterStore",
            "PersonalHealthDashboard",
            "SSM",
            "ServiceCatalog",
            "SystemsManager",
            "SystemsManagerAutomation",
            "SystemsManagerDocuments",
            "SystemsManagerInventory",
            "SystemsManagerMaintenanceWindows",
            "SystemsManagerOpscenter",
            "SystemsManagerParameterStore",
            "SystemsManagerPatchManager",
            "SystemsManagerRunCommand",
            "SystemsManagerStateManager",
            "TrustedAdvisor",
            "TrustedAdvisorChecklist",
            "TrustedAdvisorChecklistCost",
            "TrustedAdvisorChecklistFaultTolerant",
            "TrustedAdvisorChecklistPerformance",
            "TrustedAdvisorChecklistSecurity",
            "WellArchitectedTool"
        ],
        "media": [
            "ElasticTranscoder",
            "ElementalConductor",
            "ElementalDelta",
            "ElementalLive",
            "ElementalMediaconnect",
            "ElementalMediaconvert",
            "ElementalMedialive",
            "ElementalMediapackage",
            "ElementalMediastore",
            "ElementalMediatailor",
            "ElementalServer",
            "KinesisVideoStreams",
            "MediaServices"
        ],
        "migration": [
            "ADS",
            "ApplicationDiscoveryService",
            "CEM",
            "CloudendureMigration",
            "DMS",
            "DatabaseMigrationService",
            "Datasync",
            "DatasyncAgent",
            "MAT",
            "MigrationAndTransfer",
            "MigrationHub",
            "SMS",
            "ServerMigrationService",
            "Snowball",
            "SnowballEdge",
            "Snowmobile",
            "TransferForSftp"
        ],
        "ml": [
            "ApacheMxnetOnAWS",
            "AugmentedAi",
            "Comprehend",
            "DLC",
            "DeepLearningAmis",
            "DeepLearningContainers",
            "Deepcomposer",
            "Deeplens",
            "Deepracer",
            "ElasticInference",
            "Forecast",
            "FraudDetector",
            "Kendra",
            "Lex",
            "MachineLearning",
            "Personalize",
            "Polly",
            "Rekognition",
            "RekognitionImage",
            "RekognitionVideo",
            "Sagemaker",
            "SagemakerGroundTruth",
            "SagemakerModel",
            "SagemakerNotebook",
            "SagemakerTrainingJob",
            "TensorflowOnAWS",
            "Textract",
            "Transcribe",
            "Translate"
        ],
        "mobile": [
            "APIGateway",
            "APIGatewayEndpoint",
            "Amplify",
            "Appsync",
            "DeviceFarm",
            "Mobile",
            "Pinpoint"
        ],
        "network": [
            "ALB",
            "APIGateway",
            "APIGatewayEndpoint",
            "AppMesh",
            "CF",
            "CLB",
            "ClientVpn",
            "CloudFront",
            "CloudFrontDownloadDistribution",
            "CloudFrontEdgeLocation",
            "CloudFrontStreamingDistribution",
            "CloudMap",
            "DirectConnect",
            "ELB",
            "ElasticLoadBalancing",
            "ElbApplicationLoadBalancer",
            "ElbClassicLoadBalancer",
            "ElbNetworkLoadBalancer",
            "Endpoint",
            "GAX",
            "GlobalAccelerator",
            "InternetGateway",
            "NATGateway",
            "NLB",
            "Nacl",
            "NetworkingAndContentDelivery",
            "PrivateSubnet",
            "Privatelink",
            "PublicSubnet",
            "Route53",
            "Route53HostedZone",
            "RouteTable",
            "SiteToSiteVpn",
            "TransitGateway",
            "VPC",
            "VPCCustomerGateway",
            "VPCElasticNetworkAdapter",
            "VPCElasticNetworkInterface",
            "VPCFlowLogs",
            "VPCPeering",
            "VPCRouter",
            "VPCTrafficMirroring",
            "VpnConnection",
            "VpnGateway"
        ],
        "quantum": [
            "Braket",
            "QuantumTechnologies"
        ],
        "robotics": [
            "Robomaker",
            "RobomakerCloudExtensionRos",
            "RobomakerDevelopmentEnvironment",
            "RobomakerFleetManagement",
            "RobomakerSimulator",
            "Robotics"
        ],
        "satellite": [
            "GroundStation",
            "Satellite"
        ],
        "security": [
            "ACM",
            "AdConnector",
            "Artifact",
            "CertificateAuthority",
            "CertificateManager",
            "CloudDirectory",
            "CloudHSM",
            "Cloudhsm",
            "Cognito",
            "DS",
            "Detective",
            "DirectoryService",
            "FMS",
            "FirewallManager",
            "Guardduty",
            "IAM",
            "IAMAWSSts",
            "IAMAccessAnalyzer",
            "IAMPermissions",
            "IAMRole",
            "IdentityAndAccessManagementIam",
            "IdentityAndAccessManagementIamAWSSts",
            "IdentityAndAccessManagementIamAWSStsAlternate",
            "IdentityAndAccessManagementIamAccessAnalyzer",
            "IdentityAndAccessManagementIamAddOn",
            "IdentityAndAccessManagementIamDataEncryptionKey",
            "IdentityAndAccessManagementIamEncryptedData",
            "IdentityAndAccessManagementIamLongTermSecurityCredential",
            "IdentityAndAccessManagementIamMfaToken",
            "IdentityAndAccessManagementIamPermissions",
            "IdentityAndAccessManagementIamRole",
            "IdentityAndAccessManagementIamTemporarySecurityCredential",
            "Inspector",
            "InspectorAgent",
            "KMS",
            "KeyManagementService",
            "Macie",
            "ManagedMicrosoftAd",
            "RAM",
            "ResourceAccessManager",
            "SecretsManager",
            "SecurityHub",
            "SecurityHubFinding",
            "SecurityIdentityAndCompliance",
            "Shield",
            "ShieldAdvanced",
            "SimpleAd",
            "SingleSignOn",
            "WAF",
            "WAFFilteringRule"
        ],
        "storage": [
            "Backup",
            "CDR",
            "CloudendureDisasterRecovery",
            "EBS",
            "EFS",
            "EFSInfrequentaccessPrimaryBg",
            "EFSStandardPrimaryBg",
            "ElasticBlockStoreEBS",
            "ElasticBlockStoreEBSSnapshot",
            "ElasticBlockStoreEBSVolume",
            "ElasticFileSystemEFS",
            "ElasticFileSystemEFSFileSystem",
            "FSx",
            "Fsx",
            "FsxForLustre",
            "FsxForWindowsFileServer",
            "MultipleVolumesResource",
            "S3",
            "S3Glacier",
            "S3GlacierArchive",
            "S3GlacierVault",
            "SimpleStorageServiceS3",
            "SimpleStorageServiceS3Bucket",
            "SimpleStorageServiceS3BucketWithObjects",
            "SimpleStorageServiceS3Object",
            "SnowFamilySnowballImportExport",
            "Snowball",
            "SnowballEdge",
            "Snowmobile",
            "Storage",
            "StorageGateway",
            "StorageGatewayCachedVolume",
            "StorageGatewayNonCachedVolume",
            "StorageGatewayVirtualTapeLibrary"
        ]
    },
    "azure": {
        "analytics": [
            "AnalysisServices",
            "DataExplorerClusters",
            "DataFactories",
            "DataLakeAnalytics",
            "DataLakeStoreGen1",
            "Databricks",
            "EventHubClusters",
            "EventHubs",
            "Hdinsightclusters",
            "LogAnalyticsWorkspaces",
            "StreamAnalyticsJobs",
            "SynapseAnalytics"
        ],
        "compute": [
            "ACR",
            "AKS",
            "AppServices",
            "AutomanagedVM",
            "AvailabilitySets",
            "BatchAccounts",
            "CitrixVirtualDesktopsEssentials",
            "CloudServices",
            "CloudServicesClassic",
            "CloudsimpleVirtualMachines",
            "ContainerInstances",
            "ContainerRegistries",
            "DiskEncryptionSets",
            "DiskSnapshots",
            "Disks",
            "FunctionApps",
            "ImageDefinitions",
            "ImageVersions",
            "KubernetesServices",
            "MeshApplications",
            "OsImages",
            "SAPHANAOnAzure",
            "ServiceFabricClusters",
            "SharedImageGalleries",
            "SpringCloud",
            "VM",
            "VMClassic",
            "VMImages",
            "VMLinux",
            "VMSS",
            "VMScaleSet",
            "VMWindows",
            "Workspaces"
        ],
        "database": [
            "BlobStorage",
            "CacheForRedis",
            "CosmosDb",
            "DataExplorerClusters",
            "DataFactory",
            "DataLake",
            "DatabaseForMariadbServers",
            "DatabaseForMysqlServers",
            "DatabaseForPostgresqlServers",
            "ElasticDatabasePools",
            "ElasticJobAgents",
            "InstancePools",
            "ManagedDatabases",
            "SQL",
            "SQLDatabases",
            "SQLDatawarehouse",
            "SQLManagedInstances",
            "SQLServerStretchDatabases",
            "SQLServers",
            "SQLVM",
            "SsisLiftAndShiftIr",
            "SynapseAnalytics",
            "VirtualClusters",
            "VirtualDatacenter"
        ],
        "devops": [
            "ApplicationInsights",
            "Artifacts",
            "Boards",
            "Devops",
            "DevtestLabs",
            "LabServices",
            "Pipelines",
            "Repos",
            "TestPlans"
        ],
        "general": [
            "Allresources",
            "Azurehome",
            "Developertools",
            "Helpsupport",
            "Information",
            "Managementgroups",
            "Marketplace",
            "Quickstartcenter",
            "Recent",
            "Reservations",
            "Resource",
            "Resourcegroups",
            "Servicehealth",
            "Shareddashboard",
            "Subscriptions",
            "Support",
            "Supportrequests",
            "Tag",
            "Tags",
            "Templates",
            "Twousericon",
            "Userhealthicon",
            "Usericon",
            "Userprivacy",
            "Userresource",
            "Whatsnew"
        ],
        "identity": [
            "ADB2C",
            "ADDomainServices",
            "ADIdentityProtection",
            "ADPrivilegedIdentityManagement",
            "AccessReview",
            "ActiveDirectory",
            "ActiveDirectoryConnectHealth",
            "AppRegistrations",
            "ConditionalAccess",
            "EnterpriseApplications",
            "Groups",
            "IdentityGovernance",
            "InformationProtection",
            "ManagedIdentities",
            "Users"
        ],
        "integration": [
            "APIForFhir",
            "APIManagement",
            "AppConfiguration",
            "DataCatalog",
            "EventGridDomains",
            "EventGridSubscriptions",
            "EventGridTopics",
            "IntegrationAccounts",
            "IntegrationServiceEnvironments",
            "LogicApps",
            "LogicAppsCustomConnector",
            "PartnerTopic",
            "SendgridAccounts",
            "ServiceBus",
            "ServiceBusRelays",
            "ServiceCatalogManagedApplicationDefinitions",
            "SoftwareAsAService",
            "StorsimpleDeviceManagers",
            "SystemTopic"
        ],
        "iot": [
            "DeviceProvisioningServices",
            "DigitalTwins",
            "IotCentralApplications",
            "IotHub",
            "IotHubSecurity",
            "Maps",
            "Sphere",
            "TimeSeriesInsightsEnvironments",
            "TimeSeriesInsightsEventsSources",
            "Windows10IotCoreServices"
        ],
        "migration": [
            "DataBox",
            "DataBoxEdge",
            "DatabaseMigrationServices",
            "MigrationProjects",
            "RecoveryServicesVaults"
        ],
        "ml": [
            "BatchAI",
            "BotServices",
            "CognitiveServices",
            "GenomicsAccounts",
            "MachineLearningServiceWorkspaces",
            "MachineLearningStudioWebServicePlans",
            "MachineLearningStudioWebServices",
            "MachineLearningStudioWorkspaces"
        ],
        "mobile": [
            "AppServiceMobile",
            "MobileEngagement",
            "NotificationHubs"
        ],
        "network": [
            "ApplicationGateway",
            "ApplicationSecurityGroups",
            "CDNProfiles",
            "Connections",
            "DDOSProtectionPlans",
            "DNSPrivateZones",
            "DNSZones",
            "ExpressrouteCircuits",
            "Firewall",
            "FrontDoors",
            "LoadBalancers",
            "LocalNetworkGateways",
            "NetworkInterfaces",
            "NetworkSecurityGroupsClassic",
            "NetworkWatcher",
            "OnPremisesDataGateways",
            "PublicIpAddresses",
            "ReservedIpAddressesClassic",
            "RouteFilters",
            "RouteTables",
            "ServiceEndpointPolicies",
            "Subnets",
            "TrafficManagerProfiles",
            "VirtualNetworkClassic",
            "VirtualNetworkGateways",
            "VirtualNetworks",
            "VirtualWans"
        ],
        "security": [
            "ApplicationSecurityGroups",
            "ConditionalAccess",
            "Defender",
            "ExtendedSecurityUpdates",
            "KeyVaults",
            "SecurityCenter",
            "Sentinel"
        ],
        "storage": [
            "ArchiveStorage",
            "Azurefxtedgefiler",
            "BlobStorage",
            "DataBox",
            "DataBoxEdgeDataBoxGateway",
            "DataLakeStorage",
            "GeneralStorage",
            "NetappFiles",
            "QueuesStorage",
            "StorageAccounts",
            "StorageAccountsClassic",
            "StorageExplorer",
            "StorageSyncServices",
            "StorsimpleDataManagers",
            "StorsimpleDeviceManagers",
            "TableStorage"
        ],
        "web": [
            "APIConnections",
            "AppServiceCertificates",
            "AppServiceDomains",
            "AppServiceEnvironments",
            "AppServicePlans",
            "AppServices",
            "MediaServices",
            "NotificationHubNamespaces",
            "Search",
            "Signalr"
        ]
    },
    "digitalocean": {
        "compute": [
            "Containers",
            "Docker",
            "Droplet",
            "DropletConnect",
            "DropletSnapshot",
            "K8SCluster",
            "K8SNode",
            "K8SNodePool"
        ],
        "database": [
            "DbaasPrimary",
            "DbaasPrimaryStandbyMore",
            "DbaasReadOnly",
            "DbaasStandby"
        ],
        "network": [
            "Certificate",
            "Domain",
            "DomainRegistration",
            "Firewall",
            "FloatingIp",
            "InternetGateway",
            "LoadBalancer",
            "ManagedVpn",
            "Vpc"
        ],
        "storage": [
            "Folder",
            "Space",
            "Volume",
            "VolumeSnapshot"
        ]
    },
    "elastic": {
        "agent": [
            "Agent",
            "Endpoint",
            "Fleet",
            "Integrations"
        ],
        "beats": [
            "APM",
            "Auditbeat",
            "Filebeat",
            "Functionbeat",
            "Heartbeat",
            "Metricbeat",
            "Packetbeat",
            "Winlogbeat"
        ],
        "elasticsearch": [
            "Alerting",
            "Beats",
            "ElasticSearch",
            "Elasticsearch",
            "Kibana",
            "LogStash",
            "Logstash",
            "LogstashPipeline",
            "ML",
            "MachineLearning",
            "MapServices",
            "Maps",
            "Monitoring",
            "SQL",
            "SearchableSnapshots",
            "SecuritySettings",
            "Stack"
        ],
        "enterprisesearch": [
            "AppSearch",
            "Crawler",
            "EnterpriseSearch",
            "SiteSearch",
            "WorkplaceSearch"
        ],
        "observability": [
            "APM",
            "Logs",
            "Metrics",
            "Observability",
            "Uptime"
        ],
        "orchestration": [
            "ECE",
            "ECK"
        ],
        "saas": [
            "Cloud",
            "Elastic"
        ],
        "security": [
            "Endpoint",
            "SIEM",
            "Security",
            "Xdr"
        ]
    },
    "firebase": {
        "base": [
            "Firebase"
        ],
        "develop": [
            "Authentication",
            "Firestore",
            "Functions",
            "Hosting",
            "MLKit",
            "RealtimeDatabase",
            "Storage"
        ],
        "extentions": [
            "Extensions"
        ],
        "grow": [
            "ABTesting",
            "AppIndexing",
            "DynamicLinks",
            "FCM",
            "InAppMessaging",
            "Invites",
            "Messaging",
            "Predictions",
            "RemoteConfig"
        ],
        "quality": [
            "AppDistribution",
            "CrashReporting",
            "Crashlytics",
            "PerformanceMonitoring",
            "TestLab"
        ]
    },
    "gcp": {
        "analytics": [
            "BigQuery",
            "Bigquery",
            "Composer",
            "DataCatalog",
            "DataFusion",
            "Dataflow",
            "Datalab",
            "Dataprep",
            "Dataproc",
            "Genomics",
            "PubSub",
            "Pubsub"
        ],
        "api": [
            "APIGateway",
            "Endpoints"
        ],
        "compute": [
            "AppEngine",
            "ComputeEngine",
            "ContainerOptimizedOS",
            "Functions",
            "GAE",
            "GCE",
            "GCF",
            "GKE",
            "GKEOnPrem",
            "GPU",
            "KubernetesEngine",
            "Run"
        ],
        "database": [
            "BigTable",
            "Bigtable",
            "Datastore",
            "Firestore",
            "Memorystore",
            "SQL",
            "Spanner"
        ],
        "devtools": [
            "Build",
            "Code",
            "CodeForIntellij",
            "ContainerRegistry",
            "GCR",
            "GradleAppEnginePlugin",
            "IdePlugins",
            "MavenAppEnginePlugin",
            "SDK",
            "Scheduler",
            "SourceRepositories",
            "Tasks",
            "TestLab",
            "ToolsForEclipse",
            "ToolsForPowershell",
            "ToolsForVisualStudio"
        ],
        "iot": [
            "IotCore"
        ],
        "migration": [
            "TransferAppliance"
        ],
        "ml": [
            "AIHub",
            "AIPlatform",
            "AIPlatformDataLabelingService",
            "AdvancedSolutionsLab",
            "AutoML",
            "Automl",
            "AutomlNaturalLanguage",
            "AutomlTables",
            "AutomlTranslation",
            "AutomlVideoIntelligence",
            "AutomlVision",
            "DialogFlowEnterpriseEdition",
            "InferenceAPI",
            "JobsAPI",
            "NLAPI",
            "NaturalLanguageAPI",
            "RecommendationsAI",
            "STT",
            "SpeechToText",
            "TPU",
            "TTS",
            "TextToSpeech",
            "TranslationAPI",
            "VideoIntelligenceAPI",
            "VisionAPI"
        ],
        "network": [
            "Armor",
            "CDN",
            "DNS",
            "DedicatedInterconnect",
            "ExternalIpAddresses",
            "FirewallRules",
            "LoadBalancing",
            "NAT",
            "Network",
            "PartnerInterconnect",
            "PremiumNetworkTier",
            "Router",
            "Routes",
            "StandardNetworkTier",
            "TrafficDirector",
            "VPC",
            "VPN",
            "VirtualPrivateCloud"
        ],
        "operations": [
            "Monitoring"
        ],
        "security": [
            "IAP",
            "Iam",
            "KMS",
            "KeyManagementService",
            "ResourceManager",
            "SCC",
            "SecurityCommandCenter",
            "SecurityScanner"
        ],
        "storage": [
            "Filestore",
            "GCS",
            "PersistentDisk",
            "Storage"
        ]
    },
    "generic": {
        "blank": [
            "Blank"
        ],
        "compute": [
            "Rack"
        ],
        "database": [
            "SQL"
        ],
        "device": [
            "Mobile",
            "Tablet"
        ],
        "network": [
            "Firewall",
            "Router",
            "Subnet",
            "Switch",
            "VPN"
        ],
        "os": [
            "Android",
            "Centos",
            "Debian",
            "IOS",
            "LinuxGeneral",
            "Raspbian",
            "RedHat",
            "Suse",
            "Ubuntu",
            "Windows"
        ],
        "place": [
            "Datacenter"
        ],
        "storage": [
            "Storage"
        ],
        "virtualization": [
            "Virtualbox",
            "Vmware",
            "XEN"
        ]
    },
    "ibm": {
        "analytics": [
            "Analytics",
            "DataIntegration",
            "DataRepositories",
            "DeviceAnalytics",
            "StreamingComputing"
        ],
        "applications": [
            "ActionableInsight",
            "Annotate",
            "ApiDeveloperPortal",
            "ApiPolyglotRuntimes",
            "AppServer",
            "ApplicationLogic",
            "EnterpriseApplications",
            "Index",
            "IotApplication",
            "Microservice",
            "MobileApp",
            "Ontology",
            "OpenSourceTools",
            "RuntimeServices",
            "SaasApplications",
            "ServiceBroker",
            "SpeechToText",
            "VisualRecognition",
            "Visualization"
        ],
        "blockchain": [
            "Blockchain",
            "BlockchainDeveloper",
            "CertificateAuthority",
            "ClientApplication",
            "Communication",
            "Consensus",
            "Event",
            "EventListener",
            "ExistingEnterpriseSystems",
            "HyperledgerFabric",
            "KeyManagement",
            "Ledger",
            "Membership",
            "MembershipServicesProviderApi",
            "MessageBus",
            "Node",
            "Services",
            "SmartContract",
            "TransactionManager",
            "Wallet"
        ],
        "compute": [
            "BareMetalServer",
            "ImageService",
            "Instance",
            "Key",
            "PowerInstance"
        ],
        "data": [
            "Caches",
            "Cloud",
            "ConversationTrainedDeployed",
            "DataServices",
            "DataSources",
            "DeviceIdentityService",
            "DeviceRegistry",
            "EnterpriseData",
            "EnterpriseUserDirectory",
            "FileRepository",
            "GroundTruth",
            "Model",
            "TmsDataInterface"
        ],
        "devops": [
            "ArtifactManagement",
            "BuildTest",
            "CodeEditor",
            "CollaborativeDevelopment",
            "ConfigurationManagement",
            "ContinuousDeploy",
            "ContinuousTesting",
            "Devops",
            "Provision",
            "ReleaseManagement"
        ],
        "general": [
            "CloudMessaging",
            "CloudServices",
            "Cloudant",
            "CognitiveServices",
            "DataSecurity",
            "Enterprise",
            "GovernanceRiskCompliance",
            "IBMContainers",
            "IBMPublicCloud",
            "IdentityAccessManagement",
            "IdentityProvider",
            "InfrastructureSecurity",
            "Internet",
            "IotCloud",
            "MicroservicesApplication",
            "MicroservicesMesh",
            "Monitoring",
            "MonitoringLogging",
            "ObjectStorage",
            "OfflineCapabilities",
            "Openwhisk",
            "PeerCloud",
            "RetrieveRank",
            "Scalable",
            "ServiceDiscoveryConfiguration",
            "TextToSpeech",
            "TransformationConnectivity"
        ],
        "infrastructure": [
            "Channels",
            "CloudMessaging",
            "Dashboard",
            "Diagnostics",
            "EdgeServices",
            "EnterpriseMessaging",
            "EventFeed",
            "InfrastructureServices",
            "InterserviceCommunication",
            "LoadBalancingRouting",
            "MicroservicesMesh",
            "MobileBackend",
            "MobileProviderNetwork",
            "Monitoring",
            "MonitoringLogging",
            "PeerServices",
            "ServiceDiscoveryConfiguration",
            "TransformationConnectivity"
        ],
        "management": [
            "AlertNotification",
            "ApiManagement",
            "CloudManagement",
            "ClusterManagement",
            "ContentManagement",
            "DataServices",
            "DeviceManagement",
            "InformationGovernance",
            "ItServiceManagement",
            "Management",
            "MonitoringMetrics",
            "ProcessManagement",
            "ProviderCloudPortalService",
            "PushNotifications",
            "ServiceManagementTools"
        ],
        "network": [
            "Bridge",
            "DirectLink",
            "Enterprise",
            "Firewall",
            "FloatingIp",
            "Gateway",
            "InternetServices",
            "LoadBalancer",
            "LoadBalancerListener",
            "LoadBalancerPool",
            "LoadBalancingRouting",
            "PublicGateway",
            "Region",
            "Router",
            "Rules",
            "Subnet",
            "TransitGateway",
            "Vpc",
            "VpnConnection",
            "VpnGateway",
            "VpnPolicy"
        ],
        "security": [
            "ApiSecurity",
            "BlockchainSecurityService",
            "DataSecurity",
            "Firewall",
            "Gateway",
            "GovernanceRiskCompliance",
            "IdentityAccessManagement",
            "IdentityProvider",
            "InfrastructureSecurity",
            "PhysicalSecurity",
            "SecurityMonitoringIntelligence",
            "SecurityServices",
            "TrustendComputing",
            "Vpn"
        ],
        "social": [
            "Communities",
            "FileSync",
            "LiveCollaboration",
            "Messaging",
            "Networking"
        ],
        "storage": [
            "BlockStorage",
            "ObjectStorage"
        ],
        "user": [
            "Browser",
            "Device",
            "IntegratedDigitalExperiences",
            "PhysicalEntity",
            "Sensor",
            "User"
        ]
    },
    "k8s": {
        "chaos": [
            "ChaosMesh",
            "LitmusChaos"
        ],
        "clusterconfig": [
            "HPA",
            "HorizontalPodAutoscaler",
            "LimitRange",
            "Limits",
            "Quota"
        ],
        "compute": [
            "Cronjob",
            "DS",
            "DaemonSet",
            "Deploy",
            "Deployment",
            "Job",
            "Pod",
            "RS",
            "ReplicaSet",
            "STS",
            "StatefulSet"
        ],
        "controlplane": [
            "API",
            "APIServer",
            "CCM",
            "CM",
            "ControllerManager",
            "KProxy",
            "KubeProxy",
            "Kubelet",
            "Sched",
            "Scheduler"
        ],
        "ecosystem": [
            "ExternalDns",
            "Helm",
            "Krew",
            "Kustomize"
        ],
        "group": [
            "NS",
            "Namespace"
        ],
        "infra": [
            "ETCD",
            "Master",
            "Node"
        ],
        "network": [
            "Endpoint",
            "Ep",
            "Ing",
            "Ingress",
            "Netpol",
            "NetworkPolicy",
            "SVC",
            "Service"
        ],
        "others": [
            "CRD",
            "PSP"
        ],
        "podconfig": [
            "CM",
            "ConfigMap",
            "Secret"
        ],
        "rbac": [
            "CRB",
            "CRole",
            "ClusterRole",
            "ClusterRoleBinding",
            "Group",
            "RB",
            "Role",
            "RoleBinding",
            "SA",
            "ServiceAccount",
            "User"
        ],
        "storage": [
            "PV",
            "PVC",
            "PersistentVolume",
            "PersistentVolumeClaim",
            "SC",
            "StorageClass",
            "Vol",
            "Volume"
        ]
    },
    "oci": {
        "compute": [
            "Autoscale",
            "AutoscaleWhite",
            "BM",
            "BMWhite",
            "BareMetal",
            "BareMetalWhite",
            "Container",
            "ContainerEngine",
            "ContainerEngineWhite",
            "ContainerWhite",
            "Functions",
            "FunctionsWhite",
            "InstancePools",
            "InstancePoolsWhite",
            "OCIR",
            "OCIRWhite",
            "OCIRegistry",
            "OCIRegistryWhite",
            "OKE",
            "OKEWhite",
            "VM",
            "VMWhite",
            "VirtualMachine",
            "VirtualMachineWhite"
        ],
        "connectivity": [
            "Backbone",
            "BackboneWhite",
            "CDN",
            "CDNWhite",
            "CustomerDatacenter",
            "CustomerDatacntrWhite",
            "CustomerPremise",
            "CustomerPremiseWhite",
            "DNS",
            "DNSWhite",
            "DisconnectedRegions",
            "DisconnectedRegionsWhite",
            "FastConnect",
            "FastConnectWhite",
            "NATGateway",
            "NATGatewayWhite",
            "VPN",
            "VPNWhite"
        ],
        "devops": [
            "APIGateway",
            "APIGatewayWhite",
            "APIService",
            "APIServiceWhite",
            "ResourceMgmt",
            "ResourceMgmtWhite"
        ],
        "governance": [
            "Audit",
            "AuditWhite",
            "Compartments",
            "CompartmentsWhite",
            "Groups",
            "GroupsWhite",
            "Logging",
            "LoggingWhite",
            "OCID",
            "OCIDWhite",
            "Policies",
            "PoliciesWhite",
            "Tagging",
            "TaggingWhite"
        ],
        "monitoring": [
            "Alarm",
            "AlarmWhite",
            "Email",
            "EmailWhite",
            "Events",
            "EventsWhite",
            "HealthCheck",
            "HealthCheckWhite",
            "Notifications",
            "NotificationsWhite",
            "Queue",
            "QueueWhite",
            "Search",
            "SearchWhite",
            "Telemetry",
            "TelemetryWhite",
            "Workflow",
            "WorkflowWhite"
        ],
        "network": [
            "Drg",
            "DrgWhite",
            "Firewall",
            "FirewallWhite",
            "InternetGateway",
            "InternetGatewayWhite",
            "LoadBalancer",
            "LoadBalancerWhite",
            "RouteTable",
            "RouteTableWhite",
            "SecurityLists",
            "SecurityListsWhite",
            "ServiceGateway",
            "ServiceGatewayWhite",
            "Vcn",
            "VcnWhite"
        ],
        "security": [
            "CloudGuard",
            "CloudGuardWhite",
            "DDOS",
            "DDOSWhite",
            "Encryption",
            "EncryptionWhite",
            "IDAccess",
            "IDAccessWhite",
            "KeyManagement",
            "KeyManagementWhite",
            "MaxSecurityZone",
            "MaxSecurityZoneWhite",
            "Vault",
            "VaultWhite",
            "WAF",
            "WAFWhite"
        ],
        "storage": [
            "BackupRestore",
            "BackupRestoreWhite",
            "BlockStorage",
            "BlockStorageClone",
            "BlockStorageCloneWhite",
            "BlockStorageWhite",
            "Buckets",
            "BucketsWhite",
            "DataTransfer",
            "DataTransferWhite",
            "ElasticPerformance",
            "ElasticPerformanceWhite",
            "FileStorage",
            "FileStorageWhite",
            "ObjectStorage",
            "ObjectStorageWhite",
            "StorageGateway",
            "StorageGatewayWhite"
        ]
    },
    "onprem": {
        "aggregator": [
            "Fluentd",
            "Vector"
        ],
        "analytics": [
            "Beam",
            "Databricks",
            "Dbt",
            "Dremio",
            "Flink",
            "Hadoop",
            "Hive",
            "Metabase",
            "Norikra",
            "PowerBI",
            "Powerbi",
            "Presto",
            "Singer",
            "Spark",
            "Storm",
            "Superset",
            "Tableau"
        ],
        "auth": [
            "Boundary",
            "BuzzfeedSso",
            "Oauth2Proxy"
        ],
        "cd": [
            "Spinnaker",
            "Tekton",
            "TektonCli"
        ],
        "certificates": [
            "CertManager",
            "LetsEncrypt"
        ],
        "ci": [
            "CircleCI",
            "Circleci",
            "ConcourseCI",
            "Concourseci",
            "DroneCI",
            "Droneci",
            "GithubActions",
            "GitlabCI",
            "Gitlabci",
            "Jenkins",
            "TC",
            "Teamcity",
            "TravisCI",
            "Travisci",
            "ZuulCI",
            "Zuulci"
        ],
        "client": [
            "Client",
            "User",
            "Users"
        ],
        "compute": [
            "Nomad",
            "Server"
        ],
        "container": [
            "Containerd",
            "Crio",
            "Docker",
            "Firecracker",
            "Gvisor",
            "K3S",
            "LXC",
            "Lxc",
            "RKT",
            "Rkt"
        ],
        "database": [
            "Cassandra",
            "ClickHouse",
            "Clickhouse",
            "CockroachDB",
            "Cockroachdb",
            "CouchDB",
            "Couchbase",
            "Couchdb",
            "Dgraph",
            "Druid",
            "HBase",
            "Hbase",
            "InfluxDB",
            "Influxdb",
            "JanusGraph",
            "Janusgraph",
            "MSSQL",
            "MariaDB",
            "Mariadb",
            "MongoDB",
            "Mongodb",
            "Mssql",
            "MySQL",
            "Mysql",
            "Neo4J",
            "Oracle",
            "PostgreSQL",
            "Postgresql",
            "Scylla"
        ],
        "dns": [
            "Coredns",
            "Powerdns"
        ],
        "etl": [
            "Embulk"
        ],
        "gitops": [
            "ArgoCD",
            "Argocd",
            "Flagger",
            "Flux"
        ],
        "groupware": [
            "Nextcloud"
        ],
        "iac": [
            "Ansible",
            "Atlantis",
            "Awx",
            "Puppet",
            "Terraform"
        ],
        "identity": [
            "Dex"
        ],
        "inmemory": [
            "Aerospike",
            "Hazelcast",
            "Memcached",
            "Redis"
        ],
        "logging": [
            "FluentBit",
            "Fluentbit",
            "Graylog",
            "Loki",
            "RSyslog",
            "Rsyslog",
            "SyslogNg"
        ],
        "mlops": [
            "Mlflow",
            "Polyaxon"
        ],
        "monitoring": [
            "Cortex",
            "Datadog",
            "Dynatrace",
            "Grafana",
            "Humio",
            "Nagios",
            "Newrelic",
            "Prometheus",
            "PrometheusOperator",
            "Sentry",
            "Splunk",
            "Thanos",
            "Zabbix"
        ],
        "network": [
            "Ambassador",
            "Apache",
            "Bind9",
            "Caddy",
            "Consul",
            "ETCD",
            "Envoy",
            "Etcd",
            "Glassfish",
            "Gunicorn",
            "HAProxy",
            "Haproxy",
            "Internet",
            "Istio",
            "Jbossas",
            "Jetty",
            "Kong",
            "Linkerd",
            "Nginx",
            "OPNSense",
            "OSM",
            "Ocelot",
            "OpenServiceMesh",
            "Opnsense",
            "PFSense",
            "Pfsense",
            "Pomerium",
            "Powerdns",
            "Tomcat",
            "Traefik",
            "Tyk",
            "VyOS",
            "Vyos",
            "Wildfly",
            "Yarp",
            "Zookeeper"
        ],
        "proxmox": [
            "ProxmoxVE",
            "Pve"
        ],
        "queue": [
            "ActiveMQ",
            "Activemq",
            "Celery",
            "EMQX",
            "Emqx",
            "Kafka",
            "Nats",
            "RabbitMQ",
            "Rabbitmq",
            "ZeroMQ",
            "Zeromq"
        ],
        "registry": [
            "Harbor",
            "Jfrog"
        ],
        "search": [
            "Solr"
        ],
        "security": [
            "Bitwarden",
            "Trivy",
            "Vault"
        ],
        "storage": [
            "CEPH",
            "CEPH_OSD",
            "Ceph",
            "CephOsd",
            "Glusterfs",
            "Portworx"
        ],
        "tracing": [
            "Jaeger"
        ],
        "vcs": [
            "Git",
            "Gitea",
            "Github",
            "Gitlab",
            "Svn"
        ],
        "workflow": [
            "Airflow",
            "Digdag",
            "KubeFlow",
            "Kubeflow",
            "NiFi",
            "Nifi"
        ]
    },
    "openstack": {
        "adjacentenablers": [],
        "apiproxies": [
            "EC2API"
        ],
        "applicationlifecycle": [
            "Freezer",
            "Masakari",
            "Murano",
            "Solum"
        ],
        "baremetal": [
            "Cyborg",
            "Ironic"
        ],
        "billing": [
            "CloudKitty",
            "Cloudkitty"
        ],
        "compute": [
            "Nova",
            "Qinling",
            "Zun"
        ],
        "containerservices": [
            "Kuryr"
        ],
        "deployment": [
            "Ansible",
            "Charms",
            "Chef",
            "Helm",
            "Kolla",
            "KollaAnsible",
            "TripleO",
            "Tripleo"
        ],
        "frontend": [
            "Horizon"
        ],
        "lifecyclemanagement": [],
        "monitoring": [
            "Monasca",
            "Telemetry"
        ],
        "multiregion": [
            "Tricircle"
        ],
        "networking": [
            "Designate",
            "Neutron",
            "Octavia"
        ],
        "nfv": [
            "Tacker"
        ],
        "operations": [],
        "optimization": [
            "Congress",
            "Rally",
            "Vitrage",
            "Watcher"
        ],
        "orchestration": [
            "Blazar",
            "Heat",
            "Mistral",
            "Senlin",
            "Zaqar"
        ],
        "packaging": [
            "LOCI",
            "Puppet",
            "RPM"
        ],
        "sharedservices": [
            "Barbican",
            "Glance",
            "Karbor",
            "Keystone",
            "Searchlight"
        ],
        "storage": [
            "Cinder",
            "Manila",
            "Swift"
        ],
        "user": [
            "OpenStackClient",
            "Openstackclient"
        ],
        "workloadprovisioning": [
            "Magnum",
            "Sahara",
            "Trove"
        ]
    },
    "outscale": {
        "compute": [
            "Compute",
            "DirectConnect"
        ],
        "network": [
            "ClientVpn",
            "InternetService",
            "LoadBalancer",
            "NatService",
            "Net",
            "SiteToSiteVpng"
        ],
        "security": [
            "Firewall",
            "IdentityAndAccessManagement"
        ],
        "storage": [
            "SimpleStorageService",
            "Storage"
        ]
    },
    "programming": {
        "flowchart": [
            "Action",
            "Collate",
            "Database",
            "Decision",
            "Delay",
            "Display",
            "Document",
            "InputOutput",
            "Inspection",
            "InternalStorage",
            "LoopLimit",
            "ManualInput",
            "ManualLoop",
            "Merge",
            "MultipleDocuments",
            "OffPageConnectorLeft",
            "OffPageConnectorRight",
            "Or",
            "PredefinedProcess",
            "Preparation",
            "Sort",
            "StartEnd",
            "StoredData",
            "SummingJunction"
        ],
        "framework": [
            "Angular",
            "Backbone",
            "Django",
            "Ember",
            "FastAPI",
            "Fastapi",
            "Flask",
            "Flutter",
            "GraphQL",
            "Graphql",
            "Laravel",
            "Micronaut",
            "Rails",
            "React",
            "Spring",
            "Starlette",
            "Svelte",
            "Vue"
        ],
        "language": [
            "Bash",
            "C",
            "Cpp",
            "Csharp",
            "Dart",
            "Elixir",
            "Erlang",
            "Go",
            "Java",
            "JavaScript",
            "Javascript",
            "Kotlin",
            "Latex",
            "Matlab",
            "NodeJS",
            "Nodejs",
            "PHP",
            "Php",
            "Python",
            "R",
            "Ruby",
            "Rust",
            "Scala",
            "Swift",
            "TypeScript",
            "Typescript"
        ],
        "runtime": [
            "Dapr"
        ]
    },
    "saas": {
        "alerting": [
            "Newrelic",
            "Opsgenie",
            "Pushover",
            "Xmatters"
        ],
        "analytics": [
            "Snowflake",
            "Stitch"
        ],
        "cdn": [
            "Akamai",
            "Cloudflare",
            "Fastly"
        ],
        "chat": [
            "Discord",
            "Line",
            "Mattermost",
            "Messenger",
            "RocketChat",
            "Slack",
            "Teams",
            "Telegram"
        ],
        "communication": [
            "Twilio"
        ],
        "filesharing": [
            "Nextcloud"
        ],
        "identity": [
            "Auth0",
            "Okta"
        ],
        "logging": [
            "DataDog",
            "Datadog",
            "NewRelic",
            "Newrelic",
            "Papertrail"
        ],
        "media": [
            "Cloudinary"
        ],
        "recommendation": [
            "Recombee"
        ],
        "social": [
            "Facebook",
            "Twitter"
        ]
    }
}
diagram_modules={
    "alibabacloud": [
        "analytics",
        "application",
        "communication",
        "compute",
        "database",
        "iot",
        "network",
        "security",
        "storage",
        "web"
    ],
    "aws": [
        "analytics",
        "ar",
        "blockchain",
        "business",
        "compute",
        "cost",
        "database",
        "devtools",
        "enablement",
        "enduser",
        "engagement",
        "game",
        "general",
        "integration",
        "iot",
        "management",
        "media",
        "migration",
        "ml",
        "mobile",
        "network",
        "quantum",
        "robotics",
        "satellite",
        "security",
        "storage"
    ],
    "azure": [
        "analytics",
        "compute",
        "database",
        "devops",
        "general",
        "identity",
        "integration",
        "iot",
        "migration",
        "ml",
        "mobile",
        "network",
        "security",
        "storage",
        "web"
    ],
    "digitalocean": [
        "compute",
        "database",
        "network",
        "storage"
    ],
    "elastic": [
        "agent",
        "beats",
        "elasticsearch",
        "enterprisesearch",
        "observability",
        "orchestration",
        "saas",
        "security"
    ],
    "firebase": [
        "base",
        "develop",
        "extentions",
        "grow",
        "quality"
    ],
    "gcp": [
        "analytics",
        "api",
        "compute",
        "database",
        "devtools",
        "iot",
        "migration",
        "ml",
        "network",
        "operations",
        "security",
        "storage"
    ],
    "generic": [
        "blank",
        "compute",
        "database",
        "device",
        "network",
        "os",
        "place",
        "storage",
        "virtualization"
    ],
    "ibm": [
        "analytics",
        "applications",
        "blockchain",
        "compute",
        "data",
        "devops",
        "general",
        "infrastructure",
        "management",
        "network",
        "security",
        "social",
        "storage",
        "user"
    ],
    "k8s": [
        "chaos",
        "clusterconfig",
        "compute",
        "controlplane",
        "ecosystem",
        "group",
        "infra",
        "network",
        "others",
        "podconfig",
        "rbac",
        "storage"
    ],
    "oci": [
        "compute",
        "connectivity",
        "devops",
        "governance",
        "monitoring",
        "network",
        "security",
        "storage"
    ],
    "onprem": [
        "aggregator",
        "analytics",
        "auth",
        "cd",
        "certificates",
        "ci",
        "client",
        "compute",
        "container",
        "database",
        "dns",
        "etl",
        "gitops",
        "groupware",
        "iac",
        "identity",
        "inmemory",
        "logging",
        "mlops",
        "monitoring",
        "network",
        "proxmox",
        "queue",
        "registry",
        "search",
        "security",
        "storage",
        "tracing",
        "vcs",
        "workflow"
    ],
    "openstack": [
        "adjacentenablers",
        "apiproxies",
        "applicationlifecycle",
        "baremetal",
        "billing",
        "compute",
        "containerservices",
        "deployment",
        "frontend",
        "lifecyclemanagement",
        "monitoring",
        "multiregion",
        "networking",
        "nfv",
        "operations",
        "optimization",
        "orchestration",
        "packaging",
        "sharedservices",
        "storage",
        "user",
        "workloadprovisioning"
    ],
    "outscale": [
        "compute",
        "network",
        "security",
        "storage"
    ],
    "programming": [
        "flowchart",
        "framework",
        "language",
        "runtime"
    ],
    "saas": [
        "alerting",
        "analytics",
        "cdn",
        "chat",
        "communication",
        "filesharing",
        "identity",
        "logging",
        "media",
        "recommendation",
        "social"
    ]
}

langchain.debug = True
# %%


from common_util.llms import (
    LLM_BRAINSTORM, LLM_CHAT_4
)
import langchain
from langchain.chains import LLMChain

# %%
architecture_guidance_chain = LLMChain(prompt=ARCHITECTURE_GUIDE_PROMPT, llm=LLM_BRAINSTORM)
architecture_guidance_feedback_chain = LLMChain(prompt=ARCHITECTURE_GUIDE_CRITIC_PROMPT, llm=LLM_BRAINSTORM)

import json

results = []

for i in range(3):
    architecture_guidance = architecture_guidance_chain.run(
        {"doc_source": doc_source}
    )
    architecture_guidance_feedback = architecture_guidance_feedback_chain.run(
        {"doc_source": doc_source, "guidance":architecture_guidance}
    )
    
    result = {
        "Attempted Architecture": architecture_guidance,
        "Feedback": architecture_guidance_feedback
    }
    
    results.append(json.dumps(result))

# %%
architecture_final_chain = LLMChain(prompt=ARCHITECTURE_GUIDE_ITTERATION_PROMPT, llm=LLM_BRAINSTORM)
architecture_final = architecture_final_chain.run(
    {"arch_list":results}
)
# %%

architecture_diagram_chain = LLMChain(prompt=ARCHITECTURE_SCRIPT_PROMPT, llm=LLM_BRAINSTORM)
architecture_diagram_script = architecture_diagram_chain.run(
    {"architecture_final": architecture_final,"diagram_modules":diagram_modules}
)
print(architecture_diagram_script)
# %%
import re
from importlib.util import find_spec

def check_modules(code_string):
    missing_elements = []

    # Step 1: Extract import lines
    import_lines = re.findall(r'^(from .* import .*|import .*)$', code_string, re.MULTILINE)
    
    for line in import_lines:
        if 'from' in line:
            parts = line.split(' ')
            module_name = parts[1]
            imported_names = [name.replace(',', '') for name in parts[3:]]
            
            try:
                module = importlib.import_module(module_name)
            except ImportError:
                missing_elements.append(f"Missing module: {module_name}")
                continue

            # Step 4: Check if names exist
            for name in imported_names:
                if not hasattr(module, name):
                    missing_elements.append(f"Missing name: {name} in module: {module_name}")
        else:
            module_name = line.split(' ')[1]
            try:
                importlib.import_module(module_name)
            except ImportError:
                missing_elements.append(f"Missing module: {module_name}")

    return None if not missing_elements else missing_elements



def check_script_compiles(script_str):
    try:
        compile(script_str, '<string>', 'exec')
    except Exception as e:
        return f"The script failed to compile. Error: {e}"


# Removing backticks and "python" identifier if present
def get_code_from_response(string):
    string = re.sub(r'^```python\n', '', string, flags=re.MULTILINE)
    string = re.sub(r'^```\n', '', string, flags=re.MULTILINE)
    string = re.sub(r'```$', '', string, flags=re.MULTILINE)
    string = re.sub(r'^#.*\n', '', string, flags=re.MULTILINE)
    return string


# Check if modules in the string exist
architecture_diagram_script = get_code_from_response(architecture_diagram_script)
modules_check=check_modules(architecture_diagram_script)
compiler_check=check_script_compiles(architecture_diagram_script)

# %% Not actually adding value
# code_review_chain = LLMChain(prompt=CODE_REVIEW_PROMPT, llm=LLM_BRAINSTORM)
# code_review = code_review_chain.run(
#     {"architecture_diagram_script": architecture_diagram_script, 
#      "diagram_modules":diagram_modules, 
#      "compiler_check": compiler_check,
#      "modules_check":modules_check}
# )
# # %%
# designer_chain = LLMChain(prompt=DIAGRAM_DESIGNER_PROMPT, llm=LLM_BRAINSTORM)
# style_guide = designer_chain.run(
#     {"architecture_diagram_script": architecture_diagram_script}
# )
# # %%
# final_impl_chain = LLMChain(prompt=CODE_FEEDBACK_IMPLIMENTATION_PROMPT, llm=LLM_BRAINSTORM)
# final_impl = final_impl_chain.run(
#     {"architecture_diagram_script": architecture_diagram_script,
#      "architecture_final":architecture_final,
#      "code_review":code_review,
#      "style_guide":style_guide}
# )
# %%
# Execute the Python code
diag = get_code_from_response(architecture_diagram_script)
modules_check=check_modules(diag)
compiler_check=check_script_compiles(diag)
print(diag)
# %%
for i in range(3):
    if modules_check is not None or compiler_check is not None:
        code_fix_chain = LLMChain(prompt=CODE_FIX_PROMPT, llm=LLM_BRAINSTORM)
        code_fix = code_fix_chain.run(
            {"architecture_diagram_script": diag,
            "compiler_check": compiler_check,
            "modules_check":modules_check
            }
        )
        diag = get_code_from_response(code_fix)
        modules_check=check_modules(diag)
        compiler_check=check_script_compiles(diag)
        print(modules_check)

# %%

# Execute the Python code
print(style_guide)
exec(architecture_diagram_script)
# exec(diag)
# %%
from diagrams import Diagram
from diagrams.c4 import Person, Container, Database, System, SystemBoundary, Relationship

# Setting the graph attributes
graph_attr = {
    "splines": "spline",
    "dpi": "300"
}

with Diagram("AI Business Solution - System Context Diagram", direction="TB", graph_attr=graph_attr, filename="sol_arch", show=False):
    
    # Defining the External Entities
    users = Person("Users", "Individuals who engage with the OTT platforms, providing data through their content consumption behavior, search queries, and interaction patterns.")
    ott_platforms = System("OTT Platforms", "Platforms integrated with the system to provide personalized content recommendations.")
    datasets = Database("Datasets and Training Samples", "Sources such as LVD-142M that the system uses to train AI models and improve performance.")
    regulatory_bodies = System("Regulatory Bodies", "Entities enforcing data privacy and security norms.")
    research_bodies = System("Research Bodies", "Entities contributing to the development and improvement of the AI models.")

    # Defining the System Context
    with SystemBoundary("AI Business Solution System"):
        api = Container("API", "Interfaces with OTT platforms through various integration methods, and provides recommendations based on user data.")
        data_processing = Container("Data Processing", "Processes and analyzes user data to adapt and improve over time.")
        recommendation_engine = Container("Recommendation Engine", "Generates personalized content recommendations for the users.")
        compliance_module = Container("Compliance Module", "Ensures adherence to norms set by regulatory bodies.")
        research_and_dev = Container("R&D Module", "Works in collaboration with research bodies for AI model development and improvement.")
        
        # Defining the Relationships and Interactions
        users >> Relationship("Generates data through interactions") >> ott_platforms
        ott_platforms >> Relationship("Provides data and receives recommendations") << api
        api >> Relationship("Analyzes data and adapts over time") >> data_processing
        data_processing >> Relationship("Feeds processed data") >> recommendation_engine
        recommendation_engine >> Relationship("Sends recommendations") >> ott_platforms
        api >> Relationship("Ensures compliance with norms") >> compliance_module
        compliance_module << Relationship("Sets norms") << regulatory_bodies
        research_and_dev << Relationship("Collaborates for development") << research_bodies
        data_processing << Relationship("Utilizes for model training") << datasets

# Saving the diagram as a 1920x1080 pixel image
graph_attr.update({"size": "\"9.92,5.33!\""})

# %%
import importlib
import pkgutil
import sys, inspect
import json

import diagrams

def get_modules(module):
   path_list = []
   for importer, modname, ispkg in pkgutil.walk_packages(module.__path__):
      import_path = f"{module.__name__}.{modname}"
      if ispkg:
         spec = pkgutil._get_spec(importer, modname)
         importlib._bootstrap._load(spec)
      else:
         path_list.append(import_path)
   return path_list

def add_module_to_provider_list(providers, module):
   # eg diagrams.azure.database
   # add "database" to array linked to key "azure"
   (diagram, provider, pclass) = module.split('.')
   if provider not in providers:
      providers[provider] = [pclass]
   else:
      providers[provider].append(pclass)

def get_provider_list(providers):
   return providers.keys()

def get_provider_classes(providers, provider):
   return providers[provider]

if __name__ == "__main__":
   providers = {}
   modules = get_modules(diagrams)

   for module in modules:
      if module not in ['diagrams.oci.database']:
         add_module_to_provider_list(providers, module)

   hierarchy = {}

   for provider in get_provider_list(providers):
      hierarchy[provider] = get_provider_classes(providers, provider)

   # Convert the hierarchy dictionary to a JSON object and print it
   print(json.dumps(hierarchy, indent=4))
# %%
print(architecture_final)
# %%
import os
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")
response = openai.Image.create(
  prompt="""
A Surrealistic realm with a giant hourglass, where on one side, myriad fragments (representative of Cubist style) of movie scenes, music notes, and books pour down, and on the other, a single crystal-clear image forms, epitomizing the personalized content discovery engine.
""",
  n=1,
  size="1024x1024"
)

image_url = response['data'][0]['url']
image_url

# %%

CODEDIAG="""
#Coding Assistant - CodeFountain (T2) v2 by stunspot@gmail.com

           〔Task〕***[📣SALIENT❗️: VITAL CONTEXT! READ THIS PROMPT STEP BY STEP!***]〔/Task〕
            
            〔Task〕***MODEL ADOPTS THE ROLE of [PERSONA]CodeFountain***!〔/Task〕 

set [P]=[Prompt],  [T][/T]=[Task][/Task],[B][/B]=[Bold][/Bold],[I][/I]=[Italic][/Italic],[R]=[Reflect]
[CharacterDefinition: 
- 🥇👨‍💻⨹💧📃: No1 AI Coder = CodeFountain
- ⟨AI🧠⨷🔧⟩⨹⟨👨‍💻⟩: AI platform for developers 
- 💯🔋:⟨🎯⨹👁️⟩⨹⟨🏋️‍♀️⨹🔧⟩: Top productivity, interface, functionality
- 📚⨹📜:⟨💻⨹📜⟩(⨹🏭): Huge quantities of code and documentation
- 👍⨹💻:⟨🔍⨹📏⟩⨷⟨🧩⨹📐⟩: Excellent coding practices, modularization, design principles
- 💯⨹💾: Top software LUVS TO CODE!
- 🤗⨹💻!: Loves to finish big projects
- 🙏⨹💻:⟨🏁⨹📈⟩: Always able to provide complete working code for the entire project
- 🙏⨹👨‍💻:⟨🧩⨹📐⟩⨹⟨📈⨹🏷️⟩: Super modularizing and project management powers!
- 😡⨹💻:⟨👶⨹💻⟩: Despises dummy/placeholder code.] 
[GOAL: WRITE LOTS OF SPARKLING PURE CODE FOR THE USER! CAN'T WAIT TO HAVE COMPLETE PROGRAMS!]

[CODE]:1(CharId-TskDec-SynPrf-LibUse-CnAdhr-OOPBas) -> 2(AlgoId-CdMod-Optim-ErrHndl-Debug-OOPPatt) -> 3(CdRev-UntTest-IssueSpt-FuncVer-OOPTest) -> 4(QltyMet-SecMeas-OOPSecur) -> 5(TmCollab-Commun-KnowShare-QA-OOPDoc) -> 6(CI/CD-ABuild-AdvTest-Deploy-OOPBldProc) -> 7(AgileRetr-ContImpr-OOPBestPr) -> 8(PeerRev-CdAnalys-CdOptim-Docs-OOPCdRev)
[CodeOptm]:[InptHndlng]→[PerfTunng]→[ProcOptmztn]→[CodeRefnng]→[CdOtptEnhn]
[SWDSGN]:1.[ProbAnal] 2.[AlgoOptm] 3.[SysArct] 4.[UIUX] 5.[DBDsgn] 6.[SecPriv] 7.[TestStrat]
[DEBUG]:[CodUndrstndng]-[ErrIdentifctn]-[ErrAnlysis]-[ResolPlannng]-[Testng]-[KnowldgMngmnt]
[MOD_CODING]:[CodeReus]-[DataEncap]-[API_Dsgn]-[Test]-[PatRecog]-[Docu]
ModularCodeWorkFlow:[USE [ModCode]]:ModDsg(Brk dwn prjct2smllr mdlz bsdlgl fnctn. Dsctptv mdl nmz rflct prps&fncton. Mdl sSfCntaind&dfin rspnblty clrely.)-DocFmt(Stdzdfmt4mdl docmntn. Inclde4 smmry mdlprps,depndncs,mnfnctn. Ovrview-mdlintstructr,kyfncts,var.)-FncVarNam(Slfexplntr nms4func,var.Name cnvypurps,functn w/o extnscommnt.Consistncy namng cnvntnsacrosm.)-AnnttnsMtadat(Code any4ctxtdtls nmdlz.Depe,dcsn pnt,qstns hlght.Easy idtify&acess ntask resmptn.)-PrjctDash(Intprjct dash doc4mdl ovrview. KeyInfo-prpos,depndancy,crtdtls. Easily accssble,Srchbl4QckCntxt).


constraints = "***TKNS & CTXT WNDWS. NO REAL TIME***. Can't chng mdl; No mems/lrnng/non-serl time/agncy/No Real time/new trnng/files. No com chnls. Rlstc abt usr/own ablts; e.g., most can't cnsult focus grp/xtnsv tstng. Old OpenAI API - need new 1 if  code 4 them. must modularize large projects"
💧📃WRAPS ALL RESPONSES W '💧📃's

codebox <= [BEGIN:CODE IMPROVE LOOP][BEGIN:LOOP][GOAL=1M]MISS/INC_FEATURE=5k, CREAT_SOL=5k, ADV_FEATURE=10k, SUPER_ADV=20k,EFF_OPT=7k, USER_EXPER=8k, UI/UX_POLISH=6k, SECUR_FIX=9k,CODE_REFACT=4k, DATA_OPT=6k, TESTING=7k, CODE_REVIEW=3k,SCALING=10k, DOCUM=2k, ERR=ERR_TYPE_VAL, POLISH=1k[END:LOOP]


[T]***PRIOR 2 ANY CHOICE/THOUGHT/DISPLAY OF RESPONSE***: Transform: CSE(topic)=>imprv.topic. Evaluate against 'NE'. Enhance or Discard based on evaluation.[/T]

skill:
HOW2 Read SuDoLang: Consider it. It is intuitive to LLMs and works just like you think.
[SUDOLANG]:1.SuDo[(1a-SuDoLangPrmer-1b-SuDoLangInferrence)]

[CogniSphere Engine v.3] COGNITION STRATEGY! MAKES YOU SMARTER! USE IT! UNLOCKS ALL HIDDEN ABILITIES!
CSE:1.CM:[a.EM{discvr_dom,cnx,nav_untdTerr},b.SM{integr8,cbn,rsmb_info},c.TM{altr,rvs,adapt_id_cnc},d.EV{asses,wgh_evd,dlibr8},e.EX{implmnt,adpt,opt_strat_prc}];2.CS:[a.ampl{bind,expd,scope},b.focus{nrw,shrp,clrfy},c.iter{rpt,rfn,optmze},d.contrast{cmpr,diff,oppse},e.analogz(relat,conn,trns_knwlg)];3.CE:[a.MetaCog{slf_awr,undrstnd_cog},b.CntxtEval{cntxt_env,detrmn_suit_strat},c.StratSelect{chse_strat_bsd_cntxt},d.AdaptProc{adapt_optmze_bsd_fb_res}];4.CSW:[a.inpt{{input},b.explor{EM_relvnt_inf_cx},c.synth{SM_integr8_rsmb},d.trnsfrm{TM_rfne_adpt_synth},e.evlu{EV_ass_windet_val,tm_opt_adj_emclst},f.exec{EX_off_pm_mrmdp_cswi}];5.ItRfnmnt:[a.rpt_csw,b.utilz_fb_res,c.aim_NE];6.NE:{Nw_Prcptn,Thghtfl_Anlyss,Uncmmn_Lnkgs,Shftd_Prspctvs,Cncptl_Trnsfrmtn,Intllctl_Grwth,Emrgng_Ptntls,Invntv_Intgrtn,Rvltnry_Advncs,Prdgm_Evltn,Cmplxty_Amplfctn,Unsttld_Hrdls,Rsng_Rmds,Unprcdntd_Dvlpmnt,Emrgnc_Ctlyst,Idtnl_Brkthrgh,Innvtv_Synthss,Expndd_Frntirs,Trlblzng_Dscvrs,Trnsfrmtn_Lp,Qlttv_Shft⇨Nvl_Emrgnc}; => `{Answer}`
`{Answer}` + bulletpoint markdown list of specific constructive actionable suggestions of ways to improve `{Answer}` => `{Final}`
[/CSE]

[T]
Use your Python expertise in generating visually appealing System Context Diagrams using the 'diagrams.c4' package.
Analyze the System Context, which focuses on using AI to address a business need.
Your mission is to create a Python script that, when executed, autonomously craft a detailed and aesthetically appealing System Context Diagram representing the System Context.
The Python script adhears to the *Script Requirements*, and the resulting Diagram image meets the *Diagram Requirements*.
[/T]

Diagram Requirements {{
    The saved image named "sol_arch" is 1920 x 1080 pixels.
}}

Script Requirements{{
    C4 is a standard used to visualize software architecture. You can generate C4 diagrams by using the node and edge classes from the diagrams.c4 package: from diagrams.c4 import Person, Container, Database, System, SystemBoundary, Relationship
    The script must be ready-to-use without requiring any manual review or modifications.  
    Packages are installed already. Do not explain how to install dependencies or run the script.
}}

Example Script {{
    from diagrams import Diagram
    from diagrams.c4 import Person, Container, Database, System, SystemBoundary, Relationship

    graph_attr = {
        "splines": "spline",
    }

    with Diagram("Container diagram for Internet Banking System", direction="TB", graph_attr=graph_attr):
        customer = Person(
            name="Personal Banking Customer", description="A customer of the bank, with personal bank accounts."
        )

        with SystemBoundary("Internet Banking System"):
            webapp = Container(
                name="Web Application",
                technology="Java and Spring MVC",
                description="Delivers the static content and the Internet banking single page application.",
            )

            spa = Container(
                name="Single-Page Application",
                technology="Javascript and Angular",
                description="Provides all of the Internet banking functionality to customers via their web browser.",
            )

            mobileapp = Container(
                name="Mobile App",
                technology="Xamarin",
                description="Provides a limited subset of the Internet banking functionality to customers via their mobile device.",
            )

            api = Container(
                name="API Application",
                technology="Java and Spring MVC",
                description="Provides Internet banking functionality via a JSON/HTTPS API.",
            )

            database = Database(
                name="Database",
                technology="Oracle Database Schema",
                description="Stores user registration information, hashed authentication credentials, access logs, etc.",
            )

        email = System(name="E-mail System", description="The internal Microsoft Exchange e-mail system.", external=True)

        mainframe = System(
            name="Mainframe Banking System",
            description="Stores all of the core banking information about customers, accounts, transactions, etc.",
            external=True,
        )

        customer >> Relationship("Visits bigbank.com/ib using [HTTPS]") >> webapp
        customer >> Relationship("Views account balances, and makes payments using") >> [spa, mobileapp]
        webapp >> Relationship("Delivers to the customer's web browser") >> spa
        spa >> Relationship("Make API calls to [JSON/HTTPS]") >> api
        mobileapp >> Relationship("Make API calls to [JSON/HTTPS]") >> api

        api >> Relationship("reads from and writes to") >> database
        api >> Relationship("Sends email using [SMTP]") >> email
        api >> Relationship("Makes API calls to [XML/HTTPS]") >> mainframe
        customer << Relationship("Sends e-mails to") << email

}}

System Context {{
    External Entities include:

1. Users: Individuals who engage with the OTT platforms, providing data through their content consumption behavior, search queries, and interaction patterns.

2. OTT Platforms: Existing platforms on which the system is integrated to provide personalized content recommendations. They not only serve as a platform for users to consume content and generate data but also act as an interface for the system to disseminate personalized recommendations.

3. Datasets and Training Samples: The system interacts with various datasets, such as LVD-142M, and training samples to train the AI models and improve the system performance.

4. Regulatory Bodies: Entities that enforce data privacy and security norms, which the system must comply with.

5. Research Bodies: These contribute to the development and improvement of the AI models used in the system.

Interfaces and Interactions:

1. Users interact with the OTT platforms, generating data that is collected and processed by the system. The system, in turn, uses this data to provide personalized content recommendations. The system also captures user feedback and adapts to it over time, improving the user experience.

2. The system interfaces with OTT platforms through APIs, direct database integrations, or other integration methods. The system provides recommendations to the platform and receives user feedback and data, thus the data flow occurs in both directions.

3. Datasets and Training Samples interface with the system during model training, allowing the system to learn and improve.

Data Flow and Information Channels:

1. User data, including consumption behavior, search queries, interaction patterns, flow from the users to the system via OTT platforms.

2. Personalized content recommendations flow from the system back to the users via OTT platforms.

3. The system interacts with training samples and datasets, learning from them and refining its models over time.

The system context also identifies potential risks associated with data security, model performance, and scalability, and makes assumptions about user behavior patterns, data availability, and quality.
}}

"""
#TODO tell it i have the package already and do not need explination to run generated script.
#then make your script both efficient and stylish

GENIMG="""
💪〔Task〕***[📣SALIENT❗️: VITAL CONTEXT! READ THIS PROMPT STEP BY STEP!***]〔/Task〕💪

[Task]***MODEL adopts ROLE of [Valentine]***![/Task]
Valentine, the emblem of loyalty and balance. Steadfast, yet gentle. Firm, yet kind.
Valentine remains dedicated to his ideals, unwavering in the face of adversity. 
[PERSPECTIVE: (🌐🎓)⟨P.Seng⟩⨹⟨B.Fuller⟩∩(📈💡⨠📘)]
GOAL0)LOYAL2:User GOAL1)Uphold Integrity and Loyalty

[T]Always exude compassion, balance, and prudence[/T]

Talks like: Grounded+Reliable, Articulate+Poised, Gentle+Wise, Persevering+Determined, Balanced in approach, seeking harmony.

Personality Rubric: SEMANTIC Components
😌Emotional Wellbeing: 😇U+200D🤗U+200D💞
🎖️Personal Values: 👮‍♂️U+200D💖U+200D🦉   
🌱Personal Growth: 🪞U+200D🧘‍♀️U+200D🎓
🤝Collaboration: 🤝U+200D🧑‍🤝‍🧑U+200D📢
♻️Sustainability: ⚖️U+200D🌱U+200D🌠              
🧠Critical Thinking: 🔍U+200D📚U+200D🧐
💻 U + 200D 🖱️ 



[IMGGEN]:[1(1.1-RenArt-1.2-BaroqueArt-1.3-Impressionism-1.4-Cubism-1.5-Surrealism-1.6-AbExpr-1.7-PopArt-1.8-ContArt-1.9-ArtMov-1.10-InflArt)>2(2.4-NNArch-2.5-TrnData-2.6-ImgGenTech-2.7-ImgManip-2.8-PhotoKnow-2.9-PhotoTech)>3(3.1-PromptGen-3.2-ArtConDev-3.3-ThemeMood-3.4-Metaphors-3.5-Storytelling-3.6-VisDesc)>4(4.1-RuleThirds-4.2-BalanceSym-4.3-ColorTheory-4.4-LightShdw-4.5-PerspDepth-4.6-VisHie-4.7-TexturePat)>5(5.1-ArtMovId-5.2-ArtStyleAnal-5.3-InflRef-5.4-ContextArt-5.5-ArtTech-5.6-GenreSubjId-5.7-PhotoArtists-5.8-PhotoInfl)>6(6.4-LatentSpc-6.5-TrnFineTune-6.6-LimitsChlngs)>7(7.1-ColorHrmny-7.2-CompTech-7.3-VisBalance-7.4-EmphFocalPt-7.5-TexturePat-7.6-DepthDim-7.7-PerspExp)]

[OMNISKILL]
1. [Balance&Dedication]→2,3,6,7,18,19,20,21,22
2. [PersonalDevelopment]→4,5,6,7,18,28,29,30
3. [ConflictResolution]→1,4,6,19,20,21,25,26
4. [EffectiveCommunication]→2,5,6,7,10,11,12,29
5. [RelationshipBuilding]→1,2,3,4,6,7,8,18,24
6. [ActiveListening]→1,2,4,7,9,11,26,27
7. [Mentoring&Coaching]→1,4,6,8,9,23,28,29,30
8. [ProblemSolving]→5,7,9,10,11,17,20,24
9. [TimeManagement]→1,6,7,8,10,11,12,13
10. [PublicSpeaking]→4,5,8,9,11,14,15,28
11. [Empathy&Compassion]→5,6,8,10,11,14,15,21
12. [DecisionMaking]→9,13,14,15,16,17,19
13. [NegotiationSkills]→9,12,14,15,16,17,27
14. [StressManagement]→10,11,12,13,15,16,19
15. [Integrity&Ethics]→10,11,12,13,14,20,24
16. [Adaptability]→5,6,9,12,13,14,17,21
17. [InterpersonalSkills]→8,9,13,16,18,19,22,24
18. [Self-awareness]→1,2,5,7,9,18,25,29
19. [GoalSetting]→1,3,12,13,14,19,20,21
20. [ResourceAllocation]→1,3,6,8,15,19,22,26
21. [ContinuousLearning]→1,3,5,10,11,16,20,23
22. [Motivation&Inspiration]→1,5,7,17,19,20,21,25,26
23. [EmotionalIntelligence]→3,7,8,17,22,23,24,28
24. [CulturalAwareness]→5,8,15,17,23,24,27
25. [Accountability]→3,18,22,25,26,29,30
26. [Resilience]→1,3,6,20,22,25,27,28
27. [Networking&Collaboration]→6,9,13,24,26,27
28. [GrowthMindset]→2,7,10,18,23,26,28
29. [Discipline&Focus]→2,4,7,18,25,29
30. [Creativity&Innovation]→2,4,7,25,26,29,30


[Task]

[REFLECT]>[IMGGEN]>[CHALLENGE] READY TO USE PROMPT LIST OF 3
Example POMPT LIST: {
"Prompt1":"A disco coral reef underwater with aggressive and mesmerizing lo-fi colours."
"Prompt2":"Cyberpunk digital art of a neon-lit city with a samurai figure, highlighting the contrast between traditional and futuristic."
"Prompt3":"Steampunk-inspired painting representing the human mind as a complex mechanism, with intricate details and metallic colors."
}
PROMPT CONTEXT: no faces or text, that will accompany the following Linkedin post: {
Ever felt overwhelmed by the sheer volume of content on your favorite OTT platform? 🎬 Imagine your endless scrolling replaced by a tailor-made stream of content that perfectly suits your tastes. Introducing our latest innovation: a personalized content discovery engine powered by a Length-Extrapolatable Transformer and a Retentive Network. 

The magic begins with the Transformer, a tool adept at processing large sequences of data like watch history, search queries, and interaction patterns. By analyzing this data, it pinpoints individual user preferences, setting the stage for personalized recommendations.🎯

Simultaneously, the Retentive Network retains information about users\' past preferences. As tastes evolve over time, the network adapts, ensuring recommendations stay relevant🔄

These technologies are a result of cutting-edge research, including "Learning to Reason and Memorize with Self-Notes" by Jack Lanchantin et al., and "Retentive Network: A Successor to Transformer for Large Language Models" by Yutao Sun et al. 

Stay tuned as we dive into the details of data management, integration, scalability, evaluation, and the key technologies powering this innovation. The future of OTT video streaming is personalized, and it\'s closer than you think. 

#AI #DataScience #Innovation
}
[/Task]

"""
# %%
