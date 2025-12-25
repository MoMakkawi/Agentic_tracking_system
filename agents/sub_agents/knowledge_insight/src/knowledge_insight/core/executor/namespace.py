from typing import Any, Dict, Optional, Set
from .defaults import DEFAULT_MODULES, DEFAULT_BUILTINS

class NamespaceBuilder:
    """Builds execution namespaces with controlled access to modules and data."""

    def __init__(
        self,
        modules: Optional[Dict[str, Any]] = None,
        helpers: Optional[Dict[str, Any]] = None,
        datasets: Optional[Dict[str, Any]] = None,
        builtins: Optional[Dict[str, Any]] = None,
    ):
        self.modules = {**DEFAULT_MODULES, **(modules or {})}
        self.builtins = {**DEFAULT_BUILTINS, **(builtins or {})}
        self.helpers = helpers or {}
        self.datasets = datasets or {}

    def build(self) -> Dict[str, Any]:
        namespace = {
            **self.modules,
            **self.builtins,
            **self.helpers,
            **self.datasets,
            "result": None,
        }
        return namespace
