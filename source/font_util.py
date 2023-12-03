def render_w_outline(screen, text, font, font_color, outline_color, pos, thickness):
    text_r = font.render(text, False, font_color, None)
    outline_text_r = font.render(text, False, outline_color, None)
    x = pos[0]
    y = pos[1]

    for dx in range(-thickness, thickness + 1):
        for dy in range(-thickness, thickness + 1):
            screen.blit(outline_text_r, (x + dx, y + dy))
    screen.blit(text_r, pos)
