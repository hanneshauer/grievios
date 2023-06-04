import time

from .ios_strategy import iOSStrategy


class IdleStrategy(iOSStrategy):

    def interact(self):
        self.logger.info(f"Idling for 1 second")
        time.sleep(1)
        self.logger.info(f"Done idling")

