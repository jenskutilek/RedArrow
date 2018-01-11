from __future__ import print_function, division
#import outlineTestPen
#reload(outlineTestPen)
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
    
    "grid_length": getDefault('glyphViewRoundValues'),
}

def run_test(font, glyphnames):
    selection = []
    for n in glyphnames:
        g = font[n]
        otp = OutlineTestPen(CurrentFont(), options)
        g.drawPoints(otp)
        if otp.errors:
            #if len(otp.errors) > 0:
            #    g.mark = (1, 0.65, 0.6, 1)
            selection.append(g.name)
            #for e in otp.errors:
            #    print(e)
    font.selection = selection

font = CurrentFont()
glyphnames = CurrentFont().keys()
run_test(font, glyphnames)
