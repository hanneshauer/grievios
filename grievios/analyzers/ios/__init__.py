from . import ios_analyzer
from . import mitmdump
from . import tcpdump


def availableAnalyzers():
    return [cls.__name__ for cls in ios_analyzer.iOSAnalyzer.__subclasses__()]
