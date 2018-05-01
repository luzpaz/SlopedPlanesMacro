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


import math
import FreeCAD
import Part
import Sketcher
if FreeCAD.GuiUp:
    import FreeCADGui


__title__ = "SlopedPlanes Macro"
__author__ = "Damian Caceres Moreno"
__url__ = "http://www.freecadweb.org"
__version__ = ""


origin = FreeCAD.Vector(0, 0, 0)


class _Py(object):

    '''A functional Class bequeaths methods and class variables'''

    tolerance = 1e-7
    reverse = False
    size = 0
    normal = FreeCAD.Vector(0, 0, 1)
    face = None
    pyFace = None
    slopedPlanes = None
    upList = []

    def addValue(self, prop, value, direction='forward'):

        '''addValue(self, prop, value, direction='forward')'''

        valueList = getattr(self, prop)
        if direction == 'forward':
            valueList.insert(0, value)
        else:
            valueList.append(value)
        setattr(self, prop, valueList)

    def selectAlignmentBase(self):

        '''selectAlignmentBase(self)
        selects an unique alignment which base plane is (numWire, numGeom),
        and return it, or None.'''

        for pyAlign in self.alignedList:
            if pyAlign.base == self:
                return pyAlign

        return None

    def selectReflex(self, nGeom):

        '''selectReflex(self, nGeom)
        selects an unique reflex corner in the wire numWire,
        which envolves the planes numGeom and nGeom,
        and return it, or None.'''

        for pyReflex in self.reflexedList:
            for pyPlane in pyReflex.planes:
                if nGeom == pyPlane.numGeom:
                    return pyReflex

        return None

    def selectPlane(self, numWire, numGeom, pyFace=None):

        '''selectPlane(self, numWire, numGeom, pyFace=None)
        Selects the plane numWire and numGeom.'''

        if not pyFace:
            pyFace = _Py.pyFace

        return pyFace.wires[numWire].planes[numGeom]

    def selectBasePlane(self, numWire, numGeom):

        '''selectBasePlane(self, numWire, numGeom)
        Selects the plane numWire and numGeom, or if this lacks of shape
        selects the base plane of the alignment.'''

        pyPlane = self.selectPlane(numWire, numGeom)

        if not pyPlane.geomAligned:
            [nW, nG] = pyPlane.angle
            pyPlane = self.selectPlane(nW, nG)

        return pyPlane

    def cutting(self, cutted, cutter, geomShape):

        '''cutting(self, cutted, cutter, geomShape)'''

        cutted = cutted.cut(cutter, _Py.tolerance)
        cutted = self.selectFace(cutted.Faces, geomShape)

        return cutted

    def cuttingPyth(self, cutter):

        '''cuttingPyth(self, cutter)'''

        cutted = self.shape
        if cutted:
            geomShape = self.geomShape
            cutted = self.cutting(cutted, cutter, geomShape)
            self.shape = cutted

        return cutted

    def selectFace(self, faceList, geomShape):

        '''selectFace(self, faceList, geomShape)'''

        for face in faceList:
            section = face.section([geomShape], _Py.tolerance)
            if section.Edges:
                return face

        return None

    def selectFacePoint(self, shape, point):

        '''selectFacePoint(self, shape, point)'''

        vertex = Part.Vertex(point)
        for ff in shape.Faces:
            section = vertex.section([ff], _Py.tolerance)
            if section.Vertexes:
                return ff

    def selectShape(self):

        '''selectShape(self)'''

        if self.aligned:
            # print 'a'
            aliList = self.alignedList
            shape = []
            for pyA in aliList:
                shape.extend(pyA.simulatedAlignment)
            shape = Part.makeCompound(shape)

        elif self.reflexed:
            # print 'b'
            shape = self.simulatedShape

        else:
            # print 'c'
            shape = self.shape

        return shape

    def printSummary(self):

        '''printSummary(self)'''

        print '###############################################################'

        print '********* wires ', _Py.pyFace.wires
        for pyWire in _Py.pyFace.wires:

            print '****** numWire ', pyWire.numWire
            print '*** coordinates ', pyWire.coordinates
            print '*** reflexs ', pyWire.reflexs
            for pyReflex in pyWire.reflexs:

                print 'planes ', pyReflex.planes
                print 'rangoInter ', pyReflex.rango
                print 'rear reflex', pyReflex.rear
                for pyPlane in pyReflex.planes:
                    print 'numGeom ', pyPlane.numGeom  # , pyPlane.reflexedList
                    print 'rear plane ', pyPlane.rear
                    print 'secondRear ', pyPlane.secondRear
                    print 'rango ', pyPlane.rango
                    '''forward = pyPlane.forward
                    print 'forward ',\
                        (self.roundVector(forward.firstVertex(True).Point),
                         self.roundVector(forward.lastVertex(True).Point))
                    backward = pyPlane.backward
                    print 'backward ',\
                        (self.roundVector(backward.firstVertex(True).Point),
                         self.roundVector(backward.lastVertex(True).Point))'''

        print '********* alignments ', _Py.pyFace.alignments
        for pyAlignment in _Py.pyFace.alignments:

            print '****** base'
            print(pyAlignment.base.numWire, pyAlignment.base.numGeom)  #, pyAlignment.base.alignedList)
            print 'angle ', pyAlignment.base.angle
            print 'rear ', pyAlignment.base.rear
            print 'rango ', pyAlignment.base.rango
            print 'geom ', pyAlignment.base.geom
            print 'geomAligned ', pyAlignment.base.geomAligned
            print 'shape ', pyAlignment.base.shape
            print 'falsify ', pyAlignment.falsify
            print 'virtualized ', pyAlignment.base.virtualized
            print 'cross ', pyAlignment.base.cross
            print 'rangoChop ', pyAlignment.rango
            print 'rangoRear ', pyAlignment.rangoRear[0]
            print 'prior ', pyAlignment.prior.numGeom
            print 'later ', pyAlignment.later.numGeom

            print '*** chops ', [[(x.numWire, x.numGeom),
                                  (y.numWire, y.numGeom)]
                                 for [x, y] in pyAlignment.chops]
            for chop in pyAlignment.chops:
                for pyPlane in chop:
                    print(pyPlane.numWire, pyPlane.numGeom)  # , pyPlane.chopedList)
                    print 'rear ', pyPlane.rear
                    print 'secondRear ', pyPlane.secondRear
                    print 'rango ', pyPlane.rango
                    print 'virtualized ', pyPlane.virtualized
                    print 'cross ', pyPlane.cross

            print '*** aligns ', [(x.numWire, x.numGeom) for x in pyAlignment.aligns]
            for align in pyAlignment.aligns:
                print(align.numWire, align.numGeom)  # , align.alignedList)
                print 'rear ', align.rear
                print 'secondRear ', align.secondRear
                print 'rango ', align.rango
                print 'angle ', align.angle
                print 'virtualized ', align.virtualized
                print 'cross ', align.cross
                print 'geom ', align.geom
                print 'geomAligned ', align.geomAligned
                print 'shape ', align.shape

        print '###############################################################'

    def printSerialSummary(self):

        '''printSerialSummary(self)'''

        for pyFace in self.Pyth:
            for pyWire in pyFace.wires:
                for pyPlane in pyWire.planes:
                    pyPlane.printPlaneSummary()

    def printPlaneSummary(self):

        '''printPlaneSummary(self)'''

        print '###### ', (self.numWire, self.numGeom), self.shape
        if self.shape:
            print 'Area ', self.shape.Area
        geom = self.geomShape
        print (self.roundVector(geom.firstVertex(True).Point), self.roundVector(geom.lastVertex(True).Point))
        forward = self.forward
        try:
            print (self.roundVector(forward.firstVertex(True).Point), self.roundVector(forward.lastVertex(True).Point))
        except:
            pass
        backward = self.backward
        try:
            print (self.roundVector(backward.firstVertex(True).Point), self.roundVector(backward.lastVertex(True).Point))
        except:
            pass

        print '######'

    def printAssociatedShapes(self, numWire, numGeom):

        '''printAssociatedShapes(self, numWire, numGeom)'''

        slopedPlanes = self.slopedPlanes
        sketch = slopedPlanes.Base

        pl = sketch.Placement
        place = slopedPlanes.Placement
        placement = pl.multiply(place)

        pyPlane = self.selectPlane(numWire, numGeom)

        shape = pyPlane.shape
        if shape:

            shape.Placement = placement
            Part.show(shape, slopedPlanes.Name+' shape '+str(numWire)+' '+str(numGeom))

        simulatedShape = pyPlane.simulatedShape
        if simulatedShape:

            simulatedShape.Placement = placement
            Part.show(simulatedShape, slopedPlanes.Name+' simulatedShape '+str(numWire)+' '+str(numGeom))

        cutter = pyPlane.cutter
        if cutter:

            compound = Part.makeCompound(cutter)
            compound.Placement = placement
            Part.show(compound, slopedPlanes.Name+' cutter '+str(numWire)+' '+str(numGeom))

        under = pyPlane.under
        if under:

            compound = Part.makeCompound(under)
            compound.Placement = placement
            Part.show(compound, slopedPlanes.Name+' under '+str(numWire)+' '+str(numGeom))

        seed = pyPlane.seed
        if seed:

            compound = Part.makeCompound(seed)
            compound.Placement = placement
            Part.show(compound, slopedPlanes.Name+' seed '+str(numWire)+' '+str(numGeom))

        if pyPlane.aligned:
            pyAli = pyPlane.selectAlignmentBase()
            if pyAli:

                compound = Part.makeCompound(pyAli.simulatedAlignment)
                compound.Placement = placement
                Part.show(compound, slopedPlanes.Name+' simulatedAlignment '+str(numWire)+' '+str(numGeom))

        virtuals = pyPlane.virtuals
        if virtuals:
            for pyP in virtuals:

                shape = pyP.shape
                if shape:

                    shape.Placement = placement
                    Part.show(pyP.shape, slopedPlanes.Name+' virtual shape '+str(numWire)+' '+str(numGeom))

                under = pyP.under
                if under:

                    compound = Part.makeCompound(pyP.under)
                    compound.Placement = placement
                    Part.show(compound, slopedPlanes.Name+' virtual under '+str(numWire)+' '+str(numGeom))

                cutter = pyP.cutter
                if cutter:

                    cero = FreeCAD.Placement()  # no se en que momento se desplazan con el sketch

                    for ff in cutter:
                        ff.Placement = cero

                    compound = Part.makeCompound(cutter)
                    compound.Placement = placement
                    Part.show(compound, slopedPlanes.Name+' cutter '+str(numWire)+' '+str(numGeom))

    def printControl(self, text):

        '''printControl(self, text)'''

        print '###############################################################'

        print text

        for pyWire in _Py.pyFace.wires:
            print 'wire ', pyWire.numWire
            for pyPlane in pyWire.planes:
                print pyPlane.numGeom, pyPlane.control

        print '###############################################################'

    def convexReflex(self, eje, nextEje):

        '''convexReflex(self, eje, nextEje)'''

        cross = eje.cross(nextEje)
        corner = None
        if cross != origin:
            cross.normalize()

            if cross == _Py.normal:
                corner = 'convex'
            else:
                corner = 'reflex'

        return corner

    def sliceIndex(self, index, lenWire):

        '''sliceIndex(self, index, lenWire)'''

        if index >= lenWire:
            index = index - lenWire

        elif index < 0:
            index = index + lenWire

        return index

    def roundVector(self, vector):

        '''roundVector(self, vector)'''

        precision = 1 / _Py.tolerance
        precision = str(precision)
        precision = precision[:].find('.')

        return FreeCAD.Vector(round(vector.x, precision),
                              round(vector.y, precision),
                              round(vector.z, precision))

    def rotateVector(self, vector, axis, angle):

        '''rotateVector(self, vector, axis, angle)'''

        line = Part.LineSegment(origin, vector)
        rotation = FreeCAD.Rotation(axis, angle)
        placement = FreeCAD.Placement(origin, rotation)
        line.rotate(placement)
        vector = line.EndPoint
        return vector

    def faceNormal(self, face):

        '''faceNormal(self, face)'''

        normal = face.normalAt(0, 0)
        return self.roundVector(normal)

    def faceDatas(self, face):

        '''faceDatas(self, face)'''

        normal = self.faceNormal(face)

        wire = face.OuterWire

        orderVert = wire.OrderedVertexes

        if len(orderVert) == 1:
            orientVert = orderVert

        else:
            orderPoint = [vert.Point for vert in orderVert]

            # print orderPoint

            geometryList = self.geometries(face, orderPoint)
            edges = [line.toShape() for line in geometryList]
            wire = Part.Wire(edges)
            face = Part.makeFace(wire, "Part::FaceMakerSimple")
            norm = self.faceNormal(face)
            if normal == norm.negative():
                orderVert.reverse()
                geometryList.reverse()
            orientVert = orderVert

        orientPoint = [vert.Point for vert in orientVert]
        orientRoundPoint = [self.roundVector(vector)
                            for vector in orientPoint]

        coordinates = orientRoundPoint

        if normal == _Py.normal:
            index = self.lowerLeftPoint(coordinates)
        else:
            index = self.upperLeftPoint(coordinates)
        coordinates = coordinates[index:] + coordinates[:index]
        geometryList = geometryList[index:] + geometryList[:index]

        # print coordinates, geometryList

        return coordinates, geometryList

    def upperLeftPoint(self, coordinates):

        '''upperLeftPoint(self, coordinates)'''

        orig = coordinates[0]
        n = -1
        for col in coordinates:
            n += 1
            if col.y > orig.y:
                orig = col
            elif col.y == orig.y:
                if col.x < orig.x:
                    orig = col
        return coordinates.index(orig)

    def lowerLeftPoint(self, coordinates):

        '''lowerLeftPoint(self, coordinates)'''

        orig = coordinates[0]
        n = -1
        for col in coordinates:
            n += 1
            if col.y < orig.y:
                orig = col
            elif col.y == orig.y:
                if col.x < orig.x:
                    orig = col
        return coordinates.index(orig)

    def geometries(self, face, coordinates):

        '''geometries(self, face, coordinates)'''

        if len(coordinates) == 0:
            edge = face.OuterWire.Edges[0]
            return [edge.Curve]

        coordinates.append(coordinates[0])
        first = coordinates[0]
        second = coordinates[1]
        edgeList = face.OuterWire.OrderedEdges

        number = -1
        for edge in edgeList:
            number += 1
            start = edge.Vertexes[0].Point
            if start == first or start == second:
                end = edge.Vertexes[1].Point
                if end == first or end == second:
                    break
        edgeList = edgeList[number:] + edgeList[:number]

        geometries = []
        number = -1
        for edge in edgeList:
            number += 1
            curve = edge.Curve
            startParam = curve.parameter(coordinates[number])
            endParam = curve.parameter(coordinates[number+1])

            geom = self.makeGeom(curve, startParam, endParam)

            geometries.append(geom)

        coordinates.pop()

        return geometries

    def makeGeom(self, curve, startParam, endParam):

        '''makeGeom(self, curve, startParam, endParam)'''

        if isinstance(curve, (Part.Line, Part.LineSegment)):
            geom = Part.LineSegment(curve, startParam, endParam)

        elif isinstance(curve, Part.Circle):
            geom = Part.ArcOfCircle(curve, startParam, endParam)

        elif isinstance(curve, Part.ArcOfCircle):
            geom = Part.ArcOfCircle(curve.Circle, startParam, endParam)

        elif isinstance(curve, Part.Ellipse):
            geom = Part.ArcOfEllipse(curve, startParam, endParam)

        elif isinstance(curve, Part.ArcOfEllipse):
            geom = Part.ArcOfEllipse(curve.Ellipse, startParam, endParam)

        elif isinstance(curve, Part.Parabola):
            geom = Part.ArcOfParabola(curve, startParam, endParam)

        elif isinstance(curve, Part.ArcOfParabola):
            geom = Part.ArcOfParabola(curve.Parabola, startParam, endParam)

        elif isinstance(curve, Part.Hyperbola):
            geom = Part.ArcOfHyperbola(curve, startParam, endParam)

        elif isinstance(curve, Part.ArcOfHyperbola):
            geom = Part.ArcOfHyperbola(curve.Hyperbola, startParam, endParam)

        elif isinstance(curve, Part.BSplineCurve):
            pass

        else:
            pass

        return geom

    def doGeom(self):

        '''doGeom(self)'''

        if not self.aligned:
            if self.geom:
                return self.geom

        geomAligned = self.geomAligned
        curve = geomAligned.Curve
        startParam = geomAligned.parameterAt(geomAligned.firstVertex(True))
        endParam = geomAligned.parameterAt(geomAligned.lastVertex(True))
        geom = self.makeGeom(curve, startParam, endParam)

        if not self.aligned:
            self.geom = geom

        return geom

    def rang(self, pyWire, numGeom, nGeom, direction, reflex=False):

        '''rang(self, pyWire, numGeom, nGeom, direction, reflex=False)'''

        # print 'rang ', (numGeom, nGeom, reflex)

        if numGeom == nGeom:
            return []

        lenWire = len(pyWire.planes)

        if direction == 'forward':
            # print 'A'
            if reflex:
                # print 'reflex'
                num = numGeom + 2
            else:
                # print 'no reflex'
                num = numGeom + 1
            num = self.sliceIndex(num, lenWire)
            # print 'num ', num

            if nGeom >= num:
                # print 'A1'
                ran = range(num, nGeom)
            else:
                # print 'A2'
                ran = range(num, lenWire) + range(0, nGeom)

        else:
            # print 'B'
            if reflex:
                # print 'reflex'
                num = numGeom - 1
                num = self.sliceIndex(num, lenWire)
            else:
                # print 'no reflex'
                num = numGeom
            # print 'num ', num

            if numGeom >= nGeom:
                # print 'B1'
                ran = range(nGeom + 1, num)
                ran.reverse()
            else:
                # print 'B2'
                ranA = range(nGeom + 1, lenWire)
                ranA.reverse()
                ranB = range(0, num)
                ranB.reverse()
                ran = ranB + ranA

        # print 'ran ', ran
        return ran

    def refine(self, sPEdges, objEdges, endShape, childShape):

        '''refine(self, sPEdges, objEdges, endShape, childShape)'''

        # print 'sPEdges ', sPEdges
        # print 'objEdges ', objEdges

        num = -1
        for edgeOne, edgeTwo in zip(sPEdges, objEdges):
            num += 1

            pyOne = edgeOne[num][0]
            numGeom = pyOne.numGeom
            numWire = pyOne.numWire
            pyFace = edgeOne[num][1]
            pyWireList = pyFace.wires
            pyWire = pyWireList[numWire]
            lenWire = len(pyWire.planes)

            priorOne = self.sliceIndex(numGeom - 1, lenWire)
            priorOne = self.selectPlane(numWire, priorOne, pyFace)
            laterOne = self.sliceIndex(numGeom + 1, lenWire)
            laterOne = self.selectPlane(numWire, laterOne, pyFace)

            pyTwo = edgeTwo[num][0]
            numGeom = pyTwo.numGeom
            numWire = pyTwo.numWire
            pyFace = edgeTwo[num][1]
            pyWireList = pyFace.wires
            pyWire = pyWireList[numWire]
            lenWire = len(pyWire.planes)

            priorTwo = self.sliceIndex(numGeom - 1, lenWire)
            priorTwo = self.selectPlane(numWire, priorTwo, pyFace)
            laterTwo = self.sliceIndex(numGeom + 1, lenWire)
            laterTwo = self.selectPlane(numWire, laterTwo, pyFace)

            seedOne = priorOne.seedShape
            seedTwo = laterTwo.seedShape
            common = seedOne.common(seedTwo)

            if common.Area:

                nn = -1
                for ff in endShape.Faces:
                    nn += 1
                    common = ff.common(seedOne)
                    if common.Area:
                        # print ff.Area
                        break

                mm = -1
                for gg in childShape.Faces:
                    mm += 1
                    common = gg.common(seedTwo)
                    if common.Area:
                        # print gg.Area
                        childShape = childShape.removeShape([gg])
                        break

                # print (ff, nn), (gg, mm)

                faceOne = ff.copy()
                faceTwo = gg.copy()

                coordOne, geomOne = self.faceDatas(faceOne)
                # print coordOne, geomOne
                coordTwo, geomTwo = self.faceDatas(faceTwo)
                # print coordTwo, geomTwo

                numOne = -1
                for cc in coordOne:
                    numOne += 1
                    if cc in coordTwo:
                        numTwo = coordTwo.index(cc)
                        break

                # print 'NUMONE, NUMTWO', (numOne, numTwo)

                aa = geomOne[:numOne]
                # print 'aa ', aa

                bb = geomTwo[numTwo:-1]
                # print 'bb ', bb

                cc = geomTwo[:numTwo]
                # print 'cc ', cc

                dd = geomOne[numOne+1:]
                # print 'dd ', dd

                edgeList = aa + bb + cc + dd
                # print 'edgeList ', edgeList
                edgeList = [e.toShape() for e in edgeList]
                wire = Part.Wire(edgeList)
                face = Part.makeFace(wire, "Part::FaceMakerSimple")
                # print face.Area

                endShape = endShape.replaceShape([(ff, face)])

            seedOne = laterOne.seedShape
            seedTwo = priorTwo.seedShape
            common = seedOne.common(seedTwo)

            if common.Area:

                nn = -1
                for ff in endShape.Faces:
                    nn += 1
                    common = ff.common(seedOne)
                    if common.Area:
                        # print ff.Area
                        break

                mm = -1
                for gg in childShape.Faces:
                    mm += 1
                    common = gg.common(seedTwo)
                    if common.Area:
                        childShape = childShape.removeShape([gg])
                        # print gg.Area
                        break

                # print (ff, nn), (gg, mm)

                faceOne = ff.copy()
                faceTwo = gg.copy()

                coordOne, geomOne = self.faceDatas(faceOne)
                # print coordOne, geomOne
                coordTwo, geomTwo = self.faceDatas(faceTwo)
                # print coordTwo, geomTwo

                numOne = -1
                for cc in coordOne:
                    numOne += 1
                    if cc in coordTwo:
                        numTwo = coordTwo.index(cc)
                        break

                # print 'NUMONE, NUMTWO', (numOne, numTwo)

                aa = geomOne[:numOne]
                # print 'aa ', aa

                bb = geomTwo[numTwo:-1]
                # print 'bb ', bb

                cc = geomTwo[:numTwo]
                # print 'cc ', cc

                dd = geomOne[numOne+1:]
                # print 'dd ', dd

                edgeList = aa + bb + cc + dd
                # print 'edgeList ', edgeList
                edgeList = [e.toShape() for e in edgeList]
                wire = Part.Wire(edgeList)
                face = Part.makeFace(wire, "Part::FaceMakerSimple")
                # print face.Area

                endShape = endShape.replaceShape([(ff, face)])

        return endShape, childShape

    def makeSweepSketch(self, slopedPlanes):

        '''makeSweepSketch(self, slopedPlanes)'''

        pySketch =\
            FreeCAD.ActiveDocument.addObject('Sketcher::SketchObjectPython',
                                             'SweepSketch')

        _PySketch(pySketch)
        _ViewProviderPySketch(pySketch.ViewObject)

        pySketch.Proxy.locate(pySketch, self, slopedPlanes)
        pySketch.Proxy.slope(pySketch, self)

        linkList = slopedPlanes.SweepCurves
        linkList.append(pySketch)
        slopedPlanes.SweepCurves = linkList

        if FreeCAD.GuiUp:
            slopedPlanes.ViewObject.Proxy.task.reject()
            FreeCADGui.activeDocument().setEdit(pySketch.Name)

        self.sweepCurve = pySketch.Name

        return pySketch

