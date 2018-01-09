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

    '''The complementary python object class for alignments'''

    def __init__(self):

        ''''''

        self.base = None
        self.aligns = []
        self.chops = []
        self.rango = []
        self.falsify = False
        self.simulatedAlignment = []
        self.simulatedChop = []
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
    def rango(self):

        ''''''

        return self._rango

    @rango.setter
    def rango(self, rango):

        ''''''

        self._rango = rango

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
    def simulatedChop(self):

        ''''''

        return self._simulatedChop

    @simulatedChop.setter
    def simulatedChop(self, simulatedChop):

        ''''''

        self._simulatedChop = simulatedChop

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
        virtualizes the chops and the base of falsify alignnments'''

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
        The alignment blocks the progress
        of the planes in its front and laterals'''

        print '###### trimming base ', (self.base.numWire, self.base.numGeom)

        pyBase = self.base
        numGeom = pyBase.numGeom
        enormousBase = pyBase.enormousShape
        baseRear = pyBase.rear

        pyCont = self.aligns[-1]
        nGeom = pyCont.numGeom
        enormousCont = pyCont.enormousShape
        contRear = pyCont.rear

        pr = self.prior.numGeom
        lat = self.later.numGeom

        pyWireList = _Py.pyFace.wires
        pyWire = pyWireList[0]
        pyPlaneList = pyWire.planes

        rangoChop = self.rango
        copyRangoChop = rangoChop[:]
        chops = self.chops

        numChop = -1
        for rChop in rangoChop:
            numChop += 1

            [pyOne, pyTwo] = chops[numChop]

            pop = copyRangoChop.pop(numChop)
            restList = []
            for rC in copyRangoChop:
                restList.extend(rC)

            totalRango = []
            num = -1
            for pyPlane in chops[numChop]:
                num += 1
                if num == 0:
                    rRangoOne = pyPlane.rango[-1]
                    totalRango.extend(rRangoOne)
                else:
                    rRangoTwo = pyPlane.rango[0]
                    totalRango.extend(rRangoTwo)

            pyPlList = pyWireList[pyOne.numWire].planes

            # rChop: trimming bigShape
            for nG in rChop:
                pyPl = pyPlList[nG]
                if not pyPl.aligned:
                    bPl = pyPl.bigShape
                    gS = pyPl.geomShape
                    bPl = self.cutting(bPl, [enormousBase], gS)
                    pyPl.bigShape = bPl

                    # rChop doesn't cut with the two rangos
                    control = pyPl.control
                    for r in totalRango:
                        if r not in control:
                            control.append(r)

                    # rChop doesn't cut with other rChop
                    for r in restList:
                        if r not in control:
                            control.append(r)

                    # TODO rChop doesn't cut with other chop

            copyRangoChop.insert(numChop, pop)

            # TODO entre chops

            # the two rangos don't cut between them and rChop
            for nG in rRangoOne:
                pyPl = pyPlaneList[nG]
                control = pyPl.control
                for r in rRangoTwo:
                    if r not in control:
                        control.append(r)
                for r in rChop:
                    if r not in control:
                        control.append(r)
                r = pyTwo.numGeom
                if r not in control:
                    control.append(r)

            for nG in rRangoTwo:
                pyPl = pyPlaneList[nG]
                control = pyPl.control
                for r in rRangoOne:
                    if r not in control:
                        control.append(r)
                for r in rChop:
                    if r not in control:
                        control.append(r)
                r = pyOne.numGeom
                if r not in control:
                    control.append(r)

        falsify = self.falsify

        for [pyOne, pyTwo] in chops:

            num = -1
            for pyPlane in [pyOne, pyTwo]:
                num += 1
                print '### chop ', pyPlane.numWire, pyPlane.numGeom
                enShape = pyPlane.enormousShape

                cont = True
                if num == 0:
                    rango = pyPlane.rango[-1]
                    if pyPlane.virtualized:
                        if not pyPlane.geomAligned:
                            cont = False

                else:
                    rango = pyPlane.rango[0]
                    if pyPlane.virtualized:
                        if pyPlane.geomAligned:
                            cont = False

                print 'cont ', cont
                print 'rango ', rango

                # the rango's planes are cutted by the chop,
                # and perhaps by the base or the continuation

                for nG in rango:
                    pyPl = pyPlaneList[nG]
                    control = pyPl.control
                    if numGeom not in control:
                        if not pyPl.aligned and not pyPl.choped:
                            print '# nG ', nG

                            if cont:
                                print 'cont '
                                cList = [enShape]

                                if nG not in baseRear and nG not in contRear:
                                    print 'a'
                                    if nG not in [pr, lat]:
                                        print 'aa'

                                        if falsify:
                                            print 'aa1'
                                            if num == 0:
                                                print 'aa11'
                                                cList.append(enormousBase)
                                                control.append(numGeom)
                                            else:
                                                print 'aa12'
                                                cList.append(enormousCont)
                                                control.append(nGeom)

                                        else:
                                            print 'aa2'
                                            cList.append(enormousBase)
                                            control.append(numGeom)

                                pyPl.trimming(enShape, cList)
                                control.append(pyPlane.numGeom)

                            else:
                                print 'no cont'
                                pyPl.trimmingTwo(enShape)

                # the big chops are cutted by their rears

                if num == 0:
                    rear = pyPlane.rear[-1]
                else:
                    rear = pyPlane.rear[0]

                pyRear = pyPlaneList[rear]

                if pyRear.choped:
                    pass
                elif pyRear.aligned:
                    pyAlign = self.selectAlignment(0, pyRear.numGeom)
                    enBase = pyAlign.base.enormousShape

                    '''bPl = pyPlane.bigShape
                    gS = pyPlane.geomShape
                    bPl = self.cutting(bPl, [enBase], gS)
                    pyPlane.bigShape = bPl'''

                    ## pyPl.trimmingTwo(enBase)

                    pyPlane.trimming(enBase)

                elif pyRear.reflexed:
                    pass
                else:
                    pyPlane.trimming(pyRear.shape)

    def priorLater(self):

        '''priorLater(self)
        '''

        pyBase = self.base
        print '###### priorLater base ', (pyBase.numWire, pyBase.numGeom)

        numGeom = pyBase.numGeom
        base = pyBase.shape
        bigBase = pyBase.bigShape

        pyCont = self.aligns[-1]
        nGeom = pyCont.numGeom
        cont = pyCont.shape
        bigCont = pyCont.bigShape

        pyPrior = self.prior
        pyLater = self.later
        print 'pyPrior ', (pyPrior.numWire, pyPrior.numGeom)
        print 'pyLater ', (pyLater.numWire, pyLater.numGeom)
        prior = pyPrior.shape
        later = pyLater.shape
        pr = pyPrior.numGeom
        lat = pyLater.numGeom
        bigPrior = pyPrior.bigShape
        bigLater = pyLater.bigShape

        control = pyBase.control

        cutterList = []

        # podria ser mas fino con los falsos alieamientos, cutList. Con dos listas

        if ((not pyPrior.reflexed) or
           (pyPrior.choped and not pyPrior.aligned)):
            print '1'
            cutterList.append(bigPrior)
            if not pyBase.choped:
                print '11'
                control.append(pr)

        if ((not pyLater.reflexed) or
           (pyLater.choped and not pyLater.aligned)):
            print '2'
            cutterList.append(bigLater)
            if not pyBase.choped:
                print '21'
                control.append(lat)

        if not self.falsify:
            print 'A'

            if cutterList:
                print 'AA'
                gS = pyBase.geomShape
                base = self.cutting(base, cutterList, gS)
                pyBase.shape = base

        else:
            print 'B'

            [pyOne, pyTwo] = self.chops[0]
            print 'pyOne ', (pyOne.numWire, pyOne.numGeom)
            print 'pyTwo ', (pyTwo.numWire, pyTwo.numGeom)

            cList = [pyOne.bigShape] + cutterList

            gS = pyBase.geomShape
            base = self.cutting(base, cList, gS)
            control.append(pyOne.numGeom)

            pyBase.shape = base

            cList = [pyTwo.bigShape]
            pyAlignList = self.selectAllAlignment(pyCont.numWire,
                                                  nGeom)
            if len(pyAlignList) == 1:
                cList.extend(cutterList)
                pyCont.control.append(pr)
                control.append(lat)

            gS = pyCont.geomShape
            cont = self.cutting(cont, cList, gS)
            pyCont.control.append(pyTwo.numGeom)

            pyCont.shape = cont

        # cuts pyPrior and pyLater

        if not pyPrior.reflexed or pyPrior.choped:
            print 'a'

            if pyPrior.numWire == 0:
                print 'a1'

                # TODO cuando tengas arrow en dos direcciones podrás simplificar

                firstChop = self.chops[0][0]
                print 'firstChop.rango ', firstChop.rango

                if firstChop.rango[-1]:  # arrow?
                    print 'a11'

                    gS = pyPrior.geomShape
                    prior = self.cutting(prior, [bigBase], gS)
                    pyPrior.control.append(numGeom)
                    pyPrior.shape = prior

            else:
                print 'a2'

                gS = pyPrior.geomShape
                prior = self.cutting(prior, [bigBase], gS)
                pyPrior.control.append(numGeom)
                pyPrior.shape = prior

        if not pyLater.reflexed or pyLater.choped:
            print 'b'

            if pyLater.numWire == 0:
                print 'b1'

                lastChop = self.chops[-1][-1]
                print 'lastChop.rango ', lastChop.rango
                if lastChop.rango[0]:  # arrow?

                    if not self.falsify:
                        print 'b11'

                        gS = pyLater.geomShape
                        later = self.cutting(later, [bigBase], gS)
                        pyLater.control.append(numGeom)

                    else:
                        print 'b12'

                        gS = pyLater.geomShape
                        later = self.cutting(later, [bigCont], gS)
                        pyLater.control.append(nGeom)

                    pyLater.shape = later

            else:
                print 'b2'

                if not self.falsify:
                    print 'b21'

                    gS = pyLater.geomShape
                    later = self.cutting(later, [bigBase], gS)
                    pyLater.control.append(numGeom)

                else:
                    print 'b22'

                    gS = pyLater.geomShape
                    later = self.cutting(later, [bigCont], gS)
                    pyLater.control.append(nGeom)

                pyLater.shape = later

    def simulatingChop(self):

        '''simulatingChop(self)
        simulates the chops
        '''

        print '###### simulatingChop ', (self.base.numWire, self.base.numGeom)

        falsify = self.falsify
        simulatedChop = []
        rangoChop = self.rango
        pyWireList = _Py.pyFace.wires
        # pyWire = pyWireList[0]
        # pyPlaneList = pyWire.planes

        pyBase = self.base
        enormousBase = pyBase.enormousShape

        numChop = -1
        for [pyOne, pyTwo] in self.chops:
            numChop += 1

            # recolecta rangoChop

            pyPlList = pyWireList[pyOne.numWire].planes

            rChop = rangoChop[numChop]
            cutList = []
            for nn in rChop:
                pyPl = pyPlList[nn]
                if pyPl.choped or pyPl.aligned:
                    pass
                elif pyPl.reflexed:
                    cutList.append(pyPl.simulatedShape)
                else:
                    cutList.append(pyPl.shape)
                    if nn not in pyOne.control:
                        pyOne.control.append(nn)
                    if nn not in pyTwo.control:
                        pyTwo.control.append(nn)

            # cada chop es cortado por rangoChop

            enormous = pyTwo.enormousShape

            for pyPlane in [pyOne, pyTwo]:
                plane = pyPlane.shape
                gS = pyPlane.geomShape
                cutterList = cutList + [enormous]
                plane = self.cutting(plane, cutterList, gS)
                pyPlane.shape = plane

                enormous = pyOne.enormousShape

            if falsify:

                pyCont = self.aligns[-1]
                enormousCont = pyCont.enormousShape

                ffOne = pyOne.shape.copy()
                gS = pyOne.geomShape
                ffOne = self.cutting(ffOne, [enormousBase], gS)
                pyOne.simulating(enormousBase)

                ffTwo = pyTwo.shape.copy()
                gS = pyTwo.geomShape
                ffTwo = self.cutting(ffTwo, [enormousCont], gS)
                pyTwo.simulating(enormousCont)

            else:

                shapeOne = pyOne.shape.copy()
                gS = pyOne.geomShape
                ffOne = self.cutting(shapeOne, [enormousBase], gS)
                pyOne.simulating(enormousBase)

                shapeTwo = pyTwo.shape.copy()
                gS = pyTwo.geomShape
                ffTwo = self.cutting(shapeTwo, [enormousBase], gS)
                pyTwo.simulating(enormousBase)

            simulatedChop.append([ffOne, ffTwo])

        self.simulatedChop = simulatedChop

    def simulatingAlignment(self):

        '''simulatingAlignment(self)
        '''

        print '###### simulatingAlignment ', (self.base.numWire, self.base.numGeom)

        pyPlaneList = _Py.pyFace.wires[0].planes

        pyBase = self.base
        base = pyBase.shape.copy()
        print '###### base ', (pyBase.numWire, pyBase.numGeom)

        if self.falsify:

            pyCont = self.aligns[-1]
            cont = pyCont.shape.copy()

            [chopOne, chopTwo] = self.simulatedChop[0]

            # verificar cortes con prior y later y si no ejecutarlos simulados

            cList = [chopOne]
            if self.prior.numGeom not in pyBase.control:
                cList.append(self.prior.bigShape)
            gS = pyBase.geomShape
            base = self.cutting(base, cList, gS)

            cList = [chopTwo]
            if self.later.numGeom not in pyCont.control:
                cList.append(self.later.bigShape)
            gS = pyCont.geomShape
            cont = self.cutting(cont, cList, gS)

            shapeList = [base, cont]

        else:

            line = self.base.geomAligned

            chopList = self.chops

            # introduce los chops simulados y sus traseras

            cutterList = []
            numChop = -1
            for chop in self.simulatedChop:
                numChop += 1
                cutterList.extend(chop)

                [pyOne, pyTwo] = chopList[numChop]

                rearOne = pyOne.rear[-1]
                pyPl = pyPlaneList[rearOne]
                if pyPl.aligned:
                    print 'a'
                    pyAlign = self.selectAlignment(0, rearOne)
                    pyB = pyAlign.base
                    ll = pyB.geomAligned
                    section = line.section([ll], _Py.tolerance)
                    if not section.Vertexes:
                        print 'aa'
                        pl = pyB.enormousShape
                elif pyPl.reflexed:
                    print 'b'
                    pl = pyPl.simulatedShape
                else:
                    print 'c'
                    # pl = pyPl.shape
                    pl = pyPl.bigShape
                if pl:
                    cutterList.append(pl)
                    print 'rearOne ', rearOne

                rearTwo = pyTwo.rear[0]
                pyPl = pyPlaneList[rearTwo]
                if pyPl.aligned:
                    print 'a'
                    pyAlign = self.selectAlignment(0, rearTwo)
                    pyB = pyAlign.base
                    ll = pyB.geomAligned
                    section = line.section([ll], _Py.tolerance)
                    if not section.Vertexes:
                        print 'aa'
                        pl = pyB.enormousShape
                elif pyPl.reflexed:
                    print 'b'
                    pl = pyPl.simulatedShape
                else:
                    print 'c'
                    # pl = pyPl.shape
                    pl = pyPl.bigShape
                if pl:
                    cutterList.append(pl)
                    print 'rearTwo ', rearTwo

            pyPrior = self.prior
            pyLater = self.later

            # verificar cortes con prior y later y si no ejecutarlos simulados

            if pyPrior.numGeom not in pyBase.control:
                cutterList.append(pyPrior.bigShape)

            if pyLater.numGeom not in pyBase.control:
                cutterList.append(pyLater.bigShape)

            w1 = pyPrior.numWire
            w2 = pyLater.numWire
            if w1 == 0 and w2 == 0:
                g1 = pyPrior.numGeom
                g2 = pyLater.numGeom
                rearRango = self.rang((w2, g2), (w1, g1))

            print 'rearRango ', rearRango
            for nG in rearRango:
                pyPl = pyPlaneList[nG]
                if pyPl.aligned:
                    print 'a'
                    pyAlign = self.selectAlignment(0, nG)
                    pyB = pyAlign.base
                    ll = pyB.geomAligned
                    section = line.section([ll], _Py.tolerance)
                    if not section.Vertexes:
                        print 'aa'
                        pl = pyB.enormousShape
                elif pyPl.reflexed:
                    print 'b'
                    pl = pyPl.simulatedShape
                else:
                    print 'c'
                    # pl = pyPl.shape
                    pl = pyPl.bigShape
                if pl:
                    cutterList.append(pl)
                    print 'rearRango nG ', nG

            geomList = [pyP.geomShape for pyP in self.aligns]
            geomList.insert(0, pyBase.geomShape)

            print geomList

            base = base.cut(cutterList, _Py.tolerance)
            print 'base.Faces ', base.Faces
            shapeList = []
            for ff in base.Faces:
                section = ff.section(geomList, _Py.tolerance)
                if section.Edges:
                    print 'section'
                    shapeList.append(ff)
            print 'shapeList ', shapeList

        self.simulatedAlignment = shapeList

        # rangoChop es cortado por simulatedAlignment

        for rChop in self.rango:
            for nn in rChop:
                pyPl = pyPlaneList[nn]
                pl = pyPl.shape
                if pl:
                    gS = pyPl.geomShape
                    pl = self.cutting(pl, shapeList, gS)
                    pyPl.shape = pl
                    pyPl.control.append(pyBase.numGeom)

    def aligning(self):

        '''aligning(self)
        '''

        print '###### base ', (self.base.numWire, self.base.numGeom)
        print '###### base shape ', self.base.shape
        print '###### aligns ', [(x.numWire, x.numGeom) for x in self.aligns]
        print '###### chops ', [[(x.numWire, x.numGeom), (y.numWire, y.numGeom)] for [x, y] in self.chops]

        tolerance = _Py.tolerance

        pyWireList = _Py.pyFace.wires
        pyPlaneList = pyWireList[0].planes

        pyBase = self.base
        enormousBase = pyBase.enormousShape
        aligns = self.aligns
        rangoChopList = self.rango

        falsify = self.falsify

        pyCont = aligns[0]
        cont = pyCont.shape
        enormousCont = pyCont.enormousShape

        # elaborates the chops

        chopList = []
        numChop = -1
        for [pyOne, pyTwo] in self.chops:
            numChop += 1
            print[pyOne.numGeom, pyTwo.numGeom]

            rango = pyOne.rango[-1]
            rear = pyOne.rear[-1]

            cList = [enormousBase]

            num = -1
            for pyPlane in [pyOne, pyTwo]:
                num += 1
                print '# pyPlane ', pyPlane.numGeom

                cutList = []
                rC = []

                for nn in rango:
                    pyPl = pyPlaneList[nn]
                    if not pyPl.choped:
                        if not pyPl.aligned:
                            print 'a'
                            rangoPlane = pyPl.shape
                            cutList.append(rangoPlane)
                            rC.append(rangoPlane)
                            print'rango ', nn
                        else:
                            print 'b'
                            pyAlign = self.selectAlignment(0, nn)
                            cutList.extend(pyAlign.simulatedAlignment)
                            print'rango simulated', nn
                    else:
                        pass
                        # cutList.append(pyPl.simulatedShape)

                pyPl = pyPlaneList[rear]
                if not pyPl.choped:
                    if not pyPl.aligned:
                        print 'aa'
                        rearPlane = pyPl.shape
                        # if rearPlane not in cutList:
                        cutList.append(rearPlane)
                        print'rearPlane ', rear
                    else:
                        print 'bb'
                        pyAlign = self.selectAlignment(0, rear)
                        cutList.extend(pyAlign.simulatedAlignment)
                        print'rearPlane simulated', rear
                else:
                    pass
                    # cutList.append(pyPl.simulatedShape)

                rango = pyTwo.rango[0]
                rear = pyTwo.rear[0]

                rC = Part.makeCompound(rC)

                plane = pyPlane.shape
                planeCopy = plane.copy()

                cutterList = cutList + cList
                print 'cutterList ', cutterList

                if falsify:
                    cList = [enormousCont]

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

                    pyOppPlane = [pyOne, pyTwo][num-1]
                    if pyPlane.numWire == 0 and pyOppPlane.numWire != 0:
                        # debería ser mas selectivo ya que prodrian haber otros chops en el wire exterior
                        # puedes comprobarlo con self.aligns o con self.rango
                        rangoChop = rangoChopList[numChop]
                        if not rangoChop:
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

            chopList.append([pyOne, pyTwo])

        # elaborates the alignments

        if self.falsify:

            base = pyBase.shape

            rangoChop = rangoChopList[0]
            pyCont = aligns[0]

            [pyOne, pyTwo] = chopList[0]

            shapeOne = pyOne.shape
            shapeTwo = pyTwo.shape

            cutterList = [shapeOne, shapeTwo]

            for nn in rangoChop:

                nW = pyOne.numWire
                pyW = pyWireList[nW]
                pyPlList = pyW.planes

                pl = pyPlList[nn].shape
                if pl:
                    cutterList.append(pl)
                    # print 'rangoChop ', nn

            gS = pyBase.geomShape
            base = self.cutting(base, cutterList, gS)
            pyBase.shape = base

            if not pyTwo.virtualized:

                gS = pyTwo.geomShape
                shapeTwo = self.cutting(shapeTwo, [base, cont, shapeOne], gS)
                pyTwo.shape = shapeTwo

            gS = pyCont.geomShape
            cont = self.cutting(cont, cutterList, gS)
            pyCont.shape = cont

            if not pyOne.virtualized:

                gS = pyOne.geomShape
                shapeOne = self.cutting(shapeOne, [cont, base, shapeTwo], gS)
                pyOne.shape = shapeOne

        else:

            numChop = -1
            for pyCont in aligns:
                numChop += 1

                [pyOne, pyTwo] = chopList[numChop]
                rangoChop = rangoChopList[numChop]

                nW = pyOne.numWire
                pyW = pyWireList[nW]
                pyPlList = pyW.planes

                shapeOne = pyOne.shape
                shapeTwo = pyTwo.shape

                cutterList = [shapeOne, shapeTwo]

                for nn in rangoChop:
                    pl = pyPlList[nn].shape
                    if pl:
                        cutterList.append(pl)
                        # print 'rangoChop ', nn

                base = pyBase.shape
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

                else:
                    # print 'b'

                    enShapeOne = pyOne.enormousShape
                    enShapeTwo = pyTwo.enormousShape

                    baseC = baseCopy.copy()
                    baseC = baseC.cut([enShapeTwo], _Py.tolerance)

                    gS = pyBase.geomShape
                    ff = self.selectFace(baseC.Faces, gS)
                    pyBase.shape = ff

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

    def end(self, pyPlaneList):

        ''''''

        # print '# self.Base ', self.base.numGeom

        rangoChop = self.rango

        numChop = -1
        for chop in self.chops:
            numChop += 1
            rChop = rangoChop[numChop]
            # print 'rChop ', rChop

            [pyOne, pyTwo] = chop

            rangoOne = pyOne.rango[-1]
            # print 'rangoOne ', rangoOne
            rangoTwo = pyTwo.rango[0]
            # print 'rangoTwo ', rangoTwo

            rr = rangoOne + rangoTwo
            cutterList = []
            for r in rr:
                pyPl = pyPlaneList[r]
                pl = pyPl.shape
                if pl:
                    cutterList.append(pl)
            # print 'cutterList ', cutterList

            if cutterList:

                for nn in rChop:
                    pyPlane = pyPlaneList[nn]
                    plane = pyPlane.shape
                    if plane:
                        # print 'nn ', nn
                        plane = self.cutting(plane, cutterList, pyPlane.geomShape)
                        pyPlane.shape = plane

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
