from __future__ import print_function, division
import vanilla

from AppKit import (
    NSAffineTransform,
    NSBezierPath,
    NSColor,
    NSFont,
    NSFontAttributeName,
    NSForegroundColorAttributeName,
    NSMakeRect,
    NSMutableParagraphStyle,
    NSPoint,
    NSRect,
    NSString,
)
from geometry_functions import distance_between_points
from math import atan2, cos, pi, sin, degrees

from defconAppKit.windows.baseWindow import BaseWindowController
from lib.tools.defaults import getDefault
from mojo.events import addObserver, removeObserver
from mojo.roboFont import version as roboFontVersion
from mojo.roboFont import RGlyph
from mojo.UI import UpdateCurrentGlyphView
from mojo.drawingTools import (
    save,
    restore,
    fill,
    stroke,
    line,
    strokeWidth,
    rect,
    translate,
    text,
    fontSize,
    font,
    lineJoin,
    lineCap,
)

# from time import time

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
    "grid_length": getDefault("glyphViewRoundValues"),
}


class RedArrowUI(BaseWindowController):
    def __init__(self):

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
        self.w.showGlyphStatusButton = vanilla.CheckBox(
            (10, y, -10, 25),
            "Show Red Arrows",
            callback=self.checkGlyphStatus,
            sizeStyle="small",
        )
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
        _registerFactory()
        self.addObservers()
        self.drawing = True
        UpdateCurrentGlyphView()

    def hideRedArrows(self):
        self.errors = {}
        self.removeObservers()
        _unregisterFactory()
        self.drawing = False
        UpdateCurrentGlyphView()

    def toggleShowLabels(self, sender):
        if self.show_labels:
            self.show_labels = False
            if not self.track_mouse:
                addObserver(self, "mouseMoved", "mouseMoved")
                self.track_mouse = True
        else:
            self.show_labels = True
            if self.track_mouse:
                removeObserver(self, "mouseMoved")
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

    def addObservers(self):
        addObserver(self, "_drawArrows", "drawInactive")
        addObserver(self, "_drawArrows", "drawBackground")
        addObserver(self, "_drawGlyphCellArrows", "glyphCellDrawBackground")
        # addObserver(self, "_updateOutlineCheck", "currentGlyphChanged")
        # addObserver(self, "_updateOutlineCheck", "draw")
        addObserver(self, "mouseMoved", "mouseMoved")
        self.track_mouse = True

    def removeObservers(self):
        removeObserver(self, "drawBackground")
        removeObserver(self, "drawInactive")
        removeObserver(self, "glyphCellDrawBackground")
        # removeObserver(self, "currentGlyphChanged")
        # removeObserver(self, "draw")
        removeObserver(self, "mouseMoved")
        self.track_mouse = False

    def _fixSelected(self, sender=None):
        if self.fixer is not None:
            self.fixer.fixSelected()

    def _drawArrow(self, position, kind, size, vector=(-1, 1)):
        if vector is None:
            vector = (-1, 1)
        angle = atan2(vector[0], -vector[1])
        size *= 2
        x, y = position
        head_ratio = 0.7
        w = size * 0.5
        tail_width = 0.3

        chin = 0.5 * (w - w * tail_width)  # part under the head

        NSColor.colorWithCalibratedRed_green_blue_alpha_(
            0.9, 0.1, 0.0, 0.85
        ).set()
        t = NSAffineTransform.transform()
        t.translateXBy_yBy_(x, y)
        t.rotateByRadians_(angle)
        myPath = NSBezierPath.alloc().init()

        myPath.moveToPoint_((0, 0))
        myPath.relativeLineToPoint_((-size * head_ratio, w * 0.5))
        myPath.relativeLineToPoint_((0, -chin))
        myPath.relativeLineToPoint_((-size * (1 - head_ratio), 0))
        myPath.relativeLineToPoint_((0, -w * tail_width))
        myPath.relativeLineToPoint_((size * (1 - head_ratio), 0))
        myPath.relativeLineToPoint_((0, -chin))
        myPath.closePath()
        myPath.transformUsingAffineTransform_(t)
        myPath.fill()

        if (
            self.show_labels
            or distance_between_points(self.mouse_position, position) < size
        ):
            self._drawTextLabel(
                transform=t,
                text=kind,
                size=size,
                vector=vector,
            )

    def _drawTextLabel(self, transform, text, size, vector):
        if vector is None:
            vector = (-1, 1)
        angle = atan2(vector[0], -vector[1])
        text_size = 0.5 * size

        # para_style = NSMutableParagraphStyle.alloc().init()
        # para_style.setAlignment_(NSCenterTextAlignment)

        attrs = {
            NSFontAttributeName: NSFont.systemFontOfSize_(text_size),
            NSForegroundColorAttributeName: NSColor.colorWithCalibratedRed_green_blue_alpha_(
                0.4, 0.4, 0.6, 0.7
            ),
            # NSParagraphStyleAttributeName:  para_style,
        }
        myString = NSString.string().stringByAppendingString_(text)
        bbox = myString.sizeWithAttributes_(attrs)
        bw = bbox.width
        bh = bbox.height

        text_pt = NSPoint()
        text_pt.y = 0

        if -0.5 * pi < angle <= 0.5 * pi:
            text_pt.x = -1.3 * size - bw / 2 * cos(angle) - bh / 2 * sin(angle)
        else:
            text_pt.x = -1.3 * size + bw / 2 * cos(angle) + bh / 2 * sin(angle)

        text_pt = transform.transformPoint_(text_pt)

        rr = NSRect(
            origin=(text_pt.x - bw / 2, text_pt.y - bh / 2), size=(bw, bh)
        )

        if DEBUG:
            NSColor.colorWithCalibratedRed_green_blue_alpha_(
                0, 0, 0, 0.15
            ).set()
            myRect = NSBezierPath.bezierPathWithRect_(rr)
            myRect.setLineWidth_(0.05 * size)
            myRect.stroke()

        myString.drawInRect_withAttributes_(rr, attrs)

        # myString.drawAtPoint_withAttributes_(
        #   text_pt,
        #   attrs
        # )

    def _drawArrows(self, notification):
        glyph = notification["glyph"]
        if glyph is None:
            return

        self.errors = glyph.getRepresentation("de.kutilek.RedArrow.report")

        scale = notification["scale"]
        size = 10 * scale
        width = 3 * scale
        errors_by_position = {}
        for e in self.errors:
            if e.position in errors_by_position:
                errors_by_position[e.position].extend([e])
            else:
                errors_by_position[e.position] = [e]
        for pos, errors in errors_by_position.items():
            message = ""
            for e in errors:
                if e.badness is None or not DEBUG:
                    message += "%s, " % (e.kind)
                else:
                    message += "%s (Severity %0.1f), " % (e.kind, e.badness)
            if pos is None:
                pos = (self.current_layer.width + 20, -10)
                self._drawUnspecified(pos, message.strip(", "), size, e.vector)
            else:
                self._drawArrow(pos, message.strip(", "), size, e.vector)
        if options.get("show_bbox"):
            if roboFontVersion >= "2.0b":
                box = glyph.bounds
            else:
                box = glyph.box
            if box is not None:
                save()
                fill(None)
                strokeWidth(0.5 * scale)
                stroke(1, 0, 0, 0.5)
                x, y, w, h = box
                rect(x, y, w - x, h - y)
                restore()

    def _drawUnspecified(self, position, kind, size, vector=(-1, 1)):
        if vector is None:
            vector = (-1, 1)
        angle = atan2(vector[1], vector[0])
        circle_size = size * 1.3
        x, y = position
        NSColor.colorWithCalibratedRed_green_blue_alpha_(
            0.9, 0.1, 0.0, 0.85
        ).set()

        t = NSAffineTransform.transform()
        t.translateXBy_yBy_(x, y)
        t.rotateByRadians_(angle)

        myPath = NSBezierPath.alloc().init()
        myPath.setLineWidth_(0)
        myPath.appendBezierPathWithOvalInRect_(
            NSMakeRect(
                x - 0.5 * circle_size,
                y - 0.5 * circle_size,
                circle_size,
                circle_size,
            )
        )
        myPath.stroke()
        if (
            self.show_labels
            or distance_between_points(self.mouse_position, position) < size
        ):
            self._drawTextLabel(
                transform=t,
                text=kind,
                size=size,
                angle=angle,
            )

    def _drawGlyphCellArrow(self, num_errors):
        x = 3
        y = 3
        width = 2
        size = 7
        save()
        translate(4, 4)

        stroke(0.2)
        strokeWidth(0.5)
        lineJoin("miter")
        fill(0.9, 0.4, 0.3)
        rect(-1, -1, size + 1, size + 1)

        lineCap("butt")  # butt, square, round
        strokeWidth(width)
        stroke(1, 0.9, 0.65)
        line((0, width / 2 - 0.5), (size - width / 2 + 0.5, width / 2 - 0.5))
        line(
            (width / 2 - 0.5, width / 2 - 1.5),
            (width / 2 - 0.5, size - width / 2 + 0.5),
        )
        lineCap("round")
        line((width // 2, width // 2), (size - 1.5, size - 1.5))

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
            _unregisterFactory()
        UpdateCurrentGlyphView()
        super(RedArrowUI, self).windowCloseCallback(sender)


def getGlyphReport(font, glyph, options):
    # start = time()
    options["grid_length"] = getDefault("glyphViewRoundValues")
    myPen = OutlineTestPen(font, options)
    glyph.drawPoints(myPen)
    # stop = time()
    # print("updateOutlineCheck in %0.2f ms." % ((stop-start) * 1000))
    return myPen.errors


def RedArrowReportFactory(glyph):
    glyph = RGlyph(glyph)
    return getGlyphReport(glyph.font, glyph, options)


def RedArrowReportFactoryUFO2(glyph, font):
    return RedArrowReportFactory(glyph)


def _registerFactory():
    # From https://github.com/typesupply/glyph-nanny/blob/master/Glyph%20Nanny.roboFontExt/lib/glyphNanny.py
    # always register if debugging
    # otherwise only register if it isn't registered
    if roboFontVersion >= "2.0b":
        from defcon import registerRepresentationFactory, Glyph

        if DEBUG:
            if "de.kutilek.RedArrow.report" in Glyph.representationFactories:
                for font in AllFonts():
                    for glyph in font:
                        glyph.naked().destroyAllRepresentations()
            registerRepresentationFactory(
                Glyph, "de.kutilek.RedArrow.report", RedArrowReportFactory
            )
        else:
            if (
                "de.kutilek.RedArrow.report"
                not in Glyph.representationFactories
            ):
                registerRepresentationFactory(
                    Glyph, "de.kutilek.RedArrow.report", RedArrowReportFactory
                )
    else:
        from defcon import (
            addRepresentationFactory,
            removeRepresentationFactory,
        )
        from defcon.objects import glyph as _xxxHackGlyph

        if DEBUG:
            if (
                "de.kutilek.RedArrow.report"
                in _xxxHackGlyph._representationFactories
            ):
                for font in AllFonts():
                    for glyph in font:
                        glyph.naked().destroyAllRepresentations()
                removeRepresentationFactory("de.kutilek.RedArrow.report")
            addRepresentationFactory(
                "de.kutilek.RedArrow.report", RedArrowReportFactoryUFO2
            )
        else:
            if (
                "de.kutilek.RedArrow.report"
                not in _xxxHackGlyph._representationFactories
            ):
                addRepresentationFactory(
                    "de.kutilek.RedArrow.report", RedArrowReportFactoryUFO2
                )


def _unregisterFactory():
    if roboFontVersion >= "2.0b":
        from defcon import unregisterRepresentationFactory

        try:
            unregisterRepresentationFactory(
                RedArrowReportFactory, "de.kutilek.RedArrow.report"
            )
        except:
            pass
    else:
        from defcon import removeRepresentationFactory

        try:
            removeRepresentationFactory("de.kutilek.RedArrow.report")
        except:
            pass


if __name__ == "__main__":
    tool_mode = False
    OpenWindow(RedArrowUI)
