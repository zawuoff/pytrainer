"""Editor help: inline errors and autocomplete, standard library only (Jedi when it's installed).

- `diagnose(code)` finds a syntax error (with its exact position) or, when the code parses, names
  that are used but never defined anywhere in the file (almost always a typo). It's deliberately
  cautious: a name bound anywhere in the file counts as defined, so it never flags correct code.
- `complete(code, line, col)` suggests what can come next. With Jedi installed it does real type
  inference; without it, it offers names from the file, builtins and keywords, attributes of
  imported standard-library modules, of `self`, and of names assigned a literal (a str, list,
  dict, ...).

Nothing here runs the learner's code: it is parsed, never executed.
"""

from __future__ import annotations

import ast
import builtins
import importlib
import keyword
import re
import sys
import threading

MAX_CODE = 100_000
MAX_ITEMS = 60

# Stdlib modules that do something when imported (open a browser, print, start a GUI) are never
# imported just to list their names.
UNSAFE_MODULES = {"antigravity", "this", "idlelib", "tkinter", "turtle", "turtledemo", "pydoc", "webbrowser",
                  "__main__", "__hello__", "__phello__", "ensurepip", "venv", "lib2to3", "pip"}
SAFE_MODULES = set(getattr(sys, "stdlib_module_names", ())) - UNSAFE_MODULES

# Names the test harness and the LLM bridge put in reach of learner code.
HARNESS_NAMES = {"run_script", "capture", "load", "source", "__file__", "__builtins__"}

LITERAL_TYPES = {ast.List: list, ast.Dict: dict, ast.Set: set, ast.Tuple: tuple, ast.JoinedStr: str,
                 ast.ListComp: list, ast.DictComp: dict, ast.SetComp: set}

_jedi_lock = threading.Lock()


def jedi_available() -> bool:
    try:
        import jedi  # noqa: F401
    except ImportError:
        return False
    return True


# ---------------------------------------------------------------------------------------- errors

def _bound_names(tree: ast.AST) -> tuple[set[str], bool]:
    """Every name the file binds anywhere, and whether it has a star import (then we can't tell)."""
    names: set[str] = set()
    star = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            names.add(node.id)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.arg):
            names.add(node.arg)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                if alias.name == "*":
                    star = True
                else:
                    names.add((alias.asname or alias.name).split(".")[0])
        elif isinstance(node, ast.ExceptHandler) and node.name:
            names.add(node.name)
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            names.update(node.names)
        elif isinstance(node, ast.MatchAs) and node.name:
            names.add(node.name)
        elif isinstance(node, ast.MatchStar) and node.name:
            names.add(node.name)
        elif isinstance(node, ast.MatchMapping) and node.rest:
            names.add(node.rest)
        elif hasattr(ast, "TypeVar") and isinstance(node, getattr(ast, "TypeVar")):
            names.add(node.name)
    return names, star


def _close_match(name: str, known: set[str]) -> str | None:
    import difflib
    match = difflib.get_close_matches(name, sorted(known), n=1, cutoff=0.75)
    return match[0] if match else None


def diagnose(code: str, extra_names: set[str] | None = None) -> list[dict]:
    """Problems in `code`, as {line, col, end_col, severity, message} (1-based lines, 0-based cols)."""
    code = code[:MAX_CODE]
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        line = exc.lineno or 1
        col = max(0, (exc.offset or 1) - 1)
        end = (exc.end_offset - 1) if getattr(exc, "end_offset", None) and exc.end_lineno == exc.lineno else col + 1
        msg = exc.msg[0].upper() + exc.msg[1:] if exc.msg else "Invalid syntax"
        return [{"line": line, "col": col, "end_col": max(end, col + 1), "severity": "error",
                 "message": f"{type(exc).__name__}: {msg}"}]
    except (ValueError, RecursionError):
        return []
    bound, star = _bound_names(tree)
    if star:
        return []
    known = bound | set(dir(builtins)) | HARNESS_NAMES | (extra_names or set())
    out, seen = [], set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) and node.id not in known:
            key = (node.lineno, node.col_offset)
            if key in seen:
                continue
            seen.add(key)
            hint = _close_match(node.id, known - HARNESS_NAMES)
            out.append({"line": node.lineno, "col": node.col_offset,
                        "end_col": node.end_col_offset or node.col_offset + len(node.id), "severity": "warning",
                        "message": f"'{node.id}' is never defined" + (f". Did you mean '{hint}'?" if hint else ".")})
    out.sort(key=lambda d: (d["line"], d["col"]))
    return out[:50]


