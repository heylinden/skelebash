from __future__ import annotations
import typing

from .itemstack import ItemStack


def countItems(*itemstacks: ItemStack) -> list[ItemStack]:
    counted: list[ItemStack] = []
    for itemstack in itemstacks:
        if itemstack.count <= 0:
            continue
        counted_items: list[Item] = [i.item for i in counted] # type: ignore
        if itemstack.item in counted_items:
            counted[counted_items.index(itemstack.item)].count += itemstack.count
        else:
            counted.append(itemstack)
    return counted

class ItemBundle:
    def __init__(self, *itemstacks: ItemStack) -> None:
        self.itemstacks: list[ItemStack] = list(itemstacks)
        self.first: ItemStack | None = self.itemstacks[0] if len(self.itemstacks) >= 1 else None
        self.last: ItemStack | None = self.itemstacks[-1] if len(self.itemstacks) >= 1 else None
    def has(self, *itemstacks: ItemStack) -> False:
        self.update()
        for itemstack in countItems(*itemstacks):
            for inventory_itemstack in self.itemstacks:
                if itemstack.item == inventory_itemstack.item:
                    if inventory_itemstack.count >= itemstack.count:
                        break
                    else:
                        return False
            else:
                return False
        return True
    def add(self, itemstack: ItemStack) -> None:
        self.update()
        self.itemstacks.append(itemstack)
        self.first = self.itemstacks[0]
        self.last = self.itemstacks[-1]
        self.update()
    def remove(self, itemstack: ItemStack) -> None:
        self.update()
        for i, inventory_itemstack in enumerate(self.itemstacks):
            if itemstack.item == inventory_itemstack.item:
                self.itemstacks[i].count = max(0, inventory_itemstack.count - itemstack.count)
        self.update()
    def update(self) -> None:
        self.itemstacks = countItems(*self.itemstacks)
    
    def onTick(self, skelebash: Skelebash) -> None: # type: ignore
        self.update()
        for itemstack in self.itemstacks:
            itemstack.onTick(skelebash)
        self.first = self.itemstacks[0] if len(self.itemstacks) >= 1 else None
        self.last = self.itemstacks[-1] if len(self.itemstacks) >= 1 else None
    def __getitem__(self, i: int | slice) -> ItemStack | list[ItemStack]:
        return self.itemstacks[i]
    def __iter__(self) -> iter:
        return iter(self.itemstacks)
    def __repr__(self) -> str:
        return f"ItemBundle(\n  {'\n  '.join([repr(itemstack) for itemstack in self.itemstacks])}\n)"