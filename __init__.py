import os
import json
import pandas as pd
import numpy as np
from random import sample
import time

script_dir = os.path.dirname(__file__)
rel_path = "data/"
path = os.path.join(script_dir, rel_path)

class StopWatch:
    def __init__(self):
        self.start()
    def start(self):
        self._startTime = time.time()
    def getStartTime(self):
        return self._startTime
    def elapsed(self, prec=3):
        prec = 3 if prec is None or not isinstance(prec, (int)) else prec
        diff= time.time() - self._startTime
        return round(diff, prec)

stopwatch = StopWatch()
