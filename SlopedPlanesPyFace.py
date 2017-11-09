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
import SlopedPlanesUtils as utils
from SlopedPlanesPy import _Py
from SlopedPlanesPyWire import _PyWire
from SlopedPlanesPyReflex import _PyReflex
from SlopedPlanesPyAlignament import _PyAlignament
from SlopedPlanesPyPlane import _PyPlane


__title__ = "SlopedPlanes Macro"
__author__ = "Damian Caceres Moreno"
__url__ = "http://www.freecadweb.org"


class _PyFace(_Py):

    ''''''

    def __init__(self, numFace):

        ''''''

        self.numFace = numFace
        self.wires = []
        self.alignaments = []
        self.reset = False

    @property
    def numFace(self):

        ''''''

        return self._numFace

    @numFace.setter
    def numFace(self, numFace):

        ''''''

        self._numFace = numFace

    @property
    def wires(self):

        ''''''

        return self._wires

    @wires.setter
    def wires(self, wires):

        ''''''

        self._wires = wires

    @property
    def alignaments(self):

        ''''''

        return self._alignaments

    @alignaments.setter
    def alignaments(self, alignaments):

        ''''''

        self._alignaments = alignaments

    @property
    def reset(self):

        ''''''

        return self._reset

    @reset.setter
    def reset(self, reset):

        ''''''

        self._reset = reset

    def __getstate__(self):

        ''''''

        wireList = []
        for wire in self.wires:
            dct = wire.__dict__.copy()
            dct['_coordinates'] = [[v.x, v.y, v.z] for v in wire.coordinates]
            dct['_shapeGeom'] = []

            planeList = []
            for plane in wire.planes:
                dd = plane.__dict__.copy()
                # TODO change
                dd['_shape'], dd['_bigShape'], dd['_enormousShape'],\
                    dd['_geom'], dd['_geomAligned'],\
                    dd['_cutter'], dd['_oppCutter'], dd['_divide'],\
                    dd['_forward'], dd['_backward'], dd['_simulatedShape'],\
                    dd['_compound'] = \
                    None, None, None, None, None, [], [], [], None, None,\
                    None, None
                planeList.append(dd)
            dct['_planes'] = planeList

            reflexList = []
            for reflex in wire.reflexs:
                dd = reflex.__dict__.copy()
                planes = [[plane.numWire, plane.numGeom]
                          for plane in reflex.planes]
                dd['_planes'] = planes
                reflexList.append(dd)
            dct['_reflexs'] = reflexList

            wireList.append(dct)

        alignList = []
        for align in self.alignaments:
            dct = {}
            alignList.append(dct)

        return wireList, alignList

    def __setstate__(self, wires, alignaments):

        ''''''

        wireList = []
        numWire = -1
        for dct in wires:
            numWire += 1
            wire = _PyWire(numWire)

            planeList = []
            numGeom = -1
            for dd in dct['_planes']:
                numGeom += 1
                plane = _PyPlane(numWire, numGeom)
                plane.__dict__ = dd
                planeList.append(plane)
            dct['_planes'] = planeList

            reflexList = []
            for dd in dct['_reflexs']:
                reflex = _PyReflex()
                for [numWire, numGeom] in dd['_planes']:
                    plane = planeList[numGeom]
                    reflex.addLink('planes', plane)
                dd['_planes'] = reflex.planes
                reflex.__dict__ = dd
                reflexList.append(reflex)
            dct['_reflexs'] = reflexList

            coord = dct['_coordinates']
            coordinates = [FreeCAD.Vector(v) for v in coord]
            dct['_coordinates'] = coordinates

            wire.__dict__ = dct
            wireList.append(wire)

        alignList = []
        for dct in alignaments:
            alignament = _PyAlignament()
            alignList.append(alignament)

        return wireList, alignList

    def parsing(self, size):

        ''''''

        pyWireList = self.wires

        resetFace = self.reset
        if resetFace:
            for pyWire in pyWireList:
                pyWire.reflexs = []

        self.alignaments = []

        shapeGeomFace = []
        for pyWire in pyWireList:
            shapeGeomFace.extend(pyWire.shapeGeom)

        for pyWire in pyWireList:
            numWire = pyWire.numWire
            # print'###### numWire ', numWire
            ref = False

            lenWire = len(pyWire.planes)
            coord = pyWire.coordinates
            eje = coord[1].sub(coord[0])
            pyPlaneList = pyWire.planes
            for pyPlane in pyPlaneList:
                numGeom = pyPlane.numGeom
                # print'### numGeom ', numGeom
                # printpyPlane.geom

                if not pyPlane.geomAligned:

                    ref = False
                    eje = coord[numGeom+2].sub(coord[numGeom+1])

                else:

                    nextEje = coord[numGeom+2].sub(coord[numGeom+1])
                    corner = utils.convexReflex(eje, nextEje, _Py.normal, numWire)
                    eje = nextEje

                    if corner == 'convex':
                        if pyPlane.choped:
                            if not pyPlane.rear:
                                ref = True
                                pyReflex = _PyReflex()

                    if ref:
                        print'ref'
                        forwardLine = self.forBack(pyPlane, size, 'backward')
                        ref = False

                        if resetFace:
                            if pyPlane.geomAligned:
                                print'ref reset'

                                self.seatReflex(pyWire, pyReflex, pyPlane,
                                                'backward')

                    lineEnd = coord[numGeom+1]

                    if corner == 'reflex' or numWire > 0:
                        forwardLine = self.forBack(pyPlane, size, 'forward')

                    if ((numWire == 0 and corner == 'reflex') or
                       (numWire > 0 and corner == 'convex')):
                        print'1'

                        forward = pyPlane.forward
                        section = forward.section(shapeGeomFace, _Py.tolerance)

                        if section.Edges:
                            print'11'

                            numEdge = -1
                            for edge in section.Edges:
                                numEdge += 1
                                print'111'
                                edgeStart = edge.firstVertex(True).Point
                                point = utils.roundVector(edgeStart, _Py.tolerance)
                                (nWire, nGeom) =\
                                    self.findAlignament(point)

                                pyW = pyWireList[nWire]
                                pyPl = pyW.planes[nGeom]
                                if pyPl.geomAligned:
                                    print'1111'
                                    edgeEnd = edge.lastVertex(True).Point
                                    distStart = edgeStart.sub(lineEnd).Length
                                    distEnd = edgeEnd.sub(lineEnd).Length

                                    if distStart < distEnd:
                                        print'11111'

                                        if numEdge == 0:
                                            pyAlign =\
                                                self.doAlignament(pyPlane)

                                        fAng = self.findAngle(numWire, numGeom)
                                        sAng = self.findAngle(nWire, nGeom)
                                        fGeom = pyPlane.geomAligned
                                        sGeom = pyPl.geomAligned

                                        if fAng == sAng:
                                            print'111111'
                                            pyPl.geomAligned = None
                                            pyPl.angle = [numWire, numGeom]

                                            eStartParam = fGeom.FirstParameter
                                            eEndPoint = sGeom.EndPoint
                                            eEndParam =\
                                                forwardLine.parameter(eEndPoint)
                                            eGeom =\
                                                Part.LineSegment(fGeom,
                                                                 eStartParam,
                                                                 eEndParam)
                                            pyPlane.geomAligned = eGeom

                                        else:
                                            print'111112'
                                            if numEdge > 0:
                                                pyAlign =\
                                                    self.doAlignament(pyPlane)
                                            pyAlign.falsify = True

                                        self.seatAlignament(pyAlign,
                                                            pyWire, pyPlane,
                                                            pyW, pyPl,
                                                            size)

                                        if pyPl.numWire == pyPlane.numWire:
                                            ref = True

                                        pyReflex = _PyReflex()

                                        if pyAlign.falsify:
                                            print'break'
                                            break

                                    else:
                                        print'1112'
                                        if corner == 'reflex':
                                            print'11121'
                                            ref = True
                                            if resetFace:
                                                print'111211'
                                                pyReflex =\
                                                    self.doReflex(pyWire,
                                                                  pyPlane)
                                            break

                                else:
                                    print'1112'
                                    if pyPl.numWire == pyPlane.numWire:
                                        ref = True
                                    pyReflex = _PyReflex()

                            else:
                                print'end'
                                if corner == 'reflex':
                                    if resetFace:
                                        self.seatReflex(pyWire, pyReflex,
                                                        pyPlane,
                                                        'forward')

                        else:
                            print'12'
                            if corner == 'reflex':
                                print'121'
                                ref = True
                                if resetFace:
                                    print'1211'
                                    pyReflex =\
                                        self.doReflex(pyWire, pyPlane)

                    else:
                        print'2'
                        if corner == 'reflex':
                            print'21'
                            if not pyPlane.choped:
                                print'211'
                                num = utils.sliceIndex(numGeom+1, lenWire)
                                pyNextPlane = pyPlaneList[num]
                                if not pyNextPlane.choped:
                                    print'2111'
                                    ref = True
                                    if resetFace:
                                        print'21111'
                                        pyReflex =\
                                            self.doReflex(pyWire, pyPlane)

            pyWire.reset = False

        self.priorLaterAlignaments()

        self.removeExcessReflex()

        self.printSummary()

    def seatAlignament(self, pyAlign, pyWire, pyPlane, pyW, pyPl,
                       size):

        ''''''

        numWire = pyWire.numWire
        numGeom = pyPlane.numGeom
        # print 'pyPlane.numWire ', pyPlane.numWire
        # print 'pyPlane.numGeom ', pyPlane.numGeom
        pyPlane.reflexed = True
        pyPlane.aligned = True

        nWire = pyW.numWire
        nGeom = pyPl.numGeom
        # print 'pyPl.numWire ', pyPl.numWire
        # print 'pyPl.numGeom ', pyPl.numGeom
        pyPl.reflexed = True
        pyPl.aligned = True
        if not pyAlign.falsify:
            pyPl.shape = None

        # pyPl.rear = []

        aL = pyAlign.aligns

        lenWire = len(pyWire.planes)
        if aL:
            num = aL[-1].numGeom
            chopOne = utils.sliceIndex(num+1, lenWire)
            numC = aL[-1].numWire
        else:
            chopOne = utils.sliceIndex(numGeom+1, lenWire)
            numC = numWire

        aL.append(pyPl)

        if pyAlign.falsify:
            pyAli = None
        else:
            pyAli = self.selectAlignamentBase(nWire, nGeom)
            if pyAli:
                bL = pyAli.aligns
                aL.extend(bL)
                for b in bL:
                    b.angle = [numWire, numGeom]

        pyWireList = self.wires

        if numWire == nWire:
            chopTwo = utils.sliceIndex(nGeom-1, lenWire)
        else:
            lenW = len(pyWireList[nWire].planes)
            chopTwo = utils.sliceIndex(nGeom-1, lenW)

        # print 'chopOne ', (numC, chopOne)
        # print 'chopTwo ', (nWire, chopTwo)

        cL = pyAlign.chops
        pyOne = self.selectPlane(numC, chopOne)
        pyOne.reflexed = True
        pyOne.choped = True
        pyTwo = self.selectPlane(nWire, chopTwo)
        pyTwo.reflexed = True
        pyTwo.choped = True
        cL.append([pyOne, pyTwo])

        if pyAli:
            dL = pyAli.chops
            cL.extend(dL)

        pyAlign.aligns = aL
        pyAlign.chops = cL

        if pyAli:
            # print 'remove'
            self.removeAlignament(pyAli)

    def seatReflex(self, pyWire, pyReflex, pyPlane, direction):

        ''''''

        pyReflex.addLink('planes', pyPlane)
        pyPlane.reflexed = True

        shapeGeomWire = pyWire.shapeGeom
        numWire = pyWire.numWire
        lenWire = len(pyWire.planes)
        numGeom = pyPlane.numGeom
        lineShape = pyPlane.forward
        section = lineShape.section(shapeGeomWire, _Py.tolerance)

        edge = False

        # print[v.Point for v in section.Vertexes]
        # printsection.Edges
        # printlenWire
        # printlen(section.Vertexes)
        # printdirection

        if section.Edges:
            # print'a'
            edge = True
            if direction == 'forward':
                # print'aa'
                vertex = section.Edges[0].Vertexes[0]
            else:
                # print'aaa'
                vertex = section.Edges[-1].Vertexes[1]

        elif len(section.Vertexes) != lenWire:
            # print'b'
            vertex = section.Vertexes[1]

        else:
            # print'c'
            if pyPlane.aligned:
                # print'cc'
                if pyPlane.shape:
                    lineEndPoint = pyPlane.geomAligned.EndPoint
                    if section.Vertexes[0].Point == lineEndPoint:
                        return
                    else:
                        vertex = section.Vertexes[1]
                else:
                    return
            else:
                # print'ccc'
                vertex = section.Vertexes[1]

        # printvertex.Point

        nGeom =\
            self.findRear(pyWire, pyPlane, vertex, direction, edge)

        if direction == 'forward':
            endNum = utils.sliceIndex(numGeom+2, lenWire)
        else:
            endNum = utils.sliceIndex(numGeom-2, lenWire)

        # print'direction, endNum ', direction, endNum

        if nGeom == endNum:
            pyPl = self.selectPlane(numWire, endNum)
            # print'arrow'
            pyPl.arrow = True

    def findRear(self, pyWire, pyPlane, vertex, direction,
                 edge=False):

        ''''''

        shapeGeomWire = pyWire.shapeGeom
        lenWire = len(pyWire.planes)
        section = vertex.section(shapeGeomWire, _Py.tolerance)

        if len(section.Vertexes) > lenWire:
            # print 'a'
            nGeom = -1
            for shape in shapeGeomWire:
                nGeom += 1
                sect = vertex.section([shape], _Py.tolerance)
                if len(sect.Vertexes) > 0:
                    break

        else:
            # print 'b'
            coord = pyWire.coordinates
            nGeom = coord.index(vertex.Point)
            if direction == 'backward':
                nGeom = utils.sliceIndex(nGeom-1, lenWire)

        if edge:
            if direction == 'backward':
                # print 'c'
                nGeom = utils.sliceIndex(nGeom+1, lenWire)
            else:
                # print 'd'
                nGeom = utils.sliceIndex(nGeom-1, lenWire)

        pyPlane.addValue('rear', nGeom, direction)

        return nGeom

    def findAngle(self, nW, nG):

        ''''''

        pyWireList = self.wires

        pyW = pyWireList[nW]
        pyPl = pyW.planes[nG]
        angle = pyPl.angle

        if isinstance(angle, list):
            angle = self.findAngle(angle[0], angle[1])

        return angle

    def findAlignament(self, point):

        ''''''

        for pyWire in self.wires:
            nWire = pyWire.numWire
            coordinates = pyWire.coordinates
            try:
                nGeom = coordinates.index(point)
                break
            except ValueError:
                pass

        return (nWire, nGeom)

    def selectAlignament(self, nWire, nGeom):

        ''''''

        pyWireList = self.wires
        pyWire = pyWireList[nWire]
        pyPlaneList = pyWire.planes
        pyPlane = pyPlaneList[nGeom]

        pyAlignList = self.alignaments
        for pyAlign in pyAlignList:
            if pyAlign.base == pyPlane:
                # print 'a'
                return pyAlign
            elif pyPlane in pyAlign.aligns:
                # print 'b'
                return pyAlign

        return None

    def selectAlignamentBase(self, nWire, nGeom):

        ''''''

        pyWireList = self.wires
        pyWire = pyWireList[nWire]
        pyPlaneList = pyWire.planes
        pyPlane = pyPlaneList[nGeom]

        pyAlignList = self.alignaments
        for pyAlign in pyAlignList:
            if pyAlign.base == pyPlane:
                return pyAlign

        return None

    def selectReflex(self, numWire, numGeom, nGeom):

        ''''''

        pyReflexList = self.wires[numWire].reflexs
        for pyReflex in pyReflexList:
            [pyPlane, pyPl] = pyReflex.planes
            [nn, mm] = [pyPlane.numGeom, pyPl.numGeom]
            if [nn, mm] == [numGeom, nGeom] or [nn, mm] == [nGeom, numGeom]:
                return pyReflex

        return None

    def selectAllReflex(self, numWire, numGeom):

        ''''''

        pyRList = []
        pyReflexList = self.wires[numWire].reflexs
        for pyReflex in pyReflexList:
            [pyPlane, pyPl] = pyReflex.planes
            [nn, mm] = [pyPlane.numGeom, pyPl.numGeom]
            if numGeom in [nn, mm]:
                pyRList.append(pyReflex)

        return pyRList

    def selectPlane(self, nWire, nGeom):

        ''''''

        pyWireList = self.wires
        for wire in pyWireList:
            if wire.numWire == nWire:
                pyPlaneList = wire.planes
                for plane in pyPlaneList:
                    if plane.numGeom == nGeom:
                        return plane

        return None

    def removeAlignament(self, pyAlign):

        ''''''

        pyAlignList = self.alignaments
        pyAlignList.remove(pyAlign)
        self.alignaments = pyAlignList

    def forBack(self, pyPlane, size, direction):

        ''''''

        line = pyPlane.geom

        lineLastParam = line.LastParameter
        lineEndParam = lineLastParam + size
        forwardLine = Part.LineSegment(line, lineLastParam,
                                       lineEndParam)
        # print'forwardLine ', forwardLine
        forwardLineShape = forwardLine.toShape()

        lineStartParam = line.FirstParameter
        lineEndParam = lineStartParam - size
        backwardLine =\
            Part.LineSegment(line, lineStartParam, lineEndParam)
        # print'backwardLine ', backwardLine
        backwardLineShape = backwardLine.toShape()
        # printdirection

        if direction == "forward":
            # print'a'
            pyPlane.backward = backwardLineShape
            pyPlane.forward = forwardLineShape
            return forwardLine

        else:
            # print'b'
            pyPlane.backward = forwardLineShape
            pyPlane.forward = backwardLineShape
            return backwardLine

    def doReflex(self, pyWire, pyPlane):

        ''''''

        pyReflex = _PyReflex()
        pyWire.addLink('reflexs', pyReflex)
        self.seatReflex(pyWire, pyReflex, pyPlane, 'forward')

        return pyReflex

    def doAlignament(self, pyPlane):

        ''''''

        pyAlign = _PyAlignament()
        self.addLink('alignaments', pyAlign)
        pyAlign.base = pyPlane

        return pyAlign

    def priorLaterAlignaments(self):

        ''''''

        pyWireList = self.wires

        for pyAlign in self.alignaments:

            numWire = pyAlign.base.numWire
            numGeom = pyAlign.base.numGeom
            pyWire = pyWireList[numWire]
            pyPlaneList = pyWire.planes
            lenWire = len(pyPlaneList)

            prior = utils.sliceIndex(numGeom-1, lenWire)
            pyPrior = pyPlaneList[prior]

            prior = pyPrior.geomAligned
            if not prior:
                [nW, nG] = pyPrior.angle
                pyPrior = self.selectPlane(nW, nG)

            pyPl = pyAlign.aligns[-1]
            [nW, nG] = [pyPl.numWire, pyPl.numGeom]
            pyW = pyWireList[nW]
            lenW = len(pyW.planes)

            later = utils.sliceIndex(nG+1, lenW)
            pyLater = self.selectPlane(nW, later)

            later = pyLater.geomAligned
            if not later:
                [nW, nG] = pyLater.angle
                pyLater = self.selectPlane(nW, nG)

            pyAlign.prior = pyPrior
            pyAlign.later = pyLater

    def removeExcessReflex(self):

        ''''''

        for pyWire in self.wires:
            pyReflexList = pyWire.reflexs
            # print pyReflexList
            for pyReflex in pyReflexList[:]:
                rr = False
                pyPlaneList = pyReflex.planes
                # print pyPlaneList
                # print[pyPl.numGeom for pyPl in pyPlaneList]
                if len(pyPlaneList) < 2:
                    # print 'a'
                    rr = True
                else:
                    # print 'b'
                    [pyR, pyOppR] = pyPlaneList

                    if ((pyR.aligned or pyR.choped) and
                       (pyOppR.aligned or pyOppR.choped)):
                            # print 'bb'
                            rr = True

                if rr:
                    # print 'c'
                    pyReflexList.remove(pyReflex)
            # print pyReflexList
            pyWire.reflexs = pyReflexList

    def simulatedChops(self):

        ''''''

        for pyAlign in self.alignaments:
            simulatedChops = []
            for [pyChopOne, pyChopTwo] in pyAlign.chops:

                if pyChopOne.aligned:
                    [nWire, nGeom] = [pyChopOne.numWire, pyChopOne.numGeom]
                    chopOne = pyChopOne.shape
                    enormous = pyChopOne.enormousShape
                    geom = pyChopOne.geom
                    if not chopOne:
                        [nWire, nGeom] = pyChopOne.angle
                        pyPlane = self.selectPlane(nWire, nGeom)
                        chopOne = pyPlane.shape
                        enormous = pyPlane.enormousShape
                        geom = pyPlane.geom
                    pyOne = _PyPlane(nWire, nGeom)
                    pyOne.shape = chopOne.copy()
                    pyOne.enormousShape = enormous
                    pyOne.geom = geom
                else:
                    pyOne = pyChopOne

                if pyChopTwo.aligned:
                    [nWire, nGeom] = [pyChopTwo.numWire, pyChopTwo.numGeom]
                    chopTwo = pyChopTwo.shape
                    enormous = pyChopTwo.enormousShape
                    geom = pyChopTwo.geom
                    if not chopTwo:
                        [nWire, nGeom] = pyChopTwo.angle
                        pyPlane = self.selectPlane(nWire, nGeom)
                        chopTwo = pyPlane.shape
                        enormous = pyPlane.enormousShape
                        geom = pyPlane.geom
                    pyTwo = _PyPlane(nWire, nGeom)
                    pyTwo.shape = chopTwo.copy()
                    pyTwo.enormousShape = enormous
                    pyTwo.geom = geom
                else:
                    pyTwo = pyChopTwo

                simulatedChops.append([pyOne, pyTwo])

            pyAlign.simulatedChops = simulatedChops

    def planning(self, size):

        ''''''

        pyWireList = self.wires
        reset = self.reset

        for pyWire in pyWireList:

            pyWire.planning(reset, size)

        pyAlignList = self.alignaments

        for pyAlign in pyAlignList:
            if reset:

                pyAlign.rangging(self)

            pyAlign.ranggingChop(self)

        self.reset = False

    def trimming(self):

        ''''''

        for pyWire in self.wires:
            pyWire.trimming(self)

        for pyAlign in self.alignaments:
            pyAlign.trimming(self)

        self.simulatedChops()

    def priorLater(self):

        ''''''

        for pyWire in self.wires:
            pyWire.priorLater(self)

        for pyAlign in self.alignaments:
            pyAlign.priorLater(self)

    def simulating(self):

        ''''''

        for pyAlign in self.alignaments:
            if not pyAlign.falsify:
                pyAlign.simulatingBase(self)

        for pyAlign in self.alignaments:
            if pyAlign.falsify:
                pyAlign.simulatingBase(self)

        for pyAlign in self.alignaments:
            pyAlign.simulatingChop()

        for pyWire in self.wires:
            pyWire.simulating(self)

    def reflexing(self, face):

        ''''''

        for pyWire in self.wires:
            if pyWire.reflexs:
                pyWire.reflexing(self, face)

    def reviewing(self, face):

        ''''''

        for pyWire in self.wires:
            if len(pyWire.reflexs) > 1:

                pyWire.reviewing()

                solved, unsolved = pyWire.clasifyReflexPlanes()
                # print[p.numGeom for p in solved]
                # print[p.numGeom for p in unsolved]

                pyWire.reSolveReflexs(solved, unsolved)

                pyWire.betweenReflexs()

    def rearing(self):

        ''''''

        for pyWire in self.wires:
            if pyWire.reflexs:
                pyWire.rearing()

    def ordinaries(self):

        ''''''

        for pyWire in self.wires:
            pyWire.ordinaries(self)

    def between(self):

        ''''''

        pyWireList = self.wires
        if len(pyWireList) > 1:

            numWire = -1
            for pyWire in pyWireList:
                numWire += 1
                # print 'numWire ', numWire
                pop = pyWireList.pop(numWire)
                cutterList = []
                for pyW in pyWireList:
                    pyPlaneList = pyW.planes
                    # nW = pyW.numWire
                    for pyPl in pyPlaneList:
                        if not pyPl.choped:
                            if not pyPl.aligned:
                                pl = pyPl.shape
                                cutterList.append(pl)
                pyWireList.insert(numWire, pop)

                for pyPlane in pyWire.planes:
                    # print 'numGeom ', pyPlane.numGeom
                    plane = pyPlane.shape
                    if plane:
                        if cutterList:
                            gS = pyPlane.geomAligned.toShape()
                            plane = plane.cut(cutterList, _Py.tolerance)
                            plane = utils.selectFace(plane.Faces, gS,
                                                     _Py.tolerance)
                            pyPlane.shape = plane

    def aligning(self, face):

        ''''''

        pyAlignList = self.alignaments

        for pyAlign in pyAlignList:
            if not pyAlign.falsify:
                pyAlign.aligning(face, self)

        for pyAlign in pyAlignList:
            if pyAlign.falsify:
                pyAlign.aligning(face, self)

    def ending(self):

        ''''''

        pyAlignList = self.alignaments

        cutterList = []

        for pyAlign in pyAlignList:

            base = pyAlign.base.shape
            if base not in cutterList:
                cutterList.append(base)
                # print 'a', pyAlign.base.numGeom

            for pyPlane in pyAlign.aligns:
                plane = pyPlane.shape
                if plane:
                    if plane not in cutterList:
                        cutterList.append(plane)
                        # print 'b', pyPlane.numGeom

            for [pyChopOne, pyChopTwo] in pyAlign.chops:

                chopOne = pyChopOne.shape
                if chopOne:
                    if chopOne not in cutterList:
                        cutterList.append(chopOne)
                        # print 'c', pyChopOne.numGeom

                chopTwo = pyChopTwo.shape
                if chopTwo:
                    if chopTwo not in cutterList:
                        cutterList.append(chopTwo)
                        # print 'd', pyChopTwo.numGeom

        # print 'cutterList ', cutterList

        if cutterList:

            for pyWire in self.wires:
                for pyPlane in pyWire.planes:
                    plane = pyPlane.shape
                    if plane:
                        # print '1'
                        # print 'numGeom', pyPlane.numGeom

                        if pyPlane.choped or pyPlane.aligned:
                            # print '2'
                            cutterList.remove(plane)

                        plane = plane.cut(cutterList, _Py.tolerance)
                        gS = pyPlane.geom.toShape()
                        plane = utils.selectFace(plane.Faces, gS, _Py.tolerance)
                        pyPlane.shape = plane

                        if pyPlane.choped or pyPlane.aligned:
                            # print '3'
                            cutterList.append(plane)
