import pygame
class Textbox(pygame.sprite.DirtySprite):
    def __init__(self, x, y, w, h, font):
        super().__init__()
        self.rect = pygame.Rect(center=(x, y), width=w, height=h)
        self.image = pygame.Surface((w, h))
        self.font = font
        self.text = ""
        self.active = False
        
        self._layer = 10 
        self.redraw()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            was_active = self.active
            self.active = self.rect.collidepoint(event.pos)
            if self.active != was_active:
                self.redraw()

        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                print("Submitted:", self.text)
            else:
                self.text += event.unicode
            self.redraw()

    def redraw(self):
        bg_color = (255, 255, 255)
        border_color = (0, 120, 215) if self.active else (100, 100, 100)
        self.image.fill(bg_color)
        pygame.draw.rect(self.image, border_color, self.image.get_rect(), 2)

        text_surf = self.font.render(self.text, True, (0, 0, 0))
        self.image.blit(text_surf, (8, (self.rect.height - text_surf.get_height()) // 2))

        self.dirty = 1