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


import FreeCAD

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtGui, QtCore


__title__ = "SlopedPlanesMacro"
__author__ = "Damian Caceres"
__url__ = "http://www.freecadweb.org"


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
        self.advancedOptions.setObjectName("advancedOptions")
        self.grid.addWidget(self.advancedOptions, 3, 0, 1, 1)
        self.advancedOptions.setText("advancedOptions")
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

        if self.advancedOptions.isChecked():
            self.tree.setHeaderLabels([("Face"),
                                       ("Angle"),
                                       ("Length"),
                                       ("Overhang"),
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
            self.tree.setColumnCount(6)
            self.tree.header().resizeSection(0, 60)
            self.tree.header().resizeSection(1, 120)
            self.tree.header().resizeSection(2, 120)
            self.tree.header().resizeSection(3, 120)
            self.tree.header().resizeSection(4, 120)
            self.tree.header().resizeSection(5, 120)

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

                            doubleSpinBox = QtGui.QDoubleSpinBox(self.tree)
                            doubleSpinBox.setMaximum(1000.00)
                            doubleSpinBox.setMinimum(-1000.00)
                            doubleSpinBox.setValue(angle)
                            deg = u"\u00b0"
                            doubleSpinBox.setSuffix(" "+deg)
                            self.tree.setItemWidget(item, 1, doubleSpinBox)

                            if self.advancedOptions.isChecked():

                                doubleSpinBox = QtGui.QDoubleSpinBox(self.tree)
                                doubleSpinBox.setMaximum(2000*size)
                                doubleSpinBox.setMinimum(-2000*size)
                                doubleSpinBox.setValue(pyPlane.length)
                                doubleSpinBox.setSuffix(" mm")
                                self.tree.setItemWidget(item, 2, doubleSpinBox)

                                doubleSpinBox = QtGui.QDoubleSpinBox(self.tree)
                                doubleSpinBox.setMaximum(1000*size)
                                doubleSpinBox.setMinimum(-1000*size)
                                doubleSpinBox.setValue(pyPlane.overhang)
                                doubleSpinBox.setSuffix(" mm")
                                self.tree.setItemWidget(item, 3, doubleSpinBox)

                                doubleSpinBox = QtGui.QDoubleSpinBox(self.tree)
                                doubleSpinBox.setMaximum(1000*size)
                                doubleSpinBox.setMinimum(-1000*size)
                                doubleSpinBox.setValue(pyPlane.leftWidth)
                                doubleSpinBox.setSuffix(" mm")
                                self.tree.setItemWidget(item, 4, doubleSpinBox)

                                doubleSpinBox = QtGui.QDoubleSpinBox(self.tree)
                                doubleSpinBox.setMaximum(1000*size)
                                doubleSpinBox.setMinimum(-1000*size)
                                doubleSpinBox.setValue(pyPlane.rightWidth)
                                doubleSpinBox.setSuffix(" mm")
                                self.tree.setItemWidget(item, 5, doubleSpinBox)

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

                            doubleSpinBox = self.tree.itemWidget(it, 3)
                            overhang = doubleSpinBox.value()
                            pyPlane.overhang = overhang

                            doubleSpinBox = self.tree.itemWidget(it, 4)
                            left = doubleSpinBox.value()
                            pyPlane.leftWidth = left

                            doubleSpinBox = self.tree.itemWidget(it, 5)
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
