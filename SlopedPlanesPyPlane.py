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
import Part
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
        self.geomShape = None
        self.geomAligned = None
        self.shape = None
        self.bigShape = None
        self.enormousShape = None
        self.simulatedShape = None
        self.cutter = []
        self.oppCutter = []
        self.divide = []
        self.compound = None
        self.forward = None
        self.backward = None
        self.unsolved = []

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
    def geomShape(self):

        ''''''

        return self._geomShape

    @geomShape.setter
    def geomShape(self, geomShape):

        ''''''

        self._geomShape = geomShape

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
    def simulatedShape(self):

        ''''''

        return self._simulatedShape

    @simulatedShape.setter
    def simulatedShape(self, simulatedShape):

        ''''''

        self._simulatedShape = simulatedShape

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
    def divide(self):

        ''''''

        return self._divide

    @divide.setter
    def divide(self, divide):

        ''''''

        self._divide = divide

    @property
    def compound(self):

        ''''''

        return self._compound

    @compound.setter
    def compound(self, compound):

        ''''''

        self._compound = compound

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
    def unsolved(self):

        ''''''

        return self._unsolved

    @unsolved.setter
    def unsolved(self, unsolved):

        ''''''

        self._unsolved = unsolved

    def planning(self, pyWire):

        ''''''

        coordinates = pyWire.coordinates
        numGeom = self.numGeom
        geom = self.geomAligned
        eje = coordinates[numGeom+1].sub(coordinates[numGeom])
        direction = self.rotateVector(eje, _Py.normal, 90)
        angle = self.angle
        if _Py.reverse:
            angle = angle * -1
        direction = self.rotateVector(direction, eje, angle)
        direction.normalize()

        firstParam = geom.FirstParameter
        lastParam = geom.LastParameter

        scale = 1
        plane =\
            self.doPlane(direction, geom, firstParam,
                         lastParam, scale)
        self.shape = plane

        scale = 10
        bigPlane =\
            self.doPlane(direction, geom, firstParam,
                         lastParam, scale)
        self.bigShape = bigPlane

        if self.reflexed:

            scale = 100
            enormousPlane =\
                self.doPlane(direction, geom, firstParam,
                             lastParam, scale)
            self.enormousShape = enormousPlane

            self.simulatedShape = None
            self.divide = []
            self.compound = None

    def doPlane(self, direction, geom, firstParam, lastParam, scale):

        ''''''

        leftScale = self.width[0] * scale
        rightScale = self.width[1] * scale
        upScale = self.length * scale

        if isinstance(geom, (Part.LineSegment,
                             Part.ArcOfParabola)):
            startParam = firstParam - leftScale * _Py.size
            endParam = lastParam + rightScale * _Py.size

        elif isinstance(geom, (Part.ArcOfCircle,
                               Part.ArcOfEllipse)):
            startParam = (2 * pi - (lastParam - firstParam)) / 2 + lastParam
            endParam = startParam + 2 * pi

        elif isinstance(geom, Part.ArcOfHyperbola):
            pass

        elif isinstance(geom, Part.BSplineCurve):
            pass

        else:
            pass

        extendGeom = self.makeGeom(geom, startParam, endParam)
        plane = extendGeom.toShape().extrude(direction*upScale*_Py.size)

        return plane

    def trimming(self, enormousShape, enormShape=None):

        ''''''

        shape = self.shape
        bigShape = self.bigShape
        gS = self.geomShape

        if enormShape:
            cutterList = enormShape
        else:
            cutterList = [enormousShape]

        shape = self.cutting(shape, cutterList, gS)
        self.shape = shape

        bigShape = self.cutting(bigShape, [enormousShape], gS)
        self.bigShape = bigShape

    def simulating(self, enormousShape):

        ''''''

        try:
            plCopy = self.simulatedShape.copy()
        except AttributeError:
            plCopy = self.shape.copy()

        gS = self.geomShape
        plCopy = self.cutting(plCopy, [enormousShape], gS)
        self.simulatedShape = plCopy

    def virtualizing(self):

        ''''''

        if self.aligned:

            [numWire, numGeom] = [self.numWire, self.numGeom]
            plane = self.shape
            big = self.bigShape
            enormous = self.enormousShape
            geom = self.geom
            geomShape = self.geomShape
            forward = self.forward
            backward = self.backward
            rear = self.rear
            rango = self.rango

            if not plane:
                (nWire, nGeom) = self.angle
                pyPlane = self.selectPlane(nWire, nGeom)
                plane = pyPlane.shape
                big = pyPlane.bigShape
                enormous = pyPlane.enormousShape

            pyPlane = _PyPlane(numWire, numGeom)
            pyPlane.geomShape = geomShape
            pyPlane.geom = geom
            pyPlane.forward = forward
            pyPlane.backward = backward
            pyPlane.rear = rear
            pyPlane.rango = rango
            pyPlane.aligned = True
            pyPlane.reflexed = True
            pyPlane.shape = plane.copy()
            pyPlane.bigShape = big
            pyPlane.enormousShape = enormous
            pyPlane.angle = self.angle

            return pyPlane

        else:

            return self

    def ordinaries(self, pyWire):

        ''''''

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

                            pyAli =\
                                self.selectAlignment(pyPl.numWire,
                                                     pyPl.numGeom)

                            if self.aligned:
                                # print 'b11'

                                pyAlign =\
                                    self.selectAlignment(self.numWire,
                                                         self.numGeom)

                                if pyAli.base.angle == [pyAlign.base.numWire,
                                                        pyAlign.base.numGeom]:
                                    pass

                                else:

                                    ch = []
                                    for [ch1, ch2] in pyAli.chops:
                                        ch.append((ch1.numWire, ch1.numGeom))
                                        ch.append((ch2.numWire, ch2.numGeom))
    
                                    ali = []
                                    for align in pyAli.aligns:
                                        ali.append((align.numWire, align.numGeom))
    
                                    pl = (pyPl.numWire, pyPl.numGeom)
    
                                    for [pyOne, pyTwo] in pyAlign.chops:
                                        chop = [(pyOne.numWire, pyOne.numGeom),
                                                (pyTwo.numWire, pyTwo.numGeom)]
    
                                        if pl in chop:
                                            break

                                        elif (self.numWire, self.numGeom) in ali:
                                            break       # subir

                                        elif chop[0] in ali or chop[1] in ali:
                                            break
                                        elif chop[0] in ch or chop[1] in ch:
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
            gS = self.geomShape
            plane = self.cutting(plane, cutterList, gS)
            self.shape = plane

    def isUnsolved(self):

        ''''''

        self.unsolved = []

        if self.aligned:
            self.unsolved = []
            return []

        forward = self.forward
        backward = self.backward
        plane = self.shape

        section = plane.section([forward], _Py.tolerance)
        if section.Edges:
            self.addValue('unsolved', 'forward', 'forward')
        section = plane.section([backward], _Py.tolerance)
        if section.Edges:
            self.addValue('unsolved', 'backward', 'backward')

        return self.unsolved

    def rearing(self, pyWire, pyReflex):

        ''''''

        # print 'numGeom ', self.numGeom

        rear = self.rear

        # print 'rear ', rear

        plane = self.shape
        pyPlaneList = pyWire.planes

        twinReflex = pyReflex.planes
        ind = twinReflex.index(self)
        if ind == 0:
            pyOppPlane = twinReflex[1]
        else:
            pyOppPlane = twinReflex[0]
        oppPlane = pyOppPlane.shape

        # print 'numGeom ', pyOppPlane.numGeom

        if self.choped:
            if pyOppPlane.aligned:
                # print 'a'
                rear = [rear[1]]
            else:
                # print 'b'
                rear = [rear[0]]

        for numG in rear:
            pyPl = pyPlaneList[numG]
            if not (pyPl.aligned or pyPl.choped):
                pl = pyPl.shape
                if isinstance(pl, Part.Compound):
                    # TODO necesita un nivel mas de seleccion
                    pass
                else:
                    gS = pyPl.geomShape
                    pl = self.cutting(pl, [plane, oppPlane], gS)
                    pyPl.shape = pl

    def rangging(self, pyWire, direction):

        ''''''

        numGeom = self.numGeom

        rear = self.rear
        lenWire = len(pyWire.planes)
        lenRear = len(rear)

        rango = []

        if lenRear == 1:

            [nGeom] = rear

            if nGeom > numGeom:

                if direction == "forward":
                    num = self.sliceIndex(numGeom+2, lenWire)
                    ran = range(num, nGeom)

                else:
                    ranA = range(nGeom+1, lenWire)
                    ranA.reverse()
                    ranB = range(0, numGeom-1)
                    ranB.reverse()
                    ran = ranB + ranA

            else:

                if direction == "forward":
                    ran = range(numGeom+2, lenWire) +\
                        range(0, nGeom)

                else:
                    ran = range(nGeom+1, numGeom-1)

            rango.append(ran)

        elif lenRear == 2:
            [nGeom1, nGeom2] = rear

            number = -1
            for nG in rear:
                number += 1

                if number == 0:

                    if numGeom < nG:
                        ran = range(numGeom+2, nG)

                    else:
                        ranA = range(numGeom+2, lenWire)
                        ranB = range(0, nG)
                        ran = ranA + ranB

                else:

                    if numGeom < nG:
                        ranA = range(nG+1, lenWire)
                        ranB = range(0, numGeom-1)
                        ran = ranA + ranB

                    else:
                        ran = range(nG+1, numGeom-1)

                rango.append(ran)

        self.rango = rango
