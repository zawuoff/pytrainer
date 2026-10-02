"""Tiny offline style checker: flags common non-idiomatic patterns after a solve."""

from __future__ import annotations

import ast
import builtins
import re

BUILTIN_NAMES = {"list", "dict", "str", "int", "float", "set", "tuple", "type", "id", "input",
                 "sum", "max", "min", "len", "map", "filter", "object", "format", "next",
                 "iter", "open", "range", "sorted", "any", "all", "hash", "bytes", "print"}


def check(code: str) -> list[dict]:
    notes: list[dict] = []
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return notes

    def add(node, msg):
        notes.append({"line": getattr(node, "lineno", None), "message": msg})

    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            add(node, "Bare `except:` catches everything (even KeyboardInterrupt). Catch specific exceptions.")
        elif isinstance(node, ast.ExceptHandler) and isinstance(node.type, ast.Name) \
                and node.type.id in ("Exception", "BaseException") \
                and all(isinstance(s, ast.Pass) for s in node.body):
            add(node, "Silently swallowing all exceptions hides bugs.")
        elif isinstance(node, ast.Compare):
            for op, right in zip(node.ops, node.comparators):
                if isinstance(op, (ast.Eq, ast.NotEq)) and isinstance(right, ast.Constant) \
                        and right.value is None:
                    add(node, "Compare to None with `is` / `is not`, not `==`.")
                if isinstance(op, (ast.Eq, ast.NotEq)) and isinstance(right, ast.Constant) \
                        and isinstance(right.value, bool):
                    add(node, "Comparing to True/False with `==` is redundant; use the value directly.")
        elif isinstance(node, ast.For) and isinstance(node.iter, ast.Call) \
                and getattr(node.iter.func, "id", None) == "range" and len(node.iter.args) == 1 \
                and isinstance(node.iter.args[0], ast.Call) \
                and getattr(node.iter.args[0].func, "id", None) == "len":
            add(node, "`for i in range(len(x))` - consider iterating directly or using enumerate().")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for default in node.args.defaults + node.args.kw_defaults:
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    add(node, f"Mutable default argument in `{node.name}` is shared between calls.")
            if re.search(r"[a-z][A-Z]", node.name):
                add(node, f"Function `{node.name}` uses camelCase; Python uses snake_case.")
            length = (node.end_lineno or node.lineno) - node.lineno
            if length > 45:
                add(node, f"`{node.name}` is {length} lines long; consider splitting it up.")
            for arg in node.args.args + node.args.kwonlyargs:
                if arg.arg in BUILTIN_NAMES:
                    add(node, f"Parameter `{arg.arg}` shadows a built-in.")
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id in BUILTIN_NAMES and hasattr(builtins, t.id):
                    add(node, f"Variable `{t.id}` shadows a built-in.")
        elif isinstance(node, ast.Call) and getattr(node.func, "id", None) == "open":
            parent_ok = False
            for w in ast.walk(tree):
                if isinstance(w, (ast.With, ast.AsyncWith)) and any(i.context_expr is node for i in w.items):
                    parent_ok = True
            if not parent_ok:
                add(node, "open() outside a `with` block - the file may not be closed.")
        elif isinstance(node, ast.Global):
            add(node, "`global` makes code harder to reason about; pass values in and return them.")

    for i, line in enumerate(code.splitlines(), 1):
        if len(line) > 110:
            notes.append({"line": i, "message": "Very long line (>110 chars)."})
            break
    seen = set()
    unique = []
    for n in notes:
        key = (n["line"], n["message"])
        if key not in seen:
            seen.add(key)
            unique.append(n)
    return unique[:8]
