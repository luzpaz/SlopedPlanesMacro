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


import SlopedPlanesUtils as utils
from SlopedPlanesPy import _Py
from SlopedPlanesPyPlane import _PyPlane


__title__ = "SlopedPlanes Macro"
__author__ = "Damian Caceres Moreno"
__url__ = "http://www.freecadweb.org"


class _PyAlignament(_Py):

    ''''''

    def __init__(self):

        ''''''

        self.base = None
        self.aligns = []
        self.chops = []
        self.rangoChop = []
        self.falsify = False
        self.simulatedShape = None
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
    def rangoChop(self):

        ''''''

        return self._rangoChop

    @rangoChop.setter
    def rangoChop(self, rangoChop):

        ''''''

        self._rangoChop = rangoChop

    @property
    def falsify(self):

        ''''''

        return self._falsify

    @falsify.setter
    def falsify(self, falsify):

        ''''''

        self._falsify = falsify

    @property
    def simulatedShape(self):

        ''''''

        return self._simulatedShape

    @simulatedShape.setter
    def simulatedShape(self, simulatedShape):

        ''''''

        self._simulatedShape = simulatedShape

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

    def trimming(self, pyFace, tolerance):

        ''''''

        pyWireList = pyFace.wires
        enormousShape = self.base.enormousShape
        numWire = self.base.numWire
        pyWire = pyWireList[numWire]

        rangoChop = self.rangoChop
        pyPlaneList = pyWire.planes

        for ran in rangoChop:
            for nG in ran:
                pyPl = pyPlaneList[nG]
                if not pyPl.aligned:

                    pyPl.trimming(enormousShape, tolerance)

        for chop in self.chops:

            for pyPlane in chop:

                enormousShape = pyPlane.enormousShape
                if enormousShape:
                    numWire = pyPlane.numWire
                    pyWire = pyWireList[numWire]
                    pyPlaneList = pyWire.planes

                    for rango in pyPlane.rango:
                        for nG in rango:
                            pyPl = pyPlaneList[nG]
                            if not pyPl.aligned:

                                pyPl.trimming(enormousShape, tolerance)

    def priorLater(self, pyFace, tolerance):

        ''''''

        pyBase = self.base
        base = pyBase.shape
        bigBase = pyBase.bigShape
        pyCont = self.aligns[0]
        cont = pyCont.shape
        bigCont = pyCont.bigShape

        pyPrior = self.prior
        pyLater = self.later
        prior = pyPrior.shape
        later = pyLater.shape
        bigPrior = pyPrior.bigShape
        bigLater = pyLater.bigShape

        cutterList = []

        if ((not pyPrior.reflexed) or
                (pyPrior.choped and not pyPrior.aligned)):
            # print '1'
            cutterList.append(bigPrior)

            prior = prior.cut([bigBase], tolerance)
            gS = pyPrior.geom.toShape()
            prior = utils.selectFace(prior.Faces, gS, tolerance)
            pyPrior.shape = prior

        if ((not pyLater.reflexed) or
                (pyLater.choped and not pyLater.aligned)):
            # print '2'
            cutterList.append(bigLater)

            if not self.falsify:

                later = later.cut([bigBase], tolerance)
                gS = pyLater.geom.toShape()
                later = utils.selectFace(later.Faces, gS, tolerance)

            else:

                later = later.cut([bigCont], tolerance)
                gS = pyLater.geom.toShape()
                later = utils.selectFace(later.Faces, gS, tolerance)

            pyLater.shape = later

        if not self.falsify:
            # print 'A'

            if cutterList:
                # print '3'
                base = base.cut(cutterList, tolerance)
                gS = pyBase.geom.toShape()
                base = utils.selectFace(base.Faces, gS, tolerance)
                pyBase.shape = base

        else:
            # print 'B'

            chops = self.chops
            [pyChopOne, pyChopTwo] = chops[0]

            # esto se repite en aligning y simulating
            if pyChopOne.aligned:
                chopOne = pyChopOne.shape
                if not chopOne:
                    [nWire, nGeom] = pyChopOne.angle
                    pyPlane = pyFace.selectPlane(nWire, nGeom)
                    chopOne = pyPlane.shape
                pyOne = _PyPlane(nWire, nGeom)
                pyOne.shape = chopOne.copy()
            else:
                pyOne = pyChopOne

            if pyChopTwo.aligned:
                chopTwo = pyChopTwo.shape
                if not chopTwo:
                    [nWire, nGeom] = pyChopTwo.angle
                    pyPlane = pyFace.selectPlane(nWire, nGeom)
                    chopTwo = pyPlane.shape
                pyTwo = _PyPlane(nWire, nGeom)
                pyTwo.shape = chopTwo.copy()
            else:
                pyTwo = pyChopTwo

            cList = [pyOne.shape] + cutterList

            base = base.cut(cList, tolerance)
            gS = pyBase.geom.toShape()
            base = utils.selectFace(base.Faces, gS, tolerance)
            pyBase.shape = base

            cList = [pyTwo.shape] + cutterList

            cont = cont.cut(cList, tolerance)
            gS = pyCont.geom.toShape()
            cont = utils.selectFace(cont.Faces, gS, tolerance)
            pyCont.shape = cont

    def simulating(self, pyFace, tolerance):

        ''''''

        # TODO primero tienes que hacer los alienamientos normales y luego los
        # falsos, ya que uno falso podría tener uno o dos alineamientos
        # verdaderos... (esto ya está hecho)
        # En este caso los verdaderos (uno o dos) no se incluirian
        # en ordinaries y between, y si el falso (esto falta)

        pyBase = self.base
        base = pyBase.shape.copy()
        enormousBase = pyBase.enormousShape
        # print(pyBase.numWire, pyBase.numGeom)

        chops = self.chops
        rangoChop = self.rangoChop
        pyWireList = pyFace.wires

        if not self.falsify:

            chopList = []
            numChop = -1
            for [pyChopOne, pyChopTwo] in chops:
                numChop += 1

                numWire = pyChopOne.numWire
                pyWire = pyWireList[numWire]
                pyPlaneList = pyWire.planes

                rChop = rangoChop[numChop]
                # print 'rChop ', rChop
                cList = []
                for nn in rChop:
                    pyPl = pyPlaneList[nn]
                    if not pyPl.choped:
                        pl = pyPl.shape
                        if pl:
                            cList.append(pl)

                # esto se repite en priorLater y aligning
                [nWire, nGeom] = [pyChopOne.numWire, pyChopOne.numGeom]
                chopOne = pyChopOne.shape
                enormousChopOne = pyChopOne.enormousShape
                if not chopOne:
                    [nWire, nGeom] = pyChopOne.angle
                    pyPlane = pyFace.selectPlane(nWire, nGeom)
                    chopOne = pyPlane.shape
                    enormousChopOne = pyPlane.enormousShape
                chopOneCopy = chopOne.copy()

                [nWire, nGeom] = [pyChopTwo.numWire, pyChopTwo.numGeom]
                chopTwo = pyChopTwo.shape
                enormousChopTwo = pyChopTwo.enormousShape
                if not chopTwo:
                    [nWire, nGeom] = pyChopTwo.angle
                    pyPlane = pyFace.selectPlane(nWire, nGeom)
                    chopTwo = pyPlane.shape
                    enormousChopTwo = pyPlane.enormousShape
                chopTwoCopy = chopTwo.copy()

                cutList = [enormousBase, enormousChopTwo] + cList

                chopOneCopy = chopOneCopy.cut(cutList, tolerance)
                gS = pyChopOne.geom.toShape()
                chopOneCopy = utils.selectFace(chopOneCopy.Faces, gS, tolerance)

                cutList = [enormousBase, enormousChopOne] + cList

                chopTwoCopy = chopTwoCopy.cut(cutList, tolerance)
                gS = pyChopTwo.geom.toShape()
                chopTwoCopy = utils.selectFace(chopTwoCopy.Faces, gS, tolerance)

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

            rangoLeft = pyLeft.rango
            rangoRight = pyRight.rango
            rango = rangoLeft + rangoRight

            cutList = []
            for ran in rango:
                for nn in ran:
                    pyPl = pyPlaneList[nn]
                    if not pyPl.choped:
                        if pyPl != pyBase:
                            pl = pyPl.shape
                            if pl:
                                cutList.append(pl)
                                # print 'rango nn ', nn

            rearLeft = pyLeft.rear
            rearRight = pyRight.rear
            rear = rearLeft + rearRight

            for nn in rear:
                pyPl = pyPlaneList[nn]
                if not pyPl.choped:
                    pl = pyPl.shape
                    if pl:
                        cutList.append(pl)
                        # print 'rear nn ', nn

            # print 'cutList ', cutList

            cutterList = chopList + cutList

            limitList = []
            pyPrior = self.prior
            pyLater = self.later
            bigPrior = pyPrior.bigShape
            bigLater = pyLater.bigShape
            limitList.extend([bigPrior, bigLater])
            cutterList.extend(limitList)

            geomList = [py.geom.toShape() for py in self.aligns]
            geomList.insert(0, pyBase.geom.toShape())

            base = base.cut(cutterList, tolerance)
            shapeList = []
            for ff in base.Faces:
                section = ff.section(geomList, tolerance)
                if section.Edges:
                    # print 'a'
                    shapeList.append(ff)

            # print 'shapeList ', shapeList

        else:

            pyCont = self.aligns[0]
            cont = pyCont.shape.copy()

            shapeList = [base, cont]

        self.simulatedShape = shapeList

    def aligning(self, face, pyFace, tolerance):

        ''''''

        '''print(self.base.numWire, self.base.numGeom)
        print[(x.numWire, x.numGeom) for x in self.aligns]
        print[[(x.numWire, x.numGeom), (y.numWire, y.numGeom)]
              for [x, y] in self.chops]'''

        pyBase = self.base
        base = pyBase.shape

        enormousBase = pyBase.enormousShape
        aligns = self.aligns
        chops = self.chops

        rangoChopList = self.rangoChop
        rangoChopList = self.rangoChop
        pyWireList = pyFace.wires

        pyCont = aligns[0]
        cont = pyCont.shape
        enormousCont = pyCont.enormousShape

        chopList = []

        numChop = -1
        for [pyChopOne, pyChopTwo] in self.chops:
            numChop += 1

            rangoChop = rangoChopList[numChop]

            # esto se repite en priorLater y somulating. Unificar y propiedad
            if pyChopOne.aligned:
                [nWire, nGeom] = [pyChopOne.numWire, pyChopOne.numGeom]
                chopOne = pyChopOne.shape
                if not chopOne:
                    [nWire, nGeom] = pyChopOne.angle
                    pyPlane = pyFace.selectPlane(nWire, nGeom)
                    chopOne = pyPlane.shape
                pyOne = _PyPlane(nWire, nGeom)
                pyOne.shape = chopOne.copy()
            else:
                pyOne = pyChopOne

            if pyChopTwo.aligned:
                [nWire, nGeom] = [pyChopTwo.numWire, pyChopTwo.numGeom]
                chopTwo = pyChopTwo.shape
                if not chopTwo:
                    [nWire, nGeom] = pyChopTwo.angle
                    pyPlane = pyFace.selectPlane(nWire, nGeom)
                    chopTwo = pyPlane.shape
                pyTwo = _PyPlane(nWire, nGeom)
                pyTwo.shape = chopTwo.copy()
            else:
                pyTwo = pyChopTwo

            nW = pyOne.numWire
            pyW = pyWireList[nW]
            pyPlaneList = pyW.planes

            cutList = []
            for nn in rangoChop:
                pyPl = pyPlaneList[nn]
                if not pyPl.choped:
                    if not pyPl.aligned:
                        pl = pyPl.shape
                        cutList.append(pl)
                        # print 'rangoChop ', nn

            num = -1
            for pyPlane in [pyOne, pyTwo]:
                num += 1

                # print '# chop ', pyPlane.numGeom

                cutterList = []

                nW = pyPlane.numWire
                pyW = pyWireList[nW]
                pyPlaneList = pyW.planes

                rear = pyPlane.rear
                for nG in rear:
                    pyPl = pyPlaneList[nG]
                    if not pyPl.choped:
                        if not pyPl.aligned:
                            rearPlane = pyPl.shape
                            cutterList.append(rearPlane)
                            # print 'rearPlane ', nG

                rango = pyPlane.rango
                for ran in rango:
                    for nn in ran:
                        pyPl = pyPlaneList[nn]
                        if not pyPl.choped:
                            if not pyPl.aligned:
                                rangoPlane = pyPl.shape
                                cutterList.append(rangoPlane)
                                # print 'rango ', nn

                cutterList.extend(cutList)

                if cutterList:
                    plane = pyPlane.shape
                    gS = [pyChopOne, pyChopTwo][num].geom.toShape()
                    plane = plane.cut(cutterList, tolerance)
                    plane = utils.selectFace(plane.Faces, gS, tolerance)
                    pyPlane.shape = plane

            num = -1
            for pyPlane in [pyOne, pyTwo]:
                num += 1

                plane = pyPlane.shape
                planeCopy = plane.copy()

                if not self.falsify:
                    cList = [enormousBase]
                else:
                    if num == 0:
                        cList = [enormousBase]
                    else:
                        cList = [enormousCont]

                gS = [pyChopOne, pyChopTwo][num].geom.toShape()
                planeCopy = planeCopy.cut(cList, tolerance)

                for ff in planeCopy.Faces:
                    section = ff.section([gS], tolerance)
                    if not section.Edges:
                        sect = ff.section([face], tolerance)
                        if sect.Edges:
                            planeCopy = ff
                            plane = plane.cut([planeCopy], tolerance)
                            plane = utils.selectFace(plane.Faces, gS, tolerance)
                            pyPlane.shape = plane
                            break

            shapeOne = pyOne.shape
            shapeTwo = pyTwo.shape

            cutterList = [shapeTwo]
            shapeOne = shapeOne.cut(cutterList, tolerance)
            geomShape = pyChopOne.geom.toShape()
            ff = utils.selectFace(shapeOne.Faces, geomShape, tolerance)
            pyOne.shape = ff

            cutterList = [shapeOne]
            shapeTwo = shapeTwo.cut(cutterList, tolerance)
            geomShape = pyChopTwo.geom.toShape()
            ff = utils.selectFace(shapeTwo.Faces, geomShape, tolerance)
            pyTwo.shape = ff

            chopList.append([pyOne, pyTwo])

        if not self.falsify:

            numChop = -1
            for pyCont in aligns:
                numChop += 1

                [pyChopOne, pyChopTwo] = chops[numChop]
                [pyOne, pyTwo] = chopList[numChop]
                rangoChop = rangoChopList[numChop]

                nW = pyChopOne.numWire
                pyW = pyWireList[nW]
                pyPlaneList = pyW.planes

                shapeOne = pyOne.shape
                shapeTwo = pyTwo.shape

                cutterList = [shapeOne, shapeTwo]

                for nn in rangoChop:
                    pl = pyPlaneList[nn].shape
                    if pl:
                        cutterList.append(pl)
                        # print 'rangoChop ', nn

                base = base.cut(cutterList, tolerance)

                if len(base.Faces) == 2:
                    # print 'a'

                    gS = pyBase.geom.toShape()
                    base = utils.selectFace(base.Faces, gS, tolerance)
                    pyBase.shape = base

                else:
                    # print 'b'

                    gS = pyBase.geom.toShape()
                    ff = utils.selectFace(base.Faces, gS, tolerance)
                    pyBase.shape = ff

                    gS = pyChopTwo.geom.toShape()
                    shapeTwo = shapeTwo.cut([ff], tolerance)
                    shapeTwo = utils.selectFace(shapeTwo.Faces, gS, tolerance)
                    pyTwo.shape = shapeTwo

                    gS = pyCont.geom.toShape()
                    ff = utils.selectFace(base.Faces, gS, tolerance)
                    pyCont.shape = ff

                    try:
                        for pyP in aligns[numChop+1:]:
                            pyP.angle = [pyCont.numWire, pyCont.numGeom]
                    except IndexError:
                        pass

                    pyCont.angle = pyBase.angle

                    gS = pyChopOne.geom.toShape()
                    shapeOne = shapeOne.cut([ff], tolerance)
                    shapeOne = utils.selectFace(shapeOne.Faces, gS, tolerance)
                    pyOne.shape = shapeOne

                    pyBase = aligns[numChop]

        else:

            rangoChop = rangoChopList[0]
            pyCont = aligns[0]

            [pyChopOne, pyChopTwo] = chops[0]
            [pyOne, pyTwo] = chopList[0]

            cutterList = [shapeOne, shapeTwo]

            for nn in rangoChop:
                pl = pyPlaneList[nn].shape
                if pl:
                    cutterList.append(pl)
                    # print 'rangoChop ', nn

            base = base.cut(cutterList, tolerance)
            gS = pyBase.geom.toShape()
            base = utils.selectFace(base.Faces, gS, tolerance)
            pyBase.shape = base

            cont = cont.cut(cutterList, tolerance)
            gS = pyCont.geom.toShape()
            cont = utils.selectFace(cont.Faces, gS, tolerance)
            pyCont.shape = cont

    def rangging(self, pyFace):

        ''''''

        pyWireList = pyFace.wires

        for [pyPlane, pyPl] in self.chops:

            pyWire = pyWireList[pyPlane.numWire]
            pyW = pyWireList[pyPl.numWire]

            pyPlane.rangging(pyWire, 'backward')
            pyPl.rangging(pyW, 'forward')

    def ranggingChop(self, pyFace):

        ''''''

        pyWireList = pyFace.wires

        for [pyPlane, pyPl] in self.chops:
            [(w1, g1), (w2, g2)] =\
                [(pyPlane.numWire, pyPlane.numGeom),
                 (pyPl.numWire, pyPl.numGeom)]

            # print[(w1, g1), (w2, g2)]

            if w1 == w2:
                # print '1'
                pyWire = pyWireList[w1]
                lenWire = len(pyWire.planes)
                if g1 > g2:
                    # print '11'
                    ranA = range(g1+1, lenWire)
                    ranB = range(0, g2)
                    ran = ranA + ranB
                else:
                    # print '12'
                    ran = range(g1+1, g2)
                rangoChop = ran

            else:
                # print '2'
                rangoChop = []

            self.addValue('rangoChop', rangoChop, 'backward')

        # print 'rangoChop ', self.rangoChop
