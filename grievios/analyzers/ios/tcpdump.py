import datetime
import os

from .ios_analyzer import iOSAnalyzer
from ..exploration_analyzer import AnalyzerError
from ...exploration.exploration_session_options import ExplorationSessionOptions
from ...utils.cmdline_utils.cmdline_util import CmdlineUtilUnavailableException
from ...utils.cmdline_utils import rvictl
from ...utils.cmdline_utils.tcpdump import Tcpdump


class TcpdumpAnalyzer(iOSAnalyzer):
    p: Tcpdump = None

    def __init__(self, exploration_session_options: ExplorationSessionOptions):
        super().__init__(exploration_session_options)

        rvi_interface: str = None

        self.logger.info(f"Creating RVI for {self.exploration_session_options.device_udid}")
        try:
            self.rvi_interface = rvictl.Rvictl.start_device(udid=exploration_session_options.device_udid)
        except rvictl.RvictlError as e:
            self.logger.error(f"Failed to create RVI for {exploration_session_options.device_udid}")
            raise AnalyzerError
        except CmdlineUtilUnavailableException as e:
            self.logger.error(f"rvictl not avilable")
            raise AnalyzerError(e)
        self.logger.info(f"Created RVI: {self.rvi_interface}")
        self.logger.info("Starting Tcpdump")
        try:
            self.p = Tcpdump()
            self.p.run(interface=self.rvi_interface,
                       output_file=str(os.path.join(self.exploration_session_options.log_directory, datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.pcap')), # TODO: datetime.datetime.now().isoformat()
                       sudo=True)
        except Exception as e:
            self.logger.error(f"Failed to run tcpdump: {e}")
            raise e

    def __del__(self):
        try:
            self.logger.info("Terminating tcpdump")
            self.p.terminate()
        except Exception as e:
            self.logger.error(f"Failed to terminate tcpdump: {e}")
        try:
            self.logger.info(f"Removing RVI for {self.exploration_session_options.device_udid}")
            rvictl.Rvictl.stop_device(self.exploration_session_options.device_udid)
        except rvictl.RvictlError as e:
            self.logger.error(f"Failed to remove RVI for {self.exploration_session_options.device_udid}: {e}")
