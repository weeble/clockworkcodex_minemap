from nbt import NBTFile
from struct import unpack
from zlib import decompress
from StringIO import StringIO
import numpy
#import PIL.Image
import time
from collections import defaultdict
import tilemapping

white = [255,255,255]
grey = [128,128,128]
green = [64,192,64]
brown = [96,64,0]
black = [32,32,32]
darkgrey = [64,64,64]
blue = [64,64,255]
red = [255,64,0]
yellow = [192,192,64]
tan = [255, 192, 128]
gold = [255,255,0]
rosered = [255,0,32]

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
    TileInfo(50, "torch",         True,  (0,0,0),(10,13,2),(10,13,0),(10,13,1),(10,13,3),(11,13,0)),
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
    TileInfo(63, "signpost",        True,  (0,6,0)),

    TileInfo(64, "door",                 True,  (1,6,0)),
    TileInfo(65, "ladder",               True,  (0,0,0),(0,0,0),(10,14,1), (10,14,3), (10,14,2), (10,14,0)),
    TileInfo(66, "rails",                True,  (0,8,1),(0,8,0),(0,8,0),(0,8,0),(0,8,1),(0,8,1),(0,7,1),(0,7,2),(0,7,3),(0,7,0)),
    TileInfo(67, "cobblestone stairs",   False, (0,1,0)),
    TileInfo(68, "wall sign",            True,  (0,6,0)),
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
    TileInfo(81, "cactus",      False, (5,4,0)),
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




#array([tileinfo.transparent for tileinfo in ])

def arrange_8bit(data):
    return numpy.fromstring(data,dtype='u1').reshape((16,16,128))

def arrange_4bit(data):
    packed = numpy.fromstring(data,dtype='u1')
    unpacked = numpy.zeros((len(data)*2,),dtype='u1')
    unpacked[::2] = packed&0xf
    unpacked[1::2] = packed>>4
    return unpacked.reshape((16,16,128))


def get_chunk(f, x, z, multitimer=None):
    #read metadata block
    if multitimer!=None:
        multitimer.start("reading")
    block = 4*(x+z*32)
    f.seek(block)
    offset, length = unpack(">IB", "\0"+f.read(4))
    #print offset
    if offset:
        f.seek(offset*4096)
        bytecount, compression_type  = unpack(">IB", f.read(5))
        #print bytecount, compression_type
        data = f.read(bytecount-1)
        if multitimer!=None:
            multitimer.start("decompressing")
        #print repr(data[:16])
        decompressed = decompress(data)
        if multitimer!=None:
            multitimer.start("parsing")
        nbtfile = NBTFile(buffer=StringIO(decompressed))
        if multitimer!=None:
            multitimer.stop()
        return nbtfile
        #return NBTFile(fileobj=f)
    else:
        return None

def read(fname, x, z):
    f = open(fname, "rb")
    return get_chunk(f, x, z)

def empty_array(dimensions, dtype='u1'):
    w,h = dimensions
    return numpy.zeros((w,h,128), dtype=dtype)

def empty_region_array(dtype='u1'):
    return numpy.zeros((512,512,128), dtype=dtype)


class HeightMappedSlice(object):
    def __init__(self, chunk, heightmap):
        self.blocks = get_cells_using_heightmap(chunk.blocks, heightmap)
        self.data = get_cells_using_heightmap(chunk.data, heightmap)
        air_heightmap = heightmap + 1
        self.skylight = get_cells_using_heightmap(chunk.skylight, air_heightmap)
        self.blocklight = get_cells_using_heightmap(chunk.blocklight, air_heightmap)

