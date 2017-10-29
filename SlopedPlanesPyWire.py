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
                pyPlane.planning(self, normal, size, reverse)

        print '###### reflex rangos'

        if reset:
            for pyReflex in self.reflexs:

                pyReflex.rangging(self)

                direction = "forward"
                for pyPlane in pyReflex.planes:
                    pyPlane.rangging(self, direction)
                    direction = "backward"

    def trimming(self, pyFace, tolerance):

        ''''''

        for pyReflex in self.reflexs:
            for pyPlane in pyReflex.planes:

                angle = pyPlane.angle
                numWire = pyPlane.numWire
                if ((numWire == 0 and angle > 90) or
                   (numWire > 0 and angle < 90)):
                    return

                rango = pyPlane.rango
                enormousShape = pyPlane.enormousShape
                pyPlaneList = self.planes
                for ran in rango:
                    for nG in ran:
                        pyPl = pyPlaneList[nG]

                        if not pyPl.reflexed:

                            pyPl.trimming(enormousShape, tolerance)

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
                                    pyPl.trimming(enormousShape, tolerance)

    def priorLater(self, pyFace, tolerance):

        ''''''

        numWire = self.numWire
        print 'numWire ', numWire
        pyPlaneList = self.planes
        lenWire = len(pyPlaneList)
        for pyPlane in pyPlaneList:

            if not pyPlane.aligned:
                shape = pyPlane.shape

                numGeom = pyPlane.numGeom
                print 'numGeom ', numGeom
                print 'reflexed ', pyPlane.reflexed
                print 'choped ', pyPlane.choped
                print 'aligned ', pyPlane.aligned
                print 'arrow ', pyPlane.arrow

                prior = utils.sliceIndex(numGeom-1, lenWire)
                pyPrior = pyPlaneList[prior]
                later = utils.sliceIndex(numGeom+1, lenWire)
                pyLater = pyPlaneList[later]

                bigPrior = pyPrior.bigShape
                if not bigPrior:
                    [nW, nG] = pyPrior.angle
                    prior = nG
                    pyPrior = pyFace.selectPlane(nW, nG)
                    bigPrior = pyPrior.bigShape

                bigLater = pyLater.bigShape
                if not bigLater:
                    [nW, nG] = pyLater.angle
                    later = nG
                    pyLater = pyFace.selectPlane(nW, nG)
                    bigLater = pyLater.bigShape

                print 'prior ', (pyPrior.numWire, pyPrior.numGeom)
                print 'later ', (pyLater.numWire, pyLater.numGeom)

                geomShape = pyPlane.geom.toShape()
                cutterList = []

                if pyPlane.reflexed or pyPlane.arrow:
                    print 'A'
                    if not pyPrior.reflexed:
                        print '1'
                        cutterList.append(bigPrior)
                    if not pyLater.reflexed:
                        print '2'
                        cutterList.append(bigLater)

                else:
                    print 'B'
                    cutterList = [bigPrior, bigLater]

                if cutterList:
                    print 'C'
                    shape = shape.cut(cutterList, tolerance)
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

        print '###### reSolveReflexs'

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
                print 'return'
                return

            self.reSolveReflexs(tolerance, solved, unsolved, impossible)

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
