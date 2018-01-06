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


class _PyAlignment(_Py):

    '''The complementary python object class for alignments'''

    def __init__(self):

        ''''''

        self.base = None
        self.aligns = []
        self.chops = []
        self.rango = []
        self.rearRango = []
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
    def rearRango(self):

        ''''''

        return self._rearRango

    @rearRango.setter
    def rearRango(self, rearRango):

        ''''''

        self._rearRango = rearRango

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

    def simulatingChop(self):

        '''simulatingChop(self)
        simulates the chops
        '''

        falsify = self.falsify
        simulatedChop = []

        for chop in self.chops:

            [pyOne, pyTwo] = chop

            if falsify:

                ffOne = pyOne.enormousShape
                ffTwo = pyTwo.enormousShape

            else:

                enormousShapeOne = pyOne.enormousShape
                enormousShapeTwo = pyTwo.enormousShape

                shapeOne = pyOne.shape.copy()
                cutterList = [enormousShapeTwo]
                gS = pyOne.geomShape
                ffOne = self.cutting(shapeOne, cutterList, gS)

                shapeTwo = pyTwo.shape.copy()
                cutterList = [enormousShapeOne]
                gS = pyTwo.geomShape
                ffTwo = self.cutting(shapeTwo, cutterList, gS)

            simulatedChop.append([ffOne, ffTwo])

        self.simulatedChop = simulatedChop

    def trimming(self):

        '''trimming(self)
        The alignment blocks the progress
        of the planes in its front and laterals'''

        # print '###### base ', (self.base.numWire, self.base.numGeom)
        pyWireList = _Py.pyFace.wires
        pyBase = self.base
        numGeom = pyBase.numGeom
        enormousShape = pyBase.enormousShape

        lastAli = self.aligns[-1]
        lastAliRear = lastAli.rear

        pyWire = pyWireList[0]
        pyPlaneList = pyWire.planes

        rangoChop = self.rango
        chops = self.chops

        numChop = -1
        for rr in rangoChop:
            numChop += 1
            for nG in rr:
                pyW = pyWireList[chops[numChop][0].numWire]
                pyPlList = pyW.planes
                pyPl = pyPlList[nG]
                if not pyPl.aligned:
                    bPl = pyPl.bigShape
                    gS = pyPl.geomShape
                    bPl = self.cutting(bPl, [enormousShape], gS)
                    pyPl.bigShape = bPl

        falsify = self.falsify

        rearRango = []
        numChop = -1
        for chop in chops:
            numChop += 1

            [pyOne, pyTwo] = chop

            num = -1
            for pyPlane in chop:
                num += 1
                # print '### chop ', pyPlane.numWire, pyPlane.numGeom
                enShape = pyPlane.enormousShape

                cont = True
                if num == 0:
                    if pyPlane.virtualized:
                        if not pyPlane.geomAligned:
                            cont = False
                else:
                    if pyPlane.virtualized:
                        if pyPlane.geomAligned:
                            cont = False
                #print 'cont ', cont

                # print 'rango ', pyPlane.rangoConsolidate
                for nG in pyPlane.rangoConsolidate:
                    if nG not in rangoChop[numChop]:
                        pyPl = pyPlaneList[nG]
                        if not pyPl.aligned and not pyPl.choped:
                            control = pyPl.control
                            # print '# nG ', nG

                            cList = [enShape]
                            if falsify:
                                # print 'a'
                                pass
                            else:
                                # print 'b'
                                if nG not in pyBase.rear:
                                    # print 'bb'
                                    if nG not in [self.prior.numGeom,
                                                  self.later.numGeom] and\
                                       nG not in lastAliRear:
                                        # print 'bbb'
                                        if numGeom not in control:
                                            # print 'bbbb'
                                            cList.append(enormousShape)
                                            if cont:
                                                control.append(numGeom)     # la base

                            if cont:
                                # print 'cont '
                                pyPl.trimming(enShape, cList)
                                control.append(pyPlane.numGeom)       # el chop

                            else:
                                # print 'no cont'
                                pyPl.trimmingTwo(enShape)

            if pyTwo.numWire == 0 and pyOne.numWire == 0:

                rearTwo = pyTwo.rear[0]
                # print 'rearTwo ', rearTwo
                rearOne =pyOne.rear[-1]
                # print 'rearOne ', rearOne

                rang =\
                    self.rang((pyTwo.numWire, rearTwo),
                              (pyOne.numWire, rearOne))

                rang.append(rearOne)
                if rearOne is not rearTwo:
                    rang.append(rearTwo)

            else:
                rang = []
            # print 'rang ', rang

            rearRango.append(rang)

            for rr in rang:
                # print 'rr ', rr
                pyPl = pyPlaneList[rr]
                for nn in rangoChop[numChop]:
                    pyP = pyPlaneList[nn]
                    if not pyP.reflexed:
                        # print 'nn ', nn
                        pyP.control.append(rr)
                        pyPl.control.append(nn)

        self.rearRango = rearRango
        # print 'rearRango ', rearRango

        # se podría ampliar el control con rangoChop y evitar más cortes innecesarios
        # rangoChop = self.rango

    def priorLater(self):

        '''priorLater(self)
        '''

        pyBase = self.base
        # print '###### base ', (pyBase.numWire, pyBase.numGeom)

        base = pyBase.shape
        bigBase = pyBase.bigShape

        pyCont = self.aligns[0]
        cont = pyCont.shape
        bigCont = pyCont.bigShape

        pyPrior = self.prior
        pyLater = self.later
        # print 'pyPrior ', (pyPrior.numWire, pyPrior.numGeom)
        # print 'pyLater ', (pyLater.numWire, pyLater.numGeom)
        prior = pyPrior.shape
        later = pyLater.shape
        bigPrior = pyPrior.bigShape
        bigLater = pyLater.bigShape

        cutterList = []

        if ((not pyPrior.reflexed) or
           (pyPrior.choped and not pyPrior.aligned)):
            # print '1'
            cutterList.append(bigPrior)
            pyBase.addValue('control', pyPrior.numGeom)

        if ((not pyLater.reflexed) or
           (pyLater.choped and not pyLater.aligned)):
            # print '2'
            cutterList.append(bigLater)
            pyBase.addValue('control', pyLater.numGeom)

        # cuts pyPrior and pyLater

        if not pyPrior.reflexed or pyPrior.choped:
            # print 'a'

            if pyPrior.numWire == 0:

                firstChop = self.chops[0][0]
                # print 'firstChop.rango ', firstChop.rango

                if firstChop.rango[0]:  # arrow?
                    # print 'aa'

                    gS = pyPrior.geomShape
                    prior = self.cutting(prior, [bigBase], gS)
                    pyPrior.addValue('control', pyBase.numGeom)

                    pyPrior.shape = prior

            else:   # interior wires always cut pyPrior and pyLater

                gS = pyPrior.geomShape
                prior = self.cutting(prior, [bigBase], gS)
                pyPrior.addValue('control', pyBase.numGeom)

                pyPrior.shape = prior

        if not pyLater.reflexed or pyLater.choped:
            # print 'b'

            if pyLater.numWire == 0:

                lastChop = self.chops[-1][-1]
                # print 'lastChop.rango ', lastChop.rango
                if lastChop.rango[-1]:
                    # print 'bb'

                    if not self.falsify:
                        # print 'bb1'

                        gS = pyLater.geomShape
                        later = self.cutting(later, [bigBase], gS)
                        pyLater.addValue('control', pyBase.numGeom)

                    else:
                        # print 'bb11'

                        gS = pyLater.geomShape
                        later = self.cutting(later, [bigCont], gS)
                        pyLater.addValue('control', pyCont.numGeom)

                    pyLater.shape = later

            else:

                if not self.falsify:
                    # print 'bb1'

                    gS = pyLater.geomShape
                    later = self.cutting(later, [bigBase], gS)
                    pyLater.addValue('control', pyBase.numGeom)

                else:
                    # print 'bb11'

                    gS = pyLater.geomShape
                    later = self.cutting(later, [bigCont], gS)
                    pyLater.addValue('control', pyCont.numGeom)

                pyLater.shape = later

        if not self.falsify:
            # print 'A'

            if cutterList:
                # print '3'
                gS = pyBase.geomShape
                base = self.cutting(base, cutterList, gS)
                pyBase.shape = base

        else:
            # print 'B'

            [pyOne, pyTwo] = self.chops[0]
            # print 'pyOne ', (pyOne.numWire, pyOne.numGeom)
            # print 'pyTwo ', (pyTwo.numWire, pyTwo.numGeom)

            cList = [pyOne.bigShape] + cutterList

            gS = pyBase.geomShape
            base = self.cutting(base, cList, gS)
            pyBase.addValue('control', pyOne.numGeom)

            pyBase.shape = base

            cList = [pyTwo.bigShape]
            pyAlignList = self.selectAllAlignment(pyCont.numWire,
                                                  pyCont.numGeom)
            if len(pyAlignList) == 1:
                cList.extend(cutterList)
                pyCont.addValue('control', pyPrior.numGeom)
                pyBase.addValue('control', pyLater.numGeom)

            gS = pyCont.geomShape
            cont = self.cutting(cont, cList, gS)
            pyCont.addValue('control', pyTwo.numGeom)

            pyCont.shape = cont

    def simulatingAlignment(self):

        '''simulatingAlignment(self)
        '''

        pyBase = self.base
        base = pyBase.shape.copy()
        print '###### base ', (pyBase.numWire, pyBase.numGeom)

        if self.falsify:

            base = [base]

            if isinstance(pyBase.angle, list):

                # print 'a'
                [alfa, beta] = pyBase.angle
                pyAli = self.selectAlignmentBase(alfa, beta)
                base = pyAli.simulatedAlignment

            pyCont = self.aligns[0]
            pyAli = self.selectAlignmentBase(pyCont.numWire, pyCont.numGeom)

            if pyAli:
                # print 'aa'
                cont = pyAli.simulatedAlignment.copy()

            else:
                # print 'bb'
                pyLater = self.later
                bigLater = pyLater.bigShape
                cont = pyCont.shape.copy()
                gS = pyCont.geomShape
                cont = self.cutting(cont, [bigLater], gS)
                cont = [cont]

            shapeList = cont + base

        else:

            enormousBase = pyBase.enormousShape
            chops = self.chops
            rango = self.rango

            simulatedChopList = self.simulatedChop
            pyPlaneList = _Py.pyFace.wires[0].planes

            chopList = []
            numChop = -1
            for [pyOne, pyTwo] in chops:
                numChop += 1

                rChop = rango[numChop]
                cList = []
                for nn in rChop:
                    pyPl = pyPlaneList[nn]
                    if not pyPl.choped:
                        pl = pyPl.shape
                        if pl:
                            cList.append(pl)
                            print 'rChop ', nn

                cutList = [enormousBase] + cList
                simulatedChop = simulatedChopList[numChop]

                chopOneCopy = simulatedChop[0].copy()
                gS = pyOne.geomShape
                chopOneCopy = self.cutting(chopOneCopy, cutList, gS)

                chopTwoCopy = simulatedChop[1].copy()
                gS = pyTwo.geomShape
                chopTwoCopy = self.cutting(chopTwoCopy, cutList, gS)

                chopList.extend([chopOneCopy, chopTwoCopy])

            lenChops = len(chops)
            num = lenChops / 2
            rest = lenChops % 2

            if rest == 0:
                numLeft = num - 1
                numRight = num

            else:
                numLeft = num
                numRight = num

            pyLeft = chops[numLeft][0]
            pyRight = chops[numRight][-1]

            rangoLeft = pyLeft.rangoConsolidate
            rangoRight = pyRight.rangoConsolidate
            rango = rangoLeft + rangoRight

            cutList = []
            for nn in rango:
                pyPl = pyPlaneList[nn]
                if not pyPl.choped:
                    if pyPl != pyBase:
                        if pyPl.reflexed:
                            pl = pyPl.simulatedShape
                        else:
                            # pl = pyPl.shape
                            pl = pyPl.bigShape
                        if pl:
                            cutList.append(pl)
                            print 'rango nn ', nn

            rearLeft = pyLeft.rear
            rearRight = pyRight.rear
            rear = rearLeft + rearRight

            for nn in rear:
                pyPl = pyPlaneList[nn]
                if not pyPl.choped:
                    pl = pyPl.shape
                    if pl:
                        cutList.append(pl)
                        print 'rear nn ', nn

            cutterList = chopList + cutList

            # it's yet included in rango
            '''limitList = []
            pyPrior = self.prior
            pyLater = self.later
            bigPrior = pyPrior.bigShape
            bigLater = pyLater.bigShape
            limitList.extend([bigPrior, bigLater])
            cutterList.extend(limitList)'''

            geomList = [pyP.geomShape for pyP in self.aligns]
            geomList.insert(0, pyBase.geomShape)

            base = base.cut(cutterList, _Py.tolerance)
            shapeList = []
            for ff in base.Faces:
                section = ff.section(geomList, _Py.tolerance)
                if section.Edges:
                    print 'a'
                    shapeList.append(ff)

        self.simulatedAlignment = shapeList

    def simulating(self):

        '''simulating(self)
        '''

        enormousShape = self.base.enormousShape

        for chop in self.chops:
            for pyPlane in chop:
                pyPlane.simulating(enormousShape)

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

        pyCont = aligns[0]
        cont = pyCont.shape
        enormousCont = pyCont.enormousShape

        # elaborates the chops

        chopList = []
        numChop = -1
        for [pyOne, pyTwo] in self.chops:
            numChop += 1

            print[pyOne.numGeom, pyTwo.numGeom]

            cutList = []
            rC = []  # podría ser necesario diferenciado para cada chop

            # introduces the rangoChop

            rangoChop = rangoChopList[numChop]

            nW = pyOne.numWire
            pyW = pyWireList[nW]
            pyPlList = pyW.planes

            for nn in rangoChop:
                pyPl = pyPlList[nn]
                if not pyPl.choped:
                    if not pyPl.aligned:
                        pl = pyPl.shape
                        cutList.append(pl)
                        print 'rangoChop ', nn

            # introduces the rangos and rears

            for pyPlane in [pyOne, pyTwo]:
                rango = pyPlane.rangoConsolidate
                for nn in rango:
                    pyPl = pyPlaneList[nn]
                    if not pyPl.choped:
                        if not pyPl.aligned:
                            rangoPlane = pyPl.shape
                            cutList.append(rangoPlane)
                            rC.append(rangoPlane)
                            print'rango ', nn

                rear = pyPlane.rear
                for nG in rear:
                    pyPl = pyPlaneList[nG]
                    if not pyPl.choped:
                        if not pyPl.aligned:
                            rearPlane = pyPl.shape
                            if rearPlane not in cutList:
                                cutList.append(rearPlane)
                                print'rearPlane ', nG

            rC = Part.makeCompound(rC)

            # cuts chops

            num = -1
            for pyPlane in [pyOne, pyTwo]:
                num += 1

                print '# pyPlane ', pyPlane.numGeom

                plane = pyPlane.shape
                planeCopy = plane.copy()

                if not self.falsify:
                    cList = [enormousBase]
                else:
                    if num == 0:
                        cList = [enormousBase]
                    else:
                        cList = [enormousCont]

                cutterList = cList + cutList

                gS = pyPlane.geomShape
                planeCopy = planeCopy.cut(cutterList, tolerance)
                print 'planeCopy.Faces ', planeCopy.Faces

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
                        if not rangoChop:
                            falsePlane = _PyPlane(0, pyPlane.numGeom)
                            falsePlane.rear = pyPlane.rear
                            pyWire = pyWireList[0]
                            falsePlane.rangging(pyWire, 'backward')
                            rr = falsePlane.rangoConsolidate
                            print rr

                            for nn in rr:
                                pyPl = pyPlaneList[nn]
                                if not pyPl.choped:
                                    if not pyPl.aligned:
                                        pl = pyPl.shape
                                        cutList.append(pl)
                                        print 'rr ', nn

                    planeCopy = planeCopy.cut(cutList, tolerance)
                print 'planeCopy.Faces ', planeCopy.Faces

                aList = []
                for ff in planeCopy.Faces:
                    print '1'
                    section = ff.section([gS], tolerance)
                    if section.Edges:
                        print '11'
                        aList.append(ff)
                        planeCopy = planeCopy.removeShape([ff])
                        break
                print 'planeCopy.Faces ', planeCopy.Faces

                if planeCopy.Faces:
                    planeCopy = planeCopy.cut(cList, tolerance)

                forward = pyPlane.forward
                backward = pyPlane.backward

                ffList = []
                for ff in planeCopy.Faces:
                    print '2'
                    section = ff.section([forward, backward], tolerance)
                    if not section.Edges:
                        print '21'
                        section = ff.section(aList, tolerance)
                        if not section.Vertexes:
                            print '211'
                            section = ff.section([rC], tolerance)
                            if section.Edges:
                                print '2111'
                                ffList.append(ff)
                                break

                aList.extend(ffList)
                print 'aList ', aList
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
                fList.append(ff.Faces[0])

            print 'fList ', fList
            compound = Part.makeCompound(fList)
            pyOne.shape = compound

            fList = []
            gS = pyTwo.geomShape
            ff = self.cutting(shapeTwo.Faces[0], [shapeOne], gS)
            fList.append(ff)

            for ff in shapeTwo.Faces[1:]:
                ff = ff.cut([shapeOne], _Py.tolerance)
                fList.append(ff.Faces[0])

            print 'fList ', fList
            compound = Part.makeCompound(fList)
            pyTwo.shape = compound

            chopList.append([pyOne, pyTwo])

        # elaborates the alignments

        if self.falsify:

            base = pyBase.shape

            rangoChop = rangoChopList[0]
            pyCont = aligns[0]

            [pyOne, pyTwo] = chopList[0]

            cutterList = [shapeOne, shapeTwo]

            for nn in rangoChop:

                nW = pyOne.numWire
                pyW = pyWireList[nW]
                pyPlList = pyW.planes

                pl = pyPlList[nn].shape
                if pl:
                    cutterList.append(pl)
                    print 'rangoChop ', nn

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
                        print 'rangoChop ', nn

                base = pyBase.shape
                base = base.cut(cutterList, _Py.tolerance)
                print 'base.Faces ', base.Faces

                number = 2
                if len(shapeOne.Faces) > 1 or len(shapeTwo.Faces) > 1:
                    number += 1
                print 'number ', number

                if len(base.Faces) == number:
                    print 'a'

                    gS = pyBase.geomShape
                    base = self.selectFace(base.Faces, gS)
                    pyBase.shape = base

                else:
                    print 'b'

                    gS = pyBase.geomShape
                    ff = self.selectFace(base.Faces, gS)
                    pyBase.shape = ff

                    if not pyTwo.virtualized:
                        print 'bb'
                        gS = pyTwo.geomShape

                        f = shapeTwo.Faces[0]
                        f = self.cutting(f, [ff], gS)
                        fList = [f]

                        for f in shapeTwo.Faces[1:]:
                            f = f.cut([ff], _Py.tolerance)
                            fList.append(f.Faces[0])

                        print 'fList ', fList
                        compound = Part.makeCompound(fList)
                        pyTwo.shape = compound

                    gS = pyCont.geomShape
                    ff = self.selectFace(base.Faces, gS)
                    pyCont.shape = ff

                    try:
                        for pyP in aligns[numChop+1:]:
                            pyP.angle = [pyCont.numWire, pyCont.numGeom]
                    except IndexError:
                        pass

                    pyCont.angle = pyBase.angle

                    if not pyOne.virtualized:
                        print 'bbb'
                        gS = pyOne.geomShape

                        f = shapeOne.Faces[0]
                        f = self.cutting(f, [ff], gS)
                        fList = [f]

                        for f in shapeOne.Faces[1:]:
                            f = f.cut([ff], _Py.tolerance)
                            fList.append(f.Faces[0])

                        print 'fList ', fList
                        compound = Part.makeCompound(fList)
                        pyOne.shape = compound

                    pyBase = aligns[numChop]

    def end(self, pyPlaneList):

        ''''''

        rearRango = self.rearRango
        rango = self.rango

        numChop = -1
        for chop in self.chops:
            numChop += 1
            rearRan = rearRango[numChop]
            # print 'rearRan ', rearRan

            ran = rango[numChop]
            # print 'ran ', ran
            for nn in ran:
                # print '### nn ', nn
                # solo los chops exteriores tienen rear
                pyPlane = pyPlaneList[nn]
                gS = pyPlane.geomShape

                for mm in rearRan:
                    if mm != nn:
                        # print '### mm ', mm
                        pyPl = pyPlaneList[mm]
                        pl = pyPl.shape
                        # print pl
                        plane = pyPlane.shape
                        # print plane

                        if pl and plane:

                            pl = self.cutting(pl, [plane], pyPl.geomShape)
                            pyPl.shape = pl

                            plane = self.cutting(plane, [pl], gS)
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
