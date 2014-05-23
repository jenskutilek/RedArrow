from math import sqrt
from fontTools.pens.basePen import BasePen
from robofab.misc.arrayTools import pointInRect, normRect
from robofab.world import CurrentGlyph # for bbox calculation, FIXME
from helpers import RedArrowError, getExtremaForCubic

def getTriangleArea(a, b, c):
    return (b[0] -a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])


class RedArrowPen(BasePen):
    def __init__(self, glyphSet, calculateBadness=True, ignoreBelow=0):
        self.glyphSet = glyphSet
        self.__currentPoint = None
        self.calculateBadness = calculateBadness
        self.ignoreBelow = ignoreBelow
        self.errors = {}
        # final point of the previous segment, needed for bbox calculation
        self._prev = None
        self._prev_ref = None
    
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
            else:
                self.errors.append(RedArrowError(pointToCheck, "Extremum"))
    
    def _localExtremumTest(self, p1, p2, p3, p4):
        myRect = normRect((p1[0], p1[1], p4[0], p4[1]))
        if not (pointInRect(p2, myRect) and pointInRect(p3, myRect)):
            points = getExtremaForCubic(p1, p2, p3, p4)
            for p in points:
                if p in self.errors:
                    self.errors[p].extend([RedArrowError(p4, "Local extremum")])
                else:
                    self.errors[p] = [RedArrowError(p4, "Local extremum")]
    
    def _globalExtremumTest(self, p1, p2, p3, p4):
        myRect = CurrentGlyph().box
        if not (pointInRect(p2, myRect) and pointInRect(p3, myRect)):
            points = getExtremaForCubic(p1, p2, p3, p4, h=True, v=True)
            for p in points:
                if p in self.errors:
                    self.errors[p].extend([RedArrowError(p4, "Bounding box extremum")])
                else:
                    self.errors[p] = [RedArrowError(p4, "Bounding box extremum")]
    
    def _checkSmooth(self, p, refPoint):
        if self._prev_ref is not None:
            a = abs(getTriangleArea(self._prev_ref, refPoint, p))
            if 4000 > a > 200:
                if p in self.errors:
                    self.errors[p].extend([RedArrowError(p, "Smooth Connection (badness %i)" % a, a)])
                else:
                    self.errors[p] = [RedArrowError(p, "Smooth Connection (badness %i)" % a, a)]
    
    def _moveTo(self, pt):
        self._prev_ref = None
        self._prev = pt
    
    def _lineTo(self, pt):
        self._checkSmooth(self._prev, pt)
        self._prev_ref = self._prev
        self._prev = pt
    
    def _curveToOne(self, bcp1, bcp2, pt):
        # self._checkBbox doesn't display the actual extremum point,
        # but the offending handles. Superseded by self._checkExtremumCubic.
        #for bcp in [bcp1, bcp2]:
        #    self._checkBbox(bcp, pt)
        self._curveTests(bcp1, bcp2, pt)
        self._prev_ref = bcp2
        self._prev = pt
    
    def _qCurveToOne(self, bcp, pt):
        self._checkBbox(bcp, pt)
        # TODO extrema check on quadratic curves
        #self._checkExtremumQuad(bcp1, bcp2, pt)
        self._checkSmooth(self._prev, pt)
        self._prev_ref = bcp
        self._prev = pt
    
    def addComponent(self, baseGlyph, transformation):
        pass
    
    def _curveTests(self, bcp1, bcp2, pt):
        self._globalExtremumTest(self._prev, bcp1, bcp2, pt)
        self._localExtremumTest(self._prev, bcp1, bcp2, pt)
        self._checkSmooth(self._prev, bcp1)
        
