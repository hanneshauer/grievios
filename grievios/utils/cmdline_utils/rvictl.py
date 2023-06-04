import re
import subprocess

from .cmdline_util import CmdlineUtil, CmdlineUtilUnavailableException


class RvictlError(Exception):
    pass


class Rvictl(CmdlineUtil):
    name: str = "rvictl"

    @staticmethod
    def start_device(udid: str) -> str:
        success_re = re.compile(br"Starting device \w+ \[SUCCEEDED] with interface (?P<udid>\w+)")
        failure_re = re.compile(f"Starting device {udid} \[FAILED\]")

        try:
            p: subprocess.CompletedProcess = subprocess.run(
                args=[Rvictl.name, "-s", udid],
                capture_output=True,
                check=True
            )
            match = success_re.search(p.stdout)
            if not match:
                raise RvictlError
            return match.group("udid")
        except subprocess.CalledProcessError as e:
            raise RvictlError
        except FileNotFoundError as e:
            raise CmdlineUtilUnavailableException

    @staticmethod
    def stop_device(udid: str) -> None:
        try:
            p: subprocess.CompletedProcess = subprocess.run(
                args=["rvictl", "-x", udid],
                capture_output=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            raise RvictlError
        except FileNotFoundError as e:
            raise CmdlineUtilUnavailableException

    @staticmethod
    def list_devices():

        try:
            p: subprocess.CompletedProcess = subprocess.run(
                args=["rvictl", "-l"],
                capture_output=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            raise RvictlError
        except FileNotFoundError as e:
            raise CmdlineUtilUnavailableException
