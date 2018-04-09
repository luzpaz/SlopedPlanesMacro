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


class _PyAlignment(_Py):

    '''The complementary python object class for alignments. An alignment
    is formed by two or more edges of the SlopedPlanes base which have
    the same direction. The edges could belong to different wires.'''

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
        other alignment.'''

        # print '###### virtualizing alignment', (self.base.numWire, self.base.numGeom)

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
        The alignment blocks the path to the planes
        in its front and laterals.'''

        # print '###### trimming base ', (self.base.numWire, self.base.numGeom)

        pyWireList = _Py.pyFace.wires
        falsify = self.falsify
        tolerance = _Py.tolerance

        geomAligned = self.geomAligned

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
        w1 = pyPrior.numWire

        rangoChop = self.rango
        rangoCopy = rangoChop[:]
        chops = self.chops
        rangoRear = self.rangoRear

        numChop = -1
        for rChop in rangoChop:
            numChop += 1
            # print '### numChop ', numChop

            [pyOne, pyTwo] = chops[numChop]
            rangoOne = pyOne.rango[-1][:]
            if pyOne.rear:
                rearOne = pyOne.rear[-1]
            else:
                rearOne = None
            rangoTwo = pyTwo.rango[0][:]
            if pyTwo.rear:
                rearTwo = pyTwo.rear[0]
            else:
                rearTwo = None

            for nn in rangoOne:
                if nn in rangoTwo:
                    rangoOne.remove(nn)
                    rangoTwo.remove(nn)

            # print 'rangoOne ', rangoOne
            # print 'rangoTwo ', rangoTwo

            nW = pyOne.numWire
            pyPlList = pyWireList[nW].planes
            rC = []

            if nW == pyTwo.numWire:

                # the two rangos don't cut between them, if not aligned

                for nG in rangoOne:
                    if nG is not rearTwo:
                        pyPl = pyPlList[nG]
                        control = pyPl.control
                        for r in rangoTwo:
                            if r not in control and r is not rearOne:
                                pyPr = pyPlList[r]
                                if not pyPr.aligned:
                                    control.append(r)
                        # and opp Chop
                        r = pyTwo.numGeom
                        if r not in control:
                            control.append(r)

                for nG in rangoTwo:
                    if nG is not rearOne:
                        pyPl = pyPlList[nG]
                        control = pyPl.control
                        for r in rangoOne:
                            if r not in control and r is not rearTwo:
                                pyPr = pyPlList[r]
                                if not pyPr.aligned:
                                    control.append(r)
                        # and opp chop
                        r = pyOne.numGeom
                        if r not in control:
                            control.append(r)

                # self.printControl(str(self.base.numGeom))

                # rChop: trimming bigShape

                if falsify:
                    cutList = [enormousBase, enormousCont]
                else:
                    cutList = [enormousBase]

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

                        # rChop doesn't cut with rangoRear and viceversa, if not aligned
                        if w1 == nW:
                            for r in rangoRear:
                                if r not in control:
                                    control.append(r)

                                pyPlR = pyPlList[r]
                                if not pyPlR.aligned:
                                    if nG not in pyPlR.control:
                                        pyPlR.control.append(nG)

                        # rChop is not cutted by alignment
                        control.append(numGeom)
                        if falsify:
                            control.append(nGeom)

                        # the aligment is not cutted by rChop
                        baseControl.append(nG)
                        if falsify:
                            pyCont.control.append(nG)

                        # pyOne and pyTwo don't cut rChop, if not reflexed
                        if not pyPl.reflexed:
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

                # self.printControl(str(self.base.numGeom))

            # the rango of the chop are cutted by the chop,
            # and perhaps by the base or the continuation
            num = -1
            for pyPlane in [pyOne, pyTwo]:
                num += 1
                # print '### chop ', (pyPlane.numWire, pyPlane.numGeom)
                enormousShape = pyPlane.enormousShape

                if num == 0:
                    rango = rangoOne
                    pyPlList = pyWireList[pyOne.numWire].planes
                else:
                    rango = rangoTwo
                    pyPlList = pyWireList[pyTwo.numWire].planes
                # print 'rango ', rango

                # the cross
                if pyPlane.virtualized:
                    aliList = self.selectAlignments(pyPlane.numWire,
                                                    pyPlane.numGeom)
                    for pyA in aliList:
                        gA = pyA.geomAligned.copy()
                        gA = gA.cut([geomAligned], tolerance)
                        if len(gA.Edges) == 2:
                            pyPlane.cross = True
                # print 'cross ', pyPlane.cross

                # consecutives
                consecutive = False
                for nG in rango:
                    pyPl = pyPlList[nG]
                    if pyPl.aligned or pyPl.choped:  # reflexed?
                        consecutive = True
                    control = pyPl.control
                    if pyPlane.numGeom not in control:
                        if not pyPl.aligned and not pyPl.choped:
                            # print '# nG ', nG

                            if not pyPlane.cross:
                                # print 'A'

                                if consecutive:

                                    pyPl.trimming(enormousShape)

                                else:

                                    cList = [enormousShape]

                                    if nG not in baseRear and\
                                       nG not in contRear:
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

            # TODO falseAlignment base and continuation don't cut opp rango ???
            # pero si con rear y entre rears

        # self.printControl(str(self.base.numGeom))

    def priorLater(self):

        '''priorLater(self)'''

        # print '###### priorLater base ', (self.base.numWire, self.base.numGeom)

        falsify = self.falsify

        pyBase = self.base
        numGeom = pyBase.numGeom
        enormousBase = pyBase.enormousShape
        control = pyBase.control

        pyCont = self.aligns[-1]
        nGeom = pyCont.numGeom
        enormousCont = pyCont.enormousShape

        pyPrior = self.prior
        pyLater = self.later
        pr = pyPrior.numGeom
        # print 'prior ', (pyPrior.numWire, pr)
        lat = pyLater.numGeom
        # print 'later ', (pyLater.numWire, lat)
        bigPrior = pyPrior.bigShape
        bigLater = pyLater.bigShape

        if falsify:
            # print 'A'

            [pyOne, pyTwo] = self.chops[0]

            if not pyPrior.reflexed:
                # print 'AP1'

                pyBase.cuttingPyth([bigPrior])
                control.append(lat)

            else:
                # print 'AP2'

                if pyBase.virtualized:
                    # print 'AP21'

                    pyBase.cuttingPyth([bigPrior])
                    control.append(lat)

            if not pyLater.reflexed:
                # print 'AL'

                pyCont.cuttingPyth([bigLater])
                pyCont.control.append(lat)
                pyCont.control.append(pr)

        else:
            # print 'B'

            cutterList = []

            if pyPrior.aligned:

                # print '10'
                pyA = self.selectAlignmentBase(pyPrior.numWire, pr)
                # print 'pyA.later ', pyA.later.numGeom
                if pyA and pyA.later.numGeom == numGeom:
                    # print '101'
                    cutterList.append(pyA.base.bigShape)
                    control.append(pr)

            elif ((not pyPrior.reflexed) or
                  (pyPrior.choped) or
                  (not pyPrior.rear)):

                # print '1'
                cutterList.append(bigPrior)
                if not pyBase.choped:
                    # print '11'
                    control.append(pr)

            if pyLater.aligned:

                # print '20'
                pyA = self.selectAlignmentBase(pyLater.numWire, lat)
                # print 'pyA.prior ', pyA.prior.numGeom
                if pyA and pyA.prior.numGeom == numGeom:
                    # print '201'
                    cutterList.append(pyA.base.bigShape)
                    control.append(lat)

            elif ((not pyLater.reflexed) or
                  (pyLater.choped) or
                  (not pyLater.rear)):

                # print '2'
                cutterList.append(bigLater)
                if not self.falsify:
                    if not pyBase.choped:
                        # print '21'
                        control.append(lat)

            if cutterList:
                # print 'BB'

                pyBase.cuttingPyth(cutterList)
                # print 'pyBase.shape ', pyBase.shape

        # cuts pyPrior and pyLater

        if not pyPrior.reflexed:
            # print 'a'

            if not pyPrior.arrow:
                # print 'a1'

                pyPrior.trimming(enormousBase)
                pyPrior.control.append(numGeom)
                # print 'pyPrior.shape ', pyPrior.shape

                if falsify:
                    # print 'a11'
                    pyPrior.control.append(nGeom)

        if not pyLater.reflexed:
            # print 'b'

            if not pyLater.arrow:

                if not falsify:
                    # print 'b1'

                    pyLater.trimming(enormousBase)
                    pyLater.control.append(numGeom)
                    # print 'pyLater.shape ', pyLater.shape

                else:
                    # print 'b2'

                    pyLater.trimming(enormousCont)
                    pyLater.control.append(nGeom)
                    pyLater.control.append(numGeom)
                    # print 'pyLater.shape ', pyLater.shape

    def simulatingChops(self):

        '''simulatingChops(self)'''

        # print '###### simulatingChops ', (self.base.numWire, self.base.numGeom, self.falsify)

        tolerance = _Py.tolerance
        pyFace = _Py.pyFace
        face = pyFace.face
        pyWireList = pyFace.wires
        falsify = self.falsify

        enormous = self.base.enormousShape

        rangoChop = self.rango
        simulatedChops = []

        geomList = [pyP.geomShape for pyP in self.aligns]
        geomList.insert(0, self.base.geomShape)

        enormousBase = self.base.enormousShape
        enormousCont = self.aligns[-1].enormousShape

        numChop = -1
        for [pyOne, pyTwo] in self.chops:
            numChop += 1
            # print '### chops ', (pyOne.numGeom, pyTwo.numGeom)

            enormousOne = pyOne.enormousShape
            enormousTwo = pyTwo.enormousShape

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
                        pl = pyPl.simulatedShape
                        cutList.append(pl)

                    else:
                        pl = pyPl.bigShape
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

        # print '###### simulatingAlignment ', (self.base.numWire, self.base.numGeom, self.falsify, self.base.virtualized)

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

        # print 'cutterList ', cutterList
        # print 'shapeList ', shapeList

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

            # print 'cutterList ', cutterList

            geomList = [pyP.geomShape for pyP in self.aligns]
            geomList.insert(0, pyBase.geomShape)
            # print geomList

            base = base.cut(cutterList, _Py.tolerance)
            # print 'base.Faces ', base.Faces, [f.Area for f in base.Faces]
            for ff in base.Faces:
                section = ff.section(geomList, _Py.tolerance)
                if section.Edges:
                    # print 'section'
                    shapeList.append(ff)

            # print 'shapeList ', shapeList

        self.simulatedAlignment = shapeList

    def aligning(self):

        '''aligning(self)'''

        # print '###### base ', (self.base.numWire, self.base.numGeom)

        pyFace = _Py.pyFace
        geomShapeFace = pyFace.shapeGeom

        tolerance = _Py.tolerance
        pyWireList = _Py.pyFace.wires

        falsify = self.falsify

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

            rangoOne = pyOne.rango[-1]
            # print 'rangoOne ', rangoOne
            numOne = pyOne.numWire
            pyWireOne = pyWireList[numOne]
            pyPlaneListOne = pyWireOne.planes
            if pyOne.rear:
                rearOne = pyOne.rear[-1]
                pyPlOne = pyPlaneListOne[rearOne]

            rangoTwo = pyTwo.rango[0]
            # print 'rangoTwo ', rangoTwo
            numTwo = pyTwo.numWire
            pyWireTwo = pyWireList[numTwo]
            pyPlaneListTwo = pyWireTwo.planes
            if pyTwo.rear:
                rearTwo = pyTwo.rear[0]
                pyPlTwo = pyPlaneListTwo[rearTwo]

            rCOne, cListOne, oppCListOne =\
                self.processRango(rangoOne, pyPlaneListOne, pyOne,
                                  numOne, enormousBase)
            # print rCOne, cListOne, oppCListOne

            rCTwo, cListTwo, oppCListTwo =\
                self.processRango(rangoTwo, pyPlaneListTwo, pyTwo,
                                  numTwo, enormousBase)
            # print rCTwo, cListTwo, oppCListTwo

            cutList = []

            if pyOne.rear:
                # print 'rearOne ', rearOne
                plOne = self.processRear(rearOne, pyPlOne, numOne)
                if plOne:
                    cutList.extend(plOne)
                    # print plOne
            if pyTwo.rear:
                # print 'rearTwo ', rearTwo
                plTwo = self.processRear(rearTwo, pyPlTwo, numTwo)
                if plTwo:
                    cutList.extend(plTwo)
                    # print plTwo

            if numTwo == numOne:
                if pyOne.rear and pyTwo.rear:
                    between = self.rang(pyWireOne, rearTwo, rearOne, 'forward')
                    # print 'between ', between
                    cList = self.processBetween(between, pyPlaneListOne)
                    cutList.extend(cList)
                    # print cList

            # print 'cutList ', cutList

            num = -1
            for pyPlane in [pyOne, pyTwo]:
                num += 1
                # print '# pyPlane ', (pyPlane.numWire, pyPlane.numGeom)
                gS = pyPlane.geomShape
                plane = pyPlane.shape

                ccList = cutList[:]

                if num == 0:
                    rC = rCOne
                    cList = [enormousBase]

                    ccList.extend(cListOne)
                    ccList.extend(oppCListTwo)

                else:
                    rC = rCTwo
                    if falsify:
                        cList = [enormousCont]
                    else:
                        cList = [enormousBase]

                    ccList.extend(cListTwo)
                    ccList.extend(oppCListOne)

                plane = pyPlane.shape
                planeCopy = plane.copy()

                if ccList:
                    planeCopy = planeCopy.cut(ccList, tolerance)
                    # print 'planeCopy.Faces ', planeCopy.Faces

                pCopy = planeCopy.copy()
                pCopy = pCopy.cut(cList, tolerance)

                fList = []    # surplus under the figure
                hList = []
                for ff in pCopy.Faces:
                    section = ff.section([gS], tolerance)
                    if not section.Edges:
                        section = ff.section([_Py.face], tolerance)
                        if section.Edges:
                            fList.append(ff)
                            section = ff.section(geomShapeFace, tolerance)
                            if not section.Edges:
                                hList.append(ff)
                # print 'fList ', fList

                if fList:
                    pyPlane.under = fList
                    planeCopy = planeCopy.cut(fList, tolerance)
                    # print 'planeCopy.Faces ', planeCopy.Faces

                if hList:

                    if pyPlane.virtualized and not pyPlane.cross:
                        # print 'virtualized plane ', (pyPlane.numWire, pyPlane.numGeom)
                        pyP = self.selectPlane(pyPlane.numWire,
                                               pyPlane.numGeom)

                        if isinstance(pyP.angle, list):
                            # print 'virt B'
                            angle = pyP.angle
                            pyp = self.selectPlane(angle[0], angle[1])
                            shape = pyp.shape
                            shape = shape.cut(hList, tolerance)
                            gList = []
                            for ff in shape.Faces:
                                section = ff.section(geomShapeFace, tolerance)
                                if section.Edges:
                                    gList.append(ff)
                            pyp.shape = Part.makeCompound(gList)

                        else:
                            # print 'virt A'
                            shape = pyP.shape
                            shape = shape.cut(hList, tolerance)
                            gList = []
                            for ff in shape.Faces:
                                section = ff.section(geomShapeFace, tolerance)
                                if section.Edges:
                                    gList.append(ff)
                            pyP.shape = Part.makeCompound(gList)

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
                if pyPlane.rear:

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
            # print 'AA'

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

                if pyBase.virtualized:
                    pyB = self.selectPlane(pyBase.numWire, pyBase.numGeom)
                    angle = pyB.angle
                    pyb = self.selectPlane(angle[0], angle[1])
                    pyb.cuttingPyth(cutterList)

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
            # print 'BB'

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

                    pyBase = aligns[numChop]

                # rChop with base and cont
                for nn in rChop:
                    pyPl = pyPlList[nn]
                    if not pyPl.choped and not pyPl.aligned:
                        pyPl.cuttingPyth(cutList)
                        # print 'rangoChop ', nn

    def processRango(self, rango, pyPlaneList, pyPlane, numWire, enormousBase):

        '''processRango(self, rango, pyPlaneList, pyPlane, numWire, enormousBase)'''

        control = pyPlane.control
        rC, cutList, oppCutList = [], [], []
        for nn in rango:
            # print 'nn ',nn
            if nn not in control:
                pyPl = pyPlaneList[nn]

                if pyPl.aligned:
                    # print 'a'

                    if not pyPlane.virtualized:
                        pyAli = self.selectAlignmentBase(numWire, nn)
                        if pyAli and pyAli != self:
                            pl = pyAli.simulatedAlignment
                            cutList.extend(pl)
                            oppCutList.extend(pl)

                elif not pyPl.choped:
                    # print 'b'

                    pl = pyPl.shape.copy()

                    if not pyPl.fronted:
                        oppCutList.append(pl)

                    if pyPl.arrow:
                        gShape = pyPl.geomShape
                        pl = self.cutting(pl, [enormousBase], gShape)

                    cutList.append(pl)
                    rC.append(pl)

        # print 'rC ', rC
        rC = Part.makeCompound(rC)

        # print 'cutList ', cutList
        # print 'oppCutList ', oppCutList
        return rC, cutList, oppCutList

    def processRear(self, rear, pyPl, numWire):

        '''processRear(self, rear, pyPl, numWire)'''

        pl = None

        if pyPl.aligned:
            # print 'r1'

            pyAli = self.selectAlignmentBase(numWire, rear)
            if pyAli and pyAli != self:
                # print 'pyAli ', pyAli.base.numGeom
                pl = pyAli.simulatedAlignment

        elif pyPl.fronted:
            # print 'r2'
            pl = [pyPl.bigShape]

        elif not pyPl.choped:
            # print 'r3'
            pl = [pyPl.shape]

        return pl

    def processBetween(self, rango, pyPlaneList):

        '''processBetween(self, rango, pyPlaneList)'''

        cutList = []
        for nn in rango:
            pyPl = pyPlaneList[nn]
            pl = None

            if pyPl.aligned:

                pl = None

            elif not pyPl.choped and not pyPl.fronted:

                pl = [pyPl.shape]

            if pl:
                cutList.extend(pl)
                # print 'rangoBetween ', nn

        return cutList

    def postProcess(self):

        '''postProcess(self)'''

        # print '# self.Base ', self.base.numGeom

        # recolects

        pyWireList = _Py.pyFace.wires
        pyBase = self.base
        base = pyBase.shape
        bList = [base]
        for pyPl in self.aligns:
            if pyPl.shape:
                bList.append(pyPl.shape)
        # print 'bList ', bList

        # chops

        rangoChop = self.rango
        numChop = -1
        for [pyOne, pyTwo] in self.chops:
            numChop += 1
            rChop = rangoChop[numChop]
            pyPlList = pyWireList[pyOne.numWire].planes

            cutList = []
            pyO = self.selectPlane(pyOne.numWire, pyOne.numGeom)
            if pyO.shape:
                cutList.append(pyO.shape)
            pyT = self.selectPlane(pyTwo.numWire, pyTwo.numGeom)
            if pyT.shape:
                cutList.append(pyT.shape)
            # print 'cutList ', cutList

            # rangoChop with real chops

            if cutList:
                for nn in rChop:
                    pyPl = pyPlList[nn]
                    if not pyPl.choped and not pyPl.aligned:
                        pyPl.cuttingPyth(cutList)
                        # print 'rangoChop ', nn

            # rearChop with chop and alignment. Rango and rear with opp chop

            if pyO.shape and pyO.rear:
                pyPlList = pyWireList[pyO.numWire].planes
                rOne = pyO.rear[-1]
                pyRearPl = pyPlList[rOne]
                if not pyRearPl.aligned and not pyRearPl.choped:
                    pyRearPl.cuttingPyth([pyO.shape] + bList)

                    two = pyT.shape
                    if two:
                        rango = pyO.rango[-1] + [rOne]
                        for nn in rango:
                            pyPl = pyPlList[nn]
                            if not pyPl.choped and not pyPl.aligned:
                                pyPl.cuttingPyth([two])

            if pyT.shape and pyT.rear:
                pyPlList = pyWireList[pyT.numWire].planes
                rTwo = pyT.rear[0]
                pyRearPl = pyPlList[rTwo]
                if not pyRearPl.aligned and not pyRearPl.choped:
                    pyRearPl.cuttingPyth([pyT.shape] + bList)

                    one = pyO.shape
                    if one:
                        rango = pyT.rango[0] + [rTwo]
                        for nn in rango:
                            pyPl = pyPlList[nn]
                            if not pyPl.choped and not pyPl.aligned:
                                pyPl.cuttingPyth([one])

            # between rears with chops

            if pyO.shape and pyO.rear and\
               pyT.shape and pyT.rear:
                pyWireOne = pyWireList[pyO.numWire]
                between = self.rang(pyWireOne, rTwo, rOne, 'forward')
                for nn in between:
                    pyPl = pyPlList[nn]
                    if not pyPl.choped and not pyPl.aligned:
                        pyPl.cuttingPyth(cutList)

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
            '''if pyPl.choped or pyPl.aligned:
                break'''
            # esto debería estar hecho desde el principio
            # if not (pyPl.choped or pyPl.aligned or pyPl.fronted): # fronted me rompe la cruz
            if not (pyPl.choped or pyPl.fronted) and pyPl.shape:

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
                            # if not pyPl.choped: # and not pyPl.aligned:
                            if not (pyPl.choped or pyPl.fronted):
                                pl = pyPl.cuttingPyth(chopList)

        # into rangoChop

        for rC in rangoChop:
            if len(rC) > 2:
                chopList = []
                planeList = []
                for r in rC:
                    pyPl = pyPlaneList[r]
                    if pyPl.choped or pyPl.aligned:
                        break
                    pl = pyPl.shape
                    chopList.append(pl.copy())
                    planeList.append(pyPl)

                num = -1
                for pyPl in planeList:
                    num += 1
                    pop = chopList.pop(num)
                    if chopList:
                        pyPl.cuttingPyth(chopList)
                    chopList.insert(num, pop)

        # alignment with choped rangoRear

        rearList = []
        for r in rangoRear:
            # print 'r ', r
            pyPl = pyPlaneList[r]
            if pyPl.choped:
                # print 'a'
                pl = pyPl.shape
                if pl:
                    rearList.append(pl)

        if rearList:
            # print 'rearList ', rearList
            pyBase.cuttingPyth(rearList)
            for pyPl in self.aligns:
                if pyPl.shape:
                    pyPl.cuttingPyth(rearList)

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

        # rangoRear

        pyPrior = self.prior
        pyLater = self.later
        pr = pyPrior.numGeom
        lat = pyLater.numGeom
        w1 = pyPrior.numWire
        w2 = pyLater.numWire

        if w1 == w2:
            pyWire = pyWireList[w1]
            rangoRear = self.rang(pyWire, lat, pr, 'forward')
            rangoRear.insert(0, lat)
            rangoRear.append(pr)

        else:
            rangoRear = []

        self.rangoRear = rangoRear
        # print 'rangoRear ', rangoRear
