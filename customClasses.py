from langchain.memory.entity import BaseEntityStore
from typing import Any, Optional
from langchain.prompts.prompt import PromptTemplate


class SQLiteEntityStore(BaseEntityStore):
    """SQLite-backed Entity store"""
    conn:object = None
    session_id: str = "default"
    table_name: str = "memory_store"

    def __init__(
        self,
        session_id: str = "default",
        db_file: str = "entities.db",
        table_name: str = "memory_store",
        *args: Any,
        **kwargs: Any,
    ):
        try:
            import sqlite3
        except ImportError:
            raise ImportError(
                "Could not import sqlite3 python package. "
                "Please install it with `pip install sqlite3`."
            )
        super().__init__(*args, **kwargs)

        self.conn = sqlite3.connect(db_file)
        self.session_id = session_id
        self.table_name = table_name
        self._create_table_if_not_exists()

    @property
    def full_table_name(self) -> str:
        return f"{self.table_name}_{self.session_id}"

    def _create_table_if_not_exists(self) -> None:
        create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {self.full_table_name} (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """
        with self.conn:
            self.conn.execute(create_table_query)

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        query = f"""
            SELECT value
            FROM {self.full_table_name}
            WHERE key = ?
        """
        cursor = self.conn.execute(query, (key,))
        result = cursor.fetchone()
        if result is not None:
            value = result[0]
            return value
        return default

    def set(self, key: str, value: Optional[str]) -> None:
        if not value:
            return self.delete(key)
        query = f"""
            INSERT OR REPLACE INTO {self.full_table_name} (key, value)
            VALUES (?, ?)
        """
        with self.conn:
            self.conn.execute(query, (key, value))

    def delete(self, key: str) -> None:
        query = f"""
            DELETE FROM {self.full_table_name}
            WHERE key = ?
        """
        with self.conn:
            self.conn.execute(query, (key,))

    def exists(self, key: str) -> bool:
        query = f"""
            SELECT 1
            FROM {self.full_table_name}
            WHERE key = ?
            LIMIT 1
        """
        cursor = self.conn.execute(query, (key,))
        result = cursor.fetchone()
        return result is not None

    def clear(self) -> None:
        query = f"""
            DELETE FROM {self.full_table_name}
        """
        with self.conn:
            self.conn.execute(query)

from namespaceEnum import PineconeNamespaceEnum
from pydantic import BaseModel, Field, validator

class ResearchInput(BaseModel):
    ai_query: str = Field(description="should be the question to be answered by research assistant")
    research_field: str = Field(description=f"must be one of{list(PineconeNamespaceEnum.get_all_namespace_names())}")
    @validator('research_field')
    def validate_research_field(cls, v):
        if v not in PineconeNamespaceEnum.get_all_namespace_names():
            raise ValueError(f'research_field must be one of {list(PineconeNamespaceEnum.get_all_namespace_names())}')
        return v    
    
class UpdateResearchMemoryInput(BaseModel):
    query: str = Field(description="should be the question the research will provide learnings about")
    namespace: str = Field(description=f"must be one of{list(PineconeNamespaceEnum.get_all_namespace_names())}")
    # dig_deeper: bool = Field(description="set to 'True' to get interesting tangental learnings")
    @validator('namespace')
    def validate_research_field(cls, v):
        if v not in PineconeNamespaceEnum.get_all_namespace_names():
            raise ValueError(f'namespace must be one of {list(PineconeNamespaceEnum.get_all_namespace_names())}')
        return v    
    
class UpdateResearchMemoryDeeperInput(BaseModel):
    query: str = Field(description="should be the question used inspire research assistant to provide tangental learnings")
    namespace: str = Field(description=f"must be one of{list(PineconeNamespaceEnum.get_all_namespace_names())}")
    @validator('namespace')
    def validate_research_field(cls, v):
        if v not in PineconeNamespaceEnum.get_all_namespace_names():
            raise ValueError(f'namespace must be one of {list(PineconeNamespaceEnum.get_all_namespace_names())}')
        return v    

#TODO use this to extract entity keys.
# need to update examples
#     
_CUSTOM_ENTITY_EXTRACTION_TEMPLATE = """You are an AI assistant reading the Abstract of a research paper. 

Extract all of the proper nouns, and names of processes, techniques, methodologies and metrics from the Abstract. 
Proper noun: as a guideline, a proper noun is generally capitalized.
Processes, techniques, methodologies and metric names: generally will be referred to, or defined, as a specific process, technique, methodology, metric, practice or simmilar. Reasonably inferable from the context.

You should definitely extract all names.

Return the output as a single comma-separated list, or NONE if there is nothing of note to return (e.g. the user is just issuing a greeting or having a simple conversation).

# EXAMPLE
## Abstract
The chain of thought prompting technique is a cognitive strategy that involves guiding individuals through a series of interconnected thoughts or ideas in order to stimulate their thinking process and generate new insights or perspectives. This technique is often used in brainstorming sessions, problem-solving exercises, or creative thinking activities.
## Output
Chain of Thought Prompting
END OF EXAMPLE

# EXAMPLE
## Abstract
Generative AI can be used to recreate dreams by using a combination of text-to-image generation, latent diffusion models, and AI+ ethics curricula. This technology can be used to create immersive experiences and can be applied to a variety of fields, such as education, art, and storytelling. Additionally, ethical considerations must be taken into account when using this technology.",
## Output
Generative AI, Text-to-Image Generation, Latent Diffusion Models, AI+ Ethics
END OF EXAMPLE

# EXAMPLE
## Abstract
The few-shot prompting technique is a method used in natural language processing (NLP) to generate instructions for various tasks without prior training. It involves using pre-trained language models (LLMs) to propose instructions. The technique has been evaluated using different metrics and LLM models, and the results show the zero-shot test accuracy on 24 Instruction Induction tasks.\n\nTo improve the quality of the instruction candidates, an iterative Monte Carlo search is employed.
## Output
Few-Shot Prompting, Zero-Shot Test, NLP, LLM, Monte Carlo Search
END OF EXAMPLE


## Abstract
{input}
## Output
"""

CUSTOM_ENTITY_EXTRACTION_PROMPT = PromptTemplate(
    input_variables=["input"], template=_CUSTOM_ENTITY_EXTRACTION_TEMPLATE
)

#%%
PineconeNamespaceEnum.__members__.values

# %%
