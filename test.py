# -*- coding: utf-8 -*-
# @Author: jdb
# @Date:   2017-06-14 17:36:12
# @Last Modified by:   Daniel
# @Last Modified time: 2017-06-16 09:27:12


import rootio.TBuffer as TBuffer
from rootio.TFile import  TFile
import json
import logging

logging.basicConfig(filename='example.log',level=logging.DEBUG, filemode="w")

tfile = TFile( "mtd_gpid_8.root" )
tfile.ReadKeys()

obj = tfile.ReadObject( "dy3" )




