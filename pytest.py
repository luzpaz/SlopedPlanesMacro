import FreeCAD
import os
import time


numDoc = 0
numObj = 0
numError = 0
geometricList = []
vertexList = []
edgeList = []
executionList = []
touchedList = []


for directory in os.walk('/home/slopedplanestest/Test'):
    for filename in directory[2]:
        if filename.endswith('.fcstd'):
            doc = FreeCAD.openDocument(directory[0] + '/' + filename)
            numDoc += 1

            for obj in doc.Objects:
                if hasattr(obj, 'Proxy'):
                    if obj.Proxy.Type == 'SlopedPlanes':
                        numObj += 1

                        oldShape = obj.Shape.copy()

                        obj.touch()
                        doc.recompute()

                        newShape = obj.Shape

                        cut = oldShape.copy().cut(newShape)
                        cc = newShape.copy().cut(oldShape)

                        if 'Touched' in obj.State:

                            numError += 1
                            touchedList.append((doc.Name, obj.Name))

                        if 'Invalid' in obj.State:

                            numError += 1
                            executionList.append((doc.Name, obj.Name))

                        elif cut.isNull() or cc.isNull():

                            numError += 1
                            geometricList.append((doc.Name, obj.Name))

                        elif cut.Area != 0 or cc.Area != 0:

                            numError += 1
                            geometricList.append((doc.Name, obj.Name))

                        elif len(newShape.Edges) != len(oldShape.Edges):

                            numError += 1
                            edgeList.append((doc.Name, obj.Name))

                        elif len(newShape.Vertexes) != len(oldShape.Vertexes):

                            numError += 1
                            vertexList.append((doc.Name, obj.Name))

                        else:

                            pass

FreeCAD.Console.PrintMessage('files ' + str(numDoc) + '\n')
FreeCAD.Console.PrintMessage('objects ' + str(numObj) + '\n')
FreeCAD.Console.PrintMessage('errors ' + str(numError) + '\n')
FreeCAD.Console.PrintMessage('geometryErrors ' + str(geometricList) + '\n')
FreeCAD.Console.PrintMessage('edgeErrors ' + str(edgeList) + '\n')
FreeCAD.Console.PrintMessage('vertexErrors ' + str(vertexList) + '\n')
FreeCAD.Console.PrintMessage('executionErrors ' + str(executionList) + '\n')
FreeCAD.Console.PrintMessage('touchedErrors ' + str(touchedList) + '\n')
FreeCAD.Console.PrintMessage('time.clock() ' + str(time.clock()) + '\n')
