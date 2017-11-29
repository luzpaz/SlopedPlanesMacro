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


from SlopedPlanesPy import _Py


__title__ = "SlopedPlanes Macro"
__author__ = "Damian Caceres Moreno"
__url__ = "http://www.freecadweb.org"


class _PyWire(_Py):

    '''The complementary python object class for wires'''

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

    def planning(self):

        '''planning(self):
        Transfers to PyPlane
        Arranges the reflex and plane ranges
        '''

        for pyPlane in self.planes:
            if pyPlane.geomAligned:
                pyPlane.planning(self)

        reset = _Py.pyFace.reset
        if reset:
            for pyReflex in self.reflexs:
                pyReflex.rangging(self)
                direction = "forward"
                for pyPlane in pyReflex.planes:
                    pyPlane.rangging(self, direction)
                    direction = "backward"

    def trimming(self):

        '''trimming(self)
        The reflex corners act like a dam
        blocking the progress of others planes'''

        for pyReflex in self.reflexs:
            for pyPlane in pyReflex.planes:
                # print 'cutter ', pyPlane.numGeom

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
                        # print 'cutted ', nG
                        pyPl = pyPlaneList[nG]

                        # TODO pyPl numWire and angle

                        if not pyPl.reflexed:

                            pyPl.trimming(enormousShape)
                            pyPl.addValue('control', pyPlane.numGeom)

                        elif pyPl.aligned:

                            pass

                        else:

                            forward = pyPlane.forward
                            gS = pyPlane.geomShape
                            forw = pyPl.forward
                            section = forward.section([forw, gS],
                                                      _Py.tolerance)

                            if (not section.Edges and
                               len(section.Vertexes) == 1):

                                section = forw.section(section.Vertexes,
                                                       _Py.tolerance)

                                if not section.Vertexes:

                                    procc = True

                                    nWire = pyPl.numWire
                                    nGeom = pyPl.numGeom
                                    pyRList =\
                                        self.selectAllReflex(nWire,
                                                             nGeom)

                                    for pyR in pyRList:
                                        if not procc:
                                            break
                                        for pyP in pyR.planes:
                                            if pyP != pyPl:
                                                ff = pyP.forward
                                                section =\
                                                    ff.section([forward],
                                                               _Py.tolerance)

                                                if section.Vertexes:
                                                    procc = False
                                                    break

                                    if procc:
                                        # print 'procc'
                                        pyPl.trimming(enormousShape)
                                        pyPl.addValue('control',
                                                      pyPlane.numGeom)

    def priorLater(self):

        '''priorLater(self)
        '''

        pyPlaneList = self.planes
        lenWire = len(pyPlaneList)
        numWire = self.numWire
        for pyPlane in pyPlaneList:

            if not pyPlane.aligned:
                plane = pyPlane.shape

                numGeom = pyPlane.numGeom
                # print 'numGeom ', numGeom
                # print 'reflexed ', pyPlane.reflexed
                # print 'choped ', pyPlane.choped
                # print 'arrow ', pyPlane.arrow

                prior = self.sliceIndex(numGeom-1, lenWire)
                later = self.sliceIndex(numGeom+1, lenWire)

                pyPrior = self.selectBasePlane(numWire, prior)
                pyLater = self.selectBasePlane(numWire, later)
                bigPrior = pyPrior.bigShape
                bigLater = pyLater.bigShape

                # print'prior ', (pyPrior.numWire, pyPrior.numGeom)
                # print'later ', (pyLater.numWire, pyLater.numGeom)

                gS = pyPlane.geomShape
                cutterList = []

                if pyPlane.arrow:
                    # print'A'

                    if not pyPrior.reflexed:
                        # print'1'
                        cutterList.append(bigPrior)
                        pyPlane.addValue('control', prior)

                    if not pyLater.reflexed:
                        # print'2'
                        cutterList.append(bigLater)
                        pyPlane.addValue('control', later)

                elif pyPlane.reflexed:
                    # print'B'

                    if not pyPrior.reflexed:
                        # print'1'
                        cutterList.append(bigPrior)
                        pyPlane.addValue('control', prior)
                    elif not (pyPrior.choped or pyPrior.aligned):
                        pyR = self.selectReflex(self.numWire,
                                                  pyPlane.numGeom,
                                                  pyPrior.numGeom)
                        if not pyR:
                            # print '11'
                            cutterList.append(bigPrior)
                            pyPlane.addValue('control', prior)

                    if not pyLater.reflexed:
                        # print'2'
                        cutterList.append(bigLater)
                        pyPlane.addValue('control', later)
                    elif not (pyLater.choped or pyLater.aligned):
                        pyR = self.selectReflex(self.numWire,
                                                  pyPlane.numGeom,
                                                  pyLater.numGeom)
                        if not pyR:
                            # print '21'
                            cutterList.append(bigLater)
                            pyPlane.addValue('control', later)

                else:
                    # print'C'
                    cutterList = [bigPrior, bigLater]
                    pyPlane.addValue('control', prior)
                    pyPlane.addValue('control', later)

                if cutterList:
                    # print'D'
                    plane = self.cutting(plane, cutterList, gS)
                    pyPlane.shape = plane

    def simulating(self):

        '''simulating(self)
        '''

        for pyReflex in self.reflexs:
            pyReflex.virtualizing()

        for pyReflex in self.reflexs:
            pyReflex.simulating()

    def preOrdinaries(self):

        '''preOrdinaries(self)
        '''

        reflexList = []     # attribute
        for pyReflex in self.reflexs:
            [pyR, pyOppR] = pyReflex.planes
            reflexList.extend([pyR.numGeom, pyOppR.numGeom])

        # print 'reflexList ', reflexList

        for pyReflex in self.reflexs:
            pyReflex.preOrdinaries(reflexList)

    def preReflexs(self):

        '''preReflexs(self)
        '''

        for pyReflex in self.reflexs:
            pyReflex.preReflexs()

    def preProcess(self):

        ''''''

        for pyPlane in self.planes:
            ordinar = pyPlane.ordinar
            if ordinar:
                plane = pyPlane.shape
                gS = pyPlane.geomShape
                plane = self.cutting(plane, ordinar, gS)
                pyPlane.shape = plane

    def reflexing(self):

        '''reflexing(self)
        '''

        for pyReflex in self.reflexs:
            pyReflex.reflexing(self)

        for pyReflex in self.reflexs:
            pyReflex.solveReflex()

        for pyReflex in self.reflexs:
            pyReflex.rearReflex(self)

        for pyReflex in self.reflexs:
            pyReflex.compounding()

    def reviewing(self):

        '''reviewing(self)
        '''

        for pyReflex in self.reflexs:
            pyReflex.reviewing()

    def clasifyReflexPlanes(self):

        '''clasifyReflexPlanes(self)
        '''

        solved, unsolved = [], []

        for pyReflex in self.reflexs:
            for pyPlane in pyReflex.planes:
                if pyPlane.unsolved:
                    if pyPlane not in unsolved:
                        unsolved.append(pyPlane)
                else:
                    if pyPlane not in solved:
                        solved.append(pyPlane)

        return solved, unsolved

    def reSolveReflexs(self, solved=[], unsolved=[], counter=0):

        '''reSolveReflexs(self, solved=[], unsolved=[], counter=0)
        '''

        # print 'solved ', [p.numGeom for p in solved]
        # print 'unsolved ', [p.numGeom for p in unsolved]

        if counter > len(solved) + len(unsolved):
            return

        cutterList = [pyPl.shape for pyPl in solved]  # if not pyPl.aligned

        for pyPlane in unsolved[:]:
            # print 'a', pyPlane.numGeom
            plane = pyPlane.shape
            gS = pyPlane.geomShape

            plane = self.cutting(plane, cutterList, gS)
            pyPlane.shape = plane

            if pyPlane.isUnsolved():
                # print 'aa'
                pass

            else:
                # print 'ab'
                unsolved.remove(pyPlane)
                solved.append(pyPlane)

        if not unsolved:
            # print 'return'
            return

        counter += 1
        self.reSolveReflexs(solved, unsolved, counter)

    def betweenReflexs(self):

        '''betweenReflexs(self)
        '''

        pyReflexList = self.reflexs
        lenR = len(pyReflexList)
        num = -1
        for pyReflex in pyReflexList:
            num += 1
            cutterList = []
            prior = self.sliceIndex(num-1, lenR)
            later = self.sliceIndex(num+1, lenR)
            if prior != num:
                pyPriorReflex = pyReflexList[prior]
                cutterList.append(pyPriorReflex)
            if later != num and later != prior:
                pyLaterReflex = pyReflexList[later]
                cutterList.append(pyLaterReflex)

            for pyPlane in pyReflex.planes:

                if not pyPlane.aligned:

                    plane = pyPlane.shape

                    if len(plane.Faces) == 1:

                        cutList = []
                        for pyR in cutterList:
                            for pyPl in pyR.planes:
                                if pyPl != pyPlane:
                                    cutList.append(pyPl.shape)

                        gS = pyPlane.geomShape
                        plane = self.cutting(plane, cutList, gS)
                        pyPlane.shape = plane

    def rearing(self):

        '''rearing(self)
        '''

        for pyReflex in self.reflexs:
            pyReflex.rearing(self)

    def ordinaries(self):

        '''ordinaries(self)
        '''

        for pyPlane in self.planes:
            if not (pyPlane.reflexed and not pyPlane.aligned):
                # no reflexed and no choped. Yes ordinarie and aligned
                # print pyPlane.numGeom
                # print pyPlane.reflexed
                # print pyPlane.choped
                # print pyPlane.aligned
                if pyPlane.shape:
                    # print '############### ordinaries ', pyPlane.numGeom
                    pyPlane.ordinaries(self)
