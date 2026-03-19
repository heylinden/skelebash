from __future__ import annotations
class ItemStack:
    def __init__(self, item: Item | None = None, count: int = 1) -> None: # type: ignore
        self.item: Item = item # type: ignore
        self.count: int = count
    def get(self) -> list[Item | int]: # type: ignore
        return [self.item, self.count]
    def onTick(self, skelebash: Skelebash) -> None: # type: ignore
        self.item.onTick(skelebash)
    def __repr__(self) -> str:
        return f"ItemStack('{self.item.name}'*{self.count})"