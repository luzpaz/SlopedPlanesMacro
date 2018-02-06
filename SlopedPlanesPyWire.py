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

    '''The complementary python object class for wires. Two consecutive planes
    of the same wire could make a reflex corner.
    The planes of the wire could make alignments with others planes,
    even belonging to different wires.
    The exterior wires round counterclockwise, from the lowerleft point.
    The interior wires round clockwise, from the upperleft point.'''

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

    def virtualizing(self):

        '''virtualizing(self)'''

        for pyReflex in self.reflexs:
            pyReflex.virtualizing()

    def trimming(self):

        '''trimming(self)
        The reflex corners act like a dam, blocking the progress
        of others planes.'''

        print '###### trimming reflexs numWire ', self.numWire

        pyPlaneList = self.planes
        tolerance = _Py.tolerance

        for pyReflex in self.reflexs:
            num = -1
            for pyPlane in pyReflex.planes:
                num += 1
                print '### cutter ', pyPlane.numGeom

                numGeom = pyPlane.numGeom
                numWire = pyPlane.numWire
                enormousShape = pyPlane.enormousShape.copy()

                pyOppPlane = pyReflex.planes[num-1]

                rango = []
                oppRango = []

                if num == 0:
                    if pyPlane.rear:
                        rear = pyPlane.rear[0]
                        rango = pyPlane.rango[0]
                    if pyOppPlane.rear:
                        oppRango = pyOppPlane.rango[-1]
                else:
                    if pyPlane.rear:
                        rear = pyPlane.rear[-1]
                        rango = pyPlane.rango[-1]
                    if pyOppPlane.rear:
                        oppRango = pyOppPlane.rango[0]

                if len(pyPlane.rear) == 1:
                    forward = pyPlane.forward
                else:
                    if num == 0:
                        forward = pyPlane.forward
                    else:
                        forward = pyPlane.backward

                if pyPlane.secondRear:
                    # print 'secondRear'
                    pyRearPl = pyPlaneList[rear]
                    direction, geom = pyRearPl.direction(self, rear)
                    firstParam = geom.FirstParameter
                    lastParam = geom.LastParameter
                    geomCopy = geom.copy()
                    geomCopy.translate(-1*_Py.size*direction)
                    scale = 1000000
                    giantPlane =\
                        pyRearPl.doPlane(direction, geomCopy, firstParam,
                                         lastParam, scale)
                    gS = pyPlane.geomShape
                    enormousShape = self.cutting(enormousShape, [giantPlane], gS)
                    # pyPlane.enormousShape = enormousShape

                for nG in rango:
                    pyPl = pyPlaneList[nG]
                    control = pyPl.control

                    if numGeom not in control:
                        print '# cutted ', nG

                        gS = pyPl.geomShape

                        if not pyPl.reflexed:
                            print 'a'

                            pyPl.trimming(enormousShape)
                            control.append(numGeom)

                        elif pyPl.aligned:
                            print 'b'
                            pass

                        else:
                            print 'c'

                            forw = pyPl.forward     # no deberia seleccionar C?

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
                                    print 'procc'
                                    pyPl.trimming(enormousShape)
                                    control.append(numGeom)

                                else:
                                    print 'no procc'
                                    pyPl.trimmingTwo(enormousShape)

                            else:
                                print 'c2'
                                pyPl.trimmingTwo(enormousShape)

                    if not pyPl.reflexed:
                        for nn in oppRango:
                            pyP = pyPlaneList[nn]
                            if not pyP.reflexed:
                                if nn not in control:
                                    control.append(nn)

    def priorLater(self):

        '''priorLater(self)'''

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
                            # control.append(prior)

                    if later not in control:
                        if not pyLater.reflexed:
                            # print'2'
                            cutterList.append(bigLater)
                            # control.append(later)

                elif pyPlane.reflexed:
                    # print'B'

                    if prior not in control:

                        if not pyPrior.reflexed:
                            # print'1'
                            cutterList.append(bigPrior)
                            # control.append(prior)
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
                                        # print 'simul'
                                        cutList.append(bigPrior)

                    if later not in control:

                        if not pyLater.reflexed:
                            # print'2'
                            cutterList.append(bigLater)
                            # control.append(later)
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
                                        # print 'simul'
                                        cutList.append(bigLater)

                else:
                    # print'C'

                    cutterList = []

                    if not prior in control:
                        if not (pyPrior.aligned or pyPrior.choped):
                            # print '1'
                            cutterList.append(bigPrior)
                            # control.append(prior)

                    if not later in control:
                        if not (pyLater.aligned or pyLater.choped):
                            # print '2'
                            cutterList.append(bigLater)
                            # control.append(later)

                if cutterList:
                    # print'D'
                   pyPlane.cuttingPyth(cutterList)

                if cutList:
                    # print 'E'
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

        for pyReflex in self.reflexs:
            pyReflex.preProcess(self)
        # self.printControl('preProcess')

        for pyReflex in self.reflexs:
            pyReflex.reflexing(self)

        for pyReflex in self.reflexs:
            pyReflex.solveReflex(self)
        # self.printControl('solveReflex')

        for pyReflex in self.reflexs:
            pyReflex.solveReflexTwo(self)
        # self.printControl('solveReflexTwo')

        for pyReflex in self.reflexs:
            pyReflex.rearing(self, False)
        # self.printControl('rearing False')

        for pyReflex in self.reflexs:
            pyReflex.postProcess(self)
        # self.printControl('postProcess')

        for pyReflex in self.reflexs:
            pyReflex.postProcessTwo(self)
        # self.printControl('postProcessTwo')

        for pyReflex in self.reflexs:
            pyReflex.rearing(self, True)

        # '''

        # en interiores un reflexed con una sola trasera da lugar a innecesaria repeticiòn

    def ordinaries(self):

        '''ordinaries(self)'''

         # all plane with shape, except chops and reflexs and fronted. CAMBIAR
        for pyPlane in self.planes:
            # if not (pyPlane.reflexed and not pyPlane.aligned):
            if not (pyPlane.choped and not pyPlane.aligned):
                if pyPlane.shape:
                    if not pyPlane.fronted:
                        # print '###### ordinaries ', (pyPlane.numWire, pyPlane.numGeom)
                        pyPlane.ordinaries(self)
