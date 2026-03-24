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

def newBuffs(formula: dict[int, tuple[str | tuple[str, typing.Any, ...], ...]]) -> list[list[str]] | tuple[list[list[str]], list[list[typing.Callable]]]:
    result: list[list[str]] = []
    result_stats: list[list[typing.Callable]] = []
    active_buffs: list[dict[str, typing.Any]] = []
    has_stats: bool = False
    
    for level_items in formula.values():
        for item in level_items:
            if isinstance(item, tuple) and item[0] == "stat":
                has_stats = True
                break
        if has_stats:
            break
            
    safe_globals: dict = {"__builtins__": {}, "math": math, "pct": pct, "pctfloat": pctfloat, "round": round}
    
    for level in range(1, 31):
        if formula.get(level):
            for item in formula[level]:
                if isinstance(item, str):
                    active_buffs.append({
                        "string": item,
                        "value": 0,
                        "scaling": "x",
                        "cap": None,
                        "stat": "pass"
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
                        case "stat":
                            if len(item) == 5 and item[3] in ("extend", "replace"):
                                active_buffs[-1]["stat"] = (item[1], item[2], item[3], item[4])
                            elif len(item) == 3:
                                active_buffs[-1]["stat"] = (item[1], item[2])
                            elif len(item) == 2:
                                active_buffs[-1]["stat"] = item[1]
                            else:
                                raise FormulaError("stat parameter expects either a callable, a skill and attribute tuple, or a skill, attr, mode (extend/replace), and wrapper func tuple.")
                        case _:
                            raise FormulaError(f"unknown parameter: {item[0]}")
        
        current_level_buffs: list[str] = []
        current_level_stats: list[typing.Callable] = []
        for buff in active_buffs:
            value: float | int = buff["value"]
            if isinstance(value, float) and value.is_integer():
                value = int(value)
            
            fmt_str = buff["string"]
            if "{}" in fmt_str:
                current_level_buffs.append(fmt_str.format(value))
            else:
                current_level_buffs.append(fmt_str)
                
            if buff["stat"] != "pass":
                func = buff["stat"]
                if callable(func):
                    current_level_stats.append((lambda f, v: lambda target: f(target, v))(func, value))
                elif isinstance(func, tuple) and len(func) == 2:
                    skill_target, attr_name = func
                    def apply_stat_attr(skill_target=skill_target, attr_name=attr_name, v=value):
                        def actual_apply(target_or_skillset):
                            skills = getattr(target_or_skillset, "skills", None)
                            if skills is None: 
                                skills = [target_or_skillset]
                                
                            skill = None
                            if isinstance(skill_target, str):
                                skill = next((s for s in skills if s.name.lower() == skill_target.lower() or s.__class__.__name__.lower() == skill_target.lower()), None)
                            elif isinstance(skill_target, type):
                                skill = next((s for s in skills if isinstance(s, skill_target)), None)
                                
                            if skill and hasattr(skill, attr_name):
                                setattr(skill, attr_name, getattr(skill, attr_name) + v)
                        return actual_apply
                        
                    current_level_stats.append(apply_stat_attr())
            
            safe_locals = {"x": min(buff["value"], buff["cap"]) if buff["cap"] else buff["value"], "level": level}
            buff["value"] = eval(buff["scaling"], safe_globals, safe_locals)
            
        result.append(current_level_buffs)
        if has_stats:
            result_stats.append(current_level_stats)
        
    if has_stats:
        return result, result_stats
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