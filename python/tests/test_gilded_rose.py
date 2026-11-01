# -*- coding: utf-8 -*-
# Tests written from GildedRoseRequirements.md. They describe the EXISTING behaviour first, so they are the
# safety net for every refactoring commit. Conjured tests are added in the Conjured commit.
#
"""Tests for the Gilded Rose kata, written from GildedRoseRequirements.md.

Each test names the requirement it protects, so a reviewer can map spec -> test.
They describe EXISTING behaviour first, so they are the safety net for the refactoring commits.
"""
import contextlib
import io
import unittest
from unittest import mock

import texttest_fixture
from gilded_rose import GildedRose, Item

AGED_BRIE = "Aged Brie"
BACKSTAGE_PASSES = "Backstage passes to a TAFKAL80ETC concert"
SULFURAS = "Sulfuras, Hand of Ragnaros"


def update(name, sell_in, quality, days=1):
    """Build one item, run `days` daily updates and return the item."""
    item = Item(name, sell_in, quality)
    shop = GildedRose([item])
    for _ in range(days):
        shop.update_quality()
    return item


class AllItemsTest(unittest.TestCase):
    def test_sell_in_is_lowered_every_day(self):
        # "At the end of each day our system lowers both values for every item"
        for name in ["foo", AGED_BRIE, BACKSTAGE_PASSES]:
            self.assertEqual(4, update(name, 5, 10).sell_in, name)

    def test_gilded_rose_updates_every_item_in_the_list(self):
        items = [Item("foo", 5, 5), Item(AGED_BRIE, 5, 5)]
        GildedRose(items).update_quality()
        self.assertEqual([4, 6], [item.quality for item in items])

    def test_empty_inventory_is_fine(self):
        GildedRose([]).update_quality()


class NormalItemTest(unittest.TestCase):
    def test_quality_is_lowered_by_one_each_day(self):
        self.assertEqual(9, update("foo", 5, 10).quality)

    def test_last_day_before_sell_by_is_still_the_normal_rate(self):
        self.assertEqual(9, update("foo", 1, 10).quality)

    def test_quality_degrades_twice_as_fast_after_sell_by_date(self):
        # "Once the sell by date has passed, Quality degrades twice as fast"
        self.assertEqual(8, update("foo", 0, 10).quality)
        self.assertEqual(8, update("foo", -5, 10).quality)

    def test_quality_is_never_negative(self):
        # "The Quality of an item is never negative"
        self.assertEqual(0, update("foo", 5, 0).quality)
        self.assertEqual(0, update("foo", 0, 1).quality)
        self.assertEqual(0, update("foo", -1, 1).quality)
        self.assertEqual(0, update("foo", 5, 1, days=10).quality)


class AgedBrieTest(unittest.TestCase):
    def test_increases_in_quality_the_older_it_gets(self):
        self.assertEqual(11, update(AGED_BRIE, 5, 10).quality)

    def test_increases_twice_as_fast_after_sell_by_date(self):
        self.assertEqual(12, update(AGED_BRIE, 0, 10).quality)
        self.assertEqual(12, update(AGED_BRIE, -3, 10).quality)

    def test_quality_is_never_more_than_50(self):
        # "The Quality of an item is never more than 50"
        self.assertEqual(50, update(AGED_BRIE, 5, 50).quality)
        self.assertEqual(50, update(AGED_BRIE, 0, 49).quality)
        self.assertEqual(50, update(AGED_BRIE, 5, 40, days=30).quality)


class SulfurasTest(unittest.TestCase):
    def test_never_has_to_be_sold_and_never_loses_quality(self):
        for sell_in in (5, 0, -1):
            item = update(SULFURAS, sell_in, 80, days=30)
            self.assertEqual((sell_in, 80), (item.sell_in, item.quality), sell_in)


