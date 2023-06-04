import datetime
import logging
import os
from typing import Type

from appium import webdriver
from appium.options.ios import XCUITestOptions
from selenium.common.exceptions import WebDriverException
from urllib3.exceptions import MaxRetryError

from .exploration_session_options import ExplorationSessionOptions
from ..common import grievios_base_path
from .. import analyzers
from .. import strategies
from ..utils.cmdline_utils import ideviceinstaller, Ideviceinstaller
from ..utils.cmdline_utils.cmdline_util import CmdlineUtilUnavailableException


class ServerUnavailableError(Exception):
    pass


class ExplorationFailedError(Exception):
    pass


class ExplorationStartFailedError(Exception):
    cause: Exception

    def __init__(self, cause: Exception):
        self.cause = cause


class ExplorationSession:
    analyzer_instance: analyzers.ios.ios_analyzer.iOSAnalyzer = None
    analyzer_instances: list[analyzers.ios.ios_analyzer.iOSAnalyzer] = None

    def __init__(self, app, options: ExplorationSessionOptions):
        self.app = app
        self.options = options
        self.appium_wd: webdriver = None
        self.logger = logging.getLogger(os.path.basename(self.options.log_directory))

    def __enter__(self):
        try:
            os.makedirs(self.options.log_directory, exist_ok=True)
        except OSError as e:
            raise ExplorationStartFailedError(cause=e)
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(levelname)s in %(module)s - %(message)s')
        file_logger = logging.FileHandler(
            os.path.join(self.options.log_directory, datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.log'))
        file_logger.setFormatter(formatter)
        self.logger.addHandler(file_logger)

        if not self.options.bundle_installed:
            try:
                self.logger.info(f'Installing bundle {self.options.bundle_id} IPA onto {self.options.device_udid}')
                Ideviceinstaller.install_ipa(self.options.device_udid,
                                             grievios_base_path() / 'IPAs' / f'{self.options.bundle_id}.ipa')
            except ideviceinstaller.InstallationError as e:
                self.logger.error(f'Failed to install {self.options.bundle_id} IPA')
                raise ExplorationStartFailedError(cause=e)
            except CmdlineUtilUnavailableException as e:
                self.logger.error(f"ideviceinstaller is required for app installation")
                raise ExplorationStartFailedError(cause=e)

        analyzerClasses: filter[Type[analyzers.ios.ios_analyzer.iOSAnalyzer]] = filter(
            lambda c: c.__name__ in self.options.analyzers,
            analyzers.ios.ios_analyzer.iOSAnalyzer.__subclasses__()
        )
        self.analyzer_instances = [analyzerClass(exploration_session_options=self.options) for analyzerClass in
                                   analyzerClasses]

        options = XCUITestOptions()
        options.udid = self.options.device_udid
        options.bundle_id = self.options.bundle_id
        options.updated_wda_bundle_id = self.options.wda_bundle_id
        try:
            self.appium_wd = webdriver.Remote(self.options.command_executor, options=options)
        except MaxRetryError:
            raise ServerUnavailableError
        except WebDriverException as e:
            raise ExplorationStartFailedError(e)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.appium_wd:
            self.logger.info(f'Quitting app {self.options.bundle_id}')
            self.appium_wd.execute_script('mobile: terminateApp', {'bundleId': self.options.bundle_id})
            self.logger.info(f'Quitting Webdriver connection')
            self.appium_wd.quit()

            if not self.options.bundle_installed:
                self.logger.info(f'Uninstalling bundle {self.options.bundle_id} IPA')
                Ideviceinstaller.uninstall_ipa(self.options.device_udid, self.options.bundle_id)

            self.analyzer_instances = []

            for handler in self.logger.handlers:
                handler.close()

    def start(self):
        self.logger.info(f'Starting exploration session')

        strategyClass: Type[strategies.ios.ios_strategy.iOSStrategy] = next(filter(
            lambda c: c.__name__ == self.options.strategy,
            strategies.ios.ios_strategy.iOSStrategy.__subclasses__()),
            strategies.ios.ios_strategy.iOSStrategy)
        strategy_instance = strategyClass(wd=self.appium_wd, log_directory=self.options.log_directory,
                                          timeout=self.options.timeout)
        strategy_instance.run()
