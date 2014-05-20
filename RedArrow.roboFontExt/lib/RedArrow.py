import vanilla
from defconAppKit.windows.baseWindow import BaseWindowController
from mojo.events import addObserver, removeObserver
from mojo.UI import UpdateCurrentGlyphView
from mojo.drawingTools import save, restore, fill, stroke, line, strokeWidth, rect, translate, text, fontSize, font
from time import time

import pen
reload(pen)
from pen import RedArrowPen

class RedArrowUI(BaseWindowController):
    def __init__(self):
        
        self.drawing = False
        self.showLabels = False
        self.errors = []
        
        self.w = vanilla.FloatingWindow((140, 86), "RedArrow")
        y = 5
        self.w.showGlyphStatusButton = vanilla.Button((10, y , -10, 25), "Show red arrows",
            callback=self.checkGlyphStatus,
            sizeStyle="small",
        )
        y += 26
        self.w.clearGlyphStatusButton = vanilla.Button((10, y , -10, 25), "Clear red arrows",
            callback=self.uncheckGlyphStatus,
            sizeStyle="small",
        )
        y += 28
        self.w.drawLabels = vanilla.CheckBox((10, y, -10, 25), "Show labels",
            callback=self.toggleShowLabels,
            sizeStyle="small",
        )
                
        self.w.clearGlyphStatusButton.enable(False)
        #self.w.showGlyphStatusButton.enable(True)
        self.setUpBaseWindowBehavior()
        self.w.open()
    
    
    def updateOutlineCheck(self, sender=None):
        start = time()
        g = CurrentGlyph()
        
        if g is not None:
            myPen = RedArrowPen(CurrentFont(), True, 1)
            g.draw(myPen)
            self.errors = myPen.errors
        UpdateCurrentGlyphView()
        stop = time()
        print "updateOutlineCheck in %0.2f ms." % ((stop-start) * 1000)
    
    
    def checkGlyphStatus(self, sender):
        self.w.showGlyphStatusButton.enable(False)
        self.addObservers()
        self.drawing = True
        self.updateOutlineCheck()
        self.w.clearGlyphStatusButton.enable(True)
        
    
    def uncheckGlyphStatus(self, sender):
        self.w.clearGlyphStatusButton.enable(False)
        self.w.showGlyphStatusButton.enable(True)
        self.errors = []
        self.removeObservers()
        self.drawing = False
        UpdateCurrentGlyphView()
    
    
    def toggleShowLabels(self, sender):
        if self.showLabels:
            self.showLabels = False
        else:
            self.showLabels = True
        UpdateCurrentGlyphView()
    
    
    def addObservers(self):
        addObserver(self, "drawArrows", "drawInactive")
        addObserver(self, "drawArrows", "drawBackground")
        addObserver(self, "updateOutlineCheck", "currentGlyphChanged")
    
    
    def removeObservers(self):
        removeObserver(self, "drawBackground")
        removeObserver(self, "drawInactive")
        removeObserver(self, "currentGlyphChanged")
    
    
    def drawArrow(self, position, kind, size, width):
        x, y = position
        save()
        translate(x, y)
        fill(0, 0.8, 0, 0.1)
        strokeWidth(width)
        stroke(0.9, 0.1, 0, 1)
        line(-width/2, 0, size, 0)
        line(0, width/2, 0, -size)
        line(0, 0, size, -size)
        #rect(x-scale, y-scale, scale, scale)
        if self.showLabels:
            fill(0, 0, 0, 1)
            stroke(None)
            font("LucidaGrande")
            fontSize(int(round(size * 1.1)))
            text(kind, (int(round(size * 1.5)), int(round(-1.05 * size))))
        restore()
    
    
    def drawArrows(self, notification):
        scale = notification["scale"]
        size = 10 * scale
        width = 3 * scale
        #print scale
        for e in self.errors:
            self.drawArrow(e.position, e.kind, size, width)
    
    
    def windowCloseCallback(self, sender):
        if self.drawing:
            self.removeObservers()
        UpdateCurrentGlyphView()
        super(RedArrowUI, self).windowCloseCallback(sender)
    

RedArrowUI()