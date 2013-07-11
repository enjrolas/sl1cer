import svgwrite

dwg = svgwrite.Drawing('test.svg', profile='full')
horizontal_gradient = dwg.linearGradient((0, 0), (10, 100))
dwg.defs.add(horizontal_gradient)
#horizontal_gradient.add_stop_color(0, svgwrite.rgb(0,255,0, '%'))
#horizontal_gradient.add_stop_color(1, svgwrite.rgb(0,0,255, '%'))

horizontal_gradient.add_stop_color(0, 'red')
horizontal_gradient.add_stop_color(1, 'green')
dwg.add(dwg.line((0, 0), (10, 100), stroke=horizontal_gradient.get_paint_server()))
dwg.save()
