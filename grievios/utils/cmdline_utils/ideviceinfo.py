import subprocess

from .cmdline_util import CmdlineUtil, CmdlineUtilUnavailableException
from ...schemas import DeviceConnected


class Ideviceinfo(CmdlineUtil):
    name = "ideviceinfo"

    @staticmethod
    def run(device: DeviceConnected, keys: list[str]) -> dict[str, str]:
        result = {}
        for key in keys:
            try:
                ideviceinfo: subprocess.CompletedProcess = subprocess.run(
                    args=[Ideviceinfo.name, "-u", device.udid, "-k", key],
                    capture_output=True,
                    check=True
                )
                result[key] = ideviceinfo.stdout.rstrip().decode("UTF-8")
            except subprocess.CalledProcessError:
                pass
            except FileNotFoundError:
                raise CmdlineUtilUnavailableException
        return result

