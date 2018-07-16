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


V = FreeCAD.Vector


__title__ = "SlopedPlanes Macro"
__author__ = "Damian Caceres Moreno"
__url__ = "http://www.freecadweb.org"
__version__ = ""


class _PyFace(_Py):

    '''The complementary python object class for the faces resulting
    to apply the FaceMaker to the SlopedPlanes base.
    The faces could have several wires, and as a consequense holes.'''

    def __init__(self, numFace, mono=True):

        '''__init__(self, numFace)'''

        self.numFace = numFace
        self.wires = []
        self.alignments = []
        self.reset = True
        self.shapeGeom = []
        self.size = 0
        self.mono = mono

    @property
    def numFace(self):

        '''numFace(self)'''

        return self._numFace

    @numFace.setter
    def numFace(self, numFace):

        '''numFace(self, numFace)'''

        self._numFace = numFace

    @property
    def wires(self):

        '''wires(self)'''

        return self._wires

    @wires.setter
    def wires(self, wires):

        '''wires(self, wires)'''

        self._wires = wires

    @property
    def alignments(self):

        '''alignments(self)'''

        return self._alignments

    @alignments.setter
    def alignments(self, alignments):

        '''alignments(self, alignments)'''

        self._alignments = alignments

    @property
    def reset(self):

        '''reset(self)'''

        return self._reset

    @reset.setter
    def reset(self, reset):

        '''reset(self, reset)'''

        self._reset = reset

    @property
    def shapeGeom(self):

        '''shapeGeom(self)'''

        return self._shapeGeom

    @shapeGeom.setter
    def shapeGeom(self, shapeGeom):

        '''shapeGeom(self, shapeGeom)'''

        self._shapeGeom = shapeGeom

    @property
    def size(self):

        '''size(self)'''

        return self._size

    @size.setter
    def size(self, size):

        '''size(self, size)'''

        self._size = size

    @property
    def mono(self):

        '''mono(self)'''

        return self._mono

    @mono.setter
    def mono(self, mono):

        '''mono(self, mono)'''

        self._mono = mono

    def __getstate__(self, serialize):

        '''__getstate__(self, serialize)
        Serializes the complementary python objects.'''

        wireList, serialList = [], []
        for pyWire in self.wires:
            dct = pyWire.__dict__.copy()
            dct['_coordinates'] = [[v.x, v.y, v.z] for v in pyWire.coordinates]
            dct['_shapeGeom'] = []
            dct['_wire'] = None

            for pyReflex in pyWire.reflexs:
                pyReflex.lines = []

            if serialize:
                edgeList = []
                forBack = []

            planeList = []
            for pyPlane in pyWire.planes:
                dd = pyPlane.__dict__.copy()

                # print '######### ', pyPlane.numGeom, pyPlane
                # print 'dd ', dd

                dd['_shape'] = None
                dd['_bigShape'] = None
                dd['_enormousShape'] = None

                dd['_seedShape'] = None
                dd['_seedBigShape'] = None

                dd['_simulatedShape'] = None

                dd['_geom'] = None
                dd['_lineInto'] = None

                dd['_cutter'] = []
                dd['_under'] = []
                dd['_seed'] = []

                dd['_virtuals'] = []

                dd['_alignedList'] = []
                dd['_chopedList'] = []
                dd['_frontedList'] = []
                dd['_rearedList'] = []
                dd['_reflexedList'] = []

                dd['_rangoPy'] = []

                dd['_solved'] = False
                dd['_reallySolved'] = False

                if serialize:

                    edgeList.append(pyPlane.geomShape)

                    if pyPlane.forward:

                        forBack.extend([pyPlane.forward, pyPlane.backward])
                        dd['_forward'] = 'forward'
                        dd['_backward'] = 'backward'

                else:

                    dd['_forward'] = None
                    dd['_backward'] = None

                dd['_geomShape'] = None
                dd['_geomAligned'] = None

                # print 'dd ', dd

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
                    pyPlane.reflexedList.append(pyReflex)

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

        # self.printSummary()

        pyAlignList = self.alignments
        pyWireList = self.wires
        mono = self.mono

        reset = self.reset

        for pyWire in pyWireList:
            pyWire.planning(reset)

        for pyAlign in pyAlignList:
            pyAlign.rangging(reset)

        self.reset = False

        # self.printSummary()

        self.upping()

        for pyWire in pyWireList:
            pyWire.virtualizing()

        for pyAlign in pyAlignList:
            pyAlign.virtualizing()

        # self.printSummary()

        if not mono:
            for pyWire in pyWireList:
                if not pyWire.mono:
                    pyWire.trimming()
            # self.printControl('trimming reflexs')

        for pyAlign in pyAlignList:
            pyAlign.trimming()
        # self.printControl('trimming alignments')

        for pyWire in pyWireList:
            pyWire.priorLater()
        # self.printControl('priorLater wires')

        for pyAlign in pyAlignList:
            pyAlign.priorLater()
        # self.printControl('priorLater alignments')

        for pyWire in pyWireList:
            pyWire.simulating()

        for pyAlign in pyAlignList:
            pyAlign.simulatingChops()

        for pyAlign in pyAlignList:
            pyAlign.simulatingAlignment()

        # self.printControl('simulating')

        for pyWire in pyWireList:
            if pyWire.reflexs:
                pyWire.reflexing()
        # self.printControl('reflexing')

        for pyWire in pyWireList:
            pyWire.ordinaries()
        # self.printControl('ordinaries')

        self.betweenWires()

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

        # '''

    def parsing(self):

        '''parsing(self)
        Splits the pyFace object finding its reflex corners and alignments.'''

        # print '######### parsing'

        resetFace = self.reset
        # print 'resetFace ', resetFace

        face = self.face

        if not resetFace and not self.alignments:
            return

        pyWireList = self.wires
        shapeGeomFace = self.shapeGeom
        compoundFace = Part.Compound(shapeGeomFace)
        tolerance = _Py.tolerance

        if resetFace:
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
        refAlignList = []    # covers consecutive alignments in reflex

        for pyWire in pyWireList:
            numWire = pyWire.numWire
            # print '###### numWire ', numWire

            ref = False

            pyPlaneList = pyWire.planes
            coord = pyWire.coordinates

            pyPrePlane = None

            eje = coord[1].sub(coord[0])

            for pyPlane in pyPlaneList:
                numGeom = pyPlane.numGeom
                # print '### numGeom ', numGeom, ' angle ', pyPlane.angle

                possible = False

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
                            # print 'refList ', refList
                            if not pyPrePlane:
                                pyPrePlane = pyPlaneList[-1]
                            self.forBack(pyPrePlane, 'forward')
                            ref = True

                        if ref:
                            # print 'ref'
                            self.forBack(pyPlane, 'backward')

                            forward = pyPlane.forward
                            section = forward.section(shapeGeomFace, tolerance)
                            # print section.Edges, section.Vertexes

                            if section.Edges:
                                # print 'edges'

                                lineStart = coord[numGeom]
                                # print 'lineStart ', lineStart

                                edge = section.Edges[0]
                                edgeStart = edge.firstVertex(True).Point
                                point = self.roundVector(edgeStart)
                                # print 'point ', point

                                sect = compoundFace.section([edge], tolerance)
                                ed = sect.Edges[0]
                                edStart = ed.lastVertex(True).Point
                                pp = self.roundVector(edStart)
                                # print 'pp ', pp

                                lineInto =\
                                    Part.LineSegment(lineStart,
                                                     edgeStart).toShape()
                                ss =\
                                    len(lineInto.section([face],
                                                         tolerance).Vertexes)
                                # print 'ss ', ss

                                if point == pp and ss == 2:
                                    # print 'alignment'
                                    pyPlane.aligned = True

                                else:
                                    # print 'edges no alignment '

                                    if ss is not 2:

                                        pyPlane.lineInto = lineInto

                                    possible = True

                                    rearF =\
                                        self.findRear(pyWire, pyPrePlane,
                                                      'forward')
                                    rearB =\
                                        self.findRear(pyWire, pyPlane,
                                                      'backward')

                                    if not pyPrePlane.aligned:

                                        pyReflex =\
                                            self.doReflex(pyWire, pyPrePlane,
                                                          pyPlane)
                                        pyReflex.addValue('rear', rearF,
                                                          'forward')
                                        pyReflex.addValue('rear', rearB,
                                                          'backward')

                            else:
                                # print 'no alignament'

                                possible = True

                                rearF =\
                                    self.findRear(pyWire, pyPrePlane,
                                                  'forward')
                                rearB =\
                                    self.findRear(pyWire, pyPlane,
                                                  'backward')

                                if not pyPrePlane.aligned:

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
                                point = self.roundVector(edgeStart)
                                # print 'point ', point

                                sect = compoundFace.section([edge], tolerance)
                                ed = sect.Edges[0]
                                edStart = ed.firstVertex(True).Point
                                pp = self.roundVector(edStart)
                                # print 'pp ', pp

                                lineInto =\
                                    Part.LineSegment(lineEnd,
                                                     edgeStart).toShape()
                                ss =\
                                    len(lineInto.section([face],
                                                         tolerance).Vertexes)
                                # print 'ss ', ss

                                if point == pp and ss == 2:
                                    # print '1111 aligment'

                                    edgeEnd = edge.lastVertex(True).Point
                                    # print 'edgeEnd ', edgeEnd

                                    lineEnd = edgeEnd

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
                                            break

                                        if pyAlign.falsify:
                                            # print 'break false alignament'
                                            break

                                elif ss is not 2:
                                    # print '1112 interference'
                                    ref = True
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

                                nn = pyPl.numGeom
                                lenW = len(pyW.planes)
                                num = self.sliceIndex(nn + 1, lenW)
                                coo = pyW.coordinates
                                jj = coo[num].sub(coo[nn])
                                nnjj = coo[num + 1].sub(coo[num])
                                corner = self.convexReflex(jj, nnjj)
                                endPlane = pyW.planes[nn]
                                nextPlane = pyW.planes[num]

                                if corner == 'reflex':
                                    # print 'reflex'

                                    if resetFace:
                                        # print 'resetFace'

                                        if [pyW.numWire, nn] in refAlignList and nextPlane.aligned:
                                            # print 'refAlignList ', refAlignList

                                            pyAlign.rear[0] = endPlane.rear[0]

                                            nextAlign = nextPlane.selectAlignmentBase()
                                            nextAlign.rear[1] = nextPlane.rear[-1]

                                        else:
                                            # print 'refList'
                                            refList.append([pyW.numWire, num])
                                            # print 'refList ', refList

                                    else:
                                        # print 'no resetFace'
                                        if [pyW.numWire, nn] in refAlignList and nextPlane.aligned:
                                            # print 'refAlignList ', refAlignList

                                            pyAlign.rear[0] = endPlane.rear[0]

                                            nextAlign = nextPlane.selectAlignmentBase()
                                            nextAlign.rear[1] = nextPlane.rear[-1]

                                if pyPrePlane and pyPrePlane.aligned:
                                    # print 'pyPrePlane aligned'

                                    try:
                                        pyA = pyPrePlane.alignedList[0]
                                        pyB = pyA.base
                                    except IndexError:
                                        pyB =\
                                            self.selectBasePlane(numWire,
                                                                 pyPrePlane.numGeom)
                                        pyA = pyB.selectAlignmentBase()

                                    if pyA:
                                        # print 'pyA'

                                        if possible:
                                            # print 'possible'

                                            pyA.rear[0] = rearF
                                            pyAlign.rear[1] = rearB

                                        else:
                                            # print 'no possible'

                                            try:
                                                pyA.rear[0] = pyPrePlane.rear[0]
                                            except IndexError:
                                                pass

                                            try:
                                                pyAlign.rear[1] = pyAlign.base.rear[-1]
                                            except IndexError:
                                                pass

                                    else:
                                        # print 'refAlignList'
                                        refAlignList.append([pyPrePlane.numWire, pyPrePlane.numGeom])
                                        # print refAlignList

                        else:
                            # print '12 no alignment'
                            if resetFace:
                                # print '121'
                                if corner == 'reflex':
                                    # print '1211 reflexed'
                                    ref = True

                                if possible and pyPrePlane.aligned:
                                    # print 'possible'

                                    pyReflex =\
                                        self.doReflex(pyWire, pyPrePlane,
                                                      pyPlane)

                                    pyReflex.addValue('rear', rearF,
                                                      'forward')
                                    pyReflex.addValue('rear', rearB,
                                                      'backward')
                                    # print pyReflex.rear

                    else:
                        # print '2 Convex: does not look for alignments'

                        if possible and pyPrePlane.aligned:
                            # print 'possible'

                            pyReflex =\
                                self.doReflex(pyWire, pyPrePlane, pyPlane)

                            pyReflex.addValue('rear', rearF, 'forward')
                            pyReflex.addValue('rear', rearB, 'backward')

                pyPrePlane = pyPlane

                # print 'reflex ', pyWire.reflexs
                # print 'alignments ', self.alignments

            if resetFace:
                if numWire > 0 and pyPlane.geomAligned and len(coord) > 2:
                    # print 'firstPlane'

                    firstPlane = pyPlaneList[0]

                    if not firstPlane.aligned:
                        # print 'firstPlane no aligned'
                        pyReflex = self.doReflex(pyWire, pyPlane, firstPlane)

                    else:
                        # print 'firstPlane aligned'

                        if not pyPlane.choped:
                            # print 'pyPlane no choped'
                            pyReflex =\
                                self.doReflex(pyWire, pyPlane, firstPlane)

                        else:
                            pyAlignmentList = pyPlane.chopedList
                            pyAlignment = firstPlane.selectAlignmentBase()
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
                pyAliBase = pyPlane.selectAlignmentBase()

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
            pyAli = pyPl.selectAlignmentBase()

            if pyAli:
                # print 'finds an alignment forward'
                if not pyAli.falsify:
                    bL = pyAli.aligns
                    alignList.extend(bL)
                    for b in bL:
                        b.angle = [numWire, numGeom]

                rr = pyAli.rear[0]
                pyAlign.addValue('rear', rr, 'forward')

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
                # print 'pyAli ', pyAli
                dL = pyAli.chops
                chopList.extend(dL)
                self.alignments.remove(pyAli)  # joined in one alignment

                pyAli.base.alignedList.remove(pyAli)
                for ali in pyAli.aligns:
                    # print 'a'
                    ali.alignedList.remove(pyAli)
                for chop in pyAli.chops:
                    for pyP in chop:
                        # print 'b'
                        pyP.chopedList.remove(pyAli)
                        pyP.chopedList.append(pyAlign)

        pyAlign.chops = chopList

        pyPl.alignedList.append(pyAlign)
        pyOne.chopedList.append(pyAlign)
        pyTwo.chopedList.append(pyAlign)

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
        numWire = pyWire.numWire
        lenWire = len(pyWire.planes)
        numGeom = pyPlane.numGeom
        coord = pyWire.coordinates
        sGW = pyWire.wire

        forward = pyPlane.forward
        section = forward.section([sGW], tolerance)
        # print 'section.Edges ', section.Edges, [(e.firstVertex(True).Point, e.lastVertex(True).Point) for e in section.Edges]
        # print 'section.Vertexes ', [x.Point for x in section.Vertexes]

        if len(section.Vertexes) == 1:
            # print 'return'
            return

        edge = False
        if section.Edges:
            edge = True

        lineInto = pyPlane.lineInto

        if lineInto:
            # print 'a'
            sect = lineInto.section([sGW], tolerance)
            vertex = sect.Vertexes[1]

        elif section.Edges:
            # print 'b'

            if direction == "forward":
                vertex = section.Edges[0].firstVertex(True)
            else:
                vertex = section.Edges[0].lastVertex(True)

        else:
            # print 'c'

            vertex = section.Vertexes[1]

            if not pyPlane.choped:

                point = self.roundVector(vertex.Point)
                if point in coord:
                    # print 'cc'
                    edge = True

        # print 'point ', vertex.Point
        # print 'edge ', edge

        nGeom = self.findGeomRear(pyWire, pyPlane, direction, vertex, edge)
        pyPlane.addValue('rear', nGeom, direction)
        # print 'nGeom ', nGeom

        # second rear

        if len(section.Vertexes) > 2:
            # print 'secondRear'

            oo = forward.firstVertex(True)
            pp = oo.Point

            edgeList = []
            for ee in section.Edges:
                edgeList.extend([ee.firstVertex(True).Point,
                                 ee.lastVertex(True).Point])
            # print 'edgeList ', edgeList

            vertList = []
            distList = []
            for vv in section.Vertexes:
                dist = vv.Point.sub(pp).Length
                num = -1
                for dd in distList:
                    num += 1
                    if dd > dist:
                        distList.insert(num, dist)
                        vertList.insert(num, vv)
                        break
                else:
                    distList.append(dist)
                    vertList.append(vv)

            # print 'vertList ', vertList, [v.Point for v in vertList]
            # print 'distList ', distList

            for vert in vertList[2:]:
                edge = False
                if vert.Point in edgeList:
                    edge = True
                else:
                    if not pyPlane.choped:
                        point = self.roundVector(vv.Point)
                        if point in coord:
                            edge = True

                sGeom = self.findGeomRear(pyWire, pyPlane, direction, vert, edge)
                if sGeom not in pyPlane.rear:   # mejor hacerlo arriba al principio de la seccion
                    pyPlane.addValue('secondRear', sGeom, direction)
                # print 'sGeom ', sGeom

        # TODO backRear

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

    def findGeomRear(self, pyWire, pyPlane, direction, vertex, edge=False):

        '''findGeomRear(self, pyWire, pyPlane, direction, vertex, edge=False)'''

        # print '#findGeomRear ', (direction, edge)

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
            # print 'not in vertex'

            # print vertex.Point

            tolerance = _Py.tolerance

            nGeom = -1
            for geomShape in shapeGeomWire:
                nGeom += 1
                # print nGeom, geomShape, geomShape.Curve
                sect = vertex.section([geomShape], tolerance)
                # print sect.Vertexes
                if sect.Vertexes:
                    # print 'break'
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

    def forBack(self, pyPlane, direction):

        '''forBack(self, pyPlane, direction)'''

        # print (pyPlane.numWire, pyPlane.numGeom)

        geom = pyPlane.geom
        firstParam = geom.FirstParameter
        lastParam = geom.LastParameter

        # print 'geom ', geom
        # print 'firstParam ', firstParam
        # print 'lastParam ', lastParam

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

            if geom.Axis == V(0, 0, 1):
                # print 'A'

                half = (2 * pi - (lastParam - firstParam)) / 2
                startParam = lastParam
                endParam = lastParam + half

                # print 'half ', half
                # print 'startParam ', startParam
                # print 'endParam ', endParam

                gg = geom.copy()
                gg.Axis = _Py.normal * -1
                sParam = 2 * pi - firstParam
                eParam = sParam + half

                # print 'gg ', gg

                # print 'sParam ', sParam
                # print 'eParam ', eParam

            else:
                # print 'B'

                half = (2 * pi - (lastParam - firstParam)) / 2
                startParam = lastParam
                endParam = lastParam + half

                # print 'half ', half
                # print 'startParam ', startParam
                # print 'endParam ', endParam

                gg = geom.copy()
                gg.Axis = _Py.normal
                sParam = 2 * pi - firstParam
                eParam = sParam + half

                # print 'gg ', gg
                # print 'sParam ', sParam
                # print 'eParam ', eParam

        elif isinstance(geom, Part.BSplineCurve):

            pass

        forwardLine = self.makeGeom(geom, startParam, endParam)
        # print'forwardLine ', forwardLine
        # print(forwardLine.value(startParam), forwardLine.value(endParam))
        forwardLineShape = forwardLine.toShape()
        backwardLine = self.makeGeom(gg, sParam, eParam)
        # print'backwardLine ', backwardLine
        # print(backwardLine.value(sParam), backwardLine.value(eParam))
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
        pyPlane.reflexedList.append(pyReflex)
        pyPl.reflexedList.append(pyReflex)
        return pyReflex

    def doAlignment(self, pyPlane):

        '''doAlignment(self, pyPlane)'''

        pyAlign = _PyAlignment()
        self.alignments.append(pyAlign)
        # print '¡¡¡ alignment done !!!'
        pyAlign.base = pyPlane
        pyPlane.alignedList.append(pyAlign)

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

            cutterFace = []

            for pyW in pyWL:
                # print '### nW', pyW.numWire
                cutterList = []
                pyPlaneList = pyW.planes
                for pyPl in pyPlaneList:
                    if pyPl.shape:
                        # print '# nG ', pyPl.numGeom
                        if not (pyPl.choped or pyPl.fronted or pyPl.aligned):
                            # print 'a'
                            cutterList.append(pyPl)

                cutterFace.append(cutterList)

            # print 'cutterFace ', cutterFace

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

                checkList = cutterList[:]
                cutterList = [pyPl.shape for pyPl in cutterList]

                # print '### numWire ', pyWire.numWire

                for pyPlane in pyWire.planes:
                    cutList = cutterList[:]
                    chList = checkList[:]
                    plane = pyPlane.shape
                    if plane:
                        # print '# numGeom ', pyPlane.numGeom
                        gS = pyPlane.geomShape

                        aL = []

                        if pyPlane.fronted:
                            # print '0'
                            pass

                        elif pyPlane.choped:
                            # print 'A'

                            chopedList = pyPlane.chopedList
                            # print 'chopedList ', chopedList

                            for pyA in alignments:

                                if pyA in chopedList:
                                    # print 'A1'

                                    common = plane.common(pyA.simulatedAlignment, tolerance)

                                    if common.Area:
                                        # print 'A11'

                                        if len(chopedList) > 1:
                                            # print 'A111'

                                            for ch in pyA.chops:
                                                for pyC in ch:
                                                    common = pyC.shape.common([plane], tolerance)  # hay que revisar este common
                                                    if not common.Area:
                                                        # aL.append(pyC.shape)
                                                        aL.append(pyC.simulatedShape)

                                        else:
                                            # print 'A112'

                                            # if len(pyA.chops) > 1:
                                            # hay repeticion de cortes

                                            # el que va a ser cortado
                                            procc = False
                                            for ch in pyA.chops:
                                                if pyPlane in ch:
                                                    [pyOne, pyTwo] = ch
                                                    if pyOne.numWire != pyTwo.numWire:
                                                        procc = True
                                                        aa = [pyOne.numWire, pyTwo.numWire]
                                                    break

                                            # los cortadores
                                            if procc:
                                                # print 'A1121'

                                                if len(pyA.chops) > 1:

                                                    for ch in pyA.chops:
                                                        if pyPlane not in ch:
                                                            [pyO, pyT] = ch
                                                            if pyO.numWire != pyT.numWire:
                                                                if pyO.numWire in aa or pyT.numWire in aa:
                                                                    nn = pyO.simulatedShape.copy().cut([pyT.shape], tolerance)
                                                                    nn = self.selectFace(nn.Faces, pyO.geomShape)
                                                                    mm = pyT.simulatedShape.copy().cut([pyO.shape], tolerance)
                                                                    mm = self.selectFace(mm.Faces, pyT.shape)
                                                                    aL.extend([nn, mm])

                                    else:
                                        # print 'A12'
                                        aL.extend(pyA.simulatedAlignment)

                                else:
                                    # print 'A2'
                                    aL.extend(pyA.simulatedAlignment)

                            cutList.extend(aL)

                        elif pyPlane.aligned:
                            # print 'B'

                            # print cutList
                            # print chList

                            pyAlign = pyPlane.selectAlignmentBase()
                            if pyAlign:

                                simulAlign =\
                                    Part.makeShell(pyAlign.simulatedAlignment)

                                prL = [pyAlign.prior, pyAlign.later]

                                nn = -1
                                for pyP in chList:
                                    nn += 1
                                    if pyP in prL:
                                        cutList.pop(nn)

                                aList = alignments[:]
                                aList.remove(pyAlign)
                                for pyA in aList:

                                    simulA =\
                                        Part.makeShell(pyA.simulatedAlignment)

                                    common =\
                                        simulAlign.common([simulA], tolerance)

                                    if not common.Area:
                                        aL.extend(pyA.simulatedAlignment)

                                    else:
                                        for ch in pyA.chops:
                                            for pyC in ch:
                                                common = pyC.shape.common([simulAlign], tolerance)
                                                if not common.Area:
                                                    aL.append(pyC.shape)

                                cutList.extend(aL)

                        else:
                            # print 'C'

                            for ali in alignments:
                                if ali in pyPlane.rearedList:
                                    aL.extend(ali.simulatedAlignment)
                            cutList.extend(aL)

                        # print 'aL ', aL

                        if cutList:
                            # print 'cutList ', cutList, pyPlane.shape

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

        if not self.alignments:
            return

        # recolects

        aList = []
        cList = []
        for ali in self.alignments:

            aL = []
            aL.append(ali.base.shape)
            for aa in ali.aligns:
                if aa.shape:
                    aL.append(aa.shape)

            for cc in ali.chops:
                for c in cc:
                    if c.shape:
                        aL.append(c.shape)

            cL = []
            for rC in ali.rangoPy:
                for r in rC:
                    if r.shape:
                        cL.append(r.shape)

            aList.append(aL)
            cList.append(cL)

        if len(self.wires) > 1:

            for pyWire in self.wires:
                for pyPlane in pyWire.planes:

                    if not pyPlane.fronted:

                        # the planes not fronted not aligned not choped are cutted by alignments not included in its rearedList

                        if not (pyPlane.choped or pyPlane.aligned):
                            # print pyPlane.numGeom
                            rearedList = pyPlane.rearedList
                            # print rearedList

                            cutList = []
                            for ali, aa in zip(self.alignments, aList):
                                if ali not in rearedList:
                                    cutList.extend(aa)
                            if cutList:
                                # print aList
                                pyPlane.cuttingPyth(cutList)

                        # the aligned planes with shape and not fronted are cutted by other alignments not included in its alignedList and chopedList

                        elif pyPlane.aligned and pyPlane.shape:

                            alignedList = pyPlane.alignedList
                            chopedList = pyPlane.chopedList

                            cutList = []
                            for ali, aa in zip(self.alignments, aList):
                                if ali not in alignedList and ali not in chopedList:
                                    cutList.extend(aa)
                            if cutList:
                                # print aList
                                pyPlane.cuttingPyth(cutList)

        # everyone no reflexed with fronted

        num = -1
        for pyAlignment in self.alignments:
            num += 1

            cc = cList[num]
            if cc:
                for wire in self.wires:
                    for plane in wire.planes:
                        if not plane.reflexed:
                            if pyAlignment not in plane.frontedList:
                                plane.cuttingPyth(cc)
