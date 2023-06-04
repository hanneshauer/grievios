import datetime
import os
import subprocess


from .ios_analyzer import iOSAnalyzer
from ...exploration.exploration_session_options import ExplorationSessionOptions
from ...utils.cmdline_utils.mitmdump import Mitmdump


class MitmDumpAnalyzer(iOSAnalyzer):
    mitmdump_process: subprocess = None

    def __init__(self, exploration_session_options: ExplorationSessionOptions):
        super().__init__(exploration_session_options)
        self.logger.info("Starting mitmdump process")
        self.mitmdump_process = Mitmdump.subprocess(
            arguments=
            ["-w",
             os.path.join(self.exploration_session_options.log_directory, datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.mitmdump')
             ]
        )
        self.logger.info("mitmdump started")
        self.logger.info("MitmDumpAnalyzer inited")

    def __del__(self):
        self.logger.info("Terminating mitmdump process")
        self.mitmdump_process.terminate()
        self.logger.info("MitmDumpAnalyzer deleted")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.info("Terminating mitmdump process")
        self.mitmdump_process.terminate()
        self.logger.info("MitmDumpAnalyzer exited")
