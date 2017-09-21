# -*- coding: utf-8 -*-
# @Author: jdb
# @Date:   2017-06-14 17:52:34
# @Last Modified by:   Daniel
# @Last Modified time: 2017-06-16 10:58:20

from box import Box
import struct
import logging
from . import DirectStreamers
from . import CustomStreamers
from . import UnZip

def BIT( n ) :
	return (1 << n)

class ROOT(object):

	logger = logging.getLogger( "ROOT" )

	@staticmethod
	def getChar( arr, curr ) :
		return struct.unpack( 'c', arr[curr:curr+1] )[0]
	
	@staticmethod
	def getCode( arr, curr ) :
		return struct.unpack( 'b', arr[curr:curr+1] )[0]


	@staticmethod
	def AddClassMethods( classname, streamer ) :
		if None == streamer :
			return None
		ROOT.logger.debug( "AddClassMethods : Missing Impl" )
		return streamer

	@staticmethod
	def GetArrayKind( type_name ) :
		ROOT.logger.debug( "GetArrayKind( %s )", type_name )
		# HERE
		if "TString" == type_name or "string" == type_name :
			return 0

		if type_name in ROOT.IO.CustomStreamers and 'TString' == ROOT.IO.CustomStreamers[ type_name ] :
			return 0

		if len(type_name) < 7 or -1 == type_name.find('TArray') :
			return -1

		# key is string type_name
		# value is the enum type id
		array_types = {
			"TArrayI" : ROOT.IO.kInt,
			"TArrayD" : ROOT.IO.kDouble,
			"TArrayF" : ROOT.IO.kFloat,
			"TArrayS" : ROOT.IO.kShort,
			"TArrayC" : ROOT.IO.kChar,
			"TArrayL" : ROOT.IO.kLong,
			"TArrayL64" : ROOT.IO.kLong64,
		}

		if type_name in array_types :
			return array_types[ type_name ]

		return -1

	@staticmethod
	def CreateMemberSimpleStreamer( name, code ) :
		def streamer_func( buf, obj ) :
			obj[name] = buf.ntox( code )
		return streamer_func



	@staticmethod
	def CreateMember (element, file) :
		# create member entry for streamer element, which is used for reading of such data
		ROOT.logger.debug( "CreateMember( element=%s, file=%s )", element, file )

		found = False
		member = { 
			"name": element['fName'], 
			"type": element['fType'], 
			"fArrayLength": element['fArrayLength'], 
			"fArrayDim": element['fArrayDim'],
			"fMaxIndex": element['fMaxIndex'] 
		}

		if "BASE" == element['fTypeName'] :
			if ROOT.IO.GetArrayKind( member['name'] ) > 0 :
				# this is workaround for arrays as base class
				# we create 'fArray' member, which read as any other data member
				member['name'] = 'fArray'
				member['type'] = ROOT.IO.kAny
			else :
				# create streamer for base class
				member['type'] = ROOT.IO.kBase;
				# this.GetStreamer(element.fName);

		t = member['type'] 
		simple = {
			ROOT.IO.kShort: "h",
			ROOT.IO.kInt: "i",
			ROOT.IO.kCounter: "i",
			ROOT.IO.kLong: "u",
			ROOT.IO.kLong64: "u",
			ROOT.IO.kDouble: "d",
			ROOT.IO.kFloat: "f",
			ROOT.IO.kLegacyChar: "B",
			ROOT.IO.kUChar: "B",
			ROOT.IO.kUShort: "H",
			ROOT.IO.kBits: "I",
			ROOT.IO.kUInt: "I",
			ROOT.IO.kULong64: "U",
			ROOT.IO.kULong: "U"
		}

		if t == ROOT.IO.kBase :
			found = True
			member['base'] = element['fBaseVersion'] # indicate base class
			member['basename'] = element['fName']; # keep class name
			def func(buf, obj) :
				buf.ClassStreamer( obj, member['basename'] )
			member['func'] = func


		if member['type'] in simple :
			found = True
			member['func'] = ROOT.CreateMemberSimpleStreamer( member['name'], simple[ member['type'] ] )
			return member

		if t == ROOT.IO.kBool :
			found = True
			def func( buf, obj ) :
				obj[member['name']] = True if buf.ntou1() != 0 else False
			member['func'] = func

		memberL = [
			(ROOT.IO.kBool),
			(ROOT.IO.kInt),
			(ROOT.IO.kCounter),
			(ROOT.IO.kDouble),
			(ROOT.IO.kUChar),
			(ROOT.IO.kShort),
			(ROOT.IO.kUShort),
			(ROOT.IO.kBits),
			(ROOT.IO.kUInt),
			(ROOT.IO.kULong),
			(ROOT.IO.kULong64),
			(ROOT.IO.kLong),
			(ROOT.IO.kLong64),
			(ROOT.IO.kFloat)
		]

		if (t - ROOT.IO.kOffsetL) in memberL :
			found = True
			if element['fArrayDim'] < 2 :
				member['arrlength'] = element['fArrayLength']
				def func( buf, obj ) :
					obj[member['name']] = buf.ReadFastArray( member['arrlength'], member['type'] - ROOT.IO.kOffsetL )
				member[ 'func' ] = func
			else :
				member['arrlength'] = element['fMaxIndex'][ element['fArrayDim'] - 1 ]
				member['minus1'] = True

				def rnda( buf, obj ) :
					def rfa( buf1, handle ) :
						return buf1.ReadFastArray( handle['arrlength'], handle['type'] - ROOT.IO.kOffsetL )

					obj[member['name']] = buf.ReadNdimArray( member, rfa )
				
				member['func'] = rnda


		if t == ROOT.IO.kOffsetL+ROOT.IO.kChar :
			found = True
			if element['fArrayDim'] < 2 :
				member['arrlength'] = element['fArrayLength'];
				def func( buf, obj ) :
					obj[member['name']] = buf.ReadFastString(member['arrlength']);
				member['func'] = func
			else :
				member['minus1'] = True # one dimension is used for char*
				member['arrlength'] = element['fMaxIndex'][ element['fArrayDim']-1 ]
				def rnda( buf, obj ) :
					def rfs( buf1, handle ) :
						return buf1.ReadFastString( handle['arrlength'])

					obj[ member['name'] ] = buf.ReadNdimArray( member, rfs )

		if (t - ROOT.IO.kOffsetP) in memberL :
			found = True
			member['cntname'] = element['fCountName'];
			def func( buf, obj ) :
				v = buf.ntou1()
				if 1 == v :
					obj[ member['name'] ] = buf.ReadFastArray( obj[ member['cntname'] ], member['type'] - ROOT.IO.kOffsetP )
				else :
					obj[ member['name'] ] = []
			member['func'] = func
		
		if t == (ROOT.IO.kOffsetP+ROOT.IO.kChar) :
			found = True
			member['cntname'] = element['fCountName'];
			def func( buf, obj ) :
				v = buf.ntou1()
				if 1 == v :
					obj[member['name']] = buf.ReadFastString(obj[member['cntname']]);
				else :
					obj[member['name']] = None

			member['func'] = func


		if t == ROOT.IO.kDouble32 or t == (ROOT.IO.kOffsetL+ROOT.IO.kDouble32) or t == (ROOT.IO.kOffsetP+ROOT.IO.kDouble32):
			found = True
			member['double32'] = True;

		# SKIP - need to fill in

		if t == ROOT.IO.kAnyP or t == ROOT.IO.kObjectP :
			found = True
			def func( buf, obj ) :
				def roa( buf1, handle ) :
					return buf1.ReadObjectAny()
				obj[  member['name'] ] = buf.ReadNdimArray( member, roa )
			member['func'] = func
			
		if t == ROOT.IO.kAny or t == ROOT.IO.kAnyp or t == ROOT.IO.kObjectp or t == ROOT.IO.kObject:
			found = True
			classname = element[ 'fName' ] if "BASE" == element['fTypeName'] else element['fTypeName']
			if classname[-1] == "*" :
				classname = classname[ 0 : -1 ]

			arr_kind = ROOT.GetArrayKind( classname )

			if arr_kind > 0 :
				member['arrkind'] = arr_kind
				def func( buf, obj ) :
					obj[ member['name']] = buf.ReadFastArray( buf.ntou4(), member['arrkind'] )
				member['func'] = func

			elif arr_kind == 0 :
				def func( buf, obj ) :
					obj[ member['name'] ] = buf.ReadTString()
				member['func'] = func
			else :
				member['classname'] = classname

				if element['fArrayLength'] > 1 :
					def func( buf, obj ) :
						def rcs( buf1, handle ) :
							return buf1.ClassStreamer( {}, handle['classname'] )
						obj[ member['name'] ] = buf.ReadNdimArray( member, rcs )
				else :
					def func( buf, obj ) :
						obj[ member['name'] ] = buf.ClassStreamer( {}, member['classname'] )

		# Skip - need to fill in
		if t == ROOT.IO.kTString:
			found = True
			def func( buf, obj ) :
				member['name'] = buf.ReadTString()
			member['func'] = func

		if not found :
			ROOT.logger.error( "Not FOUND : %d", t )

		return member



	@staticmethod
	def GetTypeId( typename, recurse = True ) :
		# optimize by not doing this inside func
		
		type_ids = {
			"bool": ROOT.io_data['kBool'],
			"Bool_t": ROOT.io_data['kBool'],
			"char": ROOT.io_data['kChar'],
			"signed char": ROOT.io_data['kChar'],
			"Char_t": ROOT.io_data['kChar'],
			"Color_t": ROOT.io_data['kShort'],
			"Style_t": ROOT.io_data['kShort'],
			"Width_t": ROOT.io_data['kShort'],
			"short": ROOT.io_data['kShort'],
			"Short_t": ROOT.io_data['kShort'],
			"int": ROOT.io_data['kInt'],
			"EErrorType": ROOT.io_data['kInt'],
			"Int_t": ROOT.io_data['kInt'],
			"long": ROOT.io_data['kLong'],
			"Long_t": ROOT.io_data['kLong'],
			"float": ROOT.io_data['kFloat'],
			"Float_t": ROOT.io_data['kFloat'],
			"double": ROOT.io_data['kDouble'],
			"Double_t": ROOT.io_data['kDouble'],
			"unsigned char": ROOT.io_data['kUChar'],
			"UChar_t": ROOT.io_data['kUChar'],
			"unsigned short": ROOT.io_data['kUShort'],
			"UShort_t": ROOT.io_data['kUShort'],
			"unsigned": ROOT.io_data['kUInt'],
			"unsigned int": ROOT.io_data['kUInt'],
			"UInt_t": ROOT.io_data['kUInt'],
			"unsigned long": ROOT.io_data['kULong'],
			"ULong_t": ROOT.io_data['kULong'],
			"int64_t": ROOT.io_data['kLong64'],
			"long long": ROOT.io_data['kLong64'],
			"Long64_t": ROOT.io_data['kLong64'],
			"uint64_t": ROOT.io_data['kULong64'],
			"unsigned long long": ROOT.io_data['kULong64'],
			"ULong64_t": ROOT.io_data['kULong64'],
			"Double32_t": ROOT.io_data['kDouble32'],
			"Float16_t": ROOT.io_data['kFloat16'],
			"char*": ROOT.io_data['kCharStar'],
			"const char*": ROOT.io_data['kCharStar'],
			"const Char_t*": ROOT.io_data['kCharStar'],
		}

		if typename in type_ids :
			return type_ids[ typename ]

		if not recurse :
			return -1

		if typename in ROOT.IO.CustomStreamers :
			replace = ROOT.IO.CustomStreamers[ typename ];
			if type( replace ) == str : 
				return ROOT.IO.GetTypeId(replace, true);

		return -1;


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
		"kClassMask": 0x80000000,
		"Mode": "array", # could be string or array, enable usage of ArrayBuffer in http requests
		"NativeArray": True,
		"TypeNames" : ["BASE", "char", "short", "int", "long", "float", "int", "const char*", "double", "Double32_t", "char", "unsigned  char", "unsigned short", "unsigned", "unsigned long", "unsigned", "Long64_t", "ULong64_t", "bool", "Float16_t"],
		"kNotSTL": 0, "kSTLvector": 1, "kSTLlist": 2, "kSTLdeque": 3, "kSTLmap": 4, "kSTLmultimap": 5,
		"kSTLset": 6, "kSTLmultiset": 7, "kSTLbitset": 8, "kSTLforwardlist": 9,
		"kSTLunorderedset" : 10, "kSTLunorderedmultiset" : 11, "kSTLunorderedmap" : 12,
		"kSTLunorderedmultimap" : 13, "kSTLend" : 14,

		# names of STL containers
		"StlNames" : [ "", "vector", "list", "deque", "map", "multimap", "set", "multiset", "bitset"],
		"kStreamedMemberWise": BIT(14),
		"kSplitCollectionOfPointers": 100,
		"DirectStreamers" : {
			"TKey" : DirectStreamers.TKey,
			"TDatime" : DirectStreamers.TDatime,
			"TDirectory" : DirectStreamers.TDirectory
		},

		# map of user-streamer function like func(buf,obj)
		# or alias (classname) which can be used to read that function
		# or list of read functions
		"CustomStreamers": {
			"TList" : CustomStreamers.TList,
			"TObject" : CustomStreamers.TObject,
			"TNamed" : [ 
				{ "basename" : "TObject", "base": 1, "func" : CustomStreamers.TNamed_TObject }, 
				{ "name" : "fName", "func" : CustomStreamers.TNamed_fName },
				{ "name" : "fTitle", "func" : CustomStreamers.TNamed_fTitle },
			],
			"TStreamerInfo" : CustomStreamers.TStreamerInfo,
			"TObjArray" : CustomStreamers.TObjArray,
			"TStreamerBase" : CustomStreamers.TStreamerBase,
			"TStreamerString" : CustomStreamers.TStreamerString,
			"TStreamerObjectPointer" : CustomStreamers.TStreamerString,
			"TStreamerElement" : CustomStreamers.TStreamerElement,
			"TStreamerObject" : CustomStreamers.TStreamerObject,
			"TStreamerBasicType" : CustomStreamers.TStreamerObject,
			"TStreamerObjectAny" : CustomStreamers.TStreamerObject,
			"TStreamerString" : CustomStreamers.TStreamerObject,
			"TStreamerObjectPointer" : CustomStreamers.TStreamerObject,
			"TStreamerBasicPointer" : CustomStreamers.TStreamerBasicPointer,
			"TStreamerLoop" : CustomStreamers.TStreamerBasicPointer,



		},

		"kIsReferenced": BIT(4),
		"kHasUUID": BIT(5),

		"GetArrayKind" : GetArrayKind.__func__,
		"GetTypeId" : GetTypeId.__func__,
		"CreateMember" : CreateMember.__func__,
	}
	IO = Box( io_data )


