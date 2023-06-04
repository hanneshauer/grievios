import logging
import os

from ..exploration.exploration_session_options import ExplorationSessionOptions


class AnalyzerError(Exception):
    pass


class ExplorationAnalyzer:
    class Meta:
        platforms: list[str] = []

    exploration_session_options: ExplorationSessionOptions = None
    logger: logging.Logger = None

    def __init__(self, exploration_session_options: ExplorationSessionOptions):
        self.exploration_session_options = exploration_session_options
        self.logger = logging.getLogger(os.path.basename(exploration_session_options.log_directory))
