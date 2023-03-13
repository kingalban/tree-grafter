from __future__ import annotations
from typing import Callable, Optional, Any
from tree_grafter import ReplaceNode, JSONLike, PathType, deep_getitem


def limit_depth(max_path_length: float = float("inf")) -> Callable[[JSONLike, PathType, Any], Optional[ReplaceNode]]:
	""" Returns a transformer function to truncate trees at a specific depth. """
	def func(_tree: JSONLike, path: PathType, node: Any) -> Optional[ReplaceNode]:
		if len(path) > max_path_length:
			parent = deep_getitem(_tree, path[:-1])
			if isinstance(parent, dict):
				return ReplaceNode({}, -1)

			if isinstance(parent, list):
				return ReplaceNode([], -1)
		return None
	return func

