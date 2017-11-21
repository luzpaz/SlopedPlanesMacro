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


from math import degrees
import FreeCAD
import Part


__title__ = "SlopedPlanes Macro"
__author__ = "Damian Caceres Moreno"
__url__ = "http://www.freecadweb.org"


origin = FreeCAD.Vector(0, 0, 0)
axisZ = FreeCAD.Vector(0, 0, 1)


class _Py(object):

    '''A functional Class bequeaths methods and class variables'''

    tolerance = 1e-7
    reverse = False
    size = 0
    normal = 0
    face = None
    pyFace = None
    slopedPlanes = None
    upPlane = None

    def addLink(self, prop, obj):

        ''''''

        linkList = getattr(self, prop)
        if isinstance(obj, list):
            linkList.extend(obj)
        else:
            linkList.append(obj)
        setattr(self, prop, linkList)

    def addValue(self, prop, value, direction):

        ''''''

        valueList = getattr(self, prop)
        if direction == 'forward':
            valueList.insert(0, value)
        else:
            valueList.append(value)
        setattr(self, prop, valueList)

    def selectAlignment(self, nWire, nGeom):

        ''''''

        pyWireList = _Py.pyFace.wires
        pyWire = pyWireList[nWire]
        pyPlaneList = pyWire.planes
        pyPlane = pyPlaneList[nGeom]

        pyAlignList = _Py.pyFace.alignments
        for pyAlign in pyAlignList:
            if pyAlign.base == pyPlane:
                # print 'a'
                return pyAlign
            elif pyPlane in pyAlign.aligns:
                # print 'b'
                return pyAlign

        return None

    def selectAlignmentBase(self, nWire, nGeom):

        ''''''

        pyWireList = _Py.pyFace.wires
        pyWire = pyWireList[nWire]
        pyPlaneList = pyWire.planes
        pyPlane = pyPlaneList[nGeom]

        pyAlignList = _Py.pyFace.alignments
        for pyAlign in pyAlignList:
            if pyAlign.base == pyPlane:
                return pyAlign

        return None

    def selectAllAlignment(self, nWire, nGeom):

        ''''''

        pyAlignList = []

        for pyAlign in _Py.pyFace.alignments:
            for chop in pyAlign.chops:
                for pyPlane in chop:
                    if pyPlane.numWire == nWire and pyPlane.numGeom == nGeom:
                        pyAlignList.append(pyAlign)

        return pyAlignList

    def selectReflex(self, numWire, numGeom, nGeom):

        ''''''

        pyReflexList = _Py.pyFace.wires[numWire].reflexs
        for pyReflex in pyReflexList:
            [pyPlane, pyPl] = pyReflex.planes
            [nn, mm] = [pyPlane.numGeom, pyPl.numGeom]
            if [nn, mm] == [numGeom, nGeom] or [nn, mm] == [nGeom, numGeom]:
                return pyReflex

        return None

    def selectAllReflex(self, numWire, numGeom):

        ''''''

        pyRList = []
        pyReflexList = _Py.pyFace.wires[numWire].reflexs
        for pyReflex in pyReflexList:
            [pyPlane, pyPl] = pyReflex.planes
            [nn, mm] = [pyPlane.numGeom, pyPl.numGeom]
            if numGeom in [nn, mm]:
                pyRList.append(pyReflex)

        return pyRList

    def selectPlane(self, numWire, numGeom):

        ''''''

        pyWireList = _Py.pyFace.wires
        for wire in pyWireList:
            if wire.numWire == numWire:
                pyPlaneList = wire.planes
                for plane in pyPlaneList:
                    if plane.numGeom == numGeom:
                        return plane

        return None

    def selectBasePlane(self, numWire, numGeom):

        ''''''

        pyWireList = _Py.pyFace.wires
        pyWire = pyWireList[numWire]
        pyPlaneList = pyWire.planes
        pyPlane = pyPlaneList[numGeom]

        if not pyPlane.geomAligned:
            [nW, nG] = pyPlane.angle
            pyPlane = self.selectPlane(nW, nG)

        return pyPlane

    def cutting(self, cutted, cutter, geomShape):

        ''''''

        cutted = cutted.cut(cutter, _Py.tolerance)
        cutted = self.selectFace(cutted.Faces, geomShape)

        return cutted

    def selectFace(self, faceList, geomShape):

        ''''''

        for face in faceList:
            section = face.section([geomShape], _Py.tolerance)
            if section.Edges:
                return face

        return None

    def printSummary(self):

        ''''''

        print '********* wires ', _Py.pyFace.wires
        for pyWire in _Py.pyFace.wires:

            print '****** numWire ', pyWire.numWire
            print '*** reflexs ', pyWire.reflexs
            for pyReflex in pyWire.reflexs:

                print 'rangoInter ', pyReflex.rango
                print 'planes ', pyReflex.planes
                for pyPlane in pyReflex.planes:
                    print pyPlane.numGeom,\
                        pyPlane.rear,\
                        pyPlane.rango,\
                        (pyPlane.forward.FirstParameter,
                         pyPlane.forward.LastParameter),\
                        (self.roundVector(pyPlane.forward.firstVertex(True).Point),
                         self.roundVector(pyPlane.forward.lastVertex(True).Point)),\
                        (self.roundVector(pyPlane.backward.firstVertex(True).Point),
                         self.roundVector(pyPlane.backward.lastVertex(True).Point))

        print '********* alignments ', _Py.pyFace.alignments
        for pyAlignment in _Py.pyFace.alignments:

            print '****** base'
            print 'numWire ', pyAlignment.base.numWire
            print 'numGeom ', pyAlignment.base.numGeom
            print 'angle ', pyAlignment.base.angle
            print 'rear ', pyAlignment.base.rear
            print 'rango ',  pyAlignment.base.rango
            print 'geom ', pyAlignment.base.geom
            print 'geomAligned ', pyAlignment.base.geomAligned
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
                print(align.numWire, align.numGeom),\
                    align.rear,\
                    align.rango,\
                    align.geom,\
                    align.geomAligned

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

    def facePoints(self, face):

        ''''''

        normal = self.faceNormal(face)
        wire = face.OuterWire
        orientPoint = self.orientedPoints(wire, normal)
        return orientPoint

    def upperLeftPoint(self, localCoordinates):

        ''''''

        orig = localCoordinates[0]
        n = -1
        for col in localCoordinates:
            n += 1
            if col.y > orig.y:
                orig = col
            elif col.y == orig.y:
                if col.x < orig.x:
                    orig = col
        return localCoordinates.index(orig)

    def lowerLeftPoint(self, localCoordinates):

        ''''''

        orig = localCoordinates[0]
        n = -1
        for col in localCoordinates:
            n += 1
            if col.y < orig.y:
                orig = col
            elif col.y == orig.y:
                if col.x < orig.x:
                    orig = col
        return localCoordinates.index(orig)

    def faceDatas(self, face):

        ''''''

        normal = self.faceNormal(face)
        tilt = normal.getAngle(FreeCAD.Vector(0, 0, 1))
        tilt = degrees(tilt)

        if tilt == 0:
            x = FreeCAD.Vector(1, 0, 0)
            # y = FreeCAD.Vector(0, 1, 0)

        elif tilt == 180:
            x = FreeCAD.Vector(1, 0, 0)
            # y = FreeCAD.Vector(0, -1, 0)

        elif tilt == 90:
            x = self.rotateVector(normal, axisZ, 90)
            # y = rotateVector(x, normal, 90)

        else:
            pnorm = normal.projectToPlane(FreeCAD.Vector(0, 0, 0),
                                          FreeCAD.Vector(0, 0, 1))
            x = self.rotateVector(pnorm, axisZ, 90)
            normal = self.faceNormal(face)
            # y = rotateVector(normal, x, -90)

        normal = self.faceNormal(face)
        globalCoord = self.facePoints(face)

        angleZ = normal.getAngle(axisZ)
        angleZ = degrees(angleZ)
        projection = x.projectToPlane(origin, axisZ)
        angleX = projection.getAngle(FreeCAD.Vector(1, 0, 0))
        if projection.y < 0:
            angleX = -1 * angleX
        angleX = degrees(angleX)
        copyFace = face.copy()
        copyFace.rotate(origin, FreeCAD.Vector(0, 0, -1), angleX)
        copyFace.rotate(origin, FreeCAD.Vector(-1, 0, 0), angleZ)

        localCoord = self.facePoints(copyFace)
        index = self.lowerLeftPoint(localCoord)
        localCoord = localCoord[index:] + localCoord[:index]
        localCoord = [coord.sub(localCoord[0]) for coord in localCoord]
        localCoord = [self.roundVector(point) for point in localCoord]
        globalCoord = globalCoord[index:] + globalCoord[:index]

        return localCoord, globalCoord, angleX, angleZ

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

    def convexReflex(self, eje, nextEje, numWire):

        ''''''

        cross = eje.cross(nextEje)
        corner = None
        if cross != origin:
            cross.normalize()
            if cross == _Py.normal:
                if numWire == 0:
                    corner = 'convex'
                else:
                    corner = 'reflex'
            else:
                if numWire == 0:
                    corner = 'reflex'
                else:
                    corner = 'convex'

        return corner

    def sliceIndex(self, index, lenWire):

        ''''''

        if index >= lenWire:
            index = index - lenWire

        elif index < 0:
            index = index + lenWire

        return index

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
