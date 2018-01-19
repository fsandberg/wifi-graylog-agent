import time
import numpy as np
from plotly.offline import plot
from plotly.graph_objs import *


class graphdata(object):

    def draw_graph(self, yvalue):

        plot([Box(y=yvalue, showlegend=False) for i in range(45)], show_link=False)

        return

