from . import ios_strategy
from . import idle
from . import random_button


def availableStrategies():
    return [cls.__name__ for cls in ios_strategy.iOSStrategy.__subclasses__()]
