import pygame

def make_numbered_texture_atlas():
    surface = pygame.Surface((512,512))
    font = pygame.font.SysFont("arial",14,bold=True)
    for i in xrange(256):
        y = i // 16
        x = i % 16
        fg = (255,255,255) if i<=127 else (0,0,0)
        bg = (i,i,i)
        textimage = font.render(str(i), True, fg)
        w,h = textimage.get_size()
        surface.fill(bg, (32*x, 32*y, 32, 32))
        surface.blit(textimage, (32*x+16-w//2, 32*y+16-h//2))
    return surface

def main():
    pygame.init()
    pygame.image.save(
        make_numbered_texture_atlas(),
        "numbered_texture_atlas.png")

if __name__ == "__main__":
    main()
