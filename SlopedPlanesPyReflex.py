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

        rear = pyR.rear

        for nGeom in rear:
            rearPyPl = pyWire.planes[nGeom]

            if rearPyPl.aligned:
                print rearPyPl.numWire
                print rearPyPl.numGeom
                pyAlign = pyFace.selectAlignament(rearPyPl.numWire,
                                                  rearPyPl.numGeom)
                print pyAlign
                rearPl = pyAlign.simulatedShape

            elif rearPyPl.choped:
                rearPl = rearPyPl.shape

            elif rearPyPl.reflexed:
                rearPl = rearPyPl.simulatedShape

            else:
                rearPl = rearPyPl.shape

            pyR.addLink('cutter', rearPl)
            pyOppR.addLink('oppCutter', rearPl)
            print 'included rear ', (rearPl, nWire, nGeom)

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

                nG = pyOppRear.numGeom
                pyReflexList = pyFace.selectAllReflex(nWire, nG)

                cutList = []
                for pyReflex in pyReflexList:
                    for pyPl in pyReflex.planes:
                        if pyPl != pyOppRear:
                            cutList.append(pyPl.enormousShape)

                if cutList:

                    oppRearPl = oppRearPl.cut(cutList, tolerance)
                    geomShape = pyOppRear.geom.toShape()
                    oppRearPl = utils.selectFace(oppRearPl.Faces, geomShape,
                                                 tolerance)

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

        pyPl = pyWire.planes[nn]
        try:
            pl = pyPl.shape.copy()
        except AttributeError:
            [nWire, nGeom] = pyPl.angle
            pyPl = pyFace.selectPlane(nWire, nGeom)

        if not pyPl.reflexed:

            pl = pyPl.shape.copy()

            if kind == "rangoCorner":
                print 'a'
                print 'included oppCutter ', kind, ' ', (pl, nWire, nn)
                pyOppR.addLink('oppCutter', pl)
                oppReflexEnormous = pyOppR.enormousShape
                pl = pl.cut([oppReflexEnormous], tolerance)
                gS = pyPl.geom.toShape()
                pl = utils.selectFace(pl.Faces, gS, tolerance)
                print 'included cutter ', kind, ' rectified ', (pl, nWire, nn)
                pyR.addLink('cutter', pl)

            else:
                print 'b'
                print 'included cutter ', kind, ' ', (pl, nWire, nn)
                pyR.addLink('cutter', pl)

        elif pyPl.aligned:

            pass

        elif pyPl.choped:

            print 'included cutter ', kind, ' ', (pl, nWire, nn)
            pyR.addLink('cutter', pl)

        else:

            forward = pyR.forward
            forw = pyPl.forward
            section = forward.section([forw], tolerance)

            if not section.Edges:

                cutList = []

                if section.Vertexes:
                    cutList.append(pyR.enormousShape)
                else:
                    forward = pyOppR.forward
                    section = forward.section([forw], tolerance)
                    if not section.Vertexes:
                        cutList.append(pyOppR.enormousShape)

                pl = pyPl.simulatedShape.copy()

                if cutList :
                    pl = pl.cut(cutList, tolerance)
                    gS = pyPl.geom.toShape()
                    pl = utils.selectFace(pl.Faces, gS, tolerance)

                print 'c'
                print 'included cutter ', kind, ' rectified ', (pl, nWire, nn)
                pyR.addLink('cutter', pl)

                if kind == "rangoCorner":
                    print 'd'
                    print 'included oppCutter ', kind, ' rectified ', (pl, nWire, nn)
                    pyOppR.addLink('oppCutter', pl)

    def solveReflex(self, tolerance):

        ''''''

        [pyR, pyOppR] = self.planes
        print (pyR.numGeom, pyOppR.numGeom)

        aList, rDiv, AA = self.processReflex(pyR, pyOppR, tolerance)

        bList, oppRDiv, BB = self.processReflex(pyOppR, pyR, tolerance)

        if oppRDiv and not rDiv:
            print '1'

            AA = AA.cut(bList, tolerance)
            gS = pyR.geom.toShape()
            AA = utils.selectFace(AA.Faces, gS, tolerance)
            aList = [AA]

        elif rDiv and not oppRDiv:
            print '2'

            BB = BB.cut(aList, tolerance)
            gS = pyOppR.geom.toShape()
            BB = utils.selectFace(BB.Faces, gS, tolerance)
            bList = [BB]

        compound = Part.makeCompound(aList)
        pyR.shape = compound

        compound = Part.makeCompound(bList)
        pyOppR.shape = compound

    def processReflex(self, pyR, pyOppR, tolerance):

        ''''''

        rDiv = False

        aa = pyR.shape.copy()
        bb = pyOppR.shape.copy()

        print pyOppR.oppCutter

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
        gS = pyR.geom.toShape()
        print aa.Faces
        gB = pyR.backward

        aList = []
        AA = utils.selectFace(aa.Faces, gS, tolerance)
        aList.append(AA)

        # este condicional sobra
        if len(aa.Faces) == 4:

            rDiv = True
            for ff in aa.Faces:
                section = ff.section(gB, tolerance)
                if section.Edges:
                    ff = ff.cut([pyOppR.enormousShape], tolerance)
                    for FF in ff.Faces:
                        sect = FF.section([gB], tolerance)
                        if not sect.Edges:
                            print 'aa'
                            aList.append(FF)

        return aList, rDiv, AA

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
