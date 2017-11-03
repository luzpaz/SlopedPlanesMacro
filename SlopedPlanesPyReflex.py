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


import Part
import SlopedPlanesUtils as utils
from SlopedPlanesPy import _Py


__title__ = "SlopedPlanes Macro"
__author__ = "Damian Caceres Moreno"
__url__ = "http://www.freecadweb.org"


class _PyReflex(_Py):

    ''''''

    def __init__(self):

        ''''''

        self.planes = []
        self.rangoInter = []

    @property
    def planes(self):

        ''''''

        return self._planes

    @planes.setter
    def planes(self, planes):

        ''''''

        self._planes = planes

    @property
    def rangoInter(self):

        ''''''

        return self._rangoInter

    @rangoInter.setter
    def rangoInter(self, rangoInter):

        ''''''

        self._rangoInter = rangoInter

    def simulating(self, tolerance):

        ''''''

        [pyR, pyOppR] = self.planes
        enormousR = pyR.enormousShape
        enormousOppR = pyOppR.enormousShape
        try:
            rCopy = pyR.simulatedShape.copy()
        except AttributeError:
            rCopy = pyR.shape.copy()
        try:
            oppRCopy = pyOppR.simulatedShape.copy()
        except AttributeError:
            oppRCopy = pyOppR.shape.copy()

        rCopy = rCopy.cut([enormousOppR], tolerance)
        gS = pyR.geom.toShape()
        rCopy = utils.selectFace(rCopy.Faces, gS, tolerance)
        pyR.simulatedShape = rCopy

        oppRCopy = oppRCopy.cut([enormousR], tolerance)
        gS = pyOppR.geom.toShape()
        oppRCopy = utils.selectFace(oppRCopy.Faces, gS, tolerance)
        pyOppR.simulatedShape = oppRCopy

    def reflexing(self, pyFace, pyWire, tolerance):

        ''''''

        pyPlaneList = self.planes

        pyR = pyPlaneList[0]
        pyOppR = pyPlaneList[1]

        pyR.oppCutter, pyR.cutter = [], []
        pyOppR.oppCutter, pyOppR.cutter = [], []

        direction = "forward"
        print '### direction ', direction
        print(pyR.numGeom, pyOppR.numGeom)

        self.twin(pyFace, pyWire, pyR, pyOppR, direction, tolerance)

        direction = "backward"
        print '### direction ', direction
        print(pyOppR.numGeom, pyR.numGeom)

        self.twin(pyFace, pyWire, pyOppR, pyR, direction, tolerance)

    def twin(self, pyFace, pyWire, pyR, pyOppR, direction, tolerance):

        ''''''

        reflexEnormous = pyR.enormousShape.copy()
        pyOppR.addLink('oppCutter', reflexEnormous)

        oppReflexEnormous = pyOppR.enormousShape.copy()

        angle = pyR.angle
        numWire = pyR.numWire
        if ((numWire == 0 and angle > 90) or
           (numWire > 0 and angle < 90)):
            pyR.shape = pyR.simulatedShape

        nWire = pyWire.numWire
        pyPlaneList = pyWire.planes

        rear = pyR.rear

        for nGeom in rear:
            rearPyPl = pyWire.planes[nGeom]

            if rearPyPl.aligned:
                print 'a'
                pyAlign = pyFace.selectAlignament(rearPyPl.numWire,
                                                  rearPyPl.numGeom)
                rearPl = pyAlign.simulatedShape
                print 'included rear simulated ', (rearPl, nWire, nGeom)

            elif rearPyPl.choped:
                print 'b'
                rearPl = rearPyPl.shape
                print 'included rear ', (rearPl, nWire, nGeom)

            elif rearPyPl.reflexed:
                print 'c'
                rr = rearPyPl.rear[0]
                print rr
                pyRr = pyPlaneList[rr]
                print pyRr.rear
                print rearPyPl.numGeom
                if pyR.numGeom in pyRr.rear:
                    print 'a'
                    rearPl = rearPyPl.shape.copy()
                    gS = rearPyPl.geom.toShape()
                    rearPl = rearPl.cut([oppReflexEnormous], tolerance)
                    rearPl = utils.selectFace(rearPl.Faces, gS, tolerance)
                    print 'included rear rectified', (rearPl, nWire, nGeom)
                else:
                    print 'b'
                    rearPl = rearPyPl.shape
                    print 'included rear ', (rearPl, nWire, nGeom)

            else:
                print 'd'
                rearPl = rearPyPl.shape
                print 'included rear ', (rearPl, nWire, nGeom)

            pyR.addLink('cutter', rearPl)
            pyOppR.addLink('oppCutter', rearPl)

        nWire = pyWire.numWire

        oppRear = pyOppR.rear

        if len(oppRear) == 1:

            nGeom = oppRear[0]
            pyOppRear = pyWire.planes[nGeom]
            try:
                oppRearPl = pyOppRear.shape.copy()
            except AttributeError:
                [nWire, nGeom] = pyOppRear.angle
                pyOppRear = pyFace.selectPlane(nWire, nGeom)
                oppRearPl = pyOppRear.shape.copy()

            if not pyOppRear.reflexed:
                pass
                print 'included oppRear ', (oppRearPl, nWire, nGeom)

            else:
                oppRearPl = pyOppRear.simulatedShape
                print 'included oppRear rectified ', (oppRearPl, nWire, nGeom)

            pyR.addLink('cutter', oppRearPl)
            pyOppR.addLink('oppCutter', oppRearPl)

        elif len(oppRear) == 2:

            if direction == 'forward':

                self.processOppRear(oppRear, direction, pyFace, pyWire, pyR,
                                    pyOppR, oppReflexEnormous, tolerance)

            else:

                self.processOppRear(oppRear, direction, pyFace, pyWire, pyR,
                                    pyOppR, oppReflexEnormous, tolerance)

        rangoNext = pyOppR.rango

        if len(rear) == 1:
            for ran in rangoNext:
                for nn in ran:

                    self.processRango(pyFace, pyWire, pyR, pyOppR,
                                      nn, 'rangoNext', tolerance)

        rangoCorner = pyR.rango

        for ran in rangoCorner:
            for nn in ran:
                if nn not in oppRear:

                    self.processRango(pyFace, pyWire, pyR, pyOppR,
                                      nn, 'rangoCorner', tolerance)

        rangoInter = self.rangoInter
        if rangoInter:
            ran = rangoInter

            for nn in ran:

                self.processRango(pyFace, pyWire, pyR, pyOppR, nn,
                                  'rangoInter', tolerance)

    def processOppRear(self, oppRear, direction, pyFace, pyWire, pyR, pyOppR,
                       oppReflexEnormous, tolerance):

        ''''''

        nWire = pyWire.numWire

        pyWireList = pyFace.wires

        if direction == "forward":
            nGeom = oppRear[1]
        else:
            nGeom = oppRear[0]

        pyOppRear = pyWire.planes[nGeom]
        try:
            oppRearPl = pyOppRear.shape.copy()
        except AttributeError:
            [nWire, nGeom] = pyOppRear.angle
            pyOppRear = pyFace.selectPlane(nWire, nGeom)
            oppRearPl = pyOppRear.shape.copy()
        pyR.addLink('cutter', oppRearPl)
        pyOppR.addLink('oppCutter', oppRearPl)
        print 'included oppRear ', (oppRearPl, nWire, nGeom)

        nWire = pyWire.numWire

        if direction == "forward":
            nGeom = oppRear[0]
        else:
            nGeom = oppRear[1]

        pyOppRear = pyWire.planes[nGeom]
        try:
            oppRearPl = pyOppRear.shape.copy()
            pyW = pyWire
        except AttributeError:
            [nWire, nGeom] = pyOppRear.angle
            pyOppRear = pyFace.selectPlane(nWire, nGeom)
            oppRearPl = pyOppRear.shape.copy()
            pyW = pyWireList[nWire]

        oppRearPl = oppRearPl.cut([oppReflexEnormous], tolerance)

        pointWire = pyW.coordinates

        if direction == "forward":
            point = pointWire[nGeom+1]
        else:
            point = pointWire[nGeom]

        print 'point ', point
        vertex = Part.Vertex(point)

        for ff in oppRearPl.Faces:
            section = vertex.section([ff], tolerance)
            if section.Vertexes:
                pyR.addLink('cutter', ff)
                pyOppR.addLink('oppCutter', ff)
                print 'included oppRear rectified ', (oppRearPl, nWire, nGeom)
                break

    def processRango(self, pyFace, pyWire, pyR, pyOppR, nn, kind, tolerance):

        ''''''

        nWire = pyWire.numWire
        oppReflexEnormous = pyOppR.enormousShape
        pyPl = pyWire.planes[nn]

        rectified = ''

        if not pyPl.reflexed:
            print 'A'
            pl = pyPl.shape.copy()

        elif pyPl.aligned:
            print 'B'
            pl = pyPl.simulatedShape
            rectified = 'simulated'

        elif pyPl.choped:
            print 'C'
            pl = pyPl.shape.copy()

        else:
            print 'D'
            forward = pyR.forward
            forwardOpp = pyOppR.forward
            forw = pyPl.forward

            section = forward.section([forw], tolerance)
            sect = forwardOpp.section([forw], tolerance)

            if section.Edges:
                print 'edges'
                pl = None

            else:

                if pyR.numGeom in pyPl.rear:
                    print 'D1'
                    pl = pyPl.simulatedShape
                    rectified = 'simulated'

                elif section.Vertexes:
                    print 'D2'
                    pl = pyPl.shape.copy()

                    if kind == 'rangoInter':
                        pl = pyPl.simulatedShape
                        rectified = 'simulated'

                    elif kind == 'rangoNext':
                        pl = pl.cut([oppReflexEnormous], tolerance)
                        gS = pyPl.geom.toShape()
                        pl = utils.selectFace(pl.Faces, gS, tolerance)
                        rectified = 'rectified'

                elif sect.Vertexes:
                    print 'D3'
                    pl = pyPl.simulatedShape
                    rectified = 'simulated'

                else:
                    print 'D4'
                    pl = pyPl.shape.copy()

        if kind == "rangoCorner":
            print '1'

            if pyPl.reflexed:
                oppPl = pyPl.simulatedShape
                print 'included oppCutter ', kind, ' ', (oppPl, nWire, nn)
                pyOppR.addLink('oppCutter', oppPl)

            else:
                print 'included oppCutter ', kind, ' ', (pl, nWire, nn)
                pyOppR.addLink('oppCutter', pl)

            pl = pl.cut([oppReflexEnormous], tolerance)
            gS = pyPl.geom.toShape()
            pl = utils.selectFace(pl.Faces, gS, tolerance)
            print 'included cutter ', kind, ' ', rectified, (pl, nWire, nn)
            pyR.addLink('cutter', pl)

        else:
            print '2'
            if pl:
                print 'included cutter ', kind, ' ', rectified, (pl, nWire, nn)
                pyR.addLink('cutter', pl)

    def solveReflex(self, face, tolerance):

        ''''''

        print '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$'

        [pyR, pyOppR] = self.planes
        print(pyR.numGeom, pyOppR.numGeom)
        reflex = pyR.shape.copy()
        oppReflex = pyOppR.shape.copy()

        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        aList = self.processReflex(reflex, oppReflex,
                                   pyR, pyOppR, face, tolerance)

        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        bList = self.processReflex(oppReflex, reflex,
                                   pyOppR, pyR, face, tolerance)

        compoundA = Part.makeCompound(aList)
        compoundB = Part.makeCompound(bList)

        lenA = len(aList)
        lenB = len(bList)

        if lenB > 1 and lenA == 1:
            compoundA = compoundA.cut([compoundB], tolerance)
            gS = pyR.geom.toShape()
            compoundA = utils.selectFace(compoundA.Faces, gS, tolerance)

        elif lenA > 1 and lenB == 1:
            compoundB = compoundB.cut([compoundA], tolerance)
            gS = pyOppR.geom.toShape()
            compoundB = utils.selectFace(compoundB.Faces, gS, tolerance)

        pyR.shape = compoundA
        pyOppR.shape = compoundB

    def processReflex(self, reflex, oppReflex, pyR, pyOppR, face, tolerance):

        ''''''

        # TODO no necesito face

        aa = reflex.copy()
        bb = oppReflex.copy()

        bb = bb.cut(pyOppR.oppCutter, tolerance)
        gS = pyOppR.geom.toShape()
        vertex = pyOppR.forward.firstVertex(True)
        for ff in bb.Faces:
            section = ff.section([gS], tolerance)
            if section.Edges:
                section = ff.section([vertex], tolerance)
                if section.Vertexes:
                    bb = ff
                    print 'a'
                    break

        aa = aa.cut(pyR.cutter+[bb], tolerance)
        print aa.Faces

        gS = pyR.geom.toShape()
        forward = pyR.forward
        backward = pyR.backward

        aList = []
        AA = utils.selectFace(aa.Faces, gS, tolerance)
        aList.append(AA)
        print aList
        aa = aa.removeShape([AA])

        cont = True
        for ff in aa.Faces:
            if not cont:
                break
            section = ff.section([backward], tolerance)
            if section.Edges:
                ff = ff.cut([pyOppR.enormousShape], tolerance)
                for cc in ff.Faces:
                    section = cc.section([AA], tolerance)
                    if not section.Edges:
                        section = cc.section([forward, backward], tolerance)
                        if not section.Edges:
                            aList.append(cc)
                            cont = False
                            break

        return aList

    def reviewing(self, tolerance):

        ''''''

        for pyPlane in self.planes:
            pyPlane.isSolved(tolerance)

    def rearing(self, pyWire, tolerance):

        ''''''

        for pyPlane in self.planes:
            pyPlane.rearing(pyWire, self, tolerance)

    def rangging(self, pyWire):

        ''''''

        lenWire = len(pyWire.planes)

        rear = self.planes[0].rear
        oppRear = self.planes[1].rear

        rG = rear[0]
        try:
            oG = oppRear[1]
        except IndexError:
            oG = oppRear[0]

        if oG > rG:
            # print '1'
            ran = range(rG+1, oG)

        elif oG < rG:
            # print '2'
            ranA = range(rG+1, lenWire)
            ranB = range(0, oG)
            ran = ranA + ranB

        # print 'rangoInter ', ran

        self.rangoInter = ran
