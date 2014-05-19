from math import sqrt
from fontTools.pens.basePen import BasePen
from robofab.misc.arrayTools import pointInRect, normRect

class RedArrowError(object):
    def __init__(self, position, kind, badness=1):
        self.position = position
        self.kind = kind
        self.badness = badness
    
    def __repr__(self):
        return "%s at (%i, %i)" % (self.kind, self.position[0], self.position[1])
        

class RedArrowPen(BasePen):
    def __init__(self, glyphSet, calculateBadness=True, ignoreBelow=0):
        self.glyphSet = glyphSet
        self.__currentPoint = None
        self.calculateBadness = calculateBadness
        self.ignoreBelow = ignoreBelow
        self.errors = []
        self.numErrors = 0
        # final point of the previous segment, needed for bbox calculation
        self._prev = None
    
    def _getBadness(self, pointToCheck, myRect):
        # calculate distance of point to rect
        badness = 0
        if pointToCheck[0] < myRect[0]:
            # point is left from rect
            if pointToCheck[1] < myRect[1]:
                # point is lower left from rect
                badness = int(round(sqrt((myRect[0] - pointToCheck[0])**2 + (myRect[1] - pointToCheck[1])**2)))
            elif pointToCheck[1] > myRect[3]:
                # point is upper left from rect
                badness = int(round(sqrt((myRect[0] - pointToCheck[0])**2 + (myRect[3] - pointToCheck[1])**2)))
            else:
                badness = myRect[0] - pointToCheck[0]
        elif pointToCheck[0] > myRect[2]:
            # point is right from rect
            if pointToCheck[1] < myRect[1]:
                # point is lower right from rect
                badness = int(round(sqrt((myRect[2] - pointToCheck[0])**2 + (myRect[1] - pointToCheck[1])**2)))
            elif pointToCheck[1] > myRect[3]:
                # point is upper right from rect
                badness = int(round(sqrt((myRect[2] - pointToCheck[0])**2 + (myRect[3] - pointToCheck[1])**2)))
            else:
                badness = pointToCheck[0] - myRect[2]
        else:
            # point is centered from rect, check for upper/lower
            if pointToCheck[1] < myRect[1]:
                # point is lower center from rect
                badness = myRect[1] - pointToCheck[1]
            elif pointToCheck[1] > myRect[3]:
                # point is upper center from rect
                badness = pointToCheck[1] - myRect[3]
            else:
                badness = 0
        return badness
    
    def _checkBbox(self, pointToCheck, boxPoint):
        # boxPoint is the final point of the current node,
        # the other bbox point is the previous final point
        myRect = normRect((self._prev[0], self._prev[1], boxPoint[0], boxPoint[1]))
        if not pointInRect(pointToCheck, myRect):
            if self.calculateBadness:
                badness = self._getBadness(pointToCheck, myRect)
                if badness >= self.ignoreBelow:
                    self.errors.append(RedArrowError(pointToCheck, "Extremum (badness %i units)" % badness, badness))
                    self.numErrors += 1
            else:
                self.errors.append(RedArrowError(pointToCheck, "Extremum"))
                self.numErrors += 1
    
    def _moveTo(self, pt):
        self._prev = pt
    
    def _lineTo(self, pt):
        self._prev = pt
    
    def _curveToOne(self, bcp1, bcp2, pt):
        for bcp in [bcp1, bcp2]:
            self._checkBbox(bcp, pt)
        self._prev = pt
    
    def _qCurveToOne(self, bcp, pt):
        self._checkBbox(bcp, pt)
        self._prev = pt
    
    def addComponent(self, baseGlyph, transformation):
        pass
