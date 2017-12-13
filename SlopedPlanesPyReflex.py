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


__title__ = "SlopedPlanes Macro"
__author__ = "Damian Caceres Moreno"
__url__ = "http://www.freecadweb.org"


class _PyReflex(_Py):

    '''The complementary python object class for reflex corners'''

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

    def virtualizing(self):

        '''virtualizing(self)
        '''

        [pyReflex, pyOppReflex] = self.planes
        pyR = pyReflex.virtualizing()
        pyOppR = pyOppReflex.virtualizing()
        self.planes = [pyR, pyOppR]

    def simulating(self, force=False):

        '''simulating(self, force=False)
        '''

        [pyR, pyOppR] = self.planes

        enormousR = pyR.enormousShape
        enormousOppR = pyOppR.enormousShape

        pyR.simulating(enormousOppR, force)
        pyOppR.simulating(enormousR, force)

    def preProcess(self, pyWire):

        ''''''

        print '############ preProcess'

        pyPlaneList = pyWire.planes
        numWire = pyWire.numWire

        for pyReflexPlane in self.planes:
            print '# pyReflexPlane ', pyReflexPlane.numGeom, pyReflexPlane.control
            rango = pyReflexPlane.rangoConsolidate
            print rango
            pyRan = []
            for nG in rango:
                pyPl = pyPlaneList[nG]
                pyRan.append(pyPl)

            for pyPlane in pyRan:
                cList = []
                plane = pyPlane.shape
                if not pyPlane.choped and plane:

                    print 'pyPlane.numGeom ', pyPlane.numGeom
                    control = pyPlane.control
                    print 'control ', control
                    rangoPost = pyPlane.rangoConsolidate
                    total = control + rangoPost
                    print 'total ', total
                    num = -1
                    for nG in rango:
                        num += 1
                        if nG not in total:
                            pyPl = pyRan[num]
                            print 'pyPl.numGeom ', nG

                            if not pyPl.reflexed:
                                print 'a'
                                cList.append(pyPl.shape)
                                control.append(nG)  # ESTA INCORPORANDO VALORES SIN HACER pyPlane.control = control
                                print pyPl.shape

                            elif pyPl.choped:
                                print 'b'
                                pass

                            elif pyPl.aligned:
                                print 'c'
                                pyAli =\
                                    self.selectAlignment(numWire, nG)
                                if pyAli:
                                    cList.extend(pyAli.simulatedAlignment)
                                    print pyAli.simulatedAlignment

                            else:
                                print 'd'
                                if not pyPlane.reflexed or pyPlane.aligned:
                                    print 'dd'
                                    cList.append(pyPl.simulatedShape)
                                    print pyPl.simulatedShape
                                else:
                                    print 'ddd'
                                    pyReflexList =\
                                        self.selectAllReflex(numWire, nG)
                                    for pyReflex in pyReflexList:
                                        [pyOne, pyTwo] = pyReflex.planes
                                        if pyPlane.numGeom in\
                                           [pyOne.numGeom, pyTwo.numGeom]:
                                            break
                                    else:
                                        cList.append(pyPl.simulatedShape)
                                        print pyPl.simulatedShape

                if cList:
                    print 'cList', cList, pyPlane.numGeom
                    gS = pyPlane.geomShape
                    print plane
                    plane = self.cutting(plane, cList, gS)
                    print plane
                    pyPlane.shape = plane

    def reflexing(self, pyWire):

        '''reflexing(self, pyWire)
        '''

        print '############ reflexing'


        pyPlaneList = self.planes

        pyR = pyPlaneList[0]
        pyOppR = pyPlaneList[1]

        direction = "forward"
        # print '### direction ', direction
        # print(pyR.numGeom, pyOppR.numGeom)

        if not pyR.cutter:
            self.twin(pyWire, pyR, pyOppR, direction)

        direction = "backward"
        # print '### direction ', direction
        # print(pyOppR.numGeom, pyR.numGeom)

        if not pyOppR.cutter:
            self.twin(pyWire, pyOppR, pyR, direction)

    def twin(self, pyWire, pyR, pyOppR, direction):

        '''twin(self, pyWire, pyR, pyOppR, direction)
        '''

        print '# twin pyR.numGeom ', pyR.numGeom, pyR.control

        oppReflexEnormous = pyOppR.enormousShape

        angle = pyR.angle
        numWire = pyWire.numWire
        if ((numWire == 0 and angle > 90) or
           (numWire > 0 and angle < 90)):
            print 'simulated'
            pyR.shape = pyR.simulatedShape

        pyPlaneList = pyWire.planes

        control = pyR.control

        rear = pyR.rear

        for nGeom in rear:

            if nGeom not in control:

                rearPyPl = pyPlaneList[nGeom]
                gS = rearPyPl.geomShape

                if rearPyPl.aligned:
                    print 'a'
                    pyAlign = self.selectAlignment(numWire, nGeom)
                    rearPl = pyAlign.simulatedAlignment
                    pyR.addLink('cutter', rearPl)
                    print 'included rear simulated', (rearPl, numWire, nGeom)

                elif rearPyPl.choped:
                    print 'b'
                    rearPl = rearPyPl.simulatedShape
                    pyR.addLink('cutter', rearPl)
                    print 'included rear simulated ', (rearPl, numWire, nGeom)

                elif rearPyPl.reflexed:
                    print 'c'
                    rearPl = rearPyPl.simulatedShape
                    pyR.addLink('cutter', rearPl)
                    print 'included rear simulated', (rearPl, numWire, nGeom)

                else:
                    print 'd'
                    rearPl = rearPyPl.shape.copy()
                    pyR.addLink('cutter', rearPl)
                    print 'included rear ', (rearPl, numWire, nGeom)

        oppRear = pyOppR.rear

        if len(oppRear) == 1:

            nGeom = oppRear[0]

            if nGeom not in control:

                pyOppRear = pyPlaneList[nGeom]

                if pyOppRear.aligned:
                    print 'a'
                    pyAlign = self.selectAlignment(numWire, nGeom)
                    oppRearPl = pyAlign.simulatedAlignment
                    pyR.addLink('cutter', oppRearPl)
                    print 'included oppRear simulated', (oppRearPl, numWire, nGeom)

                elif pyOppRear.choped:
                    print 'b'
                    oppRearPl = pyOppRear.simulatedShape
                    pyR.addLink('cutter', oppRearPl)
                    print 'included oppRear simulated', (oppRearPl, numWire, nGeom)

                elif pyOppRear.reflexed:
                    print 'c'
                    oppRearPl = pyOppRear.simulatedShape
                    pyR.addLink('cutter', oppRearPl)
                    print 'included oppRear simulated ', (oppRearPl, numWire, nGeom)

                else:
                    print 'd'
                    oppRearPl = pyOppRear.shape.copy()
                    pyR.addLink('cutter', oppRearPl)
                    print 'included oppRear ', (oppRearPl, numWire, nGeom)

        elif len(oppRear) == 2:

            if direction == 'forward':

                self.processOppRear(oppRear, direction, pyWire, pyR,
                                    pyOppR, oppReflexEnormous)

            else:

                self.processOppRear(oppRear, direction, pyWire, pyR,
                                    pyOppR, oppReflexEnormous)

        rangoCorner = pyR.rangoConsolidate
        print 'rangoCorner ', rangoCorner

        for nn in rangoCorner:
            if nn not in control:
                if nn not in oppRear:

                    self.processRango(pyWire, pyR, pyOppR, nn, 'rangoCorner')

        rangoNext = pyOppR.rangoConsolidate
        print 'rangoNext ', rangoNext

        if len(rear) == 1:
            for nn in rangoNext:
                if nn not in control:

                    self.processRango(pyWire, pyR, pyOppR, nn, 'rangoNext')

        rangoInter = self.rango
        print 'rangoInter ', rangoInter

        for nn in rangoInter:
            if nn not in control:

                self.processRango(pyWire, pyR, pyOppR, nn,  'rangoInter')

    def processOppRear(self, oppRear, direction, pyWire, pyR, pyOppR,
                       oppReflexEnormous):

        '''processOppRear(self, oppRear, direction, pyWire, pyR, pyOppR,
                          oppReflexEnormous)
        '''

        nWire = pyWire.numWire

        control = pyR.control

        if direction == "forward":
            nGeom = oppRear[1]
        else:
            nGeom = oppRear[0]

        if nGeom not in control:

            pyOppRear = pyWire.planes[nGeom]

            oppRearPl = pyOppRear.shape.copy()
            pyR.addLink('cutter', oppRearPl)
            print 'included oppRear ', (oppRearPl, nWire, nGeom)

        if direction == "forward":
            nGeom = oppRear[0]
        else:
            nGeom = oppRear[1]

        if nGeom not in control:

            pyOppRear = pyWire.planes[nGeom]
            oppRearPl = pyOppRear.shape.copy()
            oppRearPl = oppRearPl.cut([oppReflexEnormous], _Py.tolerance)

            pointWire = pyWire.coordinates

            if direction == "forward":
                point = pointWire[nGeom+1]
            else:
                point = pointWire[nGeom]

            print 'point ', point
            vertex = Part.Vertex(point)

            for ff in oppRearPl.Faces:
                section = vertex.section([ff], _Py.tolerance)
                if section.Vertexes:
                    pyR.addLink('cutter', ff)
                    print 'included oppRear rectified ', (oppRearPl, nWire, nGeom)
                    break

    def processRango(self, pyWire, pyR, pyOppR, nn, kind):

        ''''''

        numWire = pyWire.numWire
        pyPl = pyWire.planes[nn]
        gS = pyPl.geomShape

        oppReflexEnormous = pyOppR.enormousShape
        reflexEnormous = pyR.enormousShape

        if pyPl.aligned:
            print 'A'
            pyAlign = self.selectAlignment(numWire, nn)
            pl = pyAlign.simulatedAlignment
            pyR.addLink('cutter', pl)
            print 'included rango simulated ', (pl, numWire, nn)

        elif pyPl.choped:
            print 'B'
            pl = pyPl.simulatedShape
            pyR.addLink('cutter', pl)
            print 'included rango simulated', (pl, numWire, nn)

        elif pyPl.reflexed:
            print 'C'
            # pl = pyPl.shape.copy()
            pl = pyPl.simulatedShape.copy()

            pyReflexList = self.selectAllReflex(numWire, nn)

            rear = pyPl.rear
            rango = pyPl.rangoConsolidate

            rRear = pyR.rear
            rRango = pyR.rangoConsolidate

            oppRRear = pyOppR.rear
            oppRRango = pyOppR.rangoConsolidate

            forward = pyR.forward
            backward = pyR.backward
            forwa = pyOppR.forward
            backwa = pyOppR.backward
            fo = pyPl.forward
            ba = pyPl.backward

            if pyR.numGeom in rear:
                print '1'
                

            elif pyOppR.numGeom in rear:
                print '2'
                

            elif pyPl.numGeom in rRear:
                print '3'
                

            elif pyPl.numGeom in rRango:
                print '4'
                pl = pyPl.shape.copy()

                if forward.section([fo], _Py.tolerance).Vertexes:
                    print '41'
                    cList = [reflexEnormous]
                else:
                    print '42'
                    cList = [oppReflexEnormous]

                pl = self.cutting(pl,cList , gS)

            elif pyPl.numGeom in oppRRear:
                print '5'
                

            elif pyPl.numGeom in oppRRango:
                print '6'
                pl = pyPl.shape.copy()

            pyR.addLink('cutter', pl)
            print 'included rango simulated', (pl, numWire, nn)

        else:
            print 'D'
            pl = pyPl.shape.copy()

            if kind == 'rangoCorner':
                print 'D1'
                pl = self.cutting(pl, [oppReflexEnormous], gS)

            pyR.addLink('cutter', pl)
            print 'included rango ', (pl, numWire, nn)

    def solveReflex(self):

        '''solveReflex(self)
        '''

        print '### solveReflexs'

        [pyR, pyOppR] = self.planes

        self.planes = [pyR, pyOppR]

        reflex = pyR.shape.copy()
        oppReflex = pyOppR.shape.copy()

        print(pyR.numGeom, pyOppR.numGeom)
        self.processReflex(reflex, oppReflex,
                           pyR, pyOppR,
                           'forward')
        print(pyOppR.numGeom, pyR.numGeom)
        self.processReflex(oppReflex, reflex,
                           pyOppR, pyR,
                           'backward')

        reflex = pyR.shape.copy()
        oppReflex = pyOppR.shape.copy()

        reflex = reflex.cut([oppReflex], _Py.tolerance)
        oppReflex = oppReflex.cut([reflex], _Py.tolerance)

        if len(pyR.shape.Faces) > 1:
            print 'aa1'
            aList = []
            for ff in pyR.shape.Faces:
                ff = ff.cut([oppReflex], _Py.tolerance)
                aList.append(ff.Faces[0])
            compound = Part.Compound(aList)
            pyR.shape = compound

        else:
            print 'aa2'
            gS = pyR.geomShape
            reflex = self.cutting(reflex, [oppReflex], gS)
            pyR.shape = reflex

        if len(pyOppR.shape.Faces) > 1:
            print 'aa1'
            aList = []
            for ff in pyOppR.shape.Faces:
                ff = ff.cut([reflex], _Py.tolerance)
                aList.append(ff.Faces[0])
            compound = Part.Compound(aList)
            pyOppR.shape = compound

        else:
            print 'aa2'
            gS = pyOppR.geomShape
            oppReflex = self.cutting(oppReflex, [reflex], gS)
            pyOppR.shape = oppReflex

    def processReflex(self, reflex, oppReflex, pyR, pyOppR,
                      direction):

        '''processReflex(self, reflex, oppReflex, pyR, pyOppR,
                         direction)
        '''

        numWire = pyR.numWire
        aa = reflex.copy()

        cList = [pyOppR.enormousShape]
        cList.extend(pyR.cutter)
        print 'pyR.cutter ', pyR.cutter, len(pyR.cutter)

        aa = aa.cut(cList, _Py.tolerance)
        print 'aa.Faces ', aa.Faces
        gS = pyR.geomShape

        cutterList = []
        for ff in aa.Faces:
            section = ff.section([gS], _Py.tolerance)
            if not section.Edges:
                sect = ff.section([_Py.face], _Py.tolerance)
                # if sect.Edges
                if sect.Vertexes:
                    cutterList.append(ff)

        print 'cutterList ', cutterList

        if cutterList:
            reflex = reflex.cut(cutterList, _Py.tolerance)

        reflex = reflex.cut(pyR.cutter, _Py.tolerance)

        print 'reflex.Faces ', reflex.Faces

        aList = []
        for ff in reflex.Faces:
            section = ff.section([gS], _Py.tolerance)
            if section.Edges:
                aList.insert(0, ff)
                reflex = reflex.removeShape([ff])
                break

        print 'aList ', aList

        cornerList = [self.selectPlane(numWire, n).shape
                      for n in pyR.rangoConsolidate]

        bList = []
        for ff in reflex.Faces:
            section = ff.section(aList, _Py.tolerance)
            if not section.Edges:
                section = ff.section(cornerList, _Py.tolerance)
                if section.Edges:
                    common = ff.common([pyR.simulatedShape], _Py.tolerance)
                    if not common.Faces:
                        section = ff.section([pyOppR.simulatedShape], _Py.tolerance)
                        if section.Vertexes:

                            if len(pyOppR.rear) == 1:
                                numOppRear = pyOppR.rear[0]
                            else:
                                if direction == 'forward':
                                    numOppRear = pyOppR.rear[1]
                                else:
                                    numOppRear = pyOppR.rear[0]
                            pyOppRear = self.selectPlane(numWire, numOppRear)
                            oppRear = pyOppRear.shape

                            section = ff.section([oppRear], _Py.tolerance)
                            if not section.Edges:
                                if section.Vertexes:
                                    bList.append(ff)

        print 'bList ', bList

        aList.extend(bList)
        print 'aList ', aList

        compound = Part.makeCompound(aList)
        pyR.shape = compound

    def rearing(self, pyWire):

        '''rearing(self, pyWire)
        '''

        for pyPlane in self.planes:
            # if not pyPlane.reflexed:
            if not pyPlane.choped and not pyPlane.aligned:
                pyPlane.rearing(pyWire, self)

    def rangging(self, pyWire):

        '''rangging(self, pyWire)
        '''

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
