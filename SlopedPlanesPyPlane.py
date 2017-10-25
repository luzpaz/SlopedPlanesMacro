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
import SlopedPlanesUtils as utils
from SlopedPlanesPy import _Py


__title__ = "SlopedPlanes Macro"
__author__ = "Damian Caceres Moreno"
__url__ = "http://www.freecadweb.org"


class _PyPlane(_Py):

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
        self.solved = False

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
    def solved(self):

        ''''''

        return self._solved

    @solved.setter
    def solved(self, solved):

        ''''''

        self._solved = solved

    def trackShape(self, pyWire, normal, size, reverse):

        ''''''

        coordinates = pyWire.coordinates
        numGeom = self.numGeom
        geom = self.geomAligned
        eje = coordinates[numGeom+1].sub(coordinates[numGeom])
        direction = utils.rotateVector(eje, normal, 90)
        angle = self.angle
        if reverse:
            angle = angle * -1
        direction = utils.rotateVector(direction, eje, angle)
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
            plane = utils.selectFace(plane.Faces, gS, tolerance)
            self.shape = plane

    def isSolved(self, tolerance):

        ''''''

        print '# isSolved'

        forward = self.forward
        plane = self.shape

        section = plane.section([forward], tolerance)
        if not section.Edges:
            print 'True'
            self.solved = True
            return True
        else:
            print 'False'
            self.solved = False
            return False

    def rangging(self, pyWire, direction):

        ''''''

        print '### rangging'

        numGeom = self.numGeom
        print '# numGeom ', numGeom

        rear = self.rear
        lenWire = len(pyWire.planes)
        lenRear = len(rear)
        print '# rear ', rear

        rango = []

        if lenRear == 1:
            print '1'
            [nGeom] = rear

            if nGeom > numGeom:
                print '11'

                if direction == "forward":
                    print '111'
                    num = utils.sliceIndex(numGeom+2, lenWire)
                    ran = range(num, nGeom)

                else:
                    print '112'
                    ranA = range(nGeom+1, lenWire)
                    ranA.reverse()
                    ranB = range(0, numGeom-1)
                    ranB.reverse()
                    ran = ranB + ranA

            else:
                print '12'

                if direction == "forward":
                    print '121'
                    ran = range(numGeom+2, lenWire) +\
                        range(0, nGeom)

                else:
                    print '122'
                    ran = range(nGeom+1, numGeom-1)

            rango.append(ran)

        elif lenRear == 2:
            print '2'
            [nGeom1, nGeom2] = rear

            number = -1
            for nG in rear:
                number += 1

                if number == 0:
                    print '21'

                    if numGeom < nG:
                        print '211'
                        ran = range(numGeom+2, nG)

                    else:
                        print '212'
                        ranA = range(numGeom+2, lenWire)
                        ranB = range(0, nG)
                        ran = ranA + ranB

                else:
                    print '22'

                    if numGeom < nG:
                        print '221'
                        ranA = range(nG+1, lenWire)
                        ranB = range(0, numGeom-1)
                        ran = ranA + ranB

                    else:
                        print '222'
                        ran = range(nG+1, numGeom-1)

                rango.append(ran)

        print 'rango ', rango
        self.rango = rango

    def doTrim(self, enormousShape, tolerance):

        ''''''

        shape = self.shape
        bigShape = self.bigShape
        geomShape = self.geom.toShape()

        shape = shape.cut([enormousShape], tolerance)
        shape = utils.selectFace(shape.Faces, geomShape, tolerance)
        self.shape = shape

        bigShape =\
            bigShape.cut([enormousShape], tolerance)
        bigShape =\
            utils.selectFace(bigShape.Faces, geomShape, tolerance)
        self.bigShape = bigShape

    def solveRear(self, pyWire, pyReflex, tolerance):

        ''''''

        rear = self.rear

        print '###### solveRear', rear

        plane = self.shape
        pyPlaneList = pyWire.planes

        twinReflex = pyReflex.planes
        ind = twinReflex.index(self)
        if ind == 0:
            pyOppPlane = twinReflex[1]
        else:
            pyOppPlane = twinReflex[0]
        oppPlane = pyOppPlane.shape

        for numG in rear:
            pyPl = pyPlaneList[numG]
            if not (pyPl.aligned or pyPl.choped):
                pl = pyPl.shape
                pl = pl.cut([plane, oppPlane], tolerance)
                gS = pyPl.geom.toShape()
                pl = utils.selectFace(pl.Faces, gS, tolerance)
                pyPl.shape = pl
