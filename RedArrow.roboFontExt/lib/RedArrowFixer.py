from __future__ import print_function, division
from AppKit import NSBezierPath, NSImage
from os.path import join, dirname, isfile
from fontTools.misc.arrayTools import pointInRect
from lib.tools import bezierTools # for single point click selection
from lib.tools.defaults import getDefaultColor # for drawing the selection marquee
from mojo.events import BaseEventTool, installTool
from mojo.drawingTools import fill, oval, restore, save, stroke

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
    print("Warning: Toolbar icon not found at path: '%s'" % iconpath)

class ErrorSelection(object):
    def __init__(self):
        self.errors = []
    
    def __repr__(self):
        return str(self.errors)
    
    def resetSelection(self):
        self.errors = []
    
    def addError(self, p, shiftDown):
        #if contour in self.errors:
        #    if not p in self.errors[contour]:
        #        self.errors.append((p, contour))
        #else:
        #    self.errors[contour] = [p]
        if not p in self.errors:
            self.errors.append(p)
    
    def draw(self, scale):
        size = 20 * scale
        save()
        fill(0.2, 0.5, 0.35, 0.3)
        stroke(None)
        #for contour in self.errors.keys():
        #    for p in contour:
        #        oval(p[0]-5, p[1]-5, 10, 10)
        for p in self.errors:
            oval(p[0]-size/2, p[1]-size/2, size, size)
        restore()

class RedArrowFixerTool(BaseEventTool):
    
    def setup(self):
        self.errorSelection = ErrorSelection()
        self.pStart = None
        self.pEnd = None
        self._selectedMouseDownPoint = None
    
    def getToolbarIcon(self):
        return toolbarIcon
    
    def getToolbarTip(self):
        return "Red Arrow Fixer"
    
    def becomeActive(self):
        if DEBUG:
            print("becomeActive")
        self.ui = RedArrowUI()
        self.ui.fixer = self
    
    def becomeInactive(self):
        if DEBUG:
            print("becomeInactive")
        self.ui.windowCloseCallback(None)
        self.ui.w.close()
    
    def fixSelected(self):
        if DEBUG:
            print("fixSelected")
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
            for error in self.ui.errors:
                p = error.position
                if pointInRect(p, box):
                    self.errorSelection.addError(p, self.shiftDown)
                    self._selectedMouseDownPoint = p
    
    def mouseDown(self, point, clickCount):
        if not(self.shiftDown):
            self.errorSelection.resetSelection()
        if clickCount > 1:
            #self._newAnchor(point)
            pass
        else:
            self.pStart = point
            self.pEnd = None
            s = self._view.getGlyphViewOnCurvePointsSize(minSize=7)
            for error in self.ui.errors:
                p = error.position
                if bezierTools.distanceFromPointToPoint(p, point) < s:
                    self.errorSelection.addError(p, self.shiftDown)
                    self._selectedMouseDownPoint = p
                    break
    
    def mouseUp(self, point):
        self.pEnd = point
        self._getSelectedPoints()
        #print(self.errorSelection)
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
    
    def drawSelection(self, scale):
        self.errorSelection.draw(scale)
        
installTool(RedArrowFixerTool())
print("Red Arrow Fixer installed in tool bar.")
