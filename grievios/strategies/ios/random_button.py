import random
from selenium.common.exceptions import NoSuchElementException

from .ios_strategy import iOSStrategy


class RandomButtonStrategy(iOSStrategy):

    def interact(self):
        graph = self.parse_json_source()
        self.logger.debug(f'graph: {graph}')
        buttons = list(filter(lambda el: el.__dict__.get('isVisible', '0') == '1' and el.__dict__.get('type', '') in self.XCUIElement.INTERACTIONS['tap'], graph.nodes))
        if not buttons:
            self.logger.info(f'No buttons found')
            return
        selected_button = random.choice(buttons)
        self.logger.debug(f'selected button: {selected_button}')
        try:
            appium_element = selected_button.get_wd_element(self.wd)
            appium_element.click()
        except NoSuchElementException:
            self.logger.warning(f'WebDriver couldnt find selected buttton')

