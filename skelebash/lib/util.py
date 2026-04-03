from __future__ import annotations
import typing, importlib, importlib.util, importlib.machinery, pathlib, json, sys, math, gzip, shutil, os

from .constants import CORE_DIR, MODS_DIR, PUBLIC_DIR
from .itembundle import ItemBundle


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
def incrpct(base: int, percentage: int) -> int:
    return base + pct(base, percentage)
def decrpct(base: int, percentage: int) -> int:
    return base - pct(base, percentage)
def pct100(percentage: int) -> int:
    return 100 - percentage

class FormulaError(Exception):
    pass

def newFormula(factory: type[Item], formula: str) -> list[ItemBundle]:
    safe_globals: dict = {"__builtins__": {}, "math": math, "pct": pct, "pctfloat": pctfloat, "round": round}
    safe_locals: dict = {}
    costs: list[ItemBundle] = []
    for level in range(1, 31):
        safe_locals["level"] = level
        amount = int(eval(formula, safe_globals, safe_locals))
        costs.append(ItemBundle(factory() * amount))
    return costs

def newBuffs(formula: dict[int, tuple[str | tuple[str, typing.Any, ...], ...]]) -> list[list[str]]:
    result: list[list[str]] = []
    active_buffs: list[dict[str, typing.Any]] = []
    
    safe_globals: dict = {"__builtins__": {}, "math": math, "pct": pct, "pctfloat": pctfloat, "round": round}
    
    for level in range(1, 31):
        if formula.get(level):
            for item in formula[level]:
                if isinstance(item, str):
                    active_buffs.append({
                        "string": item,
                        "value": 0,
                        "scaling": "x",
                        "cap": None
                    })
                elif isinstance(item, tuple):
                    if not active_buffs:
                        raise FormulaError("cannot pass parameters before a buff string")
                    match item[0]:
                        case "starts":
                            active_buffs[-1]["value"] = item[1]
                        case "scaling":
                            active_buffs[-1]["scaling"] = item[1]
                        case "cap":
                            active_buffs[-1]["cap"] = item[1]
                        case _:
                            raise FormulaError(f"unknown parameter: {item[0]}")
        
        current_level_buffs: list[str] = []
        for buff in active_buffs:
            value: float | int = buff["value"]
            if isinstance(value, float) and value.is_integer():
                value = int(value)
            
            fmt_str = buff["string"]
            if "{}" in fmt_str:
                current_level_buffs.append(fmt_str.format(value))
            else:
                current_level_buffs.append(fmt_str)
                
            safe_locals = {"x": min(buff["value"], buff["cap"]) if buff["cap"] else buff["value"], "level": level}
            buff["value"] = eval(buff["scaling"], safe_globals, safe_locals)
            
        result.append(current_level_buffs)
    return result

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
        pass

class extend:
    def __init__(self, function: typing.Callable | extend) -> None:
        self.__source__: typing.Callable = function.__source__ if isinstance(function, extend) else function
        self.__function__: typing.Callable | extend = function
    def __call__(self, *args, **kwargs) -> typing.Any:
        return self.__function__(*args, **kwargs)

def src(obj: typing.Any) -> str:
    return "vanilla" if obj.__module__ == "skelebash.lib" else obj.__module__.split(".")[-1]

def isModded(obj: typing.Any) -> bool:
    return src(obj) != "vanilla"

def isVanilla(obj: typing.Any) -> bool:
    return not isModded(obj)

def modExists(name: str) -> bool:
    return (MODS_DIR / f"{name}.py").exists()

def getModPath(name: str) -> pathlib.Path:
    return MODS_DIR / f"{name}.py"