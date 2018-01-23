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
__version__ = ""


class _PyWire(_Py):

    '''The complementary python object class for wires.'''

    def __init__(self, numWire):

        ''''''

        self.numWire = numWire
        self.reflexs = []
        self.planes = []
        self.coordinates = []
        self.shapeGeom = []
        self.reset = True

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
        Transfers to PyPlane.
        Arranges the reflex range and its planes ranges.
        '''

        pyPlaneList = self.planes

        for pyPlane in self.planes:
            if pyPlane.geomAligned:
                pyPlane.planning(self)

        reset = _Py.pyFace.reset
        if reset:
            for pyReflex in self.reflexs:
                pyReflex.rangging(self)
                direction = "forward"
                for pyPlane in pyReflex.planes:
                    if pyPlane.rear:
                        pyPlane.rangging(self, direction)
                        direction = "backward"

                        for rr in pyPlane.rear:
                            pyRearPlane = pyPlaneList[rr]
                            pyRearPlane.reared = True

    def virtualizing(self):

        ''''''

        for pyReflex in self.reflexs:
            pyReflex.virtualizing()

    def trimming(self):

        '''trimming(self)
        The reflex corners act like a dam blocking the progress
        of others planes.'''

        # print '###### trimming reflexs numWire ', self.numWire

        pyPlaneList = self.planes
        tolerance = _Py.tolerance

        for pyReflex in self.reflexs:
            num = -1
            for pyPlane in pyReflex.planes:
                num += 1
                # print '### cutter ', pyPlane.numGeom

                pyOppPlane = pyReflex.planes[num-1]
                enormousShape = pyPlane.enormousShape
                numGeom = pyPlane.numGeom
                numWire = pyPlane.numWire

                if num == 0:
                    rango = pyPlane.rango[0]
                    oppRango = pyOppPlane.rango[-1]
                else:
                    rango = pyPlane.rango[-1]
                    oppRango = pyOppPlane.rango[0]

                for nG in rango:
                    pyPl = pyPlaneList[nG]
                    control = pyPl.control

                    if numGeom not in pyPl.control:
                        # print '# cutted ', nG

                        if not pyPl.reflexed:
                            # print 'a'
                            pyPl.trimming(enormousShape)
                            control.append(numGeom)

                        elif pyPl.aligned:
                            # print 'b'
                            pass

                        else:
                            # print 'c'

                            if len(pyPlane.rear) == 1:
                                forward = pyPlane.forward
                            else:
                                if num == 0:
                                    forward = pyPlane.forward
                                else:
                                    forward = pyPlane.backward

                            gS = pyPl.geomShape
                            forw = pyPl.forward
                            section =\
                                forward.section([forw, gS], tolerance)

                            if (not section.Edges and
                               len(section.Vertexes) == 1):
                                # print 'c1'

                                procc = True
                                pyRList =\
                                    self.selectAllReflex(numWire, nG)
                                # print pyRList

                                for pyR in pyRList:
                                    # print '1'
                                    if not procc:
                                        break
                                    for pyP in pyR.planes:
                                        # print '2'
                                        if pyP != pyPl:
                                            # print '3'
                                            ff = pyP.forward
                                            section =\
                                                ff.section([forward],
                                                           tolerance)
                                            if section.Vertexes:
                                                # print '4'
                                                procc = False
                                                break

                                if procc:
                                    # print 'procc'
                                    pyPl.trimming(enormousShape)
                                    control.append(numGeom)

                                else:
                                    # print 'no procc'
                                    pyPl.trimmingTwo(enormousShape)

                            else:
                                # print 'c2'
                                pyPl.trimmingTwo(enormousShape)

                    for nn in oppRango:
                        pyP = pyPlaneList[nn]
                        if not pyP.reflexed:
                            if not nn in control:
                                control.append(nn)

    def priorLater(self):

        '''priorLater(self)
        '''

        # print '###### priorLater wire ', self.numWire

        pyPlaneList = self.planes
        lenWire = len(pyPlaneList)
        numWire = self.numWire

        for pyPlane in pyPlaneList:
            if not pyPlane.aligned:

                plane = pyPlane.shape
                numGeom = pyPlane.numGeom
                control = pyPlane.control
                # print '### numGeom ', numGeom

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
                cutList = []

                if pyPlane.arrow:
                    # print'A'

                    if prior not in control:
                        if not pyPrior.reflexed:
                            # print'1'
                            cutterList.append(bigPrior)
                            control.append(prior)

                    if later not in control:
                        if not pyLater.reflexed:
                            # print'2'
                            cutterList.append(bigLater)
                            control.append(later)

                elif pyPlane.reflexed:
                    # print'B'

                    if prior not in control:

                        if not pyPrior.reflexed:
                            # print'1'
                            cutterList.append(bigPrior)
                            control.append(prior)
                            if pyPlane.simulatedShape:
                                cutList.append(bigPrior)

                        else:
                            if not pyPrior.aligned:
                                pyRPrior =\
                                    self.selectReflex(numWire, numGeom, prior)
                                if not pyRPrior:
                                    # print 'reflex susecivos prior'
                                    cutterList.append(bigPrior)
                                    if pyPlane.simulatedShape:
                                        cutList.append(bigPrior)

                    if later not in control:

                        if not pyLater.reflexed:
                            # print'2'
                            cutterList.append(bigLater)
                            control.append(later)
                            if pyPlane.simulatedShape:
                                cutList.append(bigLater)

                        else:
                            if not pyLater.aligned:
                                pyRLater =\
                                    self.selectReflex(numWire, numGeom, later)
                                if not pyRLater:
                                    # print 'reflex sucesivos later'
                                    cutterList.append(bigLater)
                                    if pyPlane.simulatedShape:
                                        cutList.append(bigLater)

                else:
                    # print'C'

                    cutterList = []

                    if not prior in control:
                        if not (pyPrior.aligned or pyPrior.choped):
                            if not (pyPrior.reflexed and pyPrior.reared):
                                # print '1'
                                cutterList.append(bigPrior)
                                #if pyPrior.bigScale > 1:
                                control.append(prior)

                    if not later in control:
                        if not (pyLater.aligned or pyLater.choped):
                            if not (pyLater.reflexed and pyLater.reared):
                                # print '2'
                                cutterList.append(bigLater)
                                #if pyLater.bigScale > 1:
                                control.append(later)

                if cutterList:
                    # print'D'
                    plane = self.cutting(plane, cutterList, gS)
                    pyPlane.shape = plane

                if cutList:
                    # print 'E'
                    simulated = pyPlane.simulatedShape
                    simulated = self.cutting(simulated, cutList, gS)
                    pyPlane.simulatedShape = simulated

    def simulating(self):

        '''simulating(self)
        '''

        for pyReflex in self.reflexs:
            pyReflex.simulating()

    def reflexing(self):

        '''reflexing(self)
        '''

        # print '###### reflexing wire ', self.numWire

        for pyReflex in self.reflexs:
            pyReflex.preProcess(self)

        for pyReflex in self.reflexs:
            pyReflex.reflexing(self)

        for pyReflex in self.reflexs:
            pyReflex.solveReflex(self)

        for pyReflex in self.reflexs:
            pyReflex.solveReflexTwo(self)

        # TODO problems!!!
        for pyReflex in self.reflexs:
            pyReflex.rearing(self, False)

        for pyReflex in self.reflexs:
            pyReflex.postProcess(self)

        for pyReflex in self.reflexs:
            pyReflex.rearing(self, True)

        # '''

    def ordinaries(self):

        '''ordinaries(self)
        '''

        # the plane to be cutted
        for pyPlane in self.planes:
            # all plane with shape, except chops and reflexs
            if not (pyPlane.reflexed and not pyPlane.aligned):
                if pyPlane.shape:
                    # print '###### ordinaries ', pyPlane.numGeom
                    pyPlane.ordinaries(self)
