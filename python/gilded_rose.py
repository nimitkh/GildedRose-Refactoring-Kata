# -*- coding: utf-8 -*-
# ==========================================================================
# STEP 7 |  commit: refactor: separate sell_in and quality updates, add is_expired and named thresholds
# WHAT : Separate aging (sell_in) from quality rules; add is_expired() and named backstage thresholds.
# WHY  : Single responsibility per function. Aging now happens first, so thresholds are `< 10` / `< 5` (original `< 11` / `< 6` evaluated before aging).
# NOTE : The off-by-one shift in the backstage thresholds is the subtlest point.
# TEST : python -m unittest -v   (run inside this folder)
# ==========================================================================

AGED_BRIE = "Aged Brie"
BACKSTAGE_PASSES = "Backstage passes to a TAFKAL80ETC concert"
SULFURAS = "Sulfuras, Hand of Ragnaros"
MIN_QUALITY = 0
MAX_QUALITY = 50

# Backstage passes gain extra quality once sell_in drops BELOW these values.
# (sell_in is already aged for today when these are checked.)
# NEW: named thresholds (were bare 11 and 6).
# They are 10 / 5 here because sell_in is aged BEFORE quality is calculated:
# original `sell_in < 11` evaluated before aging == `sell_in < 10` after aging.
BACKSTAGE_DOUBLE_INCREASE_BELOW = 10
BACKSTAGE_TRIPLE_INCREASE_BELOW = 5


def increase_quality(item, amount=1):
    if item.quality < MAX_QUALITY:
        item.quality = min(MAX_QUALITY, item.quality + amount)


def decrease_quality(item, amount=1):
    if item.quality > MIN_QUALITY:
        item.quality = max(MIN_QUALITY, item.quality - amount)


# NEW: gives a name to the repeated condition `item.sell_in < 0`.
def is_expired(item):
    return item.sell_in < 0


# NEW: aging is separated from quality rules (single responsibility).
def update_sell_in(item):
    item.sell_in = item.sell_in - 1


def update_normal_quality(item):
    decrease_quality(item)
    if is_expired(item):
        decrease_quality(item)


def update_aged_brie_quality(item):
    increase_quality(item)
    if is_expired(item):
        increase_quality(item)


def update_backstage_passes_quality(item):
    increase_quality(item)
    if item.sell_in < BACKSTAGE_DOUBLE_INCREASE_BELOW:
        increase_quality(item)
    if item.sell_in < BACKSTAGE_TRIPLE_INCREASE_BELOW:
        increase_quality(item)
    if is_expired(item):
        item.quality = MIN_QUALITY


# NEW: dispatch for the quality rules only.
def update_item_quality(item):
    if item.name == AGED_BRIE:
        update_aged_brie_quality(item)
    elif item.name == BACKSTAGE_PASSES:
        update_backstage_passes_quality(item)
    else:
        update_normal_quality(item)


# CHANGED: order is now age first, then quality (rules use the already-aged sell_in).
def update_item(item):
    if item.name == SULFURAS:
        return
    update_sell_in(item)       # age first ...
    update_item_quality(item)  # ... quality rules use the already-aged sell_in


class GildedRose(object):

    def __init__(self, items):
        self.items = items

    def update_quality(self):
        for item in self.items:
            update_item(item)


class Item:
    def __init__(self, name, sell_in, quality):
        self.name = name
        self.sell_in = sell_in
        self.quality = quality

    def __repr__(self):
        return "%s, %s, %s" % (self.name, self.sell_in, self.quality)
