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

        '''__init__(self)'''

        self.planes = []
        self.rango = []
        self.rear = []
        self.lines = []

    @property
    def planes(self):

        '''planes(self)'''

        return self._planes

    @planes.setter
    def planes(self, planes):

        '''planes(self, planes)'''

        self._planes = planes

    @property
    def rango(self):

        '''rango(self)'''

        return self._rango

    @rango.setter
    def rango(self, rango):

        '''rango(self, rango)'''

        self._rango = rango

    @property
    def rear(self):

        '''rear(self)'''

        return self._rear

    @rear.setter
    def rear(self, rear):

        '''rear(self, rear)'''

        self._rear = rear

    @property
    def lines(self):

        '''lines(self)'''

        return self._lines

    @lines.setter
    def lines(self, lines):

        '''lines(self, lines)'''

        self._lines = lines

    def virtualizing(self):

        '''virtualizing(self)'''

        # print '###### virtualizing reflex'

        [pyReflex, pyOppReflex] = self.planes

        pyR = pyReflex.virtualizing()
        pyOppR = pyOppReflex.virtualizing()

        self.planes = [pyR, pyOppR]

        for pyPlane in [pyR, pyOppR]:

            if pyPlane.virtualized:
                nW = pyPlane.numWire
                pyAliList = pyPlane.alignedList

                pyAli = pyAliList[0]

                # esto esta muy raro

                pyBase = pyAli.base
                aligns = pyAli.aligns[:]
                aligns.insert(0, pyBase)
                chops = pyAli.chops
                rangoChop = pyAli.rango

                control = pyPlane.control

                num = -1
                for pyPl in aligns:
                    num += 1

                    if pyPl.numWire == nW:
                        control.append(pyPl.numGeom)
                        try:
                            for pyPl in chops[num]:
                                control.append(pyPl.numGeom)
                            for nn in rangoChop[num]:
                                control.append(nn)
                        except IndexError:
                            pass

    def simulating(self, force=False):

        '''simulating(self, force=False)'''

        [pyR, pyOppR] = self.planes

        enormousR = pyR.enormousShape
        enormousOppR = pyOppR.enormousShape

        pyR.simulating([enormousOppR])
        pyOppR.simulating([enormousR])

    def preProcess(self, pyWire):

        '''preProcess(self, pyWire)
        The planes included in a range are cutted between them,
        and by rear and oppRear'''

        # print '### preProcess'

        pyPlaneList = pyWire.planes
        refPlanes = self.planes

        pyR = refPlanes[0]
        # print (pyR.numWire, pyR.numGeom, pyR.rango)
        rango = pyR.rango[0]
        rangoPy = pyR.rangoPy[0]

        rearList = self.rear

        rear = rearList[0]
        oppRear = rearList[1]

        if oppRear and rear:

            pyRearPlane = pyPlaneList[rear]
            rearPlane = pyRearPlane.selectShape()

            pyOppRearPlane = pyPlaneList[oppRear]
            oppRearPlane = pyOppRearPlane.selectShape()

        for pyR in refPlanes:
            # print '# pyR ', pyR.numGeom
            # print 'rango ', rango
            # print 'rear ', rear
            # print 'oppRear ', oppRear

            for pyPlane in rangoPy:
                # print 'pyPlane.numGeom ', pyPlane.numGeom
                cList = []
                control = pyPlane.control

                if not (pyPlane.choped or pyPlane.aligned):
                    # print 'A'

                    rangoPost = []
                    for ran in pyPlane.rango:
                        rangoPost.extend(ran)
                    total = control + rangoPost
                    # print 'total ', total

                    num = -1
                    for nG in rango:
                        num += 1
                        if nG not in total:
                            pyPl = rangoPy[num]
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
                                    pyPl.selectAlignmentBase()
                                if pyAli:
                                    cList.extend(pyAli.simulatedAlignment)

                            else:
                                # print 'd'
                                if not pyPlane.reflexed:
                                    # print 'dd'
                                    cList.append(pyPl.simulatedShape)
                                else:
                                    # print 'ddd'
                                    pyReflexList = pyPl.reflexedList
                                    for pyReflex in pyReflexList:
                                        [pyOne, pyTwo] = pyReflex.planes
                                        if pyPlane.numGeom in\
                                           [pyOne.numGeom, pyTwo.numGeom]:
                                            # print 'ddd1'
                                            break
                                    else:
                                        # print 'ddd2'
                                        cList.append(pyPl.simulatedShape)

                if not (pyPlane.reflexed or pyPlane.fronted):
                    # print 'B'
                    if oppRear and rear:
                        cutList = []
                        if oppRear not in control:
                            # print 'a'
                            cutList.append(oppRearPlane)
                            if not pyOppRearPlane.reflexed:
                                # print 'aa'
                                control.append(oppRear)
                        if rear not in control:
                            # print 'b'
                            cutList.append(rearPlane)
                            if not pyRearPlane.reflexed:
                                # print 'bb'
                                control.append(rear)
                        cList.extend(cutList)

                if cList:
                    # print 'cList', cList
                    pyPlane.cuttingPyth(cList)
                    # print 'plane ', pyPlane.shape
                    # print 'control ', pyPlane.control

            if oppRear and rear:

                rear = rearList[1]
                oppRear = rearList[0]

                pyRearPlane = pyPlaneList[rear]
                rearPlane = pyRearPlane.selectShape()

                pyOppRearPlane = pyPlaneList[oppRear]
                oppRearPlane = pyOppRearPlane.selectShape()

            pyR = refPlanes[-1]
            rango = pyR.rango[-1]
            rangoPy = pyR.rangoPy[-1]

    def reflexing(self, pyWire):

        '''reflexing(self, pyWire)'''

        [pyR, pyOppR] = self.planes

        # print '### direction ', 'forward', (pyR.numGeom, pyOppR.numGeom)
        self.twin(pyWire, pyR, pyOppR, 'forward')

        # print '### direction ', 'backward', (pyOppR.numGeom, pyR.numGeom)
        self.twin(pyWire, pyOppR, pyR, 'backward')

    def twin(self, pyWire, pyR, pyOppR, direction):

        '''twin(self, pyWire, pyR, pyOppR, direction)'''

        pyPlaneList = pyWire.planes
        control = pyR.control

        rangoCorner, rangoCornerPy = [], []
        rangoNext, rangoNextPy = [], []

        rear = pyR.rear
        oppRear = pyOppR.rear

        if pyR.rear:

            if direction == 'forward':
                nGeom = rear[0]
                rangoCorner = pyR.rango[0]
                rangoCornerPy = pyR.rangoPy[0]
            else:
                nGeom = rear[-1]
                rangoCorner = pyR.rango[-1]
                rangoCornerPy = pyR.rangoPy[-1]

            if nGeom not in control or pyR.choped:

                rearPyPl = pyPlaneList[nGeom]
                if pyWire.numWire == 0:
                    rearPl = rearPyPl.selectShape()
                    if not rearPyPl.reflexed:
                        control.append(nGeom)
                        # print 'included rear ', (pyWire.numWire, nGeom)
                else:
                    rearPl = rearPyPl.selectShape(True)
                pyR.cutter.append(rearPl)

        else:

            if oppRear:

                if direction == 'forward':
                    numOppRear = oppRear[-1]
                else:
                    numOppRear = oppRear[0]

                if numOppRear == self.rear[1]:
                    # print 'simulatedShape'
                    pyR.cutter.append(pyOppR.simulatedShape)

        if oppRear:

            if direction == 'forward':
                rangoNext = pyOppR.rango[-1]
                rangoNextPy = pyOppR.rangoPy[-1]
            else:
                rangoNext = pyOppR.rango[0]
                rangoNextPy = pyOppR.rangoPy[0]

            if len(oppRear) == 1:

                nGeom = oppRear[0]

                if nGeom not in control or pyR.choped:

                    pyOppRear = pyPlaneList[nGeom]
                    oppRearPl = pyOppRear.selectShape()
                    pyR.cutter.append(oppRearPl)
                    if not pyOppRear.reflexed:
                        control.append(nGeom)
                    # print 'included oppRear ', (pyWire.numWire, nGeom)

            else:

                self.processOppRear(oppRear, direction, pyWire, pyR, pyOppR)

        # print 'rangoCorner ', rangoCorner
        for nn, pyPl in zip(rangoCorner, rangoCornerPy):
            if nn not in control or pyR.choped:  # or pyR.aligned:
                if nn not in oppRear:
                    # print nn
                    self.processRango(pyWire, pyR, pyOppR, pyPl,
                                      'rangoCorner', direction)

        # print 'rangoNext ', rangoNext
        if len(rear) == 1:
            for nn, pyPl in zip(rangoNext, rangoNextPy):
                if nn not in control or pyR.choped:  # or pyR.aligned:
                    if nn not in oppRear:
                        # print nn
                        self.processRango(pyWire, pyR, pyOppR, pyPl,
                                          'rangoNext', direction)

        rangoInter = self.rango
        # print 'rangoInter ', rangoInter
        for nn in rangoInter:
            if nn not in control or pyR.choped:  # or pyR.aligned:
                # print nn
                pyPlaneList = pyWire.planes  # provisionally
                pyPl = pyPlaneList[nn]
                self.processRango(pyWire, pyR, pyOppR, pyPl,
                                  'rangoInter', direction)

    def processOppRear(self, oppRear, direction, pyWire, pyR, pyOppR):

        '''processOppRear(self, oppRear, direction, pyWire, pyR, pyOppR)'''

        # print 'processOppRear'

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
            oppRearPl = pyOppRear.selectShape()
            pyR.cutter.append(oppRearPl)
            if not pyOppRear.reflexed:
                control.append(nGeom)
            # print 'included oppRear ', (pyWire.numWire, nGeom)

        if direction == "forward":
            nGeom = oppRear[0]
        else:
            nGeom = oppRear[1]

        pyOppRear = pyPlaneList[nGeom]

        if nGeom not in control or pyOppR.choped:

            oppRearPl = pyOppRear.selectShape()
            oppRearPl = oppRearPl.copy()
            oppRearPl = oppRearPl.cut([oppReflexEnormous], tolerance)

            pointWire = pyWire.coordinates
            if direction == "forward":
                point = pointWire[nGeom + 1]
            else:
                point = pointWire[nGeom]
            # print 'point ', point
            ff = self.selectFacePoint(oppRearPl, point)
            pyR.cutter.append(ff)
            # print 'included oppRear rectified ', (pyWire.numWire, nGeom)

    def processRango(self, pyWire, pyR, pyOppR, pyPl, kind, direction):

        '''processRango(self, pyWire, pyR, pyOppR, pyPl, kind, direction)'''

        tolerance = _Py.tolerance
        pyPlaneList = pyWire.planes
        numGeom = pyR.numGeom
        oppReflexEnormous = pyOppR.enormousShape

        nn = pyPl.numGeom
        gS = pyPl.geomShape

        if pyPl.aligned:
            # print 'A'
            pyAlign = pyPl.selectAlignmentBase()
            if pyAlign:
                pl = pyAlign.simulatedAlignment
                pyR.cutter.extend(pl)
                # print 'included rango simulated ', (pyWire.numWire, nn)

        elif pyPl.choped:
            # print 'B'
            pl = pyPl.simulatedShape
            pyR.cutter.append(pl)
            # print 'included rango simulated ', (pyWire.numWire, nn)

        elif pyPl.reflexed:
            # print 'C'
            pl = pyPl.simulatedShape.copy()

            rear = pyPl.rear

            pyReflexList = pyPl.reflexedList
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
                pyR.cutter.append(pl)
                # print 'included rango ', (pyWire.numWire, nn)

                pl = pyPl.simulatedShape.copy()     # Two faces included
                if kind == 'rangoCorner':
                    # print '22'
                    pl = self.cutting(pl, [oppReflexEnormous], gS)

            elif kind == 'rangoCorner':
                # print '3'

                if direction == 'forward':
                    forward = self.lines[0]
                else:
                    forward = self.lines[1]

                forw = pyPl.forward
                lList = [forw]
                if len(pyPl.rear) > 1:
                    back = pyPl.backward
                    lList.append(back)

                section = forward.section(lList, tolerance)

                if section.Vertexes:
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

                            fo = pyP.forward
                            lList = [fo]
                            if len(pyP.rear) > 1:
                                ba = pyP.backward
                                lList.append(ba)

                            section = forward.section(lList, tolerance)

                            if section.Vertexes:
                                cList.append(pyP.enormousShape)

                    if cList:
                        # print 'cList ', cList
                        pl = self.cutting(pl, cList, gS)

            else:   # rangoNext, rangoInter
                # print '4'
                pass

            pyR.cutter.append(pl)
            # print 'included rango simulated ', (pyWire.numWire, nn)

        else:
            # print 'D'
            pl = pyPl.shape.copy()

            if kind == 'rangoCorner':
                # print 'D1'
                pl = self.cutting(pl, [oppReflexEnormous], gS)

            pyR.cutter.append(pl)
            pyR.control.append(nn)
            # print 'included rango ', (pyWire.numWire, nn)

    def solveReflex(self, pyWire):

        '''solveReflex(self, pyWire)'''

        # print '### solveReflexs'

        [pyR, pyOppR] = self.planes

        reflex = pyR.shape.copy()
        oppReflex = pyOppR.shape.copy()

        # print '# processReflex forward ', (pyR.numGeom, pyOppR.numGeom, pyR.virtualized, pyOppR.virtualized)
        self.processReflex(reflex, oppReflex, pyR, pyOppR, 'forward', pyWire)

        # print '# processReflex backward', (pyOppR.numGeom, pyR.numGeom, pyOppR.virtualized, pyR.virtualized)
        self.processReflex(oppReflex, reflex, pyOppR, pyR, 'backward', pyWire)

        [pyR, pyOppR] = self.planes

        reflex = pyR.shape.copy()
        oppReflex = pyOppR.shape.copy()

        # print '# processReflexTwo forward ', (pyR.numGeom, pyOppR.numGeom)
        self.processReflexTwo(reflex, oppReflex, pyR, pyOppR, 'forward')

        # print '# processReflexTwo backward ', (pyOppR.numGeom, pyR.numGeom)
        self.processReflexTwo(oppReflex, reflex, pyOppR, pyR, 'backward')

    def processReflex(self, reflex, oppReflex, pyR, pyOppR,
                      direction, pyWire):

        '''processReflex(self, reflex, oppReflex, pyR, pyOppR,
                         direction, pyWire)'''

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
            cutList.extend(pyR.cutter)

        # print 'cutList ', cutList

        enorm = []    # auxiliar to clean the figure bottom
        rangoCorner = None
        rangoCornerPy = None
        rearList = pyR.rear
        oppRearList = pyOppR.rear

        if rearList:

            if direction == 'forward':
                pyRear = pyPlaneList[rearList[0]]
                if oppRearList:
                    pyOppRear = pyPlaneList[oppRearList[-1]]
                rangoCorner = pyR.rango[0]
                rangoCornerPy = pyR.rangoPy[0]
                forward = pyR.forward
                backward = pyR.backward

            else:
                pyRear = pyPlaneList[rearList[-1]]
                if oppRearList:
                    pyOppRear = pyPlaneList[oppRearList[0]]
                rangoCorner = pyR.rango[-1]
                rangoCornerPy = pyR.rangoPy[-1]

                if len(rearList) == 1:
                    forward = pyR.forward
                    backward = pyR.backward
                else:
                    forward = pyR.backward
                    backward = pyR.forward

            # print 'rear ', pyRear.numGeom
            # print 'rangoCorner ', rangoCorner
            rearGeom = pyRear.geomShape

            forw = forward.copy()
            forw = forw.cut([rearGeom], tolerance)
            wire = Part.Wire(forw.Edges)        ########################################
            orderedEdges = wire.OrderedEdges
            forw = orderedEdges[0]

            enormous = []  # auxiliar to build the allowed location to extra faces

            rearSimul = None
            if pyRear.aligned:
                pyA = pyRear.selectAlignmentBase()
                if pyA:
                    rearSimul = pyA.simulatedAlignment
            else:
                rearSimul = [pyRear.shape]

            if rearSimul:
                enormous.extend(rearSimul)

            if oppRearList:
                oppRearSimul = None
                if pyOppRear.aligned:
                    pyA = pyOppRear.selectAlignmentBase()
                    if pyA:
                        oppRearSimul = pyA.simulatedAlignment
                else:
                    oppRearSimul = [pyOppRear.shape]

                if oppRearSimul:
                    enormous.extend(oppRearSimul)

            # print 'enormous ', enormous

            corn = []    # auxiliar to look for extra faces
            for nn, pyPl in zip(rangoCorner, rangoCornerPy):
                # print 'rangoCorner nn ', nn
                if pyPl.aligned:
                    # print 'a'
                    pyAlign = pyPl.selectAlignmentBase()
                    if pyAlign:
                        pl = pyAlign.simulatedAlignment
                        corn.append(pl)
                elif pyPl.reflexed:
                    # print 'b'
                    pl = pyPl.simulatedShape
                    line = pyPl.forward  # ??? with pyReflex
                    # podria ser
                    # if len(pyReflexedList) > 1:
                    # añadir backward
                    section = forw.section([line], tolerance)
                    if section.Vertexes:
                        # print 'b1'
                        pass
                    else:
                        # print 'b2'
                        corn.append(pl)
                else:
                    # print 'c'
                    pl = pyPl.shape
                    corn.append(pl)

            # print 'corn ', corn
            corn = Part.makeCompound(corn)

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
            # print 'cutList ', cutList
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
                    section = ff.section([rearGeom], tolerance)
                    if not section.Vertexes:
                        cutterList.append(ff)
        # print 'cutterList ', cutterList, len(cutterList)

        cList = []    # clean cutterList

        if rearList:

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

        cList = pyR.cutter[:]

        if pyWire.numWire > 0:
            # print 'interior wire'

            if not oppRearList:

                rList = pyOppR.reflexedList
                if len(rList) == 2:
                    cList.append(pyOppR.enormousShape)

        if cList:
            reflex = reflex.cut(cList, tolerance)
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

            if not pyRear.aligned:

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
                                                    ff.common([seed],
                                                              tolerance)
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

    def processReflexTwo(self, reflex, oppReflex, pyR, pyOppR, direction):

        '''
        processReflexTwo(self, reflex, oppReflex, pyR, pyOppR, direction)
        '''

        tolerance = _Py.tolerance
        gS = pyR.geomShape

        if direction == 'forward':
            forward = pyR.forward
            backward = pyR.backward
        else:
            if len(pyR.rear) == 1:
                forward = pyR.forward
                backward = pyR.backward
            else:
                forward = pyR.backward
                backward = pyR.forward

        # podría incluir en isSolved la detención de sobrantes en planos de una cara
        # que tienen un vertice en la planta (tres vertices en total)

        if pyR.numWire > 0 and pyOppR.choped:
            oppReflex = pyOppR.bigShape

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
                    if section.Vertexes and not section.Edges:
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
                            section = backward.section(aList, tolerance)
                            if section.Edges:
                                bList = [ff]
                                break
                            else:
                                section = ff.section(aList, tolerance)
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

        '''postProcess(self, pyWire)
        Reflexed planes with only one face'''

        # print '### postProcess'

        tolerance = _Py.tolerance
        refList = self.planes
        lines = self.lines

        for pyPlane in refList:
            plane = pyPlane.shape
            control = pyPlane.control

            if len(plane.Faces) == 1:
                # print '# cutted ', pyPlane.numGeom

                forward = lines[0]
                forwardOpp = lines[-1]

                gS = pyPlane.geomShape
                lList = Part.makeCompound([gS, forward, forwardOpp])

                for pyReflex in pyWire.reflexs:
                    for pyPl, fo in zip(pyReflex.planes, pyReflex.lines):
                        if pyPl.numGeom not in control:
                            # print 'pyPl.numGeom ', pyPl.numGeom
                            pl = pyPl.shape
                            if pyPl.isSolved():
                                # print 'solved'

                                section = fo.section([lList], tolerance)

                                if section.Vertexes:
                                    # print 'cutter ', pyPl.numGeom
                                    conflictList =\
                                        pyPl.isReallySolved(pyWire, pyReflex)
                                    # print 'conflictList ', [p.numGeom for p in conflictList]

                                    if pyPlane in conflictList:
                                        # print 'A'
                                        pyPlane.cuttingPyth([pl])
                                        control.append(pyPl.numGeom)
                                        pyPl.reallySolved.remove(pyPlane)

                                    elif not conflictList:
                                        # print 'B'
                                        pyPlane.cuttingPyth([pl])
                                        control.append(pyPl.numGeom)

    def postProcessTwo(self, pyWire):

        '''postProcessTwo(self, pyWire)'''

        # print '### postProcessTwo'

        # TODO unir los dos postProcess

        tolerance = _Py.tolerance
        pyPlaneList = pyWire.planes

        refList = self.planes
        lineList = self.lines
        rangoInter = self.rango

        pyOppPlane = refList[1]

        for pyPlane, forward in zip(refList, lineList):
            # print '# pyPlane ', (pyPlane.numWire, pyPlane.numGeom)
            plane = pyPlane.shape
            control = pyPlane.control

            cutterList = []
            for pyReflex in pyWire.reflexs:
                for pyPl in pyReflex.planes:
                    if pyPl.numGeom not in control:

                        if pyPl.isSolved():
                            # print 'pyPl solved', pyPl.numGeom
                            pl = pyPl.shape

                            if len(pl.Faces) == 1:
                                # print 'A'

                                conflictList = pyPl.isReallySolved(pyWire,
                                                                   pyReflex)

                                # print 'conflictList ', conflictList

                                cList = []
                                for pyP in conflictList:
                                    if pyP.isSolved():
                                        cList.append(pyP)
                                        pyPl.reallySolved.remove(pyP)
                                    else:
                                        break
                                else:
                                    # print 'cList ', cList
                                    for pyP in cList:
                                        # print 'pyP ', pyP.numGeom
                                        pyPl.cuttingPyth([pyP.shape])
                                        pyPl.control.append(pyP.numGeom)
                                    # print 'AA'
                                    cutterList.append(pyPl.shape)
                                    control.append(pyPl.numGeom)

                            else:
                                # print 'B'
                                cutterList.append(pl)
                                control.append(pyPl.numGeom)

                        else:
                            # print 'pyPl no solved', pyPl.numGeom
                            if pyPl.numGeom in rangoInter:
                                # print 'a'

                                section = plane.section([forward], tolerance)
                                if section.Edges:
                                    # print 'b'

                                    rear = pyPlane.rear[0]
                                    pyRearPlane = pyPlaneList[rear]
                                    rearPl = pyRearPlane.shape
                                    if rear not in control:
                                        cutterList.append(rearPl)
                                        control.append(rearPl)

                                    oppRear = pyOppPlane.rear[-1]
                                    if oppRear not in control:
                                        pyOppRearPlane = pyPlaneList[oppRear]
                                        oppRearPl = pyOppRearPlane.shape
                                        cutterList.append(oppRearPl)
                                        control.append(oppRearPl)

                                    pl = pyPl.shape
                                    section = pl.section([rearPl], tolerance)

                                    if section.Edges:
                                        # print 'c'

                                        cutterList.append(pl)
                                        control.append(pyPl.numGeom)

                            elif not (pyPlane.rear or pyPl.aligned):
                                # print 'aa'

                                pl = pyPl.shape
                                cutterList.append(pl)
                                control.append(pyPl.numGeom)

            # print 'cutterList', cutterList

            if cutterList:

                gS = pyPlane.geomShape

                if len(plane.Faces) == 1:
                    # print '0'

                    plane = self.cutting(plane, cutterList, gS)
                    aList = [plane]

                else:
                    # print '1'

                    ff = plane.Faces[0]
                    ff = self.cutting(ff, cutterList, gS)
                    aList = [ff]

                    ff = plane.Faces[1]
                    ff = ff.cut(cutterList, tolerance)
                    for f in ff.Faces:
                        # print '11'
                        section = f.section([forward], tolerance)
                        if not section.Edges:
                            # print '111'
                            aList.append(f)
                            break

                compound = Part.Compound(aList)
                pyPlane.shape = compound

            pyOppPlane = refList[0]

    def rearing(self, pyWire):

        '''rearing(self, pyWire)'''

        mono = pyWire.mono

        direction = "forward"
        for pyPlane, rear in zip(self.planes, self.rear):
            if rear:
                if mono:
                    if pyPlane.secondRear:
                        pyPlane.rearing(pyWire, self, direction)
                else:
                    pyPlane.rearing(pyWire, self, direction)
            direction = "backward"

    def rangging(self, pyWire):

        '''rangging(self, pyWire)'''

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
                pyPlane.rangging(pyWire, direction, self)
            direction = "backward"
