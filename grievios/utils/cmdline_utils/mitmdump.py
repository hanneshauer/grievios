import subprocess

from .cmdline_util import CmdlineUtil, CmdlineUtilUnavailableException


class Mitmdump(CmdlineUtil):
    name: str = "mitmdump"

    @staticmethod
    def subprocess(arguments: list[str] = None) -> subprocess:
        p: subprocess = None

        if arguments is None:
            arguments = []
        try:
            plog = b""
            p = subprocess.Popen(
                args=[Mitmdump.name] + arguments,
                stdout=subprocess.PIPE
            )
            while p.poll() is None and b"listening at" not in plog:
                plog += p.stdout.read(1)
        except subprocess.CalledProcessError as e:
            raise e
        except FileNotFoundError:
            raise CmdlineUtilUnavailableException
        return p
