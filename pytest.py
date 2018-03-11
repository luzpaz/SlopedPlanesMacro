import FreeCAD
FreeCAD.openDocument('/home/travis/SlopedPlanesTest/hello_world.fcstd')
doc = FreeCAD.ActiveDocument
print '###### ', doc.Name
for obj in doc.Objects:
    if hasattr(obj, 'Proxy'):
        if obj.Proxy.Type == 'SlopedPlanes':
            oldShape = obj.Shape.copy()
            obj.touch()
            print '### ', obj.Name
            doc.recompute()
            newShape = obj.Shape
            cut = oldShape.copy().cut(newShape)
            cc = newShape.copy().cut(oldShape)
            if cut.Area != 0 or\
               cc.Area != 0 or\
               len(newShape.Edges) != len(oldShape.Edges) or\
               len(newShape.Vertexes) != len(oldShape.Vertexes):
                print '????????????????????????? geometric ERROR'
            elif obj.State[0] == 'Invalid':
                print '????????????????????????? execution ERROR'
FreeCAD.closeDocument('/home/travis/SlopedPlanesTest/hello_world.fcstd')
exit()