class BackstagePassTest(unittest.TestCase):
    def test_increases_by_1_with_more_than_10_days_left(self):
        self.assertEqual(21, update(BACKSTAGE_PASSES, 11, 20).quality)
        self.assertEqual(21, update(BACKSTAGE_PASSES, 30, 20).quality)

    def test_increases_by_2_with_10_days_or_less(self):
        for sell_in in (10, 9, 8, 7, 6):
            self.assertEqual(22, update(BACKSTAGE_PASSES, sell_in, 20).quality, sell_in)

    def test_increases_by_3_with_5_days_or_less(self):
        for sell_in in (5, 4, 3, 2, 1):
            self.assertEqual(23, update(BACKSTAGE_PASSES, sell_in, 20).quality, sell_in)

    def test_drops_to_0_after_the_concert(self):
        self.assertEqual(0, update(BACKSTAGE_PASSES, 0, 20).quality)
        self.assertEqual(0, update(BACKSTAGE_PASSES, -1, 20).quality)
        self.assertEqual(0, update(BACKSTAGE_PASSES, 1, 20, days=2).quality)
        self.assertEqual(0, update(BACKSTAGE_PASSES, 0, 20, days=5).quality)

    def test_quality_is_never_more_than_50(self):
        self.assertEqual(50, update(BACKSTAGE_PASSES, 5, 49).quality)
        self.assertEqual(50, update(BACKSTAGE_PASSES, 10, 49).quality)
        self.assertEqual(50, update(BACKSTAGE_PASSES, 15, 50).quality)


class ThirtyDayTrajectoryTest(unittest.TestCase):
    """Quality of the kata's sample items on each of 30 days (index 0 = starting value)."""

    TRAJECTORIES = [
        ("+5 Dexterity Vest", 10, 20,
         [20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 8, 6, 4, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
        ("Aged Brie", 2, 0,
         [0, 1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 50, 50, 50, 50]),
        ("Elixir of the Mongoose", 5, 7,
         [7, 6, 5, 4, 3, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
        ("Sulfuras, Hand of Ragnaros", 0, 80,
         [80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80]),
        ("Backstage passes to a TAFKAL80ETC concert", 15, 20,
         [20, 21, 22, 23, 24, 25, 27, 29, 31, 33, 35, 38, 41, 44, 47, 50, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
        ("Backstage passes to a TAFKAL80ETC concert", 10, 49,
         [49, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
        ("Backstage passes to a TAFKAL80ETC concert", 5, 49,
         [49, 50, 50, 50, 50, 50, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
    ]

    def test_quality_and_sell_in_every_day(self):
        for name, sell_in, quality, expected in self.TRAJECTORIES:
            item = Item(name, sell_in, quality)
            shop = GildedRose([item])
            for day, expected_quality in enumerate(expected):
                with self.subTest(item=name, start=(sell_in, quality), day=day):
                    self.assertEqual(expected_quality, item.quality)
                    self.assertEqual(sell_in if name == SULFURAS else sell_in - day, item.sell_in)
                shop.update_quality()


class TextFixtureTest(unittest.TestCase):
    """Runs the kata's own texttest_fixture.main() and checks the printed report."""

    def run_fixture(self, *args):
        out = io.StringIO()
        with mock.patch("sys.argv", ["texttest_fixture.py", *args]), contextlib.redirect_stdout(out):
            texttest_fixture.main()
        return out.getvalue()

    def test_default_run_prints_two_days(self):
        report = self.run_fixture()
        self.assertIn("-------- day 1 --------", report)
        self.assertNotIn("-------- day 2 --------", report)

    def test_30_day_run_prints_days_0_to_30(self):
        report = self.run_fixture("30")
        self.assertIn("-------- day 0 --------", report)
        self.assertIn("-------- day 30 --------", report)
        self.assertNotIn("-------- day 31 --------", report)

    def test_30_day_run_final_state_of_every_regular_item(self):
        last_day = self.run_fixture("30").split("-------- day 30 --------")[1]
        for row in [
        "+5 Dexterity Vest, -20, 0",
        "Aged Brie, -28, 50",
        "Elixir of the Mongoose, -25, 0",
        "Sulfuras, Hand of Ragnaros, 0, 80",
        "Backstage passes to a TAFKAL80ETC concert, -15, 0",
        "Backstage passes to a TAFKAL80ETC concert, -20, 0",
        "Backstage passes to a TAFKAL80ETC concert, -25, 0",
        "Sulfuras, Hand of Ragnaros, -1, 80",
        ]:
            self.assertIn(row, last_day)

if __name__ == "__main__":
    unittest.main()
