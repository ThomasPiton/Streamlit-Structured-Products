from abc import ABC, abstractmethod
from datetime import date, datetime
import pandas as pd
from dateutil.relativedelta import relativedelta

class DisplayBase(ABC):
    
    def __init__(self):
        pass

    @abstractmethod  
    def render(self):
        pass