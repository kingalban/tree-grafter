from __future__ import annotations
from tree_grafter import JSONLike
from typing import Any, Callable, TypeVar
from functools import reduce
import yaml
import json


T1 = TypeVar("T1")
T2 = TypeVar("T2")


def j_print(obj: JSONLike):
    print(json.dumps(obj, indent=2))


def y_print(obj: JSONLike):
    print(yaml.dump(obj, default_flow_style=False))


def pipe(data: T1, *funcs: Callable) -> Any:
    """ margittr style %>% pipe, for applying a series of functions """
    return reduce(lambda res, fn: fn(res), funcs, data)


def T(func: Callable[[T1], T2]) -> Callable[[T1], T1]:
    """ magrittr style 'T pipe' %T>% """
    def _t(data):
        func(data)
        return data
    return _t
