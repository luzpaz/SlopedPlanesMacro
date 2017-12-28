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

        pyR.simulating(enormousOppR)
        pyOppR.simulating(enormousR)

    def preProcess(self, pyWire):

        ''''''

        print '############ preProcess'

        pyPlaneList = pyWire.planes
        numWire = pyWire.numWire

        for pyReflexPlane in self.planes:
            print '###### pyReflexPlane ', pyReflexPlane.numGeom, pyReflexPlane.control
            rango = pyReflexPlane.rangoConsolidate
            # trabaja entre si los planos incluidos en un rango
            print 'rango ', rango
            pyRan = []
            for nG in rango:
                pyPl = pyPlaneList[nG]
                pyRan.append(pyPl)

            for pyPlane in pyRan:
                cList = []
                plane = pyPlane.shape
                if not pyPlane.choped and not pyPlane.aligned:

                    control = pyPlane.control
                    print '### pyPlane.numGeom ', pyPlane.numGeom, control
                    rangoPost = pyPlane.rangoConsolidate
                    total = control + rangoPost
                    print 'total ', total
                    num = -1
                    for nG in rango:
                        num += 1
                        if nG not in total:
                            pyPl = pyRan[num]
                            print '# pyPl.numGeom ', nG

                            if not pyPl.reflexed:
                                print 'a'
                                cList.append(pyPl.shape)
                                control.append(nG)
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
        print '### direction ', direction
        print(pyR.numGeom, pyOppR.numGeom)

        if not pyR.cutter:      # esto podría cambiar
            self.twin(pyWire, pyR, pyOppR, direction)

        direction = "backward"
        print '### direction ', direction
        print(pyOppR.numGeom, pyR.numGeom)

        if not pyOppR.cutter:      # esto podría cambiar
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
            # TODO perhaps this could be more elaborated

        pyPlaneList = pyWire.planes

        control = pyR.control

        rear = pyR.rear

        for nGeom in rear:

            if nGeom not in control:

                rearPyPl = pyPlaneList[nGeom]

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
                    control.append(nGeom)

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
                    control.append(nGeom)

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

        control = pyR.control

        if direction == "forward":
            nGeom = oppRear[1]
        else:
            nGeom = oppRear[0]

        if nGeom not in control:

            pyOppRear = pyWire.planes[nGeom]

            oppRearPl = pyOppRear.shape.copy()
            pyR.addLink('cutter', oppRearPl)
            print 'included oppRear ', (oppRearPl, pyWire.numWire, nGeom)
            control.append(nGeom)

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
                    print 'included oppRear rectified ', (oppRearPl, pyWire.numWire, nGeom)
                    break

    def processRango(self, pyWire, pyR, pyOppR, nn, kind):

        ''''''

        control = pyR.control

        numWire = pyWire.numWire
        lenWire = len(pyWire.planes)
        numGeom = pyR.numGeom
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
            pl = pyPl.simulatedShape.copy()

            rear = pyPl.rear
            rango = pyPl.rangoConsolidate

            rRango = pyR.rangoConsolidate
            oppRRango = pyOppR.rangoConsolidate

            forward = pyR.forward
            forwa = pyOppR.forward
            fo = pyPl.forward

            if numGeom in rear:
                print '1'
                pass
                # pl = pyPl.simulatedShape.copy()

            elif pyOppR.numGeom in rear:
                print '2'

                pl = pyPl.shape.copy()
                cList = [oppReflexEnormous]
                pl = self.cutting(pl, cList, gS)
                pyR.addLink('cutter', pl)
                print 'included rango ', (pl, numWire, nn)

                pl = pyPl.simulatedShape.copy()     # Two faces included

            elif nn in rRango:  # rangoCorner
                print '4'
                # pl = pyPl.simulatedShape.copy()

                '''if forward.section([gS], _Py.tolerance).Vertexes:
                    print '41'
                    pass
                    # pl = pyPl.simulatedShape.copy()'''

                #elif forward.section([fo], _Py.tolerance).Vertexes:
                if forward.section([fo], _Py.tolerance).Vertexes:
                    print '42'

                    if numGeom in rango:
                        print '421'
                        if pyR.simulatedShape.section([pyR.backward], _Py.tolerance).Edges:
                            print '4211'
                            pl = pyPl.shape.copy()
                            cList = [reflexEnormous]
                            pl = self.cutting(pl, cList, gS)
                        else:
                            print '4212'
                            cList = [reflexEnormous]
                            pl = self.cutting(pl, cList, gS)

                    else:
                        print '422'
                        cList = [reflexEnormous]
                        pl = self.cutting(pl, cList, gS)

                else:
                    print '43'
                    pl = pyPl.shape.copy()
                    cList = [oppReflexEnormous]
                    pl = self.cutting(pl, cList, gS)

                    '''if (nn <= self.sliceIndex(numGeom+2, lenWire) or nn <= self.sliceIndex(numGeom-2, lenWire)):
                        print '431'
                        pl = pyPl.shape.copy()
                        pl = self.cutting(pl, [oppReflexEnormous], gS)

                    else:
                        print '432'
                        pass
                        # pl = pyPl.simulatedShape.copy()'''

            elif nn in oppRRango:  # rangoNext
                print '6'
                if forwa.section([gS], _Py.tolerance).Vertexes:
                    print '61'
                    pass
                    # pl = pyPl.simulatedShape.copy()
                else:
                    print '62'
                    pl = pyPl.shape.copy()
                    pl = self.cutting(pl, [oppReflexEnormous], gS)

                    '''if (nn <= self.sliceIndex(numGeom+2, lenWire) or nn <= self.sliceIndex(numGeom-2, lenWire)):
                        print '621'
                        pl = pyPl.shape.copy()
                        pl = self.cutting(pl, [oppReflexEnormous], gS)
                    else:
                        print '622'
                        pass
                        #pl = pyPl.simulatedShape.copy()'''

            pyReflexList = self.selectAllReflex(numWire, nn)

            for pyReflex in pyReflexList:
                for pyPlane in pyReflex.planes:
                    if pyPlane != pyPl:
                        if numGeom in pyPlane.rear:
                            pl = pyPl.simulatedShape.copy()
                            print '7'
                            break

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
            control.append(nn)

    def solveReflex(self, pyWire):

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

    def processReflex(self, reflex, oppReflex, pyR, pyOppR,
                      direction):

        '''processReflex(self, reflex, oppReflex, pyR, pyOppR,
                         direction)
        '''

        aa = reflex.copy()

        cList = [pyOppR.enormousShape]
        if not pyR.aligned:
            cList.extend(pyR.cutter)
        print 'pyR.cutter ', pyR.cutter, len(pyR.cutter)

        aa = aa.cut(cList, _Py.tolerance)
        print 'aa.Faces ', aa.Faces, len(aa.Faces)
        gS = pyR.geomShape

        cutterList = []
        for ff in aa.Faces:
            section = ff.section([gS], _Py.tolerance)
            if not section.Edges:
                section = ff.section([_Py.face], _Py.tolerance)
                if section.Edges:
                    cutterList.append(ff)
                elif section.Vertexes:
                    section = ff.section([pyOppR.shape])
                    if section.Edges:
                        cutterList.append(ff)

        print 'cutterList ', cutterList, len(cutterList)

        if cutterList:
            reflex = reflex.cut(cutterList, _Py.tolerance)
            print 'reflex.Faces ', reflex.Faces, len(reflex.Faces)

        reflex = reflex.cut(pyR.cutter, _Py.tolerance)
        print 'reflex.Faces ', reflex.Faces, len(reflex.Faces)

        aList = []
        for ff in reflex.Faces:
            section = ff.section([gS], _Py.tolerance)
            if section.Edges:
                aList.append(ff)
                reflex = reflex.removeShape([ff])
                break

        print 'aList ', aList, len(aList)

        # comp = Part.makeCompound(cList)

        if reflex.Faces:
            reflex = reflex.cut([pyOppR.enormousShape], _Py.tolerance)
            print 'reflex.Faces ', reflex.Faces, len(reflex.Faces)

        bList = []
        for ff in reflex.Faces:
            print 'a', ff.Area
            '''section = ff.section([comp], _Py.tolerance)
            # ==
            if len(section.Edges) >= len(ff.Edges):'''
            print 'b'
            section = ff.section(aList, _Py.tolerance)
            if not section.Edges:
                print 'c'
                common = ff.common([pyR.simulatedShape], _Py.tolerance)
                if not common.Faces:
                    print 'd'
                    bList.append(ff)
                    # break

        print 'bList ', bList

        aList.extend(bList)
        print 'aList ', aList

        # aList = aa.Faces

        compound = Part.makeCompound(aList)
        pyR.shape = compound

    def postProcessOne(self, pyWire):

        '''postProcessOne(self, pyWire)
        cleans the eaves with multiple faces
        '''

        # print '############ postProcessOne'

        [pyR, pyOppR] = self.planes

        if len(pyR.shape.Faces) > 1:
            # print 'A ', pyR.numGeom

            dList = [pyPlane.shape for pyPlane in pyWire.planes if pyPlane.numGeom is not pyR.numGeom and pyPlane.shape]
            comp = Part.makeCompound(dList)

            cList = []
            for ff in pyR.shape.Faces[1:]:
                # print 'a'
                # print len(ff.Edges)
                section = ff.section([comp], _Py.tolerance)
                # print len(section.Edges)
                if len(section.Edges) >= len(ff.Edges):
                    # print 'aa'
                    cList.append(ff)

            # print cList
            if cList:
                cList.insert(0, pyR.shape.Faces[0])
                compound = Part.makeCompound(cList)
            else:
                compound = Part.makeCompound([pyR.shape.Faces[0]])
            pyR.shape = compound

        if len(pyOppR.shape.Faces) > 1:
            # print 'B ', pyOppR.numGeom

            dList = [pyPlane.shape for pyPlane in pyWire.planes if pyPlane.numGeom is not pyOppR.numGeom and pyPlane.shape]
            comp = Part.makeCompound(dList)

            cList = []
            for ff in pyOppR.shape.Faces[1:]:
                # print 'b'
                # print len(ff.Edges)
                section = ff.section([comp], _Py.tolerance)
                # print len(section.Edges)
                if len(section.Edges) >= len(ff.Edges):
                    # print 'bb'
                    cList.append(ff)

            # print cList
            if cList:
                cList.insert(0, pyOppR.shape.Faces[0])
                compound = Part.makeCompound(cList)
            else:
                compound = Part.makeCompound([pyOppR.shape.Faces[0]])
            pyOppR.shape = compound

    def postProcessThree(self, pyWire):

        ''''''

        # print '############ postProcessThree'

        [pyR, pyOppR] = self.planes

        if len(pyR.shape.Faces) == 1 and len(pyOppR.shape.Faces) == 1:

            # print(pyR.numGeom, pyOppR.numGeom)

            plane = pyR.shape.copy()
            oppPlane = pyOppR.shape.copy()

            plane = plane.cut([oppPlane], _Py.tolerance)
            gS = pyR.geomShape

            cList = []
            for ff in plane.Faces:
                # print'a'
                # print len(ff.Edges)
                if ff.section([gS], _Py.tolerance).Edges:
                    # print 'aa'
                    if ff.section(cList, _Py.tolerance).Edges:
                        # print 'aaa'
                        if plane.section([pyR.backward], _Py.tolerance).Edges:
                            # print 'aaaa'
                            cList = plane.Faces
                            compound = Part.makeCompound(cList)
                            pyR.shape = compound
                        break
                    else:
                        # print 'aab'
                        cList.append(ff)
                else:
                    # print 'b'
                    dList = [pyPlane.shape for pyPlane in pyWire.planes if pyPlane.numGeom is not pyR.numGeom and pyPlane.shape]
                    comp = Part.makeCompound(dList)
                    section = ff.section([comp], _Py.tolerance)
                    # print len(section.Edges)
                    if len(section.Edges) >= len(ff.Edges):
                        # print'bb'
                        if ff.section(cList, _Py.tolerance).Edges:
                            # print 'bbb'
                            if plane.section([pyR.backward], _Py.tolerance).Edges:
                                # print 'bbbb'
                                cList = plane.Faces
                                compound = Part.makeCompound(cList)
                                pyR.shape = compound
                            break
                        else:
                            # print 'bba'
                            cList.append(ff)
            else:
                # print 'compound'
                compound = Part.makeCompound(cList)
                pyR.shape = compound

            oppPlane = oppPlane.cut([plane], _Py.tolerance)
            gS = pyOppR.geomShape

            cList = []
            for ff in oppPlane.Faces:
                # print'a'
                # print len(ff.Edges)
                if ff.section([gS], _Py.tolerance).Edges:
                    # print 'aa'
                    if ff.section(cList, _Py.tolerance).Edges:
                        # print 'aaa'
                        if oppPlane.section([pyOppR.backward], _Py.tolerance).Edges:
                            # print 'aaaa'
                            cList = oppPlane.Faces
                            compound = Part.makeCompound(cList)
                            pyOppR.shape = compound
                        break
                    else:
                        # print 'aab'
                        cList.append(ff)
                else:
                    # print 'b'
                    dList = [pyPlane.shape for pyPlane in pyWire.planes if pyPlane.numGeom is not pyOppR.numGeom and pyPlane.shape]
                    comp = Part.makeCompound(dList)
                    section = ff.section([comp], _Py.tolerance)
                    # print len(section.Edges)
                    if len(section.Edges) >= len(ff.Edges):
                        # print'bb'
                        if ff.section(cList, _Py.tolerance).Edges:
                            # print 'bbb'
                            if oppPlane.section([pyOppR.backward], _Py.tolerance).Edges:
                                # print 'bbbb'
                                cList = oppPlane.Faces
                                compound = Part.makeCompound(cList)
                                pyOppR.shape = compound
                            break
                        else:
                            # print 'bba'
                            cList.append(ff)
            else:
                # print 'compound'
                compound = Part.makeCompound(cList)
                pyOppR.shape = compound

        pyR.control.append(pyOppR.numGeom)
        pyOppR.control.append(pyR.numGeom)

    def postProcessFour(self, pyWire):

        ''''''

        cutterList = []
        for pyReflex in pyWire.reflexs:
            if pyReflex != self:
                for pyPlane in pyReflex.planes:
                    if pyPlane not in self.planes:
                        section = pyPlane.shape.section([pyPlane.forward, pyPlane.backward], _Py.tolerance)
                        if not section.Edges:
                            cutterList.append(pyPlane.shape)
                            for pyPl in self.planes:
                                pyPl.control.append(pyPlane.numGeom)

        if cutterList:

            for pyPl in self.planes:
                pl = pyPl.shape

                if len(pl.Faces) > 1:
                    # print 'aa1'

                    gS = pyPl.geomShape
                    aList = []
                    for ff in pl.Faces:
                        section = ff.section([gS], _Py.tolerance)
                        ff = ff.cut(cutterList, _Py.tolerance)
                        if section.Edges:
                            # print 'aa11'
                            ff = self.selectFace(ff.Faces, gS)
                            aList.append(ff)
                        else:
                            # print 'aa12'
                            aList.append(ff.Faces[0])
                    compound = Part.Compound(aList)
                    pyPl.shape = compound

                else:
                    # print 'aa2'
                    gS = pyPl.geomShape
                    pl = self.cutting(pl, cutterList, gS)
                    compound = Part.Compound([pl])
                    pyPl.shape = compound

    def rearing(self, pyWire):

        '''rearing(self, pyWire)
        '''

        for pyPlane in self.planes:
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
