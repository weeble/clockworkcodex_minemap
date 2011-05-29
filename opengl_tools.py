#!/usr/bin/env python

# Copyright 2011, Annette Wilson
# Licensed under the MIT license: http://www.opensource.org/licenses/MIT

from OpenGL.GL import *
import pygame, pygame.image, pygame.key
import numpy
import sys
from collections import namedtuple

class ShaderProgram(namedtuple("ShaderProgramBase", "program uniforms attributes")):
    pass

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
        get_uniforms(program, *uniform_names),
        get_attributes(program, *attribute_names))

def get_uniforms(program, *names):
    return dict((name, glGetUniformLocation(program, name)) for name in names)

def get_attributes(program, *names):
    return dict((name, glGetAttribLocation(program, name)) for name in names)

def make_buffer(target, buffer_data, size):
    buffer = glGenBuffers(1)
    glBindBuffer(target, buffer)
    glBufferData(target, size, buffer_data, GL_STATIC_DRAW)
    return buffer

def float_array(*args):
    return numpy.array(args, dtype=GLfloat)

def short_array(*args):
    return numpy.array(args, dtype=GLshort)

def make_texture(filename=None, image=None, interpolate=True, alpha=False):
    if image == None:
        image = pygame.image.load(filename)
    pixels = pygame.image.tostring(image, "RGBA" if alpha else "RGB", True)
    texture=glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR if interpolate else GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR if interpolate else GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S,     GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T,     GL_CLAMP_TO_EDGE)
    glTexImage2D(
        GL_TEXTURE_2D,
        0,
        GL_RGBA8 if alpha else GL_RGB8,
        image.get_width(),
        image.get_height(),
        0,
        GL_RGBA if alpha else GL_RGB,
        GL_UNSIGNED_BYTE,
        pixels)
    return texture

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
        print glGetProgramInfoLog(program)
        glDeleteProgram(program)
        raise Exception("Failed to link shader program.")
    return program
