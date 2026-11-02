# -*- coding: utf-8 -*-
# ==========================================================================
# STEP 10 |  commit: chore: type hints, docstrings and README
# WHAT : Finish: type hints, docstrings, README with assumptions.
# WHY  : Professional polish. No behaviour change.
# NOTE : Final version.
# TEST : python -m unittest -v   (run inside this folder)
# ==========================================================================
"""Gilded Rose inventory updater.

Each kind of item has its own ItemUpdater (Strategy pattern). GildedRose looks
up the right updater for every item and delegates to it. To support a new kind
of item: write an ItemUpdater subclass and register it in ITEM_UPDATERS.
"""

from __future__ import annotations

from typing import Dict, Iterable

AGED_BRIE = "Aged Brie"
BACKSTAGE_PASSES = "Backstage passes to a TAFKAL80ETC concert"
SULFURAS = "Sulfuras, Hand of Ragnaros"
CONJURED_PREFIX = "Conjured"

MIN_QUALITY = 0
MAX_QUALITY = 50

# Backstage passes gain extra quality once sell_in drops BELOW these values.
# (sell_in is already aged for today when these are checked.)
BACKSTAGE_DOUBLE_INCREASE_BELOW = 10
BACKSTAGE_TRIPLE_INCREASE_BELOW = 5


# CHANGED in this step: type hints + docstrings were added; behaviour is unchanged.
def increase_quality(item: Item, amount: int = 1) -> None:
    """Raise quality, never above MAX_QUALITY. Items already at/above the cap are left as-is."""
    if item.quality < MAX_QUALITY:
        item.quality = min(MAX_QUALITY, item.quality + amount)


def decrease_quality(item: Item, amount: int = 1) -> None:
    """Lower quality, never below MIN_QUALITY."""
    if item.quality > MIN_QUALITY:
        item.quality = max(MIN_QUALITY, item.quality - amount)


def is_expired(item: Item) -> bool:
    """True once the sell-by date has passed (sell_in is negative)."""
    return item.sell_in < 0


class ItemUpdater:
    """Default behaviour: a normal item. Subclasses override what differs."""

    degrade_rate = 1

    def update(self, item: Item) -> None:
        # Order matters: age first, then apply quality rules to the aged sell_in.
        self.update_sell_in(item)
        self.update_quality(item)

    def update_sell_in(self, item: Item) -> None:
        item.sell_in = item.sell_in - 1

    def update_quality(self, item: Item) -> None:
        decrease_quality(item, self.degrade_rate)
        if is_expired(item):
            decrease_quality(item, self.degrade_rate)


class AgedBrieUpdater(ItemUpdater):
    """Improves with age (twice as fast once expired)."""

    def update_quality(self, item: Item) -> None:
        increase_quality(item)
        if is_expired(item):
            increase_quality(item)


class BackstagePassUpdater(ItemUpdater):
    """+1, +2 (10 days or fewer), +3 (5 days or fewer), worthless after the concert."""

    def update_quality(self, item: Item) -> None:
        increase_quality(item)
        if item.sell_in < BACKSTAGE_DOUBLE_INCREASE_BELOW:
            increase_quality(item)
        if item.sell_in < BACKSTAGE_TRIPLE_INCREASE_BELOW:
            increase_quality(item)
        if is_expired(item):
            item.quality = MIN_QUALITY


class SulfurasUpdater(ItemUpdater):
    """Legendary item: never has to be sold and never changes."""

    def update_sell_in(self, item: Item) -> None:
        pass

    def update_quality(self, item: Item) -> None:
        pass


class ConjuredItemUpdater(ItemUpdater):
    """Conjured items degrade twice as fast as normal items."""

    degrade_rate = 2


DEFAULT_UPDATER = ItemUpdater()
CONJURED_UPDATER = ConjuredItemUpdater()

ITEM_UPDATERS: Dict[str, ItemUpdater] = {
    AGED_BRIE: AgedBrieUpdater(),
    BACKSTAGE_PASSES: BackstagePassUpdater(),
    SULFURAS: SulfurasUpdater(),
}


def get_updater(item: Item) -> ItemUpdater:
    """Pick the updater for an item: exact name match, then Conjured prefix, then default."""
    if item.name in ITEM_UPDATERS:
        return ITEM_UPDATERS[item.name]
    if item.name.startswith(CONJURED_PREFIX):
        return CONJURED_UPDATER
    return DEFAULT_UPDATER


class GildedRose(object):

    def __init__(self, items: Iterable[Item]):
        self.items = items

    def update_quality(self) -> None:
        for item in self.items:
            get_updater(item).update(item)


class Item:
    def __init__(self, name, sell_in, quality):
        self.name = name
        self.sell_in = sell_in
        self.quality = quality

    def __repr__(self):
        return "%s, %s, %s" % (self.name, self.sell_in, self.quality)
