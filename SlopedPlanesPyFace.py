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


from math import pi
import FreeCAD
import Part
from SlopedPlanesPy import _Py
from SlopedPlanesPyWire import _PyWire
from SlopedPlanesPyReflex import _PyReflex
from SlopedPlanesPyAlignment import _PyAlignment
from SlopedPlanesPyPlane import _PyPlane


__title__ = "SlopedPlanes Macro"
__author__ = "Damian Caceres Moreno"
__url__ = "http://www.freecadweb.org"


class _PyFace(_Py):

    '''The complementary python object class for faces'''

    def __init__(self, numFace):

        ''''''

        self.numFace = numFace
        self.wires = []
        self.alignments = []
        self.reset = False
        self.shapeGeom = []

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
    def alignments(self):

        ''''''

        return self._alignments

    @alignments.setter
    def alignments(self, alignments):

        ''''''

        self._alignments = alignments

    @property
    def reset(self):

        ''''''

        return self._reset

    @reset.setter
    def reset(self, reset):

        ''''''

        self._reset = reset

    @property
    def shapeGeom(self):

        ''''''

        return self._shapeGeom

    @shapeGeom.setter
    def shapeGeom(self, shapeGeom):

        ''''''

        self._shapeGeom = shapeGeom

    def __getstate__(self):

        '''__getstate__(self)
        Serializes the complementary python objects
        '''

        wireList = []
        for wire in self.wires:
            dct = wire.__dict__.copy()
            dct['_coordinates'] = [[v.x, v.y, v.z] for v in wire.coordinates]
            dct['_shapeGeom'] = []

            planeList = []
            for plane in wire.planes:
                dd = plane.__dict__.copy()

                dd['_shape'] = None
                dd['_bigShape'] = None
                dd['_enormousShape'] = None
                dd['_geom'] = None
                dd['_geomShape'] = None
                dd['_geomAligned'] = None
                dd['_cutter'] = []
                dd['_oppCutter'] = []
                dd['_divide'] = []
                dd['_forward'] = None
                dd['_backward'] = None
                dd['_simulatedShape'] = None
                dd['_compound'] = None

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
        for align in self.alignments:
            dct = {}
            alignList.append(dct)

        return wireList, alignList

    def __setstate__(self, wires, alignments):

        '''__setstate__(self, wires, alignments)
        Deserializes the complementary python objects
        '''

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
        for dct in alignments:
            alignment = _PyAlignment()
            alignList.append(alignment)

        return wireList, alignList

    def parsing(self):

        '''parsing(self)
        Splits the face finding its reflexs corners and alignments'''

        pyWireList = self.wires

        resetFace = self.reset

        if resetFace:
            for pyWire in pyWireList:
                pyWire.reflexs = []     # reset reflexs

        self.alignments = []    # always reset alignments
        shapeGeomFace = self.shapeGeom

        for pyWire in pyWireList:
            numWire = pyWire.numWire
            # print '###### numWire ', numWire
            ref = False     # the second plane of a reflex corner

            lenWire = len(pyWire.planes)
            coord = pyWire.coordinates
            eje = coord[1].sub(coord[0])
            pyPlaneList = pyWire.planes

            for pyPlane in pyPlaneList:
                numGeom = pyPlane.numGeom
                # print '### numGeom ', numGeom, ' angle ', pyPlane.angle

                if not pyPlane.geomAligned:     # has not shape

                    ref = False
                    eje = coord[numGeom+2].sub(coord[numGeom+1])

                else:

                    nextEje = coord[numGeom+2].sub(coord[numGeom+1])
                    corner = self.convexReflex(eje, nextEje, numWire)
                    eje = nextEje

                    if corner == 'convex':
                        if pyPlane.choped:
                            if pyPlane.numWire == 0:
                                if not pyPlane.rear:    # needs a rear
                                    ref = True
                                    pyReflex = _PyReflex()

                    if ref:
                        # print 'ref'
                        forwardLine = self.forBack(pyPlane, 'backward')
                        ref = False

                        if resetFace:
                            if pyPlane.geomAligned:
                                # print 'ref reset'

                                self.seatReflex(pyWire, pyReflex,
                                                pyPlane, 'backward')

                    lineEnd = coord[numGeom+1]

                    if corner == 'reflex' or numWire > 0:
                        # the interior wires always need forwardLine
                        # the reflex for rear and
                        # the convex for alignments
                        # the exterior wires rear and alignaments with reflex
                        forwardLine = self.forBack(pyPlane, 'forward')

                    if ((numWire == 0 and corner == 'reflex') or
                       (numWire > 0 and corner == 'convex')):
                        # does look for alignments
                        # print '1'

                        forward = pyPlane.forward
                        section = forward.section(shapeGeomFace, _Py.tolerance)

                        if section.Edges:
                            # print '11'

                            numEdge = -1
                            for edge in section.Edges:
                                numEdge += 1
                                # print '111'

                                edgeStart = edge.firstVertex(True).Point
                                point = self.roundVector(edgeStart)
                                (nWire, nGeom) =\
                                    self.findAlignment(point)

                                pyW = pyWireList[nWire]
                                pyPl = pyW.planes[nGeom]
                                if pyPl.geomAligned:
                                    # has a shape
                                    # print '1111'
                                    edgeEnd = edge.lastVertex(True).Point
                                    distStart = edgeStart.sub(lineEnd).Length
                                    distEnd = edgeEnd.sub(lineEnd).Length

                                    if distStart < distEnd:
                                        # aligment or falseAlignment
                                        # print '11111'

                                        if numEdge == 0:
                                            pyAlign =\
                                                self.doAlignment(pyPlane)

                                        fAng = self.findAngle(numWire, numGeom)
                                        sAng = self.findAngle(nWire, nGeom)
                                        fGeom = pyPlane.geomAligned
                                        sGeom = pyPl.geomAligned

                                        if fAng == sAng:
                                            # alignment
                                            # print '111111'
                                            pyPl.geomAligned = None
                                            pyPl.angle = [numWire, numGeom]

                                            # TODO curved 

                                            startParam = fGeom.FirstParameter
                                            endPoint = sGeom.EndPoint
                                            endParam =\
                                                forwardLine.parameter(endPoint)
                                            eGeom =\
                                                Part.LineSegment(fGeom,
                                                                 startParam,
                                                                 endParam)
                                            pyPlane.geomAligned = eGeom

                                        else:
                                            # falseAlignment
                                            # print '111112'
                                            if numEdge > 0:
                                                pyAlign =\
                                                    self.doAlignment(pyPlane)
                                            pyAlign.falsify = True

                                        pyAli =\
                                            self.seatAlignment(pyAlign,
                                                               pyWire, pyPlane,
                                                               pyW, pyPl)

                                        if pyPl.numWire == pyPlane.numWire:
                                            ref = True

                                        pyReflex = _PyReflex()

                                        if pyAli:
                                            # print 'break'
                                            break

                                        if pyAlign.falsify:
                                            # print 'break'
                                            break

                                    else:
                                        # no alignment, no falseAlignment
                                        # confrontation directions
                                        # print '11112'
                                        if corner == 'reflex':
                                            # print '111121'
                                            ref = True
                                            if resetFace:
                                                # print '1111211'
                                                pyReflex =\
                                                    self.doReflex(pyWire,
                                                                  pyPlane)
                                            break

                                else:
                                    # hasn't a shape
                                    # prepares the next chop
                                    # print '1112'
                                    if pyPl.numWire == pyPlane.numWire:
                                        ref = True
                                    pyReflex = _PyReflex()

                            else:
                                # finishes alignment
                                # print 'end'
                                if corner == 'reflex':
                                    if resetFace:
                                        self.seatReflex(pyWire, pyReflex,
                                                        pyPlane, 'forward')

                        else:
                            # no alignment
                            # print '12'
                            if corner == 'reflex':
                                # exterior wire reflex
                                # print '121'
                                ref = True
                                if resetFace:
                                    # print '1211'
                                    pyReflex =\
                                        self.doReflex(pyWire, pyPlane)

                    else:
                        # doesn't look for alignments
                        # exterior wires convex
                        # interior wires reflex
                        # print '2'
                        if corner == 'reflex':
                            # interior wire reflex
                            # print '21'
                            if not pyPlane.choped:
                                # print '211'
                                num = self.sliceIndex(numGeom+1, lenWire)
                                pyNextPlane = pyPlaneList[num]
                                if not pyNextPlane.choped:    # is not an alignament
                                    # print '2111'
                                    ref = True
                                    if resetFace:
                                        # print '21111'
                                        pyReflex =\
                                            self.doReflex(pyWire, pyPlane)

                # print self.alignments
                # print[a.base.numGeom for a in self.alignments]
                # print[a.falsify for a in self.alignments]
                # print[[a.numGeom for a in ali.aligns] for ali in self.alignments]
                # print[[(a.numGeom, b.numGeom) for [a, b] in ali.chops] for ali in self.alignments]

            pyWire.reset = False

        self.priorLaterAlignments()

        self.removeExcessReflex()

        # self.printSummary()

    def seatAlignment(self, pyAlign, pyWire, pyPlane, pyW, pyPl):

        '''seatAlignment(self, pyAlign, pyWire, pyPlane, pyW, pyPl)
        pyAlign is the alignment.
        pyPlane is the base plane. pyWire is its wire
        pyPl is the continued plane. pyW is its wire
        If pyAlign finds other alignment return it, pyAli, or return None
        '''

        numWire = pyWire.numWire
        numGeom = pyPlane.numGeom
        # print  'pyPlane ', (numWire, numGeom)
        nWire = pyW.numWire
        nGeom = pyPl.numGeom
        # print  'pyPl ', (nWire, nGeom)

        alignList = pyAlign.aligns
        chopList = pyAlign.chops

        jumpChop = False
        if pyAlign.falsify:
            if pyPlane.aligned:
                pyAliBase = self.selectAlignmentBase(numWire, numGeom)

                if pyAliBase:
                    # a falseAlignment where base plane is an alignment, pyAliBase
                    jumpChop = True
                    pp = pyAliBase.aligns[-1]
                    numWireChopOne = pp.numWire
                    pyw = self.wires[numWireChopOne]
                    lenWire = len(pyw.planes)
                    numGeomChopOne = self.sliceIndex(pp.numGeom+1, lenWire)

        if not jumpChop:

            lenWire = len(pyWire.planes)
            if alignList:
                num = alignList[-1].numGeom
                numGeomChopOne = self.sliceIndex(num+1, lenWire)
                numWireChopOne = alignList[-1].numWire
            else:
                numGeomChopOne = self.sliceIndex(numGeom+1, lenWire)
                numWireChopOne = numWire

        alignList.append(pyPl)

        if pyAlign.falsify:
            pyAli = None
        else:
            pyAli = self.selectAlignmentBase(nWire, nGeom)
            if pyAli:
                # pyAlign finds an alignment, pyAli
                if not pyAli.falsify:
                    bL = pyAli.aligns
                    alignList.extend(bL)
                    for b in bL:
                        b.angle = [numWire, numGeom]

        pyWireList = self.wires
        if numWire == nWire:
            numGeomChopTwo = self.sliceIndex(nGeom-1, lenWire)
        else:
            lenW = len(pyWireList[nWire].planes)
            numGeomChopTwo = self.sliceIndex(nGeom-1, lenW)

        pyOne = self.selectPlane(numWireChopOne, numGeomChopOne)
        pyTwo = self.selectPlane(nWire, numGeomChopTwo)
        chopList.append([pyOne, pyTwo])

        if pyAli:
            if not pyAli.falsify:
                dL = pyAli.chops
                chopList.extend(dL)
                self.removeAlignment(pyAli)     # joined in one alignment

        pyAlign.aligns = alignList
        pyAlign.chops = chopList

        pyPlane.reflexed = True
        pyPlane.aligned = True
        pyPl.reflexed = True
        pyPl.aligned = True
        if not pyAlign.falsify:
            pyPl.shape = None

        pyOne.reflexed = True
        pyOne.choped = True
        pyTwo.reflexed = True
        pyTwo.choped = True

        return pyAli

    def seatReflex(self, pyWire, pyReflex, pyPlane, direction):

        '''seatReflex(self, pyWire, pyReflex, pyPlane, direction)
        '''

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
                    # print 'cc1'
                    lineEndPoint = pyPlane.geomAligned.EndPoint
                    if section.Vertexes[0].Point == lineEndPoint:
                        # print 'cc11'
                        return
                    else:
                        # print 'cc12'
                        vertex = section.Vertexes[1]
                else:
                    # print 'cc2'
                    return
            elif pyPlane.choped:
                # print 'ccc'
                vertex = section.Vertexes[1]
            else:
                # print'cccc'
                vertex = section.Vertexes[1]

        # print vertex.Point

        nGeom =\
            self.findRear(pyWire, pyPlane, vertex, direction, edge)

        if direction == 'forward':
            endNum = self.sliceIndex(numGeom+2, lenWire)
        else:
            endNum = self.sliceIndex(numGeom-2, lenWire)

        if nGeom == endNum:
            pyPl = self.selectPlane(numWire, endNum)
            pyPl.arrow = True

    def findRear(self, pyWire, pyPlane, vertex, direction, edge=False):

        '''findRear(self, pyWire, pyPlane, vertex, direction, edge=False)
        '''

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
            nGeom = coord.index(self.roundVector(vertex.Point))
            if direction == 'backward':
                nGeom = self.sliceIndex(nGeom-1, lenWire)

        if edge:
            if direction == 'backward':
                # print 'c'
                nGeom = self.sliceIndex(nGeom+1, lenWire)
            else:
                # print 'd'
                nGeom = self.sliceIndex(nGeom-1, lenWire)

        pyPlane.addValue('rear', nGeom, direction)

        return nGeom

    def findAngle(self, numWire, numGeom):

        '''findAngle(self, nW, nG)
        '''

        pyWireList = self.wires

        pyW = pyWireList[numWire]
        pyPl = pyW.planes[numGeom]
        angle = pyPl.angle

        if isinstance(angle, list):
            angle = self.findAngle(angle[0], angle[1])

        return angle

    def findAlignment(self, point):

        '''findAlignment(self, point)
        '''

        for pyWire in self.wires:
            numWire = pyWire.numWire
            coordinates = pyWire.coordinates
            try:
                numGeom = coordinates.index(point)
                break
            except ValueError:
                pass

        return (numWire, numGeom)

    def removeAlignment(self, pyAlign):

        '''removeAlignment(self, pyAlign)
        '''

        pyAlignList = self.alignments
        pyAlignList.remove(pyAlign)
        self.alignments = pyAlignList

    def forBack(self, pyPlane, direction):

        '''forBack(self, pyPlane, direction)
        '''

        geom = pyPlane.geom
        firstParam = geom.FirstParameter
        lastParam = geom.LastParameter

        if isinstance(geom, (Part.LineSegment,
                             Part.ArcOfParabola)):

            startParam = lastParam
            endParam = lastParam + _Py.size

            gg = geom
            sParam = firstParam
            eParam = firstParam - _Py.size

        elif isinstance(geom, (Part.ArcOfCircle,
                               Part.ArcOfEllipse)):

            half = (2 * pi - (lastParam - firstParam)) / 2
            startParam = lastParam
            endParam = lastParam + half

            gg = geom.copy()
            gg.Axis = _Py.normal * -1
            sParam = 2 * pi - firstParam
            eParam = sParam + half

        elif isinstance(geom, Part.ArcOfHyperbola):
            pass

        elif isinstance(geom, Part.BSplineCurve):
            pass

        else:
            pass

        forwardLine = self.makeGeom(geom, startParam, endParam)
        # print'forwardLine ', forwardLine
        forwardLineShape = forwardLine.toShape()
        backwardLine = self.makeGeom(gg, sParam, eParam)
        # print'backwardLine ', backwardLine
        backwardLineShape = backwardLine.toShape()

        if direction == "forward":
            pyPlane.backward = backwardLineShape
            pyPlane.forward = forwardLineShape
            return forwardLine

        else:
            pyPlane.backward = forwardLineShape
            pyPlane.forward = backwardLineShape
            return backwardLine

    def doReflex(self, pyWire, pyPlane):

        '''doReflex(self, pyWire, pyPlane)
        '''

        pyReflex = _PyReflex()
        pyWire.addLink('reflexs', pyReflex)
        self.seatReflex(pyWire, pyReflex, pyPlane, 'forward')

        return pyReflex

    def doAlignment(self, pyPlane):

        '''doAlignment(self, pyPlane)
        '''

        pyAlign = _PyAlignment()
        self.addLink('alignments', pyAlign)
        pyAlign.base = pyPlane

        return pyAlign

    def priorLaterAlignments(self):

        '''priorLaterAlignments(self)
        '''

        pyWireList = self.wires

        for pyAlign in self.alignments:

            pyBase = pyAlign.base
            numWire = pyBase.numWire
            numGeom = pyBase.numGeom
            pyWire = pyWireList[numWire]
            pyPlaneList = pyWire.planes
            lenWire = len(pyPlaneList)

            prior = self.sliceIndex(numGeom-1, lenWire)
            pyPrior = self.selectBasePlane(numWire, prior)

            pyPl = pyAlign.aligns[-1]
            [nW, nG] = [pyPl.numWire, pyPl.numGeom]
            pyW = pyWireList[nW]
            lenW = len(pyW.planes)

            later = self.sliceIndex(nG+1, lenW)
            pyLater = self.selectBasePlane(nW, later)

            pyAlign.prior = pyPrior
            pyAlign.later = pyLater

    def removeExcessReflex(self):

        '''removeExcessReflex(self)
        '''

        for pyWire in self.wires:
            pyReflexList = pyWire.reflexs
            for pyReflex in pyReflexList[:]:
                rr = False
                pyPlaneList = pyReflex.planes

                if len(pyPlaneList) < 2:
                    rr = True

                else:
                    [pyR, pyOppR] = pyPlaneList

                    if ((pyR.aligned or pyR.choped) and
                       (pyOppR.aligned or pyOppR.choped)):
                            rr = True

                if rr:
                    pyReflexList.remove(pyReflex)

            pyWire.reflexs = pyReflexList

    def planning(self):

        '''planning(self)
        Transfers to PyWire
        Arranges the alignment ranges
        Rearmes tha face reset system'''

        for pyWire in self.wires:
            pyWire.planning()

        for pyAlign in self.alignments:
            if self.reset:
                pyAlign.rangging()
            pyAlign.ranggingChop()

        self.reset = False

    def upping(self):

        '''upping(self)
        '''

        if _Py.slopedPlanes.Up:

            for pyWire in self.wires:
                for pyPlane in pyWire.planes:
                    plane = pyPlane.shape
                    if plane:
                        gS = pyPlane.geomShape
                        plane = self.cutting(plane, [_Py.upPlane], gS)
                        pyPlane.shape = plane

    def virtualizing(self):

        '''virtualizing(self)
        '''

        for pyAlign in self.alignments:
            pyAlign.virtualizing()

        for pyAlign in self.alignments:
            pyAlign.simulatingChop()

    def trimming(self):

        '''trimming(self)
        Transfers to PyWire and PyAlignment
        Arranges the virtualization of the alignments'''

        for pyWire in self.wires:
            pyWire.trimming()

        for pyAlign in self.alignments:
            pyAlign.trimming()

    def priorLater(self):

        '''priorLater(self)
        '''

        for pyWire in self.wires:
            pyWire.priorLater()

        for pyAlign in self.alignments:
            pyAlign.priorLater()

    def simulating(self):

        '''simulating(self)
        '''

        for pyAlign in self.alignments:
            if not pyAlign.falsify:
                pyAlign.simulatingAlignment()

        for pyAlign in self.alignments:
            if pyAlign.falsify:
                pyAlign.simulatingAlignment()

        for pyAlign in self.alignments:
            pyAlign.simulating()

        for pyWire in self.wires:
            pyWire.simulating()

    def preOrdinaries(self):

        ''''''

        for pyWire in self.wires:
            pyWire.preOrdinaries()

    def reflexing(self):

        '''reflexing(self)
        '''

        for pyWire in self.wires:
            if pyWire.reflexs:
                pyWire.reflexing()

    def reviewing(self):

        '''reviewing(self)
        '''

        for pyWire in self.wires:
            if len(pyWire.reflexs) > 1:

                pyWire.reviewing()

                solved, unsolved = pyWire.clasifyReflexPlanes()

                pyWire.reSolveReflexs(solved, unsolved)

                pyWire.betweenReflexs()

    def rearing(self):

        '''rearing(self)
        '''

        for pyWire in self.wires:
            if pyWire.reflexs:
                pyWire.rearing()

    def ordinaries(self):

        '''ordinaries(self)
        '''

        for pyWire in self.wires:
            pyWire.ordinaries()

    def between(self):

        '''between(self)
        '''

        pyWireList = self.wires[:]
        if len(pyWireList) > 1:

            numWire = -1
            for pyWire in pyWireList:
                numWire += 1
                # print '### numWire ', numWire
                pop = pyWireList.pop(numWire)
                cutterList = []
                aliList = []
                for pyW in pyWireList:
                    # print '# nW', pyW.numWire
                    pyPlaneList = pyW.planes
                    for pyPl in pyPlaneList:
                        if not pyPl.choped:
                            # print pyPl.numGeom
                            if not pyPl.aligned:
                                # print 'a'
                                pl = pyPl.shape
                                cutterList.append(pl)
                            else:
                                # print 'b'
                                pyAlign =\
                                    self.selectAlignmentBase(pyPl.numWire,
                                                             pyPl.numGeom)
                                if pyAlign:
                                    # print 'c'
                                    aliList.append(pyAlign)
                pyWireList.insert(numWire, pop)

                for pyPlane in pyWire.planes:
                    plane = pyPlane.shape
                    if plane:
                        # print 'numGeom ', pyPlane.numGeom
                        totalList = cutterList[:]
                        if aliList:
                            cont = True
                            # print 'aliList ', aliList
                            for pyAlign in aliList:
                                for chop in pyAlign.chops:
                                    # print 'A'
                                    if not cont:
                                        break
                                    for pyPl in chop:
                                        # print 'B'
                                        if ((pyPl.numWire, pyPl.numGeom) ==
                                            (pyPlane.numWire,
                                             pyPlane.numGeom)):
                                            # print 'C'
                                            cont = False
                                            break
                                else:
                                    # print 'D'
                                    totalList.extend(pyAlign.simulatedAlignment)

                        if totalList:
                            gS = pyPlane.geomShape
                            plane = self.cutting(plane, totalList, gS)
                            pyPlane.shape = plane

    def aligning(self):

        '''aligning(self)
        '''

        pyAlignList = self.alignments

        for pyAlign in pyAlignList:
            if not pyAlign.falsify:
                pyAlign.aligning()

        for pyAlign in pyAlignList:
            if pyAlign.falsify:
                pyAlign.aligning()

    def ending(self):

        '''ending(self)
        '''

        pyAlignList = self.alignments

        cutterList = []

        for pyAlign in pyAlignList:

            if isinstance(pyAlign.base.angle, float):
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

                if pyChopOne.geomAligned:
                    chopOne = pyChopOne.shape
                    if chopOne not in cutterList:
                        cutterList.append(chopOne)
                        # print 'c', pyChopOne.numGeom

                if pyChopTwo.geomAligned:
                    chopTwo = pyChopTwo.shape
                    if chopTwo not in cutterList:
                        cutterList.append(chopTwo)
                        # print 'd', pyChopTwo.numGeom

        if cutterList:

            for pyWire in self.wires:
                for pyPlane in pyWire.planes:
                    plane = pyPlane.shape
                    if plane:
                        # print 'numGeom', pyPlane.numGeom

                        if pyPlane.choped or pyPlane.aligned:
                            cutterList.remove(plane)

                        gS = pyPlane.geomShape

                        plane = self.cutting(plane, cutterList, gS)
                        pyPlane.shape = plane

                        if pyPlane.choped or pyPlane.aligned:
                            cutterList.append(plane)
