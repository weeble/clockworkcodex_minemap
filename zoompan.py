#!/usr/bin/env python

# Copyright 2011, Annette Wilson
# Licensed under the MIT license:
# http://www.opensource.org/licenses/MIT
#
# Minecraft mapping - Rendering something with OpenGL
#
# With great thanks to Joe Groff:
# http://duriansoftware.com/joe/An-intro-to-modern-OpenGL.-Chapter-1:-The-Graphics-Pipeline.html

from OpenGL.GL import *
import pygame, pygame.image, pygame.key
from pygame.locals import *
from opengl_tools import *
import math

vertex_shader='''\
#version 130

uniform vec2 screen_dimensions;
uniform vec2 cam_position;
uniform float zoom;
uniform float texture_dimension;
uniform float map_dimension;

in vec4 position;
out vec2 texcoord;

void main()
{
    gl_Position.xy =
        (
            (position.xy / 2.0 + 0.5)
            * texture_dimension
            - cam_position
        )
        * 2.0
        * zoom
        / screen_dimensions;
    gl_Position.zw = vec2(0.0, 1.0);
    texcoord = position.xy * 0.5 + 0.5;
}
'''

fragment_shader = '''\
#version 130

const float TILE_COUNT = 512.0;
const float INV_TILE_COUNT = 1.0 / TILE_COUNT;

uniform sampler2D texture_atlas;
uniform usampler2D map_texture;
uniform float zoom;

in vec2 texcoord;
out vec4 fragcolor;

void main()
{
    vec2 theta;

    
    theta = (mod(texcoord, INV_TILE_COUNT) * TILE_COUNT); //*2.0 - 1.0;
    uvec4 map_sample = texture(map_texture, texcoord);
    uint uphi = map_sample.x % 16u;
    uint vphi = 15u - (map_sample.x / 16u);
    vec2 phi = vec2(uphi, vphi);
    vec2 atlas_point = phi / 16.0 + theta / 16.0;

    fragcolor = textureGrad(texture_atlas, atlas_point, vec2(1/512.0,0/zoom), vec2(0,1/512.0/zoom));
}
'''

class Resources(object):
    pass

def make_resources():
    minecraft_map = pygame.image.load('numbered_texture_atlas.png')
    atlas = pygame.image.load('numbered_texture_atlas.png')
    vertex_buffer_data = float_array(
        -1.0, -1.0, 0.0, 1.0,
         1.0, -1.0, 0.0, 1.0,
        -1.0,  1.0, 0.0, 1.0,
         1.0,  1.0, 0.0, 1.0)
    element_buffer_data = short_array(
        0,1,2,3)
    resources = Resources()
    resources.vertex_buffer = make_buffer(
        GL_ARRAY_BUFFER,
        vertex_buffer_data,
        vertex_buffer_data.nbytes)
    resources.element_buffer = make_buffer(
        GL_ELEMENT_ARRAY_BUFFER,
        element_buffer_data,
        element_buffer_data.nbytes)
    resources.map_texture = make_texture(
        image=minecraft_map, interpolate=False, alpha=True, integer=True)
    resources.texture_atlas = make_texture(
        image=atlas, interpolate=True, alpha=True, maxlod=4.0)
    resources.program = assemble_shader_program(
        vertex_shader,
        fragment_shader,
        uniform_names=[
            'screen_dimensions',
            'cam_position',
            'zoom',
            'texture_dimension',
            'texture_atlas',
            'map_texture'],
        attribute_names=[
            'position'])
    return resources

def render(resources, position, zoom, screen_dimensions):
    screen_w, screen_h = screen_dimensions
    glViewport(0,0,screen_w,screen_h)
    glClearColor(0.4, 0.4, 0.4, 1.0)
    glClear(GL_COLOR_BUFFER_BIT)

    glUseProgram(resources.program.program)
    uniforms = resources.program.uniforms
    glUniform2f(uniforms['screen_dimensions'], screen_w, screen_h)
    glUniform2f(uniforms['cam_position'], position[0], position[1])
    glUniform1f(uniforms['zoom'], zoom)
    glUniform1f(uniforms['texture_dimension'], 8192) 

    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, resources.map_texture)
    glUniform1i(resources.program.uniforms['map_texture'], 0)

    glActiveTexture(GL_TEXTURE1)
    glBindTexture(GL_TEXTURE_2D, resources.texture_atlas)
    glUniform1i(resources.program.uniforms['texture_atlas'], 1)

    glBindBuffer(GL_ARRAY_BUFFER, resources.vertex_buffer)
    glVertexAttribPointer(
        resources.program.attributes['position'],
        4, # size
        GL_FLOAT, # type
        GL_FALSE, # normalized?
        ctypes.sizeof(GLfloat)*4, # stride
        None # offset
        )
    position_attribute = resources.program.attributes['position']
    glEnableVertexAttribArray(position_attribute)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, resources.element_buffer)
    glDrawElements(
        GL_TRIANGLE_STRIP,
        4,
        GL_UNSIGNED_SHORT,
        None)
    glDisableVertexAttribArray(position_attribute)
    pygame.display.flip()

def main(): 
    video_flags = OPENGL|DOUBLEBUF
    pygame.init()
    screen_dimensions = 800, 600
    surface = pygame.display.set_mode(
        screen_dimensions, video_flags)
    resources = make_resources()
    frames = 0
    done = 0
    zoom = 1.0
    position = [256, 8192 - 256]
    dragging = False
    draglast = 0,0

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
                    if zoom > 16:
                        zoom = 16.0
                if event.button == 5:
                    zoom /= 2.0
                    if zoom < 1.0/32.0:
                        zoom = 1.0/32.0
                    x,y = position
                    x = math.floor(x * zoom + 0.5) / zoom
                    y = math.floor(y * zoom + 0.5) / zoom
                    position = [x,y]
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False
        render(resources, position, zoom, screen_dimensions)
        frames += 1

if __name__ == '__main__':
    main()


