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

    '''The complementary python object class for alignments. An alignment
    is formed by two or more edges of the SlopedPlanes base which have
    the same direction. The edges could belong to different wires'''

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
        Virtualizes the chops which are aligned too, alignments and false
        alignments.
        Virtualizes the base of falsify alignnments which belongs to
        other alignment'''

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
        falsify = self.falsify
        tolerance = _Py.tolerance

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
        if w1 == w2:
            pyWire = pyWireList[w1]
            rangoRear = self.rang(pyWire, lat, pr, 'forward')
            # if rangoRear:
            rangoRear.insert(0, lat)
            rangoRear.append(pr)
        else:
            rangoRear = []
        self.rangoRear = rangoRear
        # print 'rangoRear ', rangoRear

        rangoChop = self.rango
        rangoCopy = rangoChop[:]
        chops = self.chops

        # rangoChop

        numChop = -1
        for rChop in rangoChop:
            numChop += 1

            [pyOne, pyTwo] = chops[numChop]

            # rango of the chops

            totalRango = []
            num = -1
            for pyPlane in [pyOne, pyTwo]:
                num += 1
                if num == 0:
                    rangoOne = pyPlane.rango[-1]
                    totalRango.extend(rangoOne)
                else:
                    rangoTwo = pyPlane.rango[0]
                    totalRango.extend(rangoTwo)

            # the two rangos don't cut between them

            nW = pyOne.numWire
            pyPlList = pyWireList[nW].planes

            if nW == pyTwo.numWire:

                for nG in rangoOne:
                    pyPl = pyPlList[nG]
                    control = pyPl.control
                    for r in rangoTwo:
                        if r not in control:
                            control.append(r)
                    # and opp Chop
                    r = pyTwo.numGeom
                    if r not in control:
                        control.append(r)

                for nG in rangoTwo:
                    pyPl = pyPlList[nG]
                    control = pyPl.control
                    for r in rangoOne:
                        if r not in control:
                            control.append(r)
                    # and opp chop
                    r = pyOne.numGeom
                    if r not in control:
                        control.append(r)

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
                    if w1 == nW:
                        for r in rangoRear:
                            if r not in control:
                                control.append(r)

                    # rChop is not cutted by alignment
                    control.append(numGeom)
                    if falsify:
                        control.append(nGeom)

                    # the aligment is not cutted by rChop
                    baseControl.append(nG)
                    if falsify:
                        pyCont.control.append(nG)

                    # pyOne and pyTwo don't cut rChop
                    pyOne.control.append(nG)
                    pyTwo.control.append(nG)

                    # rChop doesn't cut with other rChop
                    # chops doesn't cut with other rChop

                    num = -1
                    for rr in rangoCopy:
                        num += 1
                        if num != numChop:
                            [pyO, pyT] = chops[num]
                            if pyO.numWire == nW:
                                for nn in rr:
                                    pyOne.control.append(nn)
                                    pyTwo.control.append(nn)
                                    control.append(nn)

            # the rango of the chop are cutted by the chop,
            # and perhaps by the base or the continuation
            num = -1
            for pyPlane in [pyOne, pyTwo]:
                num += 1
                # print '### chop ', pyPlane.numWire, pyPlane.numGeom
                enormousShape = pyPlane.enormousShape

                # the cross
                notCross = True
                if num == 0:
                    rango = rangoOne
                    pyPlList = pyWireList[pyOne.numWire].planes
                    if pyPlane.virtualized:
                        if not pyPlane.geomAligned:
                            notCross = False
                else:
                    rango = rangoTwo
                    pyPlList = pyWireList[pyTwo.numWire].planes
                    if pyPlane.virtualized:
                        if pyPlane.geomAligned:
                            notCross = False
                # print 'notCross ', notCross
                # print 'rango ', rango

                for nG in rango:
                    pyPl = pyPlList[nG]
                    if pyPl.aligned or pyPl.choped:  # reflexed?
                        break
                    control = pyPl.control
                    if pyPlane.numGeom not in control:
                        if not pyPl.aligned and not pyPl.choped:
                            # print '# nG ', nG

                            if notCross:
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
                                baseControl.append(nG)

        if falsify:
            # the base and cont are cutted by a chop

            rC = Part.makeCompound(rC)

            section = rC.section([base], tolerance)

            if section.Edges:
                pyBase.cuttingPyth([pyTwo.enormousShape])
            else:
                pyBase.cuttingPyth([pyOne.enormousShape])

            section = rC.section([cont], tolerance)
            if section.Edges:
                pyCont.cuttingPyth([pyOne.enormousShape])
            else:
                pyCont.cuttingPyth([pyTwo.enormousShape])

            # TODO falseAlignment base and continuation don't cut opp rango ?

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
        enormousBase = pyBase.enormousShape
        control = pyBase.control

        pyCont = self.aligns[-1]
        nGeom = pyCont.numGeom
        cont = pyCont.shape
        bigCont = pyCont.bigShape
        enormousCont = pyCont.enormousShape

        pyPrior = self.prior
        pyLater = self.later
        prior = pyPrior.shape
        later = pyLater.shape
        pr = pyPrior.numGeom
        # print 'prior ', (pyPrior.numWire, pr)
        lat = pyLater.numGeom
        # print 'later ', (pyLater.numWire, lat)
        bigPrior = pyPrior.bigShape
        bigLater = pyLater.bigShape

        cutterList = []

        # arreglar

        if ((not pyPrior.reflexed) or
           (not pyPrior.rear) or
           (pyPrior.aligned)):
            # print '1'
            cutterList.append(bigPrior)
            if not pyBase.choped:
                # print '11'
                control.append(pr)

        if ((not pyLater.reflexed) or
           (not pyLater.rear) or
           (pyLater.aligned)):
            # print '2'
            cutterList.append(bigLater)
            if not self.falsify:
                if not pyBase.choped:
                    # print '21'
                    control.append(lat)

        if falsify:
            # print 'A'

            [pyOne, pyTwo] = self.chops[0]

            if not pyPrior.reflexed:

                pyBase.cuttingPyth([bigPrior])
                control.append(lat)

            if not pyLater.reflexed:

                pyCont.cuttingPyth([bigLater])
                pyCont.control.append(lat)
                pyCont.control.append(pr)

        else:
            # print 'B'

            if cutterList:
                # print 'BB'

                pyBase.cuttingPyth(cutterList)

        # cuts pyPrior and pyLater

        if not pyPrior.reflexed:  # or pyPrior.choped:
            # print 'a'

            if not pyPrior.arrow:
                # print 'a1'

                pyPrior.trimming(enormousBase)
                pyPrior.control.append(numGeom)

                if falsify:
                    # print 'a11'
                    pyPrior.control.append(nGeom)

        if not pyLater.reflexed:  # or pyLater.choped:
            # print 'b'

            if not pyLater.arrow:

                if not falsify:
                    # print 'b1'

                    pyLater.trimming(enormousBase)
                    pyLater.control.append(numGeom)

                else:
                    # print 'b2'

                    pyLater.trimming(enormousCont)
                    pyLater.control.append(nGeom)
                    pyLater.control.append(numGeom)

    def simulatingChops(self):

        ''''''

        tolerance = _Py.tolerance
        pyFace = _Py.pyFace
        face = pyFace.face
        pyWireList = pyFace.wires
        falsify = self.falsify

        rangoChop = self.rango
        simulatedChops = []

        geomList = [pyP.geomShape for pyP in self.aligns]
        geomList.insert(0, self.base.geomShape)

        enormousBase = self.base.enormousShape
        enormousCont = self.aligns[-1].enormousShape

        numChop = -1
        for [pyOne, pyTwo] in self.chops:
            numChop += 1

            if falsify:

                pyOne.simulating([enormousBase])
                pyTwo.simulating([enormousCont])

            else:

                pyOne.simulating([enormousBase])
                pyTwo.simulating([enormousBase])

            if pyOne.virtualized:
                pyO = self.selectPlane(pyOne.numWire, pyOne.numGeom)
                if pyO.shape:
                    pyO.simulating([enormousBase])

            if pyTwo.virtualized:
                pyT = self.selectPlane(pyTwo.numWire, pyTwo.numGeom)
                if pyT.shape:
                    if falsify:
                        pyT.simulating([enormousCont])
                    else:
                        pyT.simulating([enormousBase])

            rChop = rangoChop[numChop]

            pyW = pyWireList[pyOne.numWire]
            pyPlList = pyW.planes
            cutList = []
            for rr in rChop:
                pyPl = pyPlList[rr]
                if not pyPl.aligned and not pyPl.choped:
                    if pyPl.reflexed:
                        pl = pyPl.simulatedShape  # bigShape?
                    else:
                        pl = pyPl.bigShape
                        ## pl = pyPl.shape
                    cutList.append(pl)

            cList = []

            if cutList:

                bb = self.base.seedShape.copy()
                bb = bb.cut([pyOne.simulatedShape,
                             pyTwo.simulatedShape], tolerance)

                for ff in bb.Faces:
                    section = ff.section(geomList, tolerance)
                    if not section.Edges:
                        section = ff.section([face], tolerance)
                        if section.Edges:
                            bb = ff
                            break

                cL = Part.makeCompound(cutList)
                cL = cL.cut([pyOne.enormousShape,
                             pyTwo.enormousShape], tolerance)

                for ff in cL.Faces:
                    section = ff.section([bb], tolerance)
                    if section.Edges:
                        cList.append(ff)

                pyOne.simulating(cutList)
                pyTwo.simulating(cutList)

                pyOne.cuttingPyth(cutList)
                pyTwo.cuttingPyth(cutList)

                if pyOne.virtualized:
                    if pyO.shape:
                        pyO.cuttingPyth(cutList)
                        pyO.simulating(cutList)

                if pyTwo.virtualized:
                    if pyT.shape:
                        pyT.cuttingPyth(cutList)
                        pyT.simulating(cutList)

            simulatedChops.append(cList)

        self.simulatedChops = simulatedChops

    def simulatingAlignment(self):

        '''simulatingAlignment(self)'''

         # print '###### simulatingAlignment ', (self.base.numWire, self.base.numGeom)

        chops = self.chops
        simulatedChops = self.simulatedChops
        falsify = self.falsify

        pyBase = self.base
        base = pyBase.shape.copy()
        pyPrior = self.prior
        pyLater = self.later

        shapeList = []
        cutterList = []

        numChop = -1
        for [pyOne, pyTwo] in chops:
            numChop += 1

            simulC = simulatedChops[numChop]
            cutterList.extend(simulC)
            shapeList.extend(simulC)

            one = pyOne.simulatedShape.copy()
            two = pyTwo.simulatedShape.copy()

            if not falsify:

                enormousTwo = pyTwo.enormousShape
                gS = pyOne.geomShape
                one = self.cutting(one, [enormousTwo], gS)

                enormousOne = pyOne.enormousShape
                gS = pyTwo.geomShape
                two = self.cutting(two, [enormousOne], gS)

            cutterList.extend([one, two])
            shapeList.extend([one, two])

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

            shapeList.extend([base, cont])

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
            for ff in base.Faces:
                section = ff.section(geomList, _Py.tolerance)
                if section.Edges:
                    # print 'section'
                    shapeList.append(ff)
            # print 'shapeList ', shapeList

        self.simulatedAlignment = shapeList

    def aligning(self):

        '''aligning(self)
        '''

        # print '###### base ', (self.base.numWire, self.base.numGeom)
        # print '###### base shape ', self.base.shape
        #print '###### aligns ', [(x.numWire, x.numGeom) for x in self.aligns]
        # print '###### chops ', [[(x.numWire, x.numGeom), (y.numWire, y.numGeom)] for [x, y] in self.chops]

        tolerance = _Py.tolerance
        pyWireList = _Py.pyFace.wires
        pyPlaneList = pyWireList[0].planes

        falsify = self.falsify
        geomAligned = self.geomAligned

        pyBase = self.base
        base = pyBase.shape
        enormousBase = pyBase.enormousShape
        aligns = self.aligns
        rangoChop = self.rango
        simulatedChops = self.simulatedChops

        pyCont = aligns[-1]
        cont = pyCont.shape
        enormousCont = pyCont.enormousShape

        # the chops

        chopList = []
        numChop = -1
        for [pyOne, pyTwo] in self.chops:
            numChop += 1
            # print '### [pyOne, pyTwo]', [(pyOne.numWire, pyOne.numGeom), (pyTwo.numWire, pyTwo.numGeom)]

            rChop = rangoChop[numChop]

            simulatedC = simulatedChops[numChop]
            # print 'simulatedC ', simulatedC

            num = -1
            for pyPlane in [pyOne, pyTwo]:
                num += 1
                # print '# pyPlane ', (pyPlane.numWire, pyPlane.numGeom)
                gS = pyPlane.geomShape
                plane = pyPlane.shape
                control = pyPlane.control

                rear = None
                oppRear = None

                if num == 0:
                    rango = pyOne.rango[-1]
                    if pyOne.rear:
                        rear = pyOne.rear[-1]
                    oppRango = pyTwo.rango[0]
                    if pyTwo.rear:
                        oppRear = pyTwo.rear[0]
                    pyTwinPlane = pyTwo
                    cList = [enormousBase]
                    numWire = pyOne.numWire
                    pyWire = pyWireList[numWire]
                    pyPlaneList = pyWire.planes
                    nW = pyTwo.numWire
                    pyW = pyWireList[nW]
                    pyPlList = pyW.planes

                else:
                    rango = pyTwo.rango[0]
                    if pyTwo.rear:
                        rear = pyTwo.rear[0]
                    oppRango = pyOne.rango[-1]
                    if pyOne.rear:
                        oppRear = pyOne.rear[-1]
                    pyTwinPlane = pyOne
                    if falsify:
                        cList = [enormousCont]
                    else:
                        cList = [enormousBase]
                    numWire = pyTwo.numWire
                    pyWire = pyWireList[numWire]
                    pyPlaneList = pyWire.planes
                    nW = pyOne.numWire
                    pyW = pyWireList[nW]
                    pyPlList = pyW.planes

                cutList = []

                # REFACT!!!

                # rango

                rC = []
                for nn in rango:
                    if not nn in control:
                        pyPl = pyPlaneList[nn]
                        pl = None
                        if pyPl.aligned:
                            pyAli = self.selectAlignmentBase(numWire, nn)
                            if pyAli and pyAli != self:
                                geomAli = pyAli.geomAligned
                                section = geomAligned.section([geomAli], tolerance)
                                if not section.Vertexes:
                                    pl = pyAli.simulatedAlignment
                            else:
                                pl = None
                        elif not pyPl.choped:
                            rC.append(pyPl.shape)
                            pl = [pyPl.shape]
                        if pl:
                            if pl not in cutList:
                                cutList.extend(pl)
                                # print'rangoPlane ', nn
                # print 'rC ', rC
                rC = Part.makeCompound(rC)

                # oppRango

                for nn in oppRango:
                    if nn not in control:
                        pyPl = pyPlList[nn]
                        pl = None
                        if pyPl.aligned:
                            pyAli = self.selectAlignmentBase(numWire, nn)
                            if pyAli and pyAli != self:
                                geomAli = pyAli.geomAligned
                                section = geomAligned.section([geomAli], tolerance)
                                if not section.Vertexes:
                                    pl = pyAli.simulatedAlignment
                            else:
                                pl = None
                        elif not pyPl.choped:
                            pl = [pyPl.shape]
                        if pl:
                            if pl not in cutList:
                                cutList.extend(pl)
                                # print'oppRangoPlane ', nn

                if rear:

                    pyPl = pyPlaneList[rear]
                    pl = None
                    if pyPl.aligned:
                        pyAli = self.selectAlignmentBase(numWire, nn)
                        if pyAli and pyAli != self:
                            geomAli = pyAli.geomAligned
                            section = geomAligned.section([geomAli], tolerance)
                            if not section.Vertexes:
                                pl = pyAli.simulatedAlignment
                    elif not pyPl.choped:
                        pl = [pyPl.shape]
                    if pl:
                        if pl not in cutList:
                            cutList.extend(pl)
                            # print'rearPlane ', rear

                if oppRear:

                    if not oppRango:
                        pyPl = pyPlList[oppRear]
                        pl = None
                        if pyPl.aligned:
                            pyAli = self.selectAlignmentBase(numWire, nn)
                            if pyAli and pyAli != self:
                                geomAli = pyAli.geomAligned
                                section = geomAligned.section([geomAli], tolerance)
                                if not section.Vertexes:
                                    pl = pyAli.simulatedAlignment
                        elif not pyPl.choped:
                            pl = [pyPl.shape]
                        if pl:
                            if pl not in cutList:
                                cutList.extend(pl)
                                # print'oppRearPlane ', rear

                plane = pyPlane.shape
                planeCopy = plane.copy()

                cutterList = cutList + cList
                # print 'cutterList ', cutterList

                gS = pyPlane.geomShape
                planeCopy = planeCopy.cut(cutterList, tolerance)
                # print 'planeCopy.Faces ', planeCopy.Faces

                fList = []    # surplus under the figure
                for ff in planeCopy.Faces:
                    section = ff.section([gS], tolerance)
                    if not section.Edges:
                        section = ff.section([_Py.face], tolerance)
                        if section.Edges:
                            fList.append(ff)
                # print 'fList ', fList

                planeCopy = plane.copy()

                if fList:
                    planeCopy = planeCopy.cut(fList, tolerance)

                # print 'planeCopy.Faces ', planeCopy.Faces

                if cutList:

                    '''if pyPlane.numWire == 0 and pyTwinPlane.numWire != 0:
                        # debería ser mas selectivo ya que prodrian haber otros chops en el wire exterior
                        # puedes comprobarlo con self.aligns o con self.rango
                        rChop = rangoChop[numChop]
                        if not rChop:
                            falsePlane = _PyPlane(0, pyPlane.numGeom)
                            falsePlane.rear = pyPlane.rear
                            pyWire = pyWireList[0]
                            falsePlane.rangging(pyWire, 'backward')
                            rr = falsePlane.rango[-1]
                            # print rr
                            pyPlaneList = pyWire.planes
                            for nn in rr:
                                pyPl = pyPlaneList[nn]
                                if not pyPl.choped:
                                    if not pyPl.aligned:
                                        pl = pyPl.shape
                                        cutList.append(pl)
                                        # print 'rr ', nn'''

                    planeCopy = planeCopy.cut(cutList, tolerance)

                # print 'planeCopy.Faces ', planeCopy.Faces

                # main face
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
                # print 'aList ', aList

                # second face
                if rear:

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

                if num == 0:
                    rCOne = rC.copy()
                else:
                    rCTwo = rC.copy()

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
                    section = f.section([rCOne], tolerance)
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
                ff = ff.cut([shapeOne], tolerance)
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

            simulatedC = simulatedChops[0]

            cutterList.extend(simulatedC)

            if cutterList:

                base = pyBase.cuttingPyth(cutterList)
                cont = pyCont.cuttingPyth(cutterList)

            pyTwo.cuttingPyth([base, cont, shapeOne])
            pyOne.cuttingPyth([cont, base, shapeTwo])

            cutList = [cont, base]

            nW = pyOne.numWire
            pyW = pyWireList[nW]
            pyPlList = pyW.planes

            # rChop with base and cont
            for nn in rChop:
                pyPl = pyPlList[nn]
                if not pyPl.choped and not pyPl.aligned:
                    pyPl.cuttingPyth(cutList)
                    # print 'rangoChop ', nn

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

                simulatedC = simulatedChops[numChop]

                cutterList.extend(simulatedC)

                base = base.cut(cutterList, _Py.tolerance)
                # print 'base.Faces ', base.Faces, len(base.Faces)

                gA = self.geomAligned
                number = -1
                for ff in base.Faces:
                    section = ff.section([gA], tolerance)
                    if section.Edges:
                        number += 1
                # print 'number ', number

                if number <= 1:
                    # print 'a'

                    gS = pyBase.geomShape
                    base = self.selectFace(base.Faces, gS)
                    pyBase.shape = base
                    cutList.append(base)

                    shapeOne = pyOne.shape
                    fList = shapeOne.Faces
                    if len(fList) > 1:
                        ff = fList[1]
                        section = ff.section([base], tolerance)
                        if not section.Edges:
                            shapeOne = Part.makeCompound(fList[:1])
                            pyOne.shape = shapeOne

                    shapeTwo = pyTwo.shape
                    fList = shapeTwo.Faces
                    if len(fList) > 1:
                        ff = fList[1]
                        section = ff.section([base], tolerance)
                        if not section.Edges:
                            shapeTwo = Part.makeCompound(fList[:1])
                            pyTwo.shape = shapeTwo

                    ##cutList.extend([shapeOne, shapeTwo])

                else:
                    # print 'b'

                    gS = pyBase.geomShape
                    ff = self.selectFace(base.Faces, gS)
                    pyBase.shape = ff
                    cutList.append(ff)

                    gS = pyTwo.geomShape
                    f = shapeTwo.Faces[0]
                    f = self.cutting(f, [ff], gS)
                    fList = [f]
                    shapeTwo = Part.makeCompound(fList)
                    pyTwo.shape = shapeTwo
                    ##cutList.append(shapeTwo)

                    gS = pyCont.geomShape
                    ff = self.selectFace(base.Faces, gS)
                    pyCont.shape = ff
                    cutList.append(ff)

                    try:
                        for pyP in aligns[numChop + 1:]:
                            pyP.angle = [pyCont.numWire, pyCont.numGeom]
                    except IndexError:
                        pass

                    pyCont.angle = pyBase.angle

                    gS = pyOne.geomShape
                    f = shapeOne.Faces[0]
                    f = self.cutting(f, [ff], gS)
                    fList = [f]
                    shapeOne = Part.makeCompound(fList)
                    pyOne.shape = shapeOne
                    ##cutList.append(shapeOne)

                    pyBase = aligns[numChop]

                # rChop with base and cont
                for nn in rChop:
                    pyPl = pyPlList[nn]
                    if not pyPl.choped and not pyPl.aligned:
                        pyPl.cuttingPyth(cutList)
                        # print 'rangoChop ', nn

    def end(self):

        ''''''

        # print '# self.Base ', self.base.numGeom

        # recolects

        pyWireList = _Py.pyFace.wires
        pyBase = self.base
        base = pyBase.shape
        bList = [base]
        for pyPl in self.aligns:
            if pyPl.shape:
                bList.append(pyPl.shape)

        # chops

        rangoChop = self.rango
        numChop = -1
        for [pyOne, pyTwo] in self.chops:
            numChop += 1
            rChop = rangoChop[numChop]
            pyPlList = pyWireList[pyOne.numWire].planes
            # cutList = [pyOne.shape, pyTwo.shape]
            cutList = []
            pyO = self.selectPlane(pyOne.numWire, pyOne.numGeom)
            if pyO.shape:
                cutList.append(pyO.shape)
            pyT = self.selectPlane(pyTwo.numWire, pyTwo.numGeom)
            if pyT.shape:
                cutList.append(pyT.shape)

            # rangoChop with real chops

            if cutList:
                #rr = []
                for nn in rChop:
                    pyPl = pyPlList[nn]
                    if not pyPl.choped and not pyPl.aligned:
                        pyPl.cuttingPyth(cutList)
                        #rr.appeend(pyPl.shape)
                        # print 'rangoChop ', nn

            # rearChop with chop and alignment

            if pyO.rear:
                pyPlList = pyWireList[pyO.numWire].planes
                rOne = pyO.rear[-1]
                pyRearPl = pyPlList[rOne]
                if not pyRearPl.aligned and not pyRearPl.choped:
                    pyRearPl.cuttingPyth([pyO.shape] + bList)

                    two = pyT.shape
                    rango = pyO.rango[-1]
                    for nn in rango:
                        pyPl = pyPlList[nn]
                        if not pyPl.choped and not pyPl.aligned:
                            pyPl.cuttingPyth([two])

            if pyT.rear:
                pyPlList = pyWireList[pyT.numWire].planes
                rTwo = pyT.rear[0]
                pyRearPl = pyPlList[rTwo]
                if not pyRearPl.aligned and not pyRearPl.choped:
                    pyRearPl.cuttingPyth([pyT.shape] + bList)

                    one = pyO.shape
                    rango = pyT.rango[0]
                    for nn in rango:
                        pyPl = pyPlList[nn]
                        if not pyPl.choped and not pyPl.aligned:
                            pyPl.cuttingPyth([one])

        # rangoRear vs rangoChop

        chops = self.chops
        rangoChop = self.rango
        # print 'rangoChop ', rangoChop
        rangoRear = self.rangoRear
        # print 'rangoRear ', rangoRear
        w1 = self.prior.numWire
        pyPlaneList = _Py.pyFace.wires[w1].planes

        rearList = []

        for r in rangoRear:
            pyPl = pyPlaneList[r]
            if pyPl.choped or pyPl.aligned:
                break
            pl = pyPl.shape
            rearList.append(pl)

        if rearList:
            # print 'rearList ', rearList

            numChop = -1
            for rC in rangoChop:
                numChop += 1
                [pyOne, pyTwo] = chops[numChop]
                if pyOne.numWire == w1:

                    chopList = []
                    for r in rC:
                        pyPl = pyPlaneList[r]
                        if not pyPl.choped and not pyPl.aligned:
                            pl = pyPl.cuttingPyth(rearList)
                            chopList.append(pl)

                    if chopList:
                        # print 'chopList ', chopList
                        for r in rangoRear:
                            pyPl = pyPlaneList[r]
                            if not pyPl.choped and not pyPl.aligned:
                                pl = pyPl.cuttingPyth(chopList)

    def rangging(self, reset):

        '''rangging(self)
        '''

        pyWireList = _Py.pyFace.wires

        for [pyPlane, pyPl] in self.chops:

            numWire = pyPlane.numWire
            nWire = pyPl.numWire

            pyWire = pyWireList[numWire]
            pyW = pyWireList[nWire]

            if reset:

                if not pyPlane.rango:
                    pyPlane.rangging(pyWire, 'backward')
                if not pyPl.rango:
                    pyPl.rangging(pyW, 'forward')

            if numWire == nWire:
                numGeom = pyPlane.numGeom
                nGeom = pyPl.numGeom
                rangoChop = self.rang(pyWire, numGeom, nGeom, 'forward')
            else:
                rangoChop = []
            self.addValue('rango', rangoChop, 'backward')
