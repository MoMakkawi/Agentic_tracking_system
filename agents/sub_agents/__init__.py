"""
Sub-Agents Package
------------------
Exposes the main entry points for the various sub-agents.
"""

from .behavior_modeling import main as behavior_modeling_main
from .data_pipeline import main as data_pipeline_main
from .data_validation import main as data_validation_main
from .group_identification import main as group_identification_main

__all__ = [
    "behavior_modeling_main",
    "data_pipeline_main",
    "data_validation_main",
    "group_identification_main",
]