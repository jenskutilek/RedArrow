import outlineTestPen
reload(outlineTestPen)
from outlineTestPen import OutlineTestPen

options = {
    "extremum_calculate_badness": True,
    "extremum_ignore_badness_below": 2,
    "smooth_connection_max_distance": 4,
    "fractional_ignore_point_zero": True,
    "collinear_vectors_max_distance": 2,
}

def run_test(font, glyphnames):
    for n in glyphnames:
        g = font[n]
        otp = OutlineTestPen(CurrentFont(), options)
        g.draw(otp)
        if otp.errors:
            if len(otp.errors) > 0:
                g.mark = (1, 0.65, 0.6, 1)
            #for e in otp.errors:
            #    print e

font = CurrentFont()
glyphnames = CurrentFont().keys()
run_test(font, glyphnames)
