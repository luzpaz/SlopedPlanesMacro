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
__version__ = ""


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

        pyR.simulating([enormousOppR])
        pyOppR.simulating([enormousR])

    def preProcess(self, pyWire):

        '''preProcess(self, pyWire)
        The planes included in a range are cutted between them.
        '''

        # print '### preProcess'

        pyPlaneList = pyWire.planes
        numWire = pyWire.numWire

        for pyReflexPlane in self.planes:
            # print '# pyReflexPlane ', pyReflexPlane.numGeom
            rango = pyReflexPlane.rangoConsolidate
            # print 'rango ', rango
            pyRan = []
            for nG in rango:
                pyPl = pyPlaneList[nG]
                pyRan.append(pyPl)

            for pyPlane in pyRan:
                cList = []
                plane = pyPlane.shape
                if not pyPlane.choped and not pyPlane.aligned:
                    # print 'pyPlane.numGeom ', pyPlane.numGeom

                    control = pyPlane.control
                    rangoPost = pyPlane.rangoConsolidate
                    total = control + rangoPost
                    # print 'total ', total
                    num = -1
                    for nG in rango:
                        num += 1
                        if nG not in total:
                            pyPl = pyRan[num]
                            # print 'pyPl.numGeom ', nG

                            if not pyPl.reflexed:
                                # print 'a'
                                cList.append(pyPl.shape)
                                control.append(nG)

                            elif pyPl.choped:
                                # print 'b'
                                pass

                            elif pyPl.aligned:
                                # print 'c'
                                pyAli =\
                                    self.selectAlignment(numWire, nG)
                                if pyAli:
                                    cList.extend(pyAli.simulatedAlignment)

                            else:
                                # print 'd'
                                if not pyPlane.reflexed or pyPlane.aligned:
                                    # print 'dd'
                                    cList.append(pyPl.simulatedShape)
                                else:
                                    # print 'ddd'
                                    pyReflexList =\
                                        self.selectAllReflex(numWire, nG)
                                    for pyReflex in pyReflexList:
                                        [pyOne, pyTwo] = pyReflex.planes
                                        if pyPlane.numGeom in\
                                           [pyOne.numGeom, pyTwo.numGeom]:
                                            # print 'ddd1'
                                            break
                                    else:
                                        # print 'ddd2'
                                        cList.append(pyPl.simulatedShape)

                if cList:
                    # print 'cList', cList
                    gS = pyPlane.geomShape
                    plane = self.cutting(plane, cList, gS)
                    pyPlane.shape = plane
                    # print 'plane ', plane

    def reflexing(self, pyWire):

        '''reflexing(self, pyWire)
        '''

        pyPlaneList = self.planes
        pyR = pyPlaneList[0]
        pyOppR = pyPlaneList[1]

        direction = "forward"
        print '### direction ', direction
        print(pyR.numGeom, pyOppR.numGeom)
        if not pyR.cutter:
            self.twin(pyWire, pyR, pyOppR, direction)

        direction = "backward"
        print '### direction ', direction
        print(pyOppR.numGeom, pyR.numGeom)
        if not pyOppR.cutter:
            self.twin(pyWire, pyOppR, pyR, direction)

    def twin(self, pyWire, pyR, pyOppR, direction):

        '''twin(self, pyWire, pyR, pyOppR, direction)
        '''

        pyPlaneList = pyWire.planes
        control = pyR.control
        oppReflexEnormous = pyOppR.enormousShape
        numWire = pyWire.numWire

        rear = pyR.rear

        for nGeom in rear:
            if nGeom not in control:

                rearPyPl = pyPlaneList[nGeom]

                if rearPyPl.aligned:
                    # print 'a'
                    pyAlign = self.selectAlignment(numWire, nGeom)
                    rearPl = pyAlign.simulatedAlignment
                    pyR.addLink('cutter', rearPl)
                    # print 'included rear simulated', (numWire, nGeom)

                elif rearPyPl.choped:
                    # print 'b'
                    rearPl = rearPyPl.simulatedShape  # ???
                    pyR.addLink('cutter', rearPl)
                    # print 'included rear simulated ', (numWire, nGeom)

                elif rearPyPl.reflexed:
                    # print 'c'
                    rearPl = rearPyPl.simulatedShape
                    # # OJO
                    # # rearPl = rearPyPl.bigShape
                    pyR.addLink('cutter', rearPl)
                    # print 'included rear simulated', (numWire, nGeom)

                else:
                    # print 'd'
                    rearPl = rearPyPl.shape
                    # # OJO
                    # # rearPl = rearPyPl.bigShape
                    pyR.addLink('cutter', rearPl)
                    # print 'included rear ', (numWire, nGeom)
                    control.append(nGeom)

        oppRear = pyOppR.rear

        if len(oppRear) == 1:
            nGeom = oppRear[0]
            if nGeom not in control:
                pyOppRear = pyPlaneList[nGeom]

                if pyOppRear.aligned:
                    # print 'a'
                    pyAlign = self.selectAlignment(numWire, nGeom)
                    oppRearPl = pyAlign.simulatedAlignment
                    pyR.addLink('cutter', oppRearPl)
                    # print 'included oppRear simulated', (numWire, nGeom)

                elif pyOppRear.choped:
                    # print 'b'
                    oppRearPl = pyOppRear.simulatedShape
                    pyR.addLink('cutter', oppRearPl)
                    # print 'included oppRear simulated', (numWire, nGeom)

                elif pyOppRear.reflexed:
                    # print 'c'
                    oppRearPl = pyOppRear.simulatedShape
                    pyR.addLink('cutter', oppRearPl)
                    # print 'included oppRear simulated ', (numWire, nGeom)

                else:
                    # print 'd'
                    oppRearPl = pyOppRear.shape
                    pyR.addLink('cutter', oppRearPl)
                    # print 'included oppRear ', (numWire, nGeom)
                    control.append(nGeom)

        elif len(oppRear) == 2:

            self.processOppRear(oppRear, direction, pyWire, pyR,
                                pyOppR, oppReflexEnormous)

        rangoCorner = pyR.rangoConsolidate
        # print 'rangoCorner ', rangoCorner

        for nn in rangoCorner:
            if nn not in control:
                if nn not in oppRear:
                    self.processRango(pyWire, pyR, pyOppR, nn, 'rangoCorner', direction)

        rangoNext = pyOppR.rangoConsolidate
        # print 'rangoNext ', rangoNext

        if len(rear) == 1:
            for nn in rangoNext:
                if nn not in control:
                    self.processRango(pyWire, pyR, pyOppR, nn, 'rangoNext', direction)

        rangoInter = self.rango
        # print 'rangoInter ', rangoInter

        for nn in rangoInter:
            if nn not in control:
                self.processRango(pyWire, pyR, pyOppR, nn,  'rangoInter', direction)

    def processOppRear(self, oppRear, direction, pyWire, pyR, pyOppR,
                       oppReflexEnormous):

        '''processOppRear(self, oppRear, direction, pyWire, pyR, pyOppR,
                          oppReflexEnormous)
        '''

        pyPlaneList = pyWire.planes
        tolerance = _Py.tolerance
        control = pyR.control

        if direction == "forward":
            nGeom = oppRear[1]
        else:
            nGeom = oppRear[0]

        if nGeom not in control:
            pyOppRear = pyPlaneList[nGeom]

            oppRearPl = pyOppRear.shape.copy()
            pyR.addLink('cutter', oppRearPl)
            # print 'included oppRear ', (pyWire.numWire, nGeom)
            control.append(nGeom)

        if direction == "forward":
            nGeom = oppRear[0]
        else:
            nGeom = oppRear[1]

        if nGeom not in control:
            pyOppRear = pyPlaneList[nGeom]
            oppRearPl = pyOppRear.shape.copy()
            oppRearPl = oppRearPl.cut([oppReflexEnormous], tolerance)

            pointWire = pyWire.coordinates

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
                    # print 'included oppRear rectified ', (pyWire.numWire, nGeom)
                    break

    def processRango(self, pyWire, pyR, pyOppR, nn, kind, direction):

        ''''''

        tolerance = _Py.tolerance
        numWire = pyWire.numWire
        numGeom = pyR.numGeom
        oppReflexEnormous = pyOppR.enormousShape
        pyPlaneList = pyWire.planes

        pyPl = pyPlaneList[nn]
        gS = pyPl.geomShape

        if pyPl.aligned:
            # print 'A'
            pyAlign = self.selectAlignment(numWire, nn)
            pl = pyAlign.simulatedAlignment
            pyR.addLink('cutter', pl)
            # print 'included rango simulated ', (pl, numWire, nn)

        elif pyPl.choped:
            # print 'B'
            pl = pyPl.simulatedShape
            pyR.addLink('cutter', pl)
            # print 'included rango simulated', (pl, numWire, nn)

        elif pyPl.reflexed:
            # print 'C'
            pl = pyPl.simulatedShape.copy()

            rear = pyPl.rear

            forward = pyR.forward
            forwa = pyOppR.forward
            fo = pyPl.forward

            pyReflexList = self.selectAllReflex(numWire, nn)
            ref = False
            for pyReflex in pyReflexList:
                for pyPlane in pyReflex.planes:
                    if pyPlane != pyPl:
                        if numGeom in pyPlane.rear:
                            # print '0'
                            ref = True
                            break

            if ref:
                if kind == 'rangoCorner':
                    # print '00'
                    pl = self.cutting(pl, [oppReflexEnormous], gS)

            elif numGeom in rear:
                # print '1'
                pass

            elif pyOppR.numGeom in rear:
                # print '2'

                pl = pyPl.shape.copy()
                pl = self.cutting(pl, [oppReflexEnormous], gS)
                pyR.addLink('cutter', pl)
                # print 'included rango ', (pl, numWire, nn)

                pl = pyPl.simulatedShape.copy()     # Two faces included
                if kind == 'rangoCorner':
                    # print '22'
                    pl = self.cutting(pl, [oppReflexEnormous], gS)

            elif kind == 'rangoCorner':
                # print '4'

                if forward.section([fo], tolerance).Vertexes:
                    # print '42'
                    pl = self.cutting(pl, [oppReflexEnormous], gS)

                else:
                    # print '43'
                    pl = pyPl.shape.copy()
                    # cList = [oppReflexEnormous]
                    rang = self.rang(pyWire, numGeom, nn, direction)
                    # print 'rang ', rang
                    cList = []
                    for mm in rang:
                        pyP = pyPlaneList[mm]
                        if pyP.reflexed:
                            if forward.section([pyP.forward, pyP.backward], tolerance).Vertexes:
                                cList.append(pyP.enormousShape)
                    pl = self.cutting(pl, cList, gS)

            elif kind == 'rangoNext':
                # print '6'

                if forwa.section([gS], tolerance).Vertexes:
                    # print '61'
                    pass

                else:
                    # print '62'
                    pl = pyPl.shape.copy()
                    pl = self.cutting(pl, [oppReflexEnormous], gS)

            elif kind == 'rangoInter':
                # print '7'
                pass

            else:
                #print 'NEW CASE'
                pass

            pyR.addLink('cutter', pl)
            # print 'included rango simulated', (pl, numWire, nn)

        else:
            # print 'D'
            pl = pyPl.shape.copy()

            if kind == 'rangoCorner':
                # print 'D1'
                pl = self.cutting(pl, [oppReflexEnormous], gS)

            pyR.addLink('cutter', pl)
            # print 'included rango ', (pl, numWire, nn)
            pyR.control.append(nn)

    def solveReflex(self, pyWire):

        '''solveReflex(self)
        '''

        print '### solveReflexs'

        [pyR, pyOppR] = self.planes

        reflex = pyR.shape.copy()
        oppReflex = pyOppR.shape.copy()

        print '# ', (pyR.numGeom, pyOppR.numGeom)
        self.processReflex(reflex, oppReflex,
                           pyR, pyOppR,
                           'forward', pyWire)

        print '# ', (pyOppR.numGeom, pyR.numGeom)
        self.processReflex(oppReflex, reflex,
                           pyOppR, pyR,
                           'backward', pyWire)

    def processReflex(self, reflex, oppReflex, pyR, pyOppR,
                      direction, pyWire):

        '''processReflex(self, reflex, oppReflex, pyR, pyOppR,
                         direction, pyWire)
        '''

        if not pyR.rear:
            pyR.cutter = [pyOppR.enormousShape]

        tolerance = _Py.tolerance
        pyPlaneList = pyWire.planes

        if isinstance(reflex, Part.Compound):
            secondaries = reflex.Faces[1:]
        else:
            secondaries = []

        aa = reflex.copy()

        cList = [pyOppR.enormousShape]
        if not pyR.aligned:
            cList.extend(pyR.cutter)
        # print 'pyR.cutter ', pyR.cutter, len(pyR.cutter)

        aa = aa.cut(cList, tolerance)
        print 'aa.Faces ', aa.Faces, len(aa.Faces)
        gS = pyR.geomShape

        rear = pyR.rear

        if rear:

            if direction == 'forward':
                rr = pyPlaneList[rear[0]]
                print 'rango ', pyR.rango[0]
                corner = pyR.rango[0]

            else:
                rr = pyPlaneList[rear[-1]]
                print 'rango ', pyR.rango[-1]
                corner = pyR.rango[-1]

            rrG = rr.geomShape
            rrS = rr.shape

            corn = []
            for nn in corner:
                pyPl = pyPlaneList[nn]
                if pyPl.aligned:
                    print 'a'
                    pyAlign = self.selectAlignment(pyWire.numWire, nn)
                    pl = pyAlign.simulatedAlignment
                elif pyPl.reflexed:
                    print 'b'
                    pl = pyPl.simulatedShape
                else:
                    print 'c'
                    pl = pyPl.shape
                corn.append(pl)
            corn = Part.makeCompound(corn)


        cutterList = []
        for ff in aa.Faces:
            section = ff.section([gS], tolerance)
            if not section.Edges:
                section = ff.section([_Py.face], tolerance)
                if section.Edges:
                    cutterList.append(ff)
                elif section.Vertexes:
                    section = ff.section([rrG], tolerance)  # podría dar problemas en interiores sin trasera
                    if not section.Vertexes:
                        cutterList.append(ff)
        print 'cutterList ', cutterList, len(cutterList)

        if cutterList:
            reflex = reflex.cut(cutterList, tolerance)
            print 'reflex.Faces ', reflex.Faces, len(reflex.Faces)

        if not pyR.aligned:
            reflex = reflex.cut(pyR.cutter, tolerance)
            print 'reflex.Faces ', reflex.Faces, len(reflex.Faces)

        aList = []
        for ff in reflex.Faces:
            section = ff.section([gS], tolerance)
            if section.Edges:
                aList.append(ff)
                reflex = reflex.removeShape([ff])
                break
        print 'aList ', aList, len(aList)

        if pyR.rear:

            if not rr.aligned:

                if reflex.Faces:
                    reflex = reflex.cut([pyOppR.enormousShape], tolerance)
                    print 'reflex.Faces ', reflex.Faces, len(reflex.Faces)

                bList = []
                for ff in reflex.Faces:
                    print 'a'
                    section = ff.section(aList, tolerance)
                    if not section.Edges:
                        print 'b'
                        section = ff.section(cutterList, tolerance)
                        if section.Edges:
                            print 'c'
                            section = ff.section(corn, tolerance)
                            if section.Edges:
                                print 'd'
                                bList.append(ff)

                print 'bList ', bList

                if len(bList) > 1:
                    distance = _Py.size
                    ind = 0
                    obj = aList[0]
                    num = -1
                    for ff in bList:
                        num += 1
                        dist = ff.distToShape(obj)[0]
                        if dist < distance:
                            distance = dist
                            ind = num

                    ff = bList[ind]
                    bList = [ff]

                aList.extend(secondaries)
                aList.extend(bList)
                # aList.extend(reflex.Faces)
                print 'aList ', aList

        compound = Part.makeCompound(aList)
        pyR.shape = compound

    def solveReflexTwo(self, pyWire):

        ''''''

        [pyR, pyOppR] = self.planes

        reflex = pyR.shape.copy()
        oppReflex = pyOppR.shape.copy()

        print '### ', (pyR.numGeom, pyOppR.numGeom)
        self.processReflexTwo(reflex, oppReflex, pyR, pyOppR, pyWire, 'forward')

        print '### ', (pyOppR.numGeom, pyR.numGeom)
        self.processReflexTwo(oppReflex, reflex, pyOppR, pyR, pyWire, 'backward')

    def processReflexTwo(self, reflex, oppReflex, pyR, pyOppR, pyWire, direction):

        '''
        
        '''

        gS = pyR.geomShape
        tolerance = _Py.tolerance
        pyPlaneList = pyWire.planes

        if not oppReflex.section([pyOppR.forward, pyOppR.backward], tolerance).Edges:
            print 'A'

            aList = []
            ff = reflex.Faces[0].copy()
            ff = self.cutting(ff, [oppReflex], gS)
            aList.append(ff)
            print 'aList ', aList

            print 'reflex.Faces ', reflex.Faces
            bList = []
            if len(reflex.Faces) > 1:
                print 'two faces'
                ff = reflex.Faces[1]
                bList = [ff]

                if direction == 'forward':
                    print 'rango ', pyR.rango[0]
                    corner = pyR.rango[0]

                else:
                    print 'rango ', pyR.rango[-1]
                    corner = pyR.rango[-1]

                corn = []
                for nn in corner:
                    pyPl = pyPlaneList[nn]
                    if pyPl.aligned:
                        print 'a'
                        pyAlign = self.selectAlignment(pyWire.numWire, nn)
                        pl = pyAlign.simulatedAlignment
                    elif pyPl.choped:
                        print 'aa'
                        pl = pyPl.simulatedShape
                    elif pyPl.reflexed:
                        print 'b'
                        pl = pyPl.shape
                    else:
                        print 'c'
                        pl = pyPl.shape
                    corn.append(pl)
                corn = Part.makeCompound(corn)

                section = ff.section(corn, tolerance)
                print 'section.Edges ', section.Edges
                if not section.Edges:
                    print 'a'
                    bList = []

            aList.extend(bList)
            compound = Part.makeCompound(aList)
            pyR.shape = compound

        else:
            if reflex.section([pyR.forward, pyR.backward], tolerance).Edges:
                print 'B'

                aList = []
                reflex = reflex.cut([oppReflex], tolerance)
                ff = self.selectFace(reflex.Faces, gS)
                aList.append(ff)

                print 'aList ', aList
                print 'reflex.Faces', reflex.Faces

                if direction == 'forward':
                    print 'rango ', pyR.rango[0]
                    corner = pyR.rango[0]

                else:
                    print 'rango ', pyR.rango[-1]
                    corner = pyR.rango[-1]

                corn = []
                for nn in corner:
                    print 'nn', nn
                    pyPl = pyPlaneList[nn]
                    if pyPl.aligned:
                        print 'a'
                        pyAlign = self.selectAlignment(pyWire.numWire, nn)
                        pl = pyAlign.simulatedAlignment
                    elif pyPl.choped:
                        print 'aa'
                        pl = pyPl.simulatedShape
                    elif pyPl.reflexed:
                        print 'b'
                        pl = pyPl.shape
                    else:
                        print 'c'
                        pl = pyPl.shape
                    corn.append(pl)
                corn = Part.makeCompound(corn)

                bList = []
                for ff in reflex.Faces:
                    section = ff.section([gS, pyR.backward], tolerance)
                    if not section.Edges:
                        print 'a'
                        section = ff.section(corn, tolerance)
                        if section.Edges:
                            print 'b'
                            bList = [ff]

                aList.extend(bList)
                compound = Part.makeCompound(aList)
                pyR.shape = compound

            else:
                pass
                print 'C'

    def postProcess(self, pyWire):

        ''''''

        print '### postProcess'

        planeList = self.planes
        tolerance = _Py.tolerance
        reflexList = pyWire.reflexs

        pyOppPlane = planeList[1]
        forwardOpp = pyOppPlane.forward

        for pyPlane in self.planes:
            plane = pyPlane.shape

            if len(plane.Faces) == 1:
                print '# cutted ', pyPlane.numGeom

                forward = pyPlane.forward
                gS = pyPlane.geomShape

                cutterList = []
                for pyReflex in reflexList:
                    if pyReflex != self:
                        for pyPl in pyReflex.planes:
                            if pyPl not in self.planes:
                                print pyPl.numGeom

                                fo = pyPl.forward
                                ba = pyPl.backward
                                pl = pyPl.shape
                                section = pl.section([fo, ba], tolerance)
                                if not section.Edges:
                                    print 'a'
                                    section = fo.section([forward], tolerance)
                                    sect = fo.section([forwardOpp], tolerance)
                                    if section.Vertexes or sect.Vertexes:
                                        print 'b'
                                        cutterList.append(pl)
                                        print '# included cutter ', pyPl.numGeom
                                        pyPlane.control.append(pyPl.numGeom)

                if cutterList:
                    print 'cutterList', cutterList

                    ff = plane.Faces[0]
                    ff = self.cutting(ff, cutterList, gS)
                    compound = Part.Compound([ff])
                    pyPlane.shape = compound

            pyOppPlane = planeList[0]
            forwardOpp = pyOppPlane.forward

    def postProcessTwo(self, pyWire):

        ''''''

        print '### postProcessTwo'

        rangoInter = self.rango
        if not rangoInter:
            return

        tolerance = _Py.tolerance
        pyPlaneList = pyWire.planes
        reflexList = pyWire.reflexs
        refList = self.planes

        pyOppPlane = refList[1]
        oppRear = pyOppPlane.rear[-1]
        rear = refList[0].rear[0]

        for pyPlane in refList:
            plane = pyPlane.shape

            forward = pyPlane.forward

            section = plane.section([forward], tolerance)
            if section.Edges:
                print '# cutted ', pyPlane.numGeom

                pyRearPlane = pyPlaneList[rear]
                rearPl = pyRearPlane.shape
                pyOppRearPlane = pyPlaneList[oppRear]

                # esta cutterList se debe trabajar mejor

                cutterList = [rearPl, pyOppRearPlane.shape]

                for pyReflex in reflexList:
                    for pyPl in pyReflex.planes:
                        if pyPl.numGeom in rangoInter:
                            print pyPl.numGeom

                            pl = pyPl.shape
                            section = pl.section([rearPl], tolerance)

                            if section.Edges:
                                print 'a'
                                cutterList.append(pl)
                                print '# included cutter ', pyPl.numGeom
                                pyPlane.control.append(pyPl.numGeom)

                print 'cutterList', cutterList

                gS = pyPlane.geomShape

                if len(plane.Faces) == 1:

                    plane = self.cutting(plane, cutterList, gS)
                    aList = [plane]

                else:

                    ff = plane.Faces[0]
                    aList = [ff]

                    ff = plane.Faces[1]
                    ff = ff.cut(cutterList, tolerance)
                    for f in ff.Faces:
                        section = f.section([forward], tolerance)
                        if not section.Edges:
                            aList.append(f)
                            break

                compound = Part.Compound(aList)
                pyPlane.shape = compound

            pyOppPlane = refList[0]
            oppRear = pyOppPlane.rear[0]
            rear = refList[1].rear[-1]

    def rearing(self, pyWire, case):

        '''rearing(self, pyWire)
        '''

        direction = "forward"
        for pyPlane in self.planes:
            if not pyPlane.aligned:
                if pyPlane.rear:
                    pyPlane.rearing(pyWire, self, direction, case)
            direction = "backward"

    def rangging(self, pyWire):

        '''rangging(self, pyWire)
        '''

        lenWire = len(pyWire.planes)

        pyR = self.planes[0]
        pyOppR = self.planes[1]
        rear = pyR.rear
        oppRear = pyOppR.rear

        if rear and oppRear:

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

    def rang(self, pyWire, g1, g2, direction):

        ''''''

        # print(g1, g2)

        lenWire = len(pyWire.planes)

        if direction == 'forward':
            # print 'forward'
            if g2 > g1:
                # print 'a'
                ran = range(g1+1, g2)
            else:
                # print 'b'
                ranA = range(g1+1, lenWire)
                ranB = range(0, g2)
                ran = ranA + ranB

        else:
            # print 'backward'
            if g1 > g2:
                # print 'aa'
                ran = range(g2+1, g1)
            else:
                # print 'bb'
                ranB = range(0, g2)
                ranA = range(g1+1, lenWire)
                ran = ranA + ranB

        return ran
