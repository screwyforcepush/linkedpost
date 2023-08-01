from enum import Enum
from pydantic import BaseModel, Field

class PineconeNamespaceEnum(str, Enum):
    AI_RESEARCH = 'ai-research'
    VIDEO_STREAMING_ANALYTICS = 'video-streaming-analytics'
    AI_ENGINEERING_DOCUMENTATION = 'ai-engineering-documentation'
    WEB_SEARCH = 'web-search'

class PineconeNamespaceDescription(Enum):
    AI_RESEARCH = 'catalog of ai academic research papers'
    VIDEO_STREAMING_ANALYTICS = 'best practices, metrics, and analytics within the video streaming domain'
    AI_ENGINEERING_DOCUMENTATION = 'code documentation and architecture design for ai engineering libraries'
    WEB_SEARCH = 'results from past web searches'

def get_all_namespaces():
    return {PineconeNamespaceEnum[member].value: PineconeNamespaceDescription[member].value for member in PineconeNamespaceEnum.__members__}
def get_all_namespace_values():
    return [e.value for e in PineconeNamespaceEnum]

class NamespaceArg(BaseModel):
    f"""one of {get_all_namespace_values()}"""
    namespace: str = Field(..., description=f"Must be one of {get_all_namespace_values()}. Domain to query")
