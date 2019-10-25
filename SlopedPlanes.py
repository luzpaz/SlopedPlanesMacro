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


import asyncio
from math import radians, sin, cos, tan
import FreeCAD
import Part
from SlopedPlanesPy import _Py
from SlopedPlanesPyFace import _PyFace
from SlopedPlanesPyWire import _PyWire
from SlopedPlanesPyPlane import _PyPlane
import SlopedPlanesPyEdge
if FreeCAD.GuiUp:
    from os import path
    import FreeCADGui
    from SlopedPlanesTaskPanel import _TaskPanel_SlopedPlanes

V = FreeCAD.Vector
P = FreeCAD.Placement

__title__ = "SlopedPlanes Macro"
__author__ = "Damian Caceres Moreno"
__url__ = "https://gitlab.com/damianCaceres/slopedplanes"
__version__ = ""


def makeSlopedPlanes(sketch, slope=45.0, slopeList=[]):

    '''makeSlopedPlanes(sketch, slope=45.0, slopeList=[])
    makes the SlopedPlanes object from a sketch or a DWire.
    All faces of the SlopedPlanes object could have the same angle,
    45º by default, or specify a different angle for every face throught
    the slopeList'''

    if hasattr(sketch, 'Proxy'):
        if sketch.Proxy.Type != 'Wire':
            return

    elif sketch.TypeId != "Sketcher::SketchObject":
        return

    slopedPlanes =\
        FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "SlopedPlanes")

    _SlopedPlanes(slopedPlanes, slope, slopeList)
    _ViewProvider_SlopedPlanes(slopedPlanes.ViewObject)

    slopedPlanes.Base = sketch
    sketch.ViewObject.Visibility = False

    # TODO el objecto debe quedar seleccionado tras su creación

    return slopedPlanes


