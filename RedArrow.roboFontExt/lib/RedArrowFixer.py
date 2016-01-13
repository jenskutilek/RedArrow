from AppKit import NSBezierPath, NSImage
from os.path import join, dirname, isfile
from fontTools.misc.arrayTools import pointInRect
from lib.tools import bezierTools # for single point click selection
from lib.tools.defaults import getDefaultColor # for drawing the selection marquee
from mojo.events import BaseEventTool, installTool

DEBUG = True

if DEBUG:
    import RedArrow
    reload(RedArrow)
from RedArrow import RedArrowUI


iconpath = join(dirname(__file__), "RedArrowFixer.pdf")

if isfile(iconpath):
    toolbarIcon = NSImage.alloc().initByReferencingFile_(iconpath)
else:
    toolbarIcon = None
    print "Warning: Toolbar icon not found: <%s>" % iconpath

class RedArrowFixerTool(BaseEventTool):
    
    def setup(self):
        self.pStart = None
        self.pEnd = None
        self._selectedMouseDownPoint = None
    
    def getToolbarIcon(self):
        return toolbarIcon
    
    def getToolbarTip(self):
        return "Red Arrow Fixer"
    
    def becomeActive(self):
        if DEBUG:
            print "becomeActive"
        self.ui = RedArrowUI()
        self.ui.fixer = self
    
    def becomeInactive(self):
        if DEBUG:
            print "becomeInactive"
        self.ui.windowCloseCallback(None)
        self.ui.w.close()
    
    def fixSelected(self):
        if DEBUG:
            print "fixSelected"
        # Add an anchor at position p
        g = CurrentGlyph()
        #g.prepareUndo(undoTitle="Add anchor %s to /%s" % (newAnchorName, g.name))
        # TODO Fix problems
        #g.performUndo()
    
    def _normalizeBox(self, p0, p1):
        # normalize selection rectangle so it is always positive
        return (min(p0.x, p1.x), min(p0.y, p1.y), max(p0.x, p1.x), max(p0.y, p1.y))
    
    def _getSelectedPoints(self):
        if self.pStart and self.pEnd:
            box = self._normalizeBox(self.pStart, self.pEnd)
            for contour in self._glyph:
                for p in contour.onCurvePoints:
                    if pointInRect((p.x, p.y), box):
                        self.selection.addPoint(p, self.shiftDown, contour=contour)
                        self._selectedMouseDownPoint = (p.x, p.y)
                for anchor in self._glyph.anchors:
                    if pointInRect((anchor.x, anchor.y), box):
                        self.selection.addAnchor(anchor, self.shiftDown)
                        self._selectedMouseDownPoint = (anchor.x, anchor.y)
    
    def mouseDown(self, point, clickCount):
        if not(self.shiftDown):
            self.selection.resetSelection()
        if clickCount > 1:
            #self._newAnchor(point)
            pass
        else:
            self.pStart = point
            self.pEnd = None
            s = self._view.getGlyphViewOnCurvePointsSize(minSize=7)
            for contour in self._glyph:
                for p in contour.onCurvePoints:
                    if bezierTools.distanceFromPointToPoint(p, point) < s:
                        self.selection.addPoint(p, self.shiftDown, contour=contour)
                        self._selectedMouseDownPoint = (p.x, p.y)
                        return
                for anchor in self._glyph.anchors:
                    if bezierTools.distanceFromPointToPoint(anchor, point) < s:
                        self.selection.addAnchor(anchor, self.shiftDown)
                        self._selectedMouseDownPoint = (anchor.x, anchor.y)
                        return
    
    def mouseUp(self, point):
        self.pEnd = point
        self._getSelectedPoints()
        self.pStart = None
        self.pEnd = None
        self._selectedMouseDownPoint = None
    
    def mouseDragged(self, point, delta):
        self.pEnd = point
        #self._getSelectedPoints()
    
    def draw(self, scale):
        if self.isDragging() and self.pStart and self.pEnd:
            r = self.getMarqueRect()
            if r:
                color = getDefaultColor('glyphViewSelectionMarqueColor')
                color.set()
                path = NSBezierPath.bezierPathWithRect_(r)
                path.fill()
            return
        self.drawSelection(scale)
        
installTool(RedArrowFixerTool())
print "Red Arrow Fixer installed in tool bar."