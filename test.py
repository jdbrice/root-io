# -*- coding: utf-8 -*-
# @Author: jdb
# @Date:   2017-06-14 17:36:12
# @Last Modified by:   Daniel
# @Last Modified time: 2017-09-21 11:11:23


import rootio.TBuffer as TBuffer
from rootio.TFile import  TFile
import json
import rootio.make_json_serializable
import logging

logging.basicConfig(filename='example.log',level=logging.INFO, filemode="w")

tfile = TFile( "mtd_gpid_8.root" )
tfile.ReadKeys()

logging.info( "TFile after reading Keys" )
logging.info( json.dumps( tfile, indent=4, sort_keys=True ) )
# logging.info( json.dumps(tfile.fkeys, indent=4) )

# obj = tfile.ReadObject( "mtd_8_DeltaY_vs_BL" )

# logging.debug( "obj = %s", obj )





