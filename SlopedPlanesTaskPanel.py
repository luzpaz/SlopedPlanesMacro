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

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtGui, QtCore


__title__ = "SlopedPlanesMacro"
__author__ = "Damian Caceres"
__url__ = "http://www.freecadweb.org"
__version__ = ""


class _TaskPanel_SlopedPlanes():

    ''''''

    def __init__(self):

        ''''''

        self.updating = False

        self.obj = None
        self.form = QtGui.QWidget()
        self.form.setObjectName("TaskPanel")
        self.grid = QtGui.QGridLayout(self.form)
        self.grid.setObjectName("grid")
        self.title = QtGui.QLabel(self.form)
        self.grid.addWidget(self.title, 0, 0, 1, 2)
        self.tree = QtGui.QTreeWidget(self.form)
        self.grid.addWidget(self.tree, 1, 0, 1, 2)

        self.advancedOptions = QtGui.QCheckBox(self.form)
        self.advancedOptions.setObjectName("AdvancedOptions")
        self.grid.addWidget(self.advancedOptions, 3, 0, 1, 1)
        self.advancedOptions.clicked.connect(self.advanced)

        self.tree.setColumnCount(2)
        self.tree.header().resizeSection(0, 60)
        self.tree.header().resizeSection(1, 60)

        QtCore.QObject.connect(self.tree,
                               QtCore.SIGNAL("itemChanged(QTreeWidgetItem *,\
                                             int)"),
                               self.edit)

        self.update()

    def retranslateUi(self, taskPanel):

        ''''''

        taskPanel.setWindowTitle("SlopedPlanes")
        self.title.setText("SlopedPlanes parameters")
        titleToolTip = ('The angles correspond with the faces of the SlopedPlanes shape.\n'
                        'The numeration start at the LowerLeft corner and increase counter clockwise for exterior wires,\n'
                        'and at the UpperLeft corner and increase clockwise for the interior wires.')
        self.title.setToolTip(titleToolTip)

        self.advancedOptions.setText("Advanced Options")
        advancedOptionsToolTip = '''More parameters to control the faces of the SlopedPlanes.'''
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
                                       ("Right Width")])
        else:
            self.tree.setHeaderLabels([("Face"),
                                       ("Angle")])

    def isAllowedAlterSelection(self):

        ''''''

        return False

    def isAllowedAlterView(self):

        ''''''

        return True

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

        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()
        return True

    def accept(self):

        ''''''

        self.resetObject()
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()
        return True

    def edit(self, item, column):

        ''''''

        if not self.updating:
            self.resetObject()

    def advanced(self):

        ''''''

        if self.advancedOptions.isChecked():
            self.tree.setColumnCount(10)
            self.tree.header().resizeSection(0, 60)
            self.tree.header().resizeSection(1, 120)
            self.tree.header().resizeSection(2, 120)
            self.tree.header().resizeSection(3, 120)
            self.tree.header().resizeSection(4, 120)
            self.tree.header().resizeSection(5, 120)
            self.tree.header().resizeSection(6, 120)
            self.tree.header().resizeSection(7, 120)
            self.tree.header().resizeSection(8, 120)
            self.tree.header().resizeSection(9, 120)

        else:
            self.tree.setColumnCount(2)
            self.tree.header().resizeSection(0, 60)
            self.tree.header().resizeSection(1, 60)

        self.update()

    def update(self):

        ''''''

        self.updating = True
        self.tree.clear()
        slopedPlanes = self.obj

        if slopedPlanes:

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

                            item = QtGui.QTreeWidgetItem(self.tree)
                            item.setFlags(item.flags() |
                                          QtCore.Qt.ItemIsEditable)
                            item.setTextAlignment(0, QtCore.Qt.AlignLeft)
                            item.setText(0, str(numSlope))

                            doubleSpinBox = _DoubleSpinBox()
                            doubleSpinBox.setParent(self.tree)
                            doubleSpinBox.setToolTip("The angle of the related face")
                            doubleSpinBox.setMaximum(1000.00)
                            doubleSpinBox.setMinimum(-1000.00)
                            doubleSpinBox.setValue(angle)
                            deg = u"\u00b0"
                            doubleSpinBox.setSuffix(" "+deg)
                            self.tree.setItemWidget(item, 1, doubleSpinBox)

                            if self.advancedOptions.isChecked():

                                doubleSpinBox.item = item
                                doubleSpinBox.parent = self.tree
                                doubleSpinBox.valueChanged.connect(doubleSpinBox.changeAngle)

                                angle = math.radians(angle)

                                doubleSpinBox = _DoubleSpinBox()
                                doubleSpinBox.setParent(self.tree)
                                doubleSpinBox.setToolTip("The length of the related face")
                                doubleSpinBox.setMaximum(2000*size)
                                doubleSpinBox.setMinimum(-2000*size)
                                length = pyPlane.length
                                doubleSpinBox.setValue(length)
                                doubleSpinBox.setSuffix(" mm")
                                self.tree.setItemWidget(item, 2, doubleSpinBox)

                                doubleSpinBox.item = item
                                doubleSpinBox.parent = self.tree
                                doubleSpinBox.valueChanged.connect(doubleSpinBox.changeLength)

                                doubleSpinBox = _DoubleSpinBox()
                                doubleSpinBox.setParent(self.tree)
                                doubleSpinBox.setToolTip("The height of the related face")
                                doubleSpinBox.setMaximum(2000*size)
                                doubleSpinBox.setMinimum(-2000*size)
                                height = length * math.sin(angle)
                                doubleSpinBox.setValue(height)
                                doubleSpinBox.setSuffix(" mm")
                                self.tree.setItemWidget(item, 3, doubleSpinBox)

                                doubleSpinBox.item = item
                                doubleSpinBox.parent = self.tree
                                doubleSpinBox.valueChanged.connect(doubleSpinBox.changeHeight)

                                doubleSpinBox = _DoubleSpinBox()
                                doubleSpinBox.setParent(self.tree)
                                doubleSpinBox.setToolTip("The run of the related face")
                                doubleSpinBox.setMaximum(2000*size)
                                doubleSpinBox.setMinimum(-2000*size)
                                run = length * math.cos(angle)
                                doubleSpinBox.setValue(run)
                                doubleSpinBox.setSuffix(" mm")
                                self.tree.setItemWidget(item, 4, doubleSpinBox)

                                doubleSpinBox.item = item
                                doubleSpinBox.parent = self.tree
                                doubleSpinBox.valueChanged.connect(doubleSpinBox.changeRun)

                                doubleSpinBox = _DoubleSpinBox()
                                doubleSpinBox.setParent(self.tree)
                                doubleSpinBox.setToolTip("The overhang length of the related face")
                                doubleSpinBox.setMaximum(1000*size)
                                doubleSpinBox.setMinimum(-1000*size)
                                length = pyPlane.overhang
                                doubleSpinBox.setValue(length)
                                doubleSpinBox.setSuffix(" mm")
                                self.tree.setItemWidget(item, 5, doubleSpinBox)

                                doubleSpinBox.item = item
                                doubleSpinBox.parent = self.tree
                                doubleSpinBox.valueChanged.connect(doubleSpinBox.changeOverhangLength)

                                doubleSpinBox = _DoubleSpinBox()
                                doubleSpinBox.setParent(self.tree)
                                doubleSpinBox.setToolTip("The overhang height of the related face")
                                doubleSpinBox.setMaximum(1000*size)
                                doubleSpinBox.setMinimum(-1000*size)
                                height = length * math.sin(angle)
                                doubleSpinBox.setValue(height)
                                doubleSpinBox.setSuffix(" mm")
                                self.tree.setItemWidget(item, 6, doubleSpinBox)

                                doubleSpinBox.item = item
                                doubleSpinBox.parent = self.tree
                                doubleSpinBox.valueChanged.connect(doubleSpinBox.changeOverhangHeight)

                                doubleSpinBox = _DoubleSpinBox()
                                doubleSpinBox.setParent(self.tree)
                                doubleSpinBox.setToolTip("The overhang run of the related face")
                                doubleSpinBox.setMaximum(1000*size)
                                doubleSpinBox.setMinimum(-1000*size)
                                run = length * math.cos(angle)
                                doubleSpinBox.setValue(run)
                                doubleSpinBox.setSuffix(" mm")
                                self.tree.setItemWidget(item, 7, doubleSpinBox)

                                doubleSpinBox.item = item
                                doubleSpinBox.parent = self.tree
                                doubleSpinBox.valueChanged.connect(doubleSpinBox.changeOverhangRun)

                                doubleSpinBox = QtGui.QDoubleSpinBox(self.tree)
                                doubleSpinBox.setToolTip("The left width of the related face")
                                doubleSpinBox.setMaximum(1000*size)
                                doubleSpinBox.setMinimum(-1000*size)
                                doubleSpinBox.setValue(pyPlane.leftWidth)
                                doubleSpinBox.setSuffix(" mm")
                                self.tree.setItemWidget(item, 8, doubleSpinBox)

                                doubleSpinBox = QtGui.QDoubleSpinBox(self.tree)
                                doubleSpinBox.setToolTip("The right width of the related face")
                                doubleSpinBox.setMaximum(1000*size)
                                doubleSpinBox.setMinimum(-1000*size)
                                doubleSpinBox.setValue(pyPlane.rightWidth)
                                doubleSpinBox.setSuffix(" mm")
                                self.tree.setItemWidget(item, 9, doubleSpinBox)

                value = 0
                if upFace:
                    value += 1
                    upFace = False

                num = len(shell.Faces) - value - lenFace
                # print 'num ', num

        self.retranslateUi(self.form)
        self.updating = False

    def resetObject(self, remove=None):

        ''''''

        slopedPlanes = self.obj

        up = slopedPlanes.Up

        pyFaceList = slopedPlanes.Proxy.Pyth
        numSlope, num = 0, 0
        compound = self.obj.Shape
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

                        it = self.tree.findItems(str(numSlope),
                                                 QtCore.Qt.MatchExactly, 0)[0]

                        doubleSpinBox = self.tree.itemWidget(it, 1)
                        value = doubleSpinBox.value()
                        # print 'value ', value
                        pyPlane.angle = value

                        if self.advancedOptions.isChecked():

                            doubleSpinBox = self.tree.itemWidget(it, 2)
                            length = doubleSpinBox.value()
                            pyPlane.length = length

                            doubleSpinBox = self.tree.itemWidget(it, 5)
                            overhang = doubleSpinBox.value()
                            pyPlane.overhang = overhang

                            doubleSpinBox = self.tree.itemWidget(it, 8)
                            left = doubleSpinBox.value()
                            pyPlane.leftWidth = left

                            doubleSpinBox = self.tree.itemWidget(it, 9)
                            right = doubleSpinBox.value()
                            pyPlane.rightWidth = right

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


class _DoubleSpinBox(QtGui.QDoubleSpinBox):

    ''''''

    def __init__(self):

        ''''''

        super(_DoubleSpinBox, self).__init__()

    @property
    def item(self):

        ''''''

        return self._item

    @item.setter
    def item(self, item):

        ''''''

        self._item = item

    @property
    def parent(self):

        ''''''

        return self._parent

    @parent.setter
    def parent(self, parent):

        ''''''

        self._parent = parent

    def changeAngle(self, angle):

        ''''''

        item = self.item
        tree = self.parent

        length = tree.itemWidget(item, 2).value()
        angle = math.radians(angle)
        height = self.height(angle, length)
        run = self.run(angle, length)
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

        return height / math.sin(angle)

    def lengthRun(self, angle, run):

        ''''''

        return run / math.cos(angle)
