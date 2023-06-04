import os

from ..exploration_analyzer import ExplorationAnalyzer

class iOSAnalyzer(ExplorationAnalyzer):
    class Meta:
        platforms: list[str] = ['iPhone OS']
