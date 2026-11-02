# -*- coding: utf-8 -*-
# ==========================================================================
# STEP 6 |  commit: refactor: one function per item type, if/elif instead of negated conditions
# WHAT : One function per item type, chosen by a positive if/elif/else.
# WHY  : Each rule is readable on its own and the double negatives disappear.
# NOTE : Adding a new item type still means editing the if/elif chain: fixed in step 8.
# TEST : python -m unittest -v   (run inside this folder)
# ==========================================================================

AGED_BRIE = "Aged Brie"
BACKSTAGE_PASSES = "Backstage passes to a TAFKAL80ETC concert"
SULFURAS = "Sulfuras, Hand of Ragnaros"
MIN_QUALITY = 0
MAX_QUALITY = 50


def increase_quality(item, amount=1):
    if item.quality < MAX_QUALITY:
        item.quality = min(MAX_QUALITY, item.quality + amount)


def decrease_quality(item, amount=1):
    if item.quality > MIN_QUALITY:
        item.quality = max(MIN_QUALITY, item.quality - amount)


# NEW: each item type gets its own function holding only ITS rules.
def update_normal_item(item):
    decrease_quality(item)
    item.sell_in = item.sell_in - 1
    if item.sell_in < 0:
        decrease_quality(item)


# Aged Brie: quality goes UP (twice as fast once expired).
def update_aged_brie(item):
    increase_quality(item)
    item.sell_in = item.sell_in - 1
    if item.sell_in < 0:
        increase_quality(item)


# Backstage passes: +1, +2 (11 days or fewer), +3 (6 days or fewer), 0 after the concert.
def update_backstage_passes(item):
    increase_quality(item)
    if item.sell_in < 11:
        increase_quality(item)
    if item.sell_in < 6:
        increase_quality(item)
    item.sell_in = item.sell_in - 1
    if item.sell_in < 0:
        item.quality = MIN_QUALITY


# CHANGED: positive if/elif/else dispatch replaces `!= A and != B` double negatives.
# Weakness: adding a new item type still means editing this chain (fixed in step 8).
def update_item(item):
    # Positive if/elif chain instead of negated "!= A and != B" conditions.
    if item.name == SULFURAS:
        return
    elif item.name == AGED_BRIE:
        update_aged_brie(item)
    elif item.name == BACKSTAGE_PASSES:
        update_backstage_passes(item)
    else:
        update_normal_item(item)


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
