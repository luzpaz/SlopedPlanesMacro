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
from math import radians, sin, cos
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

    return slopedPlanes


class _SlopedPlanes(_Py):

    '''The Class of the FreeCAD scripted object SlopedPlanes.
    Requieres a sketch or DWire as base. The base must support the FaceMaker.
    The angles numeration corresponds to the SlopedPlanes shape faces.'''

    def __init__(self, slopedPlanes, slope=45.0, slopeList=[]):

        '''__init__(self, slopedPlanes)
        Initializes the properties of the SlopedPlanes object and its Proxy.
        The Proxy stores:

        - four flags
            Type: object recognition
            State: jumps onChanged at the loading file
            OnChanged: faster execute from property and task panels (~7%)
            Serialize: Slower loading file (~15%) and faster execute (~7%)

        - three lists:
            Pyth: the complementary python objects
            faceList: faces produced by the FaceMaker over the base
            slopeList: list of angles'''

        doc = "The sketch or Dwire in which the SlopedPlanes is based"

        slopedPlanes.addProperty("App::PropertyLink", "Base",
                                 "Base", doc)

        doc = "Reverses the angles of the SlopedPlanes"

        slopedPlanes.addProperty("App::PropertyBool", "Reverse",
                                 "SlopedPlanes", doc)

        doc = "Gives a thickness to the SlopedPlanes"

        slopedPlanes.addProperty("App::PropertyLength", "Thickness",
                                 "SlopedPlanes", doc)

        doc = "Thickness direction"

        slopedPlanes.addProperty("App::PropertyEnumeration", "ThicknessDirection",
                                 "SlopedPlanes", doc)

        doc = ('Applies over all planes overhang height,\n'
               'multiplied by the diagonal \n'
               'length of the SlopedPlanes base.\n'
               'It \'s limited to 1 or even less')

        slopedPlanes.addProperty("App::PropertyFloatConstraint", "FactorOverhang",
                                 "SlopedPlanes", doc)

        doc = ('Applies over all planes angles.\n'
               'To cero the SlopedPlanes hasn\'t shape')

        slopedPlanes.addProperty("App::PropertyAngle", "Slope",
                                 "SlopedPlanes", doc)

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

        doc = "Available curves to sweep"

        slopedPlanes.addProperty("App::PropertyLinkList", "SweepCurves",
                                 "SlopedPlanes", doc)

        slopedPlanes.addExtension("App::GroupExtensionPython", self)

        doc = "Computes de complement of the orientation of the SlopedPlanes"

        slopedPlanes.addProperty("App::PropertyBool", "Complement",
                                 "SlopedPlanesPart", doc)

        doc = "Mirrors the SlopedPlanes with respect its base"

        slopedPlanes.addProperty("App::PropertyBool", "Mirror",
                                 "SlopedPlanesPart", doc)

        doc = "Creates a solid out of the SlopedPlanes shells"

        slopedPlanes.addProperty("App::PropertyBool", "Solid",
                                 "SlopedPlanesPart", doc)

        doc = "Gives a plane on SlopedPlanes base"

        slopedPlanes.addProperty("App::PropertyBool", "Down",
                                 "SlopedPlanesPart", doc)

        doc = "Gives a plane on top of the SlopedPlanes"

        slopedPlanes.addProperty("App::PropertyLength", "Up",
                                 "SlopedPlanesPart", doc)

        doc = "Tolerance value applied in boolean operation (Fuzzy)"

        slopedPlanes.addProperty("App::PropertyPrecision", "Tolerance",
                                 "SlopedPlanesPart", doc)

        doc = "FaceMaker"

        slopedPlanes.addProperty("App::PropertyEnumeration", "FaceMaker",
                                 "SlopedPlanesPart", doc)

        self.State = True

        try:
            ang = float(slope)
        except ValueError:
            ang = 45.0

        slopedPlanes.Slope = ang

        slopedPlanes.FactorWidth = 1
        slopedPlanes.FactorLength = 2
        slopedPlanes.FactorOverhang = (0, 0, 1, 0.01)
        slopedPlanes.Up = 0
        slopedPlanes.FaceMaker = ["Part::FaceMakerBullseye",
                                  "Part::FaceMakerSimple",
                                  "Part::FaceMakerCheese"]
        slopedPlanes.ThicknessDirection = ["Vertical",
                                           "Horizontal",
                                           "Normal"]
        slopedPlanes.Tolerance = (1e-5, 1e-7, 1, 1e-7)

        slopedPlanes.Proxy = self

        self.Pyth = []
        self.faceList = []
        self.slopeList = slopeList

        self.Type = "SlopedPlanes"

        self.Serialize = True
        self.OnChanged = True

    def execute(self, slopedPlanes):

        '''execute(self, slopedPlanes)
        Builds the shape of the slopedPlanes object.'''

        # print('execute')

        sketch = slopedPlanes.Base
        shape = sketch.Shape.copy()
        placement = sketch.Placement
        shape.Placement = FreeCAD.Placement()

        self.declareSlopedPlanes(slopedPlanes)

        tolerance = slopedPlanes.Tolerance
        faceMaker = slopedPlanes.FaceMaker

        onChanged = self.OnChanged
        if not self.faceList:
            # print('hasn't faceList')
            onChanged = True

        if onChanged:
            # print('A')

            face = Part.makeFace(shape.Wires, faceMaker)
            fList = face.Faces

            # gathers the exterior wires. Lower Left criteria

            coordinatesOuterOrdered, geomOuterOrdered, faceList =\
                self.gatherExteriorWires(fList)
            # print('outer geom ', geomOuterOrdered)

            self.faceList = faceList

        else:
            # print('B')

            faceList = self.faceList

        # procedees face by face and stores them into the Proxy

        if onChanged:
            # print('AA')

            pyFaceListNew =\
                self.processFaces(slopedPlanes, faceList,
                                  coordinatesOuterOrdered, geomOuterOrdered)
            self.Pyth = pyFaceListNew

        else:
            # print('BB')

            self.reProcessFaces(slopedPlanes, faceList)
            pyFaceListNew = self.Pyth

        # print('pyFaceListNew ', pyFaceListNew)

        self.OnChanged = True

        # elaborates a list of planes for every face

        figList =\
            self.listPlanes(slopedPlanes, pyFaceListNew, faceList, placement)

        endShape = Part.makeShell(figList)

        if slopedPlanes.Group:
            endShape = self.groupping(slopedPlanes, endShape, tolerance)

        if not slopedPlanes.Complement:
            endShape.complement()

        if slopedPlanes.Thickness:
            endShape = self.fattening(slopedPlanes, faceList, endShape, placement)

        if slopedPlanes.Solid:
            endShape = Part.makeSolid(endShape)

        # endShape.removeInternalWires(True)

        slopedPlanes.Shape = endShape

    def processFaces(self, slopedPlanes, faceList,
                     coordinatesOuterOrdered, geomOuterOrdered):

        ''''''

        pyFaceListOld = self.Pyth
        pyFaceListNew = []
        numFace = -1
        for face in faceList:
            numFace += 1
            # print('######### numFace ', numFace)

            _Py.face = face

            slope = slopedPlanes.Slope.Value

            try:
                slopeList = self.slopeList
                mono = False
                # print('a')
            except AttributeError:
                # print('b')
                mono = True
                slopeList = []

            # print('slopeList ', slopeList)

            slopeListCopy = slopeList[:]

            # elaborates complementary python objects of a face

            coordinates = coordinatesOuterOrdered[numFace]
            for pyFace in pyFaceListOld:
                oldCoord = pyFace.wires[0].coordinates
                if oldCoord[0] == coordinates[0]:
                    pyFaceListNew.append(pyFace)
                    pyFace.numFace = numFace
                    break
            else:
                pyFace = _PyFace(numFace, mono)
                pyFaceListNew.append(pyFace)

            _Py.pyFace = pyFace

            size = face.BoundBox.DiagonalLength
            pyFace.size = size

            # gathers the interior wires. Upper Left criteria

            wList = face.Wires[1:]

            coordinatesInnerOrdered, geomInnerOrdered, wireList =\
                self.gatherInteriorWires(wList)

            # print('inner geom ', geomInnerOrdered)

            wireList.insert(0, face.OuterWire)

            gList = [geomOuterOrdered[numFace]]
            gList.extend(geomInnerOrdered)
            # print('gList', gList)

            coordinates = [coordinates]
            coordinates.extend(coordinatesInnerOrdered)

            if not self.Serialize:
                pyFace.reset = True

            pyWireListOld = pyFace.wires
            pyWireListNew = []
            geomShapeFace = []
            numWire = -1
            for wire, geomWire in zip(wireList, gList):
                numWire += 1
                # print('###### numWire ', numWire)
                coo = coordinates[numWire]
                for pyWire in pyWireListOld:
                    oldCoo = pyWire.coordinates
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
                    pyWire = _PyWire(numWire, mono)
                    pyWireListNew.append(pyWire)
                    pyWire.reset = True
                    pyFace.reset = True
                pyWire.coordinates = coo

                pyPlaneListOld = pyWire.planes
                pyPlaneListNew = []
                geomShapeWire = []
                numGeom = -1
                for geom in geomWire:
                    numGeom += 1
                    # print('### numGeom ', numGeom)

                    try:
                        ang = slopeListCopy.pop(0)
                        try:
                            ang = float(ang)
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
                            pyPlane.overhang =\
                                slopedPlanes.FactorOverhang * size

                            angle = pyPlane.angle
                            if isinstance(angle, list):
                                angle = self.selectPlane(angle[0],
                                                         angle[1]).angle
                                pyPlane.angle = angle

                            pyPlane.lineInto = None
                            pyPlane.cross = False

                            pyPlane.reflexedList = []

                    except IndexError:
                        # print('2')

                        pyPlane = _PyPlane(numWire, numGeom, ang)

                        pyPlaneListNew.append(pyPlane)

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

        return pyFaceListNew

    def reProcessFaces(self, slopedPlanes, faceList):

        ''''''

        numFace = -1
        for face in faceList:
            numFace += 1
            # print('######### numFace ', numFace)

            _Py.face = face

            pyFace = self.Pyth[numFace]
            _Py.pyFace = pyFace
            # print(pyFace.mono)
            for pyWire in pyFace.wires:
                # print(pyWire.mono)
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

            pyFace.faceManager()

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

    def groupping(self, slopedPlanes, endShape, tolerance):

        ''''''

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

        thicknessDirection = slopedPlanes.ThicknessDirection
        value = slopedPlanes.Thickness.Value

        if thicknessDirection == 'Vertical':

            normal = self.faceNormal(faceList[0])
            if slopedPlanes.Reverse:
                normal = normal * -1
            endShape = endShape.extrude(value * normal)

        else:

            face = Part.Compound(faceList)

            if thicknessDirection == 'Normal':

                ang = slopedPlanes.Slope.Value
                height = value * sin(radians(ang))
                value = value * cos(radians(ang))
                # print(ang, height, value)

            bigFace =\
                face.makeOffset2D(offset=value, join=2, fill=False,
                                  openResult=False, intersection=True)

            coordOutOrd, geomOutOrd, fList =\
                self.gatherExteriorWires(bigFace.Faces)

            onChanged = True

            pyFLNew =\
                self.processFaces(slopedPlanes, fList, onChanged,
                                  coordOutOrd, geomOutOrd)

            figList =\
                self.listPlanes(slopedPlanes, pyFLNew, fList, placement)

            secondShape = Part.makeShell(figList)
            secondShape = secondShape.removeSplitter()

            if thicknessDirection == 'Normal':

                secondShape.translate(V(0, 0, height))

                bigFace.translate(V(0, 0, height))

            outer = face.Wires[0]
            bigOuter = bigFace.Wires[0]
            base =\
                Part.makeLoft([outer, bigOuter])
            # hay que hacerlo también para los alambres interiores
            # si hay overhang hay que desplazarlo para cerrar malla

            shell =\
                Part.Shell(endShape.Faces + secondShape.Faces + base.Faces)
            endShape = shell

        return endShape

    def onChanged(self, slopedPlanes, prop):

        '''onChanged(self, slopedPlanes, prop)'''

        # print('onChanged ', prop)

        if self.State:

            return

        if prop == "Slope":

            slope = slopedPlanes.Slope
            value = slope.Value
            prop = "angle"
            self.overWritePyProp(prop, value)
            self.slopeList = []

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
                    _Py.slopedPlanes.FactorOverhang = 0

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

            else:

                for pyWire in pyFace.wires:
                    if prop == "angle":
                        pyWire.mono = True
                    for pyPlane in pyWire.planes:
                        setattr(pyPlane, prop, newValue)

        self.OnChanged = False

    def onDocumentRestored(self, slopedPlanes):

        ''''''

        # print('onDocumentRestored')

        tolerance = slopedPlanes.Tolerance
        slopedPlanes.Tolerance = (tolerance, 1e-7, 1, 1e-7)

        factorOverhang = slopedPlanes.FactorOverhang
        slopedPlanes.FactorOverhang = (factorOverhang, 0, 1, 0.01)

    def __getstate__(self):

        '''__getstate__(self)'''

        state = dict()

        state['Type'] = self.Type

        serialize = self.Serialize
        state['Serialize'] = serialize

        faceList = self.faceList

        pyth = []
        numFace = -1
        for pyFace in self.Pyth:
            numFace += 1
            dct = pyFace.__dict__.copy()
            wires, alignments, serials = pyFace.__getstate__(serialize)
            dct['_shapeGeom'] = []
            dct['_wires'] = wires
            dct['_alignments'] = alignments
            if serialize:
                face = faceList[numFace]
                # print('serials ', serials)
                # print('face ', face)
                serials = Part.makeCompound([face] + serials)
                dct['_serials'] = serials.exportBrepToString()
            else:
                if '_serials' in dct:
                    del dct['_serials']
            pyth.append(dct)
        state['Pyth'] = pyth

        # print('state ', state)

        return state

    def __setstate__(self, state):

        '''__setstate__(self, state)'''

        # print('__setstate__')

        self.Type = state['Type']

        serialize = state['Serialize']

        #slopedPlanes = FreeCAD.ActiveDocument.getObject('')
        #_Py

        faceList = []
        pyth = []
        numFace = -1
        for dct in state['Pyth']:
            numFace += 1
            pyFace = _PyFace(numFace)
            _Py.pyFace = pyFace

            wires = dct['_wires']
            alignments = dct['_alignments']

            if serialize:
                compound = Part.Compound([])
                compound.importBrepFromString(dct['_serials'])
                face = compound.Faces[0]
                faceList.append(face)
                compound = compound.removeShape([face])

            else:
                compound = None

            wires, alignments, geomShapeFace =\
                pyFace.__setstate__(wires, alignments, serialize, compound)

            dct['_wires'] = wires
            dct['_alignments'] = alignments
            dct['_shapeGeom'] = geomShapeFace
            pyFace.__dict__ = dct
            pyth.append(pyFace)
        self.Pyth = pyth
        self.faceList = faceList

        self.Serialize = serialize
        self.State = True

        if serialize:
            self.OnChanged = False
            # if the geometry change after loading, recompute
        else:
            self.OnChanged = True

        # self.printSerialSummary()  ROTO


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

        self.Object = vobj.Object
        obj = self.Object
        obj.Proxy.State = False

    def claimChildren(self):

        '''claimChildren(self)'''

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
