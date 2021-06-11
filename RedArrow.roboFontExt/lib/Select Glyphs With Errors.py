from __future__ import print_function, division

# import outlineTestPen
# reload(outlineTestPen)
from outlineTestPen import OutlineTestPen
from lib.tools.defaults import getDefault

options = {
    "extremum_calculate_badness": True,
    "fractional_ignore_point_zero": True,
    "extremum_ignore_badness_below": 0,
    "smooth_connection_max_distance": 4,
    "collinear_vectors_max_distance": 2,
    "semi_hv_vectors_min_distance": 30,
    "zero_handles_max_distance": 0,
    "grid_length": getDefault("glyphViewRoundValues"),
}


def run_test(font, glyphnames):
    selection = []
    otp = OutlineTestPen(CurrentFont(), options)
    for n in glyphnames:
        otp.errors = []
        g = font[n]
        g.drawPoints(otp)
        if otp.errors:
            selection.append(g.name)
    font.selection = selection


font = CurrentFont()
glyphnames = CurrentFont().keys()
run_test(font, glyphnames)
