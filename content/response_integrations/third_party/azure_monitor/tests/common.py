from __future__ import annotations

import pathlib

from integration_testing.common import get_def_file_content

INTEGRATION_PATH: pathlib.Path = pathlib.Path(__file__).parents[1]
CONFIG_PATH: pathlib.Path = pathlib.Path(__file__).parent / "config.json"
CONFIG = get_def_file_content(CONFIG_PATH)
