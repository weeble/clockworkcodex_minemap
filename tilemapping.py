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
import PIL.Image


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


pygame.init()

tilemap = make_numbered_texture_atlas()
atlas = pygame.image.load('terrain.png')
#atlas = make_numbered_texture_atlas()


#
# Actually, for a first pass we can just use the same texture
# both times.
#
















def render(resources):
    glBindFramebuffer(GL_FRAMEBUFFER, resources.framebuffer_object)
    glViewport(0,0,8192,8192)
    glClearColor(0.1, 0.1, 0.1, 1.0)
    glClear(GL_COLOR_BUFFER_BIT)
    glUseProgram(resources.program)
    glUniform1f(resources.uniforms.timer, resources.timer)
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, resources.textures[0])
    glUniform1i(resources.uniforms.textures[0], 0)
    glActiveTexture(GL_TEXTURE1)
    glBindTexture(GL_TEXTURE_2D, resources.textures[1])
    glUniform1i(resources.uniforms.textures[1], 1)
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
    pixels = glReadPixelsub(0,0,8192,8192,GL_RGBA)
    print pixels.shape
    PIL.Image.fromarray(pixels.astype('u1')[::-1,:,:]).save("openglrender.png")
    #PIL.Image.fromarray(pixels[::-1,:]).save("openglrender.png")
    #print pixels

    sys.exit(0)
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

uniform float timer;

attribute vec4 position;

varying vec2 texcoord;
varying float fade_factor;

mat4 view_frustum(
    float angle_of_view,
    float aspect_ratio,
    float z_near,
    float z_far
) {
    return mat4(
        vec4(1.0/tan(angle_of_view),           0.0, 0.0, 0.0),
        vec4(0.0, aspect_ratio/tan(angle_of_view),  0.0, 0.0),
        vec4(0.0, 0.0,    (z_far+z_near)/(z_far-z_near), 1.0),
        vec4(0.0, 0.0, -2.0*z_far*z_near/(z_far-z_near), 0.0)
    );
}

mat4 scale(float x, float y, float z)
{
    return mat4(
        vec4(x,   0.0, 0.0, 0.0),
        vec4(0.0, y,   0.0, 0.0),
        vec4(0.0, 0.0, z,   0.0),
        vec4(0.0, 0.0, 0.0, 1.0)
    );
}

mat4 translate(float x, float y, float z)
{
    return mat4(
        vec4(1.0, 0.0, 0.0, 0.0),
        vec4(0.0, 1.0, 0.0, 0.0),
        vec4(0.0, 0.0, 1.0, 0.0),
        vec4(x,   y,   z,   1.0)
    );
}

mat4 rotate_x(float theta)
{
    return mat4(
        vec4(1.0,         0.0,         0.0, 0.0),
        vec4(0.0,  cos(timer),  sin(timer), 0.0),
        vec4(0.0, -sin(timer),  cos(timer), 0.0),
        vec4(0.0,         0.0,         0.0, 1.0)
    );
}

void main()
{
    gl_Position = //view_frustum(radians(45.0), 1.0, 0.5, 5.0)
        //translate(cos(timer/10.0), sin(timer/10.0), 0.0)
        //* rotate_x(timer)
        scale(1.0, 1.0, 1.0)
        * position;
    texcoord = position.xy * vec2(0.5) + vec2(0.5);
    fade_factor = sin(timer) * 0.5 + 0.5;
}
'''

fragment_shader = '''\
#version 130

varying float fade_factor;
uniform sampler2D textures[2];

varying vec2 texcoord;

void main()
{
    float utheta = mod(texcoord.x, 1.0/512.0);
    float vtheta = mod(texcoord.y, 1.0/512.0);
    float xx = 1.0-texcoord.y;
    float yy = texcoord.x;
    vec4 tiles_sample = texture2D(textures[0], vec2(xx,yy));
    float tile_value = round(255.0 * tiles_sample.x);
    float uphi = mod(tile_value, 16.0);
    float vphi = floor(tile_value / 16.0);
    vec2 atlas_point = vec2(uphi, vphi) / 16.0 + vec2(utheta, vtheta) / (16.0/512.0);
    gl_FragColor = texture2D(textures[1], atlas_point);
    gl_FragColor.xyz *= tiles_sample.y;
}
'''


class Resources(object):
    pass

class Uniforms(object):
    pass

class Attributes(object):
    pass

def make_resources(tilemap):
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
        make_texture(image=tilemap, interpolate=False),
        make_texture(image=atlas, interpolate=False)]
    resources.vertex_shader=make_shader(
        GL_VERTEX_SHADER,
        vertex_shader)
    resources.fragment_shader=make_shader(
        GL_FRAGMENT_SHADER,
        fragment_shader)
    resources.program=make_program(
        resources.vertex_shader,
        resources.fragment_shader)
    resources.uniforms=Uniforms()
    resources.uniforms.timer = glGetUniformLocation(
        resources.program,
        "timer")
    resources.uniforms.textures =[
        glGetUniformLocation(resources.program, "textures[0]"),
        glGetUniformLocation(resources.program, "textures[1]")]
    resources.attributes=Attributes()
    resources.attributes.position = glGetAttribLocation(
        resources.program, "position")

    resources.framebuffer_texture = make_square_target_texture(8192)
    resources.framebuffer_object = make_framebuffer_object(resources.framebuffer_texture)
    return resources

class State(object):
    timer = 0
    camera_pos = float_array(0,0,-3)

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
    print "Not sure about this one..."
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
    surface = pygame.display.set_mode((640,480), video_flags)
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

def hacky_map_render(tilemap, light_values):
    w,h = tilemap.shape
    pixels = numpy.zeros((w,h,3), dtype='u1')
    pixels[:,:,0] = tilemap
    pixels[:,:,1] = light_values

    video_flags = OPENGL|DOUBLEBUF
    pygame.init()
    surface = pygame.display.set_mode((640,480), video_flags)
    resources = make_resources(pygame.surfarray.make_surface(pixels))
    update_timer(resources)
    render(resources)
    

if __name__ == '__main__':
    main()


