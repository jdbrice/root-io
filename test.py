# -*- coding: utf-8 -*-
# @Author: jdb
# @Date:   2017-06-14 17:36:12
# @Last Modified by:   jdb
# @Last Modified time: 2017-06-14 19:05:14


import rootio.TBuffer as TBuffer

buf = TBuffer.TBuffer( bytearray([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]), 0, 0, 0 )

print(buf.ntou4())
