"""


Author: Matthew Cotton
"""

class NewsWindow(object):
    
    def __init__(self, limit=30):
        self.news = [''] * limit
        self.limit = limit

    def add(self, string):
        self.news.append(string)
        diff = len(self.news) - self.limit
        if diff > 0:
            for i in range(diff):
                self.news.pop(0)

    def latest(self, n):
        return reversed(self.news[:-n-1:-1]) # yep, this is it.


NEWS = NewsWindow()
