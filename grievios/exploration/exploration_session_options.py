from dataclasses import dataclass
import os

@dataclass
class ExplorationSessionOptions:
    command_executor: str
    device_udid: str
    bundle_id: str
    wda_bundle_id: str
    strategy: str
    log_directory: os.path
    analyzers: list[str] = None
    benchmarks:str = None
    timeout: int = 55
    bundle_installed: bool = False
