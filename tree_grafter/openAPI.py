"""
    Functions for modifying openAPI docs.
    openAPI yaml documents make internal references for succinctness
    these look like: '- "$ref": "#/some/path/to/MyObject"'
"""
from __future__ import annotations
from tree_grafter import JSONLike, PathType, apply_transformations, ReplaceNode, deep_getitem
from tree_grafter.utils import pipe
from functools import reduce
from typing import Callable, Union, List, Dict, TypeVar, Any, Generator, Tuple, Optional


def is_property(node: Any) -> bool:
    """ is a json-schema style property """
    if not isinstance(node, dict):
        return False
    if "type" not in node:
        return False
    if not isinstance(node["type"], (list, tuple, str)):
        return False
    return True


def add_nulls(_tree: JSONLike, path: PathType, node: Any) -> Optional[ReplaceNode]:
    """ adds 'null' to all jsonschema like entries with a 'type' key
        eg: {"type": "object": ...} => {"type": ["null", "object"]: ...}
    """
    if is_property(node) and "null" not in node["type"]:
        current_types = node["type"] if isinstance(node["type"], list) else [node["type"]]
        node["type"] = current_types if "null" in current_types else ["null"] + current_types
        return ReplaceNode(node, 0)
    return None


def fill_refs(_tree: JSONLike, path: PathType, node: Any) -> Optional[ReplaceNode]:
    """ fill all "$ref": "#/..." fields with their value from the tree """
    if path and path[-1] == "$ref":
        assert isinstance(node, str), f"expected '$ref' path to be a string, not {type(node)} ({node=})"
        assert node.startswith("#"), f"path must start at root (#), not {node[0]} ({node=})"
        return ReplaceNode(deep_getitem(_tree, node.strip("#/").split("/")))
    return None


def combine_allOf(_tree: JSONLike, path: PathType, node: Any) -> Optional[ReplaceNode]:
    """ json-schema 'allOf' is the union of properties - combine explicitly """
    if path and path[-1] == "allOf":
        return ReplaceNode(reduce(lambda d1, d2: {**d1, **d2}, node))
    return None


def remove_excess_keys(allowed_keys=("type", "properties", "items", "format")
                       ) -> Callable[[JSONLike, PathType, Any], Optional[ReplaceNode]]:
    """ removes uninteresting properties from json-schemas"""
    def func(_tree: JSONLike, path: PathType, node: Any) -> Optional[ReplaceNode]:
        if is_property(node) and set(node) - set(allowed_keys):
            return ReplaceNode({k: v for k, v in node.items() if k in allowed_keys}, 0)
        return None
    return func


def hide_pagination(_tree: JSONLike, path: PathType, node: Any) -> Optional[ReplaceNode]:
    """ Specific for Recurly API use case.
        Pagination is silently handled by the python client
    """
    if is_property(node) \
            and "properties" in node \
            and "data" in node["properties"]:
        return ReplaceNode(node["properties"]["data"]["items"], 0)
    return None


def parse_openAPI_doc(openAPI_doc: JSONLike) -> JSONLike:
    """ fill refs and combine allOf in a openAPI doc """
    return pipe(openAPI_doc,
                apply_transformations(fill_refs),
                apply_transformations(combine_allOf))
