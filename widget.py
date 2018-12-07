import pygame
from settings import *

def get_surf(font, text, color = WHITE):
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    return surf, rect

class TextPanel:
    def __init__(self, font, texts, color = WHITE, back_color = BLACK):
        self.font = font
        self.texts = texts
        self.surfs = []
        self.rects = []
        self.text_num = len(texts)
        for text in texts:
            surf, rect = get_surf(font, text, color)
            self.surfs.append(surf)
            self.rects.append(rect)
        self.boarder = 5
        self.text_height = self.rects[0].height
        self.spacing_rate = 0.5
        self.spacing = self.text_height * self.spacing_rate
        self.width = np.max([rect.width for rect in self.rects]) + 2 * self.boarder
        self.height = (self.text_height + self.spacing) * self.text_num - self.spacing + 2 * self.boarder
        self.size = [self.width, self.height]
        self.center = [self.width / 2, self.height / 2]
        self.topleft = []
        self.set_center(self.center)
        self.color = color
        self.back_color = back_color

    def set_center(self, pos):
        self.center = pos
        self.topleft = [pos[0] - self.width / 2, 
                        pos[1] - self.height / 2]
        for idx, rect in enumerate(self.rects):
            y = self.topleft[1] + self.boarder + self.text_height / 2 + (self.text_height + self.spacing) * idx
            rect.center = [pos[0], y]

    def Collide(self, pos):
        return (pos[0] >= self.topleft[0] and
                pos[0] <= self.topleft[0] + self.width and
                pos[1] >= self.topleft[1] and
                pos[1] <= self.topleft[1] + self.height)

    def ProcessInput(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                return self.Collide(pos)
        return None

    def Update(self):
        pass

    def Render(self, screen):
        pygame.draw.rect(screen, self.back_color, self.topleft + self.size)
        for surf, rect in zip(self.surfs, self.rects):
            screen.blit(surf, rect)

class Button:
    def __init__(self, font, text, color = WHITE, back_color = BLACK):
        self.font = font
        self.text_surf, self.text_rect = get_surf(font, text, color)
        self.boarder = 5
        self.center = self.text_rect.center
        self.topleft = [self.text_rect.topleft[0] - self.boarder,
                        self.text_rect.topleft[1] - self.boarder]
        self.width = self.text_rect.width + 2 * self.boarder
        self.height = self.text_rect.height + 2 * self.boarder
        self.size = [self.width, self.height]
        self.rect = self.topleft + self.size
        self.move_on = False
        self.color = color
        self.back_color = back_color

    def set_center(self, pos):
        self.text_rect.center = pos
        self.topleft = [self.text_rect.topleft[0] - self.boarder,
                        self.text_rect.topleft[1] - self.boarder]
        self.rect = self.topleft + self.size

    def Collide(self, pos):
        return (pos[0] >= self.topleft[0] and
                pos[0] <= self.topleft[0] + self.width and
                pos[1] >= self.topleft[1] and
                pos[1] <= self.topleft[1] + self.height)

    def ProcessInput(self, events, pressed_keys):
        pos = pygame.mouse.get_pos()
        if self.Collide(pos):
            self.move_on = True
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    print('Button is clicked')
                    return True
        else:
            self.move_on = False
        return False

    def Update(self):
        pass

    def Render(self, screen):
        if self.move_on:
            pygame.draw.rect(screen, self.color, self.rect)
            pygame.draw.rect(screen, self.back_color, self.text_rect) 
        else:
            pygame.draw.rect(screen, self.back_color, self.rect) 
        screen.blit(self.text_surf, self.text_rect)

class YesNoPanel:
    def __init__(self, font, q_text, y_text, n_text,
                 color = WHITE, back_color = BLACK):
        self.color = color
        self.back_color = back_color
        self.q_surf, self.q_rect = get_surf(font, q_text, color)
        self.y_button = Button(font, y_text, color, back_color)
        self.n_button = Button(font, n_text, color, back_color)
        self.buttons = [self.y_button, self.n_button]
        self.spacing = np.maximum(self.y_button.width, self.n_button.width)
        self.center_y = self.q_rect.center[1] + self.q_rect.height
        self.center_x = self.q_rect.center[0]
        self.center = [self.center_x, self.center_y]
        b_w = np.maximum(self.y_button.width, self.n_button.width)
        self.boarder = 20
        self.width = np.maximum(self.q_rect.width, 3 * b_w) + 2 * self.boarder
        self.height = 3 * self.q_rect.height + 2 * self.boarder
        self.size = [self.width, self.height]
        self.topleft = []
        self.set_center(self.center)

    def set_center(self, center):
        self.center = center
        self.topleft = [self.center[0] - self.width / 2, self.center[1] - self.height / 2]
        self.q_rect.center = [center[0], center[1] - self.q_rect.height]
        b_w = np.maximum(self.y_button.width, self.n_button.width)
        y_x = self.center[0] + (b_w - self.width) / 2 + self.boarder
        n_x = self.center[0] - (b_w - self.width) / 2 - self.boarder
        self.y_button.set_center([y_x, self.center[1] + self.q_rect.height])
        self.n_button.set_center([n_x, self.center[1] + self.q_rect.height])

    def ProcessInput(self, events, pressed_keys):
        for button in self.buttons:
            button.ProcessInput(events, pressed_keys)
        if self.y_button.ProcessInput(events, pressed_keys):
            print('yes')
            return True
        elif self.n_button.ProcessInput(events, pressed_keys):
            print('no')
            return False
        else:
            return None

    def Update(self):
        for button in self.buttons:
            botton.Update()

    def Render(self, screen):
        pygame.draw.rect(screen, self.back_color, self.topleft + self.size)
        screen.blit(self.q_surf, self.q_rect)
        for button in self.buttons:
            button.Render(screen)
        

