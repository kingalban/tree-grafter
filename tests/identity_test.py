from tree_grafter import apply_transformations, walk_tree, stroll_tree, ReplaceNode, NextPathPlease
from tree_grafter.utils import pipe
from tests import recursive_json
from hypothesis import given
import pytest


@given(recursive_json())
def test_no_transformation_no_change(json):
	assert json == apply_transformations(lambda *a: None)(json)


@given(recursive_json())
def test_transform_to_self_no_change(json):
	""" We need to make a special exception because replacing the root is currently unsupported """
	assert json == apply_transformations(lambda t, p, n: ReplaceNode(n, 0) if p else None)(json)
