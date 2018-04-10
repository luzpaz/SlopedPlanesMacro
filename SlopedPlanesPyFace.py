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
__version__ = ""


class _PyFace(_Py):

    '''The complementary python object class for the faces resulting
    to apply the FaceMaker to the SlopedPlanes base.
    The faces could have several wires, and as a consequense holes.'''

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

        '''__getstate__(self, serialize)
        Serializes the complementary python objects.'''

        wireList, serialList = [], []
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
                dd['_lineInto'] = None

                dd['_under'] = []
                dd['_seed'] = []

                dd['_virtuals'] = []
                dd['_reallySolved'] = False

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
                    # TODO también quitar rear y rangos para recalcular todo

                planeList.append(dd)
            dct['_planes'] = planeList

            if serialize:
                ww = Part.Wire(edgeList)
                ss = Part.Compound([ww] + forBack)
                serialList.append(ss)

            reflexList = []
            for pyReflex in pyWire.reflexs:
                dd = pyReflex.__dict__.copy()
                planes = [[pyPlane.numWire, pyPlane.numGeom]
                          for pyPlane in pyReflex.planes]
                dd['_planes'] = planes
                reflexList.append(dd)
            dct['_reflexs'] = reflexList

            wireList.append(dct)

        alignList = []
        for pyAlign in self.alignments:
            dct = {}
            alignList.append(dct)

        return wireList, alignList, serialList

    def __setstate__(self, wires, alignments, serialize, compound):

        '''__setstate__(self, wires, alignments, serialize, compound)
        Deserializes the complementary python objects.'''

        geomShapeFace = []
        wireList = []
        numWire = -1

        if serialize:

            ww = compound.Wires[:]
            compound = compound.removeShape(ww)
            forBack = compound.Edges
            nf = -1

        for dct in wires:
            numWire += 1
            pyWire = _PyWire(numWire)

            planeList = []
            numGeom = -1

            geomShapeWire = []

            if serialize:

                wire = ww[numWire]
                edgeList = wire.Edges

            for dd in dct['_planes']:
                numGeom += 1
                pyPlane = _PyPlane(numWire, numGeom)
                pyPlane.__dict__ = dd

                if serialize:

                    if dd['_forward']:
                        nf += 2

                        pyPlane.forward = forBack[nf - 1]
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
                    pyReflex.planes.append(pyPlane)
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

    def faceManager(self):

        '''faceManager(self)'''

        self.parsing()

        self.planning()
        self.printSummary()

        self.upping()

        self.virtualizing()

        self.trimming()
        # self.printControl('trimming')

        self.priorLater()
        # self.printControl('priorLater')

        self.simulating()
        # self.printControl('simulating')

        self.reflexing()
        # self.printControl('reflexing')

        self.ordinaries()
        # self.printControl('ordinaries')

        self.betweenWires()

        pyAlignList = self.alignments

        for pyAlign in pyAlignList:
            if pyAlign.falsify:
                pyAlign.aligning()

        for pyAlign in pyAlignList:
            if not pyAlign.falsify:
                pyAlign.aligning()

        # self.printControl('aligning')

        for pyAlign in pyAlignList:
            pyAlign.postProcess()
        # self.printControl('postProcess')

        self.postProcess()

        # self.printSummary()

        # '''

    def parsing(self):

        '''parsing(self)
        Splits the pyFace object finding its reflex corners and alignments.'''

        # print '######### parsing'

        resetFace = self.reset
        # print 'resetFace ', resetFace

        if not resetFace and not self.alignments:
            return

        pyWireList = self.wires
        shapeGeomFace = self.shapeGeom
        tolerance = _Py.tolerance

        if resetFace:
            shapeGeomFace = Part.Wire(shapeGeomFace)    # earthquake in migration to occ 7.2
            for pyWire in pyWireList:
                pyWire.reflexs = []  # reset reflexs

        elif self.alignments:
            for pyWire in pyWireList:
                for pyReflex in pyWire.reflexs:
                    planeList = []
                    for pyPlane in pyReflex.planes:
                        if pyPlane.aligned:
                            pyPlane = self.selectPlane(pyPlane.numWire,
                                                       pyPlane.numGeom)
                        planeList.append(pyPlane)  # reset reflexs planes
                    pyReflex.planes = planeList

        self.alignments = []  # always reset alignments

        refList = []    # covers the reflexs conected with alignment

        for pyWire in pyWireList:
            numWire = pyWire.numWire
            # print '###### numWire ', numWire

            ref = False
            pyPrePlane = None

            pyPlaneList = pyWire.planes
            coord = pyWire.coordinates

            eje = coord[1].sub(coord[0])

            for pyPlane in pyPlaneList:
                numGeom = pyPlane.numGeom
                # print '### numGeom ', numGeom, ' angle ', pyPlane.angle

                if len(coord) == 2:
                    # print 'circle or ellipse'
                    break

                nextEje = coord[numGeom + 2].sub(coord[numGeom + 1])
                corner = self.convexReflex(eje, nextEje)
                # print 'corner ', corner
                eje = nextEje

                if not pyPlane.geomAligned:
                    # print 'A'

                    if not pyPlane.forward:
                        # due to falseAlignment concatenated with alignment
                        self.forBack(pyPlane, 'forward')

                    ref = False

                else:
                    # print 'B'

                    if resetFace:
                        # print '0'

                        if [numWire, numGeom] in refList:
                            # print 'refList'
                            self.forBack(pyPrePlane, 'forward')
                            ref = True

                        if ref:
                            # print 'ref'
                            self.forBack(pyPlane, 'backward')

                            forward = pyPlane.forward
                            section = forward.section(shapeGeomFace, tolerance)

                            if section.Edges:
                                # print 'edges'
                                edge = section.Edges[0]

                                edgeStart = edge.firstVertex(True).Point
                                # print 'edgeStart ', edgeStart
                                edgeEnd = edge.lastVertex(True).Point
                                # print 'edgeEnd ', edgeEnd

                                lineStart = coord[numGeom]
                                # print 'lineStart ', lineStart

                                distStart = edgeStart.sub(lineStart).Length
                                # print 'distStart ', distStart
                                distEnd = edgeEnd.sub(lineStart).Length
                                # print 'distEnd ', distEnd

                                if distStart < distEnd:
                                    into, lineInto =\
                                        self.into(lineStart, edgeStart)
                                else:
                                    into, lineInto =\
                                        self.into(lineStart, edgeEnd)

                                if distStart > distEnd and into:
                                    # print 'alignment'
                                    pass

                                else:
                                    # print 'no alignment '
                                    if not into:
                                        # print 'no into'
                                        if distStart > distEnd:
                                            # print 'distStart > distEnd'
                                            pyPlane.lineInto = lineInto
                                    rearF =\
                                        self.findRear(pyWire, pyPrePlane,
                                                      'forward')
                                    rearB =\
                                        self.findRear(pyWire, pyPlane,
                                                      'backward')
                                    pyReflex =\
                                        self.doReflex(pyWire, pyPrePlane,
                                                      pyPlane)
                                    pyReflex.addValue('rear', rearF,
                                                      'forward')
                                    pyReflex.addValue('rear', rearB,
                                                      'backward')

                            else:
                                # print 'no alignament'
                                rearF =\
                                    self.findRear(pyWire, pyPrePlane,
                                                  'forward')
                                rearB =\
                                    self.findRear(pyWire, pyPlane,
                                                  'backward')
                                pyReflex =\
                                    self.doReflex(pyWire, pyPrePlane, pyPlane)
                                pyReflex.addValue('rear', rearF, 'forward')
                                pyReflex.addValue('rear', rearB, 'backward')

                            ref = False

                        if corner == 'reflex':

                            self.forBack(pyPlane, 'forward')

                    if corner == 'reflex':
                        # print '1 Reflex: does look for alignments'

                        if not pyPlane.forward:
                            # due to falseAlignment concatenated with alignment
                            self.forBack(pyPlane, 'forward')

                        forward = pyPlane.forward
                        section = forward.section(shapeGeomFace, tolerance)

                        if section.Edges:
                            # print '11 possible alignment'

                            lineEnd = coord[numGeom + 1]
                            # print 'lineEnd ', lineEnd

                            numEdge = -1
                            pyPl = pyPlane
                            for edge in section.Edges:
                                numEdge += 1
                                # print '111 edge by edge'

                                edgeStart = edge.firstVertex(True).Point
                                # print 'edgeStart ', edgeStart
                                edgeEnd = edge.lastVertex(True).Point
                                # print 'edgeEnd ', edgeEnd

                                distStart = edgeStart.sub(lineEnd).Length
                                # print 'distStart ', distStart
                                distEnd = edgeEnd.sub(lineEnd).Length
                                # print 'distEnd ', distEnd

                                if distStart < distEnd:
                                    into, lineInto = self.into(lineEnd,
                                                               edgeStart)
                                else:
                                    into, lineInto = self.into(lineEnd,
                                                               edgeEnd)

                                if into:
                                    lineEnd = edgeEnd

                                if distStart < distEnd and into:
                                    # print '1111 aligment'

                                    pyPlMemo = pyPl

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

                                        fGeom = pyPlane.doGeom()
                                        sGeom = pyPl.doGeom()

                                        forwardLine = forward.Curve

                                        startParam = fGeom.FirstParameter
                                        endPoint =\
                                            sGeom.value(sGeom.LastParameter)
                                        endParam =\
                                            forwardLine.parameter(endPoint)

                                        eGeom = self.makeGeom(fGeom,
                                                              startParam,
                                                              endParam)

                                        # print eGeom

                                        eGeomShape = eGeom.toShape()

                                        if fAng == sAng:
                                            # print '111111 alignment'
                                            pyPl.geomAligned = None
                                            pyPl.angle = [numWire, numGeom]
                                            pyPlane.geomAligned = eGeomShape

                                        else:
                                            # print '111112 falseAlignment'
                                            if numEdge > 0:
                                                pyAlign =\
                                                    self.doAlignment(pyPlMemo)
                                            pyAlign.falsify = True

                                        pyAlign.geomAligned = eGeomShape

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

                                elif not into:
                                    # print '1112 interference'
                                    ref = True
                                    if distStart < distEnd:
                                        pyPl.lineInto = lineInto
                                    break

                                else:
                                    # print '1113 confront directions'
                                    if resetFace:
                                        # print '11131'
                                        if corner == 'reflex':
                                            # print '111311'

                                            ref = True

                                        break

                            else:
                                # print 'end alignment'
                                if resetFace:

                                    nn = pyPl.numGeom
                                    lenW = len(pyW.planes)
                                    num = self.sliceIndex(nn + 1, lenW)
                                    coo = pyW.coordinates
                                    jj = coo[num].sub(coo[nn])
                                    nnjj = coo[num + 1].sub(coo[num])
                                    corner = self.convexReflex(jj, nnjj)

                                    if corner == 'reflex':
                                        # print 'reflex'
                                        refList.append([pyW.numWire, num])
                                        # print 'refList ', refList

                                    ref = False

                        else:
                            # print '12 no alignment'
                            if resetFace:
                                # print '121'
                                if corner == 'reflex':
                                    # print '1211 reflexed'
                                    ref = True

                    else:
                        # print '2 Convex: does not look for alignments'
                        pass

                pyPrePlane = pyPlane

                # print 'reflex ', pyWire.reflexs
                # print 'alignments ', self.alignments

            if resetFace:
                if numWire > 0:
                    # print 'firstPlane'

                    firstPlane = pyPlaneList[0]

                    if not firstPlane.aligned:
                        # print 'firstPlane no aligned'
                        pyReflex = self.doReflex(pyWire, pyPlane, firstPlane)

                    else:
                        # print 'firstPlane no aligned'

                        if not pyPlane.choped:
                            # print 'pyPlane no choped'
                            pyReflex =\
                                self.doReflex(pyWire, pyPlane, firstPlane)

                        else:
                            pyAlignmentList =\
                                self.selectAlignmentsChop(numWire, numGeom)
                            pyAlignment = self.selectAlignmentBase(numWire, 0)
                            if pyAlignment:
                                if pyAlignment not in pyAlignmentList:
                                    # print 'pyPlane no chop of firstPlane'
                                    pyReflex =\
                                        self.doReflex(pyWire, pyPlane,
                                                      firstPlane)

                    # this reflex hasn't rear
                    if pyReflex:
                        pyReflex.rear = [None, None]

            pyWire.reset = False

        self.priorLaterAlignments()

    def into(self, pointOne, pointTwo):

        '''into(self, pointOne, pointTwo)'''

        # print 'pointOne ', pointOne
        # print 'pointTwo ', pointTwo

        tolerance = _Py.tolerance
        into = False
        face = self.face
        lineInto = Part.LineSegment(pointOne, pointTwo)
        lIS = lineInto.toShape()
        sect = face.section([lIS], tolerance)
        if sect.Edges:
            if len(sect.Vertexes) == 2:
                into = True

        return into, lIS

    def seatAlignment(self, pyAlign, pyWire, pyPlane, pyW, pyPl):

        '''seatAlignment(self, pyAlign, pyWire, pyPlane, pyW, pyPl)
        pyAlign is the alignment.
        pyPlane is the base plane. pyWire is its wire.
        pyPl is the continued plane. pyW is its wire.
        If pyAlign finds other alignment return it, pyAli, or return None.'''

        numWire = pyWire.numWire
        numGeom = pyPlane.numGeom
        # print 'pyPlane ', (numWire, numGeom)
        nWire = pyW.numWire
        nGeom = pyPl.numGeom
        # print 'pyPl ', (nWire, nGeom)

        alignList = pyAlign.aligns
        chopList = pyAlign.chops

        # chop one

        jumpChop = False
        if pyAlign.falsify:
            if pyPlane.aligned:
                pyAliBase = self.selectAlignmentBase(numWire, numGeom)

                if pyAliBase:
                    # print 'finds an alignment backward'
                    if not pyAliBase.falsify:
                        jumpChop = True
                        pp = pyAliBase.aligns[-1]
                        numWireChopOne = pp.numWire
                        pyw = self.wires[numWireChopOne]
                        lenWire = len(pyw.planes)
                        numGeomChopOne =\
                            self.sliceIndex(pp.numGeom + 1, lenWire)

        if not jumpChop:

            lenWire = len(pyWire.planes)
            if alignList:
                num = alignList[-1].numGeom
                numGeomChopOne = self.sliceIndex(num + 1, lenWire)
                numWireChopOne = alignList[-1].numWire
            else:
                numGeomChopOne = self.sliceIndex(numGeom + 1, lenWire)
                numWireChopOne = numWire

        # aligns

        alignList.append(pyPl)

        if pyAlign.falsify:
            pyAli = None

        else:
            pyPl.shape = None
            pyAli = self.selectAlignmentBase(nWire, nGeom)

            if pyAli:
                # print 'finds an alignment forward'
                if not pyAli.falsify:
                    bL = pyAli.aligns
                    alignList.extend(bL)
                    for b in bL:
                        b.angle = [numWire, numGeom]

        pyAlign.aligns = alignList

        # chop two

        pyWireList = self.wires
        if numWire == nWire:
            numGeomChopTwo = self.sliceIndex(nGeom - 1, lenWire)
        else:
            lenW = len(pyWireList[nWire].planes)
            numGeomChopTwo = self.sliceIndex(nGeom - 1, lenW)

        # chops

        pyOne = self.selectPlane(numWireChopOne, numGeomChopOne)
        pyTwo = self.selectPlane(nWire, numGeomChopTwo)

        chopList.append([pyOne, pyTwo])

        if pyAli:
            if not pyAli.falsify:
                dL = pyAli.chops
                chopList.extend(dL)
                self.removeAlignment(pyAli)  # joined in one alignment

        pyAlign.chops = chopList

        if self.reset:

            pyPlane.reflexed = True
            pyPlane.aligned = True
            pyPl.reflexed = True
            pyPl.aligned = True

            pyOne.reflexed = True
            pyOne.choped = True
            pyTwo.reflexed = True
            pyTwo.choped = True

            self.forBack(pyOne, 'backward')
            self.findRear(pyWireList[numWireChopOne], pyOne, 'backward')

            self.forBack(pyTwo, 'forward')
            self.findRear(pyW, pyTwo, 'forward')

        return pyAli

    def findRear(self, pyWire, pyPlane, direction):

        '''findRear(self, pyWire, pyPlane, direction)
        Finds the rear plane of a reflexed plane.
        Determines if an arrow situacion happens.'''

        # print '### findRear ', (pyPlane.numWire, pyPlane.numGeom)

        tolerance = _Py.tolerance
        shapeGeomWire = pyWire.shapeGeom
        sGW = Part.Wire(shapeGeomWire)
        numWire = pyWire.numWire
        lenWire = len(pyWire.planes)
        numGeom = pyPlane.numGeom
        coord = pyWire.coordinates
        # print 'coord ', coord
        secondRear = False

        lineShape = pyPlane.forward
        section = lineShape.section([sGW], tolerance)
        # print 'section ', [x.Point for x in section.Vertexes]

        if len(section.Vertexes) == 1:
            # print 'return'
            return

        edge = False

        if pyPlane.lineInto:
            # print 'a'

            section = pyPlane.lineInto.section([sGW], tolerance)
            vertex = section.Vertexes[1]

        elif section.Edges:
            # print 'b'

            edge = True

            if direction == 'forward':
                # print 'b1'
                vertex = section.Edges[0].Vertexes[0]

            else:
                # print 'b2'
                vertex = section.Edges[-1].Vertexes[1]

        else:
            # print 'c'

            if len(section.Vertexes) == 2:
                # print 'c1'
                vertex = section.Vertexes[1]

            else:
                # print 'c2'

                lS = lineShape.copy()
                cut = lS.cut(shapeGeomWire, tolerance)
                # print 'cut ', [x.Point for x in cut.Vertexes]
                # print 'cut ', cut.Edges
                wire = Part.Wire(cut.Edges)
                orderedVertexes = wire.OrderedVertexes

                if direction == 'forward':
                    pp = coord[numGeom + 1]
                else:
                    pp = coord[numGeom]
                # print 'pp ', pp

                if pp == self.roundVector(orderedVertexes[0].Point):
                    vertex = orderedVertexes[1]
                    vert = orderedVertexes[2]
                else:
                    vertex = orderedVertexes[0]
                    vert = orderedVertexes[1]

                # print 'second rear'

                secondRear = True

            if not pyPlane.choped:  # ???

                point = self.roundVector(vertex.Point)
                if point in coord:
                    # print 'cc'
                    edge = True

        # print 'point ', vertex.Point
        # print 'edge ', edge

        nGeom = self.findGeomRear(pyWire, direction, vertex, edge)
        pyPlane.addValue('rear', nGeom, direction)
        # print 'nGeom ', nGeom

        if secondRear:
            sGeom = self.findGeomRear(pyWire, direction, vert, edge)
            pyPlane.addValue('secondRear', sGeom, direction)
            # print 'sGeom ', sGeom

        # arrow

        if direction == 'forward':
            endNum = self.sliceIndex(numGeom + 2, lenWire)
        else:
            endNum = self.sliceIndex(numGeom - 2, lenWire)

        if nGeom == endNum:
            # print 'arrow'
            pyPl = self.selectPlane(numWire, endNum)
            pyPl.arrow = True

        return nGeom

    def findGeomRear(self, pyWire, direction, vertex, edge=False):

        '''findGeomRear(self, pyWire, direction, vertex, edge=False)'''

        coord = pyWire.coordinates
        lenWire = len(pyWire.planes)
        shapeGeomWire = pyWire.shapeGeom

        try:

            nGeom = coord.index(self.roundVector(vertex.Point))
            # print 'on vertex'

            if edge:
                if direction == 'forward':
                    # print 'aa'
                    nGeom = self.sliceIndex(nGeom - 1, lenWire)

            else:
                if direction == 'backward':
                    # print 'bb'
                    nGeom = self.sliceIndex(nGeom - 1, lenWire)

        except ValueError:
            # print 'not in vertex (edge False)'

            nGeom = -1
            for geomShape in shapeGeomWire:
                nGeom += 1
                sect = vertex.section([geomShape], _Py.tolerance)
                if sect.Vertexes:
                    break

        return nGeom

    def findAngle(self, numWire, numGeom):

        '''findAngle(self, numWire, numGeom)'''

        angle = self.wires[numWire].planes[numGeom].angle

        if isinstance(angle, list):
            angle = self.findAngle(angle[0], angle[1])

        return angle

    def findAlignment(self, point):

        '''findAlignment(self, point)'''

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

        '''removeAlignment(self, pyAlign)'''

        pyAlignList = self.alignments
        pyAlignList.remove(pyAlign)
        self.alignments = pyAlignList

    def forBack(self, pyPlane, direction):

        '''forBack(self, pyPlane, direction)'''

        geom = pyPlane.geom
        firstParam = geom.FirstParameter
        lastParam = geom.LastParameter

        if isinstance(geom, (Part.LineSegment,
                             Part.ArcOfParabola,
                             Part.ArcOfHyperbola)):

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

        elif isinstance(geom, (Part.Circle,
                               Part.Ellipse)):

            pass

        elif isinstance(geom, Part.BSplineCurve):

            pass

        forwardLine = self.makeGeom(geom, startParam, endParam)
        # print'forwardLine ', forwardLine
        forwardLineShape = forwardLine.toShape()
        backwardLine = self.makeGeom(gg, sParam, eParam)
        # print'backwardLine ', backwardLine
        backwardLineShape = backwardLine.toShape()

        # Always forward into and backward outside

        if direction == "forward":
            # print 'a'
            pyPlane.backward = backwardLineShape
            pyPlane.forward = forwardLineShape

        else:
            # print 'b'
            pyPlane.backward = forwardLineShape
            pyPlane.forward = backwardLineShape

    def doReflex(self, pyWire, pyPlane, pyPl):

        '''doReflex(self, pyWire, pyPlane, pyPl)'''

        pyPlane.reflexed = True
        pyPl.reflexed = True
        pyReflex = _PyReflex()
        pyWire.reflexs.append(pyReflex)
        # print '¡¡¡ reflex done !!!'
        pyReflex.planes.append(pyPlane)
        pyReflex.planes.append(pyPl)
        return pyReflex

    def doAlignment(self, pyPlane):

        '''doAlignment(self, pyPlane)'''

        pyAlign = _PyAlignment()
        self.alignments.append(pyAlign)
        # print '¡¡¡ alignment done !!!'
        pyAlign.base = pyPlane

        return pyAlign

    def priorLaterAlignments(self):

        '''priorLaterAlignments(self)'''

        pyWireList = self.wires

        for pyAlign in self.alignments:

            pyBase = pyAlign.base
            numWire = pyBase.numWire
            numGeom = pyBase.numGeom
            pyWire = pyWireList[numWire]
            pyPlaneList = pyWire.planes
            lenWire = len(pyPlaneList)

            prior = self.sliceIndex(numGeom - 1, lenWire)
            pyPrior = self.selectBasePlane(numWire, prior)

            pyPl = pyAlign.aligns[-1]
            [nW, nG] = [pyPl.numWire, pyPl.numGeom]
            pyW = pyWireList[nW]
            lenW = len(pyW.planes)

            later = self.sliceIndex(nG + 1, lenW)
            pyLater = self.selectBasePlane(nW, later)

            pyAlign.prior = pyPrior
            pyAlign.later = pyLater

    def planning(self):

        '''planning(self)
        Transfers to PyWire.
        Arranges the alignment ranges.
        Rearmes the face reset system.'''

        # print '######### planning'

        for pyWire in self.wires:
            pyWire.planning()

        for pyAlign in self.alignments:
            pyAlign.rangging(self.reset)

        self.reset = False

    def upping(self):

        '''upping(self)'''

        # print '######### upping'

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
                                     center.sub(FreeCAD.Vector(diaLen / 2,
                                                               diaLen / 2,
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
                    pyPlane.cuttingPyth([upPlane])

    def virtualizing(self):

        '''virtualizing(self)
        Transfers to PyWire and PyAlignment.'''

        # print '######### virtualizing'

        for pyWire in self.wires:
            pyWire.virtualizing()

        for pyAlign in self.alignments:
            pyAlign.virtualizing()

    def trimming(self):

        '''trimming(self)
        Transfers to PyWire and PyAlignment.'''

        # print '######### trimming'

        for pyWire in self.wires:
            pyWire.trimming()
        # self.printControl('trimming reflexs')

        for pyAlign in self.alignments:
            pyAlign.trimming()
        # self.printControl('trimming alignments')

    def priorLater(self):

        '''priorLater(self)
        Transfers to PyWire and PyAlignment.'''

        # print '######### priorLater'

        for pyWire in self.wires:
            pyWire.priorLater()
        # self.printControl('priorLater wires')

        for pyAlign in self.alignments:
            pyAlign.priorLater()
        # self.printControl('priorLater alignments')

    def simulating(self):

        '''simulating(self)
        Transfers to PyWire and PyAlignment.'''

        # print '######### simulating'

        for pyWire in self.wires:
            pyWire.simulating()

        for pyAlign in self.alignments:
            pyAlign.simulatingChops()

        for pyAlign in self.alignments:
            pyAlign.simulatingAlignment()

    def reflexing(self):

        '''reflexing(self)
        Transfers to PyWire.'''

        # print '######### reflexing'

        for pyWire in self.wires:
            if pyWire.reflexs:
                pyWire.reflexing()

    def ordinaries(self):

        '''ordinaries(self)
        Transfers to PyWire.'''

        # print '######### ordinaries'

        for pyWire in self.wires:
            pyWire.ordinaries()

    def betweenWires(self):

        '''betweenWires(self)'''

        # print '######### betweenWires'

        pyWireList = self.wires
        if len(pyWireList) > 1:

            pyWL = pyWireList[:]
            pop = pyWL.pop(0)
            pyWL.append(pop)

            # print 'wires ', [pyW.numWire for pyW in pyWL]

            tolerance = self.tolerance

            alignments = self.alignments
            aliList = []
            for ali in alignments:
                aliList.extend(ali.simulatedAlignment)
            # print 'aliList ', aliList

            chopFace = []
            cutterFace = []

            for pyW in pyWL:
                # print '### nW', pyW.numWire
                chopList = []
                cutterList = []
                pyPlaneList = pyW.planes
                for pyPl in pyPlaneList:
                    if pyPl.shape:
                        # print '# nG ', pyPl.numGeom
                        if not pyPl.choped and\
                           not pyPl.fronted and\
                           not pyPl.aligned:
                            # print 'a'
                            cutterList.append(pyPl)
                        elif pyPl.choped:
                            # print 'b'
                            chopList.append(pyPl)

                chopFace.append(chopList)
                cutterFace.append(cutterList)

            # print 'cutterFace ', cutterFace
            # print 'chopFace ', chopFace

            num = -1
            for pyWire in pyWL:
                num += 1

                # print '### num ', num

                pop = cutterFace.pop(num)
                cutterList = []
                for cL in cutterFace:
                    cutterList.extend(cL)
                cutterFace.insert(num, pop)
                # print 'cutterList ', cutterList

                cutterList = [pyPl.shape for pyPl in cutterList]

                pop = chopFace.pop(num)
                chopList = []
                for cL in chopFace:
                    chopList.extend(cL)
                chopFace.insert(num, pop)
                # print 'chopList ', chopList

                chopList = [pyPl.simulatedShape for pyPl in chopList]

                numWire = pyWire.numWire
                # print '### numWire ', numWire

                for pyPlane in pyWire.planes:
                    cutList = cutterList[:]
                    plane = pyPlane.shape
                    if plane:
                        # print '# numGeom ', pyPlane.numGeom
                        gS = pyPlane.geomShape

                        if pyPlane.fronted:
                            # print '0'
                            pass

                        elif pyPlane.choped:
                            # print 'A'
                            aList = alignments[:]
                            # print 'aList ', aList

                            pyAlignList =\
                                self.selectAlignmentsChop(numWire,
                                                          pyPlane.numGeom)
                            # print 'pyAlignList ', pyAlignList
                            baseList = []

                            for pyA in pyAlignList:
                                aList.remove(pyA)
                                baseList.append(pyA.base.enormousShape)

                            aL = []
                            # print 'aList ', aList
                            for aa in aList:
                                sim = aa.base.shape.copy()
                                geomShape = aa.geomAligned
                                if baseList:
                                    sim = self.cutting(sim, baseList,
                                                       geomShape)
                                aL.append(sim)
                            # print 'aL ', aL
                            cutList.extend(aL)

                        elif pyPlane.aligned:
                            # print 'B'
                            pyAlign =\
                                self.selectAlignmentBase(numWire,
                                                         pyPlane.numGeom)
                            if pyAlign:
                                line = pyAlign.geomAligned
                                simulAlign =\
                                    Part.makeShell(pyAlign.simulatedAlignment)
                                aList = alignments[:]
                                aList.remove(pyAlign)
                                aL = []
                                for pyA in aList:
                                    ll = pyA.geomAligned
                                    section = line.section([ll], tolerance)
                                    if not section.Vertexes:
                                        simulA =\
                                            Part.makeShell(pyA.simulatedAlignment)
                                        common =\
                                            simulAlign.common([simulA], tolerance)
                                        if not common.Area:
                                            aL.extend(pyA.simulatedAlignment)
                                cutList.extend(aL)

                        else:
                            # print 'C'
                            cutList.extend(aliList)
                            cutList.extend(chopList)

                        if cutList:
                            # print 'cutList ', cutList

                            if isinstance(plane, Part.Compound):
                                # print '1'

                                # esto hay que revisarlo
                                if len(plane.Faces) > 1:
                                    # print '11'

                                    fList = []
                                    for ff in plane.Faces:
                                        ff = ff.cut(cutList, tolerance)
                                        fList.append(ff.Faces[0])   # esto hay que cambiarlo
                                    compound = Part.makeCompound(fList)
                                    pyPlane.shape = compound

                                else:
                                    # print '12'

                                    plane = plane.cut(cutList, tolerance)
                                    fList = []
                                    ff = self.cutting(plane, cutList, gS)
                                    fList.append(ff)
                                    if pyPlane.rear:
                                        plane = plane.removeShape([ff])
                                        for ff in plane.Faces:
                                            section =\
                                                ff.section(fList, tolerance)
                                            if not section.Edges:
                                                fList.append(ff)
                                                break
                                    compound = Part.makeCompound(fList)
                                    pyPlane.shape = compound

                            else:
                                # print '2'
                                pyPlane.cuttingPyth(cutList)

                            # print 'pyPlane.shape ', pyPlane.shape

    def postProcess(self):

        ''''''

        alignList = self.alignments[:]

        '''cutterList = []
        for pyAlign in self.alignments:
            for rC in pyAlign.rangoChop:
                for r in rC:
                    pass

        number = -1
        for pyAlign in self.alignments:
            number += 1
            pop = alignList.pop(number)
            cutterList = []
            for pyA in alignList:
                
                pass
            alignList.insert(number, pop)'''
