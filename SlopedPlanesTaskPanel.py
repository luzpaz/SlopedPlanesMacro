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


import math
import FreeCAD
import FreeCADGui
from PySide import QtGui, QtCore


__title__ = "SlopedPlanesMacro"
__author__ = "Damian Caceres"
__url__ = "http://www.freecadweb.org"
__version__ = ""


class _TaskPanel_SlopedPlanes():

    ''''''

    def __init__(self, slopedPlanes):

        ''''''

        self.updating = False
        self.obj = slopedPlanes
        self.shaping()

        form = QtGui.QWidget()
        self.form = form
        form.setObjectName("TaskPanel")
        form.setWindowTitle(self.obj.Label)

        grid = QtGui.QGridLayout(form)
        self.grid = grid
        grid.setObjectName("grid")

        title = QtGui.QLabel(form)
        self.title = title
        grid.addWidget(title, 0, 0, 1, 2)

        tree = _TreeWidget()
        self.tree = tree
        tree.setParent(form)
        grid.addWidget(tree, 1, 0, 1, 2)
        tree.itemChanged.connect(self.edit)

        advancedOptions = QtGui.QCheckBox(form)
        self.advancedOptions = advancedOptions
        advancedOptions.setObjectName("AdvancedOptions")
        grid.addWidget(advancedOptions, 2, 0, 1, 1)
        advancedOptions.clicked.connect(self.advanced)

        foot = QtGui.QLabel(form)
        self.foot = foot
        foot.setObjectName("foot")
        grid.addWidget(foot, 3, 0, 1, 2)

        FreeCADGui.Selection.addObserver(self)

    def retranslateUi(self):

        ''''''

        advancedOptions = self.advancedOptions
        advancedOptions.setText("Advanced Options")
        advancedOptions.setToolTip("More parameters to control the faces.")
        self.title.setText("SlopedPlanes parameters by faces")
        doc = ("Hint: Select a face over the figure and \n"
               "the related item in this task panel will be selected")
        self.foot.setText(doc)

        if advancedOptions.isChecked():
            self.tree.setHeaderLabels([("Face"),
                                       ("Angle"),
                                       ("Length"),
                                       ("Height"),
                                       ("Run"),
                                       ("Slope"),
                                       ("OverhangLength"),
                                       ("OverhangHeight"),
                                       ("OverhangRun"),
                                       ("Left Width"),
                                       ("Right Width"),
                                       ("Curves"),
                                       ("Sweep Curve"),
                                       ("Face")])

        else:
            self.tree.setHeaderLabels([("Face"),
                                       ("Angle")])

    def isAllowedAlterSelection(self):

        ''''''

        return False

    def isAllowedAlterView(self):

        ''''''

        return True

    def isAllowedAlterDocument(self):

        ''''''

        return False

    def getStandardButtons(self):

        ''''''

        return int(QtGui.QDialogButtonBox.Apply |
                   QtGui.QDialogButtonBox.Close |
                   QtGui.QDialogButtonBox.Ok)

    def clicked(self, button):

        ''''''

        if button == QtGui.QDialogButtonBox.Apply:

            placement = self.obj.Placement
            self.resetObject()
            self.obj.Placement = placement
            FreeCAD.ActiveDocument.recompute()
            self.update()
            self.shaping()

    def reject(self):

        ''''''

        FreeCADGui.Selection.removeObserver(self)
        FreeCADGui.ActiveDocument.resetEdit()
        return True

    def accept(self):

        ''''''

        FreeCADGui.Selection.removeObserver(self)
        self.resetObject()
        self.obj.touch()
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()
        return True

    def helpRequested(self):

        ''''''

        pass

    def edit(self, item, column):

        ''''''

        if not self.updating:
            self.resetObject()

    def advanced(self):

        ''''''

        tree = self.tree

        if self.advancedOptions.isChecked():

            tree.setColumnCount(14)
            tree.header().resizeSection(0, 60)
            tree.header().resizeSection(1, 120)
            tree.header().resizeSection(2, 120)
            tree.header().resizeSection(3, 120)
            tree.header().resizeSection(4, 120)
            tree.header().resizeSection(5, 130)
            tree.header().resizeSection(6, 130)
            tree.header().resizeSection(7, 130)
            tree.header().resizeSection(8, 120)
            tree.header().resizeSection(9, 120)
            tree.header().resizeSection(10, 120)
            tree.header().resizeSection(11, 60)
            tree.header().resizeSection(12, 180)
            tree.header().resizeSection(13, 60)

        else:

            tree.setColumnCount(2)
            tree.header().resizeSection(0, 60)
            tree.header().resizeSection(1, 60)

        self.update()

    def update(self):

        ''''''

        # print 'update'

        self.updating = True
        slopedPlanes = self.obj
        tree = self.tree
        tree.clear()
        tree.obj = slopedPlanes

        if slopedPlanes:

            linkList = [o.Name for o in slopedPlanes.SweepCurves]
            linkList.insert(0, None)
            up = slopedPlanes.Up
            down = slopedPlanes.Down
            pyFaceList = slopedPlanes.Proxy.Pyth
            numSlope = 0

            for pyFace in pyFaceList:
                originList = []
                pyWireList = pyFace.wires
                size = pyFace.size
                # print '### numFace ', pyFace.numFace

                lenWires = len(pyWireList)

                for pyWire in pyWireList:
                    numWire = pyWire.numWire
                    # print '## numWire ', numWire
                    pyPlaneList = pyWire.planes

                    if up:
                        if numWire == 1:
                            numSlope += 1

                    for pyPlane in pyPlaneList:

                        numAngle = pyPlane.numGeom
                        angle = pyPlane.angle
                        sweepCurve = pyPlane.sweepCurve
                        # print '# numAngle, angle ', (numAngle, angle)

                        # print 'originList ', originList

                        if [numWire, numAngle] not in originList and\
                           angle not in originList:

                            numSlope += 1

                            if isinstance(angle, float):
                                # print 'a'
                                originList.append([numWire, numAngle])

                            else:
                                # print 'b'
                                originList.append(angle)

                                pyW = pyWireList[angle[0]]
                                angle = pyW.planes[angle[1]].angle

                            # print 'NUMSLOPE ', numSlope

                            item = QtGui.QTreeWidgetItem(tree)
                            item.setText(0, str(numSlope))

                            doubleSpinBox = _DoubleSpinBox()
                            doubleSpinBox.setParent(tree)
                            doubleSpinBox.setToolTip("The angle of the related face")
                            doubleSpinBox.setMaximum(1000.00)
                            doubleSpinBox.setMinimum(-1000.00)
                            doubleSpinBox.setValue(angle)
                            deg = u"\u00b0"
                            doubleSpinBox.setSuffix(" " + deg)
                            tree.setItemWidget(item, 1, doubleSpinBox)

                            if self.advancedOptions.isChecked():

                                doubleSpinBox.item = item
                                doubleSpinBox.parent = tree
                                doubleSpinBox.valueChanged.connect(doubleSpinBox.changeAngle)

                                angle = math.radians(angle)

                                doubleSpinBox = _DoubleSpinBox()
                                doubleSpinBox.setParent(tree)
                                doubleSpinBox.setToolTip("The length of the related face")
                                doubleSpinBox.setMaximum(2000*size)
                                doubleSpinBox.setMinimum(-2000*size)
                                length = pyPlane.length
                                ll = FreeCAD.Units.Quantity(length,FreeCAD.Units.Length)
                                nn = ll.getUserPreferred()
                                value = length / nn[1]
                                suffix = ' ' + nn[2]
                                doubleSpinBox.setValue(value)
                                doubleSpinBox.setSuffix(suffix)
                                tree.setItemWidget(item, 2, doubleSpinBox)

                                doubleSpinBox.item = item
                                doubleSpinBox.parent = tree
                                doubleSpinBox.valueChanged.connect(doubleSpinBox.changeLength)

                                doubleSpinBox = _DoubleSpinBox()
                                doubleSpinBox.setParent(tree)
                                doubleSpinBox.setToolTip("The height of the related face")
                                doubleSpinBox.setMaximum(2000*size)
                                doubleSpinBox.setMinimum(-2000*size)
                                height = length * math.sin(angle)
                                ll = FreeCAD.Units.Quantity(height,FreeCAD.Units.Length)
                                nn = ll.getUserPreferred()
                                suffix = ' ' + nn[2]
                                value = height / nn[1]
                                doubleSpinBox.setValue(value)
                                doubleSpinBox.setSuffix(suffix)
                                tree.setItemWidget(item, 3, doubleSpinBox)

                                doubleSpinBox.item = item
                                doubleSpinBox.parent = tree
                                doubleSpinBox.valueChanged.connect(doubleSpinBox.changeHeight)

                                doubleSpinBox = _DoubleSpinBox()
                                doubleSpinBox.setParent(tree)
                                doubleSpinBox.setToolTip("The run of the related face")
                                doubleSpinBox.setMaximum(2000*size)
                                doubleSpinBox.setMinimum(-2000*size)
                                run = length * math.cos(angle)
                                ll = FreeCAD.Units.Quantity(run,FreeCAD.Units.Length)
                                nn = ll.getUserPreferred()
                                suffix = ' ' + nn[2]
                                value = run / nn[1]
                                doubleSpinBox.setValue(value)
                                doubleSpinBox.setSuffix(suffix)
                                tree.setItemWidget(item, 4, doubleSpinBox)

                                doubleSpinBox.item = item
                                doubleSpinBox.parent = tree
                                doubleSpinBox.valueChanged.connect(doubleSpinBox.changeRun)

                                doubleSpinBox = _DoubleSpinBox()
                                doubleSpinBox.setParent(tree)
                                doubleSpinBox.setToolTip("The slope of the related face")
                                doubleSpinBox.setMaximum(2000*size)
                                doubleSpinBox.setMinimum(-2000*size)
                                slope = 100 * math.tan(angle)
                                suffix = ' %'
                                doubleSpinBox.setValue(slope)
                                doubleSpinBox.setSuffix(suffix)
                                tree.setItemWidget(item, 5, doubleSpinBox)

                                doubleSpinBox.item = item
                                doubleSpinBox.parent = tree
                                doubleSpinBox.valueChanged.connect(doubleSpinBox.changeSlope)

                                doubleSpinBox = _DoubleSpinBox()
                                doubleSpinBox.setParent(tree)
                                doubleSpinBox.setToolTip("The overhang length of the related face")
                                doubleSpinBox.setMaximum(1000*size)
                                doubleSpinBox.setMinimum(-1000*size)
                                length = pyPlane.overhang
                                ll = FreeCAD.Units.Quantity(length,FreeCAD.Units.Length)
                                nn = ll.getUserPreferred()
                                suffix = ' ' + nn[2]
                                value = length / nn[1]
                                doubleSpinBox.setValue(value)
                                doubleSpinBox.setSuffix(suffix)
                                tree.setItemWidget(item, 6, doubleSpinBox)

                                doubleSpinBox.item = item
                                doubleSpinBox.parent = tree
                                doubleSpinBox.valueChanged.connect(doubleSpinBox.changeOverhangLength)

                                # TODO limit overhang with size

                                doubleSpinBox = _DoubleSpinBox()
                                doubleSpinBox.setParent(tree)
                                doubleSpinBox.setToolTip("The overhang height of the related face")
                                doubleSpinBox.setMaximum(1000*size)
                                doubleSpinBox.setMinimum(-1000*size)
                                height = length * math.sin(angle)
                                ll = FreeCAD.Units.Quantity(height,FreeCAD.Units.Length)
                                nn = ll.getUserPreferred()
                                suffix = ' ' + nn[2]
                                value = height / nn[1]
                                doubleSpinBox.setValue(value)
                                doubleSpinBox.setSuffix(suffix)
                                tree.setItemWidget(item, 7, doubleSpinBox)

                                doubleSpinBox.item = item
                                doubleSpinBox.parent = tree
                                doubleSpinBox.valueChanged.connect(doubleSpinBox.changeOverhangHeight)

                                doubleSpinBox = _DoubleSpinBox()
                                doubleSpinBox.setParent(tree)
                                doubleSpinBox.setToolTip("The overhang run of the related face")
                                doubleSpinBox.setMaximum(1000*size)
                                doubleSpinBox.setMinimum(-1000*size)
                                run = length * math.cos(angle)
                                ll = FreeCAD.Units.Quantity(run,FreeCAD.Units.Length)
                                nn = ll.getUserPreferred()
                                suffix = ' ' + nn[2]
                                value = run / nn[1]
                                doubleSpinBox.setValue(value)
                                doubleSpinBox.setSuffix(suffix)
                                tree.setItemWidget(item, 8, doubleSpinBox)

                                doubleSpinBox.item = item
                                doubleSpinBox.parent = tree
                                doubleSpinBox.valueChanged.connect(doubleSpinBox.changeOverhangRun)

                                doubleSpinBox = QtGui.QDoubleSpinBox(tree)
                                doubleSpinBox.setToolTip("The left width of the related face")
                                doubleSpinBox.setMaximum(1000*size)
                                doubleSpinBox.setMinimum(-1000*size)
                                leftWidth = pyPlane.leftWidth
                                ll = FreeCAD.Units.Quantity(leftWidth,FreeCAD.Units.Length)
                                nn = ll.getUserPreferred()
                                suffix = ' ' + nn[2]
                                value = leftWidth / nn[1]
                                doubleSpinBox.setValue(value)
                                doubleSpinBox.setSuffix(suffix)
                                tree.setItemWidget(item, 9, doubleSpinBox)

                                doubleSpinBox = QtGui.QDoubleSpinBox(tree)
                                doubleSpinBox.setToolTip("The right width of the related face")
                                doubleSpinBox.setMaximum(1000*size)
                                doubleSpinBox.setMinimum(-1000*size)
                                rightWidth = pyPlane.rightWidth
                                ll = FreeCAD.Units.Quantity(rightWidth,FreeCAD.Units.Length)
                                nn = ll.getUserPreferred()
                                suffix = ' ' + nn[2]
                                value = rightWidth / nn[1]
                                doubleSpinBox.setValue(value)
                                doubleSpinBox.setSuffix(suffix)
                                tree.setItemWidget(item, 10, doubleSpinBox)

                                button = _NewCurve()
                                button.setParent(tree)
                                button.plane = pyPlane
                                button.slopedPlanes = slopedPlanes
                                button.setText('New')
                                tree.setItemWidget(item, 11, button)
                                button.clicked.connect(button.onClicked)

                                combo = QtGui.QComboBox(tree)
                                combo.addItems(linkList)
                                try:
                                    index = linkList.index(sweepCurve)
                                    combo.setCurrentIndex(index)
                                except ValueError:
                                    combo.setCurrentIndex(0)
                                tree.setItemWidget(item, 12, combo)

                                button.combo = combo

                                item.setText(13, str(numSlope))

                if up:
                    if lenWires == 1:
                        numSlope += 1

                if down:
                    numSlope += 1

        self.retranslateUi()
        self.updating = False

    def resetObject(self):

        ''''''

        # print 'resetObject'

        slopedPlanes = self.obj
        up = slopedPlanes.Up
        down = slopedPlanes.Down
        pyFaceList = slopedPlanes.Proxy.Pyth
        numSlope = 0

        for pyFace in pyFaceList:
            originList = []
            # print '### numFace', pyFace.numFace
            pyFace.mono = True

            pyWireList = pyFace.wires
            lenWires = len(pyWireList)
            for pyWire in pyWireList:
                numWire = pyWire.numWire
                # print '## numWire', numWire
                pyWire.mono = True

                numAngle = -1
                pyPlaneList = pyWire.planes

                if up:
                    if numWire == 1:
                        numSlope += 1

                ang = pyPlaneList[0].angle
                # print(ang)

                for pyPlane in pyPlaneList:
                    numAngle += 1
                    angle = pyPlane.angle
                    # print('# numAngle ', numAngle, ' angle ', angle)

                    if [numWire, numAngle] not in originList and\
                       angle not in originList:

                        numSlope += 1

                        tree = self.tree

                        it = tree.findItems(str(numSlope),
                                            QtCore.Qt.MatchExactly, 0)[0]

                        doubleSpinBox = tree.itemWidget(it, 1)
                        value = doubleSpinBox.value()
                        # print 'value ', value
                        pyPlane.angle = value

                        if isinstance(angle, float):
                            # print('a')
                            originList.append([numWire, numAngle])

                            if value != ang:
                                pyWire.mono = False
                                pyFace.mono = False

                        else:
                            # print('b')
                            originList.append(angle)

                            pyPl = pyFace.wires[angle[0]].planes[angle[1]]
                            pyPl.angle = value

                        if self.advancedOptions.isChecked():

                            doubleSpinBox = tree.itemWidget(it, 2)
                            length = doubleSpinBox.value()
                            suffix = doubleSpinBox.suffix()
                            length = FreeCAD.Units.Quantity(str(length) + suffix)
                            pyPlane.length = length.Value

                            doubleSpinBox = tree.itemWidget(it, 6)
                            overhang = doubleSpinBox.value()
                            suffix = doubleSpinBox.suffix()
                            overhang = FreeCAD.Units.Quantity(str(overhang) + suffix)
                            pyPlane.overhang = overhang.Value

                            doubleSpinBox = tree.itemWidget(it, 9)
                            left = doubleSpinBox.value()
                            suffix = doubleSpinBox.suffix()
                            left = FreeCAD.Units.Quantity(str(left) + suffix)
                            pyPlane.leftWidth = left.Value

                            doubleSpinBox = tree.itemWidget(it, 10)
                            right = doubleSpinBox.value()
                            suffix = doubleSpinBox.suffix()
                            right = FreeCAD.Units.Quantity(str(right) + suffix)
                            pyPlane.rightWidth = right.Value

                            comboBox = tree.itemWidget(it, 12)
                            sweepCurve = comboBox.currentText()
                            pyPlane.sweepCurve = sweepCurve

                # print(pyWire.mono)

            if up:
                if lenWires == 1:
                    numSlope += 1

            if down:
                numSlope += 1

        slopedPlanes.Proxy.OnChanged = False

    def addSelection(self, doc, obj, sub, pnt=None):

        ''''''

        # print 'addSelection'
        # print(doc, obj, sub, pnt)

        reset = True
        slopedPlanes = self.obj
        shape = self.shape
        up = slopedPlanes.Up
        down = slopedPlanes.Down

        if doc == slopedPlanes.Document.Name:
            if obj == slopedPlanes.Name:
                if sub.startswith('Face'):

                    num = int(sub[4:]) - 1
                    # print '###### num ', num
                    ff = shape.Faces[num]
                    # print ff.Area, ff.BoundBox

                    bound = ff.BoundBox
                    if bound.ZMax == bound.ZMin:
                        # print 'reset'
                        self.tree.setCurrentItem(None)
                        return

                    numSlope = 0

                    for pyFace in slopedPlanes.Proxy.Pyth:
                        # print '###### numFace ', pyFace.numFace
                        if not reset:
                            break

                        originList = []

                        pyWireList = pyFace.wires
                        lenWires = len(pyWireList)

                        for pyWire in pyWireList:
                            # print '###### numWire ', pyWire.numWire
                            if not reset:
                                break

                            numWire = pyWire.numWire

                            if up:
                                if numWire == 1:
                                    numSlope += 1

                            for pyPlane in pyWire.planes:

                                numGeom = pyPlane.numGeom
                                angle = pyPlane.angle
                                # print '### numGeom, angle ', (numGeom, angle)
                                # print 'originList ', originList

                                if [numWire, numGeom] not in originList:

                                    if isinstance(angle, float):
                                        # print 'a'
                                        originList.append([numWire, numGeom])
                                        numSlope += 1

                                    else:
                                        if angle not in originList:
                                            # print 'b'
                                            originList.append(angle)
                                            numSlope += 1

                                # print 'NUMSLOPE ', numSlope

                                geomShape = pyPlane.geomShape
                                # print geomShape, geomShape.Curve, geomShape.firstVertex(True).Point, geomShape.lastVertex(True).Point
                                section = ff.section(geomShape) # false positive, OCCT bug, see above bound
                                # print section.Edges

                                if section.Edges:
                                    # print '# numGeom, numSlope ', (numGeom, numSlope)
                                    match = QtCore.Qt.MatchExactly
                                    item =\
                                        self.tree.findItems(str(numSlope),
                                                            match, 0)[0]
                                    self.tree.setCurrentItem(item)
                                    reset = False
                                    break

                        if up:
                            if lenWires == 1:
                                numSlope += 1

                        if down:
                            numSlope += 1

        if reset:
            # print 'reset'
            self.tree.setCurrentItem(None)

    def shaping(self):

        ''''''

        slopedPlanes = self.obj

        shape = slopedPlanes.Shape.copy()
        shape.Placement = FreeCAD.Placement()

        sketch = slopedPlanes.Base
        sketchBase = sketch.Placement.Base
        sketchAxis = sketch.Placement.Rotation.Axis
        sketchAngle = sketch.Placement.Rotation.Angle

        shape.rotate(sketchBase, sketchAxis, math.degrees(-1 * sketchAngle))
        shape.translate(-1 * sketchBase)

        self.shape = shape


