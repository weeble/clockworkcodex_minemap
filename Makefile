all: zoompan.py.html opengl2.py.html opengl1.py.html make_numbered_texture_atlas.py.html opengl_tools.py.html minecraft_mapping.py.html

clean:
	rm -f zoompan.py.html
	rm -f opengl2.py.html
	rm -f opengl1.py.html
	rm -f make_numbered_texture_atlas.py.html
	rm -f opengl_tools.py.html
	rm -f minecraft_mapping.py.html

zoompan.py.html:
	pygmentize -P cssclass=syntax -o zoompan.py.html zoompan.py

opengl2.py.html:
	pygmentize -P cssclass=syntax -o opengl2.py.html opengl2.py

opengl1.py.html:
	pygmentize -P cssclass=syntax -o opengl1.py.html opengl1.py

make_numbered_texture_atlas.py.html:
	pygmentize -P cssclass=syntax -o make_numbered_texture_atlas.py.html make_numbered_texture_atlas.py

opengl_tools.py.html:
	pygmentize -P cssclass=syntax -o opengl_tools.py.html opengl_tools.py

minecraft_mapping.py.html:
	pygmentize -P cssclass=syntax -o minecraft_mapping.py.html minecraft_mapping.py
