import json
import statistics
import collections
from collections import Counter, defaultdict
from datetime import datetime, timedelta

DEFAULT_MODULES = {
    "collections": collections,
    "statistics": statistics,
    "defaultdict": defaultdict,
    "Counter": Counter,
    "datetime": datetime,
    "timedelta": timedelta,
    "json": json,
}

DEFAULT_BUILTINS = {
    "len": len,
    "sum": sum,
    "max": max,
    "min": min,
    "sorted": sorted,
    "list": list,
    "dict": dict,
    "set": set,
    "str": str,
    "int": int,
    "float": float,
}
