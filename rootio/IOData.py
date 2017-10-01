from box import Box

def BIT( n ) :
    return (1 << n)

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
		"kIsReferenced": BIT(4),
		"kHasUUID": BIT(5),

		# "GetArrayKind" : GetArrayKind.__func__,
		# "GetTypeId" : GetTypeId.__func__,
		# "CreateMember" : CreateMember.__func__,
	}

IOData = Box( io_data )