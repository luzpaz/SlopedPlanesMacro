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
from SlopedPlanesPy import _Py
from SlopedPlanesPyFace import _PyFace
from SlopedPlanesPyWire import _PyWire
from SlopedPlanesPyPlane import _PyPlane
if FreeCAD.GuiUp:
    from os import path
    import FreeCADGui
    from SlopedPlanesTaskPanel import _TaskPanel_SlopedPlanes


__title__ = "SlopedPlanes Macro"
__author__ = "Damian Caceres Moreno"
__url__ = "http://www.freecadweb.org"
__version__ = ""


def makeSlopedPlanes(sketch):

    '''makeSlopedPlanes(sketch)
    makes the SlopedPlanes object from a sketch or a DWire.'''

    if hasattr(sketch, 'Proxy'):
        if sketch.Proxy.Type != 'Wire':
            return

    elif sketch.TypeId != "Sketcher::SketchObject":
        return

    slopedPlanes =\
        FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "SlopedPlanes")

    _SlopedPlanes(slopedPlanes)
    _ViewProvider_SlopedPlanes(slopedPlanes.ViewObject)

    slopedPlanes.Base = sketch

    return slopedPlanes


class _SlopedPlanes(_Py):

    '''The Class of the FreeCAD scripted object SlopedPlanes.
    Requieres a sketch or DWire as base. The base must support the FaceMaker.
    The angles numeration corresponds to the SlopedPlanes shape faces.'''

    def __init__(self, slopedPlanes):

        '''__init__(self, slopedPlanes)
        Initializes the properties of the SlopedPlanes object and its Proxy.
        The Proxy stores:

        - four flags
            Type: object recognition
            State: jumps onChanged at the loading file
            OnChanged: faster execute from property and task panels (~7%)
            Serialize: Slower loading file (~15%) and faster execute (~7%)

        - two lists:
            Pyth: the complementary python objects
            faceList: faces produced by the FaceMaker over the base'''

        doc = "The sketch or Dwire in which the SlopedPlanes is based"

        slopedPlanes.addProperty("App::PropertyLink", "Base",
                                 "SlopedPlanes", doc)

        doc = "Computes de complement of the orientation of the SlopedPlanes"

        slopedPlanes.addProperty("App::PropertyBool", "Complement",
                                 "SlopedPlanes", doc)

        doc = "Reverses the angles of the SlopedPlanes"

        slopedPlanes.addProperty("App::PropertyBool", "Reverse",
                                 "SlopedPlanes", doc)

        doc = "Mirrors the SlopedPlanes with respect its base"

        slopedPlanes.addProperty("App::PropertyBool", "Mirror",
                                 "SlopedPlanes", doc)

        doc = "Creates a solid out of the SlopedPlanes shells"

        slopedPlanes.addProperty("App::PropertyBool", "Solid",
                                 "SlopedPlanes", doc)

        doc = "Gives a plane on SlopedPlanes base"

        slopedPlanes.addProperty("App::PropertyBool", "Down",
                                 "SlopedPlanes", doc)

        doc = "Gives a plane on top of the SlopedPlanes."

        slopedPlanes.addProperty("App::PropertyLength", "Up",
                                 "SlopedPlanes", doc)

        doc = "Gives a thickness to the SlopedPlanes."

        slopedPlanes.addProperty("App::PropertyLength", "Thickness",
                                 "SlopedPlanes", doc)

        doc = ('Applies over all planes overhang length,\n'
               'multiplied by the diagonal \n'
               'length of the SlopedPlanes base.\n'
               'It \'s limited to 1')

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

        doc = "Tolerance"

        slopedPlanes.addProperty("App::PropertyPrecision", "Tolerance",
                                 "SlopedPlanes", doc)

        doc = "FaceMaker"

        slopedPlanes.addProperty("App::PropertyEnumeration", "FaceMaker",
                                 "SlopedPlanes", doc)

        doc = "Available curves to sweep"

        slopedPlanes.addProperty("App::PropertyLinkList", "SweepCurves",
                                 "SlopedPlanes", doc)

        slopedPlanes.addExtension("App::GroupExtensionPython", self)

        self.State = True

        slopedPlanes.Slope = 45.0
        slopedPlanes.FactorWidth = 1    # 1.2 también habría que cambiar en doPlane (line 747)
        slopedPlanes.FactorLength = 2
        slopedPlanes.FactorOverhang = (0, 0, 1, 0.01)   # no tiene persistencia
        slopedPlanes.Up = 0
        slopedPlanes.FaceMaker = ["Part::FaceMakerBullseye",
                                  "Part::FaceMakerSimple",
                                  "Part::FaceMakerCheese"]
        slopedPlanes.Tolerance = (1e-7, 1e-7, 1, 1e-7)

        slopedPlanes.Proxy = self

        self.Pyth = []
        self.faceList = []
        self.Type = "SlopedPlanes"
        self.Serialize = True
        self.OnChanged = True

    def execute(self, slopedPlanes):

        '''execute(self, slopedPlanes)
        Builds the shape of the slopedPlanes object.'''

        sketch = slopedPlanes.Base
        shape = sketch.Shape.copy()
        placement = sketch.Placement
        shape.Placement = FreeCAD.Placement()

        _Py.slopedPlanes = slopedPlanes
        tolerance = slopedPlanes.Tolerance
        _Py.tolerance = tolerance
        _Py.reverse = slopedPlanes.Reverse
        _Py.upList = []

        faceMaker = slopedPlanes.FaceMaker

        onChanged = self.OnChanged
        if not self.faceList:
            # print 'faceList'
            onChanged = True

        if onChanged:
            # print 'A'

            face = Part.makeFace(shape, faceMaker)
            fList = face.Faces

            # gathers the exterior wires. Lower Left criteria

            coordinatesOuter, geomOuter = [], []
            for face in fList:
                outerWire = face.OuterWire
                falseFace = Part.makeFace(outerWire, "Part::FaceMakerSimple")
                coordinates, geometryList = self.faceDatas(falseFace)
                coordinates.extend(coordinates[0:2])
                coordinatesOuter.append(coordinates)
                geomOuter.append(geometryList)

            lowerLeft = [cc[0] for cc in coordinatesOuter]
            faceList = []
            coordinatesOuterOrdered, geomOuterOrdered = [], []
            while lowerLeft:
                index = self.lowerLeftPoint(lowerLeft)
                lowerLeft.pop(index)
                pop = coordinatesOuter.pop(index)
                coordinatesOuterOrdered.append(pop)
                pop = fList.pop(index)
                faceList.append(pop)
                pop = geomOuter.pop(index)
                geomOuterOrdered.append(pop)

            self.faceList = faceList

        else:
            # print 'B'

            faceList = self.faceList

        # procedees face by face and stores them into the Proxy

        pyFaceListOld = self.Pyth
        pyFaceListNew = []
        numFace = -1
        for face in faceList:
            numFace += 1
            # print '######### numFace ', numFace

            size = face.BoundBox.DiagonalLength
            _Py.size = size
            _Py.face = face

            if onChanged:
                # print 'AA'

                # elaborates complementary python objects of a face

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
                pyFace.size = size

                # gathers the interior wires. Upper Left criteria

                wList = face.Wires[1:]

                coordinatesInner, geomInner = [], []
                for wire in wList:
                    falseFace = Part.makeFace(wire, "Part::FaceMakerSimple")
                    coord, geomList = self.faceDatas(falseFace)
                    coord.extend(coord[0:2])
                    coordinatesInner.append(coord)
                    geomInner.append(geomList)

                upperLeft = [cc[0] for cc in coordinatesInner]
                wireList = []
                coordinatesInnerOrdered, geomInnerOrdered = [], []
                while upperLeft:
                    index = self.upperLeftPoint(upperLeft)
                    upperLeft.pop(index)
                    pop = coordinatesInner.pop(index)
                    coordinatesInnerOrdered.append(pop)
                    pop = wList.pop(index)
                    wireList.append(pop)
                    pop = geomInner.pop(index)
                    geomInnerOrdered.append(pop)

                wireList.insert(0, face.OuterWire)

                gList = [geomOuterOrdered[numFace]]
                gList.extend(geomInnerOrdered)
                # print gList

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
                    # print '###### numWire ', numWire
                    coo = coordinates[numWire]
                    for pyWire in pyWireListOld:
                        oldCoo = pyWire.coordinates
                        if oldCoo[0] == coo[0]:
                            # print 'a'
                            if oldCoo != coo:
                                # print 'b'
                                pyFace.reset = True
                                if len(oldCoo) != len(coo):
                                    # print 'c'
                                    pyWire.reset = True
                            pyWireListNew.append(pyWire)
                            pyWire.numWire = numWire
                            break
                    else:
                        # print 'd'
                        pyWire = _PyWire(numWire)
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
                        # print '### numGeom ', numGeom
                        try:
                            pyPlane = pyPlaneListOld[numGeom]
                            pyPlaneListNew.append(pyPlane)
                            pyPlane.numGeom = numGeom
                            # print '1'

                            if pyWire.reset:
                                # print '11'

                                pyPlane.angle = 45.0
                                pyPlane.rightWidth = size
                                pyPlane.leftWidth = size
                                pyPlane.length = 2 * size
                                pyPlane.overhang = 0
                                pyPlane.sweepCurve = None

                            if pyFace.reset:
                                # print '111'

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

                                pyPlane.lineInto = None
                                pyPlane.cross = False

                                pyPlane.reflexedList = []

                        except IndexError:
                            # print '2'
                            pyPlane = _PyPlane(numWire, numGeom)
                            pyPlaneListNew.append(pyPlane)

                        pyPlane.geom = geom
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

            else:
                # print 'BB'

                pyFace = self.Pyth[numFace]
                _Py.pyFace = pyFace

                for pyWire in pyFace.wires:

                    wire = Part.Wire(pyWire.shapeGeom)
                    pyWire.wire = wire

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

        if onChanged:
            # print 'AAA'
            self.Pyth = pyFaceListNew
        else:
            # print 'BBB'
            pyFaceListNew = self.Pyth

        self.OnChanged = True

        # elaborates a list of planes for every face

        figList = []
        for pyFace in pyFaceListNew:
            # print pyFace.numFace
            numFace = pyFace.numFace
            secondaries = []
            planeFaceList = []
            originList = []
            wireList = []
            for pyWire in pyFace.wires:
                # print pyWire.numWire
                numWire = pyWire.numWire
                planeWireList = []
                for pyPlane in pyWire.planes:
                    # print pyPlane.numGeom
                    numAngle = pyPlane.numGeom
                    angle = pyPlane.angle
                    # print 'angle ', angle

                    if pyPlane.length:

                        if [numWire, numAngle] not in originList:

                            if isinstance(angle, float):
                                # print 'a'

                                plane = pyPlane.shape

                                if isinstance(plane, Part.Compound):
                                    # print 'a1'
                                    planeWireList.append(plane.Faces[0])
                                    secondaries.extend(plane.Faces[1:])

                                else:
                                    # print 'a2'
                                    planeWireList.append(plane)

                                originList.append([numWire, numAngle])

                            else:
                                if angle not in originList:
                                    # print 'b'

                                    pyPl =\
                                        pyFace.selectPlane(angle[0], angle[1],
                                                           pyFace)
                                    pl = pyPl.shape
                                    planeWireList.append(pl)

                                    originList.append(angle)

                    # print 'originList ', originList

                if slopedPlanes.Up:
                    upPlaneCopy = _Py.upList[numFace].copy()
                    cut = upPlaneCopy.cut(planeWireList, _Py.tolerance)
                    edgeList = cut.Edges[4:]
                    wire = Part.Wire(edgeList)
                    wireList.append(wire)

                planeFaceList.extend(planeWireList)

            planeFaceList.extend(secondaries)

            if slopedPlanes.Up:
                upFace = Part.makeFace(wireList, faceMaker)

                planeFaceList.append(upFace)

            if slopedPlanes.Down:
                face = faceList[numFace]
                planeFaceList.append(face)

            if slopedPlanes.Mirror:
                shell = Part.makeShell(planeFaceList)
                mirror = shell.mirror(FreeCAD.Vector(0, 0, 0),
                                      FreeCAD.Vector(0, 0, -1))
                planeFaceList.extend(mirror.Faces)

            for plane in planeFaceList:
                plane.Placement = placement

            figList.append(planeFaceList)

        # makes a shell for every planes list, compunds them, and the end

        shellList = []
        for planeList in figList:
            shell = Part.makeShell(planeList)
            shellList.append(shell)

        endShape = Part.makeCompound(shellList)

        if slopedPlanes.Group:
            for obj in slopedPlanes.Group:
                if hasattr(obj, "Proxy"):
                    if obj.Proxy.Type == "SlopedPlanes":
                        childShape = obj.Shape.copy()

                        common = endShape.common([childShape], tolerance)

                        if common.Area:

                            endShape = endShape.cut([common], tolerance)
                            childShape = childShape.cut([common], tolerance)

                            sPEdges = []
                            objEdges = []

                            for ff in common.Faces:

                                oEdges = []
                                for pyFace in obj.Proxy.Pyth:
                                    for pyWire in pyFace.wires:
                                        for pyPl in pyWire.planes:
                                            gS = pyPl.geomShape
                                            if gS:
                                                section = ff.section([gS],
                                                                     tolerance)
                                                if section.Edges:
                                                    oEdges.append([pyPl,
                                                                   pyFace])

                                objEdges.append(oEdges)
                                # print 'oEdges ', oEdges

                                sEdges = []
                                for pyFace in slopedPlanes.Proxy.Pyth:
                                    for pyWire in pyFace.wires:
                                        for pyPl in pyWire.planes:
                                            gS = pyPl.geomShape
                                            if gS:
                                                section = ff.section([gS],
                                                                     tolerance)
                                                if section.Edges:
                                                    sEdges.append([pyPl,
                                                                   pyFace])

                                sPEdges.append(sEdges)
                                # print 'sEdges ', sEdges

                            endShape, childShape =\
                                self.refine(sPEdges, objEdges,
                                            endShape, childShape)

                        endShape = Part.Compound([endShape, childShape])

        if not slopedPlanes.Complement:
            endShape.complement()

        if slopedPlanes.Thickness:
            normal = self.faceNormal(faceList[0])
            if slopedPlanes.Reverse:
                normal = normal * -1
            endShape = endShape.extrude(slopedPlanes.Thickness.Value * normal)

        if slopedPlanes.Solid:
            endShape = Part.makeSolid(endShape)

        # endShape.removeInternalWires(True)

        slopedPlanes.Shape = endShape

    def onChanged(self, slopedPlanes, prop):

        '''onChanged(self, slopedPlanes, prop)'''

        if self.State:

            return

        if prop == "Slope":

            slope = slopedPlanes.Slope
            value = slope.Value
            prop = "angle"
            self.overWritePyProp(prop, value)

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

        for pyFace in self.Pyth:

            size = pyFace.size

            if prop in ["length", "width", "overhang"]:
                newValue = value * size
            else:
                newValue = value

            if prop == "width":

                for pyWire in pyFace.wires:
                    for pyPlane in pyWire.planes:
                        setattr(pyPlane, "leftWidth", newValue)
                        setattr(pyPlane, "rightWidth", newValue)

            else:

                for pyWire in pyFace.wires:
                    for pyPlane in pyWire.planes:
                        setattr(pyPlane, prop, newValue)

        self.OnChanged = False

    def __getstate__(self):

        ''''''

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
                serials = Part.makeCompound([face] + serials)
                dct['_serials'] = serials.exportBrepToString()
            else:
                if '_serials' in dct:
                    del dct['_serials']
            pyth.append(dct)
        state['Pyth'] = pyth

        return state

    def __setstate__(self, state):

        ''''''

        self.Type = state['Type']

        serialize = state['Serialize']

        faceList = []
        pyth = []
        numFace = -1
        for dct in state['Pyth']:
            numFace += 1
            pyFace = _PyFace(numFace)

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

        # self.printSerialSummary()


class _ViewProvider_SlopedPlanes():

    ''''''

    def __init__(self, vobj):

        ''''''

        vobj.addExtension("Gui::ViewProviderGroupExtensionPython", self)
        vobj.Proxy = self

    def getIcon(self):

        ''''''

        return path.dirname(__file__) + "/SlopedPlanes_Tree.svg"

    def getDefaultDisplayMode(self):

        ''''''

        return "FlatLines"

    def __getstate__(self):

        ''''''

        return None

    def __setstate__(self, state):

        ''''''

        return None

    def attach(self, vobj):

        ''''''

        self.Object = vobj.Object
        obj = self.Object
        obj.Proxy.State = False

    def claimChildren(self):

        ''''''

        obj = self.Object
        return [obj.Base] + obj.Group

    def unsetEdit(self, vobj, mode):

        ''''''

        FreeCADGui.Control.closeDialog()
        return

    def setEdit(self, vobj, mode=0):

        ''''''

        taskd = _TaskPanel_SlopedPlanes(self.Object)
        self.task = taskd
        taskd.update()
        FreeCADGui.Control.showDialog(taskd)
        return True
