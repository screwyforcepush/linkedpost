from enum import Enum

class PineconeNamespaceEnum(Enum):
    AI_RESEARCH = ('ai-research', 'catalog of ai academic research papers')
    VIDEO_STREAMING_ANALYTICS = ('video-streaming-analytics', 'best practices, metrics, and analytics within the video streaming domain')
    AI_ENGINEERING_DOCUMENTATION = ('ai-engineering-documentation', 'code documentation and readme files for ai engineering libraries')

    @property
    def value(self):
        return self._value_[0]

    @property
    def description(self):
        return self._value_[1]

    @classmethod
    def get_all_namespaces(cls):
        return {member.value: member.description for member in cls}
    
    @classmethod
    def get_all_namespace_names(cls):
        return [member.value for member in cls]
