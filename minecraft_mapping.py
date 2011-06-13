from nbt import NBTFile
from struct import unpack
from zlib import decompress
from StringIO import StringIO
import numpy
import time
from collections import defaultdict
import tilemapping
import os.path
import sys


class TileInfo(object):
    def __init__(self, blockid, name, transparent, *texture_frames):
        self.name = name
        self.blockid = blockid
        self.transparent = transparent
        # Pad texture_frames out to 16 entries:
        self.texture_frames = texture_frames + tuple(texture_frames[0] for i in xrange(16-len(texture_frames)))

all_tileinfo = [
    TileInfo(0,  "air",         True,  (2,14,0)),
    TileInfo(1,  "stone",       False, (1,0,0)),
    TileInfo(2,  "grass",       False, (0,0,0)),
    TileInfo(3,  "dirt",        False, (2,0,0)),
    TileInfo(4,  "cobblestone", False, (0,1,0)),
    TileInfo(5,  "planks",      False, (4,0,0)),
    TileInfo(6,  "sapling",     True,  (15,0,0)),
    TileInfo(7,  "bedrock",     False, (1,1,0)),

    TileInfo(8,  "water",   False, (15,13,0)),
    TileInfo(9,  "water",   False, (15,13,0)),
    TileInfo(10, "lava",    False, (15,15,0)),
    TileInfo(11, "lava",    False, (15,15,0)),
    TileInfo(12, "sand",    False, (2,1,0)),
    TileInfo(13, "gravel",  False, (3,1,0)),
    TileInfo(14, "goldore", False, (0,2,0)),
    TileInfo(15, "ironore", False, (1,2,0)),

    TileInfo(16, "coal",      False, (2,2,0)),
    TileInfo(17, "log",       False, (5,1,0)),
    TileInfo(18, "leaves",    False, (5,3,0)),
    TileInfo(19, "sponge",    False, (0,3,0)),
    TileInfo(20, "glass",     True,  (1,3,0)),
    TileInfo(21, "lapisore",  False, (0,10,0)),
    TileInfo(22, "lapis",     False, (0,9,0)),
    TileInfo(23, "dispenser", False, (14,3,0)),

    TileInfo(24, "sandstone",     False, (0,12,0)),
    TileInfo(25, "note",          False, (11,4,0)),
    TileInfo(26, "bed",           False, (6,8,0)),
    TileInfo(27, "powered rail",  True,  (3,10,1),(3,10,0),(3,10,0),(3,10,0),(3,10,1),(3,10,1),(0,0,0),(0,0,0),(3,11,1),(3,11,0),(3,11,0),(3,11,0),(3,11,1),(3,11,1),(0,0,0),(0,0,0)),
    TileInfo(28, "detector rail", True,  (3,12,1),(3,12,0),(3,12,0),(3,12,0),(3,12,1),(3,12,1)),
    TileInfo(30, "web",           True,  (11,0,0)),

    TileInfo(35, "wool",           False, (0,4,0),(2,13,0),(2,12,0),(2,11,0),(2,10,0),(2,9,0),(2,8,0),(2,7,0),(1,14,0),(1,13,0),(1,12,0),(1,11,0),(1,10,0),(1,9,0),(1,8,0),(1,7,0)),
    TileInfo(37, "dandelion",      True,  (13,0,0)),
    TileInfo(38, "rose",           True,  (12,0,0)),
    TileInfo(39, "brown mushroom", True,  (13,1,0)),

    TileInfo(40, "red mushroom", True,  (12,1,0)),
    TileInfo(41, "gold",         False, (7,1,0)),
    TileInfo(42, "iron",         False, (6,1,0)),
    TileInfo(43, "slabs",        False, (6,0,0)),
    TileInfo(44, "slab",         False, (6,0,0)),
    TileInfo(45, "brick",        False, (7,0,0)),
    TileInfo(46, "tnt",          False, (9,0,0)),
    TileInfo(47, "bookshelf",    False, (4,0,0)),

    TileInfo(48, "mossy",         False, (4,2,0)),
    TileInfo(49, "obsidian",      False, (5,2,0)),
    TileInfo(50, "torch",         True,  (0,0,0),(10,13,2),(10,13,0),(10,13,3),(10,13,1),(11,13,0)),
    TileInfo(51, "fire",          True,  (15,15,0)),
    TileInfo(52, "spawner",       False, (1,4,0)),
    TileInfo(53, "stairs",        False, (4,0,0)),
    TileInfo(54, "chest",         False, (9,1,0)),
    TileInfo(55, "redstone wire", True,  (4,6,0)),

    TileInfo(56, "diamond ore",     False, (2,3,0)),
    TileInfo(57, "diamond block",   False, (8,2,0)),
    TileInfo(58, "crafting table",  False, (11,2,0)),
    TileInfo(59, "seeds???",        False, (6,5,0)),
    TileInfo(60, "farmland",        False, (6,5,0)),
    TileInfo(61, "furnace",         False, (14,3,0)),
    TileInfo(62, "burning furnace", False, (14,3,0)),
    TileInfo(63, "signpost",        True,  (12,14,1),(11,15,1),(12,15,1),(0,6,0)),

    TileInfo(64, "door",                 True,  (1,6,0)),
    TileInfo(65, "ladder",               True,  (0,0,0),(0,0,0),(10,14,1), (10,14,3), (10,14,0), (10,14,2)),
    TileInfo(66, "rails",                True,  (0,8,1),(0,8,0),(0,8,0),(0,8,0),(0,8,1),(0,8,1),(0,7,1),(0,7,2),(0,7,3),(0,7,0)),
    TileInfo(67, "cobblestone stairs",   False, (0,1,0)),
    TileInfo(68, "wall sign",            True,  (0,0,0),(0,0,0),(11,14,1),(11,14,3),(11,14,0),(11,14,2)),
    TileInfo(69, "lever",                True,  (0,6,0)),
    TileInfo(70, "stone pressure plate", True,  (1,0,0)),
    TileInfo(71, "iron door",            True,  (2,6,0)),

    TileInfo(72, "wooden pressure plate", True,  (4,0,0)),
    TileInfo(73, "redstone ore",          False, (3,3,0)),
    TileInfo(74, "glowing redstone ore",  False, (3,3,0)),
    TileInfo(75, "redstone torch, off",   True,  (3,7,0)),
    TileInfo(76, "redstone torch, on",    True,  (3,6,0)),
    TileInfo(77, "stone button",          True,  (0,6,0)),
    TileInfo(78, "snow",                  False, (2,4,0)),
    TileInfo(79, "ice",                   False, (3,4,0)),

    TileInfo(80, "snow block",  False, (2,4,0)),
    TileInfo(81, "cactus",      True,  (5,4,0)),
    TileInfo(82, "clay",        False, (8,4,0)),
    TileInfo(83, "sugar cane",  False, (9,4,0)),
    TileInfo(84, "jukebox",     False, (11,4,0)),
    TileInfo(85, "fence",       True,  (3,5,0)),
    TileInfo(86, "pumpkin",     False, (6,6,0)),
    TileInfo(87, "netherrack",  False, (7,6,0)),

    TileInfo(88, "soulsand",       False, (8,6,0)),
    TileInfo(89, "glowstone",      False, (9,7,0)),
    TileInfo(90, "portal",         True,  (12,1,0)),
    TileInfo(91, "jock-o-lantern", False, (6,6,0)),
    TileInfo(92, "cake",           True,  (9,7,0)),
    TileInfo(93, "repeater, off",  True,  (3,8,0)),
    TileInfo(94, "repeater, on",   True,  (3,9,0)),
    TileInfo(95, "locked chest",   False, (9,1,0)),
    ]