class _TreeWidget(QtGui.QTreeWidget):

    ''''''

    def __init__(self):

        ''''''

        super(_TreeWidget, self).__init__()
        self.setColumnCount(2)
        self.header().resizeSection(0, 60)
        self.header().resizeSection(1, 60)


class _NewCurve(QtGui.QPushButton):

    ''''''

    def __init__(self):

        ''''''

        super(_NewCurve, self).__init__()

    def onClicked(self):

        ''''''

        # print 'onClicked _NewCurve'

        pyPlane = self.plane
        slopedPlanes = self.slopedPlanes
        pyPlane.makeSweepSketch(slopedPlanes)


class _DoubleSpinBox(QtGui.QDoubleSpinBox):

    ''''''

    def __init__(self):

        ''''''

        super(_DoubleSpinBox, self).__init__()

    def changeAngle(self, angle, aa=True, A=[]):

        ''''''

        # print '### changeAngle ', angle, aa, A

        if A:
            # print 'A'
            A.pop()
            return

        item = self.item
        tree = self.parent

        itemW = tree.itemWidget(item, 2)
        length = itemW.value()
        suffix = itemW.suffix()
        length = FreeCAD.Units.Quantity(str(length) + suffix)
        length = length.Value
        # print 'length ', length

        angle = math.radians(angle)
        # print 'angle ', angle

        height = self.height(angle, length)
        # print 'height ', height
        run = self.run(angle, length)
        # print 'run ', run
        tree.itemWidget(item, 3).changeHeight(height, False)
        tree.itemWidget(item, 4).changeRun(run, False)

        itemW = tree.itemWidget(item, 6)
        overhangLength = itemW.value()
        suffix = itemW.suffix()
        overhangLength = FreeCAD.Units.Quantity(str(overhangLength) + suffix)
        overhangLength = overhangLength.Value
        # print 'overhangLength ', overhangLength

        overhangHeight = self.height(angle, overhangLength)
        # print 'overhangHeight ', overhangHeight
        overhangRun = self.run(angle, overhangLength)
        # print 'overhangRun ', overhangRun
        tree.itemWidget(item, 7).changeOverhangHeight(overhangHeight, False)
        tree.itemWidget(item, 8).changeOverhangRun(overhangRun, False)

        if aa:
            # print 'aA'

            slope = 100 * math.tan(angle)
            # print 'slope ', slope
            suffix = ' %'
            tree.itemWidget(item, 5).changeSlope(slope, False)

        else:
            # print 'bA'

            deg = u"\u00b0"
            suffix = " " + deg
            # print 'suffix ', suffix
            # print 'slope ', slope
            angle = math.degrees(angle)
            A.append(angle)

            self.setValue(angle)
            self.setSuffix(suffix)

    def changeSlope(self, slope, ss=True, S=[]):

        ''''''

        # print '### changeSlope ',slope, ss, S

        if S:
            # print 'S'
            S.pop()
            return

        if ss:
            # print 'aS'

            item = self.item
            tree = self.parent

            angle = math.atan(slope / 100)
            angle = math.degrees(angle)
            # print 'angle ', angle
            tree.itemWidget(item, 1).changeAngle(angle, False)

        else:
            # print 'bS'

            suffix = ' %'
            # print 'suffix ', suffix
            # print 'slope ', slope
            S.append(slope)

            self.setValue(slope)
            self.setSuffix(suffix)

    def changeLength(self, length, ll=True, L=[]):

        ''''''

        # print '### changeLength ', length, ll, L

        if L:
            # print 'L'
            L.pop()
            return

        if ll:
            # print 'aL'

            suffix = self.suffix()
            # print 'suffix ', suffix
            # print 'length ', length
            length = FreeCAD.Units.Quantity(str(length) + suffix)

            item = self.item
            tree = self.parent

            angle = tree.itemWidget(item, 1).value()
            angle = math.radians(angle)

            length = length.Value
            # print 'length ', length

            height = self.height(angle, length)
            # print 'height ', height
            run = self.run(angle, length)
            # print 'run ', run
            tree.itemWidget(item, 3).changeHeight(height, False)
            tree.itemWidget(item, 4).changeRun(run, False)

        else:
            # print 'bL'

            suffix = 'mm'
            # print 'suffix ', suffix
            # print 'length ', length
            length = FreeCAD.Units.Quantity(str(length) + suffix)

            nn = length.getUserPreferred()
            # print nn
            length = length.Value
            # print 'length ', length
            value = length / nn[1]
            suffix = ' ' + nn[2]

            if round(value, 2) != self.value():
                L.append(length)

            self.setValue(value)
            self.setSuffix(suffix)

    def changeHeight(self, height, hh=True, H=[]):

        ''''''

        # print '### changeHeight ', height, hh, H

        if H:
            # print 'H'
            H.pop()
            return

        if hh:
            # print 'aH'

            suffix = self.suffix()
            # print 'suffix ', suffix
            # print 'height ', height
            height = FreeCAD.Units.Quantity(str(height) + suffix)

            item = self.item
            tree = self.parent

            angle = tree.itemWidget(item, 1).value()
            angle = math.radians(angle)

            height = height.Value
            # print 'height ', height

            length = self.lengthHeight(angle, height)
            # print 'length ', length
            run = self.run(angle, length)
            # print 'run ', run
            tree.itemWidget(item, 2).changeLength(length, False)
            tree.itemWidget(item, 4).changeRun(run, False)

        else:
            # print 'bH'

            suffix = 'mm'
            # print 'suffix ', suffix
            # print 'height ', height
            height = FreeCAD.Units.Quantity(str(height) + suffix)

            nn = height.getUserPreferred()
            # print nn
            height = height.Value
            # print 'height ', height
            value = height / nn[1]
            suffix = ' ' + nn[2]

            if round(value, 2) != self.value():
                H.append(height)

            self.setValue(value)
            self.setSuffix(suffix)

    def changeRun(self, run, rr=True, R=[]):

        ''''''

        # print '### changeRun ', run, rr, R

        if R:
            # print 'R'
            R.pop()
            return

        if rr:
            # print 'aR'

            suffix = self.suffix()
            # print 'suffix ', suffix
            # print 'run ', run
            run = FreeCAD.Units.Quantity(str(run) + suffix)

            item = self.item
            tree = self.parent

            angle = tree.itemWidget(item, 1).value()
            angle = math.radians(angle)

            run = run.Value
            # print 'run ', run

            length = self.lengthRun(angle, run)
            # print 'length ', length
            height = self.height(angle, length)
            # print 'height ', height
            tree.itemWidget(item, 2).changeLength(length, False)
            tree.itemWidget(item, 3).changeHeight(height, False)

        else:
            # print 'bR'

            suffix = 'mm'
            # print 'suffix ', suffix
            # print 'run ', run
            run = FreeCAD.Units.Quantity(str(run) + suffix)

            nn = run.getUserPreferred()
            # print nn
            run = run.Value
            # print 'run ', run

            value = run / nn[1]
            suffix = ' ' + nn[2]

            if round(value, 2) != self.value():
                R.append(run)

            self.setValue(value)
            self.setSuffix(suffix)

    def changeOverhangLength(self, overhangLength, lo=True, LO=[]):

        ''''''

        # print '### changeOverhangLength ', overhangLength, lo, LO

        if LO:
            # print 'LO'
            LO.pop()
            return

        if lo:
            # print 'aLO'

            suffix = self.suffix()
            # print 'suffix ', suffix
            # print 'overhangLength ', overhangLength
            overhangLength =\
                FreeCAD.Units.Quantity(str(overhangLength) + suffix)

            item = self.item
            tree = self.parent

            angle = tree.itemWidget(item, 1).value()
            angle = math.radians(angle)

            overhangLength = overhangLength.Value
            # print 'overhangLength ', overhangLength

            overhangHeight = self.height(angle, overhangLength)
            # print 'overhangHeight ', overhangHeight
            overhangRun = self.run(angle, overhangLength)
            # print 'overhangRun ', overhangRun
            tree.itemWidget(item, 7).changeOverhangHeight(overhangHeight, False)
            tree.itemWidget(item, 8).changeOverhangRun(overhangRun, False)

        else:
            # print 'bLO'

            suffix = 'mm'
            # print 'suffix ', suffix
            # print 'overhangLength ', overhangLength
            overhangLength =\
                FreeCAD.Units.Quantity(str(overhangLength) + suffix)

            nn = overhangLength.getUserPreferred()
            # print nn
            overhangLength = overhangLength.Value
            # print 'overhangLength ', overhangLength
            value = overhangLength / nn[1]
            suffix = ' ' + nn[2]

            if round(value, 2) != self.value():
                LO.append(overhangLength)

            self.setValue(value)
            self.setSuffix(suffix)

    def changeOverhangHeight(self, overhangHeight, ho=True, HO=[]):

        ''''''

        # print '### changeOverhangHeight ', overhangHeight, ho, HO

        if HO:
            # print 'HO'
            HO.pop()
            return

        if ho:
            # print 'aHO'

            suffix = self.suffix()
            # print 'suffix ', suffix
            # print 'overhangHeight ', overhangHeight
            overhangHeight =\
                FreeCAD.Units.Quantity(str(overhangHeight) + suffix)

            item = self.item
            tree = self.parent

            angle = tree.itemWidget(item, 1).value()
            angle = math.radians(angle)

            overhangHeight = overhangHeight.Value
            # print 'overhangHeight ', overhangHeight

            overhangLength = self.lengthHeight(angle, overhangHeight)
            # print 'length ', length
            overhangRun = self.run(angle, overhangHeight)
            # print 'run ', run
            tree.itemWidget(item, 6).changeOverhangLength(overhangLength, False)
            tree.itemWidget(item, 8).changeOverhangRun(overhangRun, False)

        else:
            # print 'bHO'

            suffix = 'mm'
            # print 'suffix ', suffix
            # print 'overhangHeight ', overhangHeight
            overhangHeight =\
                FreeCAD.Units.Quantity(str(overhangHeight) + suffix)

            nn = overhangHeight.getUserPreferred()
            # print nn
            overhangHeight = overhangHeight.Value
            # print 'overhangHeight ', overhangHeight
            value = overhangHeight / nn[1]
            suffix = ' ' + nn[2]

            if round(value, 2) != self.value():
                HO.append(overhangHeight)

            self.setValue(value)
            self.setSuffix(suffix)

    def changeOverhangRun(self, overhangRun, hr=True, HR=[]):

        ''''''

        # print '### changeOverhangRun ', overhangRun, hr, HR

        if HR:
            # print 'HR'
            HR.pop()
            return

        if hr:
            # print 'aHR'

            suffix = self.suffix()
            # print 'suffix ', suffix
            # print 'run ', run
            overhangRun = FreeCAD.Units.Quantity(str(overhangRun) + suffix)

            item = self.item
            tree = self.parent

            angle = tree.itemWidget(item, 1).value()
            angle = math.radians(angle)

            overhangRun = overhangRun.Value
            # print 'overhangRun ', overhangRun

            overhangLength = self.lengthRun(angle, overhangRun)
            # print 'overhangLength ', overhangLength
            overhangHeight = self.height(angle, overhangRun)
            # print 'overhangHeight ', overhangHeight
            tree.itemWidget(item, 6).changeOverhangLength(overhangLength, False)
            tree.itemWidget(item, 7).changeOverhangHeight(overhangHeight, False)

        else:
            # print 'bHR'

            suffix = 'mm'
            # print 'suffix ', suffix
            # print 'overhangRun ', overhangRun
            overhangRun = FreeCAD.Units.Quantity(str(overhangRun) + suffix)

            nn = overhangRun.getUserPreferred()
            # print nn
            overhangRun = overhangRun.Value
            # print 'overhangRun ', overhangRun

            value = overhangRun / nn[1]
            suffix = ' ' + nn[2]

            if round(value, 2) != self.value():
                HR.append(overhangRun)

            self.setValue(value)
            self.setSuffix(suffix)

    def height(self, angle, length):

        ''''''

        # print '# height'

        return length * math.sin(angle)

    def run(self, angle, length):

        ''''''

        # print '# run'

        return length * math.cos(angle)

    def lengthHeight(self, angle, height):

        ''''''

        # print '# lengthHeight'

        try:
            length = height / math.sin(angle)

        except ZeroDivisionError:
            length = height

        return length

    def lengthRun(self, angle, run):

        ''''''

        # print '# lengthRun'

        try:
            length = run / math.cos(angle)

        except ZeroDivisionError:
            length = run

        return length
