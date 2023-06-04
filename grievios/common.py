import os
import pathlib


def grievios_base_path() -> pathlib.Path:
    return pathlib.Path(os.getenv("GRIEVIOS_DIR", "~/.grievios")).expanduser()
