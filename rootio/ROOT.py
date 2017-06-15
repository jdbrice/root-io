# -*- coding: utf-8 -*-
# @Author: jdb
# @Date:   2017-06-14 17:52:34
# @Last Modified by:   jdb
# @Last Modified time: 2017-06-14 18:01:10

from box import Box

class ROOT(object):


	io_data = {
	"kBase": 0, "kOffsetL": 20, "kOffsetP": 40,
	"kChar":   1, "kShort":   2, "kInt":   3, "kLong":   4, "kFloat": 5, "kCounter": 6, "kCharStar": 7, "kDouble": 8, "kDouble32": 9, "kLegacyChar ": 10,
	"kUChar": 11, "kUShort": 12, "kUInt": 13, "kULong": 14, "kBits": 15, "kLong64": 16, "kULong64": 17, "kBool": 18,  "kFloat16": 19,
	"kObject": 61, "kAny": 62, "kObjectp": 63, "kObjectP": 64, "kTString": 65,
	"kTObject": 66, "kTNamed": 67, "kAnyp": 68, "kAnyP": 69, "kAnyPnoVT": 70, "kSTLp": 71,
	"kSkip": 100, "kSkipL": 120, "kSkipP": 140, "kConv": 200, "kConvL": 220, "kConvP": 240,
	"kSTL": 300, "kSTLstring": 365, "kStreamer": 500, "kStreamLoop": 501,
	"kMapOffset": 2,
	"kByteCountMask": 0x40000000,
	"kNewClassTag": 0xFFFFFFFF,
	"kClassMask": 0x80000000
	}
	IO = Box( io_data )
