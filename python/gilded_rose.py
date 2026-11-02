# -*- coding: utf-8 -*-
# ==========================================================================
# STEP 8 |  commit: refactor: strategy classes per item type with a registry
# WHAT : Strategy pattern: one ItemUpdater class per item type + a registry dict.
# WHY  : GildedRose.update_quality() shrinks to a 3-line loop. New types never touch existing logic (open/closed principle).
# NOTE : inheritance for reuse vs a Protocol with composition.
# TEST : python -m unittest -v   (run inside this folder)
# ==========================================================================

AGED_BRIE = "Aged Brie"
BACKSTAGE_PASSES = "Backstage passes to a TAFKAL80ETC concert"
SULFURAS = "Sulfuras, Hand of Ragnaros"
MIN_QUALITY = 0
MAX_QUALITY = 50

# Backstage passes gain extra quality once sell_in drops BELOW these values.
# (sell_in is already aged for today when these are checked.)
BACKSTAGE_DOUBLE_INCREASE_BELOW = 10
BACKSTAGE_TRIPLE_INCREASE_BELOW = 5


def increase_quality(item, amount=1):
    if item.quality < MAX_QUALITY:
        item.quality = min(MAX_QUALITY, item.quality + amount)


def decrease_quality(item, amount=1):
    if item.quality > MIN_QUALITY:
        item.quality = max(MIN_QUALITY, item.quality - amount)


def is_expired(item):
    return item.sell_in < 0


# NEW (Strategy pattern): each item type becomes a class.
# ItemUpdater is the default (normal item); subclasses override only what differs.
class ItemUpdater:
    """Default behaviour: a normal item."""

    def update(self, item):
        self.update_sell_in(item)       # age first ...
        self.update_quality(item)       # ... quality rules use the already-aged sell_in

    def update_sell_in(self, item):
        item.sell_in = item.sell_in - 1

    def update_quality(self, item):
        decrease_quality(item)
        if is_expired(item):
            decrease_quality(item)


class AgedBrieUpdater(ItemUpdater):
    def update_quality(self, item):
        increase_quality(item)
        if is_expired(item):
            increase_quality(item)


class BackstagePassUpdater(ItemUpdater):
    def update_quality(self, item):
        increase_quality(item)
        if item.sell_in < BACKSTAGE_DOUBLE_INCREASE_BELOW:
            increase_quality(item)
        if item.sell_in < BACKSTAGE_TRIPLE_INCREASE_BELOW:
            increase_quality(item)
        if is_expired(item):
            item.quality = MIN_QUALITY


# Sulfuras overrides both methods with no-ops: it never ages and never changes.
class SulfurasUpdater(ItemUpdater):
    def update_sell_in(self, item):
        pass

    def update_quality(self, item):
        pass


# One shared, stateless default instance (no new object per item).
DEFAULT_UPDATER = ItemUpdater()

# NEW registry: item name -> updater. A new item type is ONE new line here (plus its class).
ITEM_UPDATERS = {
    AGED_BRIE: AgedBrieUpdater(),
    BACKSTAGE_PASSES: BackstagePassUpdater(),
    SULFURAS: SulfurasUpdater(),
}


# NEW lookup: replaces the if/elif dispatch chain.
def get_updater(item):
    return ITEM_UPDATERS.get(item.name, DEFAULT_UPDATER)


# update_quality is now just a loop that delegates to the right updater.
class GildedRose(object):

    def __init__(self, items):
        self.items = items

    def update_quality(self):
        for item in self.items:
            get_updater(item).update(item)


class Item:
    def __init__(self, name, sell_in, quality):
        self.name = name
        self.sell_in = sell_in
        self.quality = quality

    def __repr__(self):
        return "%s, %s, %s" % (self.name, self.sell_in, self.quality)
