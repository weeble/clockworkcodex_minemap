#!/usr/bin/env python

# Annette Wilson
# Translated from Joe Groff's "An intro to modern OpenGL"
# http://duriansoftware.com/joe/An-intro-to-modern-OpenGL.-Chapter-1:-The-Graphics-Pipeline.html

from OpenGL.GL import *
from OpenGL.GL.ARB.framebuffer_object import *
import pygame, pygame.image, pygame.key
from pygame.locals import *
import numpy
import math
import sys
import time
#import PIL.Image


#
# First of all, we need some textures to test things out with.
# We're going to make a 512x512 RGBA texture that's a 16x16 grid
# of 32x32 tile textures. Each of these will have a number from 0
# to 255 rendered on it.
# We're also going to make a 512x512 mono texture that's a random
# pattern, to use as a tile map.
#


def make_numbered_texture_atlas():
    surface = pygame.Surface((512,512))
    font = pygame.font.SysFont("arial",20,bold=True)
    
    for y in xrange(16):
        for x in xrange(16):
            fg = (255,255,255) if (x+y)%2==0 else (0,0,0)
            bg = (255,255,255) if (x+y)%2!=0 else (0,0,0)
            textimage = font.render(str(y*16+x), True, fg, bg)
            w,h = textimage.get_size()
            surface.fill(bg, (32*x, 32*y, 32, 32))
            surface.blit(textimage, (32*x+16-w//2, 32*y+16-h//2))

    return surface


#pygame.init()
pygame.font.init()

tilemap = make_numbered_texture_atlas()
atlas = pygame.image.load('terrain.png')
#atlas = make_numbered_texture_atlas()


#
# Actually, for a first pass we can just use the same texture
# both times.
#
















def render(resources, position, zoom, screen_dimensions):
    screen_w, screen_h = screen_dimensions
    glBindFramebuffer(GL_FRAMEBUFFER, 0) #resources.framebuffer_object)
    glViewport(0,0,screen_w,screen_h)
    glClearColor(0.4, 0.4, 0.4, 1.0)
    glClear(GL_COLOR_BUFFER_BIT)

    for texture in (resources.textures[0], resources.textures[2],):

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glUseProgram(resources.program)
        #glUniform1f(resources.uniforms.timer, resources.timer)
        glUniform2f(resources.uniforms['screen_dimensions'], screen_w, screen_h)
        glUniform2f(resources.uniforms['cam_position'], position[0], position[1])
        glUniform1f(resources.uniforms['zoom'], zoom)
        glUniform1f(resources.uniforms['tile_dimension'], 16.0) 


        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, texture) #resources.textures[0])
        glUniform1i(resources.uniforms['textures[0]'], 0)

        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, resources.textures[1])
        glUniform1i(resources.uniforms['textures[1]'], 1)

        glBindBuffer(GL_ARRAY_BUFFER, resources.vertex_buffer)
        glVertexAttribPointer(
            resources.attributes.position,
            4, # size
            GL_FLOAT, # type
            GL_FALSE, # normalized?
            ctypes.sizeof(GLfloat)*4, # stride
            None # offset
            )
        glEnableVertexAttribArray(resources.attributes.position)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, resources.element_buffer)
        glDrawElements(
            GL_TRIANGLE_STRIP,
            4,
            GL_UNSIGNED_SHORT,
            None)
        glDisableVertexAttribArray(resources.attributes.position)
        #pixels = glReadPixelsub(0,0,8192,8192,GL_RGBA)
        #print pixels.shape
        #PIL.Image.fromarray(pixels.astype('u1')[::-1,:,:]).save("openglrender.png")
        #PIL.Image.fromarray(pixels[::-1,:]).save("openglrender.png")
        #print pixels

        #sys.exit(0)
    pygame.display.flip()

def make_buffer(target, buffer_data, size):
    buffer = glGenBuffers(1)
    glBindBuffer(target, buffer)
    glBufferData(target, size, buffer_data, GL_STATIC_DRAW)
    return buffer

def float_array(*args):
    return numpy.array(args, dtype=GLfloat)

def short_array(*args):
    return numpy.array(args, dtype=GLshort)

vertex_buffer_data = float_array(
    -1.0, -1.0, 0.0, 1.0,
     1.0, -1.0, 0.0, 1.0,
    -1.0,  1.0, 0.0, 1.0,
     1.0,  1.0, 0.0, 1.0)

element_buffer_data = short_array(
    0,1,2,3)

