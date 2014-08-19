#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import unittest

from tmgpm import Tmgpm


class TestTmgpmDefaultConstructor(unittest.TestCase):

    def setUp(self):
        self.tide = Tmgpm()

    def test_default_station(self):
        # check default station name is BREST
        self.assertEqual(self.tide.station_name, 'BREST')

    def test_default_date(self):
        # check default date is today
        today = datetime.date.today()
        self.assertEqual(datetime.date(self.tide.year, self.tide.month, self.tide.day), today)


class TestTmgpmConstructor(unittest.TestCase):

    def setUp(self):
        self.tide = Tmgpm('CONCARNEAU', 2014, 1, 1)

    def test_default_station(self):
        # check station name is properly set
        self.assertEqual(self.tide.station_name, 'CONCARNEAU')

    def test_default_date(self):
        # check date is properly set
        self.assertEqual(self.tide.year, 2014)
        self.assertEqual(self.tide.month, 1)
        self.assertEqual(self.tide.day, 1)


class TestTmgpmSetDate(unittest.TestCase):

    def setUp(self):
        self.tide = Tmgpm()

    def test_date_before_1900(self):
        # check that a date before 1/1/1900 before is refused
        self.assertRaises(ValueError, self.tide.set_date, 1899, 12, 31)

    def test_date_after_2100(self):
        # check default date is today
        self.assertRaises(ValueError, self.tide.set_date, 2100, 3, 1)


class TestTmgpmGetStationList(unittest.TestCase):

    def test_returns_a_list(self):
        # check we get a list
        station_list = Tmgpm.get_station_list()
        self.assertTrue(isinstance(station_list, list))

    def test_list_is_not_empty(self):
        # check the list is not empty
        station_list = Tmgpm.get_station_list()
        self.assertTrue(len(station_list) > 0)

    def test_list_contains_brest(self):
        # check the list contains at least BREST station
        station_list = Tmgpm.get_station_list()
        self.assertTrue('BREST' in station_list)


class TestTmgpmHarmonicConstituents(unittest.TestCase):

    def test_concarneau_1982(self):
        # Check that tide heigh in CONCARNEAU on the 1st January 1982
        # at 00:00 is 2302 mm
        tide = Tmgpm('CONCARNEAU', 1982, 1, 1)
        self.assertEqual(int(tide.height(0)), 2302)


if __name__ == '__main__':
    unittest.main()
