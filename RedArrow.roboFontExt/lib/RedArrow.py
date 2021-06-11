import vanilla

from lib.tools.defaults import getDefault
from mojo.subscriber import (
    Subscriber,
    registerGlyphEditorSubscriber,
    WindowController,
)
from mojo.UI import UpdateCurrentGlyphView
from outlineTestPen import OutlineTestPen
from RedArrowDrawing import drawArrows

from time import time


DEBUG = False

tool_mode = True

options = {
    "extremum_calculate_badness": True,
    "fractional_ignore_point_zero": True,
    "show_bbox": False,
    "extremum_ignore_badness_below": 0,
    "smooth_connection_max_distance": 4,
    "collinear_vectors_max_distance": 2,
    "semi_hv_vectors_min_distance": 30,
    "zero_handles_max_distance": 0,
    "grid_length": getDefault("glyphViewRoundValues"),
}


class RedArrowUI(Subscriber, WindowController):
    def build(self):
        glyphEditor = self.getGlyphEditor()
        self.container = glyphEditor.extensionContainer(
            identifier="de.kutilek.RedArrow.foreground",
            location="foreground",
            clear=True,
        )

        self.drawing = False
        self.fixer = None
        self.show_labels = False
        self.mouse_position = (0, 0)
        self.errors = {}
        self.track_mouse = False

        self.w = vanilla.FloatingWindow(
            (240, 298), "RedArrow", closable=not (tool_mode)
        )
        x0 = 25
        x1 = 150
        y = 5
        # self.w.showGlyphStatusButton = vanilla.CheckBox(
        #     (10, y, -10, 25),
        #     "Show Red Arrows",
        #     callback=self.checkGlyphStatus,
        #     sizeStyle="small",
        # )
        if tool_mode:
            y += 28
            self.w.fixSelectedButton = vanilla.Button(
                (10, y, -10, 25),
                "Fix Selected",
                callback=self._fixSelected,
                sizeStyle="small",
            )
        y += 28
        self.w.drawLabels = vanilla.CheckBox(
            (10, y, -10, 25),
            "Show Labels",
            callback=self.toggleShowLabels,
            sizeStyle="small",
        )
        y += 28
        self.w.optionsShowBoundingBox = vanilla.CheckBox(
            (10, y, -10, 25),
            "Show Bounding Box",
            value=options.get("show_bbox"),
            callback=self.setShowBoundingBox,
            sizeStyle="small",
        )
        y += 28
        self.w.optionsFractionalIgnorePointZero = vanilla.CheckBox(
            (10, y, -10, 25),
            "Ignore .0 Fractional Coordinates",
            value=options.get("fractional_ignore_point_zero"),
            callback=self.setFractionalIgnorePointZero,
            sizeStyle="small",
        )

        y += 42
        self.w.optionsThresholdLabel = vanilla.TextBox(
            (8, y, -10, 25),
            u"Detection Threshold Values (\u2030 em):",
            sizeStyle="small",
        )

        y += 28
        self.w.optionsExtremumToleranceLabel = vanilla.TextBox(
            (x0, y, 120, 25),
            "Extremum Points",
            sizeStyle="small",
        )
        self.w.optionsExtremumTolerance = vanilla.EditText(
            (x1, y - 3, 32, 21),
            options.get("extremum_ignore_badness_below"),
            callback=self.setExtremumTolerance,
            sizeStyle="small",
        )

        y += 28
        self.w.optionsZeroHandlesToleranceLabel = vanilla.TextBox(
            (x0, y, x1 - x0, 25),
            "Zero Handles",
            sizeStyle="small",
        )
        self.w.optionsZeroHandlesTolerance = vanilla.EditText(
            (x1, y - 3, 32, 21),
            options.get("zero_handles_max_distance"),
            callback=self.setZeroHandlesTolerance,
            sizeStyle="small",
        )

        y += 28
        self.w.optionsSmoothConnectionMaxDistLabel = vanilla.TextBox(
            (x0, y, x1 - x0, 25),
            "Smooth Connections",
            sizeStyle="small",
        )
        self.w.optionsSmoothConnectionMaxDist = vanilla.EditText(
            (x1, y - 3, 32, 21),
            options.get("smooth_connection_max_distance"),
            callback=self.setSmoothConnectionMaxDist,
            sizeStyle="small",
        )

        y += 28
        self.w.optionsCollinearVectorsMaxDistLabel = vanilla.TextBox(
            (x0, y, x1 - x0, 25),
            "Collinear Lines",
            sizeStyle="small",
        )
        self.w.optionsCollinearVectorsMaxDist = vanilla.EditText(
            (x1, y - 3, 32, 21),
            options.get("collinear_vectors_max_distance"),
            callback=self.setCollinearVectorsMaxDist,
            sizeStyle="small",
        )

        y += 28
        self.w.optionsSemiHVVectorsMinDistLabel = vanilla.TextBox(
            (x0, y, x1 - x0, 25),
            "Semi-hor./-vert. Lines",
            sizeStyle="small",
        )
        self.w.optionsSemiHVVectorsMinDist = vanilla.EditText(
            (x1, y - 3, 32, 21),
            options.get("semi_hv_vectors_min_distance"),
            callback=self.setSemiHVVectorsMinDist,
            sizeStyle="small",
        )
        # self.w.showGlyphStatusButton.set(True)
        # self.showRedArrows()
        # self.setUpBaseWindowBehavior()

    def destroy(self):
        print("destroy")
        self.container.clearSublayers()

    def started(self):
        self.w.open()
        self.current_layer = CurrentGlyph()
        self._updateOutlineCheck(self.current_layer)

    def glyphEditorGlyphDidChange(self, info):
        print("glyphEditorGlyphDidChange")
        print(info)
        self.current_layer = info["glyph"]
        if self.current_layer is None:
            return
        self._updateOutlineCheck(self.current_layer)

    def toggleShowLabels(self, sender):
        if self.show_labels:
            self.show_labels = False
            if not self.track_mouse:
                # addObserver(self, "mouseMoved", "mouseMoved")
                self.track_mouse = True
        else:
            self.show_labels = True
            if self.track_mouse:
                # removeObserver(self, "mouseMoved")
                self.track_mouse = False
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

    def mouseMoved(self, info):
        point = info["point"]
        self.mouse_position = (point.x, point.y)
        UpdateCurrentGlyphView()

    # def addObservers(self):
    #     addObserver(self, "_drawArrows", "drawInactive")
    #     addObserver(self, "_drawArrows", "drawBackground")
    #     addObserver(self, "_drawGlyphCellArrows", "glyphCellDrawBackground")
    #     # addObserver(self, "_updateOutlineCheck", "currentGlyphChanged")
    #     # addObserver(self, "_updateOutlineCheck", "draw")
    #     addObserver(self, "mouseMoved", "mouseMoved")
    #     self.track_mouse = True

    # def removeObservers(self):
    #     removeObserver(self, "drawBackground")
    #     removeObserver(self, "drawInactive")
    #     removeObserver(self, "glyphCellDrawBackground")
    #     # removeObserver(self, "currentGlyphChanged")
    #     # removeObserver(self, "draw")
    #     removeObserver(self, "mouseMoved")
    #     self.track_mouse = False

    def _fixSelected(self, sender=None):
        if self.fixer is not None:
            self.fixer.fixSelected()

    def _updateOutlineCheck(self, glyph):
        if glyph is None:
            return

        errors = getGlyphReport(glyph, options)
        drawArrows(errors, 1, options.get("show_bbox"), self.current_layer)

    # def windowCloseCallback(self, sender):
    #     if self.drawing:
    #         self.removeObservers()
    #         _unregisterFactory()
    #     UpdateCurrentGlyphView()
    #     super(RedArrowUI, self).windowCloseCallback(sender)


def getGlyphReport(glyph, options):
    start = time()
    options["grid_length"] = getDefault("glyphViewRoundValues")
    myPen = OutlineTestPen(glyph.font, options)
    glyph.drawPoints(myPen)
    stop = time()
    print("updateOutlineCheck in %0.2f ms." % ((stop-start) * 1000))
    print(myPen.errors)
    return myPen.errors


if __name__ == "__main__":
    tool_mode = False
    registerGlyphEditorSubscriber(RedArrowUI)