vertex_shader='''\
#version 110

uniform vec2 screen_dimensions;
uniform vec2 cam_position;
uniform float zoom;
uniform float tile_dimension;

attribute vec4 position;

varying vec2 texcoord;

void main()
{
    gl_Position.xy = ((position.xy / 2.0 + 0.5) * tile_dimension * 512.0 - cam_position) * 2.0 * zoom / screen_dimensions;
    gl_Position.zw = vec2(0.0, 1.0);
    texcoord = position.xy; // * vec2(0.5) + vec2(0.5);
}
'''

fragment_shader = '''\
#version 130

const float MAX_ALT_DELTA = 3.0;
const float TILE_COUNT = 512.0;
const float INV_TILE_COUNT = 1.0 / TILE_COUNT;

// cardinal directions:
const int LE_MI = 0;
const int RI_MI = 1;
const int CE_UP = 2;
const int CE_DO = 3;

// diagonals:
const int LE_UP = 4;
const int RI_UP = 5;
const int LE_DO = 6;
const int RI_DO = 7;

uniform sampler2D textures[2];

varying vec2 texcoord;

float lightcalc(in float alt_delta, in float distance)
{
    return clamp(distance * MAX_ALT_DELTA / clamp(255.0 * alt_delta, 0.001, MAX_ALT_DELTA), 0.0, 1.0);
}

float cornerlight(in float side1, in float side2, in float corner, in float distance1, in float distance2)
{
    float side1light = lightcalc(side1, distance1);
    float side2light = lightcalc(side2, distance2);
    float corner1light = lightcalc(corner, distance1);
    float corner2light = lightcalc(corner, distance2);
    // TODO: Figure out why the 2* multiplier is needed in the next line!
    return side1light*side2light - 2*max(0, side1light-corner1light)*max(0, side2light-corner2light);
}

void main()
{
    vec2 theta;

    theta = (mod(texcoord*0.5+0.5, INV_TILE_COUNT) * TILE_COUNT)*2.0 - 1.0;
    float xx = -texcoord.y * 0.5 + 0.5;
    float yy = texcoord.x * 0.5 + 0.5;
    vec4 tiles_sample = texture2D(textures[0], vec2(xx,yy));

    // Sample the altitude of the neighbouring tiles for the ambient occlusion calculation:
    float altitude = tiles_sample.w;
    float alts[8];

    alts[LE_MI] = texture2D(textures[0], vec2(xx-INV_TILE_COUNT,yy)).w-altitude;
    alts[RI_MI] = texture2D(textures[0], vec2(xx+INV_TILE_COUNT,yy)).w-altitude;
    alts[CE_UP] = texture2D(textures[0], vec2(xx,yy+INV_TILE_COUNT)).w-altitude;
    alts[LE_UP] = texture2D(textures[0], vec2(xx-INV_TILE_COUNT,yy+INV_TILE_COUNT)).w-altitude;
    alts[RI_UP] = texture2D(textures[0], vec2(xx+INV_TILE_COUNT,yy+INV_TILE_COUNT)).w-altitude;
    alts[CE_DO] = texture2D(textures[0], vec2(xx,yy-INV_TILE_COUNT)).w-altitude;
    alts[LE_DO] = texture2D(textures[0], vec2(xx-INV_TILE_COUNT,yy-INV_TILE_COUNT)).w-altitude;
    alts[RI_DO] = texture2D(textures[0], vec2(xx+INV_TILE_COUNT,yy-INV_TILE_COUNT)).w-altitude;

    // Calculate a transformation for the tile (lets us rotate and flip oriented textures, like rail-tracks):
    float flipx = (tiles_sample.z * 255.0) >= 8.0 ? -1.0 : 1.0;
    float rotation = mod(tiles_sample.z * 255.0, 8.0) * 0.5 * 3.141592653589793;
    mat2 transform = mat2(
        flipx * cos(rotation),   flipx * sin(rotation),
        -sin(rotation),          cos(rotation));

    float tile_value = round(255.0 * tiles_sample.x);
    float uphi = mod(tile_value, 16.0);
    float vphi = floor(tile_value / 16.0);
    vec2 atlas_point = (vec2(uphi, vphi) + 0.5) / 16.0 + (transform * theta * 0.5 / 16.0);
    gl_FragColor = texture2D(textures[1], atlas_point);
    // Green channel contains a brightness multiplier:
    gl_FragColor.xyz *= tiles_sample.y;

    float left_distance = max(0.001, 1-theta.y);
    float right_distance = max(0.001, 1+theta.y);
    float bottom_distance = max(0.001, 1+theta.x);
    float top_distance = max(0.001, 1-theta.x);
    float ambient_light = 0.25 * (
        cornerlight(alts[LE_MI], alts[CE_UP], alts[LE_UP], left_distance, top_distance) +
        cornerlight(alts[RI_MI], alts[CE_UP], alts[RI_UP], right_distance, top_distance) +
        cornerlight(alts[LE_MI], alts[CE_DO], alts[LE_DO], left_distance, bottom_distance) +
        cornerlight(alts[RI_MI], alts[CE_DO], alts[RI_DO], right_distance, bottom_distance));
    gl_FragColor.xyz *= ambient_light;
}
'''


