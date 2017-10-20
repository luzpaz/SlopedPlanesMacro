# -*- coding: utf8 -*-
# *****************************************************************************
# *                                                                           *
# *    Copyright (c) 2017                                                     *
# *                                                                           *
# *    This program is free software; you can redistribute it and/or modify   *
# *    it under the terms of the GNU Lesser General Public License (LGPL)     *
# *    as published by the Free Software Foundation; either version 2 of      *
# *    the License, or (at your option) any later version.                    *
# *    For detail see the LICENSE text file.                                  *
# *                                                                           *
# *    This program is distributed in the hope that it will be useful,        *
# *    but WITHOUT ANY WARRANTY; without even the implied warranty of         *
# *    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                   *
# *    See the  GNU Library General Public License for more details.          *
# *                                                                           *
# *    You should have received a copy of the GNU Library General Public      *
# *    License along with this program; if not, write to the Free Software    *
# *    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307   *
# *    USA                                                                    *
# *                                                                           *
# *****************************************************************************


from SlopedPlanesUtils import *
import SlopedPlanesPy


__title__ = "SlopedPlanes Macro"
__author__ = "Damian Caceres Moreno"
__url__ = "http://www.freecadweb.org"


class _Wire(SlopedPlanesPy._Py):

    ''''''

    def __init__(self, numWire):

        ''''''

        self.numWire = numWire
        self.reflexs = []
        self.planes = []
        self.coordinates = []
        self.shapeGeom = []
        self.reset = False

    @property
    def numWire(self):

        ''''''

        return self._numWire

    @numWire.setter
    def numWire(self, numWire):

        ''''''

        self._numWire = numWire

    @property
    def reflexs(self):

        ''''''

        return self._reflexs

    @reflexs.setter
    def reflexs(self, reflexs):

        ''''''

        self._reflexs = reflexs

    @property
    def planes(self):

        ''''''

        return self._planes

    @planes.setter
    def planes(self, planes):

        ''''''

        self._planes = planes

    @property
    def coordinates(self):

        ''''''

        return self._coordinates

    @coordinates.setter
    def coordinates(self, coordinates):

        ''''''

        self._coordinates = coordinates

    @property
    def shapeGeom(self):

        ''''''

        return self._shapeGeom

    @shapeGeom.setter
    def shapeGeom(self, shapeGeom):

        ''''''

        self._shapeGeom = shapeGeom

    @property
    def reset(self):

        ''''''

        return self._reset

    @reset.setter
    def reset(self, reset):

        ''''''

        self._reset = reset
