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


__title__ = "SlopedPlanes Macro"
__author__ = "Damian Caceres Moreno"
__url__ = "http://www.freecadweb.org"


class _Py(object):

    ''''''

    def addLink(self, prop, obj):

        ''''''

        linkList = getattr(self, prop)
        if isinstance(obj, list):
            linkList.extend(obj)
        else:
            linkList.append(obj)
        setattr(self, prop, linkList)

    def addValue(self, prop, value, direction):

        ''''''

        valueList = getattr(self, prop)
        if direction == 'forward':
            valueList.insert(0, value)
        else:
            valueList.append(value)
        setattr(self, prop, valueList)

    def printSummary(self):

        ''''''

        print '********* wires ', self.wires
        for pyWire in self.wires:

            print '****** numWire ', pyWire.numWire
            print '*** reflexs ', pyWire.reflexs
            for pyReflex in pyWire.reflexs:

                print 'rangoInter ', pyReflex.rangoInter
                print 'planes ', pyReflex.planes
                for pyPlane in pyReflex.planes:
                    print pyPlane.numGeom,\
                        pyPlane.rear,\
                        pyPlane.rango, \
                        (pyPlane.forward.firstVertex(True).Point,
                         pyPlane.forward.lastVertex(True).Point)

        print '********* alignaments ', self.alignaments
        for pyAlignament in self.alignaments:

            print '****** base'
            print 'numWire ', pyAlignament.base.numWire
            print 'numGeom ', pyAlignament.base.numGeom
            print 'rear ', pyAlignament.base.rear
            print 'rango ',  pyAlignament.base.rango
            print 'geom ', pyAlignament.base.geom
            print 'geomAligned ', pyAlignament.base.geomAligned
            print 'falsify ', pyAlignament.falsify
            print 'rangoChop ', pyAlignament.rangoChop
            print 'prior ', pyAlignament.prior.numGeom
            print 'later ', pyAlignament.later.numGeom

            print '*** chops ', [[(x.numWire, x.numGeom),
                                  (y.numWire, y.numGeom)]
                                 for [x, y] in pyAlignament.chops]
            for chop in pyAlignament.chops:
                for pyPlane in chop:
                    print(pyPlane.numWire, pyPlane.numGeom), ' ',\
                        pyPlane.rear,\
                        pyPlane.rango

            print '*** aligns ', [x.numGeom for x in pyAlignament.aligns]
            for align in pyAlignament.aligns:
                print(align.numWire, align.numGeom),\
                    align.rear,\
                    align.rango,\
                    align.geom,\
                    align.geomAligned

        print '###############################################################'