class Resources(object):
    pass

class Uniforms(object):
    pass

class Attributes(object):
    pass

def get_uniforms(program, *names):
    return dict((name, glGetUniformLocation(program, name)) for name in names)

def make_resources(tilemap, tilemap2):
    resources = Resources()
    resources.vertex_buffer = make_buffer(
        GL_ARRAY_BUFFER,
        vertex_buffer_data,
        vertex_buffer_data.nbytes)
    resources.element_buffer = make_buffer(
        GL_ELEMENT_ARRAY_BUFFER,
        element_buffer_data,
        element_buffer_data.nbytes)
    resources.textures=[
        make_alpha_texture(image=tilemap, interpolate=False),
        make_alpha_texture(image=atlas, interpolate=False),
        make_alpha_texture(image=tilemap2, interpolate=False)]
    resources.vertex_shader=make_shader(
        GL_VERTEX_SHADER,
        vertex_shader)
    resources.fragment_shader=make_shader(
        GL_FRAGMENT_SHADER,
        fragment_shader)
    resources.program=make_program(
        resources.vertex_shader,
        resources.fragment_shader)
    resources.uniforms=get_uniforms(
        resources.program,
        'screen_dimensions',
        'cam_position',
        'zoom',
        'tile_dimension',
        'textures[0]',
        'textures[1]')
    #resources.uniforms=Uniforms()
    #resources.uniforms.timer = glGetUniformLocation(
    #    resources.program,
    #    "timer")
    #resources.uniforms.textures =[
    #    glGetUniformLocation(resources.program, "textures[0]"),
    #    glGetUniformLocation(resources.program, "textures[1]")]
    resources.attributes=Attributes()
    resources.attributes.position = glGetAttribLocation(
        resources.program, "position")

    resources.framebuffer_texture = make_square_target_texture(8192)
    resources.framebuffer_object = make_framebuffer_object(resources.framebuffer_texture)
    return resources

class State(object):
    timer = 0
    camera_pos = float_array(0,0,-3)

def make_alpha_texture(filename=None, image=None, interpolate=True):
    if image == None:
        image = pygame.image.load(filename)
    pixels = pygame.image.tostring(image, "RGBA", True)
    texture=glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR if interpolate else GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR if interpolate else GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S,     GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T,     GL_CLAMP_TO_EDGE)
    glTexImage2D(
        GL_TEXTURE_2D, 0,
        GL_RGBA8,
        image.get_width(), image.get_height(), 0,
        GL_RGBA, GL_UNSIGNED_BYTE,
        pixels)
    return texture

def make_texture(filename=None, image=None, interpolate=True):
    if image == None:
        image = pygame.image.load(filename)
    pixels = pygame.image.tostring(image, "RGB", True)
    texture=glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR if interpolate else GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR if interpolate else GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S,     GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T,     GL_CLAMP_TO_EDGE)
    glTexImage2D(
        GL_TEXTURE_2D, 0,
        GL_RGB8,
        image.get_width(), image.get_height(), 0,
        GL_RGB, GL_UNSIGNED_BYTE,
        pixels)
    return texture

def make_square_target_texture(dimension):
    texture=glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexImage2D(
        GL_TEXTURE_2D, 0,
        GL_RGB8,
        dimension, dimension, 0,
        GL_RGBA,
        GL_UNSIGNED_INT,
        None)
    return texture

def make_framebuffer_object(texture_object):
    fbo=glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, fbo)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture_object, 0)
    print glCheckFramebufferStatus(GL_FRAMEBUFFER)
    return fbo


def make_shader(type, source):
    shader = glCreateShader(type)
    glShaderSource(shader, source)
    glCompileShader(shader)
    retval = ctypes.c_uint(GL_UNSIGNED_INT)
    glGetShaderiv(shader, GL_COMPILE_STATUS, retval)
    if not retval:
        print >> sys.stderr, "Failed to compile shader."
        print glGetShaderInfoLog(shader)
        glDeleteShader(shader)
        raise Exception("Failed to compile shader.")
    return shader

def make_program(vertex_shader, fragment_shader):
    program = glCreateProgram()
    glAttachShader(program, vertex_shader)
    glAttachShader(program, fragment_shader)
    glLinkProgram(program)
    retval = ctypes.c_int()
    glGetProgramiv(program, GL_LINK_STATUS, retval)
    if not retval:
        print >> sys.stderr, "Failed to link shader program."
        print glGetShaderInfoLog(shader)
        glDeleteProgram(program)
        raise Exception("Failed to link shader program.")
    return program

