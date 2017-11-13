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

        # self.tree.setColumnCount(5)
        self.tree.setColumnCount(2)
        self.tree.header().resizeSection(0, 60)
        self.tree.header().resizeSection(1, 30)
        # self.tree.header().resizeSection(2, 90)
        # self.tree.header().resizeSection(3, 90)
        # self.tree.header().resizeSection(4, 90)

        QtCore.QObject.connect(self.tree,
                               QtCore.SIGNAL("itemChanged(QTreeWidgetItem *,\
                                             int)"),
                               self.edit)

        self.update()

    def retranslateUi(self, taskPanel):

        ''''''

        taskPanel.setWindowTitle("SlopedPlanes")
        self.title.setText("SlopedPlanes parameters")
        self.tree.setHeaderLabels([("Face"),
                                   ("Angle")])
        # ("Length"),
        # ("Left Width"),
        # ("Right Width")])

    def isAllowedAlterSelection(self):

        ''''''

        return True

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
            self.obj.Proxy.execute(self.obj)
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
                            doubleSpinBox.setValue(angle)
                            self.tree.setItemWidget(item, 1, doubleSpinBox)

                            '''doubleSpinBox = QtGui.QDoubleSpinBox(self.tree)
                            doubleSpinBox.setValue(pyPlane.length)
                            self.tree.setItemWidget(item, 2, doubleSpinBox)

                            width = pyPlane.width

                            doubleSpinBox = QtGui.QDoubleSpinBox(self.tree)
                            doubleSpinBox.setValue(width[0])
                            self.tree.setItemWidget(item, 3, doubleSpinBox)

                            doubleSpinBox = QtGui.QDoubleSpinBox(self.tree)
                            doubleSpinBox.setValue(width[1])
                            self.tree.setItemWidget(item, 4, doubleSpinBox)'''

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
                    # print '# numAngle ', numAngle
                    charge = False

                    if [numWire, numAngle] not in originList:

                        if isinstance(angle, float):
                            charge = True
                            numSlope += 1

                        else:
                            alfa, beta = angle[0], angle[1]
                            if [alfa, beta] not in originList:
                                originList.append([alfa, beta])

                                if alfa == numWire:

                                    if beta > numAngle:
                                        charge = True
                                        numSlope += 1
                                        pyPlane = pyWireList[alfa].planes[beta]

                                elif alfa > numWire:
                                    charge = True
                                    numSlope += 1
                                    pyPlane = pyWireList[alfa].planes[beta]

                                elif alfa < numWire:
                                    pass

                    if charge:

                        # print 'numSlope ', numSlope

                        it = self.tree.findItems(str(numSlope),
                                                 QtCore.Qt.MatchExactly, 0)[0]

                        doubleSpinBox = self.tree.itemWidget(it, 1)
                        value = doubleSpinBox.value()
                        pyPlane.angle = value

                        '''doubleSpinBox = self.tree.itemWidget(it, 2)
                        length = doubleSpinBox.value()
                        pyPlane.length = length

                        doubleSpinBox = self.tree.itemWidget(it, 3)
                        left = doubleSpinBox.value()

                        doubleSpinBox = self.tree.itemWidget(it, 4)
                        right = doubleSpinBox.value()

                        pyPlane.width = [left, right]'''

                value = 0
                if upFace:
                    value += 1
                    upFace = False

                num = len(shell.Faces) - value - lenFace
                # print 'num ', num

        slopedPlanes.touch()
        FreeCAD.ActiveDocument.recompute()
        self.update()
