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


# import rpdb2
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


# rpdb2.start_embedded_debugger("test")


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

    '''The SlopedPlanes object Class'''

    def __init__(self, slopedPlanes):

        '''__init__(self, slopedPlanes)
        Initializes the properties of the SlopedPlanes object and its Proxy.
        The Proxy stores:
        State, Type, and the complementary python objects (Pyth)'''

        slopedPlanes.addProperty("App::PropertyLink", "Base",
                                 "SlopedPlanes")
        slopedPlanes.addProperty("App::PropertyBool", "Complement",
                                 "SlopedPlanes")
        slopedPlanes.addProperty("App::PropertyBool", "Reverse",
                                 "SlopedPlanes")
        slopedPlanes.addProperty("App::PropertyBool", "Mirror",
                                 "SlopedPlanes")
        slopedPlanes.addProperty("App::PropertyBool", "Solid",
                                 "SlopedPlanes")
        slopedPlanes.addProperty("App::PropertyBool", "Down",
                                 "SlopedPlanes")
        slopedPlanes.addProperty("App::PropertyFloat", "Up",
                                 "SlopedPlanes")
        slopedPlanes.addProperty("App::PropertyFloat", "Slope",
                                 "SlopedPlanes")
        slopedPlanes.addProperty("App::PropertyFloat", "FactorLength",
                                 "SlopedPlanes")
        slopedPlanes.addProperty("App::PropertyFloat", "FactorWidth",
                                 "SlopedPlanes")
        slopedPlanes.addProperty("App::PropertyPrecision", "Tolerance",
                                 "SlopedPlanes")
        slopedPlanes.addProperty("App::PropertyEnumeration", "FaceMaker",
                                 "SlopedPlanes")

        self.State = False
        self.OnChanged = True

        slopedPlanes.Slope = 45.0
        slopedPlanes.FactorWidth = 1
        slopedPlanes.FactorLength = 2
        slopedPlanes.Up = 0
        slopedPlanes.FaceMaker = ["Part::FaceMakerBullseye",
                                  "Part::FaceMakerSimple",
                                  "Part::FaceMakerCheese"]
        slopedPlanes.Tolerance = (1e-7, 1e-7, 1, 1e-7)

        slopedPlanes.Proxy = self
        self.Type = "SlopedPlanes"
        self.Pyth = []

    def execute(self, slopedPlanes):

        '''execute(self, slopedPlanes)
        Builds the shape of the slopedPlanes object'''

        _Py.slopedPlanes = slopedPlanes

        sketch = slopedPlanes.Base
        shape = sketch.Shape.copy()
        sketchBase = sketch.Placement.Base
        sketchAxis = sketch.Placement.Rotation.Axis
        sketchAngle = sketch.Placement.Rotation.Angle
        shape.Placement = FreeCAD.Placement()

        _Py.tolerance = slopedPlanes.Tolerance
        _Py.reverse = slopedPlanes.Reverse

        slope = slopedPlanes.Slope
        width = slopedPlanes.FactorWidth
        length = slopedPlanes.FactorLength

        faceMaker = slopedPlanes.FaceMaker
        face = Part.makeFace(shape, faceMaker)

        fList = face.Faces
        normal = self.faceNormal(fList[0])
        _Py.normal = normal

        # prepares a giant plane

        up = slopedPlanes.Up
        if up:
            upPlane = Part.makePlane(1e6, 1e6, FreeCAD.Vector(-1e3, -1e3, 0))
            upPlane.translate(FreeCAD.Vector(0, 0, 1)*up)
            _Py.upPlane = upPlane

        if self.OnChanged:
            print 'A'

            # gathers the exterior wires. Lower Left criteria

            fFaceOuter = []
            coordinatesOuter = []
            for face in fList:
                outerWire = face.OuterWire
                falseFace = Part.makeFace(outerWire, "Part::FaceMakerSimple")
                fFaceOuter.append(falseFace)
                coordinates = self.faceDatas(falseFace)[1]
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

            _Py.faceList = faceList

        else:
            print 'B'

            faceList = _Py.faceList

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

            if self.OnChanged:
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

                # gathers the interior wires. Upper Left criteria

                wList = face.Wires[1:]
                coordinatesInner = []
                fFaceList = []
                for wire in wList:
                    falseFace = Part.makeFace(wire, "Part::FaceMakerSimple")
                    fFaceList.append(falseFace)
                    coord = self.faceDatas(falseFace)[1]
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
                if coordinatesInnerOrdered:
                    coordinates.extend(coordinatesInnerOrdered)

                pyWireListOld = pyFace.wires
                pyWireListNew = []
                geomShapeFace = []
                numWire = -1
                for wire in wireList:
                    numWire += 1
                    # print '###### numWire ', numWire
                    coo = coordinates[numWire]
                    brea = False
                    for pyWire in pyWireListOld:
                        oldCoo = pyWire.coordinates
                        if oldCoo[0] == coo[0]:
                            # print 'a'
                            brea = True
                            if oldCoo != coo:
                                # print 'b'
                                pyFace.reset = True
                                if len(oldCoo) != len(coo):
                                    # print 'c'
                                    pyWire.reset = True
                            if brea:
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
                                pyPlane.angle = slope
                                pyPlane.width = [width, width]
                                pyPlane.length = length
                            if pyFace.reset:
                                # print '111'
                                pyPlane.rear = []
                                pyPlane.rango = []
                                pyPlane.aligned = False
                                pyPlane.arrow = False
                                pyPlane.choped = False
                                pyPlane.unsolved = []
                                pyPlane.reflexed = False
                        except IndexError:
                            # print '2'
                            pyPlane = _PyPlane(numWire, numGeom)
                            pyPlaneListNew.append(pyPlane)

                        pyPlane.geom = geom
                        gS = geom.toShape()
                        pyPlane.geomShape = gS
                        geomShapeWire.append(gS)
                        pyPlane.geomAligned = geom.toShape()

                    pyWire.planes = pyPlaneListNew
                    pyWire.shapeGeom = geomShapeWire
                    geomShapeFace.extend(geomShapeWire)

                pyFace.shapeGeom = geomShapeFace
                pyFace.wires = pyWireListNew

            else:
                # print 'BB'

                pyFace = self.Pyth[numFace]
                _Py.pyFace = pyFace

                if pyFace.alignments:
                    for pyWire in pyFace.wires:
                        for pyPlane in pyWire.planes:
                            pyPlane.geomAligned = pyPlane.geomShape

            pyFace.parsing()

            pyFace.planning()

            pyFace.upping()

            pyFace.virtualizing()

            pyFace.trimming()

            pyFace.priorLater()

            pyFace.simulating()

            pyFace.preOrdinaries()

            pyFace.preReflexs()

            pyFace.reSimulating()

            pyFace.reflexing()

            pyFace.reviewing()

            pyFace.rearing()

            pyFace.ordinaries()

            pyFace.betweenWires()

            pyFace.aligning()

            pyFace.ending()

        if self.OnChanged:
            self.Pyth = pyFaceListNew
        else:
            pyFaceListNew = self.Pyth
        self.OnChanged = True

        # elaborates a list of planes for every face

        figList = []
        for pyFace in pyFaceListNew:
            secondaries = []
            planeFaceList = []
            originList = []
            pyWireList = pyFace.wires
            wireList = []
            for pyWire in pyWireList:
                numWire = pyWire.numWire
                planeWireList = []
                for pyPlane in pyWire.planes:
                    numAngle = pyPlane.numGeom
                    angle = pyPlane.angle

                    # some figures (a few of them) break the planes numeration
                    '''
                    # print 'numGeom ', numAngle
                    plane = pyPlane.shape
                    gS = pyPlane.geomShape
                    # print (gS.firstVertex(True).Point,
                           gS.lastVertex(True).Point)
                    if plane:
                        section = plane.section(gS)
                        if section.Edges:
                            # print 'okey'
                        else:
                            # print 'bad'
                    else:
                        # print 'no plane'
                    '''
                    # TODO "solution" at task panel

                    if [numWire, numAngle] not in originList:

                        if isinstance(angle, float):
                            # print 'a'

                            plane = pyPlane.shape

                            if isinstance(plane, Part.Compound):
                                # print 'compound'
                                planeWireList.append(plane.Faces[0])
                                secondaries.extend(plane.Faces[1:])

                            else:
                                planeWireList.append(plane)

                        else:
                            # print 'b'

                            alfa, beta = angle[0], angle[1]

                            if [alfa, beta] not in originList:
                                originList.append([alfa, beta])

                                if alfa == numWire:
                                    if beta > numAngle:
                                        pyPl = pyFace.selectPlane(alfa, beta)
                                        pl = pyPl.shape
                                        planeWireList.append(pl)

                                elif alfa > numWire:
                                    pyPl = pyFace.selectPlane(alfa, beta)
                                    pl = pyPl.shape
                                    planeWireList.append(pl)

                                elif alfa < numWire:
                                    pass

                if up:
                    upPlaneCopy = upPlane.copy()
                    cut = upPlaneCopy.cut(planeWireList, _Py.tolerance)
                    edgeList = cut.Edges[4:]
                    if numWire > 0:     # this doesn't seem to be necessary
                        for edge in edgeList:
                            edge.reverse()
                        edgeList.reverse()
                        pass
                    wire = Part.Wire(edgeList)
                    wireList.append(wire)

                planeFaceList.extend(planeWireList)

            planeFaceList.extend(secondaries)

            if up:
                upFace = Part.makeFace(wireList, faceMaker)

                # hay que comprobar para cada interior wire que realmente corta
                # o diseñar otra solución para evitar open wires. Mirar cut

                planeFaceList.append(upFace)

                # the Up System break the interior wires numeration
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
            value = slope
            prop = "angle"
            self.overWritePyProp(prop, value)

        elif prop == "FactorLength":

            length = slopedPlanes.FactorLength
            value = length
            prop = "length"
            self.overWritePyProp(prop, value)

        elif prop == "FactorWidth":

            width = slopedPlanes.FactorWidth
            value = (width, width)
            prop = "width"
            self.overWritePyProp(prop, value)

    def overWritePyProp(self, prop, value):

        '''overWritePyProp(self, prop, value)
        '''

        for pyFace in self.Pyth:
            for pyWire in pyFace.wires:
                for pyPlane in pyWire.planes:
                    setattr(pyPlane, prop, value)

        self.OnChanged = False

    def __getstate__(self):

        ''''''

        state = dict()

        state['Type'] = self.Type

        pyth = []
        for pyFace in self.Pyth:
            dct = pyFace.__dict__.copy()
            wires, alignments = pyFace.__getstate__()
            dct['_shapeGeom'] = []
            dct['_wires'], dct['_alignments'] = wires, alignments
            pyth.append(dct)
        state['Pyth'] = pyth

        state['_faceList'] = self.getstate()

        return state

    def __setstate__(self, state):

        ''''''

        self.Type = state['Type']

        pyth = []
        numFace = -1
        for dct in state['Pyth']:
            numFace += 1
            pyFace = _PyFace(numFace)
            wires, alignments = dct['_wires'], dct['_alignments']
            wires, alignments = pyFace.__setstate__(wires, alignments)
            dct['_wires'], dct['_alignments'] = wires, alignments
            pyFace.__dict__ = dct
            pyth.append(pyFace)
        self.Pyth = pyth

        self.State = True

        self.setstate(state['_faceList'])


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
