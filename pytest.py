import FreeCAD
import os

for directory in os.walk('/home/travis/SlopedPlanesTest/Test'):
    # print 'directory ', directory
    for filename in directory[2]:
        # print 'filename ', filename
        if filename.endswith('.fcstd'):
            # print 'open'
            FreeCAD.openDocument(directory[0] + '/' + filename)

numDoc = 0
numObj = 0
numError = 0
geometricList = []
executionList = []

for doc in FreeCAD.listDocuments().values():
    numDoc += 1
    # print '######### ', doc.Name
    for obj in doc.Objects:
        if hasattr(obj, 'Proxy'):
            if obj.Proxy.Type == 'SlopedPlanes':
                numObj += 1
                oldShape = obj.Shape.copy()

                '''obj.Proxy.faceList = []
                for pyFace in obj.Proxy.Pyth:
                    pyFace.reset = True'''

                obj.touch()
                # print '####### ', obj.Name
                doc.recompute()
                newShape = obj.Shape
                cut = oldShape.copy().cut(newShape)
                cc = newShape.copy().cut(oldShape)

                if obj.State[0] == 'Invalid':
                    numError += 1
                    executionList.append((doc.Name, obj.Name))
                    # print '????????????????????????? execution ERROR'

                elif cut.Area != 0 or\
                   cc.Area != 0 or\
                   len(newShape.Edges) != len(oldShape.Edges) or\
                   len(newShape.Vertexes) != len(oldShape.Vertexes):

                    numError += 1
                    geometricList.append((doc.Name, obj.Name))
                    # print '????????????????????????? geometric ERROR'

                else:
                    pass
                    # print '### okey'

print 'files ', numDoc
print 'objects ', numObj
print 'erros ', numError
print 'geometry errors ', geometricList
print 'execution errors ', executionList
