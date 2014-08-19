PyTmgpm
=======

PyTmgpm is a tide calculator based on the book "Table des marées des grands ports du monde" (TMGPM) published by the Service Hydrographique et Océanique de la Marine (SHOM) from 1982 until 1999.

The TMGPM explained to navigators how to calculate tide levels in 1080 locations in the world with a simple programmable calculator. It provided the mathematical formulation and harmonic constituents to predict tide with an acceptable accuracy, given the technical limitations of programmable calculators in the 1980s.

The book was later withdrawn from publication for security concerns (according to the SHOM, the free publication of harmonic constituents raises concerns regarding their origin, reliability and update).

PyTmgpm is provided for educational purposes only, in the hope that it will be useful to understand the principles of tide calculations. **It must not by used for navigation.**


Prerequisites
-------------

PyTmgpm was tested with Python 3.4 on Uubuntu 14.04. It should run fine with any Python 3.x flavors.


Usage
-----

Firt import tmgpm (make sure it's on your PYTHONPATH)

.. sourcecode:: python

    import tmgpm
    

You can create a Tmgpm object, then set the station and date

.. sourcecode:: python

      tide = tmgpm.Tmgpm()
      tide.set_station('CONCARNEAU')
      tide.set_date(2014, 8, 15)      # 15th August 2014
    

Or you can create the object, set the station and date at the same time

.. sourcecode:: python

      tide = tmgpm.Tmgpm('CONCARNEAU', 2014, 8, 15)
    

Calculate and print tide height at 09h30

.. sourcecode:: python

      h = tide.height(9.5) # You must provide time with decimal minutes (e.g. 9.5 for 09h30)
      print(h)
    


Copyright and license
---------------------

The harmonic constituents provided in the TMGPM are the property of SHOM. Harmonic constituents for CONCARNEAU (Finistère, France) are provided as an example under the right to quote.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.