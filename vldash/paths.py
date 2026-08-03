"""The single choke point every filesystem-touching operation funnels
through. Resolves against the live `roots` table (default + user-added),
not a hardcoded dict, so registering a new folder never needs a code
change. See AGENTS.md Hard Rule 2.
"""
from __future__ import annotations

from pathlib import Path

from . import db


class PathViolation(Exception):
    """A resolved path escaped its allow-listed root, or the root key
    itself is unknown."""


class RootUnavailable(Exception):
    """A registered root's absolute_path doesn't exist right now (drive
    unplugged, folder renamed/moved outside the app)."""


_roots_cache: dict[str, tuple[Path, str]] | None = None


def refresh_roots_cache() -> None:
    """Call after any Add Folder / unregister action so resolve_safe_path
    sees the change without restarting the app."""
    global _roots_cache
    conn = db.get_connection()
    try:
        rows = conn.execute("SELECT key, absolute_path, kind FROM roots").fetchall()
        _roots_cache = {row["key"]: (Path(row["absolute_path"]), row["kind"]) for row in rows}
    finally:
        conn.close()


def get_roots() -> dict[str, tuple[Path, str]]:
    if _roots_cache is None:
        refresh_roots_cache()
    assert _roots_cache is not None
    return _roots_cache


def resolve_safe_path(root_key: str, relative: str = "") -> Path:
    """Resolve `relative` against the registered root `root_key`, raising
    PathViolation if the root is unknown or the resolved path escapes it,
    RootUnavailable if the root's absolute_path doesn't exist right now.
    Never accept a relative path from the caller without going through
    this function first."""
    roots = get_roots()
    if root_key not in roots:
        raise PathViolation(f"unknown root: {root_key!r}")

    base, _kind = roots[root_key]
    base_resolved = base.resolve()
    if not base_resolved.exists():
        raise RootUnavailable(f"root {root_key!r} is not reachable: {base}")

    candidate = (base_resolved / relative).resolve() if relative else base_resolved
    try:
        candidate.relative_to(base_resolved)
    except ValueError:
        raise PathViolation(f"path escapes root {root_key!r}: {relative!r}") from None
    return candidate


def assert_writable(root_key: str) -> None:
    """Raise PathViolation if root_key isn't a "dest" kind root. Every
    write/copy/discard/folder-mutation route calls this before touching
    disk, a readonly root (default or user-added) can never be a target."""
    roots = get_roots()
    if root_key not in roots:
        raise PathViolation(f"unknown root: {root_key!r}")
    _base, kind = roots[root_key]
    if kind != "dest":
        raise PathViolation(f"root {root_key!r} is read-only, not a valid write target")
