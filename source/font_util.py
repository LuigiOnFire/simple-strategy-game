import pygame as p

def render_w_outline(screen, text, font, font_color, outline_color, pos, thickness):
    text_r = font.render(text, False, font_color, None)
    outline_text_r = font.render(text, False, outline_color, None)
    x = pos[0]
    y = pos[1]

    for dx in range(-thickness, thickness + 1):
        for dy in range(-thickness, thickness + 1):
            screen.blit(outline_text_r, (x + dx, y + dy))
    screen.blit(text_r, pos)


def surface_render_w_outline(text, font, font_color, outline_color, thickness, alpha):
    text_r = font.render(text, False, font_color, None)
    (w, h) = font.size(text)
    w += thickness
    h += thickness

    surface = p.Surface((w, h), p.SRCALPHA)

    outline_text_r = font.render(text, False, outline_color, None)

    x = thickness
    y = thickness

    for dx in range(-thickness, thickness + 1):
        for dy in range(-thickness, thickness + 1):
            surface.blit(outline_text_r, (x + dx, y + dy))

    pos = (x, y)

    surface.set_alpha(alpha)

    surface.blit(text_r, pos)
    return surface
