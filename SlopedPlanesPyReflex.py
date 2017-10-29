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

        pass

    def reflexing(self, pyFace, pyWire, tolerance):

        ''''''

        pyPlaneList = self.planes

        pyR = pyPlaneList[0]
        pyOppR = pyPlaneList[1]

        pyR.oppCutter, pyR.cutter = [], []
        pyOppR.oppCutter, pyOppR.cutter = [], []

        direction = "forward"
        # print '### direction ', direction
        # print(pyR.numGeom, pyOppR.numGeom)

        self.twin(pyFace, pyWire, pyR, pyOppR, direction, tolerance)

        direction = "backward"
        # print '### direction ', direction
        # print(pyOppR.numGeom, pyR.numGeom)

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
            pyR.addLink('cutter', oppReflexEnormous)

        nWire = pyWire.numWire

        rear = pyR.rear
        # print '# rear ', rear

        for nGeom in rear:
            rearPyPl = pyWire.planes[nGeom]
            try:
                rearPl = rearPyPl.shape.copy()
            except AttributeError:
                [nWire, nGeom] = rearPyPl.angle
                rearPyPl = pyFace.selectPlane(nWire, nGeom)
                rearPl = rearPyPl.shape.copy()

            if rearPyPl.reflexed:
                pyReflexList = pyFace.selectAllReflex(nWire, nGeom)
                gS = rearPyPl.geom.toShape()
                for pyReflex in pyReflexList:
                    for pyPlane in pyReflex.planes:
                        if pyPlane != rearPyPl:
                            enormous = pyPlane.enormousShape
                            rearPl = rearPl.cut([enormous], tolerance)
                            rearPl = utils.selectFace(rearPl.Faces, gS,
                                                      tolerance)

            pyR.addLink('cutter', rearPl)
            pyOppR.addLink('oppCutter', rearPl)
            # print 'included rear ', (nWire, nGeom)

        nWire = pyWire.numWire

        oppRear = pyOppR.rear
        # print '# oppRear ', oppRear

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
                # print 'included oppRear ', (nWire, nGeom)

            else:

                nG = pyOppRear.numGeom
                pyReflexList = pyFace.selectAllReflex(nWire, nG)

                cutList = []
                for pyReflex in pyReflexList:
                    for pyPl in pyReflex.planes:
                        if pyPl != pyOppRear:
                            cutList.append(pyPl.enormousShape)

                oppRearPl = oppRearPl.cut(cutList, tolerance)
                geomShape = pyOppRear.geom.toShape()
                oppRearPl = utils.selectFace(oppRearPl.Faces, geomShape,
                                             tolerance)
                # print 'included oppRear rectified ', (nWire, nGeom)

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
        # print '# rangoNext ', rangoNext

        if len(rear) == 1:
            for ran in rangoNext:
                for nn in ran:

                    self.processRango(pyFace, pyWire, pyR, pyOppR,
                                      nn, 'rangoNext', tolerance)

        rangoCorner = pyR.rango
        # print '# rangoCorner ', rangoCorner

        for ran in rangoCorner:
            for nn in ran:
                if nn not in oppRear:

                    self.processRango(pyFace, pyWire, pyR, pyOppR,
                                      nn, 'rangoCorner', tolerance)

        rangoInter = self.rangoInter
        if rangoInter:
            ran = rangoInter
            # print '# rangoInter ', ran

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
        # print 'included oppRear ', (nWire, nGeom)

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

        # print 'point ', point
        vertex = Part.Vertex(point)

        for ff in oppRearPl.Faces:
            section = vertex.section([ff], tolerance)
            if section.Vertexes:
                pyR.addLink('cutter', ff)
                pyOppR.addLink('oppCutter', ff)
                # print 'included oppRear rectified ', (nWire, nGeom)
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
            pl = pyPl.shape.copy()

        if not pyPl.reflexed:

            if kind == "rangoCorner":
                # print 'a'
                # print 'included oppCutter ', kind, ' ', (nWire, nn)
                pyOppR.addLink('oppCutter', pl)
                oppReflexEnormous = pyOppR.enormousShape
                pl = pl.cut([oppReflexEnormous], tolerance)
                gS = pyPl.geom.toShape()
                pl = utils.selectFace(pl.Faces, gS, tolerance)
                # print 'included cutter ', kind, ' rectified ', (nWire, nn)
                pyR.addLink('cutter', pl)

            else:
                # print 'b'
                # print 'included cutter ', kind, ' ', (nWire, nn)
                pyR.addLink('cutter', pl)

        else:

            nG = nn
            pyReflexList = pyFace.selectAllReflex(nWire, nG)

            cutList = []
            for pyReflex in pyReflexList:
                for pyP in pyReflex.planes:
                    if pyP != pyPl:
                        cutList.append(pyP.enormousShape)

            forward = pyR.forward
            forw = pyPl.forward
            section = forward.section([forw], tolerance)

            if not section.Edges:

                if section.Vertexes:
                    cutList.append(pyR.enormousShape)
                else:
                    forward = pyOppR.forward
                    section = forward.section([forw], tolerance)
                    if not section.Vertexes:
                        cutList.append(pyOppR.enormousShape)

                pl = pl.cut(cutList, tolerance)
                gS = pyPl.geom.toShape()
                pl = utils.selectFace(pl.Faces, gS, tolerance)
                # print 'c'
                # print 'included cutter ', kind, ' rectified ', (nWire, nn)
                pyR.addLink('cutter', pl)

                if kind == "rangoCorner":
                    # print 'd'
                    # print 'included oppCutter ', kind,
                    # ' rectified ', (nWire, nn)
                    pyOppR.addLink('oppCutter', pl)

    def solveReflex(self, tolerance):

        ''''''

        # TODO REFACTOR
        [pyR, pyOppR] = self.planes
        # print (pyR.numGeom, pyOppR.numGeom)

        rDiv = False
        oppRDiv = False

        aa = pyR.shape.copy()
        bb = pyOppR.shape.copy()

        bb = bb.cut(pyOppR.oppCutter, tolerance)
        gS = pyOppR.geom.toShape()
        vertex = pyOppR.forward.firstVertex(True)
        for ff in bb.Faces:
            section = ff.section([gS], tolerance)
            if section.Edges:
                section = ff.section([vertex], tolerance)
                if section.Vertexes:
                    bb = ff
                    # print 'a'
                    break

        aa = aa.cut(pyR.cutter+[bb], tolerance)
        gS = pyR.geom.toShape()
        # print aa.Faces
        gB = pyR.backward

        aList = []
        AA = utils.selectFace(aa.Faces, gS, tolerance)
        aList.append(AA)

        if len(aa.Faces) == 4:

            rDiv = True
            for ff in aa.Faces:
                section = ff.section(gB, tolerance)
                if section.Edges:
                    ff = ff.cut([pyOppR.enormousShape], tolerance)
                    for FF in ff.Faces:
                        sect = FF.section([gB], tolerance)
                        if not sect.Edges:
                            # print 'aa'
                            aList.append(FF)

        # print aList

        cc = pyR.shape.copy()
        bb = pyOppR.shape.copy()

        cc = cc.cut(pyR.oppCutter, tolerance)
        gS = pyR.geom.toShape()
        vertex = pyR.forward.firstVertex(True)
        for ff in cc.Faces:
            section = ff.section([gS], tolerance)
            if section.Edges:
                section = ff.section([vertex], tolerance)
                if section.Vertexes:
                    # print 'b'
                    cc = ff
                    break

        bb = bb.cut(pyOppR.cutter + [cc], tolerance)
        gS = pyOppR.geom.toShape()
        # print bb.Faces
        gB = pyOppR.backward

        bList = []
        BB = utils.selectFace(bb.Faces, gS, tolerance)
        bList.append(BB)

        if len(bb.Faces) == 4:

            oppRDiv = True
            for ff in bb.Faces:
                section = ff.section(gB, tolerance)
                if section.Edges:
                    ff = ff.cut([pyR.enormousShape], tolerance)
                    for FF in ff.Faces:
                        sect = FF.section([gB], tolerance)
                        if not sect.Edges:
                            # print 'bb'
                            bList.append(FF)

        # print bList

        if oppRDiv and not rDiv:
            # print '1'

            AA = AA.cut(bList, tolerance)
            gS = pyR.geom.toShape()
            AA = utils.selectFace(AA.Faces, gS, tolerance)
            aList = [AA]

        elif rDiv and not oppRDiv:
            # print '2'

            BB = BB.cut(aList, tolerance)
            gS = pyOppR.geom.toShape()
            BB = utils.selectFace(BB.Faces, gS, tolerance)
            bList = [BB]

        compound = Part.makeCompound(aList)
        pyR.shape = compound

        compound = Part.makeCompound(bList)
        pyOppR.shape = compound

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
