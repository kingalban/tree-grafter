"""
tree_grafter provides tools to manipulate json like
datastructures, generally made of python dicts and lists.

At the core the function `walk_tree` is a generator
which will yield node of the tree and receive instructions
on mutating the tree.
To simplify this `apply_transformations` will handle
apply mutating functions to each node of the tree.
"""
from __future__ import annotations
from copy import deepcopy
from collections import deque
from dataclasses import dataclass
from functools import reduce
from typing import Callable, TypeVar, Any, Generator, Tuple, Optional, Type, Sequence


@dataclass(frozen=True, slots=True)
class ReplaceNode:
    """ Signal to tree_walker() to replace a node.
        value: the replacement value
        depth: the distance from the current node (eg parent node: depth=-1)
    """
    value: Any
    depth: int = -1

    def __post_init__(self):
        assert self.depth < 1, "Cannot replace child node"


class NextPathPlease:
    """ Signal to tree_walker to move to the next path in the queue """
    def __init__(self):
        raise NotImplementedError("Please pass as class, not instance")


KeyType = str | int
JSONLike = dict[KeyType, "JSONLike"] | list["JSONLike"]
PathType = Sequence[KeyType]
TransformerFunction = Callable[[JSONLike, PathType, Any], Optional[ReplaceNode]]


def deep_getitem(tree: JSONLike, path: PathType):
    return reduce(lambda obj, key: obj[key], path, tree)


class DeepIndexError(Exception):
    pass


def deep_setitem(tree: JSONLike, path: PathType, value: Any):
    """ Warning: This is a mutating function """
    assert path, f"Cannot replace root of tree"
    try:
        if len(path) == 1:
            tree[path[0]] = value  # type: ignore   # if we try to index a list with a str, we'll deal with it
        else:
            deep_setitem(tree[path[0]], path[1:], value)  # type: ignore
    except (KeyError, IndexError) as e:
        raise DeepIndexError(f"Failed to set or recurse into object. {path=!r}, {tree=!r}") from e


def walk_tree(tree: JSONLike) -> Generator[Tuple[JSONLike, PathType, Any],              # yields
                                           ReplaceNode | Type[NextPathPlease] | None,   # accepts to '.send'
                                           JSONLike]:                                   # returns in StopIteration
    def get_next(_node, prev=None) -> list[PathType]:
        prev = prev or []
        if isinstance(_node, list):
            return [prev + [i] for i, _ in enumerate(_node)]
        if isinstance(_node, dict):
            return [prev + [k] for k in _node]
        return []

    que = deque(get_next(tree))
    while que:
        path = que.pop()
        try:
            node = deep_getitem(tree, path)
        except (KeyError, IndexError):   # tree must have been mutated
            continue

        resp = yield tree, path, node

        while resp is not NextPathPlease:
            if isinstance(resp, ReplaceNode): # NOTE: cannot replace root!
                replacement_path = path[:resp.depth] if resp.depth < 0 else path
                deep_setitem(tree, replacement_path, resp.value)

                try:
                    node = deep_getitem(tree, path)
                except (KeyError, IndexError):   # tree must have been mutated
                    # print("WARNING: tree mutated between transformations on same node "
                    #       f"- should not cause error!\n{tree=}\n{path=}\n{node=}\n{resp=}", 
                    #       file=sys.stderr)
                    # raise
                    """ The node at the current path is gone """
                    break

                if replacement_path not in que:
                    que.append(replacement_path)

            resp = yield tree, path, node
        else:
            que.extend(get_next(node, path))

    return tree


def stroll_tree(tree):
    """ Iterate over the (tree, path, node) without sending changes """
    walker = walk_tree(tree)
    while True:
        try:
            yield next(walker)
            walker.send(NextPathPlease)
        except StopIteration:
            return


def apply_transformations(*transformers: TransformerFunction) -> Callable[[JSONLike], JSONLike]:
    """ Test each transformer on each (tree, path, node), mutate tree accordingly.
        transformers are tested/applied in the order given.

    """
    def _transform(tree: JSONLike) -> JSONLike:
        tree = deepcopy(tree)
        walker = walk_tree(tree)
        while True:
            try:
                _tree, path, node = next(walker)
                for transformer in transformers:
                    transformation = transformer(_tree, path, node)
                    if transformation:
                        walker.send(transformation)
                        _tree, path, node = next(walker)

                walker.send(NextPathPlease)                        

            except StopIteration:
                return tree
    return _transform
