from __future__ import print_function, division

# import outlineTestPen
# reload(outlineTestPen)
from outlineTestPen import OutlineTestPen

from vanilla import EditText, FloatingWindow, PopUpButton, TextBox
import random


class RedArrowErrorFilter:
    def __init__(self):
        self.errorList = [
            "Extremum",
            "Mixed cubic and quadratic segments",
            "Fractional Coordinates",
            "Fractional transformation",
            "Incorrect smooth connection",
            "Empty segment",
            "Vector on closepath",
            "Collinear vectors",
            "Semi-horizontal vector",
            "Semi-vertical vector",
            "Zero handle",
        ]
        self.errorList.insert(0, "select Red Arrow Error")
        self.heightOfTool = 360
        self.widthOfTool = 200
        self.w = FloatingWindow(
            (self.widthOfTool, self.heightOfTool), "Red Arrow Error Filter"
        )  ### FloatingWindow
        # self.w.text = TextBox((10, 5, -10, 16), "...", sizeStyle='regular')
        self.w.select_test = PopUpButton(
            (10, 10, -10, 16),
            self.errorList,
            sizeStyle="regular",
            callback=self.select_test,
        )
        self.w.extremumToleranceText = TextBox(
            (10, 35, -25, 18), "Extremum Tolerance", sizeStyle="small"
        )
        self.w.extremumToleranceInput = EditText(
            (160, 35, -10, 18), "2", sizeStyle="small"
        )

        self.w.smooth_connection_max_distance_Text = TextBox(
            (10, 57, -25, 18), "Smooth Connect max_dist", sizeStyle="small"
        )
        self.w.smooth_connection_max_distance_Input = EditText(
            (160, 55, -10, 18), "4", sizeStyle="small"
        )

        self.w.collinear_vectors_max_distance_Text = TextBox(
            (10, 77, -25, 18), "Collinear Vectors max_dist", sizeStyle="small"
        )
        self.w.collinear_vectors_max_distance_Input = EditText(
            (160, 75, -10, 18), "2", sizeStyle="small"
        )

        self.w.report = EditText(
            (10, 100, -10, -10), "...", sizeStyle="regular"
        )
        self.w.report.enable(False)

        self.count = []
        self.report = []
        self.w.open()

    def select_test(self, sender):

        # options
        try:
            extremumTolerance = int(self.w.extremumToleranceInput.get())
        except ValueError:
            self.w.extremumToleranceInput.set(2)
            extremumTolerance = 2
        try:
            smooth_connection_max_distance_Input = int(
                self.w.smooth_connection_max_distance_Input.get()
            )
        except ValueError:
            self.w.smooth_connection_max_distance_Input.set(4)
            smooth_connection_max_distance_Input = 4
        try:
            collinear_vectors_max_distance_Input = int(
                self.w.collinear_vectors_max_distance_Input.get()
            )
        except ValueError:
            self.w.collinear_vectors_max_distance_Input.set(2)
            collinear_vectors_max_distance_Input = 2

        options = {
            "extremum_calculate_badness": True,
            "extremum_ignore_badness_below": extremumTolerance,
            "smooth_connection_max_distance": smooth_connection_max_distance_Input,
            "fractional_ignore_point_zero": True,
            "collinear_vectors_max_distance": collinear_vectors_max_distance_Input,
        }

        # a random number to change the mark color
        # randomNumber = random.random()
        # check if a font is open or not
        if CurrentFont():
            font = CurrentFont()
            glyphnames = CurrentFont().keys()
        else:
            self.w.report.set("Open a Font")
            return
        # start the outline test
        selection = []
        otp = OutlineTestPen(CurrentFont(), options)
        for n in glyphnames:
            otp.errors = []
            g = font[n]
            g.drawPoints(otp)
            if otp.errors:
                for e in otp.errors:
                    # convert error object to string
                    errorString = str(e).split(" ")[0]
                    # if the first part of error string = the first part of selection from PopUp
                    if (
                        errorString
                        == str(sender.getItems()[sender.get()]).split(" ")[0]
                    ):
                        # g.mark = (1, randomNumber, 0.6, 1)
                        selection.append(g.name)
                        # print(e)
        font.selection = selection
        # output of glyphs with errors in UI
        result = dict((x, selection.count(x)) for x in set(selection))
        formattedResult = "  ".join(
            "%s=%r" % (key, val) for (key, val) in sorted(result.items())
        )
        self.w.report.set(formattedResult)


RedArrowErrorFilter()
