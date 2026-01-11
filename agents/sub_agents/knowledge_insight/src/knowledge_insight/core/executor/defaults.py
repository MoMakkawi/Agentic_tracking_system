import json
import statistics
import collections
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import sklearn

DEFAULT_MODULES = {
    "collections": collections,
    "statistics": statistics,
    "defaultdict": defaultdict,
    "Counter": Counter,
    "datetime": datetime,
    "timedelta": timedelta,
    "json": json,
    "numpy": np,
    "pandas": pd,
    "sklearn": sklearn,
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
