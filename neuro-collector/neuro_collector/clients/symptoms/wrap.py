import pygame


def truncline(text, font, maxwidth):
    real = len(text)
    stext = text
    l = font.size(text)[0]
    cut = 0
    a = 0
    done = 1
    old = None
    while l > maxwidth:
        a = a + 1
        n = text.rsplit(None, a)[0]
        if stext == n:
            cut += 1
            stext = n[:-cut]
        else:
            stext = n
        l = font.size(stext)[0]
        real = len(stext)
        done = 0
    return real, done, stext


def wrapline(text, font, maxwidth):
    done = 0
    wrapped = []

    while not done:
        nl, done, stext = truncline(text, font, maxwidth)
        wrapped.append(stext.strip())
        text = text[nl:]
    return wrapped


def render_wrap(text, font, maxwidth):
    lines = wrapline(text, font, maxwidth)

    total_height = 0
    largest_width = 0

    surfaces = []
    for line in lines:
        surface = font.render(line, True, (0, 0, 0))
        total_height += surface.get_height()

        width = surface.get_width()
        if width > largest_width:
            largest_width = width

        surfaces.append(surface)

    wrap_surface = pygame.Surface((largest_width, total_height))
    wrap_surface.fill((255, 255, 255))

    y = 0
    for surface in surfaces:
        wrap_surface.blit(surface, (0, y))
        y += surface.get_height()

    return wrap_surface
