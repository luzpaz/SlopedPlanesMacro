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


import FreeCAD
import Part


__title__ = "SlopedPlanes Macro"
__author__ = "Damian Caceres Moreno"
__url__ = "http://www.freecadweb.org"
__version__ = ""


origin = FreeCAD.Vector(0, 0, 0)
axisZ = FreeCAD.Vector(0, 0, 1)


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

    def getstate(self, faceList):

        ''''''

        fList = []
        for face in faceList:
            string = face.exportBrepToString()
            fList.append(string)

        return fList

    def setstate(self, fList):

        faceList = []
        for string in fList:
            shape = Part.Shape()
            shape.importBrepFromString(string)
            faceList.append(shape.Faces[0])

        return faceList

    def addLink(self, prop, obj):

        ''''''

        linkList = getattr(self, prop)
        if isinstance(obj, list):
            linkList.extend(obj)
        else:
            linkList.append(obj)
        setattr(self, prop, linkList)

    def addValue(self, prop, value, direction='forward'):

        ''''''

        # hacer que no se repitan valores

        valueList = getattr(self, prop)
        if direction == 'forward':
            valueList.insert(0, value)
        else:
            valueList.append(value)
        setattr(self, prop, valueList)

    def selectAlignment(self, numWire, numGeom):

        '''selectAlignment(self, numWire, numGeom)
        select an unique alignment which includes the plane (numWire, numGeom)
        as base plane or in its aligned planes and return it, or None
        used in Py, PyPlane and PyReflex'''

        pyWireList = _Py.pyFace.wires
        pyWire = pyWireList[numWire]
        pyPlaneList = pyWire.planes
        pyPlane = pyPlaneList[numGeom]

        pyAlignList = _Py.pyFace.alignments
        for pyAlign in pyAlignList:
            if pyAlign.base == pyPlane:
                return pyAlign
            elif pyPlane in pyAlign.aligns:
                return pyAlign

        return None

    def selectAlignmentBase(self, numWire, numGeom):

        '''selectAlignmentBase(self, numWire, numGeom)
        select an unique alignment which base plane is (numWire, numGeom),
        and return it, or None
        used in PyFace'''

        pyPlane = self.selectPlane(numWire, numGeom)

        for pyAlign in _Py.pyFace.alignments:
            if pyAlign.base == pyPlane:
                return pyAlign

        return None

    def selectAllAlignment(self, numWire, numGeom):

        '''selectAllAlignment(self, numWire, numGeom)
        select all alignment which the plane (numWire, numGeom)
        is in their chops, and return them
        used in PyAlignment'''

        pyAlignList = []

        for pyAlign in _Py.pyFace.alignments:
            for chop in pyAlign.chops:
                for pyPlane in chop:
                    if pyPlane.numWire == numWire and\
                       pyPlane.numGeom == numGeom:
                        pyAlignList.append(pyAlign)

        return pyAlignList

    def selectAllReflex(self, numWire, numGeom):

        '''selectAllReflex(self, numWire, numGeom)
        select all reflex corner (cero, one or two) in the wire numWire,
        which envolve the plane numGeom,
        and return it
        used in PyWire and PyReflex'''

        pyRList = []
        for pyReflex in _Py.pyFace.wires[numWire].reflexs:
            [pyPlane, pyPl] = pyReflex.planes
            [nn, mm] = [pyPlane.numGeom, pyPl.numGeom]
            if numGeom in [nn, mm]:
                pyRList.append(pyReflex)

        return pyRList

    def selectReflex(self, numWire, numGeom, nGeom):

        '''selectReflex(self, numWire, numGeom, nGeom)
        select an unique reflex corner in the wire numWire,
        which envolves the planes numGeom and nGeom,
        and return it, or None
        used in PyWire.'''

        for pyReflex in _Py.pyFace.wires[numWire].reflexs:
            [pyPlane, pyPl] = pyReflex.planes
            [nn, mm] = [pyPlane.numGeom, pyPl.numGeom]
            if [nn, mm] == [numGeom, nGeom] or [nn, mm] == [nGeom, numGeom]:
                return pyReflex

        return None

    def selectPlane(self, numWire, numGeom):

        '''selectPlane(self, numWire, numGeom)
        '''

        return _Py.pyFace.wires[numWire].planes[numGeom]

    def selectBasePlane(self, numWire, numGeom):

        '''selectBasePlane(self, numWire, numGeom)
        '''

        pyPlane = self.selectPlane(numWire, numGeom)

        if not pyPlane.geomAligned:
            [nW, nG] = pyPlane.angle
            pyPlane = self.selectPlane(nW, nG)

        return pyPlane

    def cutting(self, cutted, cutter, geomShape):

        '''cutting(self, cutted, cutter, geomShape)
        '''

        cutted = cutted.cut(cutter, _Py.tolerance)
        cutted = self.selectFace(cutted.Faces, geomShape)

        return cutted

    def selectFace(self, faceList, geomShape):

        '''selectFace(self, faceList, geomShape)
        '''

        for face in faceList:
            section = face.section([geomShape], _Py.tolerance)
            if section.Edges:
                return face

        return None

    def convexReflex(self, eje, nextEje):

        ''''''

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

        ''''''

        if index >= lenWire:
            index = index - lenWire

        elif index < 0:
            index = index + lenWire

        return index

    def printSummary(self):

        '''printSummary(self)'''

        print '###############################################################'

        print '********* wires ', _Py.pyFace.wires
        for pyWire in _Py.pyFace.wires:

            print '****** numWire ', pyWire.numWire
            # print '*** coordinates ', pyWire.coordinates
            print '*** reflexs ', pyWire.reflexs
            for pyReflex in pyWire.reflexs:

                print 'rangoInter ', pyReflex.rango
                print 'planes ', pyReflex.planes
                for pyPlane in pyReflex.planes:
                    print 'numGeom ', pyPlane.numGeom
                    print 'rear ', pyPlane.rear
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
            print(pyAlignment.base.numWire, pyAlignment.base.numGeom)
            print 'angle ', pyAlignment.base.angle
            print 'rear ', pyAlignment.base.rear
            print 'rango ',  pyAlignment.base.rango
            # print 'geom ', pyAlignment.base.geom
            # print 'geomAligned ', pyAlignment.base.geomAligned
            # print 'shape ', pyAlignment.base.shape
            print 'falsify ', pyAlignment.falsify
            print 'rangoChop ', pyAlignment.rango
            print 'prior ', pyAlignment.prior.numGeom
            print 'later ', pyAlignment.later.numGeom

            print '*** chops ', [[(x.numWire, x.numGeom),
                                  (y.numWire, y.numGeom)]
                                 for [x, y] in pyAlignment.chops]
            for chop in pyAlignment.chops:
                for pyPlane in chop:
                    print(pyPlane.numWire, pyPlane.numGeom), ' ',\
                        pyPlane.rear,\
                        pyPlane.rango

            print '*** aligns ', [x.numGeom for x in pyAlignment.aligns]
            for align in pyAlignment.aligns:
                print(align.numWire, align.numGeom)
                print 'rear ', align.rear
                print 'rango ', align.rango
                print 'angle ', align.angle
                # print 'geom ', align.geom
                # print 'geomAligned ', align.geomAligned
                # print 'shape ', align.shape

        print '###############################################################'

    def printAssociatedShapes(self, numWire, numGeom):

        '''printAssociatedShapes(self, numWire, numGeom)'''

        sketch = self.slopedPlanes.Base
        placement = sketch.Placement

        pyPlane = self.selectPlane(numWire, numGeom)

        simulatedShape = pyPlane.simulatedShape
        if simulatedShape:
            simulatedShape.Placement = placement
            Part.show(simulatedShape, self.slopedPlanes.Name+' simulatedShape '+str(numWire)+' '+str(numGeom))

        cutter = pyPlane.cutter
        if cutter:
            print cutter

            compound = Part.makeCompound(cutter)
            compound.Placement = placement
            Part.show(compound, self.slopedPlanes.Name+' cutter '+str(numWire)+' '+str(numGeom))

        if pyPlane.aligned:
            pyAli = self.selectAlignment(numWire, numGeom)
            print pyAli

            compound = Part.makeCompound(pyAli.simulatedAlignment)
            compound.Placement = placement
            Part.show(compound, self.slopedPlanes.Name+' simulatedAlignment '+str(numWire)+' '+str(numGeom))

        if pyPlane.choped:

            compound = Part.makeCompound(pyPlane.simulatedShape)
            compound.Placement = placement
            Part.show(compound, self.slopedPlanes.Name+' simulatedShape '+str(numWire)+' '+str(numGeom))

    def printControl(self, text):

        '''printControl(self, text)'''

        print '###############################################################'

        print text

        for pyWire in _Py.pyFace.wires:
            print 'wire ', pyWire.numWire
            for pyPlane in pyWire.planes:
                print pyPlane.numGeom, pyPlane.control

        print '###############################################################'

    def roundVector(self, vector):

        ''''''

        precision = 1 / _Py.tolerance
        precision = str(precision)
        precision = precision[:].find('.')

        return FreeCAD.Vector(round(vector.x, precision),
                              round(vector.y, precision),
                              round(vector.z, precision))

    def rotateVector(self, vector, axis, angle):

        ''''''

        line = Part.LineSegment(origin, vector)
        rotation = FreeCAD.Rotation(axis, angle)
        placement = FreeCAD.Placement(origin, rotation)
        line.rotate(placement)
        vector = line.EndPoint
        return vector

    def faceNormal(self, face):

        ''''''

        normal = face.normalAt(0, 0)
        return self.roundVector(normal)

    def geometries(self, pointList):

        ''''''

        pointList.append(pointList[0])
        geometryList = []
        num = 0
        while num < len(pointList) - 1:
            pointA = pointList[num]
            pointB = pointList[num+1]
            lineSegment = Part.LineSegment(pointA, pointB)
            geometryList.append(lineSegment)
            num += 1
        pointList.pop()
        return geometryList

    def orientedVertixes(self, wire, normal):

        ''''''

        orderVert = wire.OrderedVertexes

        orderPoint = [vert.Point for vert in orderVert]
        geometryList = self.geometries(orderPoint)
        edges = [line.toShape() for line in geometryList]
        wire = Part.Wire(edges)
        face = Part.makeFace(wire, "Part::FaceMakerSimple")
        norm = self.faceNormal(face)

        if normal == norm.negative():
            orderVert.reverse()
        orientVert = orderVert

        return orientVert

    def orientedPoints(self, wire, normal):

        ''''''

        orientVert = self.orientedVertixes(wire, normal)
        orientPoint = [vert.Point for vert in orientVert]
        orientRoundPoint = [self.roundVector(vector)
                            for vector in orientPoint]
        return orientRoundPoint

    def facePoints(self, face, normal):

        ''''''

        wire = face.OuterWire
        orientPoint = self.orientedPoints(wire, normal)
        return orientPoint

    def faceDatas(self, face):

        ''''''

        # print '_Py.normal ', _Py.normal
        normal = self.faceNormal(face)
        # print 'faceData normal ', normal
        coordinates = self.facePoints(face, normal)
        if normal == _Py.normal:
            index = self.lowerLeftPoint(coordinates)
        else:
            index = self.upperLeftPoint(coordinates)
        coordinates = coordinates[index:] + coordinates[:index]

        # print coordinates

        return coordinates

    def upperLeftPoint(self, coordinates):

        ''''''

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

        ''''''

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

    def arcGeometries(self, face, coordinates):

        ''''''

        coordinates.append(coordinates[0])
        first = coordinates[0]
        second = coordinates[1]
        edgeList = face.OuterWire.OrderedEdges

        number = -1
        for edge in edgeList:
            number += 1
            start = self.roundVector(edge.Vertexes[0].Point)
            if start == first or start == second:
                end = self.roundVector(edge.Vertexes[1].Point)
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

        ''''''

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
            # geom = Part.ArcOfHyperbola(curve, startParam, endParam)
            pass

        elif isinstance(curve, Part.ArcOfHyperbola):
            # geom = Part.ArcOfHyperbola(curve.Hyperbola, startParam, endParam)
            pass

        elif isinstance(curve, Part.BSplineCurve):
            pass

        else:
            pass

        return geom

    def deGeom(self):

        ''''''

        geomAligned = self.geomAligned.Edges[0]
        curve = geomAligned.Curve
        startParam = geomAligned.parameterAt(geomAligned.firstVertex(True))
        endParam = geomAligned.parameterAt(geomAligned.lastVertex(True))
        geom = self.makeGeom(curve, startParam, endParam)

        return geom
