from dataclasses import dataclass
import re
import subprocess

from .cmdline_util import CmdlineUtil, CmdlineUtilUnavailableException
from ...schemas import DeviceConnected


@dataclass
class IDevice:
    udid: str
    name: str
    os: str
    os_version: str


class IdeviceId(CmdlineUtil):
    name = "idevice_id"

    @staticmethod
    def run() -> list[DeviceConnected]:
        devices: list[DeviceConnected] = []
        try:
            idevice_ids: subprocess.CompletedProcess = subprocess.run(
                args=[IdeviceId.name],
                capture_output=True,
                check=True
            )
        except subprocess.CalledProcessError:
            return []
        except FileNotFoundError:
            raise CmdlineUtilUnavailableException
        for line in idevice_ids.stdout.split(b'\n'):
            re_result = re.search(r'^([a-zA-Z0-9\-]+).+\([USB]+\)$', line.decode('utf-8'))
            if re_result:
                udid = re_result.groups()[0]
                devices.append(DeviceConnected(udid=udid))

        return devices
