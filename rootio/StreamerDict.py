import rootio.CustomStreamers as CustomStreamers
import rootio.DirectStreamers as DirectStreamers
from box import Box
# Does Not work!!!

StreamerDict = {
    "CustomStreamers" : {
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
        "TStreamerSTL" : CustomStreamers.TStreamerSTL,
        "TObjString" : [
            { "basename" : "TObject", "base" : 1, "func" : CustomStreamers.TObjString_TObject },
            { "name" : "fString", "func" : CustomStreamers.TObjString_fString }
        ]
    },
    "DirectStreamers" : {
        "TKey" : DirectStreamers.TKey,
        "TDatime" : DirectStreamers.TDatime,
        "TDirectory" : DirectStreamers.TDirectory
    },

}

Streamers = Box( StreamerDict )