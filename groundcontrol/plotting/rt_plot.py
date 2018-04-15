from groundcontrol.utils import CircBuffer
from pylab import *
import tkinter as tk
from _tkinter import TclError
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
import time
from groundcontrol.menu import AxisMenu

class RtPlot(tk.Frame, threading.Thread):
    REFRESH_PERIOD = 0.01 # [s]

    def __init__(self, parent, data_buffer_dict, x_buffer, lock):
        tk.Frame.__init__(self, parent)
        threading.Thread.__init__(self)

        self.x_buffer = x_buffer
        self.lock = lock

        self.axis_menu_frame = tk.Frame(self)

        self.subplots_dict = {}
        self.fig, self.axes = subplots(len(data_buffer_dict),1, sharex=True)
        tk.Label(self.axis_menu_frame).pack(fill=tk.BOTH, expand=True)
        for i,var in enumerate(sorted(data_buffer_dict)):
            sp = {}
            sp['axis'] = self.axes[i]
            sp['buffer'] = data_buffer_dict[var]
            sp['axis_menu'] = AxisMenu(self.axis_menu_frame, var)
            sp['axis_menu'].pack()#fill=tk.Y, expand=True)
            tk.Label(self.axis_menu_frame).pack(fill=tk.BOTH, expand=True)    
            self.subplots_dict[var] = sp
        self.axis_menu_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.fig.tight_layout()

        # self.draw_fig()

        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def run(self):
        self.running = True
        while self.running:
            try:
                self.update()
            except TclError:
               break

    def update(self):
        self.draw_fig()
        self.canvas.draw()
        time.sleep(self.REFRESH_PERIOD)

    def draw_fig(self):
        for sp in self.subplots_dict.values():
            axis = sp['axis']
            axis.clear()
            if self.lock:
                self.lock.acquire()
            axis.plot(self.x_buffer.head_view(500),sp['buffer'].head_view(500))
            if self.lock:
                self.lock.release()
            axis.set_ylim(sp['axis_menu'].get_limits())