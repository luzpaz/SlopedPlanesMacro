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


V = FreeCAD.Vector


__title__ = "SlopedPlanes Macro"
__author__ = "Damian Caceres Moreno"
__url__ = "https://gitlab.com/damianCaceres/slopedplanes"
__version__ = ""


class _PySketch():

    ''''''

    def __init__(self, sketch):

        '''__init__(self, sketch)'''

        sketch.Proxy = self
        self.Type = "SweepSketch"

        vectorA = V(-707.107, -707.107, 0)
        vectorB = V(0, 0, 0)
        vectorC = V(1414.21, 1414.21, 0)

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

    def __getstate__(self):

        '''__getstate__(self)'''

        state = dict()
        state['Type'] = self.Type
        return state

    def __setstate__(self, state):

        '''__setstate__(self, state)'''

        self.Type = state['Type']

    def locate(self, sketch, plane, slopedPlanes):

        '''locate(self, sketch, plane, slopedPlanes)'''

        numWire = plane.numWire
        geomShape = plane.geomShape
        ffPoint = geomShape.firstVertex(True).Point
        llPoint = geomShape.lastVertex(True).Point

        # print('ffPoint ', ffPoint)
        # print('llPoint ', llPoint)

        if ffPoint == llPoint:
            # print('a')
            edge = slopedPlanes.Shape.Edges[1]
            aa = ffPoint
            bb = edge.firstVertex(True).Point
            direction = bb.sub(aa)

        else:
            # print('b')
            direction = llPoint.sub(ffPoint)

        # print('direction ', direction)

        angle = direction.getAngle(V(1, 0, 0)) + math.pi / 2
        # print('angle ', angle)

        if ffPoint.y > llPoint.y:
            angle = angle + math.pi
            # print('angle ', angle)

        rotation = FreeCAD.Rotation()
        rotation.Axis = V(1, 0, 0)
        rotation.Angle = math.pi / 2
        sketch.Placement.Rotation = rotation

        if ffPoint == llPoint:
            # print('aa')
            rotation = FreeCAD.Rotation()
            rotation.Axis = V(0, 0, 1)
            angleXU = geomShape.Curve.AngleXU
            # print(angleXU)
            if numWire == 0:
                rotation.Angle = math.pi + angleXU
            else:
                rotation.Angle = angleXU
            sketch.Placement.Rotation =\
                rotation.multiply(sketch.Placement.Rotation)

        else:
            # print('bb')
            rotation = FreeCAD.Rotation()
            rotation.Axis = V(0, 0, 1)
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
