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


__title__ = "SlopedPlanes Macro"
__author__ = "Damian Caceres Moreno"
__url__ = "http://www.freecadweb.org"

###############################################################################


globalOrigin = FreeCAD.Vector(0, 0, 0)
axisX = FreeCAD.Vector(1, 0, 0)
axisZ = FreeCAD.Vector(0, 0, 1)


def roundVector(vector, tolerance):

    ''''''

    precision = 1 / tolerance
    precision = str(precision)
    precision = precision[:].find('.')

    return FreeCAD.Vector(round(vector.x, precision),
                          round(vector.y, precision),
                          round(vector.z, precision))


def rotateVector(vector, axis, angle):

    ''''''

    line = Part.LineSegment(globalOrigin, vector)
    rotation = FreeCAD.Rotation(axis, angle)
    placement = FreeCAD.Placement(globalOrigin, rotation)
    line.rotate(placement)
    vector = line.EndPoint
    return vector


def faceNormal(face, tolerance):

    ''''''

    normal = face.normalAt(0, 0)
    return roundVector(normal, tolerance)


def geometries(pointList):

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


def orientedVertixes(wire, normal, tolerance):

    ''''''

    orderVert = wire.OrderedVertexes

    orderPoint = [vert.Point for vert in orderVert]
    geometryList = geometries(orderPoint)
    edges = [line.toShape() for line in geometryList]
    wire = Part.Wire(edges)
    face = Part.makeFace(wire, "Part::FaceMakerSimple")
    norm = faceNormal(face, tolerance)

    if normal == norm.negative():
        orderVert.reverse()
    orientVert = orderVert

    return orientVert


def orientedPoints(wire, normal, tolerance):

    ''''''

    orientVert = orientedVertixes(wire, normal, tolerance)
    orientPoint = [vert.Point for vert in orientVert]
    orientRoundPoint = [roundVector(vector, tolerance)
                        for vector in orientPoint]
    return orientRoundPoint


def facePoints(face, tolerance):

    ''''''

    normal = faceNormal(face, tolerance)
    wire = face.OuterWire
    orientPoint = orientedPoints(wire, normal, tolerance)
    return orientPoint


def lowerLeftPoint(localCoordinates):

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


def faceDatas(face, tolerance):

    ''''''

    normal = faceNormal(face, tolerance)
    tilt = normal.getAngle(FreeCAD.Vector(0, 0, 1))
    tilt = math.degrees(tilt)

    if tilt == 0:
        x = FreeCAD.Vector(1, 0, 0)
        y = FreeCAD.Vector(0, 1, 0)

    elif tilt == 180:
        x = FreeCAD.Vector(1, 0, 0)
        y = FreeCAD.Vector(0, -1, 0)

    elif tilt == 90:
        x = rotateVector(normal, axisZ, 90)
        y = rotateVector(x, normal, 90)

    else:
        pnorm = normal.projectToPlane(FreeCAD.Vector(0, 0, 0),
                                      FreeCAD.Vector(0, 0, 1))
        x = rotateVector(pnorm, axisZ, 90)
        normal = faceNormal(face)
        # y = rotateVector(normal, x, -90)

    normal = faceNormal(face, tolerance)
    globalCoord = facePoints(face, tolerance)

    angleZ = normal.getAngle(axisZ)
    angleZ = math.degrees(angleZ)
    projection = x.projectToPlane(globalOrigin, axisZ)
    angleX = projection.getAngle(axisX)
    if projection.y < 0:
        angleX = -1 * angleX
    angleX = math.degrees(angleX)
    copyFace = face.copy()
    copyFace.rotate(globalOrigin, FreeCAD.Vector(0, 0, -1), angleX)
    copyFace.rotate(globalOrigin, FreeCAD.Vector(-1, 0, 0), angleZ)

    localCoord = facePoints(copyFace, tolerance)
    index = lowerLeftPoint(localCoord)
    localCoord = localCoord[index:] + localCoord[:index]
    localCoord = [coord.sub(localCoord[0]) for coord in localCoord]
    localCoord = [roundVector(point, tolerance) for point in localCoord]
    globalCoord = globalCoord[index:] + globalCoord[:index]

    return localCoord, globalCoord, angleX, angleZ


def arcGeometries(face, tolerance):

    ''''''

    globalCoord = faceDatas(face, tolerance)[1]
    globalCoord.append(globalCoord[0])
    first = globalCoord[0]
    second = globalCoord[1]
    edgeList = face.OuterWire.OrderedEdges

    number = -1
    for edge in edgeList:
        number += 1
        start = roundVector(edge.Vertexes[0].Point, tolerance)
        if start == first or start == second:
            end = roundVector(edge.Vertexes[1].Point, tolerance)
            if end == first or end == second:
                break
    edgeList = edgeList[number:] + edgeList[:number]

    geometries = []
    number = -1
    for edge in edgeList:
        number += 1
        curve = edge.Curve
        startParam = curve.parameter(globalCoord[number])
        endParam = curve.parameter(globalCoord[number+1])

        if isinstance(curve, Part.Line):
            geom = Part.LineSegment(globalCoord[number], globalCoord[number+1])
        elif isinstance(curve, Part.Circle):
            geom = Part.ArcOfCircle(curve, startParam, endParam)
        elif isinstance(curve, Part.Ellipse):
            geom = Part.ArcOfEllipse(curve, startParam, endParam)
        elif isinstance(curve, Part.Hyperbola):
            geom = Part.ArcOfHyperbola(curve, startParam, endParam)
        elif isinstance(curve, Part.Parabola):
            geom = Part.ArcOfParabola(curve, startParam, endParam)

        geometries.append(geom)

    globalCoord.pop()

    return globalCoord, geometries


def wireGeometries(wire, tolerance):

    ''''''

    falseFace = Part.makeFace(wire, "Part::FaceMakerSimple")
    pointWire, geomWire = arcGeometries(falseFace, tolerance)

    shapeGeomWire = []
    numGeom = -1
    for geom in geomWire:
        numGeom += 1
        shapeGeomWire.append(geom.toShape())

    return pointWire, geomWire, shapeGeomWire


def convexReflex(eje, nextEje, normal, numWire):

    ''''''

    cross = eje.cross(nextEje)
    corner = None
    if cross != globalOrigin:
        cross.normalize()
        if cross == normal:
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


def sliceIndex(index, lenWire):

    ''''''

    if index >= lenWire:
        index = index - lenWire

    elif index < 0:
        index = index + lenWire

    return index


def selectFace(faceList, geomShape, tolerance):

    ''''''

    for face in faceList:
        section = face.section(geomShape, tolerance)
        if section.Edges:
            return face
    return faceList[0]