class Chunk(object):
    def __init__(self, dimensions=(16,16)):
        self.timer = MultiTimer()
        self.dimensions = dimensions
        self.blocks = empty_array(self.dimensions)
        self.skylight = empty_array(self.dimensions)
        self.blocklight = empty_array(self.dimensions)
        self.data = empty_array(self.dimensions)
    def load_chunk(self, nbtfile):        
        if nbtfile is None:
            self.blocks[:,:,:]=0
            self.skylight[:,:,:]=0
            self.blocklight[:,:,:]=0
            self.data[:,:,:]=0
            return
        self.dimensions=(16,16)
        level = nbtfile['Level']
        self.timer.start("blocks")
        self.blocks = arrange_8bit(level['Blocks'].value)
        self.timer.start("skylight")
        self.skylight = arrange_4bit(level['SkyLight'].value)
        self.timer.start("blocklight")
        self.blocklight = arrange_4bit(level['BlockLight'].value)
        self.timer.start("data")
        self.data = arrange_4bit(level['Data'].value)
        self.timer.stop()
    def load_region(self, fname):
        f = open(fname, "rb")
        chunk = Chunk()
        chunk.timer = self.timer
        for z in xrange(32):
            for x in xrange(32):
                self.timer.start("get_chunk")
                chunkdata = get_chunk(f, x, z, self.timer)
                self.timer.stop()
                chunk.load_chunk(chunkdata)
                self.timer.start("copying")
                self.blocks[16*x:16*(x+1), 16*z:16*(z+1), :] = chunk.blocks
                self.skylight[16*x:16*(x+1), 16*z:16*(z+1), :] = chunk.skylight
                self.blocklight[16*x:16*(x+1), 16*z:16*(z+1), :] = chunk.blocklight
                self.data[16*x:16*(x+1), 16*z:16*(z+1), :] = chunk.data
                self.timer.stop()
        self.timer.report()
    def get_deepest_air(self):
        #def deepest_air_in_col(col):
        #    return numpy.nonzero(col==0)[0][0]
        #return numpy.apply_along_axis(deepest_air_in_col, 2, self.blocks).astype('i4')
        return numpy.argmax(self.blocks == 0, axis=2)
    def get_highest_floor(self):
        max_height = self.blocks.shape[2]
        potential_floors = self.blocks[:,:,:-1]
        potential_footspace = self.blocks[:,:,1:]
        good_floors = numpy.logical_and(potential_floors!=0, potential_footspace==0)
        return (max_height-1)-numpy.argmax(good_floors[:,:,::-1], axis=2)
    def get_floor_heights(self, low_limit, high_limit, include_transparent=True):
        low_limit_3d = numpy.atleast_3d(low_limit)
        high_limit_3d = numpy.atleast_3d(high_limit)
        max_height = self.blocks.shape[2]
        shape = self.blocks.shape
        trimmed_shape = (shape[0], shape[1], shape[2]-1)
        cell_depth = numpy.indices(trimmed_shape)[2]
        cell_is_selected = numpy.logical_and(cell_depth>=low_limit_3d, cell_depth<high_limit_3d)
        selectable_substance = self.blocks[:,:,:-1] if include_transparent else numpy.logical_not(tileid_is_transparent[self.blocks[:,:,:-1]])
        potential_floors = numpy.logical_and(selectable_substance, cell_is_selected)
        potential_footspace = self.blocks[:,:,1:] if include_transparent else numpy.logical_not(tileid_is_transparent[self.blocks[:,:,1:]])
        good_floors = numpy.logical_and(potential_floors!=0, potential_footspace==0)
        floor_heights = (max_height-2)-numpy.argmax(good_floors[:,:,::-1], axis=2)
        #print high_limit[260:266,480:490]
        #print floor_heights[260:266,480:490]
        #raise Exception("stop")
        return numpy.clip(floor_heights, low_limit, high_limit)
    def altitude_slice(self, low, high):
        chunk2 = Chunk(dimensions=self.dimensions)
        chunk2.blocks = self.blocks[:,:,low:high]
        chunk2.skylight = self.skylight[:,:,low:high]
        chunk2.blocklight = self.blocklight[:,:,low:high]
        chunk2.data = self.data[:,:,low:high]
        return chunk2

def get_cells_using_heightmap(source, heightmap):
    idx = [numpy.arange(dimension) for dimension in source.shape]
    idx = list(numpy.ix_(*idx))
    idx[2] = numpy.expand_dims(heightmap, 2)
    return numpy.squeeze(source[idx])


def save_byte_image(data, filename):
    PIL.Image.fromarray(data.astype('u1')[:,::-1]).save(filename)


def do_air_picture(fname):
    ch=Chunk((512,512))
    ch.load_region(fname)
    save_byte_image(ch.get_deepest_air(), fname+'_deepair.png')

def do_colour_air_picture(fname):
    ch=Chunk((512,512))
    ch.load_region(fname)
    deepest_air = ch.get_deepest_air()
    floor_heights = deepest_air - 1
    colour_values = colour_array[get_cells_using_heightmap(ch.blocks, floor_heights)]
    alpha_values = numpy.ones((512,512,1), dtype='i1') * 255
    rgba_values = numpy.dstack([colour_values, alpha_values])
    save_byte_image(rgba_values, fname+'_colourdeepair.png')

    

class AccTimer(object):
    def __init__(self):
        self.lasttime=None
        self.acc=0.0
    def start(self):
        self.lasttime = time.time()
    def stop(self):
        self.acc += time.time() - self.lasttime
        self.lasttime = None

class MultiTimer(object):
    def __init__(self):
        self.timers = defaultdict(AccTimer)
        self.current = None
    def start(self, name):
        if self.current is not None:
            self.timers[self.current].stop()
        self.timers[name].start()
        self.current = name
    def stop(self):
        if self.current is not None:
            self.timers[self.current].stop()
        self.current = None
    def report(self):
        for name, timer in self.timers.items():
            print name, "%.2fs" % timer.acc
        

class Timer(object):
    def __init__(self):
        self.lasttime=None
    def start(self):
        self.lasttime = time.time()
    def event(self, name=""):
        newtime = time.time()
        elapsed = ("%.2fs" % (newtime - self.lasttime)) if self.lasttime is not None else "N/A"
        print name, elapsed
        self.lasttime = newtime
    def stop(self):
        self.lasttime = time.time()

