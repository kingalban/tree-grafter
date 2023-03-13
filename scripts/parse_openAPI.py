"""
	Fills '$ref' and 'allOf' in openAPI documents from stdin
"""
from __future__ import annotations
from tree_grafter.utils import y_print, j_print, pipe
from tree_grafter.openAPI import parse_openAPI_doc, hide_pagination
from tree_grafter import apply_transformations
from typing import Callable
import argparse
import yaml
import json
import sys


if __name__ == "__main__":
	parser = argparse.ArgumentParser("fill $ref:... in openAPI docs from stdin")
	parser.add_argument("-p", "--hide-pagination", action="store_true", help="remove pagination levels of schemas")
	parser.add_argument("-f", "--format", choices=("json", "yaml"), default="yaml", help="input AND output format")

	args = parser.parse_args()

	if args.format == "json":
		reader: Callable = json.loads
		printer: Callable = j_print
	else:
		reader = yaml.safe_load
		printer = y_print

	pipe(
		sys.stdin.read(),
		reader,
		parse_openAPI_doc, 
		apply_transformations(hide_pagination) if args.hide_pagination else lambda x: x,
		printer,
	)
