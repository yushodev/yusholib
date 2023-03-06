from typing import Literal
from pystyle import Colors
import time

class Logger:
  
  w = Colors.white
  r = Colors.red
  y = Colors.yellow
  c = Colors.cyan
  g = Colors.green
  re = Colors.reset
  gr = Colors.gray
  
  separator = f'{re}{w}:: '
  
  err_prefix = f'{re}{r}ERROR   {separator}'
  wrn_prefix = f'{re}{y}WARN    {separator}'
  suc_prefix = f'{re}{g}SUCCESS {separator}'
  inf_prefix = f'{re}{c}INFO    {separator}'
  dbg_prefix = f'{re}{w}DEBUG   {separator}'
  
  def __init__(self, level: Literal['error', 'warn', 'info', 'debug'], /, hide_time:bool=False, timestamp_format:str="%m/%d/%YT%H:%M:%S"):
    if level == 'error':
        self.level = 0
    elif level == 'warn':
        self.level = 1
    elif level == 'success' or level =='info':
        self.level = 2
    elif level == 'debug':
        self.level = 3

    self.hide_time = hide_time
    self.timestamp_format = timestamp_format

  def __time(self):
    _date = time.strftime(self.timestamp_format, time.localtime()) 

    if self.hide_time:
      return ""
    else:
      return f"{self.gr}[{_date}] "

  def error(self, message):
    if 0 <= self.level:
      print(f'{self.__time()}{self.err_prefix}{message}{self.re}')

  def warn(self, message):
    if 1 <= self.level:
      print(f'{self.__time()}{self.wrn_prefix}{message}{self.re}')

  def success(self, message):
    if 2 <= self.level:
      print(f'{self.__time()}{self.suc_prefix}{message}{self.re}')
    
  def info(self, message):
    if 2 <= self.level:
      print(f'{self.__time()}{self.inf_prefix}{message}{self.re}')

  def debug(self, message):
    if 3 <= self.level:
      print(f'{self.__time()}{self.dbg_prefix}{message}{self.re}')