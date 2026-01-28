import os
import importlib
import traceback

from utils.plugin_status import (
    mark_plugin_loaded,
    mark_plugin_error
)

def load_plugins():
    for file in os.listdir("plugins"):
        if not file.endswith(".py") or file.startswith("_"):
            continue

        name = file
        try:
            importlib.import_module(f"plugins.{file[:-3]}")
            mark_plugin_loaded(name)
        except Exception as e:
            mark_plugin_error(name, traceback.format_exc())