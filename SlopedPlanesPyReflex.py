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

        self.twin(pyWire, pyR, pyOppR, direction)

        direction = "backward"
        # print '### direction ', direction
        # print(pyOppR.numGeom, pyR.numGeom)

        self.twin(pyWire, pyOppR, pyR, direction)

    def twin(self, pyWire, pyR, pyOppR, direction):

        '''twin(self, pyWire, pyR, pyOppR, direction)
        '''

        print '# twin pyR.numGeom ', pyR.numGeom, pyR.control

        # reflexEnormous = pyR.enormousShape
        oppReflexEnormous = pyOppR.enormousShape
        pyR.addValue('oppCutter', oppReflexEnormous, 'forward')
        ### OJO para los metodos TWO
        pyR.addValue('cutter', oppReflexEnormous, 'forward')

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
                    pyR.addLink('oppCutter', oppRearPl)
                    pyR.addLink('cutter', oppRearPl)
                    print 'included oppRear simulated', (rearPl, numWire, nGeom)

                elif pyOppRear.choped:
                    print 'b'
                    oppRearPl = pyOppRear.simulatedShape
                    pyR.addLink('cutter', oppRearPl)
                    pyR.addLink('oppCutter', oppRearPl)
                    print 'included oppRear simulated', (oppRearPl, numWire, nGeom)

                elif pyOppRear.reflexed:
                    print 'c'
                    oppRearPl = pyOppRear.simulatedShape
                    pyR.addLink('cutter', oppRearPl)
                    pyR.addLink('oppCutter', oppRearPl)
                    print 'included oppRear simulated ', (oppRearPl, numWire, nGeom)

                else:
                    print 'd'
                    oppRearPl = pyOppRear.shape.copy()
                    pyR.addLink('cutter', oppRearPl)
                    pyR.addLink('oppCutter', oppRearPl)
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

                    # self.processRango(pyWire, pyR, pyOppR, nn, 'rangoCorner')
                    self.processRangoTwo(pyWire, pyR, pyOppR, nn, 'rangoCorner')

        rangoNext = pyOppR.rangoConsolidate
        print 'rangoNext ', rangoNext

        if len(rear) == 1:
            for nn in rangoNext:
                if nn not in control:

                    # self.processRango(pyWire, pyR, pyOppR, nn, 'rangoNext')
                    self.processRangoTwo(pyWire, pyR, pyOppR, nn, 'rangoNext')

        rangoInter = self.rango
        print 'rangoInter ', rangoInter

        for nn in rangoInter:
            if nn not in control:

                # self.processRango(pyWire, pyR, pyOppR, nn,  'rangoInter')
                self.processRangoTwo(pyWire, pyR, pyOppR, nn,  'rangoInter')

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
            pyR.addLink('oppCutter', oppRearPl)
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
                    pyR.addLink('oppCutter', ff)
                    print 'included oppRear rectified ', (oppRearPl, nWire, nGeom)
                    break

    def processRangoTwo(self, pyWire, pyR, pyOppR, nn, kind):

        ''''''

        numWire = pyWire.numWire
        pyPl = pyWire.planes[nn]

        oppReflexEnormous = pyOppR.enormousShape

        if pyPl.aligned:
            print 'A'
            pyAlign = self.selectAlignment(numWire, nn)
            pl = pyAlign.simulatedAlignment
            pyR.addLink('cutter', pl)
            if kind == 'rangoNext':
                pyR.addLink('oppCutter', pl)
            print 'included rango simulated ', (pl, numWire, nn)

        elif pyPl.choped:
            print 'B'
            pl = pyPl.simulatedShape
            pyR.addLink('cutter', pl)
            if kind == 'rangoNext':
                pyR.addLink('oppCutter', pl)
            print 'included rango simulated', (pl, numWire, nn)

        elif pyPl.reflexed:
            print 'C'


            '''pyReflexList = self.selectAllReflex(numWire, nn)
            

            oppReflexEnormous = pyOppR.enormousShape
            reflexEnormous = pyR.enormousShape

            rear = pyPl.rear
            rRear = pyR.rear
            oppRRear = pyOppR.rear

            forward = pyR.forward
            backward = pyR.backward
            forwa = pyOppR.forward
            backwa = pyOppR.backward
            fo = pyPl.forward
            ba = pyPl.backward

            if pyR.numGeom in rear:
                pass
            elif pyOppR.numGeom in rear:
                pass

            if fo.section([forward], _Py.tolerance).Vertexes:
                pass
            if fo.section([forwa], _Py.tolerance).Vertexes:
                pass

            if len(rRear) > 1:
                if fo.section([backward], _Py.tolerance).Vertexes:
                    pass
            if len(oppRRear) > 1:
                if fo.section([backwa], _Py.tolerance).Vertexes:
                    pass
            if len(rear) > 1:
                if ba.section([forward], _Py.tolerance).Vertexes:
                    pass
                if ba.section([forwa], _Py.tolerance).Vertexes:
                    pass'''

        else:
            print 'D'
            pl = pyPl.shape.copy()

            if kind == 'rangoCorner':
                print 'D1'
                gS = pyPl.geomShape
                pl = self.cutting(pl, [oppReflexEnormous], gS)

            pyR.addLink('cutter', pl)
            if kind == 'rangoNext':
                pyR.addLink('oppCutter', pl)
            print 'included rango ', (pl, numWire, nn)

    def processRango(self, pyWire, pyR, pyOppR, nn, kind):

        '''processRango(self, pyWire, pyR, pyOppR, nn, kind)
        '''

        nWire = pyWire.numWire
        oppReflexEnormous = pyOppR.enormousShape
        reflexEnormous = pyR.enormousShape
        pyPl = pyWire.planes[nn]

        if pyPl.aligned:
            print 'A'
            pyAlign = self.selectAlignment(nWire, nn)
            pl = pyAlign.simulatedAlignment
            pyR.addLink('cutter', pl)
            if kind == 'rangoNext':
                pyR.addLink('oppCutter', pl)
            print 'included rango simulated ', (pl, nWire, nn)

        elif pyPl.choped:
            print 'B'
            pl = pyPl.simulatedShape
            pyR.addLink('cutter', pl)
            if kind == 'rangoNext':
                pyR.addLink('oppCutter', pl)
            print 'included rango simulated', (pl, nWire, nn)

        elif pyPl.reflexed:
            print 'C'

            pl = pyPl.simulatedShape
            gS = pyPl.geomShape
            forwar = pyR.forward
            forw = pyPl.forward
            fo = pyOppR.forward

            section = forwar.section([forw], _Py.tolerance)
            sect = fo.section([forw], _Py.tolerance)
            se = pyPl.geomShape.section([pyR.geomShape], _Py.tolerance)

            if section.Vertexes:
                print 'section vertexes'
                pl = self.cutting(pl, [reflexEnormous], gS)

            elif sect.Vertexes:
                print 'sect vertexes'
                # pl = pyPl.shape.copy()    # uhm!
                pl = self.cutting(pl, [reflexEnormous], gS)

            elif se.Vertexes:
                print 'se vertexes'
                pl = self.cutting(pl, [oppReflexEnormous], gS)

            if kind == 'rangoCorner':
                print 'C1'

                pl = self.cutting(pl, [oppReflexEnormous], gS)
                pyR.addLink('cutter', pl)
                print 'included rango modified', (pl, nWire, nn)

            elif kind == 'rangoNext':
                print 'C2'

                pyR.addLink('cutter', pl)
                pyR.addLink('oppCutter', pl)
                print 'included rango simulated ', (pl, nWire, nn)

            else:   # rangoInter
                print 'C3'

                if pyOppR.numGeom in pyPl.rear:
                    print 'C31'
                    pl = pyPl.shape.copy()
                    gS = pyPl.geomShape
                    pl = self.cutting(pl, [oppReflexEnormous], gS)
                    pyOppR.addValue('oppCutter', pl, 'backward')
                    pyR.addLink('cutter', pl)

                pl = pyPl.simulatedShape
                pyR.addLink('cutter', pl)
                print 'included rango simulated ', (pl, nWire, nn)

        else:
            print 'D'
            pl = pyPl.shape.copy()

            if kind == 'rangoCorner':
                print 'D1'
                gS = pyPl.geomShape
                pl = self.cutting(pl, [oppReflexEnormous], gS)

            pyR.addLink('cutter', pl)
            if kind == 'rangoNext':
                pyR.addLink('oppCutter', pl)
            print 'included rango ', (pl, nWire, nn)

    def solveReflex(self):

        '''solveReflex(self)
        '''

        print '### solveReflexs'

        [pyR, pyOppR] = self.planes


        self.planes = [pyR, pyOppR]

        reflex = pyR.shape.copy()
        oppReflex = pyOppR.shape.copy()

        print(pyR.numGeom, pyOppR.numGeom)
        ### OJO 
        self.processReflexTwo(reflex, oppReflex,
                              pyR, pyOppR,
                              'forward')
        '''self.processReflex(reflex, oppReflex,
                           pyR, pyOppR,
                           'forward')'''
        print(pyOppR.numGeom, pyR.numGeom)
        ### OJO
        self.processReflexTwo(oppReflex, reflex,
                              pyOppR, pyR,
                              'backward')
        '''self.processReflex(oppReflex, reflex,
                           pyOppR, pyR,
                           'backward')'''

    def processReflexTwo(self, reflex, oppReflex, pyR, pyOppR,
                      direction):

        '''processReflex(self, reflex, oppReflex, pyR, pyOppR,
                         direction)
        '''

        numWire = pyR.numWire
        aa = reflex.copy()
        bb = oppReflex.copy()

        print pyR.cutter
        print[p.Area for p in pyR.cutter]

        aa = aa.cut(pyR.cutter, _Py.tolerance)
        print aa.Faces
        gS = pyR.geomShape

        cutterList = []
        for ff in aa.Faces:
            section = ff.section([gS], _Py.tolerance)
            if not section.Edges:
                sect = ff.section([_Py.face], _Py.tolerance)
                if sect.Vertexes:
                    cutterList.append(ff)

        reflex = reflex.cut(cutterList, _Py.tolerance)

        if len(pyOppR.rear) == 1:
            numOppRear = pyOppR.rear[0]
        else:
            if direction == 'forward':
                numOppRear = pyOppR.rear[1]
            else:
                numOppRear = pyOppR.rear[0]
        pyOppRear = self.selectPlane(numWire, numOppRear)
        oppRear = pyOppRear.shape

        aList = []
        for ff in reflex.Faces:
            section = ff.section([oppRear], _Py.tolerance)
            if section.Edges:
                reflex = reflex.removeShape([ff])
            else:
                section = ff.section([gS], _Py.tolerance)
                if section.Edges:
                    aList.insert(0, ff)
                else:
                    aList.append(ff)

        compound = Part.makeCompound(aList)
        pyR.shape = compound

    def processReflex(self, reflex, oppReflex, pyR, pyOppR,
                      direction):

        '''processReflex(self, reflex, oppReflex, pyR, pyOppR,
                         direction)
        '''

        numWire = pyR.numWire
        aa = reflex.copy()
        bb = oppReflex.copy()

        bb = bb.cut(pyOppR.oppCutter, _Py.tolerance)
        print 'bb.Faces ', bb.Faces
        gS = pyOppR.geomShape

        bList = []
        for ff in bb.Faces:
            section = ff.section([gS], _Py.tolerance)
            if section.Edges:
                bList.append(ff)
        print 'bList ', bList

        cList = pyR.cutter
        if pyR.aligned:
            cList = []

        cList.extend(bList)      # me esta ampliando la propiedad sin hacer pyR.cutter = cList

        aa = aa.cut(cList, _Py.tolerance)

        print 'aa.Faces ', aa.Faces

        aList = []
        gS = pyR.geomShape
        AA = self.selectFace(aa.Faces, gS)
        aList.append(AA)
        aa = aa.removeShape([AA])

        forward = pyR.forward
        backward = pyR.backward

        numRear = pyR.rear[0]
        pyRear = self.selectPlane(numWire, numRear)
        rear = pyRear.shape

        if len(pyOppR.rear) == 1:
            numOppRear = pyOppR.rear[0]
        else:
            if direction == 'forward':
                numOppRear = pyOppR.rear[1]
            else:
                numOppRear = pyOppR.rear[0]
        pyOppRear = self.selectPlane(numWire, numOppRear)
        oppRear = pyOppRear.shape

        if aa.Faces:

            oppReflexEnormous = pyOppR.enormousShape
            aa = aa.cut([oppReflexEnormous], _Py.tolerance)

            under = []
            for ff in aa.Faces:
                print 'aa'
                section = ff.section([_Py.face], _Py.tolerance)
                # if section.Edges_
                if section.Vertexes:
                    print 'bb'
                    section = ff.section([rear], _Py.tolerance)
                    if section.Edges:
                        print 'cc'
                        aa = aa.removeShape([ff])
                        under.append(ff)

            print 'under ', under

            if under:

                try:
                    numFirstRangoCorner = pyR.rangoConsolidate[0]
                except IndexError:
                    pass
                else:
                    pyFirstRangoCorner =\
                        self.selectPlane(numWire, numFirstRangoCorner)
                    fRC = pyFirstRangoCorner.shape

                    for ff in aa.Faces:
                        print 'a'
                        section = ff.section([_Py.face], _Py.tolerance)
                        if not section.Vertexes:
                            print 'b'
                            section = ff.section(under, _Py.tolerance)
                            if section.Edges:
                                print 'c'
                                section = ff.section([AA], _Py.tolerance)
                                if not section.Edges:
                                    print 'd'
                                    section = ff.section([forward, backward],
                                                         _Py.tolerance)     # creo que puedo quitar forward ya que antes comprobe con _Py.face
                                    if not section.Edges:
                                        print 'e'
                                        section = ff.section([rear],
                                                             _Py.tolerance)
                                        if section.Edges:
                                            print 'f'
                                            section = ff.section([oppRear],
                                                                 _Py.tolerance)
                                            if not section.Edges:
                                                print 'g'  # llevar al primero?
                                                # ampliar rango
                                                section =\
                                                    ff.section([fRC],
                                                               _Py.tolerance)
                                                if section.Vertexes:
                                                    print 'h'
                                                    aList.append(ff)
                                                    break

        # aList = aa.Faces

        compound = Part.makeCompound(aList)
        pyR.shape = compound

    def reviewing(self):

        '''reviewing(self)
        '''

        print '###### reviewing'

        for pyPlane in self.planes:
            pyPlane.isUnsolved()

        [pyR, pyOppR] = self.planes
        print[pyR.numGeom, pyOppR.numGeom]

        if 'forward' in pyR.unsolved and 'forward' in pyOppR.unsolved:
            print 'twice'

            reflex = pyR.shape
            oppReflex = pyOppR.shape

            reflex = reflex.cut([oppReflex], _Py.tolerance)
            gS = pyR.geomShape
            aList = []
            AA = self.selectFace(reflex.Faces, gS)
            aList.append(AA)
            reflex = reflex.removeShape([AA])

            #if reflex.Faces:
            for ff in reflex.Faces:
                section = ff.section([_Py.face], _Py.tolerance)
                if section.Edges:
                    reflex = reflex.removeShape([ff])

            if reflex.Faces:
                aList.extend(reflex.Faces)

            reflex = Part.makeCompound(aList)
            pyR.shape = reflex

            oppReflex = oppReflex.cut([reflex], _Py.tolerance)
            gS = pyOppR.geomShape
            aList = []
            AA = self.selectFace(oppReflex.Faces, gS)
            aList.append(AA)
            oppReflex = oppReflex.removeShape([AA])

            #if oppReflex.Faces:
            for ff in oppReflex.Faces:
                section = ff.section([_Py.face], _Py.tolerance)
                if section.Edges:
                    oppReflex = oppReflex.removeShape([ff])

            if oppReflex.Faces:
                aList.extend(oppReflex.Faces)

            oppReflex = Part.makeCompound(aList)
            pyOppR.shape = oppReflex

    def rearReflex(self, pyWire):

        '''rearReflex(self, pyWire)
        '''

        print '###### rearReflex'


        pyPlaneList = pyWire.planes

        for pyPlane in self.planes:
            print 'pyPlane ', pyPlane.numGeom, pyPlane.shape.Faces
            # if len(pyPlane.shape.Faces) > 1:
            if not pyPlane.aligned:
                rear = pyPlane.rear
                for nGeom in rear:
                    pyRear = pyPlaneList[nGeom]
                    if pyRear.reflexed:
                        print 'rearReflex ', pyRear.numGeom
                        rearPl = pyRear.shape
                        gS = pyRear.geomShape
                        rearPl = rearPl.cut([pyPlane.shape], _Py.tolerance)

                        aList = []
                        AA = self.selectFace(rearPl.Faces, gS)
                        aList.append(AA)
                        rearPl = rearPl.removeShape([AA])

                        backward = pyRear.backward
                        forward = pyRear.forward

                        if rearPl.Faces:

                            pyReflex = self.selectAllReflex(pyRear.numWire,
                                                            pyRear.numGeom)

                            for pyPl in pyReflex[0].planes:     # TODO corregir esto y los metodos select
                                if (pyRear.numWire, pyRear.numGeom) !=\
                                   (pyPl.numWire, pyPl.numGeom):
                                       enormous = pyPl.enormousShape
                                       break

                            rearPl = rearPl.cut([enormous], _Py.tolerance)
                            for ff in rearPl.Faces:
                                print 'aaa'
                                section = ff.section([forward, backward],
                                                     _Py.tolerance)
                                if not section.Edges:
                                    print 'bbb'
                                    aList.append(ff)

                        rearPl = Part.makeCompound(aList)
                        pyRear.shape = rearPl

        for pyPlane in self.planes:
            pyPlane.isUnsolved()

    def rearing(self, pyWire):

        '''rearing(self, pyWire)
        '''

        for pyPlane in self.planes:
            if not pyPlane.reflexed:
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
