# -*- coding: utf-8 -*-
# ==========================================================================
# STEP 9 |  commit: feat: add Conjured items (degrade twice as fast)
# WHAT : Add the Conjured feature (degrades twice as fast).
# WHY  : Because the design is extendable, the feature is a tiny class plus a prefix check, with its own tests.
# NOTE : ASSUMPTION: any name starting with 'Conjured' counts; degrades 2/day and 4/day once expired.
# TEST : python -m unittest -v   (run inside this folder)
# ==========================================================================

AGED_BRIE = "Aged Brie"
BACKSTAGE_PASSES = "Backstage passes to a TAFKAL80ETC concert"
SULFURAS = "Sulfuras, Hand of Ragnaros"
# NEW: any item whose name starts with this is treated as Conjured.
CONJURED_PREFIX = "Conjured"
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


class ItemUpdater:
    """Default behaviour: a normal item."""

    # NEW: quality lost per day by a normal item. Subclasses change it (Conjured = 2).
    degrade_rate = 1

    def update(self, item):
        self.update_sell_in(item)       # age first ...
        self.update_quality(item)       # ... quality rules use the already-aged sell_in

    def update_sell_in(self, item):
        item.sell_in = item.sell_in - 1

    def update_quality(self, item):
        decrease_quality(item, self.degrade_rate)
        if is_expired(item):
            decrease_quality(item, self.degrade_rate)


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


class SulfurasUpdater(ItemUpdater):
    def update_sell_in(self, item):
        pass

    def update_quality(self, item):
        pass


# NEW FEATURE: only a few lines because the design is extendable.
class ConjuredItemUpdater(ItemUpdater):
    """Conjured items degrade twice as fast as normal items."""

    degrade_rate = 2


DEFAULT_UPDATER = ItemUpdater()
CONJURED_UPDATER = ConjuredItemUpdater()

ITEM_UPDATERS = {
    AGED_BRIE: AgedBrieUpdater(),
    BACKSTAGE_PASSES: BackstagePassUpdater(),
    SULFURAS: SulfurasUpdater(),
}


# CHANGED: exact-name lookup first, then Conjured prefix, then default.
def get_updater(item):
    if item.name in ITEM_UPDATERS:
        return ITEM_UPDATERS[item.name]
    if item.name.startswith(CONJURED_PREFIX):
        return CONJURED_UPDATER
    return DEFAULT_UPDATER


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
