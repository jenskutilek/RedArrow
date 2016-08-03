import vanilla
from defconAppKit.windows.baseWindow import BaseWindowController
from lib.tools.defaults import getDefault
from mojo.events import addObserver, removeObserver
from mojo.roboFont import version as roboFontVersion
from mojo.roboFont import RGlyph
from mojo.UI import UpdateCurrentGlyphView
from mojo.drawingTools import save, restore, fill, stroke, line, strokeWidth, rect, translate, text, fontSize, font, lineJoin, lineCap
#from time import time
from string import strip

DEBUG = False

if DEBUG:
    import outlineTestPen
    reload(outlineTestPen)
from outlineTestPen import OutlineTestPen

tool_mode = True

options = {
    "extremum_calculate_badness": True,
    "fractional_ignore_point_zero": True,
    "show_bbox": True,
    
    "extremum_ignore_badness_below": 0,
    "smooth_connection_max_distance": 4,
    "collinear_vectors_max_distance": 2,
    "semi_hv_vectors_min_distance": 30,
    "zero_handles_max_distance": 0,
    
    "grid_length": getDefault('glyphViewRoundValues'),
}

class RedArrowUI(BaseWindowController):
    def __init__(self):
        
        self.drawing = False
        self.fixer = None
        self.showLabels = False
        self.errors = {}
        
        self.w = vanilla.FloatingWindow((240, 298), "RedArrow", closable = not(tool_mode))
        x0 = 25
        x1 = 150
        y = 5
        self.w.showGlyphStatusButton = vanilla.CheckBox((10, y , -10, 25), "Show Red Arrows",
            callback=self.checkGlyphStatus,
            sizeStyle="small",
        )
        if tool_mode:
            y += 28
            self.w.fixSelectedButton = vanilla.Button((10, y , -10, 25), "Fix Selected",
                callback=self._fixSelected,
                sizeStyle="small",
            )
        y += 28
        self.w.drawLabels = vanilla.CheckBox((10, y, -10, 25), "Show Labels",
            callback=self.toggleShowLabels,
            sizeStyle="small",
        )
        y += 28
        self.w.optionsShowBoundingBox = vanilla.CheckBox((10, y, -10, 25), "Show Bounding Box",
            value=options.get("show_bbox"),
            callback=self.setShowBoundingBox,
            sizeStyle="small",
        )
        y += 28
        self.w.optionsFractionalIgnorePointZero = vanilla.CheckBox((10, y, -10, 25), "Ignore .0 Fractional Coordinates",
            value=options.get("fractional_ignore_point_zero"),
            callback=self.setFractionalIgnorePointZero,
            sizeStyle="small",
        )
        
        y += 42
        self.w.optionsThresholdLabel = vanilla.TextBox((8, y, -10, 25), u"Detection Threshold Values (\u2030 em):",
            sizeStyle="small",
        )
        
        y += 28
        self.w.optionsExtremumToleranceLabel = vanilla.TextBox((x0, y, 120, 25), "Extremum Points",
            sizeStyle="small",
        )
        self.w.optionsExtremumTolerance = vanilla.EditText((x1, y-3, 32, 21),
            options.get("extremum_ignore_badness_below"),
            callback=self.setExtremumTolerance,
            sizeStyle="small",
        )
        
        y += 28
        self.w.optionsZeroHandlesToleranceLabel = vanilla.TextBox((x0, y, x1-x0, 25), "Zero Handles",
            sizeStyle="small",
        )
        self.w.optionsZeroHandlesTolerance = vanilla.EditText((x1, y-3, 32, 21),
            options.get("zero_handles_max_distance"),
            callback=self.setZeroHandlesTolerance,
            sizeStyle="small",
        )
        
        y += 28
        self.w.optionsSmoothConnectionMaxDistLabel = vanilla.TextBox((x0, y, x1-x0, 25), "Smooth Connections",
            sizeStyle="small",
        )
        self.w.optionsSmoothConnectionMaxDist = vanilla.EditText((x1, y-3, 32, 21),
            options.get("smooth_connection_max_distance"),
            callback=self.setSmoothConnectionMaxDist,
            sizeStyle="small",
        )
        
        y += 28
        self.w.optionsCollinearVectorsMaxDistLabel = vanilla.TextBox((x0, y, x1-x0, 25), "Collinear Lines",
            sizeStyle="small",
        )
        self.w.optionsCollinearVectorsMaxDist = vanilla.EditText((x1, y-3, 32, 21),
            options.get("collinear_vectors_max_distance"),
            callback=self.setCollinearVectorsMaxDist,
            sizeStyle="small",
        )
               
        y += 28
        self.w.optionsSemiHVVectorsMinDistLabel = vanilla.TextBox((x0, y, x1-x0, 25), "Semi-hor./-vert. Lines",
            sizeStyle="small",
        )
        self.w.optionsSemiHVVectorsMinDist = vanilla.EditText((x1, y-3, 32, 21),
            options.get("semi_hv_vectors_min_distance"),
            callback=self.setSemiHVVectorsMinDist,
            sizeStyle="small",
        )
        self.w.showGlyphStatusButton.set(True)
        self.showRedArrows()
        self.setUpBaseWindowBehavior()
        self.w.open()
    
    
    def checkGlyphStatus(self, sender):
        active = sender.get()
        if active:
            self.showRedArrows()
        else:
            self.hideRedArrows()
    
    def showRedArrows(self):
        if roboFontVersion > "1.5.1":
            _registerFactory()
        self.addObservers()
        self.drawing = True
        UpdateCurrentGlyphView()
    
    def hideRedArrows(self):
        self.errors = {}
        self.removeObservers()
        if roboFontVersion > "1.5.1":
            _unregisterFactory()
        self.drawing = False
        UpdateCurrentGlyphView()
    
    def toggleShowLabels(self, sender):
        if self.showLabels:
            self.showLabels = False
        else:
            self.showLabels = True
        UpdateCurrentGlyphView()
    
    
    def setShowBoundingBox(self, sender):
        options["show_bbox"] = sender.get()
        UpdateCurrentGlyphView()
    
    def setFractionalIgnorePointZero(self, sender):
        options["fractional_ignore_point_zero"] = sender.get()
        UpdateCurrentGlyphView()
    
    def setExtremumTolerance(self, sender):
        options["extremum_ignore_badness_below"] = int(sender.get())
        UpdateCurrentGlyphView()
    
    def setZeroHandlesTolerance(self, sender):
        options["zero_handles_max_distance"] = int(sender.get())
        UpdateCurrentGlyphView()
    
    def setSmoothConnectionMaxDist(self, sender):
        options["smooth_connection_max_distance"] = int(sender.get())
        UpdateCurrentGlyphView()
    
    def setCollinearVectorsMaxDist(self, sender):
        options["collinear_vectors_max_distance"] = int(sender.get())
        UpdateCurrentGlyphView()
    
    def setSemiHVVectorsMinDist(self, sender):
        options["semi_hv_vectors_min_distance"] = int(sender.get())
        UpdateCurrentGlyphView()
    
    def addObservers(self):
        addObserver(self, "_drawArrows", "drawInactive")
        addObserver(self, "_drawArrows", "drawBackground")
        if roboFontVersion >= "1.7":
            addObserver(self, "_drawGlyphCellArrows", "glyphCellDrawBackground")
        #addObserver(self, "_updateOutlineCheck", "currentGlyphChanged")
        #addObserver(self, "_updateOutlineCheck", "draw")
    
    
    def removeObservers(self):
        removeObserver(self, "drawBackground")
        removeObserver(self, "drawInactive")
        if roboFontVersion >= "1.7":
            removeObserver(self, "glyphCellDrawBackground")
        #removeObserver(self, "currentGlyphChanged")
        #removeObserver(self, "draw")
    
    def _fixSelected(self, sender=None):
        if self.fixer is not None:
            self.fixer.fixSelected()
    
    def _drawArrow(self, position, kind, size, width):
        if position is not None:
            x, y = position
        else:
            x = 0
            y = 0
        save()
        translate(x, y)
        fill(0, 0.8, 0, 0.1)
        strokeWidth(width)
        stroke(0.9, 0.2, 0.1, 1)
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
            self.errors = glyph.getRepresentation("de.kutilek.RedArrow.report")
        else:
            self.errors = getGlyphReport(font, glyph)
        
        scale = notification["scale"]
        size = 10 * scale
        width = 3 * scale
        errors_by_position = {}
        for e in self.errors:
            #if not e.kind == "Vector on closepath": # FIXME
            if e.position in errors_by_position:
                errors_by_position[e.position].extend([e])
            else:
                errors_by_position[e.position] = [e]
        for pos, errors in errors_by_position.iteritems():
            message = ""
            for e in errors:
                if e.badness is None or not DEBUG:
                    message += "%s, " % (e.kind)
                else:
                    message += "%s (Severity %0.1f), " % (e.kind, e.badness)
            self._drawArrow(pos, message.strip(", "), size, width)
        if options.get("show_bbox"):
            box = glyph.box
            if box is not None:
                save()
                fill(None)
                strokeWidth(0.5 * scale)
                stroke(1, 0, 0, 0.5)
                x, y, w, h = box
                rect(x, y, w-x, h-y)
                restore()
    
    def _drawGlyphCellArrow(self, num_errors):
        x = 3
        y = 3
        width = 2
        size = 7
        save()
        translate(4, 4)
        
        fill(0.9, 0.4, 0.3, 1)
        rect(-1, -1, size+1, size+1)
        
        lineJoin("round")
        lineCap("butt") # butt, square, round
        strokeWidth(width)
        stroke(1, 1, 1)
        line(-width/2, 0, size, 0)
        line(0, -width/2, 0, size)
        line(width/2, width/2, size-0.5, size-0.5)
        
        restore()
    
    def _drawGlyphCellArrows(self, notification):
        glyph = notification["glyph"]
        if glyph is None:
            return
        num_errors = len(glyph.getRepresentation("de.kutilek.RedArrow.report"))
        if num_errors > 0:
            self._drawGlyphCellArrow(num_errors)
    
    
    def windowCloseCallback(self, sender):
        if self.drawing:
            self.removeObservers()
            if roboFontVersion > "1.5.1":
                _unregisterFactory()
        UpdateCurrentGlyphView()
        super(RedArrowUI, self).windowCloseCallback(sender)



