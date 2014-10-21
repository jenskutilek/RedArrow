import vanilla
from defconAppKit.windows.baseWindow import BaseWindowController
from mojo.events import addObserver, removeObserver
from mojo.roboFont import version as roboFontVersion
from mojo.UI import UpdateCurrentGlyphView
from mojo.drawingTools import save, restore, fill, stroke, line, strokeWidth, rect, translate, text, fontSize, font
#from time import time
from string import strip

DEBUG = False

if DEBUG:
    import outlineTestPen
    reload(outlineTestPen)
from outlineTestPen import OutlineTestPen

class RedArrowUI(BaseWindowController):
    def __init__(self):
        
        self.drawing = False
        self.showLabels = False
        self.errors = {}
        
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
    
    
    def checkGlyphStatus(self, sender):
        self.w.showGlyphStatusButton.enable(False)
        self.addObservers()
        self.drawing = True
        self.w.clearGlyphStatusButton.enable(True)
        UpdateCurrentGlyphView()
        
    
    def uncheckGlyphStatus(self, sender):
        self.w.clearGlyphStatusButton.enable(False)
        self.w.showGlyphStatusButton.enable(True)
        self.errors = {}
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
        addObserver(self, "_drawArrows", "drawInactive")
        addObserver(self, "_drawArrows", "drawBackground")
        #addObserver(self, "_updateOutlineCheck", "currentGlyphChanged")
        #addObserver(self, "_updateOutlineCheck", "draw")
    
    
    def removeObservers(self):
        removeObserver(self, "drawBackground")
        removeObserver(self, "drawInactive")
        #removeObserver(self, "currentGlyphChanged")
        #removeObserver(self, "draw")
    
    
    def _drawArrow(self, position, kind, size, width):
        x, y = position
        save()
        translate(x, y)
        fill(0, 0.8, 0, 0.1)
        strokeWidth(width)
        stroke(0.9, 0.1, 0, 0.85)
        line(-width/2, 0, size, 0)
        line(0, width/2, 0, -size)
        line(0, 0, size, -size)
        #rect(x-scale, y-scale, scale, scale)
        if self.showLabels:
            fill(0.4, 0.4, 0.4, 0.7)
            stroke(None)
            font("LucidaGrande")
            fontSize(int(round(size * 1.1)))
            text(kind, (int(round(size * 1.8)), int(round(-size))))
        restore()
    
    
    def _drawArrows(self, notification):
        glyph = notification["glyph"]
        if glyph is None:
            return
        font = glyph.getParent()
        
        if roboFontVersion > "1.5.1":
            self.errors = glyph.getRepresentation("de.netzallee.RedArrow.report")
        else:
            self.errors = getGlyphReport(font, glyph)
        
        scale = notification["scale"]
        size = 10 * scale
        width = 3 * scale
        errors_by_position = {}
        for e in self.errors:
            if not e.kind == "Vector on closepath": # FIXME
                if e.position in errors_by_position:
                    errors_by_position[e.position].extend([e])
                else:
                    errors_by_position[e.position] = [e]
        for pos, errors in errors_by_position.iteritems():
            message = ""
            for e in errors:
                if e.badness is None:
                    message += "%s, " % (e.kind)
                else:
                    message += "%s (Severity %0.1f), " % (e.kind, e.badness)
            self._drawArrow(pos, message.strip(", "), size, width)
    
    
    def windowCloseCallback(self, sender):
        if self.drawing:
            self.removeObservers()
        if roboFontVersion > "1.5.1":
            removeRepresentationFactory("de.netzallee.RedArrow.report")
        UpdateCurrentGlyphView()
        super(RedArrowUI, self).windowCloseCallback(sender)



def getGlyphReport(font, glyph):
    #start = time()
    myPen = OutlineTestPen(font)
    glyph.draw(myPen)
    #stop = time()
    #print "updateOutlineCheck in %0.2f ms." % ((stop-start) * 1000)
    return myPen.errors


def RedArrowReportFactory(glyph, font):
    glyph = RGlyph(glyph)
    font = glyph.getParent()
    return getGlyphReport(font, glyph)


def _registerFactory():
    # From https://github.com/typesupply/glyph-nanny/blob/master/Glyph%20Nanny.roboFontExt/lib/glyphNanny.py
    # always register if debugging
    # otherwise only register if it isn't registered
    from defcon import addRepresentationFactory, removeRepresentationFactory
    from defcon.objects import glyph as _xxxHackGlyph
    if DEBUG:
        if "de.netzallee.RedArrow.report" in _xxxHackGlyph._representationFactories:
            for font in AllFonts():
                for glyph in font:
                    glyph.naked().destroyAllRepresentations()
            removeRepresentationFactory("de.netzallee.RedArrow.report")
        addRepresentationFactory("de.netzallee.RedArrow.report", RedArrowReportFactory)
    else:
        if "de.netzallee.RedArrow.report" not in _xxxHackGlyph._representationFactories:
            addRepresentationFactory("de.netzallee.RedArrow.report", RedArrowReportFactory)


def _unregisterFactory():
    from defcon import removeRepresentationFactory
    removeRepresentationFactory("de.netzallee.RedArrow.report")


if __name__ == "__main__":
    if roboFontVersion > "1.5.1":
        _registerFactory()
    RedArrowUI()