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


from math import pi
import FreeCAD
import Part
from SlopedPlanesPy import _Py


V = FreeCAD.Vector


__title__ = "SlopedPlanes Macro"
__author__ = "Damian Caceres Moreno"
__url__ = "http://www.freecadweb.org"
__version__ = ""


def makePyEdge(pyPlane):

    ''''''

    geom = pyPlane.geom

    if isinstance(geom, Part.LineSegment):
        pyEdge = _PyEdgeLineSegment(pyPlane)

    if isinstance(geom, Part.ArcOfParabola):
        pyEdge = _PyEdgeArcOfParabola(pyPlane)

    if isinstance(geom, Part.ArcOfHyperbola):
        pyEdge = _PyEdgeArcOfHyperbola(pyPlane)

    if isinstance(geom, Part.ArcOfCircle):
        pyEdge = _PyEdgeArcOfCircle(pyPlane)

    if isinstance(geom, Part.ArcOfEllipse):
        pyEdge = _PyEdgeArcOfEllipse(pyPlane)

    if isinstance(geom, Part.BSplineCurve):
        pyEdge = _PyEdgeBSplineCurve(pyPlane)

    return pyEdge


class _PyEdge(_Py):

    '''The complementary python object class for edges.The edges of the base
    sketch are extruded to create the planes. This is a delagated class'''

    def __init__(self, pyPlane):

        '''__init__(self, pyPlane)'''

        self.plane = pyPlane
        geom = pyPlane.geom
        self.geom = geom
        self.firstParam = geom.FirstParameter
        self.lastParam = geom.LastParameter

        # print('geom ', geom)
        # print('firstParam ', firstParam)
        # print('lastParam ', lastParam)

    @property
    def forward(self):

        ''''''

        return self._forward

    @forward.setter
    def forward(self, forward):

        ''''''

        self._forward = forward

    @property
    def backward(self):

        ''''''

        return self._backward

    @backward.setter
    def backward(self, backward):

        ''''''

        self._backward = backward

    def params(self, geom, gg, startParam, endParam, sParam, eParam):

        ''''''

        forwardLine = self.makeGeom(geom, startParam, endParam)
        # print('forwardLine ', forwardLine)
        # print(forwardLine.value(startParam), forwardLine.value(endParam))
        forwardLineShape = forwardLine.toShape()
        self.forward = forwardLineShape

        backwardLine = self.makeGeom(gg, sParam, eParam)
        # print('backwardLine ', backwardLine)
        # print(backwardLine.value(sParam), backwardLine.value(eParam))
        backwardLineShape = backwardLine.toShape()
        self.backward = backwardLineShape


class _PyEdgeOpen(_PyEdge):

    ''''''

    def __init__(self, pyPlane):

        '''__init__(self, pyPlane)'''

        _PyEdge.__init__(self, pyPlane)

    def forBack(self):

        ''''''

        geom = self.geom
        firstParam = self.firstParam
        lastParam = self.lastParam

        startParam = lastParam
        endParam = lastParam + _Py.size

        gg = geom
        sParam = firstParam
        eParam = firstParam - _Py.size

        self.params(geom, gg, startParam, endParam, sParam, eParam)

    def baseEdge(self, leftScale, rightScale):

        ''''''

        startParam = self.firstParam - leftScale
        endParam = self.lastParam + rightScale

        return startParam, endParam


class _PyEdgeLineSegment(_PyEdgeOpen):

    ''''''

    def __init__(self, pyPlane):

        '''__init__(self, pyPlane)'''

        _PyEdgeOpen.__init__(self, pyPlane)


class _PyEdgeArcOfParabola(_PyEdgeOpen):

    ''''''

    def __init__(self, pyPlane):

        '''__init__(self, pyPlane)'''

        _PyEdgeOpen.__init__(self, pyPlane)


class _PyEdgeArcOfHyperbola(_PyEdgeOpen):

    ''''''

    def __init__(self, pyPlane):

        '''__init__(self, pyPlane)'''

        _PyEdgeOpen.__init__(self, pyPlane)

    def baseEdge(self, leftScale, rightScale):

        ''''''

        startParam = self.firstParam
        endParam = self.lastParam

        return startParam, endParam


class _PyEdgeClosed(_PyEdge):

    ''''''

    def __init__(self, pyPlane):

        '''__init__(self, pyPlane)'''

        _PyEdge.__init__(self, pyPlane)

    def forBack(self):

        ''''''

        geom = self.geom
        firstParam = self.firstParam
        lastParam = self.lastParam

        if geom.Axis == V(0, 0, 1):
            # print('A')

            half = (2 * pi - (lastParam - firstParam)) / 2
            startParam = lastParam
            endParam = lastParam + half

            # print('half ', half)
            # print('startParam ', startParam)
            # print('endParam ', endParam)

            gg = geom.copy()
            gg.Axis = _Py.normal * -1
            sParam = 2 * pi - firstParam
            eParam = sParam + half

            # print('gg ', gg)

            # print('sParam ', sParam)
            # print('eParam ', eParam)

        else:
            # print('B')

            half = (2 * pi - (lastParam - firstParam)) / 2
            startParam = lastParam
            endParam = lastParam + half

            # print('half ', half)
            # print('startParam ', startParam)
            # print('endParam ', endParam)

            gg = geom.copy()
            gg.Axis = _Py.normal
            sParam = 2 * pi - firstParam
            eParam = sParam + half

            # print('gg ', gg)
            # print('sParam ', sParam)
            # print('eParam ', eParam)

        self.params(geom, gg, startParam, endParam, sParam, eParam)

    def baseEdge(self, leftScale, rightScale):

        ''''''

        pyPlane = self.plane
        firstParam = self.firstParam
        lastParam = self.lastParam

        rear = pyPlane.rear

        if rear:
            # print('reflex')

            if len(rear) == 1:
                # print('c1')

                pyReflex = pyPlane.reflexedList[0]

                if rear[0] == pyReflex.rear[0]:
                    # print('c11')

                    startParam = firstParam
                    endParam = startParam + 2 * pi

                else:
                    # print('c12')

                    startParam = lastParam
                    endParam = startParam - 2 * pi

            else:
                # print('c2')

                startParam =\
                    (2 * pi - (lastParam - firstParam)) / 2 + lastParam
                endParam = startParam + 2 * pi

        else:
            # print('no reflex')

            dist = abs(lastParam - firstParam)
            # print('dist ', dist)

            if dist >= pi:
                # print('2pi o more')

                startParam = firstParam
                endParam = lastParam

            else:
                # print('less 2pi')

                center = (lastParam - firstParam) / 2 + firstParam
                # print('center ', center)
                startParam = center - pi / 2
                endParam = center + pi / 2

        return startParam, endParam


class _PyEdgeArcOfCircle(_PyEdgeClosed):

    ''''''

    def __init__(self, pyPlane):

        '''__init__(self, pyPlane)'''

        _PyEdgeClosed.__init__(self, pyPlane)


class _PyEdgeArcOfEllipse(_PyEdgeClosed):

    ''''''

    def __init__(self, pyPlane):

        '''__init__(self, pyPlane)'''

        _PyEdgeClosed.__init__(self, pyPlane)


class _PyEdgeBSplineCurve(_PyEdge):

    ''''''

    def __init__(self, pyPlane):

        '''__init__(self, pyPlane)'''

        _PyEdge.__init__(self, pyPlane)
