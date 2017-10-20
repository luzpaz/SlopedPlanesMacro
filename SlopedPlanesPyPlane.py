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


import Part
from SlopedPlanesUtils import *
import SlopedPlanesPy


__title__ = "SlopedPlanes Macro"
__author__ = "Damian Caceres Moreno"
__url__ = "http://www.freecadweb.org"


class _Plane(SlopedPlanesPy._Py):

    ''''''

    def __init__(self, numWire, numGeom):

        ''''''

        self.numWire = numWire
        self.numGeom = numGeom
        self.angle = 45.0
        self.width = (1, 1)
        self.length = 2
        self.rear = []
        self.rango = []
        self.reflexed = False
        self.aligned = False
        self.choped = False
        self.arrow = False
        self.geom = None
        self.geomAligned = None
        self.shape = None
        self.bigShape = None
        self.enormousShape = None
        self.cutter = []
        self.oppCutter = []
        self.forward = None
        self.backward = None
        self.problem = []

    @property
    def numWire(self):

        ''''''

        return self._numWire

    @numWire.setter
    def numWire(self, numWire):

        ''''''

        self._numWire = numWire

    @property
    def numGeom(self):

        ''''''

        return self._numGeom

    @numGeom.setter
    def numGeom(self, numGeom):

        ''''''

        self._numGeom = numGeom

    @property
    def angle(self):

        ''''''

        return self._angle

    @angle.setter
    def angle(self, angle):

        ''''''

        self._angle = angle

    @property
    def width(self):

        ''''''

        return self._width

    @width.setter
    def width(self, width):

        ''''''

        self._width = width

    @property
    def length(self):

        ''''''

        return self._length

    @length.setter
    def length(self, length):

        ''''''

        self._length = length

    @property
    def rear(self):

        ''''''

        return self._rear

    @rear.setter
    def rear(self, rear):

        ''''''

        self._rear = rear

    @property
    def rango(self):

        ''''''

        return self._rango

    @rango.setter
    def rango(self, rango):

        ''''''

        self._rango = rango

    @property
    def reflexed(self):

        ''''''

        return self._reflexed

    @reflexed.setter
    def reflexed(self, reflexed):

        ''''''

        self._reflexed = reflexed

    @property
    def aligned(self):

        ''''''

        return self._aligned

    @aligned.setter
    def aligned(self, aligned):

        ''''''

        self._aligned = aligned

    @property
    def choped(self):

        ''''''

        return self._choped

    @choped.setter
    def choped(self, choped):

        ''''''

        self._choped = choped

    @property
    def arrow(self):

        ''''''

        return self._arrow

    @arrow.setter
    def arrow(self, arrow):

        ''''''

        self._arrow = arrow

    @property
    def geom(self):

        ''''''

        return self._geom

    @geom.setter
    def geom(self, geom):

        ''''''

        self._geom = geom

    @property
    def geomAligned(self):

        ''''''

        return self._geomAligned

    @geomAligned.setter
    def geomAligned(self, geomAligned):

        ''''''

        self._geomAligned = geomAligned

    @property
    def shape(self):

        ''''''

        return self._shape

    @shape.setter
    def shape(self, shape):

        ''''''

        self._shape = shape

    @property
    def bigShape(self):

        ''''''

        return self._bigShape

    @bigShape.setter
    def bigShape(self, bigShape):

        ''''''

        self._bigShape = bigShape

    @property
    def enormousShape(self):

        ''''''

        return self._enormousShape

    @enormousShape.setter
    def enormousShape(self, enormousShape):

        ''''''

        self._enormousShape = enormousShape

    @property
    def cutter(self):

        ''''''

        return self._cutter

    @cutter.setter
    def cutter(self, cutter):

        ''''''

        self._cutter = cutter

    @property
    def oppCutter(self):

        ''''''

        return self._oppCutter

    @oppCutter.setter
    def oppCutter(self, oppCutter):

        ''''''

        self._oppCutter = oppCutter

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

    @property
    def problem(self):

        ''''''

        return self._problem

    @problem.setter
    def problem(self, problem):

        ''''''

        self._problem = problem

    def trackShape(self, pyWire, normal, size, reverse):

        ''''''

        coordinates = pyWire.coordinates
        numGeom = self.numGeom
        geom = self.geomAligned
        eje = coordinates[numGeom+1].sub(coordinates[numGeom])
        direction = rotateVector(eje, normal, 90)
        angle = self.angle
        if reverse:
            angle = angle * -1
        direction = rotateVector(direction, eje, angle)
        direction.normalize()

        firstParam = geom.FirstParameter
        lastParam = geom.LastParameter

        scale = 1
        plane =\
            self.doPlane(size, direction, geom, firstParam,
                         lastParam, scale)
        self.shape = plane

        scale = 10
        bigPlane =\
            self.doPlane(size, direction, geom, firstParam,
                         lastParam, scale)
        self.bigShape = bigPlane

        if self.reflexed:

            scale = 100
            enormousPlane =\
                self.doPlane(size, direction, geom, firstParam,
                             lastParam, scale)
            self.enormousShape = enormousPlane

    def doPlane(self, size, direction, geom, firstParam, lastParam, scale):

        ''''''

        leftScale = self.width[0] * scale
        rightScale = self.width[1] * scale
        upScale = self.length * scale

        startParam = firstParam - leftScale * size
        endParam = lastParam + rightScale * size
        extendGeom = Part.LineSegment(geom, startParam, endParam)
        plane = extendGeom.toShape().extrude(direction*upScale*size)

        return plane

    def solvePlane(self, pyFace, pyWire, tolerance):

        ''''''

        print '###### solvePlane'

        pyPlaneList = pyWire.planes

        numGeom = self.numGeom

        cutterList = []
        for pyPl in pyPlaneList:
            if pyPl.numGeom != numGeom:
                # print 'numGeom ', pyPl.numGeom
                if not (pyPl.choped and not pyPl.aligned):
                    pl = pyPl.shape

                    if not pyPl.aligned:
                        # print 'a'
                        cutterList.append(pl)

                    else:
                        # print 'b'
                        if pl:
                            # print 'b1'

                            # no seria mejor simulatedShape en el plano ?

                            pyAli =\
                                pyFace.selectAlignament(pyPl.numWire,
                                                        pyPl.numGeom)

                            if self.aligned:
                                # print 'b11'

                                pyAlign =\
                                    pyFace.selectAlignament(self.numWire,
                                                            self.numGeom)

                                ch = []
                                for [ch1, ch2] in pyAli.chops:
                                    ch.extend([ch1, ch2])

                                for [pyChopOne, pyChopTwo] in pyAlign.chops:
                                    if pyPl in [pyChopOne, pyChopTwo]:
                                        break
                                    elif (pyChopOne in pyAli.aligns or
                                          pyChopTwo in pyAli.aligns):
                                        break
                                    elif (pyChopOne in ch or
                                          pyChopTwo in ch):
                                        break
                                else:
                                    # print 'b111'
                                    simulatedPl = pyAli.simulatedShape
                                    cutterList.extend(simulatedPl)

                            else:
                                # print 'b12'
                                simulatedPl = pyAli.simulatedShape
                                cutterList.extend(simulatedPl)

        if cutterList:
            plane = self.shape
            plane = plane.cut(cutterList, tolerance)
            gS = self.geom.toShape()
            plane = selectFace(plane.Faces, gS, tolerance)
            self.shape = plane

    def isSolved(self, face, pyFace, pyOppReflex, tolerance):

        ''''''

        numWire = self.numWire

        print '###### isSolved ', (numWire, self.numGeom)

        forward = self.forward
        backward = self.backward

        plane = self.shape

        section = plane.section([backward], tolerance)
        if section.Edges:
            self.addValue('problem', 'backward', 'forward')

        section = plane.section([forward], tolerance)
        if section.Edges:
            self.addValue('problem', 'forward', 'backward')
