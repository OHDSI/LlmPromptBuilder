"""
llm_prompt_builders/__init__.py
Dynamic function re-exporter.
"""

import inspect
import importlib
import pkgutil
from types import ModuleType
from typing import Callable, Dict, List

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