def update_timer(resources):
    milliseconds = pygame.time.get_ticks()
    resources.timer = milliseconds * 0.001

def main():
    video_flags = OPENGL|DOUBLEBUF
    pygame.init()
    surface = pygame.display.set_mode((800,600), video_flags)
    resources = make_resources()
    frames = 0
    done = 0
    ticks = pygame.time.get_ticks()
    while not done:
        while 1:
            event = pygame.event.poll()
            if event.type == NOEVENT:
                break
            if event.type == KEYDOWN:
                pass
            if event.type == QUIT:
                done = 1
        update_timer(resources)
        render(resources)
        frames += 1
    print "fps:  %d" % ((frames*1000)/(pygame.time.get_ticks()-ticks))



# pygame.surfarray.make_surface is broken in 1.9.1. It reads uninitialized
# stack contents on 64-bit systems. :( Here we use numpy to do the copying
# instead.
def make_surface(array):
    w,h,depth = array.shape
    if depth == 4:
        surf = pygame.Surface((w,h), depth=32, flags=pygame.SRCALPHA)
        pixels = pygame.surfarray.pixels3d(surf)
        pixels[:,:,:] = array[:,:,:3]
        alpha = pygame.surfarray.pixels_alpha(surf)
        alpha[:,:] = array[:,:,3]
    elif depth == 3:
        surf = pygame.Surface((w,h), depth=32)
        pixels = pygame.surfarray.pixels3d(surf)
        pixels[:,:,:depth] = array
    else:
        raise ValueError("Array must have minor dimension of 3 or 4.")
    return surf

def hacky_map_render(tilemap, light_values, orientation_array, altitudes, tilemap2, orientation2, altitudes2):
    w,h = tilemap.shape
    pixels = numpy.zeros((w,h,4), dtype='u1')
    pixels[:,:,0] = tilemap
    pixels[:,:,1] = light_values
    pixels[:,:,2] = orientation_array #numpy.mod(numpy.indices((w,h))[1],16)
    pixels[:,:,3] = altitudes

    pixels2 = numpy.zeros((w,h,4), dtype='u1')
    pixels2[:,:,0] = tilemap2
    pixels2[:,:,1] = light_values
    pixels2[:,:,2] = orientation2
    pixels2[:,:,3] = altitudes2
    #numpy.dstack([tilemap2, light_values, orientation2])
    print pixels[190,300:320,2]
    print "Pixel shape (expecting (8192, 8192, 3)):", pixels.shape

    video_flags = OPENGL|DOUBLEBUF
    #pygame.init()
    pygame.display.init()
    # Workaround for pygame bug: pygame.time cannot be initialized if you don't
    # call pygame.init. But if we call that, pygame.mixer will be initialized
    # and add seconds to our shutdown time for no good reason. So instead we
    # replace get_ticks.
    pygame.time.get_ticks = lambda:int(time.time()*1000)
    #pygame.font.init()

    screen_dimensions = 1024, 768 #800,600
    surface = pygame.display.set_mode(screen_dimensions, video_flags)
    #resources = make_resources(pygame.surfarray.make_surface(pixels))
    resources = make_resources(make_surface(pixels), make_surface(pixels2))
    update_timer(resources)
    #render(resources)
    frames = 0
    done = 0
    zoom = 1.0
    position = [4096.0, 4096.0]
    dragging = False
    draglast = 0,0

    ticks = pygame.time.get_ticks()
    print ticks
    while not done:
        while 1:
            event = pygame.event.poll()
            if event.type == NOEVENT:
                break
            if event.type == KEYDOWN:
                pass
            if event.type == QUIT:
                done = 1
            if event.type == MOUSEMOTION:
                if dragging:
                    mx,my = event.pos
                    lx,ly = draglast
                    dx = (mx - lx)/zoom
                    dy = (my - ly)/zoom
                    position[0] -= dx
                    position[1] += dy
                    draglast = mx, my
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    draglast = event.pos
                    dragging = True
                if event.button == 4:
                    zoom *= 2.0
                if event.button == 5:
                    zoom /= 2.0
                    x,y = position
                    x = math.floor(x * zoom + 0.5) / zoom
                    y = math.floor(y * zoom + 0.5) / zoom
                    position = [x,y]
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False
        update_timer(resources)
        render(resources, position, zoom, screen_dimensions)
        frames += 1
    elapsed_ticks = pygame.time.get_ticks()-ticks
    if elapsed_ticks>0:
        print "fps:  %d" % ((frames*1000.0)/elapsed_ticks)
    else:
        print "fps:  ???"
    

if __name__ == '__main__':
    main()


