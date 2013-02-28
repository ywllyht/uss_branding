from pychart import *
import sys
import time
theme.get_options()
theme.use_color = 1

if theme.use_color:
    colors = [ fill_style.red, fill_style.blue, fill_style.green, fill_style.darkseagreen, fill_style.white, fill_style.goldenrod  ]
    line_colors = [line_style.red, line_style.blue, line_style.green, line_style.darkseagreen, line_style.darkkhaki_dash2, line_style.darkblue_dash1]
else:
    colors = [ fill_style.gray90, fill_style.gray30, fill_style.black, fill_style.white, fill_style.gray10, fill_style.gray50 ]
    line_colors = [line_style.gray90, line_style.gray30, line_style.black_dash1, line_style.gray60_dash3, line_style.gray10, line_style.gray50_dash2]


def format_date1(ordinal):
    return "/08/a60{}" + ordinal

def ussdefect1(fn1):
    #fn1 = "ussdefect1.csv"
    format1 = "%s,%d,%d"
    data = chart_data.read_csv(fn1,format1)
    
    # The attribute y_coord=... tells that the Y axis values
    # should be taken from samples.
    # In this example, Y values will be [40,50,60,70,80].
    xaxis = axis.X(label="month",format=format_date1)
    yaxis = axis.Y(label="defect")
    ar = area.T(x_coord = category_coord.T(data, 0),
                x_grid_style=line_style.gray50_dash1,
                x_grid_interval=10, 
                y_range = (0,30),
                x_axis=xaxis,
                y_axis=yaxis,
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


def ussdefect2(fn1):
    #fn1 = "ussdefect2.csv"
    format1 = "%s,%d,%d"
    data = chart_data.read_csv(fn1,format1)
    
    # The attribute y_coord=... tells that the Y axis values
    # should be taken from samples.
    # In this example, Y values will be [40,50,60,70,80].
    xaxis = axis.X(label="month",format=format_date1)
    yaxis = axis.Y(label="defect")
    ar = area.T(x_coord = category_coord.T(data, 0),
                x_grid_style=line_style.gray50_dash1,
                x_grid_interval=10, 
                y_range = (0,100),
                x_axis=xaxis,
                y_axis=yaxis,
                bg_style = fill_style.white,
                border_line_style = line_style.default,
                size=(300,200),
                legend = legend.T( loc=(100,100) ))
    
    # Below call sets the default attributes for all bar plots.
    chart_object.set_defaults(bar_plot.T, direction="vertical", data=data)
    
    # Attribute cluster=(0,3) tells that you are going to draw three bar
    # plots side by side.  The plot labeled "foo" will the leftmost (i.e.,
    # 0th out of 3).  Attribute hcol tells the column from which to
    # retrive sample values from.  It defaults to one.
    plot = line_plot.T(label="open", data=data, ycol=1, line_style=line_colors[0])#, data_label_format="/8{}%d") #, tick_mark=tick_mark.star)
    plot2 = line_plot.T(label="close", data=data, ycol=2, line_style=line_colors[1])#, data_label_format="/8{}%d")#, tick_mark=tick_mark.square)

    ar.add_plot(plot, plot2)    
    ar.draw()

    open_last = data[-1][1]
    close_last = data[-1][2]
    number_msg = "Current: open %d, close %d" % (open_last, close_last)

    can = canvas.default_canvas()
    can.show(10,150,"/10{}" + font.quotemeta( number_msg ) )
    can.show(200, -55, "/10/C" + font.quotemeta(  time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()) ))
    #tb = text_box.T(loc=(100,100), text="Without frame")
    #tb.draw()


def ussdefect3(fn1):
    #fn1 = "ussdefect3.csv"
    format1 = "%s,%d"
    data = chart_data.read_csv(fn1,format1)
    #print data
    
    # The attribute y_coord=... tells that the Y axis values
    # should be taken from samples.
    # In this example, Y values will be [40,50,60,70,80].

    ar = area.T(size=(150,150), legend=legend.T(),
            x_grid_style = None, y_grid_style = None)

    plot = pie_plot.T(data=data, 
                    arc_offsets=[ 10 for x in range(len(data))],
                    shadow = (2, -2, fill_style.gray50),
                    label_offset = 25,
                    arrow_style = arrow.a3)
    ar.add_plot(plot)
    ar.draw()

    can = canvas.default_canvas()
    can.show(100, -15, "/10/C" + font.quotemeta(  time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()) ))
    #tb = text_box.T(loc=(100,100), text="Without frame")
    #tb.draw()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "ussdefectpic1 sys.argv!=3"
        exit(1)
    func1 = globals()[sys.argv[1]]
    func1(sys.argv[2])
    #defect_pic1("ussdefect1.csv","%s,%d,%d")
