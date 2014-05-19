import vanilla
from defconAppKit.windows.baseWindow import BaseWindowController
from mojo.events import addObserver, removeObserver
from mojo.UI import UpdateCurrentGlyphView
from mojo.drawingTools import save, restore, fill, stroke, line, strokeWidth, rect, translate, text

import pen
reload(pen)
from pen import RedArrowPen

class RedArrowUI(BaseWindowController):
    def __init__(self):
        
        self.drawing = False
        self.errors = []
        
        self.w = vanilla.FloatingWindow((180, 280), "RedArrow")
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
        y += 30
                
        self.w.clearGlyphStatusButton.enable(False)
        #self.w.showGlyphStatusButton.enable(True)
        self.setUpBaseWindowBehavior()
        self.w.open()
    
    
    def checkGlyphStatus(self, sender):
        self.w.showGlyphStatusButton.enable(False)
        self.addObservers()
        self.drawing = True
        
        g = CurrentGlyph()
        
        if g is not None:
            myPen = RedArrowPen(CurrentFont(), True, 1)
            g.draw(myPen)
            self.errors = myPen.errors
        self.w.clearGlyphStatusButton.enable(True)
        UpdateCurrentGlyphView()
        
    
    def uncheckGlyphStatus(self, sender):
        self.w.clearGlyphStatusButton.enable(False)
        self.w.showGlyphStatusButton.enable(True)
        self.errors = []
        self.removeObservers()
        self.drawing = False
        UpdateCurrentGlyphView()
    
    
    def addObservers(self):
        addObserver(self, "drawArrows", "drawInactive")
        addObserver(self, "drawArrows", "drawBackground")
    
    
    def removeObservers(self):
        removeObserver(self, "drawBackground")
        removeObserver(self, "drawInactive")
    
    
    def drawArrow(self, position, kind, size, width):
        x, y = position
        save()
        translate(x, y)
        fill(0, 0.8, 0, 0.1)
        strokeWidth(width)
        stroke(1.0, 0, 0, 1)
        line(0, 0, size, 0)
        line(0, 0, 0, -size)
        line(0, 0, size, -size)
        #rect(x-scale, y-scale, scale, scale)
        fill(0, 0, 0, 1)
        stroke(None)
        text(kind, (size * 1.5, - size))
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