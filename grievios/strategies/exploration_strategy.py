import logging
import os
import time

from appium import webdriver


class ExplorationStrategy:
    class Meta:
        platforms: list[str] = []

    wd: webdriver = None
    log_directory: os.path = None
    timeout: int = None
    logger: logging.Logger = None

    def __init__(self, wd: webdriver, log_directory: os.path, timeout: int = None):
        self.wd = wd
        self.log_directory = log_directory
        self.timeout = timeout
        self.logger = logging.getLogger(os.path.basename(log_directory))

    def run(self) -> None:
        stoptime: float = time.time() + self.timeout
        while time.time() < stoptime:
            self.interact()

    def interact(self):
        raise NotImplementedError