# ---------------------------------------------------------------------------------------- completions

def _kind(value) -> str:
    if isinstance(value, type):
        return "class"
    if callable(value):
        return "function"
    if type(value).__name__ == "module":
        return "module"
    return "value"


def _attrs_of(obj) -> list[dict]:
    items = []
    for name in dir(obj):
        if name.startswith("__") and name.endswith("__"):
            continue
        try:
            value = getattr(obj, name)
        except Exception:  # noqa: BLE001 - some attributes raise on access
            value = None
        items.append({"text": name, "kind": _kind(value), "detail": _doc_line(value)})
    return items


def _doc_line(value) -> str:
    if value is None or isinstance(value, (int, float, str, bytes, bool)):
        return ""
    doc = getattr(value, "__doc__", None)
    if not isinstance(doc, str):
        return ""
    first = doc.strip().splitlines()[0] if doc.strip() else ""
    return first[:100]


def _safe_module(name: str):
    root = name.split(".")[0]
    if root not in SAFE_MODULES:
        return None
    try:
        return importlib.import_module(name)
    except Exception:  # noqa: BLE001 - a module that can't import here just offers nothing
        return None


def _resolve(path: str):
    """A module, or a name inside one (`collections.Counter`), from a safe stdlib module."""
    mod = _safe_module(path)
    if mod is not None:
        return mod
    parent, _, attr = path.rpartition(".")
    mod = _safe_module(parent) if parent else None
    return getattr(mod, attr, None) if mod is not None else None


def _imports(tree: ast.AST) -> dict[str, str]:
    """Local name -> dotted module path, for `import x`, `import x.y as z` and `from x import y`."""
    found = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.asname:
                    found[a.asname] = a.name
                else:
                    found[a.name.split(".")[0]] = a.name.split(".")[0]
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            for a in node.names:
                if a.name != "*":
                    found[a.asname or a.name] = f"{node.module}.{a.name}"
    return found


def _literal_types(tree: ast.AST) -> dict[str, type]:
    types: dict[str, type] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            v = node.value
            t = type(v.value) if isinstance(v, ast.Constant) and v.value is not None else LITERAL_TYPES.get(type(v))
            if t:
                types[node.targets[0].id] = t
    return types


def _self_attrs(tree: ast.AST, line: int) -> list[dict]:
    """Attributes and methods of the class the cursor is in (the innermost one that contains it)."""
    classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.lineno <= line <= (n.end_lineno or n.lineno)]
    if not classes:
        return []
    cls = max(classes, key=lambda n: n.lineno)
    items: dict[str, str] = {}
    for sub in ast.walk(cls):
        if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)) and sub in cls.body:
            items[sub.name] = "function"
        elif isinstance(sub, ast.Attribute) and isinstance(sub.value, ast.Name) and sub.value.id == "self" \
                and isinstance(sub.ctx, ast.Store):
            items.setdefault(sub.attr, "value")
    return [{"text": k, "kind": v, "detail": ""} for k, v in items.items()]


def _blank(line: str) -> str:
    return line[:len(line) - len(line.lstrip())] + "pass"


def _parse_lenient(lines: list[str], typing_at: int) -> ast.AST | None:
    """Parse code that's mid-edit. The line being typed becomes `pass` (keeping its block valid),
    and each line a syntax error points at is blanked the same way, a few times over."""
    lines = list(lines)
    if 0 < typing_at <= len(lines):
        lines[typing_at - 1] = _blank(lines[typing_at - 1])
    for _ in range(20):
        try:
            return ast.parse("\n".join(lines))
        except SyntaxError as exc:
            bad = (exc.lineno or 0) - 1
            if not 0 <= bad < len(lines):
                if not lines:
                    return None
                lines.pop()  # an unclosed bracket can point past the end: drop the tail
            elif lines[bad].strip() != "pass":
                lines[bad] = _blank(lines[bad])
            else:  # blanking wasn't enough (an indented `pass` with no block): empty the line
                lines[bad] = ""
        except (ValueError, RecursionError):
            return None
    return None