class _SlopedPlanes(_Py):

    '''The Class of the FreeCAD scripted object SlopedPlanes.
    Requieres a sketch or DWire as base. The base must support the FaceMaker.
    The angles numeration corresponds to the SlopedPlanes shape faces.'''

    def __init__(self, slopedPlanes, slope=45.0, slopeList=[]):

        '''__init__(self, slopedPlanes)
        Initializes the properties of the SlopedPlanes object and its Proxy.
        The Proxy stores:

        - three flags
            Type: object recognition
            State: jumps onChanged function at the loading file
            OnChanged: faster execute from property and task panels (~7%)

        - three lists:
            Pyth: the complementary python objects (serialized)
            faceList: produced by the FaceMaker over the base
            slopeList: list of angles'''

        # _____________________________________________________________________

        slopedPlanes.addExtension("App::GroupExtensionPython", self)

        doc = "The sketch or Dwire in which the SlopedPlanes is based"

        slopedPlanes.addProperty("App::PropertyLink", "Base",
                                 "Base", doc)

        # _____________________________________________________________________

        doc = ('Applies over all planes angles.\n'
               'To cero the SlopedPlanes hasn\'t shape')

        slopedPlanes.addProperty("App::PropertyAngle", "Slope",
                                 "SlopedPlanes", doc)

        doc = "Reverses the angles of the SlopedPlanes"

        slopedPlanes.addProperty("App::PropertyBool", "Reverse",
                                 "SlopedPlanes", doc)

        # _____________________________________________________________________

        doc = ('Applies over all planes length, or length of extrusion \n'
               'of the base\'s edges, multiplied by the diagonal \n'
               'length of the SlopedPlanes base.\n'
               'To cero the SlopedPlanes hasn\'t shape')

        slopedPlanes.addProperty("App::PropertyFloat", "FactorLength",
                                 "SlopedPlanes", doc)

        doc = ('Applies over all planes width, left and right,\n'
               'multiplied by the diagonal length of the SlopedPlanes base.\n'
               'To cero the plane width is equal to the length of \n'
               'the related edge of the base')

        slopedPlanes.addProperty("App::PropertyFloat", "FactorWidth",
                                 "SlopedPlanes", doc)

        doc = ('Applies over all planes overhang height,\n'
               'multiplied by the diagonal \n'
               'length of the SlopedPlanes base.\n'
               'It \'s limited to 1 or even less')

        slopedPlanes.addProperty("App::PropertyFloatConstraint",
                                 "FactorOverhang",
                                 "SlopedPlanes", doc)

        # _____________________________________________________________________

        doc = "Available curves to sweep (Not available yet!)"

        slopedPlanes.addProperty("App::PropertyLinkList", "SweepCurves",
                                 "SlopedPlanes", doc)

        # _____________________________________________________________________

        doc = "Gives a thickness to the SlopedPlanes"

        slopedPlanes.addProperty("App::PropertyLength", "Thickness",
                                 "SlopedPlanes", doc)

        doc = ('Thickness direction.\n'
               '    Vertical: \n'
               '    Horizontal: \n'
               '    Slope: \n'
               '    ThicknessSlope: \n'
               '    Normal: normal to planes. Height calculated with 45º \n'
               '            and the length of Thickness property. \n')

        slopedPlanes.addProperty("App::PropertyEnumeration",
                                 "ThicknessDirection",
                                 "SlopedPlanes", doc)

        doc = "Thickness slope"

        slopedPlanes.addProperty("App::PropertyAngle", "ThicknessSlope",
                                 "SlopedPlanes", doc)

        # _____________________________________________________________________

        doc = "Gives a plane on SlopedPlanes base"

        slopedPlanes.addProperty("App::PropertyBool", "Down",
                                 "SlopedPlanesPart", doc)

        doc = "Gives a plane on top of the SlopedPlanes"

        slopedPlanes.addProperty("App::PropertyLength", "Up",
                                 "SlopedPlanesPart", doc)

        doc = "Mirrors the SlopedPlanes with respect its base"

        slopedPlanes.addProperty("App::PropertyBool", "Mirror",
                                 "SlopedPlanesPart", doc)

        doc = "Computes de complement of the orientation of the SlopedPlanes"

        slopedPlanes.addProperty("App::PropertyBool", "Complement",
                                 "SlopedPlanesPart", doc)

        doc = "Creates a solid out of the SlopedPlanes shells"

        slopedPlanes.addProperty("App::PropertyBool", "Solid",
                                 "SlopedPlanesPart", doc)

        doc = "FaceMaker"

        slopedPlanes.addProperty("App::PropertyEnumeration", "FaceMaker",
                                 "SlopedPlanesPart", doc)

        doc = "Tolerance value applied in boolean operation (Fuzzy)"

        slopedPlanes.addProperty("App::PropertyPrecision", "Tolerance",
                                 "SlopedPlanesPart", doc)

        # _____________________________________________________________________

        self.State = True

        try:
            ang = float(slope)
        except ValueError:
            ang = 45.0
        slopedPlanes.Slope = ang

        slopedPlanes.FactorLength = 2
        slopedPlanes.FactorWidth = 1

        slopedPlanes.ThicknessDirection = ["Vertical",
                                           "Horizontal",
                                           "Slope",
                                           "ThicknessSlope",
                                           "Normal"]

        slopedPlanes.ThicknessSlope = ang

        slopedPlanes.FaceMaker = ["Part::FaceMakerBullseye",
                                  "Part::FaceMakerSimple",
                                  "Part::FaceMakerCheese"]

        slopedPlanes.Tolerance = 1e-7

        slopedPlanes.Proxy = self

        self.Pyth = []
        self.faceList = []
        self.slopeList = slopeList

        self.Type = "SlopedPlanes"

        self.OnChanged = False

    def execute(self, slopedPlanes):

        '''execute(self, slopedPlanes)
        Builds the shape of the slopedPlanes object.'''

        # print('execute')

        sketch = slopedPlanes.Base
        shape = sketch.Shape.copy()
        placement = sketch.Placement
        shape.Placement = P()

        self.declareSlopedPlanes(slopedPlanes)

        # print(self.OnChanged)

        if self.OnChanged:
            # print('A ', self.OnChanged)

            faceList = self.faceList
            self.reProcessFaces(slopedPlanes, faceList)
            pyFaceListNew = self.Pyth

        else:
            # print('B ', self.OnChanged)

            face = Part.makeFace(shape.Wires, slopedPlanes.FaceMaker)
            fList = face.Faces
            faceList, pyFaceListNew = self.processFaces(slopedPlanes, fList)
            self.faceList = faceList
            self.Pyth = pyFaceListNew

        # print('pyFaceListNew ', pyFaceListNew)

        self.OnChanged = False
        self.State = False

        # elaborates a list of planes for every face

        figList =\
            self.listPlanes(slopedPlanes, pyFaceListNew, faceList, placement)

        endShape = Part.makeShell(figList)

        if slopedPlanes.Group:
            # print('Group')
            endShape = self.groupping(slopedPlanes, endShape)

        if slopedPlanes.Thickness:
            # print('Thickness')
            endShape = self.fattening(slopedPlanes, faceList,
                                      endShape, placement)

        if not slopedPlanes.Complement:
            endShape.complement()

        # endShape.removeInternalWires(True)

        if slopedPlanes.Solid:
            endShape = Part.makeSolid(endShape)

        slopedPlanes.Shape = endShape

    def processFaces(self, slopedPlanes, fList, thickness=False):

        ''''''

        # print('processFaces')

        # gathers the exterior wires. Lower Left criteria

        coordinatesOuterOrdered, geomOuterOrdered, faceList =\
            self.gatherExteriorWires(fList)
        # print('outer geom ', geomOuterOrdered)

        slope = slopedPlanes.Slope.Value
        try:
            slopeList = self.slopeList
            # print('a')
        except AttributeError:
            # print('b')
            slopeList = []
        # print('slopeList ', slopeList)
        slopeListCopy = slopeList[:]

        angleList = []

        pyFaceListOld = self.Pyth
        pyFaceListNew = []
        numFace = -1
        for face in faceList:
            numFace += 1
            # print('######### numFace ', numFace)

            _Py.face = face

            # elaborates complementary python objects of a face

            # TODO mono

            coordinates = coordinatesOuterOrdered[numFace]
            for pyFace in pyFaceListOld:
                oldCoord = pyFace.wires[0].coordinates
                if oldCoord[0] == coordinates[0]:
                    pyFaceListNew.append(pyFace)
                    pyFace.numFace = numFace
                    break
            else:
                pyFace = _PyFace(numFace)
                pyFaceListNew.append(pyFace)
            _Py.pyFace = pyFace

            if thickness:
                size = pyFaceListOld[numFace].size
            else:
                size = face.BoundBox.DiagonalLength
            pyFace.size = size

            fOverhang = slopedPlanes.FactorOverhang * size
            # print(size, fOverhang)

            # gathers the interior wires. Upper Left criteria

            coordinatesInnerOrdered, geomInnerOrdered, wireList =\
                self.gatherInteriorWires(face.Wires[1:])
            # print('inner geom ', geomInnerOrdered)

            wireList.insert(0, face.OuterWire)

            gList = [geomOuterOrdered[numFace]]
            gList.extend(geomInnerOrdered)
            # print('gList', gList)

            coordinates = [coordinates]
            coordinates.extend(coordinatesInnerOrdered)

            pyWireListOld = pyFace.wires
            pyWireListNew = []
            geomShapeFace = []
            numWire = -1
            for wire, geomWire in zip(wireList, gList):
                numWire += 1
                # print('###### numWire ', numWire)
                # TODO change to new topologic name
                coo = coordinates[numWire]
                # print(coo)
                for pyWire in pyWireListOld:
                    oldCoo = pyWire.coordinates
                    # print(oldCoo)
                    if oldCoo[0] == coo[0]:
                        # print('a')
                        if oldCoo != coo:
                            # print('b')
                            pyFace.reset = True
                            if len(oldCoo) != len(coo):
                                # print('c')
                                pyWire.reset = True
                        pyWireListNew.append(pyWire)
                        pyWire.numWire = numWire
                        break
                else:
                    # print('d')
                    pyWire = _PyWire(numWire)
                    pyWireListNew.append(pyWire)
                    pyFace.reset = True
                pyWire.coordinates = coo

                pyPlaneListOld = pyWire.planes
                pyPlaneListNew = []
                geomShapeWire = []
                numGeom = -1
                for geom in geomWire:
                    numGeom += 1
                    # print('### numGeom ', numGeom)

                    # unificar denominaciones con task panel ang angle slope ...

                    try:
                        ang = slopeListCopy.pop(0)
                        if isinstance(ang, float):
                            try:
                                ang = float(ang)
                                if ang != slope:
                                    pyWire.mono = False
                                    pyFace.mono = False
                            except ValueError:
                                ang = slope
                    except IndexError:
                        ang = slope

                    try:
                        pyPlane = pyPlaneListOld[numGeom]
                        pyPlaneListNew.append(pyPlane)
                        pyPlane.numGeom = numGeom
                        # print('1')

                        if pyWire.reset:
                            # print('11')

                            pyPlane.angle = ang
                            pyPlane.rightWidth = size
                            pyPlane.leftWidth = size
                            pyPlane.length = 2 * size
                            pyPlane.overhang = 0
                            pyPlane.sweepCurve = None

                        if pyFace.reset:
                            # print('111')

                            pyPlane.rear = []
                            pyPlane.secondRear = []
                            pyPlane.under = []
                            pyPlane.seed = []
                            pyPlane.seedShape = None
                            pyPlane.rango = []
                            pyPlane.aligned = False
                            pyPlane.arrow = False
                            pyPlane.choped = False
                            pyPlane.virtuals = []
                            pyPlane.reflexed = False
                            pyPlane.fronted = False

                            pyPlane.rightWidth =\
                                slopedPlanes.FactorWidth * size
                            pyPlane.leftWidth =\
                                slopedPlanes.FactorWidth * size
                            pyPlane.length =\
                                slopedPlanes.FactorLength * size

                            angle = pyPlane.angle
                            if isinstance(angle, list):
                                angle = self.selectPlane(angle[0],
                                                         angle[1]).angle
                                pyPlane.angle = angle

                            pyPlane.overhang = fOverhang / sin(radians(angle))

                            pyPlane.lineInto = None
                            pyPlane.cross = False

                            pyPlane.reflexedList = []

                    except IndexError:
                        # print('2')

                        pyPlane = _PyPlane(numWire, numGeom, ang)
                        pyPlaneListNew.append(pyPlane)
                        if thickness and isinstance(ang, float):
                            pyPlane.overhang = fOverhang / sin(radians(ang))

                    # print(pyPlane.overhang)

                    angleList.append(pyPlane.angle)

                    pyPlane.geom = geom

                    pyEdge = SlopedPlanesPyEdge.makePyEdge(pyPlane)
                    pyPlane.edge = pyEdge

                    gS = geom.toShape()
                    pyPlane.geomShape = gS
                    pyPlane.geomAligned = gS
                    geomShapeWire.append(gS)

                    pyPlane.control = [numGeom]
                    pyPlane.solved = False
                    pyPlane.reallySolved = False

                    pyPlane.alignedList = []
                    pyPlane.chopedList = []
                    pyPlane.frontedList = []
                    pyPlane.rearedList = []

                pyWire.planes = pyPlaneListNew

                pyWire.shapeGeom = geomShapeWire
                pyWire.wire = wire
                geomShapeFace.extend(geomShapeWire)

            pyFace.shapeGeom = geomShapeFace
            pyFace.wires = pyWireListNew

            pyFace.faceManager()

        self.slopeList = angleList

        return faceList, pyFaceListNew

    def reProcessFaces(self, slopedPlanes, faceList):

        ''''''

        # print('reProcessFaces')

        angleList = []
        # TODO mono
        numFace = -1
        for face in faceList:
            numFace += 1
            # print('######### numFace ', numFace)

            _Py.face = face

            pyFace = self.Pyth[numFace]
            _Py.pyFace = pyFace
            pyFace.reset = False
            # print(pyFace.mono)
            for pyWire in pyFace.wires:
                # print(pyWire.mono)
                pyWire.reset = False
                pyWire.wire = Part.Wire(pyWire.shapeGeom)

                for pyPlane in pyWire.planes:
                    pyPlane.geomAligned = pyPlane.geomShape
                    pyPlane.control = [pyPlane.numGeom]
                    pyPlane.solved = False
                    pyPlane.reallySolved = False

                    pyPlane.alignedList = []
                    pyPlane.chopedList = []
                    pyPlane.frontedList = []
                    pyPlane.rearedList = []

                    angleList.append(pyPlane.angle)

                    # print(pyPlane.overhang)

            pyFace.faceManager()

        self.slopeList = angleList

    def listPlanes(self, slopedPlanes, pyFaceListNew, faceList, placement):

        ''''''

        figList = []
        for pyFace in pyFaceListNew:
            # print(pyFace.numFace)
            numFace = pyFace.numFace
            secondaries = []
            planeFaceList = []
            originList = []
            wireList = []
            for pyWire in pyFace.wires:
                # print(pyWire.numWire)
                numWire = pyWire.numWire
                planeWireList = []
                for pyPlane in pyWire.planes:
                    # print(pyPlane.numGeom)
                    numAngle = pyPlane.numGeom
                    angle = pyPlane.angle
                    # print('angle ', angle)

                    if pyPlane.length:

                        if [numWire, numAngle] not in originList:

                            if isinstance(angle, float):
                                # print('a')

                                plane = pyPlane.shape

                                if isinstance(plane, Part.Compound):
                                    # print('a1')
                                    planeWireList.append(plane.Faces[0])
                                    secondaries.extend(plane.Faces[1:])

                                else:
                                    # print('a2')
                                    planeWireList.append(plane)

                                originList.append([numWire, numAngle])

                            else:
                                if angle not in originList:
                                    # print('b')

                                    pyPl =\
                                        pyFace.selectPlane(angle[0], angle[1],
                                                           pyFace)
                                    planeWireList.append(pyPl.shape)

                                    originList.append(angle)

                    # print('originList ', originList)

                if slopedPlanes.Up:
                    upPlaneCopy = _Py.upList[numFace].copy()
                    cut = upPlaneCopy.cut(planeWireList, _Py.tolerance)
                    edgeList = cut.Edges[4:]
                    wire = Part.Wire(edgeList)
                    wireList.append(wire)

                planeFaceList.extend(planeWireList)

            planeFaceList.extend(secondaries)

            if slopedPlanes.Up:
                # print('Up')
                faceMaker = slopedPlanes.FaceMaker
                upFace = Part.makeFace(wireList, faceMaker)

                planeFaceList.append(upFace)

            if not slopedPlanes.Mirror:
                if slopedPlanes.Down:
                    # print('Down')
                    face = faceList[numFace].copy()
                    planeFaceList.append(face)

            else:
                # print('mirror')
                shell = Part.makeShell(planeFaceList)
                mirror = shell.mirror(FreeCAD.Vector(0, 0, 0),
                                      FreeCAD.Vector(0, 0, -1))
                planeFaceList.extend(mirror.Faces)

            for plane in planeFaceList:
                plane.Placement = placement.multiply(plane.Placement)

            figList.extend(planeFaceList)

        return figList

    def groupping(self, slopedPlanes, endShape):

        ''''''

        # limitar a figuras con una sola face: REMOVESPLITTER ?

        tolerance = slopedPlanes.Tolerance

        for obj in slopedPlanes.Group:
            if hasattr(obj, "Proxy"):
                if obj.Proxy.Type == "SlopedPlanes":
                    childShape = obj.Shape.copy()

                    common = endShape.common([childShape], tolerance)

                    if common.Area:

                        endShape = endShape.cut([common], tolerance)
                        childShape = childShape.cut([common], tolerance)

                    shell = Part.Shell(endShape.Faces + childShape.Faces)
                    shell = shell.removeSplitter()
                    endShape = shell

        return endShape

    def fattening(self, slopedPlanes, faceList, endShape, placement):

        ''''''

        # print('fattening ')

        thicknessDirection = slopedPlanes.ThicknessDirection
        value = slopedPlanes.Thickness.Value

        pyth = slopedPlanes.Proxy.Pyth

        if thicknessDirection == 'Vertical':
            # print('Vertical')

            normal = self.faceNormal(faceList[0])
            if slopedPlanes.Reverse:
                normal = normal * -1

            shellList = []
            vv = value * normal
            for ss in endShape.Shells:
                ss = ss.extrude(vv)
                shell = Part.Shell(ss.Faces)
                shellList.append(shell)

            if len(shellList) > 1:
                endShape = Part.Compound(shellList)
            else:
                endShape = shellList[0]

            # cuando convierto a sólido da un error de geometría

        else:
            # print('No Vertical')

            angle = slopedPlanes.Slope.Value
            height = value * sin(radians(angle))

            # print(angle, height, value)

            if thicknessDirection == 'Horizontal':

                ang = angle
                hei = 0
                val = value

            elif thicknessDirection == 'Slope':

                ang = 90.0 - angle
                hei = value * sin(radians(ang))
                val = value * cos(radians(ang))

            elif thicknessDirection == 'ThicknessSlope':

                ang = slopedPlanes.ThicknessSlope.Value
                hei = value * sin(radians(ang))
                val = value * cos(radians(ang))

            elif thicknessDirection == 'Normal':

                ang = 45.0
                hei = value * sin(radians(ang))
                val = None

            # print(ang, hei, val)

            face = Part.Compound(faceList)

            if thicknessDirection == 'Normal':

                bigFaceList = []
                for pyFace, face in zip(pyth, faceList):

                    bFace = self.normalWires(pyFace, face, hei, angle)
                    bigFaceList.append(bFace)

                if len(bigFaceList) == 1:
                    bigFace = bigFaceList[0]
                else:
                    bigFace = Part.Compound(bigFaceList)

            else:

                bigFace =\
                    face.makeOffset2D(offset=val, join=2, fill=False,
                                      openResult=False, intersection=False)
                bigFace.translate(V(0, 0, hei))

            fList, pyFLNew =\
                self.processFaces(slopedPlanes, bigFace.Faces,
                                  thickness=True)

            figList =\
                self.listPlanes(slopedPlanes, pyFLNew, fList, placement)

            secondShape = Part.makeShell(figList)

            shellList = []
            factorOverhang = slopedPlanes.FactorOverhang

            if factorOverhang:

                for ss, SS, face, pyFace in zip(endShape.Shells,
                                                secondShape.Shells,
                                                faceList, pyth):

                    ff, FF = self.overhangWires(endShape, secondShape, pyFace)

                    baseFaces = ss.Faces + SS.Faces
                    for ww, WW in zip(ff.Wires, FF.Wires):
                        base = Part.makeLoft([ww, WW])
                        for bf in base.Faces:
                            bf.Placement = bf.Placement.multiply(placement)
                            baseFaces.append(bf)
                    shell = Part.Shell(baseFaces)
                    # shell = Part.Compound(baseFaces)
                    shell.Placement = placement
                    shellList.append(shell)

            else:

                for ss, SS, ff, FF in zip(endShape.Shells, secondShape.Shells,
                                          face.Faces, bigFace.Faces):
                    baseFaces = ss.Faces + SS.Faces
                    for ww, WW in zip(ff.Wires, FF.Wires):
                        base = Part.makeLoft([ww, WW])
                        for bf in base.Faces:
                            bf.Placement = bf.Placement.multiply(placement)
                            baseFaces.append(bf)
                    shell = Part.Shell(baseFaces)
                    # shell = Part.Compound(baseFaces)
                    shellList.append(shell)

            # print(shellList)
            if len(shellList) > 1:
                endShape = Part.Compound(shellList)
            else:
                endShape = shellList[0]

        return endShape

    def overhangWires(self, endShape, secondShape, pyFace):

        ''''''

        size = pyFace.size
        ss = 10 * size
        cc = -1 * 5 * size # TODO habría que centrarlo en la primera coordenada

        # print(endShape.BoundBox.ZMin)
        endPlane = Part.makePlane(ss, ss, V(cc, cc, endShape.BoundBox.ZMin))
        cut = endPlane.cut(endShape, _Py.tolerance)
        ff = Part.makeFace(cut.Wires[1:], 'Part::FaceMakerBullseye')

        # print(secondShape.BoundBox.ZMin)
        secondPlane =\
            Part.makePlane(ss, ss, V(cc, cc, secondShape.BoundBox.ZMin))
        cut = secondPlane.cut(secondShape, _Py.tolerance)
        FF = Part.makeFace(cut.Wires[1:], 'Part::FaceMakerBullseye')

        return ff, FF

    def normalWires(self, pyFace, face, height, angle):

        ''''''

        if pyFace.mono:

            run = height / tan(radians(angle))
            # print(height, run)

            ff =\
                face.makeOffset2D(offset=run, join=2, fill=False,
                                  openResult=False, intersection=False)

            ff.translate(V(0, 0, height))

            return ff

        size = pyFace.size
        tolerance = _Py.tolerance
        wireList = []

        for pyWire in pyFace.wires:

            # TODO pyWire.mono

            geomShapeWire = pyWire.shapeGeom
            eeList, ttList = [], []

            for pyPlane, geomShape in zip(pyWire.planes, geomShapeWire):
                ang = pyPlane.angle
                if isinstance(ang, list):
                    pyPl = pyFace.selectPlane(ang[0], ang[1], pyFace)
                    ang = pyPl.angle
                    sh = pyPl.shape.Faces[0]
                else:
                    sh = pyPlane.shape.Faces[0]

                length = height / cos(radians(ang))
                extrDirect = sh.normalAt(0, 0)
                # print(angle, extrDirect, length)

                geomShape.translate(-1 * length * extrDirect)

                ll = 0.49 * geomShape.Length

                geomS = Part.LineSegment(geomShape.firstVertex(True).Point,
                                         geomShape.lastVertex(True).Point)

                geomS.setParameterRange(geomS.FirstParameter + ll,
                                        geomS.LastParameter - ll)

                ttList.append(geomS.toShape())

                gS = Part.LineSegment(geomShape.firstVertex(True).Point,
                                      geomShape.lastVertex(True).Point)

                gS.setParameterRange(gS.FirstParameter - size,
                                     gS.LastParameter + size)

                eeList.append(gS.toShape())

            # print(eeList, ttList)

            edgeList = []
            nn = -1
            for ee, tt in zip(eeList, ttList):

                prior = eeList[nn]
                try:
                    later = eeList[nn + 2]
                except IndexError:
                    later = eeList[0]
                ee = ee.cut([prior, later], tolerance)
                nn += 1

                for ll in ee.Edges:
                    section = ll.section(tt)
                    if section.Edges:
                        edgeList.append(ll)
                        break

            # print(edgeList)
            self.ed = Part.Compound(edgeList)
            self.et = Part.Compound(ttList)
            self.ee = Part.Compound(eeList)

            ww = Part.Wire(edgeList)
            wireList.append(ww)

        baseFace = Part.makeFace(wireList, 'Part::FaceMakerBullseye')

        return baseFace

    def onChanged(self, slopedPlanes, prop):

        '''onChanged(self, slopedPlanes, prop)'''

        # print('onChanged ', prop, ' self.state ', self.State)

        if self.State:

            return

        if prop in ['Shape', 'Visibility']:

            self.OnChanged = False
            return

        elif prop == "Slope":

            slope = slopedPlanes.Slope
            value = slope.Value
            prop = "angle"
            self.overWritePyProp(prop, value)
            self.slopeList = []
            slopedPlanes.FactorOverhang = 0

        elif prop == "FactorLength":

            length = slopedPlanes.FactorLength
            value = length
            prop = "length"
            self.overWritePyProp(prop, value)

        elif prop == "FactorWidth":

            width = slopedPlanes.FactorWidth
            value = width
            prop = "width"
            self.overWritePyProp(prop, value)

        elif prop == "FactorOverhang":

            overhang = slopedPlanes.FactorOverhang
            value = overhang
            prop = "overhang"
            self.overWritePyProp(prop, value)

        elif prop == "Reverse":

            value = None
            prop = "seedShape"
            self.overWritePyProp(prop, value)

        elif prop == "SweepCurves":

            curvesList = slopedPlanes.SweepCurves

            for pyFace in self.Pyth:
                for pyWire in pyFace.wires:
                    for pyPlane in pyWire.planes:
                        sw = pyPlane.sweepCurve
                        if sw:
                            if sw not in curvesList:
                                pyPlane.sweepCurve = None

        self.OnChanged = True

    def overWritePyProp(self, prop, value):

        '''overWritePyProp(self, prop, value)'''

        # print('overWritePyProp', prop)

        for pyFace in self.Pyth:

            _Py.pyFace = pyFace

            if prop in ["length", "width", "overhang"]:
                size = pyFace.size
                newValue = value * size
            else:
                newValue = value
                if prop == "angle":
                    pyFace.mono = True

            if prop == "width":

                for pyWire in pyFace.wires:
                    for pyPlane in pyWire.planes:
                        setattr(pyPlane, "leftWidth", newValue)
                        setattr(pyPlane, "rightWidth", newValue)

            elif prop == "overhang":

                for pyWire in pyFace.wires:
                    for pyPlane in pyWire.planes:

                        angle = pyPlane.angle
                        if isinstance(angle, list):
                            angle = pyFace.selectPlane(angle[0], angle[1],
                                                       pyFace).angle

                        factorOverhang = sin(radians(angle))
                        length = newValue / factorOverhang
                        # print(pyPlane.numGeom, angle, length, newValue)

                        if length > size:
                            # print('size ', (size, factorOverhang))
                            setattr(pyPlane, "overhang", size)
                            _Py.slopedPlanes.FactorOverhang = factorOverhang
                            return

                        setattr(pyPlane, "overhang", length)

            elif prop == "angle":

                pyFace.mono = True
                for pyWire in pyFace.wires:
                    pyWire.mono = True
                    for pyPlane in pyWire.planes:
                        setattr(pyPlane, prop, newValue)

            else:

                for pyWire in pyFace.wires:
                    for pyPlane in pyWire.planes:
                        setattr(pyPlane, prop, newValue)

    def onDocumentRestored(self, slopedPlanes):

        ''''''

        # print('onDocumentRestored')

        _Py.slopedPlanes = slopedPlanes

    def __getstate__(self):

        '''__getstate__(self)'''

        state = dict()

        state['Type'] = self.Type

        pyth = []
        numFace = -1
        for pyFace in self.Pyth:
            numFace += 1
            dct = pyFace.__dict__.copy()
            wires, alignments = pyFace.__getstate__()
            dct['_shapeGeom'] = []
            dct['_wires'] = wires
            dct['_alignments'] = alignments
            pyth.append(dct)
        state['Pyth'] = pyth

        # print('state ', state)

        return state

    def __setstate__(self, state):

        '''__setstate__(self, state)'''

        # print('__setstate__')

        self.Type = state['Type']

        pyth = []
        numFace = -1
        for dct in state['Pyth']:
            numFace += 1
            pyFace = _PyFace(numFace)
            _Py.pyFace = pyFace

            wires = dct['_wires']
            alignments = dct['_alignments']

            wires, alignments =\
                pyFace.__setstate__(wires, alignments)

            dct['_wires'] = wires
            dct['_alignments'] = alignments
            dct['_shapeGeom'] = []
            pyFace.__dict__ = dct
            pyFace.reset = True
            pyth.append(pyFace)
        self.Pyth = pyth

        self.faceList = []

        self.State = True

        self.OnChanged = False


