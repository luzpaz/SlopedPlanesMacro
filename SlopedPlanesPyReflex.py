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
from SlopedPlanesPy import _Py
from SlopedPlanesPyPlane import _PyPlane


__title__ = "SlopedPlanes Macro"
__author__ = "Damian Caceres Moreno"
__url__ = "http://www.freecadweb.org"


class _PyReflex(_Py):

    ''''''

    def __init__(self):

        ''''''

        self.planes = []
        self.rango = []

    @property
    def planes(self):

        ''''''

        return self._planes

    @planes.setter
    def planes(self, planes):

        ''''''

        self._planes = planes

    @property
    def rango(self):

        ''''''

        return self._rango

    @rango.setter
    def rango(self, rango):

        ''''''

        self._rango = rango

    def simulating(self):

        ''''''

        [pyR, pyOppR] = self.planes

        enormousR = pyR.enormousShape
        enormousOppR = pyOppR.enormousShape

        pyR.simulating(enormousOppR)
        pyOppR.simulating(enormousR)

    def virtualizing(self):

        ''''''

        [pyR, pyOppR] = self.planes

        if pyR.aligned:
            if not pyR.geomAligned:
                [numWire, numGeom] = [pyR.numWire, pyR.numGeom]
                dct = pyR.__dict__
                (nW, nG) = pyR.angle
                pyPlane = self.selectPlane(nW, nG)
                shape = pyPlane.shape.copy()
                enormous = pyPlane.enormousShape
                pyR = _PyPlane(numWire, numGeom)
                pyR.__dict__ = dct
                pyR.shape = shape
                pyR.enormousShape = enormous

        if pyOppR.aligned:
            if not pyOppR.geomAligned:
                [numWire, numGeom] = [pyOppR.numWire, pyOppR.numGeom]
                dct = pyOppR.__dict__
                (nW, nG) = pyOppR.angle
                pyPlane = self.selectPlane(nW, nG)
                shape = pyPlane.shape.copy()
                enormous = pyPlane.enormousShape
                pyOppR = _PyPlane(numWire, numGeom)
                pyOppR.__dict__ = dct
                pyOppR.shape = shape
                pyOppR.enormousShape = enormous

        self.planes = [pyR, pyOppR]

    def reflexing(self, pyWire):

        ''''''

        pyPlaneList = self.planes

        pyR = pyPlaneList[0]
        pyOppR = pyPlaneList[1]

        pyR.oppCutter, pyR.cutter = [], []
        pyOppR.oppCutter, pyOppR.cutter = [], []

        direction = "forward"
        # print '### direction ', direction
        # print(pyR.numGeom, pyOppR.numGeom)

        self.twin(pyWire, pyR, pyOppR, direction)

        direction = "backward"
        # print '### direction ', direction
        # print(pyOppR.numGeom, pyR.numGeom)

        self.twin(pyWire, pyOppR, pyR, direction)

    def twin(self, pyWire, pyR, pyOppR, direction):

        ''''''

        reflexEnormous = pyR.enormousShape.copy()
        pyOppR.addLink('oppCutter', reflexEnormous)

        oppReflexEnormous = pyOppR.enormousShape

        angle = pyR.angle
        numWire = pyWire.numWire
        if ((numWire == 0 and angle > 90) or
           (numWire > 0 and angle < 90)):
            pyR.shape = pyR.simulatedShape

        pyPlaneList = pyWire.planes

        rear = pyR.rear

        for nGeom in rear:
            rearPyPl = pyPlaneList[nGeom]

            if rearPyPl.aligned:
                # print 'a'
                pyAlign = self.selectAlignament(numWire, nGeom)
                rearPl = pyAlign.virtualizedBase
                pyOppR.addLink('oppCutter', rearPl)
                pyR.addLink('cutter', rearPl)
                # print 'included rear simulated', (rearPl, numWire, nGeom)

            elif rearPyPl.choped:
                # print 'b'
                rearPl = rearPyPl.virtualizedBase
                pyR.addLink('cutter', rearPl)
                pyOppR.addLink('oppCutter', rearPl)
                # print 'included rear simulated ', (rearPl, numWire, nGeom)

            elif rearPyPl.reflexed:
                # print 'c'
                rearPl = rearPyPl.simulatedShape
                pyOppR.addLink('oppCutter', rearPl)
                pyR.addLink('cutter', rearPl)
                # print 'included rear simulated', (rearPl, numWire, nGeom)

            else:
                # print 'd'
                rearPl = rearPyPl.shape
                pyR.addLink('cutter', rearPl)
                pyOppR.addLink('oppCutter', rearPl)
                # print 'included rear ', (rearPl, numWire, nGeom)

        oppRear = pyOppR.rear

        if len(oppRear) == 1:

            nGeom = oppRear[0]
            pyOppRear = pyPlaneList[nGeom]

            if pyOppRear.aligned:
                # print 'a'
                pyAlign = self.selectAlignament(numWire, nGeom)
                oppRearPl = pyAlign.virtualizedBase
                pyOppR.addLink('oppCutter', oppRearPl)
                pyR.addLink('cutter', oppRearPl)
                # print 'included oppRear simulated', (rearPl, numWire, nGeom)

            elif pyOppRear.choped:
                # print 'b'
                oppRearPl = pyOppRear.simulatedShape
                pyR.addLink('cutter', oppRearPl)
                pyOppR.addLink('oppCutter', oppRearPl)
                # print 'included oppRear simulated', (oppRearPl, numWire, nGeom)

            elif pyOppRear.reflexed:
                # print 'c'
                oppRearPl = pyOppRear.simulatedShape
                pyR.addLink('cutter', oppRearPl)
                pyOppR.addLink('oppCutter', oppRearPl)
                # print 'included oppRear simulated ', (oppRearPl, numWire, nGeom)

            else:
                # print 'd'
                oppRearPl = pyOppRear.shape
                pyR.addLink('cutter', oppRearPl)
                pyOppR.addLink('oppCutter', oppRearPl)
                # print 'included oppRear ', (oppRearPl, numWire, nGeom)

        elif len(oppRear) == 2:

            if direction == 'forward':

                self.processOppRear(oppRear, direction, pyWire, pyR,
                                    pyOppR, oppReflexEnormous)

            else:

                self.processOppRear(oppRear, direction, pyWire, pyR,
                                    pyOppR, oppReflexEnormous)

        rangoCorner = pyR.rango

        for ran in rangoCorner:
            for nn in ran:
                if nn not in oppRear:

                    self.processRango(pyWire, pyR, pyOppR,
                                      nn, 'rangoCorner')

        rangoNext = pyOppR.rango

        if len(rear) == 1:
            for ran in rangoNext:
                for nn in ran:

                    self.processRango(pyWire, pyR, pyOppR,
                                      nn, 'rangoNext')

        rangoInter = self.rango
        for nn in rangoInter:

            self.processRango(pyWire, pyR, pyOppR, nn,
                              'rangoInter')

    def processOppRear(self, oppRear, direction, pyWire, pyR, pyOppR,
                       oppReflexEnormous):

        ''''''

        nWire = pyWire.numWire

        if direction == "forward":
            nGeom = oppRear[1]
        else:
            nGeom = oppRear[0]

        pyOppRear = pyWire.planes[nGeom]
        oppRearPl = pyOppRear.shape.copy()
        pyR.addLink('cutter', oppRearPl)
        pyOppR.addLink('oppCutter', oppRearPl)
        # print 'included oppRear ', (oppRearPl, nWire, nGeom)

        if direction == "forward":
            nGeom = oppRear[0]
        else:
            nGeom = oppRear[1]

        pyOppRear = pyWire.planes[nGeom]
        oppRearPl = pyOppRear.shape.copy()
        oppRearPl = oppRearPl.cut([oppReflexEnormous], _Py.tolerance)

        pointWire = pyWire.coordinates

        if direction == "forward":
            point = pointWire[nGeom+1]
        else:
            point = pointWire[nGeom]

        # print 'point ', point
        vertex = Part.Vertex(point)

        for ff in oppRearPl.Faces:
            section = vertex.section([ff], _Py.tolerance)
            if section.Vertexes:
                pyR.addLink('cutter', ff)
                pyOppR.addLink('oppCutter', ff)
                # print 'included oppRear rectified ', (oppRearPl, nWire, nGeom)
                break

    def processRango(self, pyWire, pyR, pyOppR, nn, kind):

        ''''''

        nWire = pyWire.numWire
        oppReflexEnormous = pyOppR.enormousShape
        pyPl = pyWire.planes[nn]

        if pyPl.aligned:
            # print 'A'
            pyAlign = self.selectAlignament(nWire, nn)
            pl = pyAlign.virtualizedBase
            pyR.addLink('cutter', pl)
            pyOppR.addLink('oppCutter', pl)
            # print 'included rango simulated ', (pl, nWire, nn)

        elif pyPl.choped:
            # print 'B'
            pl = pyPl.simulatedShape
            pyR.addLink('cutter', pl)
            pyOppR.addLink('oppCutter', pl)
            # print 'included rango simulated', (pl, nWire, nn)

        elif pyPl.reflexed:
            # print 'C'

            if pyOppR.numGeom in pyPl.rear:

                pl = pyPl.simulatedShape
                pyR.addLink('cutter', pl)
                pyOppR.addLink('oppCutter', pl)
                # print 'included rango simulated ', (pl, nWire, nn)

                if kind != 'rangoCorner':

                    pl = pyPl.shape.copy()
                    gS = pyPl.geomShape
                    pl = self.cutting(pl, [oppReflexEnormous], gS)
                    pyR.addLink('divide', pl)
                    # print 'included rango divide', (pl, nWire, nn)

            else:
                pl = pyPl.simulatedShape

                if kind == 'rangoCorner':
                    # print 'Corner'
                    gS = pyPl.geomShape
                    pl = self.cutting(pl, [oppReflexEnormous], gS)

                pyR.addLink('cutter', pl)
                pyOppR.addLink('oppCutter', pl)
                # print 'included rango simulated ', (pl, nWire, nn)

        else:
            # print 'D'
            pl = pyPl.shape.copy()

            if kind == 'rangoCorner':
                # print 'rangoCorner'
                gS = pyPl.geomShape
                pl = self.cutting(pl, [oppReflexEnormous], gS)

            pyR.addLink('cutter', pl)
            pyOppR.addLink('oppCutter', pl)
            # print 'included rango ', (pl, nWire, nn)

    def solveReflex(self):

        ''''''

        [pyR, pyOppR] = self.planes
        # print(pyR.numGeom, pyOppR.numGeom)

        self.planes = [pyR, pyOppR]

        reflex = pyR.shape.copy()
        oppReflex = pyOppR.shape.copy()

        self.processReflex(reflex, oppReflex,
                           pyR, pyOppR,
                           'forward')

        self.processReflex(oppReflex, reflex,
                           pyOppR, pyR,
                           'backward')

    def processReflex(self, reflex, oppReflex, pyR, pyOppR,
                      direction):

        ''''''

        numWire = pyR.numWire

        aa = reflex.copy()
        bb = oppReflex.copy()

        divide = pyR.divide

        bb = bb.cut(pyOppR.oppCutter + divide, _Py.tolerance)
        gS = pyOppR.geomShape
        if len(pyOppR.rear) == 1:
            if numWire == 0:
                vertex = pyOppR.forward.firstVertex(True)
            else:
                vertex = pyOppR.backward.firstVertex(True)
        else:
            if direction == 'backward':
                vertex = pyOppR.forward.firstVertex(True)
            else:
                vertex = pyOppR.backward.firstVertex(True)
        # print vertex.Point

        for ff in bb.Faces:
            section = ff.section([gS], _Py.tolerance)
            if section.Edges:
                section = ff.section([vertex], _Py.tolerance)
                if section.Vertexes:
                    bb = ff
                    # print 'a'
                    break

        # OJO
        cList = pyR.cutter
        if pyR.aligned:
            cList = []

        aa = aa.cut(cList+[bb], _Py.tolerance)

        aList = []
        gS = pyR.geomShape
        AA = self.selectFace(aa.Faces, gS)
        aList.append(AA)
        aa = aa.removeShape([AA])

        forward = pyR.forward
        backward = pyR.backward

        rear = pyR.cutter[0]
        if len(pyOppR.rear) == 1:
            oppRear = pyOppR.cutter[0]
            try:
                firstRangoCorner = pyR.cutter[2]
            except IndexError:
                pass
        else:
            firstRangoCorner = pyR.cutter[3]
            if direction == 'forward':
                oppRear = pyOppR.cutter[1]
            else:
                oppRear = pyOppR.cutter[0]

        if aa.Faces:

            oppReflexEnormous = pyOppR.enormousShape
            aa = aa.cut(divide + [oppReflexEnormous], _Py.tolerance)

            under = []
            for ff in aa.Faces:
                # print 'aa'
                section = ff.section([_Py.face], _Py.tolerance)
                if section.Edges:
                    # print 'bb'
                    section = ff.section([rear], _Py.tolerance)
                    if section.Edges:
                        # print 'cc'
                        aa = aa.removeShape([ff])
                        under.append(ff)
                        ### break

            if under:
                for ff in aa.Faces:
                    # print 'a'
                    section = ff.section([_Py.face], _Py.tolerance)
                    if not section.Edges:
                        # print 'b'
                        section = ff.section(under, _Py.tolerance)
                        if section.Edges:
                            # print 'c'
                            section = ff.section([AA], _Py.tolerance)
                            if not section.Edges:
                                # print 'd'
                                section = ff.section([forward, backward],
                                                     _Py.tolerance)
                                if not section.Edges:
                                    # print 'e'
                                    section = ff.section([rear], _Py.tolerance)
                                    if section.Edges:
                                        # print 'f'
                                        section = ff.section([oppRear],
                                                             _Py.tolerance)
                                        if not section.Edges:
                                            # print 'g'
                                            section =\
                                                ff.section([firstRangoCorner],
                                                           _Py.tolerance)
                                            if section.Vertexes:
                                                # print 'h'
                                                aList.append(ff)
                                                break

        compound = Part.makeCompound(aList)
        if pyR.compound:
            compound = Part.makeCompound([compound, pyR.compound])
        else:
            pyR.compound = compound

    def rearReflex(self, pyWire):

        ''''''

        pyPlaneList = pyWire.planes

        for pyPlane in self.planes:
            if len(pyPlane.compound.Faces) > 1:
                rear = pyPlane.rear
                for nGeom in rear:
                    pyRear = pyPlaneList[nGeom]
                    if pyRear.reflexed:
                        # print 'rearReflex'
                        # print pyRear.numGeom
                        rearPl = pyRear.compound
                        gS = pyRear.geomShape
                        rearPl = self.cutting(rearPl, [pyPlane.compound], gS)
                        pyRear.compound = rearPl

                        # TODO aplica tambien al oppReflex de rearPl

    def compounding(self):

        ''''''

        [pyR, pyOppR] = self.planes

        compoundA = pyR.compound
        compoundB = pyOppR.compound

        lenA = len(compoundA.Faces)
        lenB = len(compoundB.Faces)

        # print lenA
        # print lenB

        if lenB > 1 and lenA == 1:
            # print 'A'
            gS = pyR.geomShape
            compoundA = self.cutting(compoundA, [compoundB], gS)

        elif lenA > 1 and lenB == 1:
            # print 'B'
            gS = pyOppR.geomShape
            compoundB = self.cutting(compoundB, [compoundA], gS)

        elif lenA == 1 and lenB == 1:
            # print 'C'
            # TODO make copy
            gS = pyR.geomShape
            compoundA = self.cutting(compoundA, [compoundB], gS)

            gS = pyOppR.geomShape
            compoundB = self.cutting(compoundB, [compoundA], gS)

        else:
            # print 'D'
            pass

        pyR.shape = compoundA
        pyOppR.shape = compoundB

    def reviewing(self):

        ''''''

        for pyPlane in self.planes:
            pyPlane.isSolved()

    def rearing(self, pyWire):

        ''''''

        for pyPlane in self.planes:
            if not pyPlane.reflexed:
                pyPlane.rearing(pyWire, self)

    def rangging(self, pyWire):

        ''''''

        lenWire = len(pyWire.planes)

        pyR = self.planes[0]
        pyOppR = self.planes[1]
        rear = pyR.rear
        oppRear = pyOppR.rear

        rG = rear[0]
        try:
            oG = oppRear[1]
        except IndexError:
            oG = oppRear[0]

        if oG > rG:
            ran = range(rG+1, oG)

        elif oG < rG:
            ranA = range(rG+1, lenWire)
            ranB = range(0, oG)
            ran = ranA + ranB

        else:
            ran = []

        self.rango = ran
