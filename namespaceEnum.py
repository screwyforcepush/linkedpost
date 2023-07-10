from enum import Enum

class PineconeNamespaceEnum(str, Enum):
    AI_RESEARCH = 'ai-research'
    VIDEO_STREAMING_ANALYTICS = 'video-streaming-analytics'
    AI_ENGINEERING_DOCUMENTATION = 'ai-engineering-documentation'

class PineconeNamespaceDescription:
    AI_RESEARCH = 'catalog of ai academic research papers'
    VIDEO_STREAMING_ANALYTICS = 'best practices, metrics, and analytics within the video streaming domain'
    AI_ENGINEERING_DOCUMENTATION = 'code documentation and readme files for ai engineering libraries'

def get_all_namespaces():
    return {member: PineconeNamespaceDescription.__dict__[member] for member in PineconeNamespaceEnum.__members__}

def get_all_namespace_values():
    return [e.value for e in PineconeNamespaceEnum]
