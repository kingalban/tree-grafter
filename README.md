# tree-grafter
A tool for walking over and manipulating json like objects in python.
_Tree_ in the data structure sense, and _graft_ as in to prune, mutate, etc. 

## installation
For use of this package use:
~~~
pip install git+https://github.com/kingalban/tree-grafter.git
~~~

For development of the package use:
~~~
https://github.com/kingalban/tree-grafter.git
pipenv install 
~~~

## example usage:
~~~
>>> from tree_grafter import apply_transformations, ReplaceNode
>>> def uppercase_keys(tree, path, node):
...     if isinstance(node, dict):
...         return ReplaceNode({k.upper(): v for k,v in node.items()}, 0)
... 
>>> my_tree = [{"potato":1}, {"tomato": 3}]
>>> apply_transformations(uppercase_keys)(my_tree)
[{'POTATO': 1}, {'TOMATO': 3}]
~~~

## limitations
Replacing the root of a tree is not currently supported. 
Notice how the above example only includes dicts as second level items.
All mutating is replacing a node, adding a key or item to a list.

