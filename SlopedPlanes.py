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


from os import path
from math import degrees
import FreeCAD
import FreeCADGui
import Part
from SlopedPlanesPy import _Py
from SlopedPlanesPyFace import _PyFace
from SlopedPlanesPyWire import _PyWire
from SlopedPlanesPyPlane import _PyPlane
from SlopedPlanesTaskPanel import _TaskPanel_SlopedPlanes


__title__ = "SlopedPlanes Macro"
__author__ = "Damian Caceres Moreno"
__url__ = "http://www.freecadweb.org"
__version__ = ""
__doc__ = '''Requieres a sketch or DWire as base.
             The base must support the FaceMaker.
             The angles numeration corresponds
             to the faces of the SlopedPlane's shape.'''


def makeSlopedPlanes(sketch):

    '''makeSlopedPlanes(sketch)
    makes the SlopedPlanes object from a sketch or a DWire'''

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

    '''The Class of the FreeCAD scripted object SlopedPlanes'''

    def __init__(self, slopedPlanes):

        '''__init__(self, slopedPlanes)
        Initializes the properties of the SlopedPlanes object and its Proxy.
        The Proxy stores:

        - the four flags
            Type: object recognition
            State: indicates the loading file
            OnChanged: faster execute from property and task panels
            Serialize: Slower loading file and faster execute with State = True

        - the two lists:
            Pyth: the complementary python objects
            faceList: faces produced by the base'''

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

        doc = '''Gives a plane on top of the SlopedPlanes.
The Up could break the interior wires numeration.
First give the angles and later apply Up.'''

        slopedPlanes.addProperty("App::PropertyLength", "Up",
                                 "SlopedPlanes", doc)

        doc = '''Gives a thickness to the SlopedPlanes.
First give the angles and later apply thickness.'''

        slopedPlanes.addProperty("App::PropertyLength", "Thickness",
                                 "SlopedPlanes", doc)

        doc = "Gives an overhang to all planes of the SlopedPlanes"

        slopedPlanes.addProperty("App::PropertyLength", "Overhang",
                                 "SlopedPlanes", doc)

        doc = '''Applies over all planes angles.
To cero the SlopedPlanes hasn't shape'''

        slopedPlanes.addProperty("App::PropertyAngle", "Slope",
                                 "SlopedPlanes", doc)

        doc = '''Applies over all planes length, or length of extrusion of the
planes, multiplied by the diagonal of the SlopedPlanes base.
To cero the SlopedPlanes hasn't shape'''

        slopedPlanes.addProperty("App::PropertyFloat", "FactorLength",
                                 "SlopedPlanes", doc)

        doc = '''Applies over all planes width, left and right, multiplied by
the diagonal of the SlopedPlanes base.
To cero the plane width is equal to the related edge length of the base'''

        slopedPlanes.addProperty("App::PropertyFloat", "FactorWidth",
                                 "SlopedPlanes", doc)

        doc = "Tolerance"

        slopedPlanes.addProperty("App::PropertyPrecision", "Tolerance",
                                 "SlopedPlanes", doc)

        doc = "FaceMaker"

        slopedPlanes.addProperty("App::PropertyEnumeration", "FaceMaker",
                                 "SlopedPlanes", doc)

        self.State = True

        slopedPlanes.Slope = 45.0
        slopedPlanes.FactorWidth = 1
        slopedPlanes.FactorLength = 2
        slopedPlanes.Overhang = 0
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
        sketchBase = sketch.Placement.Base
        sketchAxis = sketch.Placement.Rotation.Axis
        sketchAngle = sketch.Placement.Rotation.Angle
        shape.Placement = FreeCAD.Placement()

        _Py.tolerance = slopedPlanes.Tolerance
        _Py.reverse = slopedPlanes.Reverse
        _Py.slopedPlanes = slopedPlanes
        _Py.upList = []

        faceMaker = slopedPlanes.FaceMaker

        onChanged = self.OnChanged
        if not self.faceList:
            onChanged = True

        if onChanged:
            # print 'A'

            face = Part.makeFace(shape, faceMaker)
            fList = face.Faces

            # gathers the exterior wires. Lower Left criteria

            fFaceOuter = []
            coordinatesOuter = []
            for face in fList:
                outerWire = face.OuterWire
                falseFace = Part.makeFace(outerWire, "Part::FaceMakerSimple")
                fFaceOuter.append(falseFace)
                coordinates = self.faceDatas(falseFace)
                coordinates.extend(coordinates[0:2])
                coordinatesOuter.append(coordinates)

            lowerLeft = [cc[0] for cc in coordinatesOuter]
            faceList = []
            falseFaceOuter = []
            coordinatesOuterOrdered = []
            while lowerLeft:
                index = self.lowerLeftPoint(lowerLeft)
                lowerLeft.pop(index)
                pop = coordinatesOuter.pop(index)
                coordinatesOuterOrdered.append(pop)
                pop = fList.pop(index)
                faceList.append(pop)
                pop = fFaceOuter.pop(index)
                falseFaceOuter.append(pop)

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
                # elaborates complementary python objects of a face
                # print 'AA'

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
                coordinatesInner = []
                fFaceList = []
                for wire in wList:
                    falseFace = Part.makeFace(wire, "Part::FaceMakerSimple")
                    fFaceList.append(falseFace)
                    coord = self.faceDatas(falseFace)
                    coord.extend(coord[0:2])
                    coordinatesInner.append(coord)

                upperLeft = [cc[0] for cc in coordinatesInner]
                wireList = []
                falseFaceList = []
                coordinatesInnerOrdered = []
                while upperLeft:
                    index = self.upperLeftPoint(upperLeft)
                    upperLeft.pop(index)
                    pop = coordinatesInner.pop(index)
                    coordinatesInnerOrdered.append(pop)
                    pop = wList.pop(index)
                    wireList.append(pop)
                    pop = fFaceList.pop(index)
                    falseFaceList.append(pop)

                wireList.insert(0, face.OuterWire)
                falseFaceList.insert(0, falseFaceOuter[numFace])

                coordinates = [coordinates]
                # if coordinatesInnerOrdered:
                coordinates.extend(coordinatesInnerOrdered)

                pyWireListOld = pyFace.wires
                pyWireListNew = []
                geomShapeFace = []
                numWire = -1
                for wire in wireList:
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

                    falseFace = falseFaceList[numWire]
                    geomWire = self.arcGeometries(falseFace, coo[:-2])

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
                                pyPlane.angle = 45
                                pyPlane.rightWidth = size
                                pyPlane.leftWidth = size
                                pyPlane.length = 2 * size
                                pyPlane.overhang = 0
                            if pyFace.reset:
                                # print '111'
                                pyPlane.rear = []
                                pyPlane.rango = []
                                pyPlane.rangoConsolidate = []
                                pyPlane.aligned = False
                                pyPlane.arrow = False
                                pyPlane.choped = False
                                pyPlane.reflexed = False
                                pyPlane.fronted = False
                                pyPlane.seedShape = None
                                angle = pyPlane.angle
                                if isinstance(angle, list):
                                    angle = self.selectPlane(angle[0],
                                                             angle[1]).angle
                                    pyPlane.angle = angle
                                pyPlane.reared = False
                                pyPlane.lineInto = None

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

                    pyWire.planes = pyPlaneListNew
                    pyWire.shapeGeom = geomShapeWire
                    geomShapeFace.extend(geomShapeWire)

                pyFace.shapeGeom = geomShapeFace
                pyFace.wires = pyWireListNew

            else:
                # print 'BB'

                pyFace = self.Pyth[numFace]
                _Py.pyFace = pyFace

                for pyWire in pyFace.wires:
                    for pyPlane in pyWire.planes:
                        pyPlane.geomAligned = pyPlane.geomShape
                        pyPlane.control = [pyPlane.numGeom]

            pyFace.parsing()        #

            pyFace.planning()       #

            pyFace.upping()         #

            pyFace.virtualizing()   #

            pyFace.trimming()       #

            pyFace.priorLater()     #

            pyFace.simulating()     #

            pyFace.reflexing()      #

            pyFace.ordinaries()     #

            pyFace.betweenWires()   #

            pyFace.aligning()       #

            pyFace.end()            # '''

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
            numFace = pyFace.numFace
            secondaries = []
            planeFaceList = []
            originList = []
            wireList = []
            for pyWire in pyFace.wires:
                numWire = pyWire.numWire
                planeWireList = []
                for pyPlane in pyWire.planes:
                    numAngle = pyPlane.numGeom
                    angle = pyPlane.angle
                    # some figures (a few of them) break the planes numeration

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

                            else:
                                # print 'b'

                                alfa, beta = angle[0], angle[1]

                                if [alfa, beta] not in originList:
                                    originList.append([alfa, beta])

                                    if alfa == numWire:
                                        # print 'b1'
                                        if beta > numAngle:
                                            pyPl =\
                                                pyFace.selectPlane(alfa, beta)
                                            pl = pyPl.shape
                                            planeWireList.append(pl)

                                    elif alfa > numWire:
                                        # print 'b2'
                                        pyPl = pyFace.selectPlane(alfa, beta)
                                        pl = pyPl.shape
                                        planeWireList.append(pl)

                                    elif alfa < numWire:
                                        # print 'b3'
                                        pass

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

                # the Up System could break the interior wires numeration
                # first give the angles and later apply Up

            if slopedPlanes.Down:
                face = faceList[numFace]
                planeFaceList.append(face)

            if slopedPlanes.Mirror:
                shell = Part.makeShell(planeFaceList)
                mirror = shell.mirror(FreeCAD.Vector(0, 0, 0),
                                      FreeCAD.Vector(0, 0, -1))
                planeFaceList.extend(mirror.Faces)

            for plane in planeFaceList:
                plane.rotate(FreeCAD.Vector(0, 0, 0), sketchAxis,
                             degrees(sketchAngle))
                plane.translate(sketchBase)

            figList.append(planeFaceList)

        # makes a shell for every planes list, compunds them, and the end

        shellList = []
        for planeList in figList:
            shell = Part.makeShell(planeList)
            shellList.append(shell)

        endShape = Part.makeCompound(shellList)

        if not slopedPlanes.Complement:
            endShape.complement()

        if slopedPlanes.Thickness:
            normal = self.faceNormal(faceList[0])
            if slopedPlanes.Reverse:
                normal = normal * -1
            endShape = endShape.extrude(slopedPlanes.Thickness.Value*normal)

            # the Thickness System breaks the faces numeration
            # first give the angles and later apply Thickness

        if slopedPlanes.Solid:
            endShape = Part.makeSolid(endShape)

        # endShape.removeInternalWires(True)

        slopedPlanes.Shape = endShape

    def onChanged(self, slopedPlanes, prop):

        '''onChanged(self, slopedPlanes, prop)
        '''

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

        elif prop == "Overhang":

            overhang = slopedPlanes.Overhang
            value = overhang.Value
            prop = "overhang"
            self.overWritePyProp(prop, value)

        elif prop == "Reverse":

            value = None
            prop = "seedShape"
            self.overWritePyProp(prop, value)

    def overWritePyProp(self, prop, value):

        '''overWritePyProp(self, prop, value)
        '''

        for pyFace in self.Pyth:

            size = pyFace.size

            if prop in ["length", "width"]:
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

        if serialize:
            state['_faceList'] = self.getstate(self.faceList)
        else:
            state['_faceList'] = []

        pyth = []
        for pyFace in self.Pyth:
            dct = pyFace.__dict__.copy()
            wires, alignments = pyFace.__getstate__(serialize)
            dct['_shapeGeom'] = []
            dct['_wires'] = wires
            dct['_alignments'] = alignments
            pyth.append(dct)
        state['Pyth'] = pyth

        return state

    def __setstate__(self, state):

        ''''''

        self.Type = state['Type']

        serialize = state['Serialize']

        faceList = self.setstate(state['_faceList'])
        self.faceList = faceList

        pyth = []
        numFace = -1
        for dct in state['Pyth']:
            numFace += 1
            pyFace = _PyFace(numFace)
            wires = dct['_wires']
            alignments = dct['_alignments']
            wires, alignments, geomShapeFace =\
                pyFace.__setstate__(wires, alignments, serialize)
            dct['_wires'] = wires
            dct['_alignments'] = alignments
            dct['_shapeGeom'] = geomShapeFace
            pyFace.__dict__ = dct
            pyth.append(pyFace)
        self.Pyth = pyth

        self.Serialize = serialize
        self.State = True

        if serialize:
            self.OnChanged = False
            # if the geometry change after loading, recompute
        else:
            self.OnChanged = True


class _ViewProvider_SlopedPlanes():

    ''''''

    def __init__(self, vobj):

        ''''''

        vobj.Proxy = self

    def getIcon(self):

        ''''''

        pth = path.dirname(__file__)
        return pth + "/SlopedPlanes_Tree.svg"

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
        base = obj.Base
        return [base]

    def unsetEdit(self, vobj, mode):

        ''''''

        FreeCADGui.Control.closeDialog()
        return

    def setEdit(self, vobj, mode=0):

        ''''''

        taskd = _TaskPanel_SlopedPlanes()
        taskd.obj = self.Object
        taskd.update()
        FreeCADGui.Control.showDialog(taskd)
        return True
