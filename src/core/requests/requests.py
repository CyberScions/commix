#!/usr/bin/env python
# encoding: UTF-8

"""
 This file is part of commix (@commixproject) tool.
 Copyright (c) 2015 Anastasios Stasinopoulos (@ancst).
 https://github.com/stasinopoulos/commix

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.
 
 For more see the file 'readme/COPYING' for copying permission.
"""


import time
import urllib2

from src.utils import menu
from src.utils import settings
from src.core.requests import headers

from src.thirdparty.colorama import Fore, Back, Style, init

# -------------------------------------------
# Estimating the response time (in seconds)
# -------------------------------------------
def estimate_response_time(url, delay):

  request = urllib2.Request(url)
  headers.do_check(request)
  start = time.time()
  response = urllib2.urlopen(request)
  response.read(1)
  response.close()
  end = time.time()
  diff = end - start
  if int(diff) < 1:
    url_time_response = int(diff)
  else:
    url_time_response = int(round(diff))
    print Style.BRIGHT + "(!) The estimated response time is " + str(url_time_response) + " second" + "s"[url_time_response == 1:] + "." + Style.RESET_ALL
  delay = int(delay) + int(url_time_response)

  return delay, url_time_response

#eof