def darken_by_depth(colour_array, depth_array, low_depth, high_depth, low_brightness, high_brightness):
    colour_values = colour_array.astype('f4')
    delta_depth = float(high_depth - low_depth)
    delta_brightness = float(high_brightness - low_brightness)
    colour_values *= numpy.expand_dims((((depth_array - low_depth) / delta_depth) + low_brightness) * delta_brightness,2)
    colour_values = numpy.clip(colour_values, 0.0, 255.0)
    return colour_values #.astype('i1')
    
def darken_by_blocklight(colour_array, depth_array, blocklight, low_brightness, high_brightness):
    #colour_values = colour_array.astype('f4')
    light_levels = get_cells_using_heightmap(blocklight, depth_array)
    return darken_by_depth(colour_array, light_levels, 0.0, 15.0, low_brightness, high_brightness)

def darken_by_combined_light(colour_array, depth_array, blocklight, skylight, low_brightness, high_brightness, daylight):
    block_light_levels = get_cells_using_heightmap(blocklight, depth_array)
    sky_light_levels = get_cells_using_heightmap(skylight, depth_array)
    light_levels = numpy.max([block_light_levels.astype('f4'), sky_light_levels.astype('f4') * daylight], axis=0)
    return darken_by_depth(colour_array, light_levels, 0.0, 15.0, low_brightness, high_brightness)
    
def light_levels_combined(depth_array, blocklight, skylight, low_brightness, high_brightness, daylight):
    block_light_levels = get_cells_using_heightmap(blocklight, depth_array)
    sky_light_levels = get_cells_using_heightmap(skylight, depth_array)
    light_levels = numpy.max([block_light_levels.astype('f4'), sky_light_levels.astype('f4') * daylight], axis=0)
    low_depth = 0
    high_depth = 15
    delta_depth = float(high_depth - low_depth)
    delta_brightness = float(high_brightness - low_brightness)
    new_light_levels = (((light_levels - low_depth) / delta_depth) + low_brightness) * delta_brightness
    return numpy.clip(new_light_levels*255.0, 0.0, 255.0)

def array_rescale(array, old_low_value, old_high_value, new_low_value, new_high_value):
    old_delta = old_high_value - old_low_value
    new_delta = new_high_value - new_low_value
    return (array - old_low_value) / old_delta * new_delta + new_low_value

def do_shaded_colour_air_picture(fname):
    t=Timer()
    t.start()
    ch=Chunk((512,512))
    ch.load_region(fname)
    t.event("Loading")
    for low, high in [(0,128)]: #34),(31,65),(63,97),(94,128)]:
        chunk_slice = ch.altitude_slice(low, high)
        #deepest_air = chunk_slice.get_deepest_air()
        #floor_heights = chunk_slice.get_highest_floor() - 1
        max_heights = numpy.indices((512,512))[1] // 5
        max_heights[:,:] = 127
        print "max_heights.shape (expecting (512,512)):", max_heights.shape
        floor_heights = chunk_slice.get_floor_heights(0,max_heights,False)
        t.event("Deep air")
        #floor_heights = deepest_air - 1
        deepest_air = floor_heights + 1
        t.event("Floor heights")
        #colour_values = colour_array[get_cells_using_heightmap(chunk_slice.blocks, floor_heights)]
        t.event("Get cells using heightmap")
        #colour_values = darken_by_depth(colour_values, deepest_air, 0.0, 128.0, 0.2, 1.0)
        '''
        colour_values = colour_values.astype('f4')
        colour_values *= numpy.expand_dims(deepest_air,2)
        colour_values = numpy.clip((colour_values / 36.0) + 32, 0.0, 255.0)
        colour_values = colour_values.astype('i1')
        '''
        light_levels = light_levels_combined(deepest_air,
            chunk_slice.blocklight, chunk_slice.skylight, 0.8, 1.4, 0.2)
        light_levels[:,:] = 255.0
        depth_lighting = numpy.clip((floor_heights-60.0)/20.0, 0.2, 1.0)
        light_levels = numpy.clip(light_levels*depth_lighting, 20.0, 255.0)
        t.event("Colour manipulation")
        alpha_values = numpy.ones((512,512,1), dtype='i1') * 255
        numpy.putmask(alpha_values, floor_heights == max_heights, 0)
        #rgba_values = numpy.dstack([colour_values, alpha_values])
        blocks = get_cells_using_heightmap(chunk_slice.blocks, floor_heights)
        data = get_cells_using_heightmap(chunk_slice.data, floor_heights)
        block_array = tileid_advanced_mapping_array[blocks, data, 0]
        orientation_array = tileid_advanced_mapping_array[blocks, data, 1]
        tilemapping.hacky_map_render(block_array, light_levels, orientation_array)  #tileid_mapping_bytes[get_cells_using_heightmap(chunk_slice.blocks, floor_heights)], light_levels)
        #save_byte_image(rgba_values, fname+'_generalised_slice.png')
        t.event("Finishing and saving")

def x():
    do_shaded_colour_air_picture('world/region/r.0.0.mcr')
#class Region(object):
#    def __ini

#def write_image
