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
import sys

logging.basicConfig(filename='example.log',level=logging.INFO, filemode="w")

if ( len(sys.argv) < 2 ) :
	exit()

tfile = TFile( sys.argv[1] )
# tfile.ReadKeys()

# logging.info( "TFile after reading Keys" )
# logging.info( json.dumps( tfile, indent=4, sort_keys=True ) )
tfile.list_keys()


# logging.info( json.dumps(tfile.fkeys, indent=4) )

if  len(sys.argv) >= 3 :
	print("READING OBJECT", sys.argv[2] )
	obj = tfile.ReadObject( sys.argv[2] )

	print( "hello danny" )
	# print( "%s" % (json.dumps(obj, indent=True)  ))

	# hist = tfile.Get( sys.argv[2] )
	# print "hist ndim =", hist.n_dim





