from Tkinter import *
import Image, ImageDraw

width = 400
height = 300
center = height//2
white = (255, 255, 255)
green = (0,128,0)

root = Tk()

# Tkinter create a canvas to draw on
cv = Canvas(root, width=width, height=height, bg='white')
cv.pack()

# PIL create an empty image and draw object to draw on
# memory only, not visible
image1 = Image.new("RGB", (width, height), white)
draw = ImageDraw.Draw(image1)

# do the Tkinter canvas drawings (visible)
cv.create_line([0, center, width, center], fill='green')

# do the PIL image/draw (in memory) drawings
draw.line([0, center, width, center], green)

# PIL image can be saved as .png .jpg .gif or .bmp file (among others)
filename = "my_drawing.png"
image1.save(filename)

root.mainloop()
