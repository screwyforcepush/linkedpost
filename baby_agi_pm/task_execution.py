from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema.language_model import BaseLanguageModel
from langchain.agents import ZeroShotAgent, Tool, AgentExecutor
from langchain import OpenAI, PromptTemplate, LLMChain


class TaskExecutionChain(LLMChain):
    """Chain to execute tasks."""

    @classmethod
    def from_llm(cls, llm: BaseLanguageModel, verbose: bool = True) -> LLMChain:
        """Get the response parser."""
        execution_template = (
            "You are an AI who performs one task based on the following objective: "
            "{objective}."
            "Take into account these previously completed tasks: {context}."
            " Your task: {task}. Response:"
        )
        prompt = PromptTemplate(
            template=execution_template,
            input_variables=["objective", "context", "task"],
        )
        return cls(prompt=prompt, llm=llm, verbose=verbose)

class TaskExecutionAgent(AgentExecutor):
    """Chain to execute tasks."""

    @classmethod
    def from_agent_and_tools(cls, llm: BaseLanguageModel, tools:[Tool], verbose: bool = True, max_iterations: int = 10) -> LLMChain:
        """Get the response parser."""

        FORMAT_INSTRUCTIONS = """Use the following format:

        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the detailed,at most comprehensive result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer based on my observation
        Final Answer: the final answer to the original input question is the full detailed explanation from the Observation provided as bullet points."""




        def _handle_error(error) -> str:
            INSTRUCTIONS = """Use the following format:
            
                  Thought: you should always think about what to do
                  Action: the action to take, should be one of [{tool_names}]
                  Action Input: the input to the action  
                  Observation: the detailed, comprehensive result of the action
                  Thought: I now know the final answer based on my observation
                  Final Answer: the final answer to the original input question is the full detailed explanation from the Observation provided as bullet points."""

            ouput = str(error).removeprefix("Could not parse LLM output: `").removesuffix("`")

            response = f"Thought: {ouput}\nThe above completion did not satisfy the Format Instructions given in the Prompt.\nFormat Instructions: {INSTRUCTIONS}\nPlease try again and conform to the format."
            # print("error msg: ", response)
            return response


        prefix = """System {{
            You are the Research and Development AI (RDAI). You always deliver high quality results swiftly. 
            Utilize examples and detailed explanations to ensure comprehensive understanding of your Task. 
            Your task is one of many that contributes to the Greater Objective.
            Account for the context of Previously Completed Tasks when constructing your Final Answer.
            }}

            Greater Objective {{
                {objective}
            }}

            Previously Completed Tasks {{
                {context}
            }}
            
            You have access to the following tools: """

        suffix = """/RDAI

        Task {{ 
            {task} 
            }}

        {agent_scratchpad}"""
        prompt = ZeroShotAgent.create_prompt(
            tools,
            prefix=prefix,
            suffix=suffix,
            format_instructions=FORMAT_INSTRUCTIONS,
            input_variables=["objective", "task", "context", "agent_scratchpad"],
        )

        llm_chain = LLMChain(llm=llm, prompt=prompt)

        # changed to tools from allowed_tools=tool_names in ZeroShotAgent param
        # tool_names = [tool.name for tool in tools]
        agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools, handle_parsing_errors=_handle_error)

        return cls(agent=agent, tools=tools, verbose=verbose, handle_parsing_errors=_handle_error, max_iterations=max_iterations)