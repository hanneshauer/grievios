import os
import subprocess

from .cmdline_util import CmdlineUtil, CmdlineUtilUnavailableException


class InstallationError(Exception):
    pass


class UninstallationError(Exception):
    pass


class Ideviceinstaller(CmdlineUtil):
    name = "ideviceinstaller"

    @staticmethod
    def install_ipa(udid: str, path: os.path):
        try:
            p: subprocess.CompletedProcess = subprocess.run(
                args=[Ideviceinstaller.name, '-u', udid, '-i', path],
                capture_output=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            raise InstallationError
        except FileNotFoundError as e:
            raise CmdlineUtilUnavailableException

    @staticmethod
    def uninstall_ipa(udid: str, bundle_id: str):
        try:
            p: subprocess.CompletedProcess = subprocess.run(
                args=[Ideviceinstaller.name, '-u', udid, '-U', bundle_id],
                capture_output=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            raise UninstallationError
        except FileNotFoundError:
            raise UninstallationError

