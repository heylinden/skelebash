from __future__ import annotations
import typing, importlib, importlib.util, importlib.machinery, pathlib, json, sys, math, gzip, shutil, os

from .constants import CORE_DIR, MODS_DIR, PUBLIC_DIR


def isJsonCompatible(obj: typing.Any) -> bool:
    return isinstance(obj, (int, float, str, bool, type(None)))
def parse(v: typing.Any, _seen: set[int] | None = None) -> typing.Any:
    if _seen is None:
        _seen = set()
    if isinstance(v, dict):
        return {k: parse(v2, _seen) for k, v2 in v.items()}
    elif isinstance(v, list):
        new_v: list = []
        for v2 in v:
            new_v.append(parse(v2, _seen))
        return new_v
    elif isinstance(v, tuple):
        new_v: tuple = ()
        for v2 in v:
            new_v += (parse(v2, _seen),)
        return new_v
    elif isinstance(v, set):
        new_v: set = set()
        for v2 in v:
            new_v.add(parse(v2, _seen))
        return new_v
    elif isJsonCompatible(v):
        return v
    if getattr(v.__class__, "__public__", False) or getattr(v, "__public__", False):
        return f"public.{v.__class__.__qualname__.lower()}"
    if id(v) in _seen:
        return None
    _seen.add(id(v))
    res = serialize(v, _seen)
    _seen.remove(id(v))
    return res
def serialize(obj: typing.Any, _seen: set[int] | None = None) -> dict:
    if _seen is None:
        _seen = set()
    if hasattr(obj, "__dict__"):
        d: dict = {k: parse(v, _seen) for k, v in obj.__dict__.items()}
    else:
        d: dict = {}
    if hasattr(obj.__class__, "__qualname__"):
        d["__class__"] = obj.__class__.__qualname__
    if hasattr(obj.__class__, "__module__"):
        d["__source__"] = obj.__class__.__module__.split(".")[-1]
        d["__fullsource__"] = obj.__class__.__module__
    return d
def reverseParse(v: typing.Any, prefer: typing.Literal["core", "mod"] | None = None) -> typing.Any:
    if isinstance(v, str) and v.startswith("public."):
        json_path = PUBLIC_DIR / (v.removeprefix("public.") + ".pack")
        if json_path.exists():
            with gzip.open(json_path, "rt", encoding="utf-8") as file:
                return deserialize(json.load(file), prefer)
    if isinstance(v, dict) and v.get("__class__") and v.get("__source__") and v.get("__fullsource__"):
        return deserialize(v, prefer)
    elif isinstance(v, dict):
        return {k: reverseParse(v2) for k, v2 in v.items()}
    elif isinstance(v, list):
        new_v: list = []
        for v2 in v:
            new_v.append(reverseParse(v2))
        return new_v
    elif isinstance(v, tuple):
        new_v: tuple = ()
        for v2 in v:
            new_v += (reverseParse(v2),)
        return new_v
    elif isinstance(v, set):
        new_v: set = set()
        for v2 in v:
            new_v.add(reverseParse(v2))
        return new_v
    return v
def deserialize(d: dict, prefer: typing.Literal["core", "mod"] | None = None) -> typing.Any:
    core_path: pathlib.Path = CORE_DIR / (d["__source__"] + ".py")
    mod_path: pathlib.Path = MODS_DIR / (d["__source__"] + ".py")
    path: pathlib.Path | None = None
    if core_path.exists() and mod_path.exists():
        if prefer == "core":
            path = core_path
        elif prefer == "mod":
            path = mod_path
        else:
            raise NameError(f"source '{d['__source__']}' exists both as a core file and mod file. please remove the mod file or specify 'prefer' argument.")
    if core_path.exists():
        path = core_path
    elif mod_path.exists():
        path = mod_path
    else:
        raise NameError(f"source {d['__source__']} does not exist.")
    spec: importlib.machinery.ModuleSpec = importlib.util.spec_from_file_location(d["__fullsource__"], path)
    obj: typing.Any = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = obj
    spec.loader.exec_module(obj)
    for part in d["__class__"].split("."):
        obj = getattr(obj, part)
    obj = obj() # type: ignore
    d = {k: reverseParse(v, prefer) for k, v in d.items()}
    obj.__dict__ = d
    return obj

def pctfloat(base: int, percentage: int) -> float:
    return base * (percentage / 100)
def pct(base: int, percentage: int) -> int:
    return math.floor(pctfloat(base, percentage))

def public(obj: typing.Any) -> typing.Any:
    if not PUBLIC_DIR.exists():
        PUBLIC_DIR.mkdir()
    try:
        data = serialize(obj() if callable(obj) else obj)
    except Exception: # type: ignore
        data = serialize(obj)
    with gzip.open(PUBLIC_DIR / f"{obj.__qualname__.lower() if hasattr(obj, '__qualname__') else obj.__class__.__qualname__.lower()}.pack", "wt", encoding="utf-8") as file:
        json.dump(data, file, indent=4) # type: ignore
    obj.__public__ = True
    return obj

class new:
    def __init__(self, *parents: type) -> None:
        self.parents: list[type] = list(parents)
    def __enter__(self) -> typing.Any:
        return type(f"New{self.parents[0].__name__}", tuple(self.parents), {})
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        ...