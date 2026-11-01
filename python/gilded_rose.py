# -*- coding: utf-8 -*-
# ==========================================================================
# STEP 5 |  commit: refactor: extract update_item and add guard clause for Sulfuras
# WHAT : Extract update_item() and add a guard clause for Sulfuras.
# WHY  : Sulfuras never changes, so returning early deletes every `!= SULFURAS` check.
# NOTE : Still has `!= AGED_BRIE and != BACKSTAGE_PASSES` double negatives: removed in step 6.
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


# NEW: loop body extracted so one item = one function.
def update_item(item):
    # Guard clause: Sulfuras never changes, so every "!= SULFURAS" check disappears.
    # NEW guard clause: Sulfuras never changes, so return early.
    # This deletes every `!= SULFURAS` check that used to be scattered below.
    if item.name == SULFURAS:
        return

    if item.name != AGED_BRIE and item.name != BACKSTAGE_PASSES:
        decrease_quality(item)
    else:
        increase_quality(item)
        if item.name == BACKSTAGE_PASSES:
            if item.sell_in < 11:
                increase_quality(item)
            if item.sell_in < 6:
                increase_quality(item)

    item.sell_in = item.sell_in - 1

    if item.sell_in < 0:
        if item.name != AGED_BRIE:
            if item.name != BACKSTAGE_PASSES:
                decrease_quality(item)
            else:
                item.quality = MIN_QUALITY
        else:
            increase_quality(item)


# update_quality is now a thin loop. Public API GildedRose(items).update_quality() is unchanged.
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
