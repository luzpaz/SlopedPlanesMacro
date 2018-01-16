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
from SlopedPlanesPyPlane import _PyPlane

__title__ = "SlopedPlanes Macro"
__author__ = "Damian Caceres Moreno"
__url__ = "http://www.freecadweb.org"
__version__ = ""


class _PyAlignment(_Py):

    '''The complementary python object class for alignments.'''

    def __init__(self):

        ''''''

        self.base = None
        self.aligns = []
        self.chops = []
        self.geomAligned = None
        self.rango = []
        self.rangoRear = []
        self.falsify = False
        self.simulatedAlignment = []
        self.simulatedChops = []
        self.prior = None
        self.later = None

    @property
    def base(self):

        ''''''

        return self._base

    @base.setter
    def base(self, base):

        ''''''

        self._base = base

    @property
    def aligns(self):

        ''''''

        return self._aligns

    @aligns.setter
    def aligns(self, aligns):

        ''''''

        self._aligns = aligns

    @property
    def chops(self):

        ''''''

        return self._chops

    @chops.setter
    def chops(self, chops):

        ''''''

        self._chops = chops

    @property
    def geomAligned(self):

        ''''''

        return self._geomAligned

    @geomAligned.setter
    def geomAligned(self, geomAligned):

        ''''''

        self._geomAligned = geomAligned

    @property
    def rango(self):

        ''''''

        return self._rango

    @rango.setter
    def rango(self, rango):

        ''''''

        self._rango = rango

    @property
    def rangoRear(self):

        ''''''

        return self._rangoRear

    @rangoRear.setter
    def rangoRear(self, rangoRear):

        ''''''

        self._rangoRear = rangoRear

    @property
    def falsify(self):

        ''''''

        return self._falsify

    @falsify.setter
    def falsify(self, falsify):

        ''''''

        self._falsify = falsify

    @property
    def simulatedAlignment(self):

        ''''''

        return self._simulatedAlignment

    @simulatedAlignment.setter
    def simulatedAlignment(self, simulatedAlignment):

        ''''''

        self._simulatedAlignment = simulatedAlignment

    @property
    def simulatedChops(self):

        ''''''

        return self._simulatedChops

    @simulatedChops.setter
    def simulatedChops(self, simulatedChops):

        ''''''

        self._simulatedChops = simulatedChops

    @property
    def prior(self):

        ''''''

        return self._prior

    @prior.setter
    def prior(self, prior):

        ''''''

        self._prior = prior

    @property
    def later(self):

        ''''''

        return self._later

    @later.setter
    def later(self, later):

        ''''''

        self._later = later

    def virtualizing(self):

        '''virtualizing(self)
        Virtualizes the chops and the base of falsify alignnments.'''

        virtualizedChops = []
        for [pyChopOne, pyChopTwo] in self.chops:

            pyOne = pyChopOne.virtualizing()
            pyOne.choped = True
            pyTwo = pyChopTwo.virtualizing()
            pyTwo.choped = True

            virtualizedChops.append([pyOne, pyTwo])

        self.chops = virtualizedChops

        if self.falsify:
            if not self.base.shape:
                virtualBase = self.base.virtualizing()
                self.base = virtualBase

    def trimming(self):

        '''trimming(self)
        The alignment blocks the progress of the planes
        in its front and laterals.'''

        # print '###### trimming base ', (self.base.numWire, self.base.numGeom)

        pyWireList = _Py.pyFace.wires
        pyWire = pyWireList[0]
        pyPlaneList = pyWire.planes

        falsify = self.falsify

        pyBase = self.base
        base = pyBase.shape
        numGeom = pyBase.numGeom
        enormousBase = pyBase.enormousShape
        baseRear = pyBase.rear
        baseControl = pyBase.control

        pyCont = self.aligns[-1]
        cont = pyCont.shape
        nGeom = pyCont.numGeom
        enormousCont = pyCont.enormousShape
        contRear = pyCont.rear

        pyPrior = self.prior
        pyLater = self.later
        pr = pyPrior.numGeom
        lat = pyLater.numGeom

        # rangoRear
        w1 = pyPrior.numWire
        w2 = pyLater.numWire
        g1 = pyPrior.numGeom
        g2 = pyLater.numGeom
        rangoRear = self.rang((w2, g2), (w1, g1))
        if rangoRear:
            rangoRear.insert(0, lat)
            rangoRear.append(pr)
        self.rangoRear = rangoRear
        # print 'rangoRear ', rangoRear

        rangoChop = self.rango
        chops = self.chops

        numChop = -1
        for rChop in rangoChop:
            numChop += 1

            [pyOne, pyTwo] = chops[numChop]

            # rango
            totalRango = []
            num = -1
            for pyPlane in chops[numChop]:
                num += 1
                if num == 0:
                    rangoOne = pyPlane.rango[-1]
                    totalRango.extend(rangoOne)
                else:
                    rangoTwo = pyPlane.rango[0]
                    totalRango.extend(rangoTwo)

            # the two rangos don't cut between them

            for nG in rangoOne:
                pyPl = pyPlaneList[nG]
                control = pyPl.control
                for r in rangoTwo:
                    if r not in control:
                        control.append(r)
                # and opp Chop
                r = pyTwo.numGeom
                if r not in control:
                    control.append(r)

            for nG in rangoTwo:
                pyPl = pyPlaneList[nG]
                control = pyPl.control
                for r in rangoOne:
                    if r not in control:
                        control.append(r)
                # and opp chop
                r = pyOne.numGeom
                if r not in control:
                    control.append(r)

            # TODO [pyOne, pyTwo] dont cut with other twin chops

            pyPlList = pyWireList[pyOne.numWire].planes

            # rChop: trimming bigShape

            if falsify:
                cutList = [enormousBase, enormousCont]
            else:
                cutList = [enormousBase]

            rC = []

            for nG in rChop:
                pyPl = pyPlList[nG]
                if not pyPl.aligned:
                    bPl = pyPl.bigShape
                    gS = pyPl.geomShape
                    bPl = self.cutting(bPl, cutList, gS)
                    pyPl.bigShape = bPl
                    pyPl.fronted = True

                    rC.append(bPl)

                    control = pyPl.control

                    # rChop doesn't cut with rangoRear
                    if w1 == pyOne.numWire:
                        for r in rangoRear:
                            if r not in control:
                                control.append(r)

                    # rChop doesn't cut with alignment
                    control.append(numGeom)
                    if falsify:
                        control.append(nGeom)

                    # pyOne and pyTwo don't cut rChop
                    pyOne.control.append(nG)
                    pyTwo.control.append(nG)

                    # the aligment doesn't cut rChop ???
                    baseControl.append(nG)

                    # TODO rChop doesn't cut with other rChop
                    # TODO rChop doesn't cut with other chops

            # the rango's planes are cutted by the chop,
            # and perhaps by the base or the continuation
            num = -1
            for pyPlane in [pyOne, pyTwo]:
                num += 1
                # print '### chop ', pyPlane.numWire, pyPlane.numGeom
                enormousShape = pyPlane.enormousShape

                # the cross
                cont = True
                if num == 0:
                    rango = rangoOne
                    if pyPlane.virtualized:
                        if not pyPlane.geomAligned:
                            cont = False
                else:
                    rango = rangoTwo
                    if pyPlane.virtualized:
                        if pyPlane.geomAligned:
                            cont = False
                # print 'cont ', cont
                # print 'rango ', rango

                for nG in rango:
                    pyPl = pyPlaneList[nG]
                    control = pyPl.control
                    if numGeom not in control:
                        if not pyPl.aligned and not pyPl.choped:
                            # print '# nG ', nG

                            if cont:
                                # print 'A'
                                cList = [enormousShape]

                                if nG not in baseRear and nG not in contRear:
                                    # print 'a'
                                    if nG not in [pr, lat]:
                                        # print 'aa'

                                        if falsify:
                                            # print 'aa1'
                                            if num == 0:
                                                # print 'aa11'
                                                cList.append(enormousBase)
                                                control.append(numGeom)
                                            else:
                                                # print 'aa12'
                                                cList.append(enormousCont)
                                                control.append(nGeom)

                                        else:
                                            # print 'aa2'
                                            cList.append(enormousBase)
                                            control.append(numGeom)

                                pyPl.trimming(enormousShape, cList)
                                control.append(pyPlane.numGeom)

                            else:
                                # print 'B'
                                pyPl.trimmingTwo(enormousShape)

        if falsify:
            # the base and cont are cutted by a chop

            rC = Part.makeCompound(rC)

            section = rC.section([base], _Py.tolerance)
            gS = pyBase.geomShape
            if section.Edges:
                base = self.cutting(base, [pyTwo.enormousShape], gS)
            else:
                base = self.cutting(base, [pyOne.enormousShape], gS)
            pyBase.shape = base

            section = rC.section([cont], _Py.tolerance)
            gS = pyCont.geomShape
            if section.Edges:
                cont = self.cutting(cont, [pyOne.enormousShape], gS)
            else:
                cont = self.cutting(cont, [pyTwo.enormousShape], gS)
            pyCont.shape = cont

            # TODO falseAlignment base and continuation don't cut opp rango

        # rangoRear doesn't cut with rangoChop
        pyPlList = pyWireList[w1].planes
        for rr in rangoRear:
            # print 'rangoRear ', rr
            pyPl = pyPlList[rr]
            control = pyPl.control
            numChop = -1
            for rChop in self.rango:
                numChop += 1
                [pyOne, pyTwo] = chops[numChop]
                if w1 == pyOne.numWire:
                    for nn in rChop:
                        control.append(nn)
                        # print 'rangoRear doesn\'t cut with rangoChop', nn

    def priorLater(self):

        '''priorLater(self)
        '''

        # print '###### priorLater base ', (self.base.numWire, self.base.numGeom)

        falsify = self.falsify

        pyBase = self.base
        numGeom = pyBase.numGeom
        base = pyBase.shape
        bigBase = pyBase.bigShape
        control = pyBase.control

        pyCont = self.aligns[-1]
        nGeom = pyCont.numGeom
        cont = pyCont.shape
        bigCont = pyCont.bigShape

        pyPrior = self.prior
        pyLater = self.later
        prior = pyPrior.shape
        later = pyLater.shape
        pr = pyPrior.numGeom
        lat = pyLater.numGeom
        bigPrior = pyPrior.bigShape
        bigLater = pyLater.bigShape

        cutterList = []

        if ((not pyPrior.reflexed) or
           (pyPrior.choped and not pyPrior.aligned)):
            # print '1'
            cutterList.append(bigPrior)
            if not pyBase.choped:
                # print '11'
                control.append(pr)

        if ((not pyLater.reflexed) or
           (pyLater.choped and not pyLater.aligned)):
            # print '2'
            cutterList.append(bigLater)
            if not self.falsify:
                if not pyBase.choped:
                    # print '21'
                    control.append(lat)

        if not falsify:
            # print 'A'

            if cutterList:
                # print 'AA'
                gS = pyBase.geomShape
                base = self.cutting(base, cutterList, gS)
                pyBase.shape = base

        else:
            # print 'B'

            [pyOne, pyTwo] = self.chops[0]

            cList = [bigPrior]
            gS = pyBase.geomShape
            base = self.cutting(base, cList, gS)
            control.append(lat)

            pyBase.shape = base

            cList = [bigLater]
            pyCont.control.append(lat)
            pyCont.control.append(pr)

            gS = pyCont.geomShape
            cont = self.cutting(cont, cList, gS)

            pyCont.shape = cont

        # cuts pyPrior and pyLater

        if not pyPrior.reflexed or pyPrior.choped:
            # print 'a'

            if pyPrior.numWire == 0:
                # print 'a1'

                if not pyPrior.arrow:
                    # print 'a11'

                    gS = pyPrior.geomShape
                    prior = self.cutting(prior, [bigBase], gS)
                    pyPrior.control.append(numGeom)
                    pyPrior.shape = prior

            else:
                # print 'a2'

                gS = pyPrior.geomShape
                prior = self.cutting(prior, [bigBase], gS)
                pyPrior.control.append(numGeom)
                pyPrior.shape = prior

            if falsify:
                pyPrior.control.append(nGeom)

        if not pyLater.reflexed or pyLater.choped:
            # print 'b'

            if pyLater.numWire == 0:
                # print 'b1'

                if not pyLater.arrow:

                    if not falsify:
                        # print 'b11'

                        gS = pyLater.geomShape
                        later = self.cutting(later, [bigBase], gS)
                        pyLater.control.append(numGeom)

                    else:
                        # print 'b12'

                        gS = pyLater.geomShape
                        later = self.cutting(later, [bigCont], gS)
                        pyLater.control.append(nGeom)
                        pyLater.control.append(numGeom)

                    pyLater.shape = later

            else:
                # print 'b2'

                if not falsify:
                    # print 'b21'

                    gS = pyLater.geomShape
                    later = self.cutting(later, [bigBase], gS)
                    pyLater.control.append(numGeom)

                else:
                    # print 'b22'

                    gS = pyLater.geomShape
                    later = self.cutting(later, [bigCont], gS)
                    pyLater.control.append(nGeom)
                    pyLater.control.append(numGeom)

                pyLater.shape = later

    def simulating(self):

        ''''''

        enormousBase = self.base.enormousShape

        for [pyOne, pyTwo] in self.chops:

            enormous = pyTwo.enormousShape
            pyOne.simulating([enormous, enormousBase])

            enormous = pyOne.enormousShape
            pyTwo.simulating([enormous, enormousBase])

    def simulatingAlignment(self):

        '''simulatingAlignment(self)
        '''

        # print '###### simulatingAlignment ', (self.base.numWire, self.base.numGeom)

        chops = self.chops
        falsify = self.falsify

        pyBase = self.base
        base = pyBase.shape.copy()

        pyPrior = self.prior
        pyLater = self.later

        # the chops
        cutterList = []

        for [pyOne, pyTwo] in chops:

            cutterList.append(pyOne.simulatedShape)
            cutterList.append(pyTwo.simulatedShape)

        if falsify:

            pyCont = self.aligns[-1]
            cont = pyCont.shape.copy()

            # prior and later

            cList = cutterList[:]
            if pyPrior.numGeom not in pyBase.control:
                cList.append(pyPrior.bigShape)
            gS = pyBase.geomShape
            base = self.cutting(base, cList, gS)

            cList = cutterList[:]
            if pyLater.numGeom not in pyCont.control:
                cList.append(pyLater.bigShape)
            gS = pyCont.geomShape
            cont = self.cutting(cont, cList, gS)

            shapeList = [base, cont]

        else:

            # prior and later

            if pyPrior.numGeom not in pyBase.control:
                cutterList.append(pyPrior.bigShape)

            if pyLater.numGeom not in pyBase.control:
                cutterList.append(pyLater.bigShape)

            geomList = [pyP.geomShape for pyP in self.aligns]
            geomList.insert(0, pyBase.geomShape)
            # print geomList

            base = base.cut(cutterList, _Py.tolerance)
            # print 'base.Faces ', base.Faces
            shapeList = []
            for ff in base.Faces:
                section = ff.section(geomList, _Py.tolerance)
                if section.Edges:
                    # print 'section'
                    shapeList.append(ff)
            # print 'shapeList ', shapeList

        self.simulatedAlignment = shapeList

    def simulatingChops(self):

        ''''''

        tolerance = _Py.tolerance

        pyFace = _Py.pyFace
        pyWireList = pyFace.wires

        simulatedAlignment = self.simulatedAlignment
        rangoChop = self.rango
        simulatedChops = []

        geomList = [pyP.geomShape for pyP in self.aligns]
        geomList.insert(0, self.base.geomShape)

        numChop = -1
        for [pyOne, pyTwo] in self.chops:
            numChop += 1

            rChop = rangoChop[numChop]

            pyW = pyWireList[pyOne.numWire]
            pyPlList = pyW.planes
            cutList = []
            for rr in rChop:
                pyPl = pyPlList[rr]
                if not pyPl.aligned and not pyPl.choped:
                    pl = pyPl.bigShape
                    cutList.append(pl)

            cList = []

            if cutList:

                bb = self.base.shape.copy()
                bb = bb.cut([pyOne.simulatedShape,
                             pyTwo.simulatedShape], tolerance)

                for ff in bb.Faces:
                    section = ff.section(geomList, tolerance)
                    if not section.Edges:
                        bb = ff
                        break

                cL = Part.makeCompound(cutList)
                cL = cL.cut([pyOne.enormousShape,
                             pyTwo.enormousShape], tolerance)

                for ff in cL.Faces:
                    section = ff.section([bb], tolerance)
                    if section.Edges:
                        cList.append(ff)

                if cList:

                    pyOne.simulating(cList)
                    pyTwo.simulating(cList)

            simulatedChops.append(cList[:])

            shapeOne = pyOne.simulatedShape
            cList.append(shapeOne)

            shapeTwo = pyTwo.simulatedShape
            cList.append(shapeTwo)

            simulatedAlignment.extend(cList)

        self.simulatedChops = simulatedChops

    def aligning(self):

        '''aligning(self)
        '''

        # print '###### base ', (self.base.numWire, self.base.numGeom)
        # print '###### base shape ', self.base.shape
        # print '###### aligns ', [(x.numWire, x.numGeom) for x in self.aligns]
        # print '###### chops ', [[(x.numWire, x.numGeom), (y.numWire, y.numGeom)] for [x, y] in self.chops]

        tolerance = _Py.tolerance
        pyWireList = _Py.pyFace.wires
        pyPlaneList = pyWireList[0].planes

        falsify = self.falsify

        pyBase = self.base
        base = pyBase.shape
        enormousBase = pyBase.enormousShape
        aligns = self.aligns
        rangoChop = self.rango

        pyCont = aligns[-1]
        cont = pyCont.shape
        enormousCont = pyCont.enormousShape

        # the chops

        simulatedChops = self.simulatedChops

        chopList = []
        numChop = -1
        for [pyOne, pyTwo] in self.chops:
            numChop += 1
            # print '### [pyOne, pyTwo]', [(pyOne.numWire, pyOne.numGeom), (pyTwo.numWire, pyTwo.numGeom)]

            rChop = rangoChop[numChop]

            nW = pyOne.numWire
            pyW = pyWireList[nW]
            pyPlList = pyW.planes

            simulatedC = simulatedChops[numChop]
            # print 'simulatedC ', simulatedC

            pyTwinPlane = pyTwo

            num = -1
            for pyPlane in [pyOne, pyTwo]:
                num += 1
                # print '# pyPlane ', (pyPlane.numWire, pyPlane.numGeom)
                gS = pyPlane.geomShape
                plane = pyPlane.shape

                # with complex rChop this will not work fine ???
                # en la etapa de simulado ya haces este corte. Revisar
                if simulatedC:
                    plane = self.cutting(plane, simulatedC, gS)
                    pyPlane.shape = plane
                else:
                    if rChop:
                        if num == 0:
                            nextNum = self.sliceIndex(pyOne.numGeom+1,
                                                      len(pyPlList))
                            nextPl = self.selectPlane(nW, nextNum)
                            if not nextPl.aligned and not nextPl.choped:
                                plane = self.cutting(plane, [nextPl.shape], gS)
                                pyPlane.shape = plane
                        else:
                            preNum = self.sliceIndex(pyTwo.numGeom-1,
                                                     len(pyPlList))
                            prePl = self.selectPlane(nW, preNum)
                            if not prePl.aligned and not prePl.choped:
                                plane = self.cutting(plane, [prePl.shape], gS)
                                pyPlane.shape = plane

                if num == 0:
                    rango = pyOne.rango[-1]
                    rear = pyOne.rear[-1]
                    rearOne = rear
                    cList = [enormousBase]
                    oppRango = pyTwo.rango[0]
                    oppRear = pyTwo.rear[0]

                else:
                    rango = pyTwo.rango[0]
                    rear = pyTwo.rear[0]
                    rearTwo = rear
                    oppRango = pyOne.rango[-1]
                    oppRear = pyOne.rear[-1]
                    if falsify:
                        cList = [enormousCont]
                    else:
                        cList = [enormousBase]

                cutList = []
                rC = []

                for nn in rango:
                    pyPl = pyPlaneList[nn]
                    if pyPl.aligned:
                        pyAli = self.selectAlignment(0, nn)
                        pl = pyAli.simulatedAlignment
                    elif not pyPl.choped:
                        rC.append(pyPl.shape)
                        pl = [pyPl.shape]
                    else:
                        pl = None
                    if pl:
                        if pl not in cutList:
                            cutList.extend(pl)
                            # print'rangoPlane ', nn

                # print 'rC ', rC
                rC = Part.makeCompound(rC)

                pyPl = pyPlaneList[rear]
                if pyPl.aligned:
                    pyAli = self.selectAlignment(0, rear)
                    pl = pyAli.simulatedAlignment
                elif not pyPl.choped:
                    pl = [pyPl.shape]
                else:
                    pl = None
                if pl:
                    if pl not in cutList:
                        cutList.extend(pl)
                        # print'rearPlane ', rear

                if not oppRango:
                    pyPl = pyPlaneList[oppRear]
                    if not pyPl.choped:
                        # print 'a'
                        if not pyPl.aligned:
                            # print 'a1'
                            oppRearPlane = pyPl.shape
                            # if rearPlane not in cutList:
                            cutList.append(oppRearPlane)
                            # print'rearPlane ', rear

                plane = pyPlane.shape
                planeCopy = plane.copy()

                cutterList = cutList + cList
                # print 'cutterList ', cutterList

                gS = pyPlane.geomShape
                planeCopy = planeCopy.cut(cutterList, tolerance)
                # print 'planeCopy.Faces ', planeCopy.Faces

                fList = []
                for ff in planeCopy.Faces:
                    section = ff.section([gS], tolerance)
                    if not section.Edges:
                        section = ff.section([_Py.face], tolerance)
                        if section.Edges:
                            fList.append(ff)

                planeCopy = plane.copy()

                if fList:
                    planeCopy = planeCopy.cut(fList, tolerance)

                if cutList:

                    if pyPlane.numWire == 0 and pyTwinPlane.numWire != 0:
                        # debería ser mas selectivo ya que prodrian haber otros chops en el wire exterior
                        # puedes comprobarlo con self.aligns o con self.rango
                        rChop = rangoChop[numChop]
                        if not rChop:
                            falsePlane = _PyPlane(0, pyPlane.numGeom)
                            falsePlane.rear = pyPlane.rear
                            pyWire = pyWireList[0]
                            falsePlane.rangging(pyWire, 'backward')
                            rr = falsePlane.rangoConsolidate
                            # print rr

                            for nn in rr:
                                pyPl = pyPlaneList[nn]
                                if not pyPl.choped:
                                    if not pyPl.aligned:
                                        pl = pyPl.shape
                                        cutList.append(pl)
                                        # print 'rr ', nn

                    planeCopy = planeCopy.cut(cutList, tolerance)

                # print 'planeCopy.Faces ', planeCopy.Faces

                aList = []
                for ff in planeCopy.Faces:
                    # print '1'
                    section = ff.section([gS], tolerance)
                    if section.Edges:
                        # print '11'
                        aList.append(ff)
                        planeCopy = planeCopy.removeShape([ff])
                        break
                # print 'planeCopy.Faces ', planeCopy.Faces

                if planeCopy.Faces:
                    planeCopy = planeCopy.cut(cList, tolerance)

                forward = pyPlane.forward
                backward = pyPlane.backward

                ffList = []
                for ff in planeCopy.Faces:
                    # print '2'
                    section = ff.section([forward, backward], tolerance)
                    if not section.Edges:
                        # print '21'
                        section = ff.section(aList, tolerance)
                        if not section.Vertexes:
                            # print '211'
                            section = ff.section([rC], tolerance)
                            if section.Edges:
                                # print '2111'
                                ffList.append(ff)
                                break

                aList.extend(ffList)
                # print 'aList ', aList
                comp = Part.makeCompound(aList)
                pyPlane.shape = comp

                pyTwinPlane = pyOne

                if num == 0:
                    rCOne = rC
                else:
                    rCTwo = rC

            # twin

            shapeOne = pyOne.shape.copy()
            shapeTwo = pyTwo.shape.copy()

            fList = []
            gS = pyOne.geomShape
            ff = self.cutting(shapeOne.Faces[0], [shapeTwo], gS)
            fList.append(ff)

            for ff in shapeOne.Faces[1:]:
                ff = ff.cut([shapeTwo], _Py.tolerance)
                for f in ff.Faces:
                    section = f.section([rCOne], _Py.tolerance)
                    if section.Edges:
                        fList.append(f)

            # print 'fList ', fList
            compound = Part.makeCompound(fList)
            pyOne.shape = compound

            fList = []
            gS = pyTwo.geomShape
            ff = self.cutting(shapeTwo.Faces[0], [shapeOne], gS)
            fList.append(ff)

            for ff in shapeTwo.Faces[1:]:
                ff = ff.cut([shapeOne], _Py.tolerance)
                for f in ff.Faces:
                    section = f.section([rCTwo])
                    if section.Edges:
                        fList.append(f)

            # print 'fList ', fList
            compound = Part.makeCompound(fList)
            pyTwo.shape = compound

            chopList.append([pyOne, pyTwo])

        # the alignments

        if self.falsify:

            rChop = rangoChop[0]
            pyCont = aligns[0]

            [pyOne, pyTwo] = chopList[0]

            shapeOne = pyOne.shape
            shapeTwo = pyTwo.shape

            cutterList = [shapeOne, shapeTwo]

            for nn in rChop:

                nW = pyOne.numWire
                pyW = pyWireList[nW]
                pyPlList = pyW.planes

                pl = pyPlList[nn].shape
                if pl:
                    cutterList.append(pl)
                    # print 'rangoChop ', nn

            if cutterList:

                gS = pyBase.geomShape
                base = self.cutting(base, cutterList, gS)
                pyBase.shape = base

            if not pyTwo.virtualized:

                gS = pyTwo.geomShape
                shapeTwo = self.cutting(shapeTwo, [base, cont, shapeOne], gS)
                pyTwo.shape = shapeTwo

            if cutterList:

                gS = pyCont.geomShape
                cont = self.cutting(cont, cutterList, gS)
                pyCont.shape = cont

            if not pyOne.virtualized:

                gS = pyOne.geomShape
                shapeOne = self.cutting(shapeOne, [cont, base, shapeTwo], gS)
                pyOne.shape = shapeOne

        else:

            cutList = []

            numChop = -1
            for pyCont in aligns:
                numChop += 1

                [pyOne, pyTwo] = chopList[numChop]
                rChop = rangoChop[numChop]

                nW = pyOne.numWire
                pyW = pyWireList[nW]
                pyPlList = pyW.planes

                shapeOne = pyOne.shape
                shapeTwo = pyTwo.shape

                cutterList = [shapeOne, shapeTwo]
                cutList.extend(cutterList)

                simulatedC = simulatedChops[numChop]

                cutterList.extend(simulatedC)

                base = base.cut(cutterList, _Py.tolerance)
                # print 'base.Faces ', base.Faces
                baseCopy = base.copy()

                number = 2
                if len(shapeOne.Faces) > 1 or len(shapeTwo.Faces) > 1:
                    number += 1
                # print 'number ', number

                if len(base.Faces) == number:
                    # print 'a'

                    gS = pyBase.geomShape
                    base = self.selectFace(base.Faces, gS)
                    pyBase.shape = base
                    cutList.append(base)

                else:
                    # print 'b'

                    enShapeOne = pyOne.enormousShape
                    enShapeTwo = pyTwo.enormousShape

                    baseC = baseCopy.copy()
                    baseC = baseC.cut([enShapeTwo], _Py.tolerance)

                    gS = pyBase.geomShape
                    ff = self.selectFace(baseC.Faces, gS)
                    pyBase.shape = ff
                    cutList.append(ff)

                    if not pyTwo.virtualized:
                        # print 'bb'
                        gS = pyTwo.geomShape

                        f = shapeTwo.Faces[0]
                        f = self.cutting(f, [ff], gS)
                        fList = [f]

                        for f in shapeTwo.Faces[1:]:
                            f = f.cut([ff], _Py.tolerance)
                            fList.append(f.Faces[0])

                        # print 'fList ', fList
                        compound = Part.makeCompound(fList)
                        pyTwo.shape = compound

                    baseC = baseCopy.copy()
                    baseC = baseC.cut([enShapeOne], _Py.tolerance)

                    gS = pyCont.geomShape
                    ff = self.selectFace(baseC.Faces, gS)
                    pyCont.shape = ff
                    cutList.append(ff)

                    try:
                        for pyP in aligns[numChop+1:]:
                            pyP.angle = [pyCont.numWire, pyCont.numGeom]
                    except IndexError:
                        pass

                    pyCont.angle = pyBase.angle

                    if not pyOne.virtualized:
                        # print 'bbb'
                        gS = pyOne.geomShape

                        f = shapeOne.Faces[0]
                        f = self.cutting(f, [ff], gS)
                        fList = [f]

                        for f in shapeOne.Faces[1:]:
                            f = f.cut([ff], _Py.tolerance)
                            fList.append(f.Faces[0])

                        # print 'fList ', fList
                        compound = Part.makeCompound(fList)
                        pyOne.shape = compound

                    pyBase = aligns[numChop]

                for nn in rChop:
                    pyPl = pyPlList[nn]
                    if not pyPl.choped and not pyPl.aligned:
                        pl = pyPl.shape
                        if pl:
                            section = pl.section([base], _Py.tolerance)
                            if section.Edges:
                                gS = pyPl.geomShape
                                pl = self.cutting(pl, cutList, gS)
                                pyPl.shape = pl
                                # print 'rangoChop ', nn

    def end(self, pyPlaneList):

        ''''''

        # print '# self.Base ', self.base.numGeom

        rangoChopList = self.rango
        rangoChop = []
        for rC in rangoChopList:
            rangoChop.extend(rC)

        rangoRear = self.rangoRear

        chopList = []
        rearList = []

        for r in rangoChop:
            pyPl = pyPlaneList[r]
            if not pyPl.choped and not pyPl.aligned:
                pl = pyPl.shape
                chopList.append(pl)

        for r in rangoRear:
            pyPl = pyPlaneList[r]
            if not pyPl.choped and not pyPl.aligned:
                pl = pyPl.shape
                rearList.append(pl)

        if rearList and chopList:

            for r in rangoChop:
                pyPl = pyPlaneList[r]
                if not pyPl.choped and not pyPl.aligned:
                    pl = pyPl.shape
                    gS = pyPl.geomShape
                    pl = self.cutting(pl, rearList, gS)
                    pyPl.shape = pl

            for r in rangoRear:
                pyPl = pyPlaneList[r]
                if not pyPl.choped and not pyPl.aligned:
                    pl = pyPl.shape
                    gS = pyPl.geomShape
                    pl = self.cutting(pl, chopList, gS)
                    pyPl.shape = pl

    def rangging(self):

        '''rangging(self)
        '''

        pyWireList = _Py.pyFace.wires

        for [pyPlane, pyPl] in self.chops:

            pyWire = pyWireList[pyPlane.numWire]
            pyW = pyWireList[pyPl.numWire]

            pyPlane.rangging(pyWire, 'backward')
            pyPl.rangging(pyW, 'forward')

    def ranggingChop(self):

        '''ranggingChop(self)
        '''

        for [pyPlane, pyPl] in self.chops:
            [(w1, g1), (w2, g2)] =\
                [(pyPlane.numWire, pyPlane.numGeom),
                 (pyPl.numWire, pyPl.numGeom)]

            rangoChop = self.rang((w1, g1), (w2, g2))

            self.addValue('rango', rangoChop, 'backward')

    def rang(self, (w1, g1), (w2, g2)):

        ''''''

        pyWireList = _Py.pyFace.wires

        if w1 == w2:
            pyWire = pyWireList[w1]
            lenWire = len(pyWire.planes)
            if g1 > g2:
                ranA = range(g1+1, lenWire)
                ranB = range(0, g2)
                ran = ranA + ranB
            else:
                ran = range(g1+1, g2)
            rangoChop = ran

        else:
            rangoChop = []

        return rangoChop
