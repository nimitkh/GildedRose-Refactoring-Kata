# -*- coding: utf-8 -*-
# ==========================================================================
# STEP 3 commit: refactor: replace magic strings and numbers with constants
# WHAT : Replace magic strings and numbers with named constants.
# WHY  : No logic changes, only names. Removes typo risk and makes rules readable.
# NOTE : Still nested and still full of `!=` conditions.
# TEST : python -m unittest -v   (run inside this folder)
# ==========================================================================

# NEW: constants replace the magic strings that were repeated through the code.
AGED_BRIE = "Aged Brie"
BACKSTAGE_PASSES = "Backstage passes to a TAFKAL80ETC concert"
SULFURAS = "Sulfuras, Hand of Ragnaros"
# NEW: named limits instead of bare 0 and 50.
MIN_QUALITY = 0
MAX_QUALITY = 50


class GildedRose(object):

    def __init__(self, items):
        self.items = items

    def update_quality(self):
        for item in self.items:
            # Logic is UNCHANGED: only the literals were replaced with constants.
            if item.name != AGED_BRIE and item.name != BACKSTAGE_PASSES:
                if item.quality > MIN_QUALITY:
                    if item.name != SULFURAS:
                        item.quality = item.quality - 1
            else:
                if item.quality < MAX_QUALITY:
                    item.quality = item.quality + 1
                    if item.name == BACKSTAGE_PASSES:
                        if item.sell_in < 11:
                            if item.quality < MAX_QUALITY:
                                item.quality = item.quality + 1
                        if item.sell_in < 6:
                            if item.quality < MAX_QUALITY:
                                item.quality = item.quality + 1
            if item.name != SULFURAS:
                item.sell_in = item.sell_in - 1
            if item.sell_in < 0:
                if item.name != AGED_BRIE:
                    if item.name != BACKSTAGE_PASSES:
                        if item.quality > MIN_QUALITY:
                            if item.name != SULFURAS:
                                item.quality = item.quality - 1
                    else:
                        item.quality = item.quality - item.quality
                else:
                    if item.quality < MAX_QUALITY:
                        item.quality = item.quality + 1


class Item:
    def __init__(self, name, sell_in, quality):
        self.name = name
        self.sell_in = sell_in
        self.quality = quality

    def __repr__(self):
        return "%s, %s, %s" % (self.name, self.sell_in, self.quality)
