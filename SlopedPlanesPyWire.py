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

    '''The complementary python object class for wires.
    Two consecutive edges of the same wire could make a reflex corner.
    The edges of the wire could make alignments with others edges,
    even belonging to different wires.
    The exterior wires round counterclockwise, from the lowerleft point.
    The interior wires round clockwise, from the upperleft point.'''

    def __init__(self, numWire, mono=True):

        ''''''

        self.numWire = numWire
        self.reflexs = []
        self.planes = []
        self.coordinates = []
        self.shapeGeom = []
        self.reset = True
        self.wire = None
        self.mono = mono

    @property
    def numWire(self):

        '''numWire(self)'''

        return self._numWire

    @numWire.setter
    def numWire(self, numWire):

        '''numWire(self, numWire)'''

        self._numWire = numWire

    @property
    def reflexs(self):

        '''reflexs(self)'''

        return self._reflexs

    @reflexs.setter
    def reflexs(self, reflexs):

        '''reflexs(self, reflexs)'''

        self._reflexs = reflexs

    @property
    def planes(self):

        '''planes(self)'''

        return self._planes

    @planes.setter
    def planes(self, planes):

        '''planes(self, planes)'''

        self._planes = planes

    @property
    def coordinates(self):

        '''coordinates(self)'''

        return self._coordinates

    @coordinates.setter
    def coordinates(self, coordinates):

        '''coordinates(self, coordinates)'''

        self._coordinates = coordinates

    @property
    def shapeGeom(self):

        '''shapeGeom(self)'''

        return self._shapeGeom

    @shapeGeom.setter
    def shapeGeom(self, shapeGeom):

        '''shapeGeom(self, shapeGeom)'''

        self._shapeGeom = shapeGeom

    @property
    def reset(self):

        '''reset(self)'''

        return self._reset

    @reset.setter
    def reset(self, reset):

        '''reset(self, reset)'''

        self._reset = reset

    @property
    def wire(self):

        '''wire(self)'''

        return self._wire

    @wire.setter
    def wire(self, wire):

        '''wire(self, wire)'''

        self._wire = wire

    @property
    def mono(self):

        '''mono(self)'''

        return self._mono

    @mono.setter
    def mono(self, mono):

        '''mono(self, mono)'''

        self._mono = mono

    def planning(self, reset):

        '''planning(self, reset):
        Transfers to PyPlane.
        Arranges the reflex range and its planes ranges.'''

        if len(self.coordinates) == 2:

            pyPlane = self.planes[0]
            pyPlane.planning(self, True)

        else:

            reflexList = self.reflexs

            for pyPlane in self.planes:
                pyPlane.planning(self)

            if reset:
                for pyReflex in reflexList:
                    pyReflex.rangging(self)

            pyPlaneList = self.planes

            for pyReflex in reflexList:
                for pyPlane in pyReflex.planes:

                    cc = []
                    for ran in pyPlane.rango:
                        c = []
                        for nn in ran:
                            pyPl = pyPlaneList[nn]
                            c.append(pyPl)
                        cc.append(c)
                    pyPlane.rangoPy = cc

    def virtualizing(self):

        '''virtualizing(self)
        Assigns the forward and backward to the reflexs.
        Transfers to PyReflex'''

        # print '###### virtualizing wire ', self.numWire

        reflexList = self.reflexs[:]

        reflexList.reverse()

        controlList = []

        for pyReflex in reflexList:

            if not pyReflex.lines:

                [pyR, pyOppR] = pyReflex.planes
                # print '### ', (pyR.numGeom, pyOppR.numGeom)

                if pyOppR in controlList:
                    # print 'A'

                    pyReflex.addValue('lines', pyR.forward, 'forward')
                    pyReflex.addValue('lines', pyOppR.backward, 'backward')

                else:
                    # print 'B'

                    if pyOppR.aligned:
                        # print 'B1'

                        pyReflex.addValue('lines', pyR.forward, 'forward')
                        pyReflex.addValue('lines', pyOppR.backward, 'backward')

                    else:
                        # print 'B2'

                        pyReflex.addValue('lines', pyR.forward, 'forward')
                        pyReflex.addValue('lines', pyOppR.forward, 'backward')

                controlList.append(pyR)

            else:

                break

        for pyReflex in reflexList:

            pyReflex.virtualizing()

    def trimming(self):

        '''trimming(self)
        The reflex corners acts like a dam, blocking the path to others planes,
        except another reflex plane or an alignment.'''

        # print '###### trimming reflexs numWire ', self.numWire

        pyPlaneList = self.planes
        tolerance = _Py.tolerance

        for pyReflex in self.reflexs:

            num = -1
            for pyPlane in pyReflex.planes:
                num += 1
                # print '### cutter ', pyPlane.numGeom

                numGeom = pyPlane.numGeom
                enormousShape = pyPlane.enormousShape

                pyOppPlane = pyReflex.planes[num - 1]

                rango, rangoPy, oppRango, oppRangoPy, nextRango =\
                    [], [], [], [], []

                if num == 0:
                    # print 'A'

                    rear = pyReflex.rear[0]
                    oppRear = pyReflex.rear[1]
                    forward = pyReflex.lines[0]

                    if rear is not None:
                        # print 'A1'
                        rango = pyPlane.rango[0]
                        rangoPy = pyPlane.rangoPy[0]

                    if oppRear is not None:
                        # print 'A2'
                        oppRango = pyOppPlane.rango[-1]
                        oppRangoPy = pyOppPlane.rangoPy[-1]

                        if len(pyOppPlane.rango) > 1:
                            nextRango = pyOppPlane.rango[0]

                    if self.numWire > 0:

                        try:
                            rr = pyOppPlane.rear[-1]

                        except IndexError:
                            pass

                        else:
                            if rr is not oppRear:
                                pyPl = pyPlaneList[rr]

                                pyPl.cuttingPyth([enormousShape])
                                pyPl.control.append(numGeom)

                                pl = pyPl.shape.copy()
                                pl = pl.cut([pyOppPlane.enormousShape],
                                            tolerance)
                                point = self.coordinates[rr + 1]
                                pl = self.selectFacePoint(pl, point)

                                pyPlane.cuttingPyth([pl])
                                pyPlane.control.append(rr)

                else:
                    # print 'B'

                    rear = pyReflex.rear[1]
                    oppRear = pyReflex.rear[0]
                    forward = pyReflex.lines[-1]

                    if rear is not None:
                        # print 'B1'
                        rango = pyPlane.rango[-1]
                        rangoPy = pyPlane.rangoPy[-1]

                    if oppRear is not None:
                        # print 'B2'
                        oppRango = pyOppPlane.rango[0]
                        oppRangoPy = pyOppPlane.rangoPy[0]

                        if len(pyOppPlane.rango) > 1:
                            nextRango = pyOppPlane.rango[-1]

                    if self.numWire > 0:

                        try:
                            rr = pyOppPlane.rear[0]

                        except IndexError:
                            pass

                        else:
                            if rr is not oppRear:
                                pyPl = pyPlaneList[rr]

                                pyPl.cuttingPyth([enormousShape])
                                pyPl.control.append(numGeom)

                                pl = pyPl.shape.copy()
                                pl = pl.cut([pyOppPlane.enormousShape],
                                            tolerance)
                                point = self.coordinates[rr]
                                pl = self.selectFacePoint(pl, point)

                                pyPlane.cuttingPyth([pl])
                                pyPlane.control.append(rr)

                # print 'rear ', rear
                # print 'rango ', rango
                # print 'rangoPy ', rangoPy
                # print 'forward ', (self.roundVector(forward.firstVertex(True).Point), self.roundVector(forward.lastVertex(True).Point))
                # print 'oppRear ', oppRear
                # print 'oppRango ', oppRango
                # print 'oppRangoPy ', oppRangoPy
                # print 'nextRango ', nextRango

                if pyPlane.secondRear:

                    if num == 0:
                        sR = pyPlane.secondRear[0]
                    else:
                        sR = pyPlane.secondRear[-1]
                    if sR in rango:
                        # print 'secondRear'
                        pyRearPl = pyPlaneList[rear]
                        direction, geom = pyRearPl.direction(self, rear)
                        firstParam = geom.FirstParameter
                        lastParam = geom.LastParameter
                        geomCopy = geom.copy()
                        geomCopy.translate(-1 * _Py.size * direction)
                        scale = 500
                        giantPlane =\
                            pyRearPl.doPlane(direction, self, geomCopy,
                                             firstParam, lastParam,
                                             scale, False)
                        gS = pyPlane.geomShape
                        enormousShape = enormousShape.copy()
                        enormousShape =\
                            self.cutting(enormousShape, [giantPlane], gS)

                for nG, pyPl in zip(rango, rangoPy):
                    control = pyPl.control

                    if numGeom not in control:
                        # print '# cutted ', nG

                        # TODO backRear

                        if not pyPl.aligned and nG in nextRango:
                            # print '0'
                            # rango doesn't cut with nextRango G

                            control.append(numGeom)
                            pyPlane.control.append(nG)

                        elif not pyPl.reflexed:
                            # print 'a'

                            pyPl.trimming(enormousShape)
                            control.append(numGeom)

                        elif pyPl.aligned or pyPl.choped:
                            # print 'b'

                            pass

                        else:
                            # print 'c, interference between reflexs'

                            procc = True
                            pyRList = pyPl.reflexedList
                            # print pyRList

                            for pyR in pyRList:

                                section = forward.section(pyR.lines, tolerance)

                                if section.Vertexes:

                                    procc = False
                                    break

                            if procc:
                                # print 'procc'
                                pyPl.trimming(enormousShape)
                                control.append(numGeom)

                            else:
                                # print 'no procc'
                                pyPl.trimmingTwo(enormousShape)

                    # rango doesn't cut with oppRango
                    if not pyPl.reflexed:
                        for nn, pyP in zip(oppRango, oppRangoPy):
                            if nn not in control:
                                if not pyP.reflexed:
                                    control.append(nn)

    def priorLater(self):

        '''priorLater(self)'''

        # print '###### priorLater wire ', self.numWire

        pyPlaneList = self.planes
        lenWire = len(pyPlaneList)
        numWire = self.numWire

        mono = self.mono

        for pyPlane in pyPlaneList:
            if not pyPlane.aligned:

                numGeom = pyPlane.numGeom
                control = pyPlane.control
                # print '### numGeom ', numGeom

                prior = self.sliceIndex(numGeom - 1, lenWire)
                later = self.sliceIndex(numGeom + 1, lenWire)

                pyPrior = self.selectBasePlane(numWire, prior)
                pyLater = self.selectBasePlane(numWire, later)

                bigPrior = pyPrior.bigShape
                bigLater = pyLater.bigShape

                # print'prior ', (pyPrior.numWire, pyPrior.numGeom)
                # print'later ', (pyLater.numWire, pyLater.numGeom)

                gS = pyPlane.geomShape
                cutterList = []     # shape
                cutList = []        # simulatedShape

                arrow = pyPlane.arrow

                if pyPlane.reflexed:
                    # print 'B reflexed'

                    if prior not in control:

                        if not pyPrior.reflexed or (mono and not arrow and not (pyPlane.choped and pyPrior.aligned)):
                            # print '1'
                            cutterList.append(bigPrior)
                            control.append(prior)
                            if pyPlane.simulatedShape:
                                cutList.append(bigPrior)

                        else:
                            # print '11'

                            if not pyPrior.aligned:

                                pyRPrior = pyPlane.selectReflex(prior)

                                if not pyRPrior:
                                    # print 'reflex successives prior'

                                    if pyPlane.arrow:
                                        nn = self.sliceIndex(prior - 1, lenWire)
                                        pyPl = pyPlaneList[nn]
                                        if numGeom not in pyPl.rear:
                                            # print '111'
                                            cutterList.append(bigPrior)

                                    else:
                                        cutterList.append(bigPrior)
                                        if pyPlane.simulatedShape:
                                            # print 'simulatedShape'
                                            cutList.append(bigPrior)

                    if later not in control:

                        if not pyLater.reflexed or (mono and not arrow and not (pyPlane.choped and pyLater.aligned)):
                            # print '2'
                            cutterList.append(bigLater)
                            control.append(later)
                            if pyPlane.simulatedShape:
                                cutList.append(bigLater)

                        else:
                            # print '21'

                            if not pyLater.aligned:
                                pyRLater = pyPlane.selectReflex(later)

                                if not pyRLater:
                                    # print 'reflex succesives later'

                                    if pyPlane.arrow:
                                        nn = self.sliceIndex(later + 1, lenWire)
                                        pyPl = pyPlaneList[nn]
                                        if numGeom not in pyPl.rear:
                                            # print '211'
                                            cutterList.append(bigLater)

                                    else:
                                        cutterList.append(bigLater)
                                        if pyPlane.simulatedShape:
                                            # print 'simulatedShape'
                                            cutList.append(bigLater)

                elif pyPlane.arrow:
                    # print 'A arrow'

                    if prior not in control:
                        if not pyPrior.reflexed:
                            # print '1'
                            cutterList.append(bigPrior)
                            control.append(prior)
                        else:
                            # print '11'
                            nn = self.sliceIndex(prior - 1, lenWire)
                            pyPl = pyPlaneList[nn]
                            if numGeom not in pyPl.rear:
                                # print '111'
                                cutterList.append(bigPrior)

                    if later not in control:
                        if not pyLater.reflexed:
                            # print '2'
                            cutterList.append(bigLater)
                            control.append(later)
                        else:
                            # print '21'
                            nn = self.sliceIndex(later + 1, lenWire)
                            pyPl = pyPlaneList[nn]
                            if numGeom not in pyPl.rear:
                                # print '211'
                                cutterList.append(bigLater)

                else:
                    # print 'C no arrow no reflexed'

                    cutterList = []

                    if not prior in control:
                        if not (pyPrior.aligned or pyPrior.choped):
                            # print '1'
                            cutterList.append(bigPrior)
                            if not pyPrior.reflexed:
                                # print '11'
                                control.append(prior)

                    if not later in control:
                        if not (pyLater.aligned or pyLater.choped):
                            # print '2'
                            cutterList.append(bigLater)
                            if not pyLater.reflexed:
                                # print '21'
                                control.append(later)

                if cutterList:
                    # print 'D cutterList shape ', cutterList
                    pyPlane.cuttingPyth(cutterList)
                    # print 'pyPlane.shape ', pyPlane.shape

                if cutList:
                    # print 'E cutList simulatedShape ', cutList
                    simulated = pyPlane.simulatedShape
                    simulated = self.cutting(simulated, cutList, gS)
                    pyPlane.simulatedShape = simulated

    def simulating(self):

        '''simulating(self)'''

        for pyReflex in self.reflexs:
            pyReflex.simulating()

    def reflexing(self):

        '''reflexing(self)'''

        # print '###### reflexing wire ', self.numWire

        if not self.mono:

            for pyReflex in self.reflexs:
                pyReflex.preProcess(self)
            # self.printControl('preProcess')

            for pyReflex in self.reflexs:
                pyReflex.reflexing(self)

            for pyReflex in self.reflexs:
                pyReflex.solveReflex(self)
                # self.printControl('solveReflex')
            # self.printControl('solveReflex')

            for pyReflex in self.reflexs:
                pyReflex.postProcess(self)
            # self.printControl('postProcess')

            for pyReflex in self.reflexs:
                pyReflex.postProcessTwo(self)
            # self.printControl('postProcessTwo')

        for pyReflex in self.reflexs:
            pyReflex.rearing(self)

        # '''

        # en interiores un reflexed con una sola trasera da lugar a innecesaria repeticiòn

    def ordinaries(self):

        '''ordinaries(self)'''

        for pyPlane in self.planes:
            if not (pyPlane.choped and not pyPlane.aligned):
                if pyPlane.shape:
                    if not pyPlane.fronted:
                        # print '############ ordinaries ', (pyPlane.numWire, pyPlane.numGeom), pyPlane.shape
                        pyPlane.ordinaries(self)
