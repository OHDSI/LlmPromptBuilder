"""
llm_prompt_builders/__init__.py
Dynamic function re-exporter.
"""

import inspect
import importlib
from importlib import import_module
import pkgutil
from types import ModuleType
from typing import Callable, Dict, List
from pathlib import Path
import sys as _sys

__all__: List[str] = []          # populated at import time
_functions: Dict[str, Callable] = {}  # optional: keep a registry if you need it


def _load_all_functions() -> None:
    """
    Walk every sub-module inside the current package, import it,
    and pull any *top-level* functions up into this namespace.
    """
    pkg_name = __name__
    pkg = importlib.import_module(pkg_name)

    for _, mod_name, is_pkg in pkgutil.walk_packages(
        pkg.__path__,  prefix=f"{pkg_name}."
    ):
        if is_pkg:
            # Skip sub-packages; walk_packages will recurse automatically.
            continue

        try:
            module: ModuleType = importlib.import_module(mod_name)
        except Exception as err:
            # Optionally log so failures don’t kill the import chain.
            # print(f"⚠️  Skipped {mod_name}: {err}")
            continue

        for obj_name, obj in inspect.getmembers(module, inspect.isfunction):
            # Skip dunder helpers, etc.  Tighten/loosen as desired.
            if obj_name.startswith("_"):
                continue

            # Don’t overwrite if a name already exists.
            if obj_name in globals():
                # Optionally warn or raise.
                continue

            globals()[obj_name] = obj
            __all__.append(obj_name)
            _functions[obj_name] = obj


# Do the work once at import time.
_load_all_functions()

# Optional: provide a lazy fallback so unknown attributes are still searched.
def __getattr__(name: str):
    if name in _functions:
        return _functions[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# --- Prompt-helper aliases -----------------------------------------------
# Makes every file in llm_prompt_builders/prompts/ importable as a top-level
# module, so `from is_relevant import ...` keeps working.
_prompts_dir = Path(__file__).parent

for _file in _prompts_dir.glob("*.py"):
    if _file.name == "__init__.py":
        continue
    _alias = _file.stem                     # e.g. "is_relevant"
    _full  = f"{__name__}.{_alias}"         # e.g. "llm_prompt_builders.prompts.is_relevant"
    _sys.modules.setdefault(_alias, import_module(_full))

for _name in (
    "_file",
    "_alias",
    "_full",
    "_prompts_dir",
    "import_module",
    "Path",
    "_sys",
):
    globals().pop(_name, None)        # quietly ignore if the symbol never existed