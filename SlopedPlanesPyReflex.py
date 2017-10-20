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
from SlopedPlanesUtils import *
import SlopedPlanesPy


__title__ = "SlopedPlanes Macro"
__author__ = "Damian Caceres Moreno"
__url__ = "http://www.freecadweb.org"


class _Reflex(SlopedPlanesPy._Py):

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

    def ranggingInter(self, pyWire):

        ''''''

        print '### ranggingInter'

        lenWire = len(pyWire.planes)

        rear = self.planes[0].rear
        oppRear = self.planes[1].rear

        rG = rear[0]
        try:
            oG = oppRear[1]
        except IndexError:
            oG = oppRear[0]

        if oG > rG:
            print '1'
            ran = range(rG+1, oG)

        elif oG < rG:
            print '2'
            ranA = range(rG+1, lenWire)
            ranB = range(0, oG)
            ran = ranA + ranB

        print 'rangoInter ', ran

        self.rangoInter = ran

    def solveReflex(self, pyFace, pyWire, tolerance):

        ''''''

        print '###### solveReflex '
        numWire = pyWire.numWire
        print '###### numWire', numWire

        pyPlaneList = self.planes

        reflex = pyPlaneList[0]
        oppReflex = pyPlaneList[1]

        reflex.oppCutter = []
        reflex.cutter = []
        oppReflex.oppCutter = []
        oppReflex.cutter = []

        direction = "forward"
        print '### direction ', direction
        print(reflex.numGeom, oppReflex.numGeom)

        self.twin(pyFace, pyWire, reflex, oppReflex, direction, tolerance)

        direction = "backward"
        print '### direction ', direction
        print(oppReflex.numGeom, reflex.numGeom)

        self.twin(pyFace, pyWire, oppReflex, reflex, direction, tolerance)

        aa = reflex.shape.copy()
        bb = oppReflex.shape.copy()

        bb = bb.cut(oppReflex.oppCutter, tolerance)
        gS = oppReflex.geomAligned.toShape()
        bb = selectFace(bb.Faces, gS, tolerance)

        aa = aa.cut(reflex.cutter+[bb], tolerance)
        gS = reflex.geomAligned.toShape()
        aa = selectFace(aa.Faces, gS, tolerance)
        reflex.shape = aa

        aa = reflex.shape.copy()
        bb = oppReflex.shape.copy()

        aa = aa.cut(reflex.oppCutter, tolerance)
        gS = reflex.geomAligned.toShape()
        aa = selectFace(aa.Faces, gS, tolerance)

        bb = bb.cut(oppReflex.cutter + [aa], tolerance)
        gS = oppReflex.geomAligned.toShape()
        bb = selectFace(bb.Faces, gS, tolerance)
        oppReflex.shape = bb

    def twin(self, pyFace, pyWire, reflex, oppReflex, direction, tolerance):

        ''''''

        oppReflexEnormous = oppReflex.enormousShape.copy()
        reflex.addLink('oppCutter', oppReflexEnormous)

        pyWireList = pyFace.wires
        nWire = pyWire.numWire

        rear = reflex.rear
        print '# rear ', rear

        for nGeom in rear:
            rearPyPl = pyWire.planes[nGeom]
            try:
                rearPl = rearPyPl.shape.copy()
            except AttributeError:
                [nWire, nGeom] = rearPyPl.angle
                rearPyPl = pyFace.selectPlane(nWire, nGeom)
                rearPl = rearPyPl.shape.copy()
            reflex.addLink('cutter', rearPl)
            reflex.addLink('oppCutter', rearPl)
            print 'included rear ', (nWire, nGeom)

        #######################################################################

        nWire = pyWire.numWire

        oppRear = oppReflex.rear
        print '# oppRear ', oppRear

        if len(oppRear) == 1:

            nGeom = oppRear[0]
            oppRearPyPl = pyWire.planes[nGeom]
            try:
                oppRearPl = oppRearPyPl.shape.copy()
            except AttributeError:
                [nWire, nGeom] = oppRearPyPl.angle
                oppRearPyPl = pyFace.selectPlane(nWire, nGeom)
                oppRearPl = oppRearPyPl.shape.copy()

            if not oppRearPyPl.reflexed:
                print 'included oppRear ', (nWire, nGeom)

            else:

                nG = oppRearPyPl.numGeom
                pyW = pyWireList[nWire]
                lenWire = len(pyW.planes)
                if direction == 'forward':
                    if nWire == 0:
                        num = sliceIndex(nG+1, lenWire)
                    else:
                        num = sliceIndex(nG-1, lenWire)
                else:
                    if nWire == 0:
                        num = sliceIndex(nG-1, lenWire)
                    else:
                        num = sliceIndex(nG+1, lenWire)

                print 'num ', num

                nPyPlane = pyW.planes[num]
                nPl = nPyPlane.enormousShape

                oppRearPl = oppRearPl.cut([nPl], tolerance)
                geomShape = oppRearPyPl.geomAligned.toShape()
                oppRearPl = selectFace(oppRearPl.Faces, geomShape, tolerance)
                print 'included oppRear rectified ', (nWire, nGeom)

            reflex.addLink('cutter', oppRearPl)

        elif len(oppRear) == 2:

            if direction == 'forward':

                self.processOppRear(oppRear, direction, pyFace, pyWire, reflex,
                                    oppReflexEnormous, tolerance)

            else:

                self.processOppRear(oppRear, direction, pyFace, pyWire, reflex,
                                    oppReflexEnormous, tolerance)

        #######################################################################

        rangoNext = oppReflex.rango
        print '# rangoNext ', rangoNext

        if len(rear) == 1:
            for ran in rangoNext:
                for nn in ran:

                    self.processRango(pyFace, pyWire, reflex, nn, 'rangoNext')

        #######################################################################

        rangoCorner = reflex.rango
        print '# rangoCorner ', rangoCorner

        for ran in rangoCorner:
            for nn in ran:
                if nn not in oppRear:

                    self.processRango(pyFace, pyWire, reflex, nn, 'rangoCorner')

        #######################################################################

        rangoInter = self.rangoInter
        if rangoInter:
            ran = rangoInter
            print '# rangoInter ', ran

            for nn in ran:

                self.processRango(pyFace, pyWire, reflex, nn, 'rangoInter')

    def processOppRear(self, oppRear, direction, pyFace, pyWire, reflex,
                       oppReflexEnormous, tolerance):

        ''''''

        nWire = pyWire.numWire

        pyWireList = pyFace.wires

        if direction == "forward":
            nGeom = oppRear[1]
        else:
            nGeom = oppRear[0]

        oppRearPyPl = pyWire.planes[nGeom]
        try:
            oppRearPl = oppRearPyPl.shape.copy()
        except AttributeError:
            [nWire, nGeom] = oppRearPyPl.angle
            oppRearPyPl = pyFace.selectPlane(nWire, nGeom)
            oppRearPl = oppRearPyPl.shape.copy()
        reflex.addLink('cutter', oppRearPl)
        print 'included oppRear ', (nWire, nGeom)

        nWire = pyWire.numWire

        if direction == "forward":
            nGeom = oppRear[0]
        else:
            nGeom = oppRear[1]

        oppRearPyPl = pyWire.planes[nGeom]
        try:
            oppRearPl = oppRearPyPl.shape.copy()
            pyW = pyWire
        except AttributeError:
            [nWire, nGeom] = oppRearPyPl.angle
            oppRearPyPl = pyFace.selectPlane(nWire, nGeom)
            oppRearPl = oppRearPyPl.shape.copy()
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
                reflex.addLink('cutter', ff)
                print 'included oppRear rectified ',\
                    (nWire, nGeom)
                break

    def processRango(self, pyFace, pyWire, reflex, nn, kind):

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
            print 'included ', kind, ' ', (nWire, nn)
            reflex.addLink('cutter', pl)
            if kind == "rangoCorner":
                reflex.addLink('oppCutter', pl)

