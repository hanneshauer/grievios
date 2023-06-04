import collections
import json
import queue
import time

import networkx

from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import InvalidElementStateException

from ..exploration_strategy import ExplorationStrategy


class iOSStrategy(ExplorationStrategy):
    class Meta:
        platforms: list[str] = ['iPhone OS']

    class XCUIElement:
        def __init__(self, properties_dict):
            for key in properties_dict:
                if key != 'children':
                    setattr(self, key, properties_dict[key])

        def __eq__(self, other):
            comparison_values = ['type', 'rect', 'name', 'label']
            for attribute_name in comparison_values:
                if getattr(self, attribute_name, None) != getattr(other, attribute_name, None):
                    return False
            return True

        def __lt__(self, other):
            return self.rect('y'), self.rect('x') < other.rect('y'), other.rect('x')

        def __hash__(self):
            return hash((frozenset(self.rect),
                         self.label if self.label else "",
                         self.name if self.name else "",
                         self.value if self.value else ""
                         ))

        def get_wd_element(self, wd: webdriver):
            return wd.find_element(
                by=AppiumBy.IOS_PREDICATE,
                value=
                f"type == 'XCUIElementType{self.type}' AND "
                f"rect.x == {self.rect['x']} AND "
                f"rect.y == {self.rect['y']}"
            )

        INTERACTIONS = {
            'tap': ['Button']
        }
        ELEMENT_INTERACTIONS = {
            'Button': ['tap']
        }

    def interact(self):
        graph = self.parse_json_source()

    def parse_json_source(self) -> networkx.DiGraph:
        IGNORE_TYPES = [
            'Keyboard',
            'StatusBar'
        ]

        graph = networkx.DiGraph()

        try:
            json_source = self.wd.execute_script('mobile:source', {'format': 'json'})
        except InvalidElementStateException as ex:
            self.logger.error(f'Failed to get UI source representation: {ex.msg}')
            return graph
        children = json_source.pop('children', [])
        root_el = self.XCUIElement(json_source)
        graph.add_node(root_el)

        q: queue.Queue = queue.Queue()
        for child in children:
            q.put((child, root_el))
        while not q.empty():
            (el, parent) = q.get()
            if el.get('type', '') in IGNORE_TYPES:
                continue
            children = el.pop('children', [])
            el = self.XCUIElement(el)
            graph.add_node(el)
            graph.add_edge(parent, el)
            for child in children:
                q.put((child, el))

        return graph
