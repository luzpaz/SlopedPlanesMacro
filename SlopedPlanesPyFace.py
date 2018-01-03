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
        self.reset = True
        self.shapeGeom = []
        self.size = 0

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

    @property
    def size(self):

        ''''''

        return self._size

    @size.setter
    def size(self, size):

        ''''''

        self._size = size

    def __getstate__(self, serialize):

        '''__getstate__(self)
        Serializes the complementary python objects
        '''

        wireList = []
        for pyWire in self.wires:
            dct = pyWire.__dict__.copy()
            dct['_coordinates'] = [[v.x, v.y, v.z] for v in pyWire.coordinates]
            dct['_shapeGeom'] = []

            if serialize:
                edgeList = []
                forBack = []

            planeList = []
            for pyPlane in pyWire.planes:
                dd = pyPlane.__dict__.copy()

                dd['_shape'] = None
                dd['_bigShape'] = None
                dd['_enormousShape'] = None
                dd['_geom'] = None
                dd['_cutter'] = []
                dd['_simulatedShape'] = None

                dd['_geomAligned'] = None

                dd['_seedShape'] = None
                dd['_seedBigShape'] = None

                if serialize:

                    edgeList.append(pyPlane.geomShape)
                    dd['_geomShape'] = None

                    if pyPlane.forward:
                        forBack.extend([pyPlane.forward, pyPlane.backward])
                        dd['_forward'] = 'forward'
                        dd['_backward'] = 'backward'

                else:
                    dd['_geomShape'] = None
                    dd['_geomAligned'] = None
                    dd['_forward'] = None
                    dd['_backward'] = None

                planeList.append(dd)
            dct['_planes'] = planeList

            if serialize:
                ww = Part.Wire(edgeList)
                dct['_shapeGeom'] = ww.exportBrepToString()

                fb = Part.Compound(forBack)
                dct['_forBack'] = fb.exportBrepToString()

            reflexList = []
            for pyReflex in pyWire.reflexs:
                dd = pyReflex.__dict__.copy()
                planes = [[pyPlane.numWire,  pyPlane.numGeom]
                          for pyPlane in pyReflex.planes]
                dd['_planes'] = planes
                reflexList.append(dd)
            dct['_reflexs'] = reflexList

            wireList.append(dct)

        alignList = []
        for pyAlign in self.alignments:
            dct = {}
            alignList.append(dct)

        return wireList, alignList

    def __setstate__(self, wires, alignments, serialize):

        '''__setstate__(self, wires, alignments)
        Deserializes the complementary python objects
        '''

        geomShapeFace = []
        wireList = []
        numWire = -1
        for dct in wires:
            numWire += 1
            pyWire = _PyWire(numWire)

            planeList = []
            numGeom = -1
            nf = -1
            geomShapeWire = []

            if serialize:
                edgeList = Part.Shape()
                edgeList.importBrepFromString(dct['_shapeGeom'])
                edgeList = edgeList.Edges

                forBack = Part.Shape()
                forBack.importBrepFromString(dct['_forBack'])
                forBack = forBack.Edges

            for dd in dct['_planes']:
                numGeom += 1
                pyPlane = _PyPlane(numWire, numGeom)
                pyPlane.__dict__ = dd

                if serialize:

                    if dd['_forward']:
                        nf += 2

                        pyPlane.forward = forBack[nf-1]
                        pyPlane.backward = forBack[nf]

                    geomShape = edgeList[numGeom]

                    pyPlane.geomShape = geomShape

                    geomShapeWire.append(geomShape)

                planeList.append(pyPlane)
            dct['_planes'] = planeList

            reflexList = []
            for dd in dct['_reflexs']:
                pyReflex = _PyReflex()
                for [numWire, numGeom] in dd['_planes']:
                    pyPlane = planeList[numGeom]
                    pyReflex.addLink('planes', pyPlane)
                dd['_planes'] = pyReflex.planes
                pyReflex.__dict__ = dd
                reflexList.append(pyReflex)
            dct['_reflexs'] = reflexList

            coord = dct['_coordinates']
            coordinates = [FreeCAD.Vector(v) for v in coord]
            dct['_coordinates'] = coordinates

            pyWire.__dict__ = dct

            if serialize:
                pyWire.shapeGeom = geomShapeWire
                geomShapeFace.extend(geomShapeWire)

            wireList.append(pyWire)

        alignList = []
        for dct in alignments:
            pyAlignment = _PyAlignment()
            alignList.append(pyAlignment)

        return wireList, alignList, geomShapeFace

    def parsing(self):

        '''parsing(self)
        Splits the face finding its reflex corners and alignments'''

        resetFace = self.reset

        if not resetFace and not self.alignments:
            # self.printSummary()
            return

        pyWireList = self.wires

        if resetFace:
            for pyWire in pyWireList:
                pyWire.reflexs = []  # reset reflexs

        elif self.alignments and _Py.slopedPlanes.Proxy.State is False:
            # print 'reset reflexs planes'
            for pyWire in pyWireList:
                for pyReflex in pyWire.reflexs:
                    planeList = []
                    for pyPlane in pyReflex.planes:
                        if pyPlane.aligned:
                            pyPlane = self.selectPlane(pyPlane.numWire,
                                                       pyPlane.numGeom)
                        planeList.append(pyPlane)
                    pyReflex.planes = planeList

        self.alignments = []  # always reset alignments
        shapeGeomFace = self.shapeGeom

        for pyWire in pyWireList:
            numWire = pyWire.numWire
            # print '###### numWire ', numWire
            ref = False  # the second plane of a reflex corner

            lenWire = len(pyWire.planes)
            coord = pyWire.coordinates
            # print 'coordinates ', coord
            eje = coord[1].sub(coord[0])
            pyPrePlane = None  # the first corner always convex
            pyPlaneList = pyWire.planes

            refList, preList = [], []

            for pyPlane in pyPlaneList:
                numGeom = pyPlane.numGeom
                # print '### numGeom ', numGeom, ' angle ', pyPlane.angle

                if not pyPlane.geomAligned:
                    eje = coord[numGeom+2].sub(coord[numGeom+1])

                else:
                    nextEje = coord[numGeom+2].sub(coord[numGeom+1])
                    corner = self.convexReflex(eje, nextEje, numWire)
                    # print 'corner ', corner
                    eje = nextEje

                    if resetFace:

                        try:
                            index = refList.index([numWire, numGeom])
                            ref = True
                            pyPrePlane = preList[index]
                        except ValueError:
                            pass

                        if ref:
                            # print 'ref'
                            self.forBack(pyPlane, 'backward')
                            forward = pyPlane.forward
                            section = forward.section(shapeGeomFace,
                                                      _Py.tolerance)
                            if section.Edges:
                                # print 'edges'
                                edge = section.Edges[0]

                                edgeStart = edge.firstVertex(True).Point
                                edgeEnd = edge.lastVertex(True).Point
                                lineEnd = pyWire.coordinates[numGeom]  # TODO revisar
                                distStart = edgeStart.sub(lineEnd).Length
                                distEnd = edgeEnd.sub(lineEnd).Length

                                if distStart > distEnd and numWire == 0:  # TODO revisar
                                    # print 'alignament'
                                    pass

                                else:
                                    # print 'no alignament '
                                    self.findRear(pyWire, pyPrePlane,
                                                  'forward')
                                    self.findRear(pyWire, pyPlane,
                                                  'backward')
                                    self.doReflex(pyWire, pyPrePlane, pyPlane)

                            else:
                                # print 'no alignament'
                                self.findRear(pyWire, pyPrePlane, 'forward')
                                self.findRear(pyWire, pyPlane, 'backward')
                                self.doReflex(pyWire, pyPrePlane, pyPlane)

                            ref = False

                        if corner == 'reflex' or numWire > 0:
                            # print '0'
                            # interior wires always need forwardLine
                            # the reflex for rear and
                            # the convex for alignments
                            # exterior wires rear and alignaments with reflex
                            self.forBack(pyPlane, 'forward')

                    if ((numWire == 0 and corner == 'reflex') or
                       (numWire > 0 and corner == 'convex')):
                        # print '1'  # does look for alignments

                        forward = pyPlane.forward
                        section = forward.section(shapeGeomFace, _Py.tolerance)

                        if section.Edges:
                            # print '11 possible alignament'

                            numEdge = -1
                            for edge in section.Edges:
                                numEdge += 1
                                # print '111 edge by edge'

                                edgeStart = edge.firstVertex(True).Point
                                edgeEnd = edge.lastVertex(True).Point
                                lineEnd = pyWire.coordinates[numGeom+1]  # TODO revisar
                                distStart = edgeStart.sub(lineEnd).Length
                                distEnd = edgeEnd.sub(lineEnd).Length

                                if distStart < distEnd:  # TODO revisar
                                    # print '1111 aligment'

                                    point = self.roundVector(edgeStart)
                                    (nWire, nGeom) = self.findAlignment(point)
                                    pyW = self.wires[nWire]
                                    pyPl = self.selectPlane(nWire, nGeom)

                                    if pyPl.geomAligned:
                                        # print '11111 has a shape'

                                        if numEdge == 0:
                                            pyAlign =\
                                                self.doAlignment(pyPlane)

                                        fAng = self.findAngle(numWire, numGeom)
                                        sAng = self.findAngle(nWire, nGeom)
                                        fGeom = pyPlane.deGeom()
                                        sGeom = pyPl.deGeom()

                                        if fAng == sAng:
                                            # print '111111 alignment'
                                            pyPl.geomAligned = None
                                            pyPl.angle = [numWire, numGeom]

                                            # TODO curved 

                                            forwardLine = forward.Curve

                                            startParam = fGeom.FirstParameter
                                            endPoint = sGeom.EndPoint
                                            endParam =\
                                                forwardLine.parameter(endPoint)
                                            eGeom =\
                                                Part.LineSegment(fGeom,
                                                                 startParam,
                                                                 endParam)
                                            pyPlane.geomAligned =\
                                                eGeom.toShape()

                                        else:
                                            # print '111112 falseAlignment'
                                            if numEdge > 0:
                                                pyAlign =\
                                                    self.doAlignment(pyPlane)
                                            pyAlign.falsify = True

                                        pyAli =\
                                            self.seatAlignment(pyAlign,
                                                               pyWire, pyPlane,
                                                               pyW, pyPl)

                                        if pyAli:
                                            # print 'break other alignament'
                                            ref = False
                                            break

                                        if pyAlign.falsify:
                                            # print 'break false alignament'
                                            ref = False
                                            break

                                else:
                                    # print '11112 confront directions'
                                    if resetFace:
                                        # print '111121'
                                        if corner == 'reflex':
                                            # print '1111211'
                                            if ref:
                                                # print 'ref'
                                                self.findRear(pyWire,
                                                              pyPlane,
                                                              'backward')
                                                self.findRear(pyWire, pyPlane,
                                                              'forward')
                                            ref = True
                                        break

                            else:
                                # print 'end alignment'
                                if resetFace:

                                    pyEnd = pyAlign.aligns[-1]
                                    if not pyEnd.rear:
                                        nn = pyPl.numGeom
                                        lenW = len(pyW.planes)
                                        num = self.sliceIndex(nn+1, lenW)
                                        pyNextPlane = pyW.planes[num]
                                        coo = pyW.coordinates
                                        jj = coo[num].sub(coo[nn])
                                        nnjj = coo[num+1].sub(coo[num])
                                        corner = self.convexReflex(jj, nnjj,
                                                                   pyW.numWire)

                                        if corner == 'reflex':
                                            # print 'reflex'
                                            if not pyPl.forward:
                                                refList.append([pyW.numWire,
                                                                num])
                                                # print 'refList ', refList
                                                preList.append(pyPlane)
                                                # print preList

                                        ref = False

                        else:
                            # print '12 no alignment'
                            if resetFace:
                                # print '121'
                                if corner == 'reflex':
                                    # print '1211 exterior wire reflexed'
                                    if not pyPlane.choped:
                                        # print '12111'
                                        if ref:
                                            # print 'ref'
                                            pyPlane.addValue('forward',
                                                             pyPlane.backward,
                                                             'backward')
                                            pyPlane.addValue('backward',
                                                             pyPlane.forward,
                                                             'backward')
                                            self.findRear(pyWire, pyPlane,
                                                          'backward')
                                            self.doReflex(pyWire, pyPrePlane,
                                                          pyPlane)
                                        ref = True

                    else:
                        # print '2 does not look for alignments'
                        # exterior wires convex, interior wires reflex
                        if resetFace:
                            if corner == 'reflex':
                                # print '21 interior wire reflex'
                                if not pyPlane.choped:
                                    # print '211 is not choped'
                                    num = self.sliceIndex(numGeom+1, lenWire)
                                    pyNextPlane = pyPlaneList[num]
                                    if not pyNextPlane.choped:
                                        # print '2111 next is not alignament'
                                        ref = True

                pyPrePlane = pyPlane

                # print pyWire.reflexs
                # print self.alignments
                # print[a.base.numGeom for a in self.alignments]
                # print[a.falsify for a in self.alignments]
                # print[[a.numGeom for a in ali.aligns] for ali in self.alignments]
                # print[[(a.numGeom, b.numGeom) for [a, b] in ali.chops] for ali in self.alignments]
                # print '######'

            pyWire.reset = False

        self.priorLaterAlignments()

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
        # print 'pyPlane ', (numWire, numGeom)
        nWire = pyW.numWire
        nGeom = pyPl.numGeom
        # print 'pyPl ', (nWire, nGeom)

        alignList = pyAlign.aligns
        chopList = pyAlign.chops

        jumpChop = False
        if pyAlign.falsify:
            if pyPlane.aligned:
                pyAliBase = self.selectAlignmentBase(numWire, numGeom)

                if pyAliBase:
                    # a falseAlignment where base plane is aligned (and not falsify, of course), pyAliBase
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
                # pyAlign finds an alignment (could be falsify), pyAli
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

        if self.reset:

            if numWireChopOne == 0:
                self.forBack(pyOne, 'backward')
                self.findRear(pyWireList[numWireChopOne], pyOne, 'backward')

            if nWire == 0:
                self.forBack(pyTwo, 'forward')
                self.findRear(pyW, pyTwo, 'forward')

        chopList.append([pyOne, pyTwo])

        if pyAli:
            if not pyAli.falsify:
                dL = pyAli.chops
                chopList.extend(dL)
                self.removeAlignment(pyAli)  # joined in one alignment

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

    def findRear(self, pyWire, pyPlane, direction):

        '''findRear(self, pyWire, pyPlane, direction)
        finds the rear plane of a reflexed plane
        also determines if a arrow situacion happens'''

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

        shapeGeomWire = pyWire.shapeGeom
        lenWire = len(pyWire.planes)
        section = vertex.section(shapeGeomWire, _Py.tolerance)

        if len(section.Vertexes) > lenWire:
            # print '1'
            nGeom = -1
            for shape in shapeGeomWire:
                nGeom += 1
                sect = vertex.section([shape], _Py.tolerance)
                if len(sect.Vertexes) > 0:
                    break

        else:
            # print '2'
            coord = pyWire.coordinates
            nGeom = coord.index(self.roundVector(vertex.Point))
            if direction == 'backward':
                nGeom = self.sliceIndex(nGeom-1, lenWire)

        if edge:
            if direction == 'backward':
                # print '3'
                nGeom = self.sliceIndex(nGeom+1, lenWire)
            else:
                # print '4'
                nGeom = self.sliceIndex(nGeom-1, lenWire)

        # print 'nGeom ', nGeom

        pyPlane.addValue('rear', nGeom, direction)

        if direction == 'forward':
            endNum = self.sliceIndex(numGeom+2, lenWire)
        else:
            endNum = self.sliceIndex(numGeom-2, lenWire)

        if nGeom == endNum:
            pyPl = self.selectPlane(numWire, endNum)
            pyPl.arrow = True

    def findAngle(self, numWire, numGeom):

        '''findAngle(self, nW, nG)
        '''

        angle = self.wires[numWire].planes[numGeom].angle

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
            # print 'a'
            pyPlane.backward = backwardLineShape
            pyPlane.forward = forwardLineShape

        else:
            # print 'b'
            pyPlane.backward = forwardLineShape
            pyPlane.forward = backwardLineShape

    def doReflex(self, pyWire, pyPlane, pyPl):

        '''doReflex(self, pyWire, pyPlane, pyPl)
        '''

        pyPlane.reflexed = True
        pyPl.reflexed = True
        pyReflex = _PyReflex()
        pyWire.addLink('reflexs', pyReflex)
        pyReflex.addLink('planes', pyPlane)
        pyReflex.addLink('planes', pyPl)

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

        # self.printSummary()

    def upping(self):

        '''upping(self)
        '''

        if _Py.slopedPlanes.Up:

            planeList = []
            for pyWire in self.wires:
                for pyPlane in pyWire.planes:
                    plane = pyPlane.shape
                    if plane:
                        planeList.append(plane)

            compound = Part.makeCompound(planeList)
            boundBox = compound.BoundBox
            diaLen = boundBox.DiagonalLength
            center = boundBox.Center
            upPlane = Part.makePlane(diaLen, diaLen,
                                     center.sub(FreeCAD.Vector(diaLen/2,
                                                               diaLen/2,
                                                               center.z)))

            up = _Py.slopedPlanes.Up
            if _Py.reverse:
                up = -1 * up
            upPlane.Placement.Base.z = up

            upList = _Py.upList
            upList.append(upPlane)
            _Py.upList = upList

            for pyWire in self.wires:
                for pyPlane in pyWire.planes:
                    plane = pyPlane.shape
                    if plane:
                        gS = pyPlane.geomShape
                        plane = self.cutting(plane, [upPlane], gS)
                        pyPlane.shape = plane

    def virtualizing(self):

        '''virtualizing(self)
        '''

        for pyAlign in self.alignments:
            pyAlign.virtualizing()

        for pyAlign in self.alignments:
            pyAlign.simulatingChop()

        # self.printControl('virtualizing')

    def trimming(self):

        '''trimming(self)
        Transfers to PyWire and PyAlignment
        '''

        for pyWire in self.wires:
            pyWire.trimming()

        # self.printControl('trimming reflexs')

        for pyAlign in self.alignments:
            pyAlign.trimming()

        # self.printControl('trimming alignments')

    def priorLater(self):

        '''priorLater(self)
        '''

        for pyWire in self.wires:
            pyWire.priorLater()

        # self.printControl('priorLater wires')

        for pyAlign in self.alignments:
            pyAlign.priorLater()

        # self.printControl('priorLater alignments')

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

    def reflexing(self):

        '''reflexing(self)
        '''

        for pyWire in self.wires:
            if pyWire.reflexs:
                pyWire.reflexing()

        # self.printControl('reflexing')

    def ordinaries(self):

        '''ordinaries(self)
        '''

        for pyWire in self.wires:
            pyWire.ordinaries()

        # self.printControl('ordinaries')

    def betweenWires(self):

        '''betweenWires(self)
        '''

        print '###### betweenWires'

        self.printSummary()

        pyWireList = self.wires[:]
        if len(pyWireList) > 1:

            tolerance = _Py.tolerance

            numWire = -1
            for pyWire in pyWireList:
                numWire += 1
                print '### numWire ', numWire
                pop = pyWireList.pop(numWire)

                cutterList = []
                aliList = []

                for pyW in pyWireList:
                    print '# nW', pyW.numWire
                    pyPlaneList = pyW.planes
                    for pyPl in pyPlaneList:
                        print pyPl.numGeom

                        if not pyPl.choped:
                            print 'A'

                            if not pyPl.aligned:
                                print 'a'
                                pl = pyPl.shape
                                cutterList.append(pl)

                            else:
                                print 'b'
                                pyAlign =\
                                    self.selectAlignmentBase(pyPl.numWire,
                                                             pyPl.numGeom)
                                if pyAlign:
                                    print 'c'
                                    aliList.append(pyAlign)

                pyWireList.insert(numWire, pop)

                for pyPlane in pyWire.planes:
                    plane = pyPlane.shape
                    if plane:
                        print 'numGeom ', pyPlane.numGeom
                        gS = pyPlane.geomShape
                        totalList = cutterList[:]

                        if aliList:
                            print 'aliList ', aliList

                            for pyAlign in aliList:
                                cont = True

                                for chop in pyAlign.chops:
                                    print 'aa'

                                    if not cont:
                                        break

                                    for pyPl in chop:
                                        print 'bb'
                                        if ((pyPl.numWire, pyPl.numGeom) ==
                                            (pyPlane.numWire,
                                             pyPlane.numGeom)):
                                            print 'cc'
                                            cont = False
                                            break

                                else:
                                    if cont:
                                        print 'D'
                                        totalList.extend(pyAlign.simulatedAlignment)

                        if totalList:

                            if isinstance(plane, Part.Compound):
                                print 'A'

                                if len(plane.Faces) > 1:
                                    print 'A1'

                                    fList = []
                                    for ff in plane.Faces:
                                        ff = ff.cut(totalList, tolerance)
                                        fList.append(ff.Faces[0])
                                    compound = Part.makeCompound(fList)
                                    pyPlane.shape = compound

                                else:
                                    print 'A2'

                                    plane = plane.cut(totalList, tolerance)
                                    fList = []
                                    ff = self.cutting(plane, totalList, gS)
                                    fList.append(ff)
                                    plane = plane.removeShape([ff])
                                    for ff in plane.Faces:
                                        section = ff.section(fList, tolerance)
                                        if not section.Edges:
                                            fList.append(ff)
                                            break
                                    compound = Part.makeCompound(fList)
                                    pyPlane.shape = compound

                            else:
                                print 'B'
                                plane = self.cutting(plane, totalList, gS)
                                pyPlane.shape = plane

    def aligning(self):

        '''aligning(self)
        '''

        # self.printSummary()

        pyAlignList = self.alignments

        for pyAlign in pyAlignList:
            if not pyAlign.falsify:
                pyAlign.aligning()

        for pyAlign in pyAlignList:
            if pyAlign.falsify:
                pyAlign.aligning()

        # self.printControl('aligning')

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

        # print cutterList

        if cutterList:

            for pyWire in self.wires:
                for pyPlane in pyWire.planes:
                    plane = pyPlane.shape
                    if plane:
                        # print 'numGeom', pyPlane.numGeom

                        if pyPlane.choped or pyPlane.aligned:
                            cutterList.remove(plane)

                            if pyPlane.choped:
                                fList = []
                                for ff in plane.Faces:
                                    ff = ff.cut(cutterList, _Py.tolerance)
                                    fList.append(ff.Faces[0])

                                plane = Part.makeCompound(fList)
                                pyPlane.shape = plane

                            else:
                                gS = pyPlane.geomShape
                                plane = self.cutting(plane, cutterList, gS)
                                pyPlane.shape = plane

                            cutterList.append(plane)

                        else:
                            gS = pyPlane.geomShape
                            plane = self.cutting(plane, cutterList, gS)
                            pyPlane.shape = plane

        # self.printControl('ending')

        pyWireList = _Py.pyFace.wires
        pyPlaneList = pyWireList[0].planes

        for pyAlign in pyAlignList:
            rearRango = pyAlign.rearRango
            rango = pyAlign.rango
            numChop = -1
            for chop in pyAlign.chops:
                numChop += 1
                rearRan = rearRango[numChop]
                # print 'rearRan ', rearRan
                ran = rango[numChop]
                # print 'ran ', ran
                for nn in ran:
                    # print '### nn ', nn
                    # solo los chops exteriores tienen rear
                    pyPlane = pyPlaneList[nn]
                    gS = pyPlane.geomShape
                    for mm in rearRan:
                        if mm != nn:
                            # print '### mm ', mm
                            pyPl = pyPlaneList[mm]
                            pl = pyPl.shape
                            # print pl
                            plane = pyPlane.shape
                            # print plane

                            if pl and plane:

                                pl = self.cutting(pl, [plane], pyPl.geomShape)
                                pyPl.shape = pl

                                plane = self.cutting(plane, [pl], gS)
                                pyPlane.shape = plane

        # self.printControl('moreEnding')
