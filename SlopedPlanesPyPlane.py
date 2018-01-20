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
__version__ = ""


class _PyPlane(_Py):

    '''The complementary python object class for planes.'''

    def __init__(self, numWire, numGeom):

        ''''''

        self.numWire = numWire
        self.numGeom = numGeom
        self.angle = 45.0
        size = _Py.size
        self.rightWidth = size
        self.leftWidth = size
        self.length = 2 * size
        self.overhang = 0
        self.rear = []
        self.rango = []
        self.rangoConsolidate = []
        self.reflexed = False
        self.aligned = False
        self.choped = False
        self.fronted = False
        self.arrow = False
        self.geom = None
        self.geomShape = None
        self.geomAligned = None
        self.shape = None
        self.bigShape = None
        self.enormousShape = None
        self.simulatedShape = None
        self.cutter = []
        self.forward = None
        self.backward = None
        self.virtualized = False
        self.control = [numGeom]
        self.seedShape = None
        self.seedBigShape = None
        self.bigScale = 100
        self.enormousScale = 10000

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

        try:
            oldAngle = self.angle
            if oldAngle != angle:
                self.seedShape = None
        except AttributeError:
            pass

        self._angle = angle

    @property
    def rightWidth(self):

        ''''''

        return self._rightWidth

    @rightWidth.setter
    def rightWidth(self, width):

        ''''''

        try:
            oldWidth = self.rightWidth
            if oldWidth != width:
                self.seedShape = None
        except AttributeError:
            pass

        self._rightWidth = width

    @property
    def leftWidth(self):

        ''''''

        return self._leftWidth

    @leftWidth.setter
    def leftWidth(self, width):

        ''''''

        try:
            oldWidth = self.leftWidth
            if oldWidth != width:
                self.seedShape = None
        except AttributeError:
            pass

        self._leftWidth = width

    @property
    def length(self):

        ''''''

        return self._length

    @length.setter
    def length(self, length):

        ''''''

        try:
            oldLength = self.length
            if oldLength != length:
                self.seedShape = None
        except AttributeError:
            pass

        self._length = length

    @property
    def overhang(self):

        ''''''

        return self._overhang

    @overhang.setter
    def overhang(self, overhang):

        ''''''

        try:
            oldOverhang = self.overhang
            if oldOverhang != overhang:
                self.seedShape = None
        except AttributeError:
            pass

        self._overhang = overhang

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
    def rangoConsolidate(self):

        ''''''

        return self._rangoConsolidate

    @rangoConsolidate.setter
    def rangoConsolidate(self, rangoConsolidate):

        ''''''

        self._rangoConsolidate = rangoConsolidate

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
    def fronted(self):

        ''''''

        return self._fronted

    @fronted.setter
    def fronted(self, fronted):

        ''''''

        self._fronted = fronted

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
    def virtualized(self):

        ''''''

        return self._virtualized

    @virtualized.setter
    def virtualized(self, virtualized):

        ''''''

        self._virtualized = virtualized

    @property
    def control(self):

        ''''''

        return self._control

    @control.setter
    def control(self, control):

        ''''''

        self._control = control

    @property
    def seedShape(self):

        ''''''

        return self._seedShape

    @seedShape.setter
    def seedShape(self, seedShape):

        ''''''

        self._seedShape = seedShape

    @property
    def seedBigShape(self):

        ''''''

        return self._seedBigShape

    @seedBigShape.setter
    def seedBigShape(self, seedBigShape):

        ''''''

        self._seedBigShape = seedBigShape

    @property
    def bigScale(self):

        ''''''

        return self._bigScale

    @bigScale.setter
    def bigScale(self, bigScale):

        ''''''

        try:
            oldScale = self.bigScale
            if oldScale != bigScale:
                self.seedShape = None
        except AttributeError:
            pass

        self._bigScale = bigScale

    @property
    def enormousScale(self):

        ''''''

        return self._enormousScale

    @enormousScale.setter
    def enormousScale(self, enormousScale):

        ''''''

        try:
            oldScale = self.enormousScale
            if oldScale != enormousScale:
                self.seedShape = None
        except AttributeError:
            pass

        self._enormousScale = enormousScale

    def planning(self, pyWire):

        '''planning(self, pyWire)
        '''

        numGeom = self.numGeom
        # print '# planning ', numGeom

        if self.seedShape:
            # print 'seed'

            self.shape = self.seedShape.copy()
            self.bigShape = self.seedBigShape.copy()

        else:
            # print 'no seed'

            coordinates = pyWire.coordinates
            geom = self.deGeom()
            eje = coordinates[numGeom+1].sub(coordinates[numGeom])
            direction = self.rotateVector(eje, _Py.normal, 90)
            angle = self.angle
            if _Py.reverse:
                angle = angle * -1
            direction = self.rotateVector(direction, eje, angle)
            direction.normalize()

            firstParam = geom.FirstParameter
            lastParam = geom.LastParameter

            geomCopy = geom.copy()
            geomCopy.translate(-1*self.overhang*direction)

            # print '# normal'
            scale = 1
            plane =\
                self.doPlane(direction, geomCopy, firstParam,
                             lastParam, scale)
            self.shape = plane
            self.seedShape = plane.copy()

            geomCopy = geom.copy()
            geomCopy.translate(-1*_Py.size*direction)

            # print '# big'
            scale = self.bigScale
            bigPlane =\
                self.doPlane(direction, geomCopy, firstParam,
                             lastParam, scale)
            self.bigShape = bigPlane
            self.seedBigShape = bigPlane.copy()

            if self.reflexed:

                # print '# enormous'
                scale = self.enormousScale
                enormousPlane =\
                    self.doPlane(direction, geomCopy, firstParam,
                                 lastParam, scale)
                self.enormousShape = enormousPlane

        if self.reflexed:
            self.simulatedShape = None
            self.cutter = []

    def doPlane(self, direction, geom, firstParam, lastParam, scale):

        '''doPlane(self, direction, geom, firstParam, lastParam, scale)
        '''

        # print 'scale ', scale

        size = _Py.size
        width = size
        length = 2 * size

        # print 'size ', size
        # print 'width ', width
        # print 'length ', length

        leftScale = self.leftWidth * scale
        rightScale = self.rightWidth * scale
        upScale = self.length * scale

        # print 'leftScale ', leftScale
        # print 'rightScale ', rightScale
        # print 'upScale ', upScale

        if not upScale:
            # print 'up'
            upScale = 2 * size * scale

        if scale > 1:

            if self.leftWidth < width:
                # print 'left'
                leftScale = width * scale

            if self.rightWidth < width:
                # print 'right'
                rightScale = width * scale

            if self.length < length:
                # print 'length'
                upScale = length * scale

        # print 'leftScale ', leftScale
        # print 'rightScale ', rightScale
        # print 'upScale ', upScale

        if isinstance(geom, (Part.LineSegment,
                             Part.ArcOfParabola)):
            startParam = firstParam - leftScale
            endParam = lastParam + rightScale

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
        # print 'extendGeom ', extendGeom
        plane = extendGeom.toShape().extrude(direction*upScale)

        return plane

    def virtualizing(self):

        '''virtualizing(self)
        '''

        if self.aligned:

            # TODO copying dict

            [numWire, numGeom] = [self.numWire, self.numGeom]
            plane = self.shape
            big = self.bigShape
            enormous = self.enormousShape
            simulated = self.simulatedShape
            geom = self.geom
            geomAligned = self.geomAligned
            geomShape = self.geomShape
            forward = self.forward
            backward = self.backward
            rear = self.rear
            rango = self.rango
            rangoConsolidate = self.rangoConsolidate
            angle = self.angle
            fronted = self.fronted

            if not plane:
                (nWire, nGeom) = angle
                pyPlane = self.selectPlane(nWire, nGeom)
                plane = pyPlane.shape
                big = pyPlane.bigShape
                enormous = pyPlane.enormousShape
                simulated = pyPlane.simulatedShape
                angle = pyPlane.angle

            pyPlane = _PyPlane(numWire, numGeom)
            pyPlane.geomShape = geomShape
            pyPlane.geom = geom
            pyPlane.geomAligned = geomAligned
            pyPlane.forward = forward
            pyPlane.backward = backward
            pyPlane.rear = rear
            pyPlane.rango = rango
            pyPlane.rangoConsolidate = rangoConsolidate
            pyPlane.aligned = True
            pyPlane.reflexed = True
            pyPlane.fronted = fronted
            pyPlane.shape = plane.copy()
            pyPlane.bigShape = big
            pyPlane.enormousShape = enormous
            pyPlane.simulatedShape = simulated
            pyPlane.angle = angle
            pyPlane.virtualized = True

            return pyPlane

        else:

            return self

    def trimming(self, enormousShape, enormShape=None):

        '''trimming(self, enormousShape, enormShape=None)
        '''

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

    def trimmingTwo(self, enormousShape):

        '''trimmingTwo(self, enormousShape)
        '''

        self.simulating(enormousShape)

        bigShape = self.bigShape
        gS = self.geomShape
        bigShape = self.cutting(bigShape, [enormousShape], gS)
        self.bigShape = bigShape

    def simulating(self, cList):

        '''simulating(self, enormousShape)
        '''

        # print '# simulating ', self.numGeom

        try:
            plCopy = self.simulatedShape.copy()
            # print 'a'
        except AttributeError:
            # print 'b'
            plCopy = self.shape.copy()

        gS = self.geomShape
        plCopy = self.cutting(plCopy, cList, gS)
        self.simulatedShape = plCopy

    def rearing(self, pyWire, pyReflex, direction, case):

        '''rearing(self, pyWire, pyReflex)
        '''

        # print '# rearing ', (self.numWire, self.numGeom)

        tolerance = _Py.tolerance
        plane = self.shape
        forward = self.forward

        fo = False
        if plane.section([forward], tolerance).Edges:
            # print 'fo'
            fo = True

        pyPlaneList = pyWire.planes

        if direction == "forward":
            pyOppPlane = pyReflex.planes[1]
        else:
            pyOppPlane = pyReflex.planes[0]
        oppPlane = pyOppPlane.shape
        # print 'pyOppPlane.numGeom ', pyOppPlane.numGeom

        rear = self.rear
        if self.choped:
            if pyOppPlane.aligned:
                # print 'a'
                rear = [rear[1]]
            else:
                # print 'b'
                rear = [rear[0]]
        # print 'rear ', rear

        for numG in rear:

            pyPl = pyPlaneList[numG]

            if not pyPl.aligned:

                gS = pyPl.geomShape
                pl = pyPl.shape
                forw = pyPl.forward
                control = pyPl.control

                if case:
                    condition = not (pyPl.aligned or pyPl.choped)

                else:
                    condition = (pyPl.reflexed and not pyPl.aligned and not pyPl.choped)

                if condition:
                    # print 'numG ', numG

                    if not fo:
                        # print 'no fo'

                        cList = []
                        if self.numGeom not in control:
                            cList.append(plane)
                            # print 'included ', self.numGeom
                            control.append(self.numGeom)

                        if pyOppPlane.numGeom not in control:
                            cList.append(oppPlane)
                            # print 'included ', pyOppPlane.numGeom
                            control.append(pyOppPlane.numGeom)

                        if cList:
                            # print 'cList ', cList

                            if isinstance(pl, Part.Compound):
                                # print 'aa'

                                if len(pl.Faces) > 1:
                                    # print 'aa1'

                                    aList = []
                                    for ff in pl.Faces:
                                        section = ff.section([gS], tolerance)
                                        ff = ff.cut(cList, tolerance)
                                        if section.Edges:
                                            # print 'aa11'
                                            ff = self.selectFace(ff.Faces, gS)
                                            aList.append(ff)
                                        else:
                                            # print 'aa12'
                                            aList.append(ff.Faces[0])

                                    compound = Part.Compound(aList)
                                    pyPl.shape = compound

                                else:
                                    # print 'aa2'
                                    pl = self.cutting(pl, cList, gS)
                                    compound = Part.Compound([pl])
                                    pyPl.shape = compound

                            else:
                                # print 'bb'
                                pl = self.cutting(pl, cList, gS)
                                pyPl.shape = pl

                            if len(plane.Faces) == 1:
                                # print 'AA'

                                gS = self.geomShape
                                plane = self.cutting(plane, [pl], gS)
                                compound = Part.Compound([plane])
                                self.shape = compound
                                self.control.append(numG)

                            if len(oppPlane.Faces) == 1:
                                # print 'BB'

                                gS = pyOppPlane.geomShape
                                oppPlane = self.cutting(oppPlane, [pl], gS)
                                compound = Part.Compound([oppPlane])
                                pyOppPlane.shape = compound
                                pyOppPlane.control.append(numG)

                    else:
                        # print 'fo'
                        if pyPl.reflexed:
                            # print 'fo1'
                            if not pl.section([forw], tolerance).Edges:
                                # print 'fo11'
                                gS = self.geomShape
                                plane = self.cutting(plane, [pl], gS)
                                compound = Part.Compound([plane])
                                self.shape = compound
                                self.control.append(numG)
                        else:
                            # print 'fo2'
                            # if not self.choped:
                            if not self.choped and not self.aligned:
                                # print 'fo21'
                                gS = self.geomShape
                                enormous = pyOppPlane.enormousShape  # MUCHO OJO
                                plane = self.cutting(plane, [enormous], gS)
                                compound = Part.Compound([plane])
                                self.shape = compound

    def ordinaries(self, pyWire):

        '''ordinaries(self, pyWire)
        '''

        pyPlaneList = pyWire.planes
        numWire = pyWire.numWire
        control = self.control

        if self.aligned:
            # print 'aligned'

            pyAlign = self.selectAlignment(numWire, self.numGeom)
            # print 'pyAlign ', (pyAlign.base.numWire, pyAlign.base.numGeom)
            line = pyAlign.geomAligned

        cutterList = []
        for pyPl in pyPlaneList:
            nGeom = pyPl.numGeom
            if nGeom not in control:
                pl = pyPl.shape
                if pl:
                    # print '### numGeom ', pyPl.numGeom

                    if pyPl.aligned:
                        # print 'a'

                        pyAli = self.selectAlignment(numWire, nGeom)
                        # print 'pyAli ', (pyAli.base.numWire, pyAli.base.numGeom)
                        ll = pyAli.geomAligned

                        if self.aligned:
                            # print 'a1'
                            section = line.section([ll], _Py.tolerance)
                            if not section.Vertexes:
                                # TODO dos alineaciones en esquina ?
                                cutterList.extend(pyAli.simulatedAlignment)

                        else:
                            # print 'a2'
                            cutterList.extend(pyAli.simulatedAlignment)

                    elif pyPl.choped:
                        # print 'b'
                        pass

                    else:
                        # print 'c'
                        cutterList.append(pl)
                        control.append(pyPl.numGeom)

        if cutterList:
            # print 'cutterList ', cutterList
            plane = self.shape
            gS = self.geomShape
            plane = self.cutting(plane, cutterList, gS)
            self.shape = plane
            # print 'plane ', plane

    def rangging(self, pyWire, direction):

        '''rangging(self, pyWire, direction)
        '''

        numGeom = self.numGeom

        rear = self.rear
        lenWire = len(pyWire.planes)
        lenRear = len(rear)

        rango = []
        rangoConsolidate = []

        if lenRear == 0:

            rango = [[]]

        elif lenRear == 1:

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
            rangoConsolidate.extend(ran)

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
                rangoConsolidate.extend(ran)

        self.rango = rango
        self.rangoConsolidate = rangoConsolidate
