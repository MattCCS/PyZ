
from pyz import colors


class StatsWindow(object):

    def __init__(self, layer):
        self._layer = layer
        self._gameticks = 0

    def render(self):
        self._layer.reset()
        self._layer.setrange(0, 1, "gameticks: {}".format(self._gameticks), colors.get("white"))

    def inc(self):
        self._gameticks += 1
