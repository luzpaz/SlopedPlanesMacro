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

    '''The complementary python object class for reflex corners.
    Two consecutives edges of the same wire make a reflex corner
    when the result of the right hand rule is opposed to the base normal.'''

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
        The planes included in a range are cutted between them'''

        # print '### preProcess'

        pyPlaneList = pyWire.planes
        numWire = pyWire.numWire

        rango = self.planes[0].rango[0]

        for pyReflexPlane in self.planes:
            # print '# pyReflexPlane ', pyReflexPlane.numGeom
            # print 'rango ', rango

            pyRan = []
            for nG in rango:
                pyPl = pyPlaneList[nG]
                pyRan.append(pyPl)

            for pyPlane in pyRan:
                cList = []
                if not pyPlane.choped and not pyPlane.aligned:
                    # print 'pyPlane.numGeom ', pyPlane.numGeom

                    control = pyPlane.control
                    ## ???
                    rangoPost = []
                    for ran in pyPlane.rango:
                        rangoPost.extend(ran)
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
                                    self.selectAlignmentBase(numWire, nG)
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
                    pyPlane.cuttingPyth(cList)
                    # print 'plane ', pyPlane.shape

            rango = self.planes[-1].rango[-1]

    def preProcessTwo(self, pyWire):

        '''preProcess(self, pyWire)
        The planes included in a range are cutted by rear and oppRear'''

        # print '### preProcessTwo'

        pyPlaneList = pyWire.planes

        num = -1
        for pyPlane in self.planes:
            num += 1
            # print '# pyPlane ', pyPlane.numGeom

            pyOppPlane = self.planes[num - 1]
            if pyOppPlane.rear and pyPlane.rear:

                rango = []

                if num == 0:
                    rango = pyPlane.rango[0]
                    rear = pyPlane.rear[0]
                    oppRear = pyOppPlane.rear[-1]
                else:
                    rango = pyPlane.rango[-1]
                    rear = pyPlane.rear[-1]
                    oppRear = pyOppPlane.rear[0]

                # print 'rango ', rango
                # print 'oppRear ', oppRear
                # print 'rear ', rear

                pyRearPlane = pyPlaneList[rear]
                if pyRearPlane.reflexed:
                    rearPlane = pyRearPlane.simulatedShape
                else:
                    rearPlane = pyRearPlane.shape

                pyOppRearPlane = pyPlaneList[oppRear]
                if pyOppRearPlane.reflexed:
                    oppRearPlane = pyOppRearPlane.simulatedShape
                else:
                    oppRearPlane = pyOppRearPlane.shape

                for nG in rango:
                    # print '# nG ', nG
                    pyPl = pyPlaneList[nG]
                    if not pyPl.reflexed:
                        # print 'a'
                        control = pyPl.control
                        cList = []
                        if oppRear not in control:
                            cList.append(oppRearPlane)
                            if not pyOppRearPlane.reflexed:
                                control.append(oppRear)
                        if rear not in control:
                            cList.append(rearPlane)
                            if not pyRearPlane.reflexed:
                                control.append(rear)
                        if cList:
                            pyPl.cuttingPyth(cList)

    def reflexing(self, pyWire):

        '''reflexing(self, pyWire)
        '''

        [pyR, pyOppR] = self.planes

        # print '### direction ', 'forward', (pyR.numGeom, pyOppR.numGeom)
        self.twin(pyWire, pyR, pyOppR, 'forward')

        # print '### direction ', 'backward', (pyOppR.numGeom, pyR.numGeom)
        self.twin(pyWire, pyOppR, pyR, 'backward')

    def twin(self, pyWire, pyR, pyOppR, direction):

        '''twin(self, pyWire, pyR, pyOppR, direction)
        '''

        pyPlaneList = pyWire.planes
        numWire = pyWire.numWire
        control = pyR.control
        rear = pyR.rear

        rangoCorner = []
        rangoNext = []

        if pyR.rear:

            if direction == 'forward':
                nGeom = rear[0]
                rangoCorner = pyR.rango[0]
            else:
                nGeom = rear[-1]
                rangoCorner = pyR.rango[-1]

            if nGeom not in control:

                rearPyPl = pyPlaneList[nGeom]

                if rearPyPl.aligned:
                    # print 'a'
                    pyAlign = self.selectAlignment(numWire, nGeom)
                    rearPl = pyAlign.simulatedAlignment
                    pyR.addLink('cutter', rearPl)
                    # print 'included rear simulated ', (numWire, nGeom)

                elif rearPyPl.choped:
                    # print 'b'
                    rearPl = rearPyPl.simulatedShape
                    pyR.addLink('cutter', rearPl)
                    # print 'included rear simulated ', (numWire, nGeom)

                elif rearPyPl.reflexed:
                    # print 'c'
                    rearPl = rearPyPl.simulatedShape
                    pyR.addLink('cutter', rearPl)
                    # print 'included rear simulated ', (numWire, nGeom)

                else:
                    # print 'd'
                    rearPl = rearPyPl.shape
                    pyR.addLink('cutter', rearPl)
                    control.append(nGeom)
                    # print 'included rear ', (numWire, nGeom)

        oppRear = pyOppR.rear

        if oppRear:

            if direction == 'forward':
                rangoNext = pyOppR.rango[-1]
            else:
                rangoNext = pyOppR.rango[0]

            if len(oppRear) == 1:

                nGeom = oppRear[0]
                if nGeom not in control:
                    pyOppRear = pyPlaneList[nGeom]

                    if pyOppRear.aligned:
                        # print 'a'
                        pyAlign = self.selectAlignment(numWire, nGeom)
                        oppRearPl = pyAlign.simulatedAlignment
                        pyR.addLink('cutter', oppRearPl)
                        # print 'included oppRear simulated ', (numWire, nGeom)

                    elif pyOppRear.choped:
                        # print 'b'
                        oppRearPl = pyOppRear.simulatedShape
                        pyR.addLink('cutter', oppRearPl)
                        # print 'included oppRear simulated ', (numWire, nGeom)

                    elif pyOppRear.reflexed:
                        # print 'c'
                        oppRearPl = pyOppRear.simulatedShape
                        pyR.addLink('cutter', oppRearPl)
                        # print 'included oppRear simulated ', (numWire, nGeom)

                    else:
                        # print 'd'
                        oppRearPl = pyOppRear.shape
                        pyR.addLink('cutter', oppRearPl)
                        control.append(nGeom)
                        # print 'included oppRear ', (numWire, nGeom)

            else:

                self.processOppRear(oppRear, direction, pyWire, pyR, pyOppR)

        # print 'rangoCorner ', rangoCorner
        for nn in rangoCorner:
            if nn not in control:
                if nn not in oppRear:
                    self.processRango(pyWire, pyR, pyOppR, nn,
                                      'rangoCorner', direction)

        # print 'rangoNext ', rangoNext
        if len(rear) == 1:
            for nn in rangoNext:
                if nn not in control:
                    if nn not in oppRear:
                        self.processRango(pyWire, pyR, pyOppR, nn,
                                          'rangoNext', direction)

        rangoInter = self.rango
        # print 'rangoInter ', rangoInter
        for nn in rangoInter:
            if nn not in control:
                self.processRango(pyWire, pyR, pyOppR, nn,
                                  'rangoInter', direction)

    def processOppRear(self, oppRear, direction, pyWire, pyR, pyOppR):

        '''processOppRear(self, oppRear, direction, pyWire, pyR, pyOppR)'''

        pyPlaneList = pyWire.planes
        tolerance = _Py.tolerance
        control = pyR.control
        oppReflexEnormous = pyOppR.enormousShape

        if direction == "forward":
            nGeom = oppRear[1]
        else:
            nGeom = oppRear[0]

        if nGeom not in control:
            pyOppRear = pyPlaneList[nGeom]

            oppRearPl = pyOppRear.shape.copy()
            pyR.addLink('cutter', oppRearPl)
            control.append(nGeom)
            # print 'included oppRear ', (pyWire.numWire, nGeom)

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
                point = pointWire[nGeom + 1]
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

        '''processRango(self, pyWire, pyR, pyOppR, nn, kind, direction)'''

        tolerance = _Py.tolerance
        numWire = pyWire.numWire
        pyPlaneList = pyWire.planes
        numGeom = pyR.numGeom
        oppReflexEnormous = pyOppR.enormousShape

        pyPl = pyPlaneList[nn]
        gS = pyPl.geomShape

        if pyPl.aligned:
            # print 'A'
            pyAlign = self.selectAlignment(numWire, nn)
            pl = pyAlign.simulatedAlignment
            pyR.addLink('cutter', pl)
            # print 'included rango simulated ', (numWire, nn)

        elif pyPl.choped:
            # print 'B'
            pl = pyPl.simulatedShape
            pyR.addLink('cutter', pl)
            # print 'included rango simulated ', (numWire, nn)

        elif pyPl.reflexed:
            # print 'C'
            pl = pyPl.simulatedShape.copy()

            rear = pyPl.rear

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
                # print 'included rango ', (numWire, nn)

                pl = pyPl.simulatedShape.copy()     # Two faces included
                if kind == 'rangoCorner':
                    # print '22'
                    pl = self.cutting(pl, [oppReflexEnormous], gS)

            elif kind == 'rangoCorner':
                # print '3'

                forward = pyR.forward
                fo = pyPl.forward
                # ba = pyPl.backward ???

                if direction == 'forward':
                    forward = pyR.forward
                else:
                    if len(pyR.rear) == 1:
                        forward = pyR.forward
                    else:
                        forward = pyR.backward

                # if forward.section([fo, ba], tolerance).Vertexes: ???
                if forward.section([fo], tolerance).Vertexes:
                    # print '32'
                    pl = self.cutting(pl, [oppReflexEnormous], gS)

                else:
                    # print '33'
                    pl = pyPl.shape.copy()
                    rang = self.rang(pyWire, numGeom, nn, direction)
                    # print 'rang ', rang
                    cList = []
                    for mm in rang:
                        pyP = pyPlaneList[mm]
                        if pyP.reflexed:
                            section =\
                                forward.section([pyP.forward, pyP.backward],
                                                tolerance)
                            if section.Vertexes:
                                cList.append(pyP.enormousShape)
                    if cList:
                        # print 'cList ', cList
                        pl = self.cutting(pl, cList, gS)

            else:   # rangoNext, rangoInter
                # print '4'
                pass

            pyR.addLink('cutter', pl)
            # print 'included rango simulated ', (numWire, nn)

        else:
            # print 'D'
            pl = pyPl.shape.copy()

            if kind == 'rangoCorner':
                # print 'D1'
                pl = self.cutting(pl, [oppReflexEnormous], gS)

            pyR.addLink('cutter', pl)
            pyR.control.append(nn)
            # print 'included rango ', (numWire, nn)

    def solveReflex(self, pyWire):

        '''solveReflex(self, pyWire)
        '''

        # print '### solveReflexs'

        [pyR, pyOppR] = self.planes

        reflex = pyR.shape.copy()
        oppReflex = pyOppR.shape.copy()

        # print '# ', (pyR.numGeom, pyOppR.numGeom)
        self.processReflex(reflex, oppReflex, pyR, pyOppR, 'forward', pyWire)

        # print '# ', (pyOppR.numGeom, pyR.numGeom)
        self.processReflex(oppReflex, reflex, pyOppR, pyR, 'backward', pyWire)

    def processReflex(self, reflex, oppReflex, pyR, pyOppR,
                      direction, pyWire):

        '''processReflex(self, reflex, oppReflex, pyR, pyOppR,
                         direction, pyWire)
        '''

        tolerance = _Py.tolerance
        pyPlaneList = pyWire.planes
        gS = pyR.geomShape
        simul = pyR.simulatedShape
        face = _Py.face
        reflexList = pyWire.reflexs

        cutList = [pyOppR.enormousShape]

        # the planes with two rears could drag extra faces
        if isinstance(reflex, Part.Compound):
            # print '0'
            secondaries = reflex.Faces[1:]
        else:
            # print '1'
            secondaries = []
            if not pyR.aligned:
                # print '11'
                cutList.extend(pyR.cutter)

        # print 'cutList ', cutList

        enorm = []    # auxiliar to clean the figure bottom
        rangoCorner = None
        rear = pyR.rear
        oppRear = pyOppR.rear
        if rear:

            if direction == 'forward':
                rr = pyPlaneList[rear[0]]
                if oppRear:
                    oppRr = pyPlaneList[oppRear[-1]]
                rangoCorner = pyR.rango[0]
                forward = pyR.forward
                backward = pyR.backward

            else:
                rr = pyPlaneList[rear[-1]]
                if oppRear:
                    oppRr = pyPlaneList[oppRear[0]]
                rangoCorner = pyR.rango[-1]
                if len(rear) == 1:
                    forward = pyR.forward
                    backward = pyR.backward
                else:
                    forward = pyR.backward
                    backward = pyR.forward

            # print 'rear ', rr.numGeom
            # print 'rangoCorner ', rangoCorner
            rrG = rr.geomShape

            forw = forward.copy()
            forw = forw.cut([rrG], tolerance)
            wire = Part.Wire(forw.Edges)
            orderedEdges = wire.OrderedEdges
            forw = orderedEdges[0]

            enormous = [rr.shape]    # auxiliar to build the allowed location to extra faces
            if oppRear:
                enormous.append(oppRr.shape)

            corn = []    # auxiliar to look for extra faces
            for nn in rangoCorner:
                # print 'rangoCorner nn ', nn
                pyPl = pyPlaneList[nn]
                if pyPl.aligned:
                    # print 'a'
                    pyAlign = self.selectAlignment(pyWire.numWire, nn)
                    pl = pyAlign.simulatedAlignment
                    corn.append(pl)
                elif pyPl.reflexed:
                    # print 'b'
                    pl = pyPl.simulatedShape
                    line = pyPl.forward
                    section = forw.section([line], tolerance)
                    if section.Vertexes:
                        # print 'b1'
                        enormous.append(pyPl.enormousShape)
                    else:
                        # print 'b2'
                        corn.append(pl)
                else:
                    # print 'c'
                    pl = pyPl.shape
                    corn.append(pl)
            corn = Part.makeCompound(corn)
            # print 'corn ', corn
            # print 'enormous ', enormous

            for pyReflex in reflexList:
                if pyReflex != self:
                    for pyPl in pyReflex.planes:
                        if pyPl not in [pyR, pyOppR]:
                            section = forw.section([pyPl.forward], tolerance)
                            if section.Vertexes:
                                section = pyPl.forward.section([gS], tolerance)
                                if not section.Vertexes:
                                    # print 'enorm ', pyPl.numGeom
                                    enorm.append(pyPl.enormousShape)
            # print 'enorm ', enorm

        aa = reflex.copy()
        if enorm:
            cutList.extend(enorm)
        aa = aa.cut(cutList, tolerance)
        # print 'aa.Faces ', aa.Faces, len(aa.Faces)

        cutterList = []    # surplus figure's bottom
        for ff in aa.Faces:
            section = ff.section([gS], tolerance)
            if not section.Edges:
                section = ff.section([face], tolerance)
                if section.Edges:
                    cutterList.append(ff)
                elif section.Vertexes:
                    section = ff.section([rrG], tolerance)
                    if not section.Vertexes:
                        cutterList.append(ff)
        # print 'cutterList ', cutterList, len(cutterList)

        if rear:

            cList = []    # clean cutterList
            for f in cutterList:
                section = f.section([backward], tolerance)
                if not section.Edges:
                    cList.append(f)
            pyR.under.extend(cList)    # surplus figure's bottom
            # print 'cList ', cList, len(cList)
            cutterList = Part.makeCompound(pyR.under)

        if cList:
            reflex = reflex.cut(cList, tolerance)
            # print 'reflex.Faces ', reflex.Faces, len(reflex.Faces)

        if not pyR.aligned and pyR.cutter:
            reflex = reflex.cut(pyR.cutter, tolerance)
            # print 'reflex.Faces ', reflex.Faces, len(reflex.Faces)

        # main face
        aList = []
        for ff in reflex.Faces:
            section = ff.section([gS], tolerance)
            if section.Edges:
                aList.append(ff)
                reflex = reflex.removeShape([ff])
                break
        # print 'aList ', aList, len(aList)

        # second face
        if rangoCorner:

            if not rr.aligned:

                if reflex.Faces:
                    reflex = reflex.cut([pyOppR.enormousShape], tolerance)
                    # print 'reflex.Faces ', reflex.Faces, len(reflex.Faces)

                if enormous:

                    seedList = pyR.seed
                    # print 'seedList ', seedList
                    if not seedList:
                        # print 'a'
                        seed = pyR.seedShape.copy()
                    else:
                        # print 'b'
                        seed = Part.makeShell(seedList)
                        seedList = []
                    seed = seed.cut(enormous, tolerance)
                    ff = self.selectFace(seed.Faces, gS)
                    seed = seed.removeShape([ff])
                    seedList.append(ff)
                    for ff in seed.Faces:
                        # print '1'
                        section = ff.section([face], tolerance)
                        if section.Edges:
                            # print '2'
                            section = ff.section(seedList, tolerance)
                            if not section.Edges:
                                # print '3'
                                seedList.append(ff)
                    # print 'seedList ', seedList
                    pyR.seed = seedList    # allowed location for extra faces
                    seed = Part.makeShell(seedList)

                bList = []
                for ff in reflex.Faces:
                    # print 'a'
                    section = ff.section(cutterList, tolerance)
                    if section.Edges:
                        # print 'b'
                        section = ff.section([simul], tolerance)
                        if not section.Edges:
                            # print 'c'
                            section = ff.section(aList, tolerance)
                            if not section.Edges:
                                # print 'd'
                                section = ff.section(corn, tolerance)
                                if section.Edges:
                                    # print 'e'

                                    section = ff.section([forward, backward],
                                                         tolerance)

                                    if section.Edges:
                                        # print 'e1'
                                        section = ff.section(aList, tolerance)
                                        if len(section.Vertexes) == 1:
                                            # print 'e11'
                                            if enormous:
                                                # print 'e111'
                                                common =\
                                                    ff.common([seed], tolerance)
                                                if common.Area:
                                                    # print 'e1111'
                                                    bList.append(ff)
                                            else:
                                                # print 'e12'
                                                bList.append(ff)

                                    else:
                                        # print 'e2'
                                        if enormous:
                                            # print 'e21'
                                            common =\
                                                ff.common([seed], tolerance)
                                            if common.Area:
                                                # print 'e211'
                                                bList.append(ff)
                                        else:
                                            # print 'e22'
                                            bList.append(ff)

                # print 'bList ', bList

                aList.extend(secondaries)
                aList.extend(bList)

        # print 'aList ', aList
        compound = Part.makeCompound(aList)
        pyR.shape = compound

    def solveReflexTwo(self, pyWire):

        '''solveReflexTwo(self, pyWire)'''

        [pyR, pyOppR] = self.planes

        reflex = pyR.shape.copy()
        oppReflex = pyOppR.shape.copy()

        # print '### ', (pyR.numGeom, pyOppR.numGeom)
        self.processReflexTwo(reflex, oppReflex, pyR, pyOppR, 'forward')

        # print '### ', (pyOppR.numGeom, pyR.numGeom)
        self.processReflexTwo(oppReflex, reflex, pyOppR, pyR, 'backward')

    def processReflexTwo(self, reflex, oppReflex, pyR, pyOppR, direction):

        '''
        processReflexTwo(self, reflex, oppReflex, pyR, pyOppR, direction)
        '''

        tolerance = _Py.tolerance
        gS = pyR.geomShape
        forward = pyR.forward
        backward = pyR.backward

        if pyOppR.isSolved():
            # print 'A'

            aList = []
            ff = reflex.Faces[0].copy()
            ff = self.cutting(ff, [oppReflex], gS)
            aList.append(ff)
            # print 'aList ', aList

            bList = []
            if len(reflex.Faces) > 1:
                ff = reflex.Faces[1]
                section = ff.section([forward], tolerance)
                if section.Edges:
                    section = ff.section(aList, tolerance)
                    if section.Vertexes:
                        bList = [ff]
                else:
                    bList = [ff]

            aList.extend(bList)
            compound = Part.makeCompound(aList)
            pyR.shape = compound
            pyR.control.append(pyOppR.numGeom)

        else:

            if not pyR.isSolved():
                # print 'B'

                aList = []
                reflex = reflex.cut([oppReflex], tolerance)
                ff = self.selectFace(reflex.Faces, gS)
                aList.append(ff)
                # print 'aList ', aList

                bList = []
                if pyR.rear:

                    for ff in reflex.Faces:
                        section = ff.section([gS, backward], tolerance)
                        if not section.Edges:
                            bList = [ff]
                            break

                aList.extend(bList)
                compound = Part.makeCompound(aList)
                pyR.shape = compound
                pyR.control.append(pyOppR.numGeom)

            else:
                # print 'C'

                pass

        # print pyR.shape.Faces, len(pyR.shape.Faces)

        if direction == 'backward':
            if pyR.numGeom not in pyOppR.control:
                # print 'D'

                oppReflex = pyOppR.shape
                reflex = pyR.shape
                self.processReflexTwo(oppReflex, reflex, pyOppR, pyR,
                                      'forward')

    def postProcess(self, pyWire):

        ''''''

        # print '### postProcess'

        refList = self.planes
        # print 'refList ', refList
        tolerance = _Py.tolerance
        reflexList = pyWire.reflexs
        # print 'reflexList ', reflexList

        pyOppPlane = refList[1]
        forwardOpp = pyOppPlane.forward

        for pyPlane in refList:
            plane = pyPlane.shape

            if len(plane.Faces) == 1:
                # print '# cutted ', pyPlane.numGeom

                forward = pyPlane.forward
                gS = pyPlane.geomShape

                cutterList = []
                for pyReflex in reflexList:
                    if pyReflex != self:
                        for pyPl in pyReflex.planes:
                            if pyPl not in refList:
                                # print 'reflexed plane ', pyPl.numGeom

                                if pyPl.isSolved():
                                    # print 'a'
                                    fo = pyPl.forward
                                    section = fo.section([forward], tolerance)
                                    sect = fo.section([forwardOpp], tolerance)
                                    se = fo.section([gS], tolerance)
                                    if section.Vertexes or\
                                       sect.Vertexes or\
                                       se.Vertexes:
                                        # print 'b'
                                        pl = pyPl.shape
                                        cutterList.append(pl)
                                        pyPlane.control.append(pyPl.numGeom)
                                        # print '# included cutter ', pyPl.numGeom

                if cutterList:
                    # print 'cutterList', cutterList

                    ff = plane.Faces[0]
                    ff = self.cutting(ff, cutterList, gS)
                    compound = Part.Compound([ff])
                    pyPlane.shape = compound

            pyOppPlane = refList[0]
            forwardOpp = pyOppPlane.forward

    def postProcessTwo(self, pyWire):

        ''''''

        # print '### postProcessTwo'

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
                # print '# cutted ', pyPlane.numGeom

                pyRearPlane = pyPlaneList[rear]
                rearPl = pyRearPlane.shape
                pyOppRearPlane = pyPlaneList[oppRear]
                oppRearPl = pyOppRearPlane.shape

                # esta cutterList se debe trabajar mejor

                cutterList = [rearPl, oppRearPl]

                for pyReflex in reflexList:
                    for pyPl in pyReflex.planes:
                        if pyPl.numGeom in rangoInter:
                            # print pyPl.numGeom

                            pl = pyPl.shape
                            section = pl.section([rearPl], tolerance)

                            if section.Edges:
                                # print 'a'
                                cutterList.append(pl)
                                pyPlane.control.append(pyPl.numGeom)
                                # print '# included cutter ', pyPl.numGeom

                # print 'cutterList', cutterList

                gS = pyPlane.geomShape

                if len(plane.Faces) == 1:
                    # print 'A'

                    plane = self.cutting(plane, cutterList, gS)
                    aList = [plane]

                else:
                    # print 'B'

                    ff = plane.Faces[0]
                    ff = self.cutting(ff, cutterList, gS)
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

        pyR = self.planes[0]
        pyOppR = self.planes[1]
        rear = pyR.rear
        oppRear = pyOppR.rear

        if rear and oppRear:

            rG = rear[0]
            oG = oppRear[-1]
            ran = self.rang(pyWire, rG, oG, 'forward')
            self.rango = ran

        direction = "forward"
        for pyPlane in self.planes:
            if not pyPlane.rango:
                pyPlane.rangging(pyWire, direction)
            direction = "backward"
