from __future__ import annotations

import json
import pathlib

INTEGRATION_PATH: pathlib.Path = pathlib.Path(__file__).parent.parent
CONFIG_PATH = pathlib.Path.joinpath(INTEGRATION_PATH, "tests", "config.json")

with CONFIG_PATH.open() as config_file:
    config_data = json.load(config_file)

TEST_BOT_TOKEN = config_data.get("API TOKEN", "test_bot_token")
