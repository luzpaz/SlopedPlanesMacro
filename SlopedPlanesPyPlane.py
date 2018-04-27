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


from math import pi, degrees, radians, tan, sqrt
import FreeCAD
import Part
from SlopedPlanesPy import _Py


__title__ = "SlopedPlanes Macro"
__author__ = "Damian Caceres Moreno"
__url__ = "http://www.freecadweb.org"
__version__ = ""


class _PyPlane(_Py):

    '''The complementary python object class for planes.A plane correspond
    to one or more edges of the base. A plane could have several faces.'''

    def __init__(self, numWire, numGeom):

        ''''''

        self.alignedList = []
        self.chopedList = []
        self.frontedList = []
        self.rearedList = []
        self.reflexedList = []

        self.numWire = numWire
        self.numGeom = numGeom
        self.angle = 45.0
        size = _Py.size
        self.rightWidth = size
        self.leftWidth = size
        self.length = 2 * size
        self.overhang = 0
        self.rear = []
        self.secondRear = []
        self.under = []
        self.seed = []
        self.rango = []
        self.rangoPy = []   # TODO unir rangos
        self.reflexed = False
        self.aligned = False  # quitar
        self.choped = False  # quitar
        self.fronted = False  # quitar
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
        self.virtuals = []
        self.control = [numGeom]
        self.seedShape = None
        self.seedBigShape = None
        self.lineInto = None
        self.cross = False
        self.solved = False
        self.reallySolved = False
        self.sweepCurve = None

    @property
    def alignedList(self):

        ''''''

        return self._alignedList

    @alignedList.setter
    def alignedList(self, alignedList):

        ''''''

        self._alignedList = alignedList

    @property
    def chopedList(self):

        ''''''

        return self._chopedList

    @chopedList.setter
    def chopedList(self, chopedList):

        ''''''

        self._chopedList = chopedList

    @property
    def frontedList(self):

        ''''''

        return self._frontedList

    @frontedList.setter
    def frontedList(self, frontedList):

        ''''''

        self._frontedList = frontedList

    @property
    def rearedList(self):

        ''''''

        return self._rearedList

    @rearedList.setter
    def rearedList(self, rearedList):

        ''''''

        self._rearedList = rearedList

    @property
    def reflexedList(self):

        ''''''

        return self._reflexedList

    @reflexedList.setter
    def reflexedList(self, reflexedList):

        ''''''

        self._reflexedList = reflexedList

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

        size = _Py.size
        if overhang > size:
            overhang = size

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
    def secondRear(self):

        ''''''

        return self._secondRear

    @secondRear.setter
    def secondRear(self, secondRear):

        ''''''

        self._secondRear = secondRear

    @property
    def under(self):

        ''''''

        return self._under

    @under.setter
    def under(self, under):

        ''''''

        self._under = under

    @property
    def seed(self):

        '''used in PyReflex, allowed location for a second face'''

        return self._seed

    @seed.setter
    def seed(self, seed):

        ''''''

        self._seed = seed

    @property
    def rango(self):

        ''''''

        return self._rango

    @rango.setter
    def rango(self, rango):

        ''''''

        self._rango = rango

    @property
    def rangoPy(self):

        ''''''

        return self._rangoPy

    @rangoPy.setter
    def rangoPy(self, rangoPy):

        ''''''

        self._rangoPy = rangoPy

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
    def virtuals(self):

        ''''''

        return self._virtuals

    @virtuals.setter
    def virtuals(self, virtuals):

        '''virtuals(self, virtuals)
        _Py.printAsociatedShapes'''

        self._virtuals = virtuals

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
    def lineInto(self):

        ''''''

        return self._lineInto

    @lineInto.setter
    def lineInto(self, lineInto):

        ''''''

        self._lineInto = lineInto

    @property
    def cross(self):

        ''''''

        return self._cross

    @cross.setter
    def cross(self, cross):

        ''''''

        self._cross = cross

    @property
    def solved(self):

        ''''''

        return self._solved

    @solved.setter
    def solved(self, solved):

        ''''''

        self._solved = solved

    @property
    def reallySolved(self):

        ''''''

        return self._reallySolved

    @reallySolved.setter
    def reallySolved(self, reallySolved):

        ''''''

        self._reallySolved = reallySolved

    @property
    def sweepCurve(self):

        ''''''

        return self._sweepCurve

    @sweepCurve.setter
    def sweepCurve(self, sweepCurve):

        ''''''

        try:
            oldCurve = self.sweepCurve
            if oldCurve != sweepCurve:
                self.seedShape = None
        except AttributeError:
            pass

        self._sweepCurve = sweepCurve

    def planning(self, pyWire, closed=False):

        '''planning(self, pyWire, closed=False)
        '''

        numGeom = self.numGeom
        # print '### planning ', numGeom

        if self.reflexed:
            # print 'reflexed'
            self.simulatedShape = None
            self.cutter = []
            self.under = []
            self.seed = []
            self.virtuals = []
            self.virtualized = False

        if not self.geomAligned:
            return

        if self.seedShape:
            # print '### seed'

            self.shape = self.seedShape.copy()
            self.bigShape = self.seedBigShape.copy()

        else:
            # print '### no seed'

            if closed:
                geom = self.makeGeom(self.geomShape.Curve, 0, 2 * pi)
                angle = self.angle
                radius = geom.Radius
                height = radius * tan(radians(angle))
                pointA = self.geomShape.Vertexes[0].Point
                pointB = geom.Location + FreeCAD.Vector(0, 0, height)
                direction = pointB.sub(pointA)
                direction.normalize()

            else:
                direction, geom = self.direction(pyWire, numGeom)

            # print 'geom ', geom
            # print 'direction ', direction

            firstParam = geom.FirstParameter
            lastParam = geom.LastParameter

            geomCopy = geom.copy()
            if not (self.sweepCurve or closed):
                geomCopy.translate(-1 * self.overhang * direction)

            # print '# normal'
            scale = 1
            plane =\
                self.doPlane(direction, geomCopy, firstParam,
                             lastParam, scale, closed)
            self.shape = plane
            self.seedShape = plane.copy()

            geomCopy = geom.copy()
            if not (self.sweepCurve or closed):
                geomCopy.translate(-1 * _Py.size * direction)

            # print '# big'
            scale = 5
            bigPlane =\
                self.doPlane(direction, geomCopy, firstParam,
                             lastParam, scale, closed)
            self.bigShape = bigPlane
            self.seedBigShape = bigPlane.copy()

            if self.reflexed:

                # print '# enormous'
                scale = 50
                enormousPlane =\
                    self.doPlane(direction, geomCopy, firstParam,
                                 lastParam, scale, closed)
                self.enormousShape = enormousPlane

    def direction(self, pyWire, numGeom):

        '''direction(self, pyWire, numGeom)'''

        coordinates = pyWire.coordinates

        geom = self.doGeom()

        eje = coordinates[numGeom + 1].sub(coordinates[numGeom])
        direction = self.rotateVector(eje, _Py.normal, 90)
        angle = self.angle
        if _Py.reverse:
            angle = angle * -1
        direction = self.rotateVector(direction, eje, angle)
        direction.normalize()

        return direction, geom

    def doPlane(self, direction, geom, firstParam, lastParam, scale, closed):

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
                             Part.ArcOfParabola,
                             Part.ArcOfHyperbola)):
            # print 'a'

            startParam = firstParam - leftScale
            endParam = lastParam + rightScale

        elif isinstance(geom, (Part.ArcOfCircle,
                               Part.ArcOfEllipse)):
            # print 'b'

            startParam = (2 * pi - (lastParam - firstParam)) / 2 + lastParam
            endParam = startParam + 2 * pi

        elif isinstance(geom, (Part.Circle, Part.Ellipse)):

            startParam = 0
            endParam = 2 * pi

        elif isinstance(geom, Part.BSplineCurve):

            pass

        # print 'startParam ', startParam
        # print 'endParam ', endParam

        extendGeom = self.makeGeom(geom, startParam, endParam)
        # print 'extendGeom ', extendGeom
        # TODO problem with ArcOfHiperbola
        extendShape = extendGeom.toShape()

        if self.sweepCurve:
            # print 'A'

            sweepSketch = FreeCAD.ActiveDocument.getObject(self.sweepCurve)
            wire = sweepSketch.Shape.copy()

            wire.Placement = FreeCAD.Placement()

            try:
                constraint = degrees(sweepSketch.Constraints[3].Value)
            except IndexError:
                constraint = 45

            angleConstraint = constraint
            angle = self.angle
            ang = angle - angleConstraint
            wire.rotate(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 0, 1), ang)

            geomShape = self.geomShape
            ffPoint = geomShape.firstVertex(True).Point
            llPoint = geomShape.lastVertex(True).Point
            direct = llPoint.sub(ffPoint)
            aa = direct.getAngle(FreeCAD.Vector(1, 0, 0)) + pi / 2
            if ffPoint.y > llPoint.y:
                aa = aa + pi

            rotation = FreeCAD.Rotation()
            rotation.Axis = FreeCAD.Vector(1, 0, 0)
            rotation.Angle = pi / 2
            wire.Placement.Rotation =\
                rotation.multiply(wire.Placement.Rotation)

            rotation = FreeCAD.Rotation()
            rotation.Axis = _Py.normal
            rotation.Angle = aa
            wire.Placement.Rotation =\
                rotation.multiply(wire.Placement.Rotation)

            wire.Placement.Base = ffPoint

            extendShape = Part.Wire(extendShape)
            plane = wire.makePipeShell([extendShape])

        else:
            # print 'B'

            if closed:

                point = geom.Location
                angle = self.angle
                radius = geom.Radius
                height = radius * tan(radians(angle))
                length = sqrt(radius ** 2 + height ** 2)
                pointA = self.geomShape.Vertexes[0].Point
                pointB = geom.Location + FreeCAD.Vector(0, 0, height)
                revolCurve = Part.makeLine(pointA, pointB)

                plane = Part.makeRevolution(revolCurve, 0, length, 360, point,
                                            FreeCAD.Vector(0, 0, 1),).Faces[0]

                # TODO para la ellipse hacerlo con sweep ??
                # y los angulos igual o mayor que 90 ??

            else:
                plane = extendShape.extrude(direction * upScale)

        return plane

    def virtualizing(self):

        '''virtualizing(self)
        '''

        if self.aligned:

            # TODO change to copy dictionary

            # print '# virtualizing ', (self.numWire, self.numGeom)

            [numWire, numGeom] = [self.numWire, self.numGeom]
            plane = self.shape
            seedShape = self.seedShape
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
            angle = self.angle
            fronted = self.fronted

            alignedList = self.alignedList
            chopedList = self.chopedList
            reflexedList = self.reflexedList
            rearedList = self.rearedList
            frontedList = self.frontedList

            rangoPy = self.rangoPy

            if not plane:
                (nWire, nGeom) = angle
                pyPl = self.selectPlane(nWire, nGeom)
                plane = pyPl.shape
                seedShape = pyPl.seedShape
                big = pyPl.bigShape
                enormous = pyPl.enormousShape
                simulated = pyPl.simulatedShape
                angle = pyPl.angle

            pyPlane = _PyPlane(numWire, numGeom)

            pyPlane.angle = angle    # danger. It could change the seedShape
            pyPlane.geomShape = geomShape
            pyPlane.geom = geom
            pyPlane.geomAligned = geomAligned
            pyPlane.forward = forward
            pyPlane.backward = backward
            pyPlane.rear = rear
            pyPlane.rango = rango
            pyPlane.aligned = True
            pyPlane.reflexed = True
            pyPlane.fronted = fronted
            pyPlane.shape = plane.copy()
            pyPlane.seedShape = seedShape
            pyPlane.bigShape = big
            pyPlane.enormousShape = enormous
            pyPlane.simulatedShape = simulated
            pyPlane.virtualized = True

            pyPlane.alignedList = alignedList
            pyPlane.chopedList = chopedList
            pyPlane.reflexedList = reflexedList
            pyPlane.rearedList = rearedList
            pyPlane.frontedList = frontedList

            pyPlane.rangoPy = rangoPy

            self.virtuals.append(pyPlane)

            return pyPlane

        else:

            return self

    def trimming(self, enormousShape, enormShape=None):

        '''trimming(self, enormousShape, enormShape=None)'''

        bigShape = self.bigShape
        gS = self.geomShape

        if enormShape:
            cutterList = enormShape
        else:
            cutterList = [enormousShape]

        self.cuttingPyth(cutterList)

        bigShape = self.cutting(bigShape, [enormousShape], gS)
        self.bigShape = bigShape

    def trimmingTwo(self, enormousShape):

        '''trimmingTwo(self, enormousShape)'''

        self.simulating(enormousShape)

        bigShape = self.bigShape
        gS = self.geomShape
        bigShape = self.cutting(bigShape, [enormousShape], gS)
        self.bigShape = bigShape

    def simulating(self, cList):

        '''simulating(self, cList)'''

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

    def rearing(self, pyWire, pyReflex, direction):

        '''rearing(self, pyWire, pyReflex, direction)'''

        # print '### rearing ', (self.numWire, self.numGeom, direction, self.virtualized)

        tolerance = _Py.tolerance
        plane = self.shape

        # TODO pasar forward backward para PyReflex

        forward = self.forward

        if direction == "forward":
            pyOppPlane = pyReflex.planes[1]
            rear = self.rear[0]

            if len(self.rear) > 1:

                rr = pyReflex.rear[0]
                # print(rr, rear)
                if rr != rear:
                    # print 'backw'
                    forward = self.backward

        else:
            pyOppPlane = pyReflex.planes[0]
            rear = self.rear[-1]

            # alignments with reflexs
            if self.virtualized:
                forward = self.backward

            elif len(self.rear) > 1:

                rr = pyReflex.rear[-1]
                # print(rr, rear)
                if rr == rear:
                    # print 'backw'
                    forward = self.backward

        pyPlaneList = pyWire.planes

        oppPlane = pyOppPlane.shape
        # print 'pyOppPlane ', pyOppPlane.numGeom

        pyRearPl = pyPlaneList[rear]
        # print 'pyRearPl ', rear

        if not self.isSolved():
            # print 'fo'

            section = plane.section([forward], tolerance)
            if section.Edges:
                # print 'fofo'
                return

        # if not (pyRearPl.aligned or pyRearPl.choped):
        if not pyRearPl.aligned:

            gS = pyRearPl.geomShape
            rearPl = pyRearPl.shape
            control = pyRearPl.control

            cList = []
            if self.numGeom not in control:
                cList.append(plane)
                # print 'included ', self.numGeom
                control.append(self.numGeom)

            if pyOppPlane.numGeom not in control:
                fo = pyOppPlane.forward
                ba = pyOppPlane.backward
                section = oppPlane.section([fo, ba], tolerance)
                if not section.Edges:
                    cList.append(oppPlane)
                    # print 'included ', pyOppPlane.numGeom
                    control.append(pyOppPlane.numGeom)

            if cList:
                # print 'cList ', cList

                if isinstance(rearPl, Part.Compound):
                    # print 'aa'

                    if len(rearPl.Faces) > 1:
                        # print 'aa1'

                        aList = []
                        for ff in rearPl.Faces:
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
                        pyRearPl.shape = compound

                    else:
                        # print 'aa2'
                        rearPl = self.cutting(rearPl, cList, gS)
                        compound = Part.Compound([rearPl])
                        pyRearPl.shape = compound

                else:
                    # print 'bb'
                    pyRearPl.cuttingPyth(cList)

                if not pyRearPl.choped:

                    if len(plane.Faces) == 1:
                        # print 'AA'

                        if rear not in self.control:

                            gS = self.geomShape
                            plane = self.cutting(plane, [rearPl], gS)
                            compound = Part.Compound([plane])
                            self.shape = compound
                            self.control.append(rear)

                    if len(oppPlane.Faces) == 1:    # cuidado
                        # print 'BB'

                        if rear not in pyOppPlane.control:

                            gS = pyOppPlane.geomShape
                            oppPlane = self.cutting(oppPlane, [rearPl], gS)
                            compound = Part.Compound([oppPlane])
                            pyOppPlane.shape = compound
                            pyOppPlane.control.append(rear)

    def ordinaries(self, pyWire):

        '''ordinaries(self, pyWire)'''

        tolerance = _Py.tolerance
        pyPlaneList = pyWire.planes
        control = self.control

        if self.aligned:

            pyAlignList = self.alignedList
            # print 'pyAlignList ', pyAlignList

            pyAlign = pyAlignList[0]
            rr = pyAlign.rangoRear[0]

        cutterList = []
        for pyPl in pyPlaneList:
            nGeom = pyPl.numGeom
            if nGeom not in control:
                pl = pyPl.shape
                if pl:
                    # print '### numGeom ', pyPl.numGeom

                    if pyPl.aligned:
                        # print 'a'

                        pyAli = pyPl.selectAlignmentBase()

                        if pyAli:
                            # print 'pyAli ', (pyAli.base.numWire, pyAli.base.numGeom)
                            ll = pyAli.geomAligned
                            simulAlign = pyAli.simulatedAlignment

                            if self.aligned:
                                # print 'a1'
                                # for pyAlign in pyAlignList:

                                line = pyAlign.geomAligned
                                base = pyAlign.base.shape

                                section = line.section([ll], tolerance)
                                if not section.Vertexes:
                                    section = base.section([pl], tolerance)
                                    if section.Edges:
                                        common = base.common(simulAlign,
                                                             tolerance)
                                        # print 'area ', common.Area
                                        if not common.Area:
                                            # print 'a11'
                                            cutterList.extend(pyAli.simulatedAlignment)

                            else:
                                # print 'a2'
                                if pyAli in self.rearedList:
                                    cutterList.extend(pyAli.simulatedAlignment)

                    elif pyPl.choped:
                        # print 'b'
                        pass

                    elif pyPl.fronted:
                        # print 'c'
                        if self.aligned:
                            # print 'c1'
                            if nGeom in rr:
                                pl = pyPl.bigShape
                                cutterList.append(pl)
                        else:
                            # print 'c2'
                            pass

                    elif pyPl.reflexed:
                        # print 'd'

                        if self.aligned:
                            if pyPl not in [pyAlign.prior, pyAlign.later]:

                                if pyPl.isSolved():
                                    # print 'd1'
                                    cutterList.append(pl)
                                    control.append(pyPl.numGeom)
                                else:
                                    # print 'd2'
                                    cutterList.append(pyPl.simulatedShape)

                        else:

                            if pyPl.isSolved():
                                # print 'd11'
                                cutterList.append(pl)
                                control.append(pyPl.numGeom)
                            else:
                                # print 'd22'
                                cutterList.append(pyPl.simulatedShape)

                    else:
                        # print 'e'
                        cutterList.append(pl)
                        control.append(pyPl.numGeom)

        if cutterList:
            # print 'cutterList ', cutterList,  # [sh.Area for sh in cutterList]
            plane = self.shape.copy()
            gS = self.geomShape

            if self.reflexed and not self.aligned:
                # print '1'

                if len(plane.Faces) == 1:
                    # print '11'
                    plane = plane.cut(cutterList, tolerance)
                    ff = self.selectFace(plane.Faces, gS)
                    fList = [ff]
                    plane = plane.removeShape([ff])
                    for ff in plane.Faces:
                        section = ff.section(fList, tolerance)
                        if not section.Edges:
                            fList.append(ff)
                            break
                    compound = Part.makeCompound(fList)
                    self.shape = compound
                    # print 'fList ', fList
                    # print 'compound ', compound

                else:
                    # print '12'
                    ff = plane.Faces[0]
                    ff = self.cutting(ff, cutterList, gS)
                    fList = [ff]

                    ff = plane.Faces[1]
                    ff = ff.cut(cutterList, tolerance)
                    fList.append(ff.Faces[0])   # esto hay que cambiarlo?

                    compound = Part.makeCompound(fList)
                    self.shape = compound
                    # print 'fList ', fList
                    # print 'compound ', compound

            else:
                # print '2'

                self.cuttingPyth(cutterList)

        # print 'shape ', self.shape

    def rangging(self, pyWire, direction, pyReflex=None):

        '''rangging(self, pyWire, direction)'''

        # print 'rangging ', (self.numWire, self.numGeom), direction, self.rear
        numGeom = self.numGeom

        rear = self.rear
        lenRear = len(rear)

        if lenRear == 0:
            # print 'a'

            self.rango = [[]]

        elif lenRear == 1:
            # print 'b'

            if pyReflex:
                # print 'b1'
                rearReflex = pyReflex.rear
                if direction == 'forward':
                    nGeom = rearReflex[0]
                else:
                    nGeom = rearReflex[1]
                if nGeom is None:
                    return

            else:
                # print 'b2'
                nGeom = rear[0]

            ran = self.rang(pyWire, numGeom, nGeom, direction, True)
            self.addValue('rango', ran, direction)

        else:
            # print 'c'

            nGeom = rear[0]
            ran = self.rang(pyWire, numGeom, nGeom, 'forward', True)
            self.addValue('rango', ran, 'forward')

            nGeom = rear[-1]
            ran = self.rang(pyWire, numGeom, nGeom, 'backward', True)
            self.addValue('rango', ran, 'backward')

        # print 'rango ', self.rango

    def isSolved(self):

        '''isSolved(self)'''

        if self.solved:
            # print 'memory'
            return True

        tolerance = _Py.tolerance
        forward = self.forward
        backward = self.backward
        plane = self.shape
        section = plane.section([forward, backward], tolerance)
        if section.Edges:
            # print 'edges'
            return False
        else:
            # print 'no edges'
            self.solved = True
            return True

    def isReallySolved(self, pyWire, pyReflex):

        '''isReallySolved(self, pyWire, pyReflex)'''

        if self.reallySolved is not False:
            return self.reallySolved

        tolerance = _Py.tolerance
        conflictList = []
        simul = self.simulatedShape

        pyReflexList = pyWire.reflexs
        for pyRef in pyReflexList:
            for pyPlane in pyRef.planes:
                if pyPlane != self:
                    # print pyPlane.numGeom
                    plane = pyPlane.shape
                    shape = self.shape.copy()
                    shape = shape.cut([plane], tolerance)
                    if len(shape.Faces) == 2:
                        conf = []
                        for ff in shape.Faces:
                            # print 'a'
                            common = ff.common([simul], tolerance)
                            if common.Area:
                                # print 'b'
                                conf.append(pyPlane)
                        if len(conf) == 1:
                            conflictList.extend(conf)

        self.reallySolved = conflictList

        return conflictList
