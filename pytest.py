print 'hello world'
'''import sys
sys.path.append('/usr/lib/freecad-daily/lib')
import FreeCAD
FreeCAD.openDocument('/home/travis/SlopedPlanesTest/hello_world.fcstd')
doc = FreeCAD.ActiveDocument
for obj in doc.Objects:
    if hasattr(obj, 'Proxy'):
        if obj.Proxy.Type == 'SlopedPlanes':
            oldShape = obj.Shape.copy()'''

            '''obj.Proxy.faceList = []
            for pyFace in obj.Proxy.Pyth:
                pyFace.reset = True'''

            '''obj.touch()
            FreeCAD.Console.PrintLog(obj.Name)
            doc.recompute()
            newShape = obj.Shape
            cut = oldShape.copy().cut(newShape)
            cc = newShape.copy().cut(oldShape)
            if cut.Area != 0 or\
               cc.Area != 0 or\
               len(newShape.Edges) != len(oldShape.Edges) or\
               len(newShape.Vertexes) != len(oldShape.Vertexes):
                FreeCAD.Console.PrintError('????????????????????????? ERROR')'''
