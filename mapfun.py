from nbt import NBTFile
from struct import unpack
from zlib import decompress
from StringIO import StringIO
import numpy
#import PIL.Image
import time
from collections import defaultdict
import tilemapping
import os.path
import sys

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

class HeightMappedSlice(object):
    def __init__(self, chunk, heightmap):
        self.blocks = get_cells_using_heightmap(chunk.blocks, heightmap)
        self.data = get_cells_using_heightmap(chunk.data, heightmap)
        air_heightmap = heightmap + 1
        self.skylight = get_cells_using_heightmap(chunk.skylight, air_heightmap)
        self.blocklight = get_cells_using_heightmap(chunk.blocklight, air_heightmap)

class VolumeFactory(object):
    def __init__(self, timer):
        self.timer = timer
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
                raise TypeError("load_chunk requires a volume that is 16x16x128")
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
        self.timer.start("blocks")
        volume.blocks[:,:,:] = arrange_8bit(level['Blocks'].value)
        self.timer.start("skylight")
        volume.skylight[:,:,:] = arrange_4bit(level['SkyLight'].value)
        self.timer.start("blocklight")
        volume.blocklight[:,:,:] = arrange_4bit(level['BlockLight'].value)
        self.timer.start("data")
        volume.data[:,:,:] = arrange_4bit(level['Data'].value)
        self.timer.stop()
        return volume
    def load_region(self, fname):
        f = open(fname, "rb")
        region = self.empty_volume((512,512,128))
        chunk = self.empty_volume((16,16,128))
        for z in xrange(32):
            for x in xrange(32):
                self.timer.start("get_chunk")
                chunkdata = get_chunk(f, x, z, self.timer)
                self.timer.stop()
                self.load_chunk(chunkdata, volume=chunk)
                self.timer.start("copying")
                region[16*x:16*(x+1), 16*z:16*(z+1), :] = chunk
                self.timer.stop()
        #self.timer.report()
        return region
    def load_rectangle(self, regiondir, xmin, zmin, xmax, zmax):
        chunk_xmin = xmin // 16
        chunk_xmax = (xmax + 15) // 16
        chunk_zmin = zmin // 16
        chunk_zmax = (zmax + 15) // 16
        region_files = {}
        chunk = self.empty_volume((16,16,128))
        volume = self.empty_volume((16*(chunk_xmax-chunk_xmin), 16*(chunk_zmax-chunk_zmin), 128))
        for chunkz in xrange(chunk_zmin, chunk_zmax):
            for chunkx in xrange(chunk_xmin, chunk_xmax):
                fname = "r.{0}.{1}.mcr".format(chunkx//32, chunkz//32)
                if fname not in region_files:
                    try:
                        region_files[fname] = open(os.path.join(regiondir,fname), "rb")
                    except:
                        region_files[fname] = None
                f = region_files[fname]
                if f is None:
                    chunkdata = None
                else:
                    self.timer.push("get_chunk")
                    chunkdata = get_chunk(f, chunkx % 32, chunkz % 32, self.timer)
                    self.timer.pop()
                self.timer.push("load_chunk")
                self.load_chunk(chunkdata, volume=chunk)
                self.timer.pop()
                self.timer.start("copy_chunk_to_volume")
                chunkix = chunkx - chunk_xmin
                chunkiz = chunkz - chunk_zmin
                #print 16*chunkix, 16*(chunkix+1), 16*chunkiz, 16*(chunkiz+1)
                volume[16*chunkix:16*(chunkix+1), 16*chunkiz:16*(chunkiz+1), :] = chunk
                self.timer.stop()
        for f in region_files.values():
            if f is not None:
                f.close()
        return volume





class CellArray(object):
    def __init__(self, data):
        self._data=data
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

class Layer(CellArray):
    def get_texture_codes(self, mask=None):
        if mask is None:
            return tileid_advanced_mapping_array[self.blocks, self.data, 0]
        return tileid_advanced_mapping_array[numpy.choose(mask, [numpy.zeros(self.dimensions, dtype='u1'), self.blocks]), self.data, 0]
    def get_orientations(self):
        return tileid_advanced_mapping_array[self.blocks, self.data, 1]
    def render(self, renderdatafactory=None):
        if renderdatafactory is None:
            renderdatafactory = LayerRenderDataFactory()
        renderdata

class LayerRenderData(object):
    def __init__(self, data):
        self._data=data
    @property
    def dimensions(self):
        return self._data.shape
    @property
    def texture_code(self):
        return self._data['texture_code']
    @property
    def brightness(self):
        return self._data['brightness']
    @property
    def orientation(self):
        return self._data['orientation']
    @property
    def altitude(self):
        return self._data['altitude']
    def __getitem__(self, index):
        data = self._data[index]
        return LayerRenderData(data)
    def __setitem__(self, index, value):
        self._data[index] = value._data
    
class LayerRenderDataFactory(object):
    def empty_render_data(self, dimensions):
        data = numpy.zeros(
            dimensions,
            dtype = [
                ('texture_code', 'u1'),
                ('brightness', 'u1'),
                ('orientation', 'u1'),
                ('altitude', 'u1')])
        return LayerRenderData(data)

class Volume(CellArray):
    @property
    def height(self):
        return self.dimensions[2]
    def heightmap_slice(self, heightmap):
        # For solid blocks, use the lighting data of the cell above.
        this_layer = get_cells_using_heightmap(self._data, heightmap)
        above_layer = get_cells_using_heightmap(self._data, numpy.clip(heightmap + 1, 0, self.height-1))
        is_transparent = tileid_is_transparent[this_layer['blocks']]
        result = this_layer.copy()
        result['skylight'] = numpy.choose(is_transparent, [above_layer['skylight'], this_layer['skylight']])
        result['blocklight'] = numpy.choose(is_transparent, [above_layer['blocklight'], this_layer['blocklight']])
        return Layer(result)
    def get_transparent_item_heights_and_mask(self, low_limit, high_limit):
        low_limit_3d = numpy.atleast_3d(low_limit)
        high_limit_3d = numpy.atleast_3d(high_limit)
        max_height = self.blocks.shape[2]
        shape = self.blocks.shape
        trimmed_shape = (shape[0], shape[1], shape[2]-1)
        cell_depth = numpy.indices(trimmed_shape)[2]
        cell_is_selected = numpy.logical_and(cell_depth>=low_limit_3d, cell_depth<high_limit_3d)
        selectable_substance = numpy.logical_and(tileid_is_transparent[self.blocks[:,:,:-1]], self.blocks[:,:,:-1] != 0)
        potential_blocks = numpy.logical_and(selectable_substance, cell_is_selected)
        floor_heights = (max_height-2)-numpy.argmax(potential_blocks[:,:,::-1], axis=2)
        mask = get_cells_using_heightmap(potential_blocks, floor_heights)
        return numpy.clip(floor_heights, low_limit, high_limit), mask
    def get_floor_heights_and_mask(self, low_limit, high_limit, include_transparent=True):
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
        mask = get_cells_using_heightmap(good_floors, floor_heights)
        return numpy.clip(floor_heights, low_limit, high_limit), mask

def get_cells_using_heightmap(source, heightmap):
    idx = [numpy.arange(dimension) for dimension in source.shape]
    idx = list(numpy.ix_(*idx))
    idx[2] = numpy.expand_dims(heightmap, 2)
    return numpy.squeeze(source[idx])

def save_byte_image(data, filename):
    PIL.Image.fromarray(data.astype('u1')[:,::-1]).save(filename)

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
        self.stack = []
        self.current = None
        self.report_format = []
    def push(self, name):
        self.start(name)
        self.stack.append(self.current)
        self.current = None
    def pop(self):
        self.stop()
        self.current = self.stack.pop()
        self.stop()
    def start(self, name):
        if self.current is not None:
            self.timers[self.current].stop()
        if name not in self.timers:
            self.report_format.append((name, len(self.stack)))
        self.timers[name].start()
        self.current = name
    def stop(self):
        if self.current is not None:
            self.timers[self.current].stop()
        self.current = None
    def report(self):
        for name, depth in self.report_format:
            print ("  "*depth) + name, "%.3fs" % self.timers[name].acc
        #for name, timer in self.timers.items():
        #    print name, "%.2fs" % timer.acc

class VolumeAnalyser(object):
    low_limit = 0
    high_limit = 127
    ambient_light = 0.1
    depth_light = 0.6
    true_light = 0.3
    daylight = 0.0
    layerfactory = LayerRenderDataFactory()

    def __init__(self, multitimer):
        self.multitimer = multitimer

    def apply_lighting(self, layer, heightmap):
        depth_light = (heightmap - 1.0 * self.low_limit) / (1.0 * (self.high_limit - self.low_limit))
        true_light = numpy.max([layer.blocklight / 15.0, layer.skylight * (self.daylight / 15.0)], axis=0)
        return ((self.ambient_light + depth_light * self.depth_light + true_light * self.true_light) * 255.0 + 0.5).astype('u1')

    def analyse_volume(self, volume):
        ''' Takes a volume, returns two LayerRenderData, one for the floors, and one for
        transparent objects. (In future, we might do more layers, because it's not nice to
        lose train tracks or flowers when they are partially obscured by glass or torches.)'''
        self.multitimer.start("floor_heights")
        floor_heights, mask = volume.get_floor_heights_and_mask(self.low_limit, self.high_limit, False)
        self.multitimer.start("decoration_heights")
        decoration_heights, mask2 = volume.get_transparent_item_heights_and_mask(floor_heights+1, self.high_limit)
        self.multitimer.start("slicing")
        mask2 = numpy.logical_and(mask, mask2)
        floor_slice = volume.heightmap_slice(floor_heights)
        transparent_slice = volume.heightmap_slice(decoration_heights)
        floor_render_data = self.layerfactory.empty_render_data(floor_slice.dimensions)
        transparent_render_data = self.layerfactory.empty_render_data(floor_slice.dimensions)
        self.multitimer.start("assembly")
        floor_render_data.texture_code[:,:] = floor_slice.get_texture_codes(mask)
        floor_render_data.brightness[:,:] = self.apply_lighting(floor_slice, floor_heights)
        floor_render_data.orientation[:,:]= floor_slice.get_orientations()
        floor_render_data.altitude[:,:] = floor_heights
        transparent_render_data.texture_code[:,:] = transparent_slice.get_texture_codes(mask2)
        transparent_render_data.brightness[:,:] = self.apply_lighting(transparent_slice, floor_heights)
        transparent_render_data.orientation[:,:] = transparent_slice.get_orientations()
        transparent_render_data.altitude[:,:] = floor_heights
        self.multitimer.stop()
        return floor_render_data, transparent_render_data
        




def do_shaded_colour_air_picture(fname,low_limit,high_limit,centre=(256,256)):
    mt = MultiTimer()
    mt.push("Total")
    volume_factory = VolumeFactory(mt)
    volume_analyser = VolumeAnalyser(mt)
    # You can tweak the height limits here:
    volume_analyser.low_limit=low_limit
    volume_analyser.high_limit=high_limit
    mt.push("load_region")
    #region = volume_factory.load_rectangle(fname, -256, -512, 256, 0)
    mt.pop()
    mt.push("analyse_volume")
    x,y = centre
    ground_render_data = volume_analyser.layerfactory.empty_render_data((512,512))
    transparent_render_data = volume_analyser.layerfactory.empty_render_data((512,512))
    sys.stdout.write("[                ]\x0d[")
    for y1,y2 in [(0,128),(128,256),(256,384),(384,512)]:
        for x1,x2 in [(0,128),(128,256),(256,384),(384,512)]:
            local_region = volume_factory.load_rectangle(fname, y1-256+y, x1-256+x, y2-256+y, x2-256+x)
            ground_render_data_small, transparent_render_data_small = volume_analyser.analyse_volume(local_region) #region[y1:y2,x1:x2])
            ground_render_data[y1:y2,x1:x2] = ground_render_data_small
            transparent_render_data[y1:y2,x1:x2] = transparent_render_data_small
            sys.stdout.write("=")
            sys.stdout.flush()
    print
    mt.pop()
    mt.pop()
    mt.report()
    tilemapping.hacky_map_render(
        ground_render_data.texture_code,
        ground_render_data.brightness,
        ground_render_data.orientation,
        ground_render_data.altitude,
        transparent_render_data.texture_code,
        transparent_render_data.orientation,
        transparent_render_data.altitude)
    #save_byte_image(rgba_values, fname+'_generalised_slice.png')

def x():
    #do_shaded_colour_air_picture('world/region/r.0.0.mcr')
    CHORUSMAP = 'chorus/world/region'
    ROBBIEMAP = 'world/region'
    do_shaded_colour_air_picture(ROBBIEMAP, 0, 20, centre=(256,256)) #/r.0.-1.mcr',0,128)
