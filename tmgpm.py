#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tide calculator based on "La Table des Marées des Grands Ports du Monde" (SHOM)

Please review the README file carefully before using this software.
"""

__author__ = "Hervé Le Roy"
__email__ = "hleroy@hleroy.com"

import csv
import datetime
from math import cos, acos, sin, asin, degrees, radians, floor, sqrt, pow as power, copysign
import os


def sign(x):
    return copysign(1, x)


class Tmgpm(object):

    # Load stations data from csv file
    stations_data = {}
    filename = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'tmgpm.csv')
    with open(filename) as csvfile:
        csvreader = csv.DictReader(row for row in csvfile if not row.startswith('#'))
        for row in csvreader:
            name = row.pop('NAME')
            stations_data[name] = row

    # Constants initialization
    n1 = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, -2, -3, 0, -2, 0, 0, 0, 0, 0, 0], [-2, -3, 0, -4, -4, -3, -1, 0, 0, -2, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [-5, -4, -2, 0, 0, 0, 0, 0, 0, 0, 0]]
    n2 = [[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [1, 1, 1, -1, 1, 1, 0, 0, 0, 0, 0], [2, 2, 0, 2, 4, 4, 2, 2, -1, 2, 2], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [4, 4, 2, 0, 0, 0, 0, 0, 0, 0, 0]]
    n3 = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0], [0, 1, 0, 2, 0, -1, -1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
    n4 = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, -1, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
    n5 = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
    n6 = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [1, -1, -1, 1, -1, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

    def __init__(self, station_name=None, year=None, month=None, day=None):
        """Initialise a Tmpgpm object

        If the station name is omitted, it defaults to 'BREST'.
        The date must be comprised between 1/3/1900 and 28/02/2100. If the date is omitted, it defaults to today.

        Args:
          station_name (str, optional)-- station name, defaults to 'BREST'
          year (int, optional) -- year (4 digits, e.g. 1980), defaults to current year
          month (int, optional) -- month (1 to 12), defaults to current month
          day (int, optional) -- day (1 to 31), defaults to current day
        """

        # Initialise instance attributes to None to make PyLint happy
        self.station_data = None
        self.station_name = None
        self.year = None
        self.month = None
        self.day = None
        self.LO = None
        self.LA = None
        self.UTC = None
        self.Z0 = None
        self.A = None
        self.G = None
        self.R0 = None
        self.R24 = None
        self.phi0 = None
        self.phi24 = None

        # Set station name or defaults to BREST
        self.set_station(station_name if (station_name is not None) else "BREST")

        # Set date or defaults to datetime.now()
        if not any([year, month, day]):  # if year, month and date are all None
            now = datetime.datetime.now()  # use datetime.now()
            year = now.year
            month = now.month
            day = now.day
        self.set_date(year, month, day)

    @staticmethod
    def get_station_list():
        """Return the list of stations

        Returns:
          A list of strings with the station names
        """
        return list(Tmgpm.stations_data.keys())

    def get_station_tz(self):
        """Return current station timezone offset

        Returns:
          A string with the timezone offset e.g. +1.0
        """
        return self.UTC

    def set_station(self, station_name):
        """Set station name and initialize harmonic data for this station

        Args:
          station_name (str): station name

        Raises:
          ValueError: if the station name is not recognized
        """
        if station_name in Tmgpm.stations_data:
            self.station_name = station_name
            self.station_data = Tmgpm.stations_data[station_name]
            self._init_harmonic_data()
        else:
            raise ValueError("Station name not recognized")

    def set_date(self, year, month, day):
        """Set date and compute data for this date

        The date must be comprised between 1/3/1900 and 28/02/2100.

        Args:
          year (int) -- Year (4 digits, e.g. 1980)
          month (int) -- Month (1 to 12)
          day (int) -- Day (1 to 31)

        Raises:
          ValueError: if the date is not a valid or out of bounds
        """
        # Check if the date is valid
        try:
            d = datetime.date(year, month, day)
        except:
            raise ValueError("The date is not valid")

        # Check if the date is comprised between 1/3/1900 and 28/02/2100
        if datetime.date(1900, 3, 1) < d < datetime.date(2100, 2, 28):
            self.year = year
            self.month = month
            self.day = day
            self._init_precalc()
        else:
            raise ValueError("The date is out of bounds. It must be comprised between 1/3/1900 and 28/02/2100")

    def height(self, t):
        """Calculate tide height at the given time

        Args:
          t (float) -- Time expressed as a fractional number (e.g. 9.5 for 09h30m

        Returns:
          Tide height in mmillimeters
        """
        # Initialize tide height at the station Z0 value
        # Z0 is stored in cm and the tide calculations are done in millimeters,
        # hence the * 10
        height = self.Z0 * 10

        # Calculate tide height
        for j in range(5):
            if j != 3:
                Rj = self.R0[j] + t / 24.0 * (self.R24[j] - self.R0[j])
                delta_j = self.phi24[j] - self.phi0[j]
                if delta_j < -180:
                    delta_j += 360
                if delta_j > 180:
                    delta_j -= 360
                phij = self.phi0[j] + t / 24.0 * (j * 360 + delta_j)
                height += Rj * cos(radians(phij))

        # and return the value
        return height

    def _init_harmonic_data(self):
        self.A = [[0. for _ in range(11)] for _ in range(5)]
        self.G = [[0. for _ in range(11)] for _ in range(5)]
        self.Z0 = float(self.station_data['Z0'])
        self.A[0][0] = float(self.station_data['ASa'])
        self.A[1][0] = float(self.station_data['AK1'])
        self.A[1][1] = float(self.station_data['AO1'])
        self.A[1][2] = float(self.station_data['AQ1'])
        self.A[1][3] = -1 / 3.0 * float(self.station_data['AK1'])
        self.A[1][4] = 1 / 5.3 * float(self.station_data['AO1'])
        self.A[1][5] = 1 / 7.4 * float(self.station_data['AK1'])
        self.A[2][0] = float(self.station_data['AM2'])
        self.A[2][1] = float(self.station_data['AN2'])
        self.A[2][2] = float(self.station_data['AS2'])
        self.A[2][3] = 1 / 7.6 * float(self.station_data['AN2'])
        self.A[2][4] = 1 / 6.3 * float(self.station_data['AN2'])
        self.A[2][5] = 1 / 5.3 * float(self.station_data['AN2'])
        self.A[2][6] = -1 / 35.0 * float(self.station_data['AM2'])
        self.A[2][7] = 1 / 3.7 * float(self.station_data['AS2'])
        self.A[2][8] = 1 / 17.0 * float(self.station_data['AS2'])
        self.A[2][9] = -1 / 27.0 * float(self.station_data['AM2'])
        self.A[2][10] = 1 / 12.0 * float(self.station_data['AS2'])
        self.A[4][0] = float(self.station_data['AMN4'])
        self.A[4][1] = float(self.station_data['AM4'])
        self.A[4][2] = float(self.station_data['AMS4'])
        self.G[0][0] = float(self.station_data['GSa'])
        self.G[1][0] = float(self.station_data['GK1'])
        self.G[1][1] = float(self.station_data['GO1'])
        self.G[1][2] = float(self.station_data['GQ1'])
        self.G[1][3] = float(self.station_data['GK1'])
        self.G[1][4] = float(self.station_data['GO1'])
        self.G[1][5] = float(self.station_data['GK1'])
        self.G[2][0] = float(self.station_data['GM2'])
        self.G[2][1] = float(self.station_data['GN2'])
        self.G[2][2] = float(self.station_data['GS2'])
        self.G[2][3] = float(self.station_data['GN2'])
        self.G[2][4] = float(self.station_data['GN2'])
        self.G[2][5] = float(self.station_data['GN2'])
        self.G[2][6] = float(self.station_data['GM2'])
        self.G[2][7] = float(self.station_data['GS2'])
        self.G[2][8] = float(self.station_data['GS2']) - 283
        self.G[2][9] = float(self.station_data['GM2'])
        self.G[2][10] = float(self.station_data['GS2'])
        self.G[4][0] = float(self.station_data['GMN4'])
        self.G[4][1] = float(self.station_data['GM4'])
        self.G[4][2] = float(self.station_data['GMS4'])
        self.LA = self.station_data['LA']
        self.LO = self.station_data['LO']
        self.UTC = self.station_data['UTC']
        # TODO: add control mechanism

    def _init_precalc(self):

        def compute_R_and_phi_at(t):
            R = [0., 0., 0., 0., 0.]
            phi = [0., 0., 0., 0., 0.]

            T = floor(30.6001 * (1 + self.month + 12 * floor(1 / (self.month + 1.0) + 0.7))) + floor(
                365.25 * (self.year - floor(1 / (self.month + 1.0) + 0.7))) + self.day + t / 24 - 723258
            h = 279.82 + 0.98564734 * T
            s = 78.16 + 13.17639673 * T
            p = 349.5 + 0.11140408 * T
            N = 208.1 + 0.05295392 * T
            p1 = 282.6 + 0.000047069 * T
            D = 90

            for j in range(5):
                if j != 3:
                    Xj = 0
                    Yj = 0
                    for i in range(11):
                        Vij = 15 * j * t + Tmgpm.n1[j][i] * s + Tmgpm.n2[j][i] * h + Tmgpm.n3[j][i] * p + \
                            Tmgpm.n4[j][i] * N + Tmgpm.n5[j][i] * p1 + Tmgpm.n6[j][i] * D
                        Xj += self.A[j][i] * cos(radians(Vij - self.G[j][i]))
                        Yj += self.A[j][i] * sin(radians(Vij - self.G[j][i]))

                    R[j] = sqrt(power(Xj, 2) + power(Yj, 2))
                    if R[j] == 0:
                        phi[j] = 90
                    else:
                        phi[j] = degrees(
                            acos(Xj / R[j])) * sign(degrees(asin(Yj / R[j])))

            return R, phi

        self.R0, self.phi0 = compute_R_and_phi_at(0)
        self.R24, self.phi24 = compute_R_and_phi_at(24)

    def __repr__(self):
        """Return a string containing a printable representation of a Tmgpm object"""
        return """'{}.{}("{}", {}, {}, {})'""".format(self.__class__.__module__,
                                                      self.__class__.__name__,
                                                      self.station_name,
                                                      self.year,
                                                      self.month,
                                                      self.day)

    def __str__(self):
        """Return a string containing a nicely printable representation of a Tmgpm"""
        return """Tide object for {} on {:%d, %b %Y}""".format(self.station_name,
                                                               datetime.date(self.year, self.month, self.day))
