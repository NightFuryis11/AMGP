
from matplotlib import pyplot as plt

from ModulesCore import AMGP_UTIL as amgp

def StyleInfo():
    return {
        "name":"classic-1-panel",
        "axes":1,
        "preview":"classic-1-panel.png"
    }

def StyleTemplate():
    FSO = FigStyle()
    return FSO

class FigStyle():
    def __init__(self):
        self.figure = plt.figure(1, figsize = (10, 10))
        self.axis = []
        self.axes = 1
        self.ratio = (None, None)
    
    def Prepare(self, proj : list):
        self.axis.append(plt.subplot(111, projection = proj[0]))
        return self
    
    def Destroy(self):
        plt.close(self.figure)
        