def _file_names(tree: ast.AST | None) -> list[dict]:
    if tree is None:
        return []
    items: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            items[node.name] = "function"
        elif isinstance(node, ast.ClassDef):
            items[node.name] = "class"
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            items.setdefault(node.id, "value")
        elif isinstance(node, ast.arg):
            items.setdefault(node.arg, "value")
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for a in node.names:
                if a.name != "*":
                    items.setdefault((a.asname or a.name).split(".")[0], "module")
    return [{"text": k, "kind": v, "detail": ""} for k, v in items.items()]


def _fallback(code: str, line: int, col: int) -> tuple[str, list[dict]]:
    lines = code.split("\n")
    text = lines[line - 1][:col] if 0 < line <= len(lines) else ""
    m = re.search(r"([A-Za-z_][\w.]*)?\.(\w*)$", text)
    tree = _parse_lenient(lines, line)
    if m and m.group(1):
        prefix, target = m.group(2), m.group(1)
        if tree is None:
            return prefix, []
        if target == "self":
            return prefix, _self_attrs(tree, line)
        imports = _imports(tree)
        head, _, rest = target.partition(".")
        if head in imports:
            obj = _resolve(imports[head])
            for part in filter(None, rest.split(".")):
                obj = getattr(obj, part, None)
            return prefix, _attrs_of(obj) if obj is not None else []
        if not rest:
            lit = _literal_types(tree).get(head)
            if lit:
                return prefix, _attrs_of(lit)
        return prefix, []
    if m:  # a lone "." (a float, or nothing to look up)
        return m.group(2), []
    word = re.search(r"[A-Za-z_]\w*$", text)
    prefix = word.group(0) if word else ""
    m_from = re.match(r"\s*from\s+([\w.]+)\s+import\s+(?:.*,\s*)?(\w*)$", text)
    if m_from:
        mod = _safe_module(m_from.group(1))
        return m_from.group(2), _attrs_of(mod) if mod else []
    m_imp = re.match(r"\s*(?:import|from)\s+(\w*)$", text)
    if m_imp:
        return m_imp.group(1), [{"text": n, "kind": "module", "detail": ""} for n in sorted(SAFE_MODULES)
                                if not n.startswith("_")]
    items = _file_names(tree)
    items += [{"text": k, "kind": "keyword", "detail": ""} for k in keyword.kwlist + list(keyword.softkwlist)]
    items += [{"text": n, "kind": _kind(getattr(builtins, n)), "detail": _doc_line(getattr(builtins, n))}
              for n in dir(builtins) if not n.startswith("_")]
    return prefix, items


def _jedi(code: str, line: int, col: int) -> tuple[str, list[dict]] | None:
    try:
        import jedi
    except ImportError:
        return None
    try:
        with _jedi_lock:  # Jedi's caches aren't thread-safe; the server is threaded
            found = jedi.Script(code).complete(line, col)
            items = [{"text": c.name, "kind": c.type, "detail": (c.description or "")[:100]} for c in found[:MAX_ITEMS * 2]]
    except Exception:  # noqa: BLE001 - Jedi trips over some half-written code; fall back
        return None
    lines = code.split("\n")
    text = lines[line - 1][:col] if 0 < line <= len(lines) else ""
    word = re.search(r"\w*$", text)
    return (word.group(0) if word else ""), items


def complete(code: str, line: int, col: int) -> dict:
    """Completions at (line, col) (1-based line, 0-based column), best first."""
    code = code[:MAX_CODE]
    result = _jedi(code, line, col)
    engine = "jedi"
    if result is None or not result[1]:
        result, engine = _fallback(code, line, col), "basic"
    prefix, items = result
    low = prefix.lower()
    seen, out = set(), []
    for it in items:
        name = it["text"]
        if name in seen or (low and not name.lower().startswith(low)) or name == prefix:
            continue
        if not low and name.startswith("_"):
            continue
        seen.add(name)
        out.append(it)
    if engine == "basic":
        rank = {"value": 0, "function": 0, "class": 0, "module": 1, "keyword": 2}
        out.sort(key=lambda i: (not i["text"].startswith(prefix), i["text"].startswith("_"), rank.get(i["kind"], 1), i["text"].lower()))
    return {"prefix": prefix, "items": out[:MAX_ITEMS], "engine": engine}
