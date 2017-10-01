# -*- coding: utf-8 -*-
# @Author: jdb
# @Date:   2017-06-14 17:52:34
# @Last Modified by:   Daniel
# @Last Modified time: 2017-09-21 09:23:26



import logging
from . import UnZip
import json
from rootio.StreamerDict import Streamers
from rootio.IOData import IOData

def BIT( n ) :
	return (1 << n)

class ROOT(object):

	logger = logging.getLogger( "ROOT" )

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

		if type_name in Streamers.CustomStreamers and 'TString' == Streamers.CustomStreamers[ type_name ] :
			return 0

		if len(type_name) < 7 or -1 == type_name.find('TArray') :
			return -1

		# key is string type_name
		# value is the enum type id
		array_types = {
			"TArrayI" : IOData.kInt,
			"TArrayD" : IOData.kDouble,
			"TArrayF" : IOData.kFloat,
			"TArrayS" : IOData.kShort,
			"TArrayC" : IOData.kChar,
			"TArrayL" : IOData.kLong,
			"TArrayL64" : IOData.kLong64,
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
			if ROOT.GetArrayKind( member['name'] ) > 0 :
				# this is workaround for arrays as base class
				# we create 'fArray' member, which read as any other data member
				member['name'] = 'fArray'
				member['type'] = IOData.kAny
			else :
				# create streamer for base class
				member['type'] = IOData.kBase;
				# this.GetStreamer(element.fName);

		t = member['type'] 
		simple = {
			IOData.kShort: "h",
			IOData.kInt: "i",
			IOData.kCounter: "i",
			IOData.kLong: "u",
			IOData.kLong64: "u",
			IOData.kDouble: "d",
			IOData.kFloat: "f",
			IOData.kLegacyChar: "B",
			IOData.kUChar: "B",
			IOData.kUShort: "H",
			IOData.kBits: "I",
			IOData.kUInt: "I",
			IOData.kULong64: "U",
			IOData.kULong: "U"
		}

		if t == IOData.kBase :
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

		if t == IOData.kBool :
			found = True
			def func( buf, obj ) :
				obj[member['name']] = True if buf.ntou1() != 0 else False
			member['func'] = func

		memberL = [
			(IOData.kBool),
			(IOData.kInt),
			(IOData.kCounter),
			(IOData.kDouble),
			(IOData.kUChar),
			(IOData.kShort),
			(IOData.kUShort),
			(IOData.kBits),
			(IOData.kUInt),
			(IOData.kULong),
			(IOData.kULong64),
			(IOData.kLong),
			(IOData.kLong64),
			(IOData.kFloat)
		]

		if (t - IOData.kOffsetL) in memberL :
			found = True
			if element['fArrayDim'] < 2 :
				member['arrlength'] = element['fArrayLength']
				def func( buf, obj ) :
					ROOT.getLogger("memberL").info( "member %s", member )
					obj[member['name']] = buf.ReadFastArray( member['arrlength'], member['type'] - IOData.kOffsetL )
				member[ 'func' ] = func
			else :
				member['arrlength'] = element['fMaxIndex'][ element['fArrayDim'] - 1 ]
				member['minus1'] = True

				def rnda( buf, obj ) :
					def rfa( buf1, handle ) :
						ROOT.getLogger("memberL").info( "member %s", member )
						return buf1.ReadFastArray( handle['arrlength'], handle['type'] - IOData.kOffsetL )

					obj[member['name']] = buf.ReadNdimArray( member, rfa )
				
				member['func'] = rnda


		if t == IOData.kOffsetL+IOData.kChar :
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

		if (t - IOData.kOffsetP) in memberL :
			found = True
			member['cntname'] = element['fCountName'];
			def func( buf, obj ) :
				v = buf.ntou1()
				if 1 == v :
					# ROOT.getLogger("memberL").info( "obj \n%s, member \n%s ", json.dumps( {k:v for k, v in obj.iteritems() if k is not "func"} , indent=4), json.dumps({k:v for k, v in member.iteritems() if k is not "func"}, indent=4) )
					obj[ member['name'] ] = buf.ReadFastArray( obj[ member['cntname'] ], member['type'] - IOData.kOffsetP )
				else :
					obj[ member['name'] ] = []
			member['func'] = func
		
		if t == (IOData.kOffsetP+IOData.kChar) :
			found = True
			member['cntname'] = element['fCountName'];
			def func( buf, obj ) :
				v = buf.ntou1()
				if 1 == v :
					obj[member['name']] = buf.ReadFastString(obj[member['cntname']]);
				else :
					obj[member['name']] = None

			member['func'] = func


		if t == IOData.kDouble32 or t == (IOData.kOffsetL+IOData.kDouble32) or t == (IOData.kOffsetP+IOData.kDouble32):
			found = True
			member['double32'] = True;

		# SKIP - need to fill in

		if t == IOData.kAnyP or t == IOData.kObjectP :
			found = True
			def func( buf, obj ) :
				def roa( buf1, handle ) :
					return buf1.ReadObjectAny()
				obj[  member['name'] ] = buf.ReadNdimArray( member, roa )
			member['func'] = func
			
		if t == IOData.kAny or t == IOData.kAnyp or t == IOData.kObjectp or t == IOData.kObject:
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
					member['func'] = func
				else :
					def func( buf, obj ) :
						obj[ member['name'] ] = buf.ClassStreamer( {}, member['classname'] )
					member['func'] = func

		# Skip - need to fill in
		if t == IOData.kTString:
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
			"bool": IOData['kBool'],
			"Bool_t": IOData['kBool'],
			"char": IOData['kChar'],
			"signed char": IOData['kChar'],
			"Char_t": IOData['kChar'],
			"Color_t": IOData['kShort'],
			"Style_t": IOData['kShort'],
			"Width_t": IOData['kShort'],
			"short": IOData['kShort'],
			"Short_t": IOData['kShort'],
			"int": IOData['kInt'],
			"EErrorType": IOData['kInt'],
			"Int_t": IOData['kInt'],
			"long": IOData['kLong'],
			"Long_t": IOData['kLong'],
			"float": IOData['kFloat'],
			"Float_t": IOData['kFloat'],
			"double": IOData['kDouble'],
			"Double_t": IOData['kDouble'],
			"unsigned char": IOData['kUChar'],
			"UChar_t": IOData['kUChar'],
			"unsigned short": IOData['kUShort'],
			"UShort_t": IOData['kUShort'],
			"unsigned": IOData['kUInt'],
			"unsigned int": IOData['kUInt'],
			"UInt_t": IOData['kUInt'],
			"unsigned long": IOData['kULong'],
			"ULong_t": IOData['kULong'],
			"int64_t": IOData['kLong64'],
			"long long": IOData['kLong64'],
			"Long64_t": IOData['kLong64'],
			"uint64_t": IOData['kULong64'],
			"unsigned long long": IOData['kULong64'],
			"ULong64_t": IOData['kULong64'],
			"Double32_t": IOData['kDouble32'],
			"Float16_t": IOData['kFloat16'],
			"char*": IOData['kCharStar'],
			"const char*": IOData['kCharStar'],
			"const Char_t*": IOData['kCharStar'],
		}

		if typename in type_ids :
			return type_ids[ typename ]

		if not recurse :
			return -1

		if typename in Streamers.CustomStreamers :
			replace = Streamers.CustomStreamers[ typename ];
			if type( replace ) == str : 
				return ROOT.GetTypeId(replace, true);

		return -1;

	

