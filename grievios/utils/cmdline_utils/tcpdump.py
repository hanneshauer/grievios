import subprocess

from .cmdline_util import CmdlineUtil, CmdlineUtilUnavailableException


class Tcpdump(CmdlineUtil):
    name: str = "tcpdump"
    p: subprocess = None

    def run(self, interface: str = None, output_file: str = None, sudo: bool = False):
        try:
            self.p = subprocess.Popen(
                args=
                (['sudo'] if sudo else []) +
                [Tcpdump.name] +
                (['-i', interface] if interface else []) +
                (['-w', output_file] if output_file else [])
            )
        except subprocess.CalledProcessError as e:
            raise e
        except FileNotFoundError as e:
            raise CmdlineUtilUnavailableException(e)

    def terminate(self):
        self.p.terminate()
