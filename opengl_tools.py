#!/usr/bin/env python

# Copyright 2011, Annette Wilson
# Licensed under the MIT license: http://www.opensource.org/licenses/MIT

from OpenGL.GL import (
    GL_TEXTURE_2D,
    GL_TEXTURE_MIN_FILTER,
    GL_TEXTURE_MAG_FILTER,
    GL_NEAREST_MIPMAP_NEAREST,
    GL_NEAREST,
    GL_TEXTURE_WRAP_S,
    GL_TEXTURE_WRAP_T,
    GL_CLAMP_TO_EDGE,
    GL_TEXTURE_MAX_LOD,
    GL_RGBA8UI,
    GL_RGBA_INTEGER,
    GL_RGBA8,
    GL_RGBA,
    GL_RGB8UI,
    GL_RGB_INTEGER,
    GL_RGB8,
    GL_RGB,
    GL_GENERATE_MIPMAP,
    GL_TRUE,
    GL_UNSIGNED_BYTE,
    GL_TEXTURE_INTERNAL_FORMAT,
    GL_UNSIGNED_INT,
    GL_COMPILE_STATUS,
    GL_LINK_STATUS,
    GL_VERTEX_SHADER,
    GL_FRAGMENT_SHADER,
    GL_STATIC_DRAW,
    GLfloat,
    GLshort,
    glGetUniformLocation,
    glGetAttribLocation,
    glGenBuffers,
    glBindBuffer,
    glBufferData,
    glGenTextures,
    glBindTexture,
    glTexParameteri,
    glTexParameterf,
    glTexImage2D,
    glGetTexLevelParameteriv,
    glCreateShader,
    glShaderSource,
    glCompileShader,
    glGetShaderiv,
    glCreateProgram,
    glAttachShader,
    glLinkProgram,
    glGetProgramiv,
    glDeleteShader,
    glGetShaderInfoLog,
    glDeleteShader,
    glGetProgramInfoLog,
    glDeleteProgram)
import ctypes
import pygame
import pygame.image
import pygame.key
import numpy
import sys
from collections import namedtuple


ShaderProgram = namedtuple("ShaderProgram", "program uniforms attributes")


def assemble_shader_program(
        vertex_shader_source,
        fragment_shader_source,
        uniform_names,
        attribute_names):
    vertex_shader = make_shader(GL_VERTEX_SHADER, vertex_shader_source)
    fragment_shader = make_shader(GL_FRAGMENT_SHADER, fragment_shader_source)
    program = make_program(vertex_shader, fragment_shader)
    return ShaderProgram(
        program,
        get_uniforms(program, uniform_names),
        get_attributes(program, attribute_names))


def get_uniforms(program, names):
    return dict((name, glGetUniformLocation(program, name)) for name in names)


def get_attributes(program, names):
    return dict((name, glGetAttribLocation(program, name)) for name in names)


def make_buffer(target, buffer_data, size):
    buf = glGenBuffers(1)
    glBindBuffer(target, buf)
    glBufferData(target, size, buffer_data, GL_STATIC_DRAW)
    return buf


def float_array(*args):
    return numpy.array(args, dtype=GLfloat)


def short_array(*args):
    return numpy.array(args, dtype=GLshort)


def make_texture(
        filename=None,
        image=None,
        interpolate=True,
        alpha=False,
        integer=False,
        maxlod=None):
    if image == None:
        image = pygame.image.load(filename)
    pixels = pygame.image.tostring(image, "RGBA" if alpha else "RGB", True)
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexParameteri(
        GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,
        GL_NEAREST_MIPMAP_NEAREST if interpolate else GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S,     GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T,     GL_CLAMP_TO_EDGE)
    if maxlod is not None:
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAX_LOD, maxlod)
    if alpha:
        if integer:
            targetformat = GL_RGBA8UI
            sourceformat = GL_RGBA_INTEGER
        else:
            targetformat = GL_RGBA8
            sourceformat = GL_RGBA
    else:
        if integer:
            targetformat = GL_RGB8UI
            sourceformat = GL_RGB_INTEGER
        else:
            targetformat = GL_RGB8
            sourceformat = GL_RGB
    glTexParameteri(GL_TEXTURE_2D, GL_GENERATE_MIPMAP, GL_TRUE)
    glTexImage2D(
        GL_TEXTURE_2D,
        0,
        targetformat,
        image.get_width(),
        image.get_height(),
        0,
        sourceformat,
        GL_UNSIGNED_BYTE,
        pixels)

    print glGetTexLevelParameteriv(
            GL_TEXTURE_2D,
            0,
            GL_TEXTURE_INTERNAL_FORMAT)
    return texture


def make_shader(shadertype, source):
    shader = glCreateShader(shadertype)
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
        print glGetProgramInfoLog(program)
        glDeleteProgram(program)
        raise Exception("Failed to link shader program.")
    return program


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
