from AppKit import (
    NSAffineTransform,
    NSBezierPath,
    NSColor,
    NSFont,
    NSFontAttributeName,
    NSForegroundColorAttributeName,
    NSMakeRect,
    # NSMutableParagraphStyle,
    NSPoint,
    NSRect,
    NSString,
)
from geometry_functions import distance_between_points
from math import atan2, cos, pi, sin
from mojo.drawingTools import (
    save,
    restore,
    fill,
    stroke,
    line,
    strokeWidth,
    rect,
    translate,
    # text,
    # fontSize,
    # font,
    lineJoin,
    lineCap,
)


DEBUG = False


def drawArrow(position, kind, size, vector=(-1, 1), show_labels=False, mouse_position=(0, 0)):
    if vector is None:
        vector = (-1, 1)
    angle = atan2(vector[0], -vector[1])
    size *= 2
    x, y = position
    head_ratio = 0.7
    w = size * 0.5
    tail_width = 0.3

    chin = 0.5 * (w - w * tail_width)  # part under the head

    NSColor.colorWithCalibratedRed_green_blue_alpha_(0.9, 0.1, 0.0, 0.85).set()
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
        show_labels
        or distance_between_points(mouse_position, position) < size
    ):
        drawTextLabel(
            transform=t,
            text=kind,
            size=size,
            vector=vector,
        )


def drawTextLabel(transform, text, size, vector):
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

    rr = NSRect(origin=(text_pt.x - bw / 2, text_pt.y - bh / 2), size=(bw, bh))

    if DEBUG:
        NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 0, 0.15).set()
        myRect = NSBezierPath.bezierPathWithRect_(rr)
        myRect.setLineWidth_(0.05 * size)
        myRect.stroke()

    myString.drawInRect_withAttributes_(rr, attrs)

    # myString.drawAtPoint_withAttributes_(
    #   text_pt,
    #   attrs
    # )


def drawArrows(errors, scale, show_bbox, current_layer):
    size = 10 * scale
    errors_by_position = {}
    for e in errors:
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
            pos = (current_layer.width + 20, -10)
            drawUnspecified(pos, message.strip(", "), size, e.vector)
        else:
            drawArrow(pos, message.strip(", "), size, e.vector)
    if show_bbox:
        box = current_layer.bounds
        if box is not None:
            save()
            fill(None)
            strokeWidth(0.5 * scale)
            stroke(1, 0, 0, 0.5)
            x, y, w, h = box
            rect(x, y, w - x, h - y)
            restore()


def drawUnspecified(position, kind, size, vector=(-1, 1), show_labels=False, mouse_position=(0, 0)):
    if vector is None:
        vector = (-1, 1)
    angle = atan2(vector[1], vector[0])
    circle_size = size * 1.3
    x, y = position
    NSColor.colorWithCalibratedRed_green_blue_alpha_(0.9, 0.1, 0.0, 0.85).set()

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
        show_labels
        or distance_between_points(mouse_position, position) < size
    ):
        drawTextLabel(
            transform=t,
            text=kind,
            size=size,
            angle=angle,
        )


def drawGlyphCellArrow(num_errors):
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


def drawGlyphCellArrows(notification):
    glyph = notification["glyph"]
    if glyph is None:
        return
    num_errors = len(glyph.getRepresentation("de.kutilek.RedArrow.report"))
    if num_errors > 0:
        drawGlyphCellArrow(num_errors)
