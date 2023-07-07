from enum import Enum

class PineconeNamespaceEnum(str, Enum):
    AI_RESEARCH = 'ai-research'
    VIDEO_STREAMING_ANALYTICS = 'video-streaming-analytics'
    AI_ENGINEERING_DOCUMENTATION = 'ai-engineering-documentation'

    @classmethod
    def get_all_namespaces(cls):
        return {member.name: member.value for member in cls}
