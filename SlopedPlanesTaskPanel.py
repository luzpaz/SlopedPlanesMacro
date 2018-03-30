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

        form = QtGui.QWidget()
        self.form = form
        form.setObjectName("TaskPanel")

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
        # tree.currentItemChanged.connect(tree.changeCurrentItem)

        advancedOptions = QtGui.QCheckBox(form)
        self.advancedOptions = advancedOptions
        advancedOptions.setObjectName("AdvancedOptions")
        grid.addWidget(advancedOptions, 3, 0, 1, 1)
        advancedOptions.clicked.connect(self.advanced)

        FreeCADGui.Selection.addObserver(self)

        self.update()

    def retranslateUi(self, taskPanel):

        ''''''

        taskPanel.setWindowTitle(self.obj.Label)

        self.advancedOptions.setText("Advanced Options")
        advancedOptionsToolTip = '''More parameters to control the faces.'''
        self.advancedOptions.setToolTip(advancedOptionsToolTip)

        if self.advancedOptions.isChecked():
            self.tree.setHeaderLabels([("Face"),
                                       ("Angle"),
                                       ("Length"),
                                       ("Height"),
                                       ("Run"),
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

    def reject(self):

        ''''''

        FreeCADGui.Selection.removeObserver(self)
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()
        return True

    def accept(self):

        ''''''

        FreeCADGui.Selection.removeObserver(self)
        self.resetObject()
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

            tree.setColumnCount(13)
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
            tree.header().resizeSection(10, 60)
            tree.header().resizeSection(11, 180)
            tree.header().resizeSection(12, 60)

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

            pyFaceList = slopedPlanes.Proxy.Pyth
            numSlope, num = 0, 0
            compound = slopedPlanes.Shape
            upFace = False
            for pyFace in pyFaceList:
                originList = []
                pyWireList = pyFace.wires
                numFace = pyFace.numFace
                size = pyFace.size
                # print '### numFace ', numFace
                shell = compound.Shells[numFace]
                numSlope += num
                num, lenFace = 0, 0

                for pyWire in pyWireList:
                    numWire = pyWire.numWire
                    # print '## numWire ', numWire
                    pyPlaneList = pyWire.planes
                    lenWire = len(pyPlaneList)
                    lenFace += lenWire

                    if up:
                        if numWire == 1:
                            numSlope += 1
                            upFace = True

                    for pyPlane in pyPlaneList:

                        charge = False
                        numAngle = pyPlane.numGeom
                        # print '# numGeom ', numAngle
                        sweepCurve = pyPlane.sweepCurve
                        angle = pyPlane.angle
                        if [numWire, numAngle] not in originList:

                            if isinstance(angle, float):
                                numSlope += 1
                                charge = True

                            else:
                                alfa, beta = angle[0], angle[1]
                                if [alfa, beta] not in originList:
                                    originList.append([alfa, beta])

                                    if alfa == numWire:

                                        if beta > numAngle:
                                            pyW = pyWireList[alfa]
                                            angle =\
                                                pyW.planes[beta].angle
                                            numSlope += 1
                                            charge = True

                                    elif alfa > numWire:
                                        pyW = pyWireList[alfa]
                                        angle =\
                                            pyW.planes[beta].angle
                                        numSlope += 1
                                        charge = True

                                    elif alfa < numWire:
                                        pass

                        if charge:

                            # print 'numSlope ', numSlope

                            item = QtGui.QTreeWidgetItem(tree)
                            item.setText(0, str(numSlope))

                            doubleSpinBox = _DoubleSpinBox()
                            doubleSpinBox.setParent(tree)
                            doubleSpinBox.setToolTip("The angle of the related face")
                            doubleSpinBox.setMaximum(1000.00)
                            doubleSpinBox.setMinimum(-1000.00)
                            doubleSpinBox.setValue(angle)
                            deg = u"\u00b0"
                            doubleSpinBox.setSuffix(" "+deg)
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
                                value = float(nn[0].split()[0].replace(',', '.'))
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
                                value = float(nn[0].split()[0].replace(',', '.'))
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
                                value = float(nn[0].split()[0].replace(',', '.'))
                                doubleSpinBox.setValue(value)
                                doubleSpinBox.setSuffix(suffix)
                                tree.setItemWidget(item, 4, doubleSpinBox)

                                doubleSpinBox.item = item
                                doubleSpinBox.parent = tree
                                doubleSpinBox.valueChanged.connect(doubleSpinBox.changeRun)

                                doubleSpinBox = _DoubleSpinBox()
                                doubleSpinBox.setParent(tree)
                                doubleSpinBox.setToolTip("The overhang length of the related face")
                                doubleSpinBox.setMaximum(1000*size)
                                doubleSpinBox.setMinimum(-1000*size)
                                length = pyPlane.overhang
                                ll = FreeCAD.Units.Quantity(length,FreeCAD.Units.Length)
                                nn = ll.getUserPreferred()
                                suffix = ' ' + nn[2]
                                value = float(nn[0].split()[0].replace(',', '.'))
                                doubleSpinBox.setValue(value)
                                doubleSpinBox.setSuffix(suffix)
                                tree.setItemWidget(item, 5, doubleSpinBox)

                                doubleSpinBox.item = item
                                doubleSpinBox.parent = tree
                                doubleSpinBox.valueChanged.connect(doubleSpinBox.changeOverhangLength)

                                doubleSpinBox = _DoubleSpinBox()
                                doubleSpinBox.setParent(tree)
                                doubleSpinBox.setToolTip("The overhang height of the related face")
                                doubleSpinBox.setMaximum(1000*size)
                                doubleSpinBox.setMinimum(-1000*size)
                                height = length * math.sin(angle)
                                ll = FreeCAD.Units.Quantity(height,FreeCAD.Units.Length)
                                nn = ll.getUserPreferred()
                                suffix = ' ' + nn[2]
                                value = float(nn[0].split()[0].replace(',', '.'))
                                doubleSpinBox.setValue(value)
                                doubleSpinBox.setSuffix(suffix)
                                tree.setItemWidget(item, 6, doubleSpinBox)

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
                                value = float(nn[0].split()[0].replace(',', '.'))
                                doubleSpinBox.setValue(value)
                                doubleSpinBox.setSuffix(suffix)
                                tree.setItemWidget(item, 7, doubleSpinBox)

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
                                value = float(nn[0].split()[0].replace(',', '.'))
                                doubleSpinBox.setValue(value)
                                doubleSpinBox.setSuffix(suffix)
                                tree.setItemWidget(item, 8, doubleSpinBox)

                                doubleSpinBox = QtGui.QDoubleSpinBox(tree)
                                doubleSpinBox.setToolTip("The right width of the related face")
                                doubleSpinBox.setMaximum(1000*size)
                                doubleSpinBox.setMinimum(-1000*size)
                                rigthWidth = pyPlane.rightWidth
                                ll = FreeCAD.Units.Quantity(rigthWidth,FreeCAD.Units.Length)
                                nn = ll.getUserPreferred()
                                suffix = ' ' + nn[2]
                                value = float(nn[0].split()[0].replace(',', '.'))
                                doubleSpinBox.setValue(value)
                                doubleSpinBox.setSuffix(suffix)
                                tree.setItemWidget(item, 9, doubleSpinBox)

                                button = _NewCurve()
                                button.setParent(tree)
                                button.plane = pyPlane
                                button.slopedPlanes = slopedPlanes
                                button.setText('New')
                                tree.setItemWidget(item, 10, button)
                                button.clicked.connect(button.onClicked)

                                combo = QtGui.QComboBox(tree)
                                combo.addItems(linkList)
                                try:
                                    index = linkList.index(sweepCurve)
                                    combo.setCurrentIndex(index)
                                except ValueError:
                                    combo.setCurrentIndex(0)
                                tree.setItemWidget(item, 11, combo)

                                button.combo = combo

                                item.setText(12, str(numSlope))

                value = 0
                if upFace:
                    value += 1
                    upFace = False

                num = len(shell.Faces) - value - lenFace
                # print 'num ', num

        self.retranslateUi(self.form)
        self.updating = False

    def resetObject(self):

        ''''''

        # print 'resetObject'

        slopedPlanes = self.obj

        up = slopedPlanes.Up

        pyFaceList = slopedPlanes.Proxy.Pyth
        numSlope, num = 0, 0
        compound = slopedPlanes.Shape
        upFace = False
        for pyFace in pyFaceList:
            originList = []
            numSlope += num
            num, lenFace = 0, 0
            numFace = pyFace.numFace
            # print '### numFace', numFace
            shell = compound.Shells[numFace]

            pyWireList = pyFace.wires
            for pyWire in pyWireList:
                numWire = pyWire.numWire
                # print '## numWire', numWire
                pyPlaneList = pyWire.planes
                lenWire = len(pyPlaneList)
                lenFace += lenWire
                numAngle = -1
                pyPlaneList = pyWire.planes

                if up:
                    if numWire == 1:
                        numSlope += 1
                        upFace = True

                for pyPlane in pyPlaneList:
                    numAngle += 1
                    angle = pyPlane.angle
                    # print '# numAngle ', numAngle, ' angle ', angle
                    charge = False

                    if [numWire, numAngle] not in originList:

                        if isinstance(angle, float):
                            # print 'A'
                            charge = True
                            numSlope += 1

                        else:
                            # print 'B'
                            alfa, beta = angle[0], angle[1]
                            if [alfa, beta] not in originList:
                                # print 'BB'
                                originList.append([alfa, beta])

                                if alfa == numWire:
                                    # print 'BB1'

                                    if beta > numAngle:
                                        # print 'BB11'
                                        charge = True
                                        numSlope += 1
                                        pyPlane = pyWireList[alfa].planes[beta]

                                elif alfa > numWire:
                                    # print 'BB2'
                                    charge = True
                                    numSlope += 1
                                    pyPlane = pyWireList[alfa].planes[beta]

                                elif alfa < numWire:
                                    # print 'BB3'
                                    pass

                    if charge:

                        # print 'numSlope ', numSlope

                        tree = self.tree

                        it = tree.findItems(str(numSlope),
                                            QtCore.Qt.MatchExactly, 0)[0]

                        doubleSpinBox = tree.itemWidget(it, 1)
                        value = doubleSpinBox.value()
                        # print 'value ', value
                        pyPlane.angle = value

                        if self.advancedOptions.isChecked():

                            doubleSpinBox = tree.itemWidget(it, 2)
                            length = doubleSpinBox.value()
                            suffix = doubleSpinBox.suffix()
                            length = FreeCAD.Units.Quantity(str(length) + suffix)
                            pyPlane.length = length.Value

                            doubleSpinBox = tree.itemWidget(it, 5)
                            overhang = doubleSpinBox.value()
                            overhang = FreeCAD.Units.Quantity(str(overhang) + suffix)
                            pyPlane.overhang = overhang.Value

                            doubleSpinBox = tree.itemWidget(it, 8)
                            left = doubleSpinBox.value()
                            left = FreeCAD.Units.Quantity(str(left) + suffix)
                            pyPlane.leftWidth = left.Value

                            doubleSpinBox = tree.itemWidget(it, 9)
                            right = doubleSpinBox.value()
                            right = FreeCAD.Units.Quantity(str(right) + suffix)
                            pyPlane.rightWidth = right.Value

                            comboBox = tree.itemWidget(it, 11)
                            sweepCurve = comboBox.currentText()
                            pyPlane.sweepCurve = sweepCurve

                value = 0
                if upFace:
                    value += 1
                    upFace = False

                num = len(shell.Faces) - value - lenFace
                # print 'num ', num

        slopedPlanes.Proxy.OnChanged = False

        slopedPlanes.touch()
        FreeCAD.ActiveDocument.recompute()
        self.update()

    def addSelection(self, doc, obj, sub, pnt=None):

        ''''''

        # print 'addSelection'
        # print(doc, obj, sub, pnt)

        reset = True
        slopedPlanes = self.obj

        shape = slopedPlanes.Shape.copy()
        shape.Placement = FreeCAD.Placement()

        if doc == slopedPlanes.Document.Name:
            if obj == slopedPlanes.Name:
                if sub.startswith('Face'):

                    sketch = slopedPlanes.Base
                    sketchBase = sketch.Placement.Base
                    sketchAxis = sketch.Placement.Rotation.Axis
                    sketchAngle = sketch.Placement.Rotation.Angle
                    shape.rotate(sketchBase, sketchAxis, math.degrees(-1 * sketchAngle))
                    shape.translate(-1 * sketchBase)

                    originList = []

                    num = int(sub[4:])
                    ff = shape.Faces[num - 1]
                    number = 0
                    for pyFace in slopedPlanes.Proxy.Pyth:
                        if not reset:
                            break
                        for pyWire in pyFace.wires:
                            numWire = pyWire.numWire
                            if not reset:
                                break
                            for pyPlane in pyWire.planes:

                                number += 1
                                geomShape = pyPlane.geomShape
                                section = ff.section(geomShape)

                                if section.Edges:
                                    item =\
                                        self.tree.findItems(str(number),
                                                            QtCore.Qt.MatchExactly,
                                                            0)[0]
                                    self.tree.setCurrentItem(item)
                                    reset = False
                                    break

                                if [numWire, number - 1] in originList:
                                    number -= 1

                                if isinstance(pyPlane.angle, list):
                                    [nW, nG] = pyPlane.angle
                                    originList.append([nW, nG])

        if reset:
            self.tree.setCurrentItem(None)


class _TreeWidget(QtGui.QTreeWidget):

    ''''''

    def __init__(self):

        ''''''

        super(_TreeWidget, self).__init__()
        self.setColumnCount(2)
        self.header().resizeSection(0, 60)
        self.header().resizeSection(1, 60)

    '''def changeCurrentItem(self, current, previous):

        ''''''

        print 'currentItemChanged'

        if current:
            number = self.indexFromItem(previous).data()
            print 'number ', number
            num = self.indexFromItem(current).data()
            print 'num ', num
            if num != number:
                FreeCADGui.Selection.clearSelection()
                obj = self.obj
                sub = 'Face' + str(num)
                FreeCADGui.Selection.addSelection(obj, [sub])'''


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

    def changeAngle(self, angle):

        ''''''

        item = self.item
        tree = self.parent

        length = tree.itemWidget(item, 2).value()
        # print 'length ', length
        angle = math.radians(angle)
        # print 'angle ', angle
        height = self.height(angle, length)
        # print 'height ', height
        run = self.run(angle, length)
        # print 'run ', run
        tree.itemWidget(item, 3).changeHeight(height, False)
        tree.itemWidget(item, 4).changeRun(run, False)

    def changeLength(self, length, update=True):

        ''''''

        item = self.item
        tree = self.parent

        if update:
            angle = tree.itemWidget(item, 1).value()
            angle = math.radians(angle)
            height = self.height(angle, length)
            run = self.run(angle, length)
            tree.itemWidget(item, 3).changeHeight(height, False)
            tree.itemWidget(item, 4).changeRun(run, False)
        else:
            tree.itemWidget(item, 2).setValue(length)

    def changeHeight(self, height, update=True):

        ''''''

        item = self.item
        tree = self.parent

        if update:
            angle = tree.itemWidget(item, 1).value()
            angle = math.radians(angle)
            length = self.lengthHeight(angle, height)
            run = self.run(angle, length)
            tree.itemWidget(item, 2).changeLength(length, False)
            tree.itemWidget(item, 4).changeRun(run, False)
        else:
            tree.itemWidget(item, 3).setValue(height)

    def changeRun(self, run, update=True):

        ''''''

        item = self.item
        tree = self.parent

        if update:
            angle = tree.itemWidget(item, 1).value()
            angle = math.radians(angle)
            length = self.lengthRun(angle, run)
            height = self.height(angle, length)
            tree.itemWidget(item, 2).changeLength(length, False)
            tree.itemWidget(item, 3).changeHeight(height, False)
        else:
            tree.itemWidget(item, 4).setValue(run)

    def changeOverhangLength(self, length, update=True):

        ''''''

        item = self.item
        tree = self.parent

        if update:
            angle = tree.itemWidget(item, 1).value()
            angle = math.radians(angle)
            height = self.height(angle, length)
            run = self.run(angle, length)
            tree.itemWidget(item, 6).changeOverhangHeight(height, False)
            tree.itemWidget(item, 7).changeOverhangRun(run, False)
        else:
            tree.itemWidget(item, 5).setValue(length)

    def changeOverhangHeight(self, height, update=True):

        ''''''

        item = self.item
        tree = self.parent

        if update:
            angle = tree.itemWidget(item, 1).value()
            angle = math.radians(angle)
            length = self.lengthHeight(angle, height)
            run = self.run(angle, length)
            tree.itemWidget(item, 5).changeOverhangLength(length, False)
            tree.itemWidget(item, 7).changeOverhangRun(run, False)
        else:
            tree.itemWidget(item, 6).setValue(height)

    def changeOverhangRun(self, run, update=True):

        ''''''

        item = self.item
        tree = self.parent

        if update:
            angle = tree.itemWidget(item, 1).value()
            angle = math.radians(angle)
            length = self.lengthRun(angle, run)
            height = self.height(angle, length)
            tree.itemWidget(item, 5).changeOverhangLength(length, False)
            tree.itemWidget(item, 6).changeOverhangHeight(height, False)
        else:
            tree.itemWidget(item, 7).setValue(run)

    def height(self, angle, length):

        ''''''

        return length * math.sin(angle)

    def run(self, angle, length):

        ''''''

        return length * math.cos(angle)

    def lengthHeight(self, angle, height):

        ''''''

        try:
            length = height / math.sin(angle)

        except ZeroDivisionError:
            length = 0

        return length

    def lengthRun(self, angle, run):

        ''''''

        try:
            length = run / math.cos(angle)

        except ZeroDivisionError:
            length = 0

        return length
