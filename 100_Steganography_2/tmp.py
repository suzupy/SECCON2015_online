import sys
import struct
import binascii

class PNG:

    def __init__(self, binary):
        self.binary = binary

    def is_PNG(self):
        return struct.unpack_from(">Q", self.binary, 0)[0] == 9894494448401390090

    def chunk(self, offset):
        chunk = struct.unpack_from(">I4s", self.binary, offset)
        chunk += struct.unpack_from(">I", self.binary, offset + chunk[0] + 8)
        return chunk

    def chunk_data(self, chunk, offset):
        if chunk[1] == b'IHDR':
            return self.IHDR(chunk, offset)
        elif chunk[1] == b'sRGB':
            return self.sRGB(chunk, offset)
        elif chunk[1] == b'gAMA':
            return self.gAMA(chunk, offset)
        elif chunk[1] == b'pHYs':
            return self.pHYs(chunk, offset)
        elif chunk[1] == b'tEXt':
            return self.tEXt(chunk, offset)
        elif chunk[1] == b'tIME':
            return self.tIME(chunk, offset)
        elif chunk[1] == b'IDAT':
            return self.IDAT(chunk, offset)
        elif chunk[1] == b'IEND':
            return self.IEND(chunk, offset)
        else:
            return False

    def CRC32(self, chunk, offset):
        crc_data = chunk[1]
        crc_data += struct.unpack_from(">%ds" % chunk[0], self.binary, offset + 8)[0]
        return binascii.crc32(crc_data)

    def IHDR(self, chunk, offset):
        labels = ('width', 'height', 'bit depth', 'colour type', 'compression method', 'filter method', 'interlace method')
        values = struct.unpack_from(">2I5B", self.binary, offset + 8)
        return dict(zip(labels, values))

    def sRGB(self, chunk, offset):
        labels = ('rendering intent',)
        values = struct.unpack_from(">B", self.binary, offset + 8)
        return dict(zip(labels, values))

    def gAMA(self, chunk, offset):
        labels = ('image gamma',)
        values = struct.unpack_from(">I", self.binary, offset + 8)
        return dict(zip(labels, values))

    def pHYs(self, chunk, offset):
        labels = ('pixels per unit, X axis', 'pixels per unit, Y axis', 'unit specifier')
        values = struct.unpack_from(">IIB", self.binary, offset + 8)
        return dict(zip(labels, values))

    def tEXt(self, chunk, offset):
        offset += 8
        data_offset = 0
        keyword = ''
        while(True):
            c = struct.unpack_from(">s", self.binary, offset + data_offset)
            if c[0] == b'\x00': break
            keyword += str(c[0])
            data_offset += 1
        data_offset += 1
        text_string = ''
        while(data_offset < chunk[0]):
            c = struct.unpack_from(">s", self.binary, offset + data_offset)
            text_string += str(c[0])
            data_offset += 1
        return {'keyword': keyword, 'text string': text_string}

    def tIME(self, chunk, offset):
        labels = ('year', 'month', 'day', 'hour', 'minute', 'second')
        values = struct.unpack_from(">H5B", self.binary, offset + 8)
        return dict(zip(labels, values))

    def IDAT(self, chunk, offset):
        labels = ('image data',)
        values = ('TODO',)
        return dict(zip(labels, values))

    def IEND(self, chunk, offset):
        return ()

with open('./sunrise.png', 'rb') as f:
    png = PNG(f.read())
    if not png.is_PNG():
       print('ERROR: This is not png')
       sys.exit(1)

    offset = 8
    while(True):
        print('--------------------')
        chunk = png.chunk(offset)
        print(chunk)
        if(chunk[1] == b'IEND'):
            break
        chunk_data = png.chunk_data(chunk, offset)
        print(chunk_data)
        crc = png.CRC32(chunk, offset)
        if chunk[2] != crc:
            print('WARNING: CRC error. expected: %d actual: %d' % (chunk[2], crc))
        if chunk_data == False:
            break
        offset += chunk[0] + 12