def getGlyphReport(font, glyph, options):
    #start = time()
    options["grid_length"] = getDefault('glyphViewRoundValues')
    myPen = OutlineTestPen(font, options)
    glyph.drawPoints(myPen)
    #stop = time()
    #print "updateOutlineCheck in %0.2f ms." % ((stop-start) * 1000)
    return myPen.errors


def RedArrowReportFactory(glyph, font):
    glyph = RGlyph(glyph)
    font = glyph.getParent()
    return getGlyphReport(font, glyph, options)


def _registerFactory():
    # From https://github.com/typesupply/glyph-nanny/blob/master/Glyph%20Nanny.roboFontExt/lib/glyphNanny.py
    # always register if debugging
    # otherwise only register if it isn't registered
    from defcon import addRepresentationFactory, removeRepresentationFactory
    from defcon.objects import glyph as _xxxHackGlyph
    if DEBUG:
        if "de.kutilek.RedArrow.report" in _xxxHackGlyph._representationFactories:
            for font in AllFonts():
                for glyph in font:
                    glyph.naked().destroyAllRepresentations()
            removeRepresentationFactory("de.kutilek.RedArrow.report")
        addRepresentationFactory("de.kutilek.RedArrow.report", RedArrowReportFactory)
    else:
        if "de.kutilek.RedArrow.report" not in _xxxHackGlyph._representationFactories:
            addRepresentationFactory("de.kutilek.RedArrow.report", RedArrowReportFactory)


def _unregisterFactory():
    from defcon import removeRepresentationFactory
    try:
        removeRepresentationFactory("de.kutilek.RedArrow.report")
    except:
        pass


if __name__ == "__main__":
    tool_mode = False
    OpenWindow(RedArrowUI)