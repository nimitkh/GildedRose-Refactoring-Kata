# -*- coding: utf-8 -*-
# ==========================================================================
# STEP 4 |  commit: refactor: extract increase/decrease quality helpers
# WHAT : Extract increase_quality() / decrease_quality() helpers.
# WHY  : The repeated `if quality < 50: quality += 1` blocks now live in one place each.
# NOTE : Still has negated conditions (`!=`): removed in steps 5 and 6.
# TEST : python -m unittest -v   (run inside this folder)
# ==========================================================================

AGED_BRIE = "Aged Brie"
BACKSTAGE_PASSES = "Backstage passes to a TAFKAL80ETC concert"
SULFURAS = "Sulfuras, Hand of Ragnaros"
MIN_QUALITY = 0
MAX_QUALITY = 50


# NEW helper: replaces every repeated `if quality < 50: quality += 1` block.
# The upper-bound check now lives in ONE place.
def increase_quality(item, amount=1):
    if item.quality < MAX_QUALITY:
        item.quality = min(MAX_QUALITY, item.quality + amount)


# NEW helper: same idea for `quality > 0` / `quality - 1`.
def decrease_quality(item, amount=1):
    if item.quality > MIN_QUALITY:
        item.quality = max(MIN_QUALITY, item.quality - amount)


class GildedRose(object):

    def __init__(self, items):
        self.items = items

    def update_quality(self):
        for item in self.items:
            # The nested bounds checks (quality > 0, quality < 50) are gone: the helpers handle them.
            # Still negated (`!=`) conditions here: removed in steps 5 and 6.
            if item.name != AGED_BRIE and item.name != BACKSTAGE_PASSES:
                if item.name != SULFURAS:
                    decrease_quality(item)
            else:
                increase_quality(item)
                if item.name == BACKSTAGE_PASSES:
                    if item.sell_in < 11:
                        increase_quality(item)
                    if item.sell_in < 6:
                        increase_quality(item)
            if item.name != SULFURAS:
                item.sell_in = item.sell_in - 1
            if item.sell_in < 0:
                if item.name != AGED_BRIE:
                    if item.name != BACKSTAGE_PASSES:
                        if item.name != SULFURAS:
                            decrease_quality(item)
                    else:
                        item.quality = MIN_QUALITY
                else:
                    increase_quality(item)


class Item:
    def __init__(self, name, sell_in, quality):
        self.name = name
        self.sell_in = sell_in
        self.quality = quality

    def __repr__(self):
        return "%s, %s, %s" % (self.name, self.sell_in, self.quality)
