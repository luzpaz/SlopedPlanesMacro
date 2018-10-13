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


from SlopedPlanesPy import _Py


__title__ = "SlopedPlanes Macro"
__author__ = "Damian Caceres Moreno"
__url__ = "http://www.freecadweb.org"
__version__ = ""


class _PyEdge(_Py):

    '''The complementary python object class for edges.The edges of the base
    sketch are extruded to create the planes. This is a delagated class'''

    pass


class _PyEdgeLineSegment(_PyEdge):

    ''''''

    pass


class _PyEdgeCircle(_PyEdge):

    ''''''

    pass


class _PyEdgeArcOfCircle(_PyEdge):

    ''''''

    pass


class _PyEdgeEllipse(_PyEdge):

    ''''''

    pass


class _PyEdgeArcOfEllipse(_PyEdge):

    ''''''

    pass


class _PyEdgeParabola(_PyEdge):

    ''''''

    pass


class _PyEdgeArcOfParabola(_PyEdge):

    ''''''

    pass


class _PyEdgeHyperbola(_PyEdge):

    ''''''

    pass


class _PyEdgeArcOfHyperbola(_PyEdge):

    ''''''

    pass


class _PyEdgeBSplineCurve(_PyEdge):

    ''''''

    pass
