s = 1.5
c = 16
newPage(c, c)
strokeWidth(s)
stroke(0)
fill(None)
oval(s, s * 2 / 3.0, width() - 2 * s, height() - 2 * s)
saveImage("RedArrowFixer.pdf")
