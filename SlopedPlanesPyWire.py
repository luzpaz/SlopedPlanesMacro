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


import SlopedPlanesUtils as utils
from SlopedPlanesPy import _Py


__title__ = "SlopedPlanes Macro"
__author__ = "Damian Caceres Moreno"
__url__ = "http://www.freecadweb.org"


class _PyWire(_Py):

    ''''''

    def __init__(self, numWire):

        ''''''

        self.numWire = numWire
        self.reflexs = []
        self.planes = []
        self.coordinates = []
        self.shapeGeom = []
        self.reset = False

    @property
    def numWire(self):

        ''''''

        return self._numWire

    @numWire.setter
    def numWire(self, numWire):

        ''''''

        self._numWire = numWire

    @property
    def reflexs(self):

        ''''''

        return self._reflexs

    @reflexs.setter
    def reflexs(self, reflexs):

        ''''''

        self._reflexs = reflexs

    @property
    def planes(self):

        ''''''

        return self._planes

    @planes.setter
    def planes(self, planes):

        ''''''

        self._planes = planes

    @property
    def coordinates(self):

        ''''''

        return self._coordinates

    @coordinates.setter
    def coordinates(self, coordinates):

        ''''''

        self._coordinates = coordinates

    @property
    def shapeGeom(self):

        ''''''

        return self._shapeGeom

    @shapeGeom.setter
    def shapeGeom(self, shapeGeom):

        ''''''

        self._shapeGeom = shapeGeom

    @property
    def reset(self):

        ''''''

        return self._reset

    @reset.setter
    def reset(self, reset):

        ''''''

        self._reset = reset

    def planning(self, reset, normal, size, reverse):

        ''''''

        for pyPlane in self.planes:
            if pyPlane.geomAligned:
                pyPlane.trackShape(self, normal, size, reverse)

        print '###### reflex rangos'

        if reset:
            for pyReflex in self.reflexs:

                pyReflex.ranggingInter(self)

                direction = "forward"
                for pyPlane in pyReflex.planes:
                    pyPlane.rangging(self, direction)
                    direction = "backward"

    def trimming(self, pyFace, tolerance):

        ''''''

        for pyReflex in self.reflexs:
            for pyPlane in pyReflex.planes:
                rango = pyPlane.rango
                enormousShape = pyPlane.enormousShape
                pyPlaneList = self.planes
                for ran in rango:
                    for nG in ran:
                        pyPl = pyPlaneList[nG]

                        if not pyPl.reflexed:

                            pyPl.doTrim(enormousShape, tolerance)

                        else:

                            forward = pyPlane.forward
                            forw = pyPl.forward
                            section = forward.section(forw)

                            if not section.Vertexes:

                                procc = True
                                nWire = pyPl.numWire
                                pyRList = pyFace.selectAllReflex(nWire, nG)
                                for pyR in pyRList:
                                    if not procc:
                                        break
                                    for pyP in pyR.planes:
                                        if pyP != pyPl:
                                            forw = pyP.forward
                                            section =\
                                                forward.section([forw],
                                                                tolerance)
                                            if section.Vertexes:
                                                procc = False
                                                break

                                if procc:
                                    pyPl.doTrim(enormousShape, tolerance)

    def priorLater(self, pyFace, tolerance):

        ''''''

        pyWireList = pyFace.wires
        numWire = self.numWire
        pyPlaneList = self.planes
        lenWire = len(pyPlaneList)
        for pyPlane in pyPlaneList:
            shape = pyPlane.shape
            if shape:

                numGeom = pyPlane.numGeom
                print 'numGeom ', numGeom
                print 'reflexed ', pyPlane.reflexed
                print 'arrow ', pyPlane.arrow

                prior = utils.sliceIndex(numGeom-1, lenWire)
                pyPrior = pyPlaneList[prior]
                bigPrior = pyPrior.bigShape
                if not bigPrior:
                    [nW, nG] = pyPrior.angle
                    prior = nG
                    pyPrior = pyFace.selectPlane(nW, nG)
                    bigPrior = pyPrior.bigShape

                if pyPlane.aligned:
                    pyAlign = pyFace.selectAlignament(numWire, numGeom)
                    pyPl = pyAlign.aligns[-1]
                    [nW, nG] = [pyPl.numWire, pyPl.numGeom]
                    pyW = pyWireList[nW]
                    lenW = len(pyW.planes)
                    later = utils.sliceIndex(nG+1, lenW)
                    pyLater = pyFace.selectPlane(nW, later)
                    bigLater = pyLater.bigShape
                else:
                    later = utils.sliceIndex(numGeom+1, lenWire)
                    pyLater = pyPlaneList[later]
                    bigLater = pyLater.bigShape
                if not bigLater:
                    [nW, nG] = pyLater.angle
                    later = nG
                    pyLater = pyFace.selectPlane(nW, nG)
                    bigLater = pyLater.bigShape

                print 'prior ', prior
                print 'later ', later

                geomShape = pyPlane.geom.toShape()

                cutterList = []
                if pyPlane.reflexed or pyPlane.arrow:
                    print 'A'

                    if not pyPrior.reflexed:
                        print '1'
                        cutterList.append(bigPrior)

                    elif not pyPlane.arrow:
                        print '11'
                        if not pyPrior.aligned:
                            print '111'
                            pyReflex =\
                                pyFace.selectReflex(numWire, numGeom, prior)
                            if not pyReflex:
                                print '1111'
                                cutterList.append(bigPrior)

                        else:
                            numWire = pyPrior.numWire
                            numGeom = pyPrior.numGeom
                            pyAlign = pyFace.selectAlignament(numWire,
                                                            numGeom)
                            chops = []
                            for chop in pyAlign.chops:
                                chops.extend(chop)
                            if pyPlane not in chops:
                                print '112'
                                cutterList.append(bigPrior)

                    if not pyLater.reflexed:
                        print '2'
                        cutterList.append(bigLater)

                    elif not pyPlane.arrow:
                        print '22'
                        if not pyLater.aligned:
                            print '221'
                            pyReflex =\
                                pyFace.selectReflex(numWire, numGeom, later)
                            if not pyReflex:
                                print '2211'
                                cutterList.append(bigLater)

                        else:
                            numWire = pyLater.numWire
                            numGeom = pyLater.numGeom
                            pyAlign = pyFace.selectAlignament(numWire,
                                                            numGeom)
                            chops = []
                            for chop in pyAlign.chops:
                                chops.extend(chop)
                            if pyPlane not in chops:
                                print '222'
                                cutterList.append(bigLater)

                    if cutterList:
                        print '3'
                        shape = shape.cut(cutterList, tolerance)
                        shape = utils.selectFace(shape.Faces, geomShape,
                                                 tolerance)
                        pyPlane.shape = shape

                else:
                    print 'B'

                    shape = shape.cut([bigPrior, bigLater], tolerance)
                    shape = utils.selectFace(shape.Faces, geomShape,
                                             tolerance)
                    pyPlane.shape = shape

    def reflexing(self, pyFace, tolerance):

        ''''''

        for pyReflex in self.reflexs:
            pyReflex.processReflex(pyFace, self, tolerance)

        for pyReflex in self.reflexs:
            pyReflex.solveReflex(tolerance)

    def reviewing(self, tolerance):

        ''''''

        print '###### reviewWire'

        for pyReflex in self.reflexs:
            pyReflex.reviewing(tolerance)

    def clasifyReflexPlanes(self, tolerance):

        ''''''

        print '###### clasifyReflexPlanes'

        solved, unsolved = [], []

        for pyReflex in self.reflexs:
            for pyPlane in pyReflex.planes:
                if pyPlane.solved:
                    solved.append(pyPlane)
                else:
                    unsolved.append(pyPlane)

        return solved, unsolved

    def reSolveReflexs(self, tolerance, solved=[], unsolved=[],
                         impossible=[]):

        ''''''

        print '###### reProcessReflexs'

        for pyPlane in unsolved:
            print 'a'
            plane = pyPlane.shape
            gS = pyPlane.geom.toShape()
            cutterList = [pyPl.shape for pyPl in solved]
            plane = plane.cut(cutterList, tolerance)
            plane = utils.selectFace(plane.Faces, gS, tolerance)
            pyPlane.shape = plane

            if pyPlane.isSolved(tolerance):
                print 'aa'
                unsolved.remove(pyPlane)
                solved.append(pyPlane)
                unsolved.extend(impossible)
                impossible = []

            else:
                print 'ab'
                impossible.append(pyPlane)

            if not unsolved:
                return

            self.reProcessReflexs(tolerance)

    def betweenReflexs(self, tolerance):

        ''''''

        print '###### betweenReflexs'

        pyReflexList = self.reflexs
        lenR = len(pyReflexList)
        num = -1
        for pyReflex in pyReflexList:
            num += 1
            cutterList = []
            prior = utils.sliceIndex(num-1, lenR)
            later = utils.sliceIndex(num+1, lenR)
            if prior != num:
                pyPriorReflex = pyReflexList[prior]
                cutterList.append(pyPriorReflex)
            if later != num and later != prior:
                pyLaterReflex = pyReflexList[later]
                cutterList.append(pyLaterReflex)

            for pyPlane in pyReflex.planes:

                plane = pyPlane.shape

                if len(plane.Faces) == 1:

                    cutList = []
                    for pyR in cutterList:
                        for pyPl in pyR.planes:
                            if pyPl != pyPlane:
                                cutList.append(pyPl.shape)

                    gS = pyPlane.geom.toShape()
                    plane = plane.cut(cutList, tolerance)
                    plane = utils.selectFace(plane.Faces, gS,
                                             tolerance)
                    pyPlane.shape = plane

    def rearing(self, tolerance):

        ''''''

        for pyReflex in self.reflexs:
            pyReflex.rearing(self, tolerance)

    def ordinaries(self, pyFace, tolerance):

        ''''''

        for pyPlane in self.planes:
            if not (pyPlane.reflexed and not pyPlane.aligned):
                if pyPlane.shape:
                    pyPlane.solvePlane(pyFace, self, tolerance)
