from pychart import *
import sys
import time
theme.get_options()
theme.use_color = 1

if theme.use_color:
    colors = [ fill_style.red, fill_style.blue, fill_style.brown, fill_style.darkseagreen, fill_style.white, fill_style.brown ]
else:
    colors = [ fill_style.gray90, fill_style.gray30, fill_style.black, fill_style.white, fill_style.gray10, fill_style.gray50 ]


def format_date1(ordinal):
    return "/a60{}" + ordinal

def ussdefect1(fn1):
    #fn1 = "ussdefect1.csv"
    format1 = "%s,%d,%d"
    data = chart_data.read_csv(fn1,format1)
    
    # The attribute y_coord=... tells that the Y axis values
    # should be taken from samples.
    # In this example, Y values will be [40,50,60,70,80].
    ar = area.T(x_coord = category_coord.T(data, 0),
                x_grid_style=line_style.gray50_dash1,
                x_grid_interval=10, 
                y_range = (0,30),
                x_axis=axis.X(label="month",format=format_date1),
                y_axis=axis.Y(label="defect"),
                bg_style = fill_style.white,
                border_line_style = line_style.default,
                size=(300,200),
                legend = legend.T(loc=(200,160)))
    
    # Below call sets the default attributes for all bar plots.
    chart_object.set_defaults(bar_plot.T, direction="vertical", data=data)
    
    # Attribute cluster=(0,3) tells that you are going to draw three bar
    # plots side by side.  The plot labeled "foo" will the leftmost (i.e.,
    # 0th out of 3).  Attribute hcol tells the column from which to
    # retrive sample values from.  It defaults to one.
    ar.add_plot(bar_plot.T(label="open", hcol=1, cluster=(0,2),fill_style=colors[0]))
    ar.add_plot(bar_plot.T(label="close", hcol=2, cluster=(1,2),fill_style=colors[1]))
    
    ar.draw()

    can = canvas.default_canvas()
    can.show(200, -55, "/10/C" + font.quotemeta(  time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()) ))
    #tb = text_box.T(loc=(100,100), text="Without frame")
    #tb.draw()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "usspic1 sys.argv!=3"
        exit(1)
    func1 = globals()[sys.argv[1]]
    func1(sys.argv[2])
    #defect_pic1("ussdefect1.csv","%s,%d,%d")