class _ViewProvider_SlopedPlanes():

    ''''''

    def __init__(self, vobj):

        '''__init__(self, vobj)'''

        vobj.addExtension("Gui::ViewProviderGroupExtensionPython", self)
        vobj.Proxy = self

    def getIcon(self):

        '''getIcon(self)'''

        return path.dirname(__file__) + "/SlopedPlanes_Tree.svg"

    def getDefaultDisplayMode(self):

        '''getDefaultDisplayMode(self)'''

        return "FlatLines"

    def __getstate__(self):

        '''__getstate__(self)'''

        return None

    def __setstate__(self, state):

        '''__setstate__(self, state)'''

        return None

    def attach(self, vobj):

        '''attach(self, vobj)'''

        # print('attach')

        self.Object = vobj.Object

    def claimChildren(self):

        '''claimChildren(self)'''

        # print('claimChildren')

        obj = self.Object
        group = obj.Group
        for oo in group:
            if hasattr(oo, 'Proxy'):
                if oo.Proxy.Type == 'SlopedPlanes':
                    oo.ViewObject.Visibility = False
        return [obj.Base] + group

    def unsetEdit(self, vobj, mode):

        '''unsetEdit(self, vobj, mode)'''

        FreeCADGui.Control.closeDialog()
        return

    def setEdit(self, vobj, mode=0):

        '''setEdit(self, vobj, mode=0)'''

        taskd = _TaskPanel_SlopedPlanes(self.Object)
        self.task = taskd
        taskd.update()
        FreeCADGui.Control.showDialog(taskd)
        return True