tileid_advanced_mapping_array = numpy.zeros((256,16,2), dtype="u1")
tileid_is_transparent = numpy.zeros((256,), dtype="bool")

for tileinfo in all_tileinfo:
    tileid_advanced_mapping_array[tileinfo.blockid] = [(x + 16 * (15 - y), r) for (x,y,r) in tileinfo.texture_frames]
    tileid_is_transparent[tileinfo.blockid] = tileinfo.transparent


def arrange_8bit(data):
    return numpy.fromstring(data,dtype='u1').reshape((16,16,128))


def arrange_4bit(data):
    packed = numpy.fromstring(data,dtype='u1')
    unpacked = numpy.zeros((len(data)*2,),dtype='u1')
    unpacked[::2] = packed&0xf
    unpacked[1::2] = packed>>4
    return unpacked.reshape((16,16,128))


def read_nbt_from_mcr_file(mcrfile, x, z):
    """
    Read NBT chunk (x,z) from the mcrfile.
    0 <= x < 32
    0 <= z < 32
    """
    #read metadata block
    block = 4*(x+z*32)
    mcrfile.seek(block)
    offset, length = unpack(">IB", "\0"+mcrfile.read(4))
    if offset:
        mcrfile.seek(offset*4096)
        bytecount, compression_type  = unpack(">IB", mcrfile.read(5))
        data = mcrfile.read(bytecount-1)
        decompressed = decompress(data)
        nbtfile = NBTFile(buffer=StringIO(decompressed))
        return nbtfile
    else:
        return None


class VolumeFactory(object):
    def empty_volume(self, dimensions):
        data = numpy.zeros(
            dimensions,
            dtype = [
                ('blocks', 'u1'),
                ('data', 'u1'),
                ('skylight', 'u1'),
                ('blocklight', 'u1')])
        return Volume(data)
    def load_chunk(self, nbtfile, volume=None):
        if volume is not None:
            if volume.dimensions != (16,16,128):
                raise TypeError(
                    "load_chunk requires a volume "+
                    "that is 16x16x128")
        if nbtfile is None:
            if volume is None:
                return self.empty_volume((16,16,128))
            volume.blocks[:,:,:]=0
            volume.skylight[:,:,:]=0
            volume.blocklight[:,:,:]=0
            volume.data[:,:,:]=0
            return volume
        if volume is None:
            volume = self.empty_volume((16,16,128))
        level = nbtfile['Level']
        blocks = arrange_8bit(level['Blocks'].value)
        skylight = arrange_4bit(level['SkyLight'].value)
        blocklight = arrange_4bit(level['BlockLight'].value)
        data = arrange_4bit(level['Data'].value)
        volume.blocks[:, :, :] =  blocks
        volume.skylight[:, :, :] = skylight
        volume.blocklight[:, :, :] = blocklight
        volume.data[:, :, :] = data
        return volume
    def load_region(self, fname):
        f = open(fname, "rb")
        region = self.empty_volume((512,512,128))
        chunk = self.empty_volume((16,16,128))
        for z in xrange(32):
            for x in xrange(32):
                chunkdata = read_nbt_from_mcr_file(f, x, z)
                self.load_chunk(chunkdata, volume=chunk)
                region[16*x:16*(x+1), 16*z:16*(z+1), :] = chunk
        return region


class Volume(object):
    def __init__(self, data):
        self._data = data
        self.height = self.dimensions[2]
    @property
    def dimensions(self):
        return self._data.shape
    @property
    def blocks(self):
        return self._data['blocks']
    @property
    def data(self):
        return self._data['data']
    @property
    def skylight(self):
        return self._data['skylight']
    @property
    def blocklight(self):
        return self._data['blocklight']
    def __getitem__(self, index):
        data = self._data[index]
        return type(self)(data)
    def __setitem__(self, index, value):
        self._data[index] = value._data

