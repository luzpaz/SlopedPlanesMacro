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
from SlopedPlanesPy import _Py


__title__ = "SlopedPlanes Macro"
__author__ = "Damian Caceres Moreno"
__url__ = "http://www.freecadweb.org"

###############################################################################


origin = FreeCAD.Vector(0, 0, 0)
axisZ = FreeCAD.Vector(0, 0, 1)


def roundVector(vector):

    ''''''

    precision = 1 / _Py.tolerance
    precision = str(precision)
    precision = precision[:].find('.')

    return FreeCAD.Vector(round(vector.x, precision),
                          round(vector.y, precision),
                          round(vector.z, precision))


def rotateVector(vector, axis, angle):

    ''''''

    line = Part.LineSegment(origin, vector)
    rotation = FreeCAD.Rotation(axis, angle)
    placement = FreeCAD.Placement(origin, rotation)
    line.rotate(placement)
    vector = line.EndPoint
    return vector


def faceNormal(face):

    ''''''

    normal = face.normalAt(0, 0)
    return roundVector(normal)


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


def orientedVertixes(wire, normal):

    ''''''

    orderVert = wire.OrderedVertexes

    orderPoint = [vert.Point for vert in orderVert]
    geometryList = geometries(orderPoint)
    edges = [line.toShape() for line in geometryList]
    wire = Part.Wire(edges)
    face = Part.makeFace(wire, "Part::FaceMakerSimple")
    norm = faceNormal(face)

    if normal == norm.negative():
        orderVert.reverse()
    orientVert = orderVert

    return orientVert


def orientedPoints(wire, normal):

    ''''''

    orientVert = orientedVertixes(wire, normal)
    orientPoint = [vert.Point for vert in orientVert]
    orientRoundPoint = [roundVector(vector)
                        for vector in orientPoint]
    return orientRoundPoint


def facePoints(face):

    ''''''

    normal = faceNormal(face)
    wire = face.OuterWire
    orientPoint = orientedPoints(wire, normal)
    return orientPoint


def upperLeftPoint(localCoordinates):

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


def faceDatas(face):

    ''''''

    normal = faceNormal(face)
    tilt = normal.getAngle(FreeCAD.Vector(0, 0, 1))
    tilt = math.degrees(tilt)

    if tilt == 0:
        x = FreeCAD.Vector(1, 0, 0)
        # y = FreeCAD.Vector(0, 1, 0)

    elif tilt == 180:
        x = FreeCAD.Vector(1, 0, 0)
        # y = FreeCAD.Vector(0, -1, 0)

    elif tilt == 90:
        x = rotateVector(normal, axisZ, 90)
        # y = rotateVector(x, normal, 90)

    else:
        pnorm = normal.projectToPlane(FreeCAD.Vector(0, 0, 0),
                                      FreeCAD.Vector(0, 0, 1))
        x = rotateVector(pnorm, axisZ, 90)
        normal = faceNormal(face)
        # y = rotateVector(normal, x, -90)

    normal = faceNormal(face)
    globalCoord = facePoints(face)

    angleZ = normal.getAngle(axisZ)
    angleZ = math.degrees(angleZ)
    projection = x.projectToPlane(origin, axisZ)
    angleX = projection.getAngle(FreeCAD.Vector(1, 0, 0))
    if projection.y < 0:
        angleX = -1 * angleX
    angleX = math.degrees(angleX)
    copyFace = face.copy()
    copyFace.rotate(origin, FreeCAD.Vector(0, 0, -1), angleX)
    copyFace.rotate(origin, FreeCAD.Vector(-1, 0, 0), angleZ)

    localCoord = facePoints(copyFace)
    index = lowerLeftPoint(localCoord)
    localCoord = localCoord[index:] + localCoord[:index]
    localCoord = [coord.sub(localCoord[0]) for coord in localCoord]
    localCoord = [roundVector(point) for point in localCoord]
    globalCoord = globalCoord[index:] + globalCoord[:index]

    return localCoord, globalCoord, angleX, angleZ


def arcGeometries(face, coordinates):

    ''''''

    coordinates.append(coordinates[0])
    first = coordinates[0]
    second = coordinates[1]
    edgeList = face.OuterWire.OrderedEdges

    number = -1
    for edge in edgeList:
        number += 1
        start = roundVector(edge.Vertexes[0].Point)
        if start == first or start == second:
            end = roundVector(edge.Vertexes[1].Point)
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

        if isinstance(curve, Part.Line):
            geom = Part.LineSegment(coordinates[number], coordinates[number+1])
        elif isinstance(curve, Part.Circle):
            geom = Part.ArcOfCircle(curve, startParam, endParam)
        elif isinstance(curve, Part.Ellipse):
            geom = Part.ArcOfEllipse(curve, startParam, endParam)
        elif isinstance(curve, Part.Hyperbola):
            geom = Part.ArcOfHyperbola(curve, startParam, endParam)
        elif isinstance(curve, Part.Parabola):
            geom = Part.ArcOfParabola(curve, startParam, endParam)

        geometries.append(geom)

    coordinates.pop()

    return geometries


def convexReflex(eje, nextEje, numWire):

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


def sliceIndex(index, lenWire):

    ''''''

    if index >= lenWire:
        index = index - lenWire

    elif index < 0:
        index = index + lenWire

    return index
