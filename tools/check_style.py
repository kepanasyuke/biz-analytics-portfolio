"""Проверка правил стиля Python: не больше одного return, и он последний; без while/break/continue."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".venv", ".tools", "node_modules", "dist", "__pycache__", ".ruff_cache", "tools"}
FUNCTIONS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)


def collect_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.py") if not SKIP_DIRS.intersection(path.relative_to(root).parts))


def is_function(node: ast.AST) -> bool:
    return isinstance(node, FUNCTIONS)


def inner(node: ast.AST) -> list[ast.AST]:
    return [node] + [item for child in ast.iter_child_nodes(node) if not is_function(child) for item in inner(child)]


def returns_of(node: ast.AST) -> list[ast.Return]:
    return [item for statement in getattr(node, "body", []) for item in inner(statement) if isinstance(item, ast.Return)]


def last_contains(node: ast.AST, target: ast.AST) -> bool:
    return bool(node.body) and target in inner(node.body[-1])


def return_problems(node: ast.AST) -> list[tuple[int, str]]:
    returns = returns_of(node)
    valid = len(returns) <= 1 and (not returns or last_contains(node, returns[0]))
    return [] if valid else [(node.lineno, f"{len(returns)} return в функции, разрешён один и последним оператором")]


def banned_nodes(tree: ast.AST) -> list[tuple[int, str]]:
    kinds = {ast.While: "while", ast.Break: "break", ast.Continue: "continue"}
    return [(node.lineno, kinds[type(node)]) for node in inner(tree) if type(node) in kinds]


def check_file(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    found = [*banned_nodes(tree), *[problem for node in inner(tree) if is_function(node) and not isinstance(node, ast.Lambda) for problem in return_problems(node)]]
    return [f"{path.relative_to(ROOT)}:{line}: {message}" for line, message in found]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    problems = [line for path in collect_files(ROOT) for line in check_file(path)]
    print("\n".join(problems) or "Стиль Python: OK (один return, без while/break/continue)")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