class _PySketch(_Py):

    ''''''

    def __init__(self, sketch):

        '''__init__(self, sketch)'''

        sketch.Proxy = self

        vectorA = FreeCAD.Vector(-707.107, -707.107, 0)
        vectorB = FreeCAD.Vector(0, 0, 0)
        vectorC = FreeCAD.Vector(1414.21, 1414.21, 0)

        lineA = Part.LineSegment(vectorA, vectorB)
        lineA.Construction = True
        lineB = Part.LineSegment(vectorA, vectorC)
        lineB.Construction = True

        sketch.Geometry = [lineA, lineB]

        constrA = Sketcher.Constraint('Coincident', 0, 2, 1, 1)

        constrB = Sketcher.Constraint('Coincident', 0, 2, -1, 1)

        constrC = Sketcher.Constraint('Parallel', 0, 1)

        constrD = Sketcher.Constraint('Angle', -1, 1, 1, 1, 0.785398)

        sketch.Constraints = [constrA, constrB, constrC, constrD]

    def execute(self, sketch):

        '''execute(self, sketch)'''

        sketch.recompute()

    def locate(self, sketch, plane, slopedPlanes):

        '''locate(self, sketch, plane, slopedPlanes)'''

        geomShape = plane.geomShape
        ffPoint = geomShape.firstVertex(True).Point
        llPoint = geomShape.lastVertex(True).Point
        direction = llPoint.sub(ffPoint)
        # print 'ffPoint ', ffPoint
        # print 'llPoint ', llPoint
        # print 'direction ', direction

        angle = direction.getAngle(FreeCAD.Vector(1, 0, 0)) + math.pi / 2
        # print 'angle ', angle

        if ffPoint.y > llPoint.y:
            angle = angle + math.pi
            # print 'angle ', angle

        rotation = FreeCAD.Rotation()
        rotation.Axis = FreeCAD.Vector(1, 0, 0)
        rotation.Angle = math.pi / 2
        sketch.Placement.Rotation = rotation

        rotation = FreeCAD.Rotation()
        rotation.Axis = _Py.normal
        rotation.Angle = angle
        sketch.Placement.Rotation =\
            rotation.multiply(sketch.Placement.Rotation)

        sketch.Placement.Base = ffPoint

        baseSketch = slopedPlanes.Base
        placement = baseSketch.Placement

        sketch.Placement = placement.multiply(sketch.Placement)

        placement = slopedPlanes.Placement

        sketch.Placement = placement.multiply(sketch.Placement)

    def slope(self, sketch, plane):

        '''slope(self, sketch, plane)'''

        angle = plane.angle
        sketch.setDatum(3, math.radians(angle))


class _ViewProviderPySketch():

    ''''''

    def __init__(self, vobj):

        '''__init__(self, vobj)'''

        vobj.Proxy = self
