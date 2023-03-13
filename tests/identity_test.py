from tree_grafter import apply_transformations, walk_tree, stroll_tree, ReplaceNode, NextPathPlease
from tree_grafter.utils import pipe
from tests import recursive_json
from hypothesis import given
import pytest


@given(recursive_json())
def test_no_transformation_no_change(json):
	assert json == apply_transformations(lambda *a: None)(json)
