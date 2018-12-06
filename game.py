# -*- coding: utf-8 -*-
import pygame
import os
import random
import numpy as np


#init pygame
pygame.init()
pygame.font.init()

#background settings
BOARDER = 10
CARD_SPACING = 5
FIG_WIDTH = 372 // 3
FIG_HEIGHT = 587 // 3
FIG_SIZE = [FIG_WIDTH, FIG_HEIGHT]
CARD_BOARDER = 5
CARD_WIDTH = 2 * CARD_BOARDER + FIG_WIDTH
CARD_HEIGHT = 2 * CARD_BOARDER + FIG_HEIGHT
CARD_SIZE = [CARD_WIDTH, CARD_HEIGHT]
DECK_WIDTH = 600
MIDDLE_SPACING = 20
WINDOW_WIDTH = BOARDER * 2 + (CARD_SPACING + CARD_WIDTH) * 8 - CARD_SPACING + DECK_WIDTH
WINDOW_HEIGHT = 4 * CARD_HEIGHT + 4 * MIDDLE_SPACING
#Cautious: Really Dirty! Calculate the ratio and resize.
(USER_WINDOW_WIDTH,USER_WINDOW_HEIGHT) = pygame.display.list_modes()[0]
if USER_WINDOW_WIDTH < WINDOW_WIDTH and USER_WINDOW_HEIGHT < WINDOW_HEIGHT:
    ratio_width = USER_WINDOW_WIDTH/WINDOW_WIDTH
    ratio_height = USER_WINDOW_HEIGHT/WINDOW_HEIGHT
    ratio = ratio_width if ratio_width < ratio_height else ratio_height
    print('Exceed available width or height! Resizing with ratio {}...'.format(ratio))
    BOARDER = int(10*ratio)
    CARD_SPACING = int(5*ratio)
    FIG_WIDTH = int((372 // 3)*ratio)
    FIG_HEIGHT = int((587 // 3)*ratio)
    FIG_SIZE = [FIG_WIDTH, FIG_HEIGHT]
    CARD_BOARDER = int(5*ratio)
    CARD_WIDTH = 2 * CARD_BOARDER + FIG_WIDTH
    CARD_HEIGHT = 2 * CARD_BOARDER + FIG_HEIGHT
    CARD_SIZE = [CARD_WIDTH, CARD_HEIGHT]
    DECK_WIDTH = int(600*ratio)
    MIDDLE_SPACING = int(20*ratio)
    WINDOW_WIDTH = BOARDER * 2 + (CARD_SPACING + CARD_WIDTH) * 8 - CARD_SPACING + DECK_WIDTH
    WINDOW_HEIGHT = 4 * CARD_HEIGHT + 4 * MIDDLE_SPACING
WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)
WINDOW_CENTER = [WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2]
WINDOW_RECT = pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
UP_CARD_POS = [[BOARDER + i * (CARD_SPACING + CARD_WIDTH), BOARDER] for i in range(0, 8)]
DOWN_CARD_POS = [[p[0], WINDOW_HEIGHT - BOARDER - CARD_HEIGHT] for p in UP_CARD_POS]
POOL_WIDTH = 8
MIDDLE_BUFFER = MIDDLE_SPACING + CARD_HEIGHT
MIDDLE_CARD_X = [BOARDER + (i + 1) * (MIDDLE_SPACING + CARD_WIDTH) for i in range(0, POOL_WIDTH)]
MIDDLE_CARD_POS = [[x, BOARDER + i * MIDDLE_BUFFER] for x in MIDDLE_CARD_X for i in range(1, 3)]
CARD_POS = UP_CARD_POS + DOWN_CARD_POS + MIDDLE_CARD_POS[:8]
DECK_SIZE = 8
POOL_SIZE = 8
COVER_BOARDER = 10


#colors
WHITE = [255, 255, 255]
YELLOW = [255, 255, 0]
BLACK = [0, 0, 0]
GRAY = [128, 128, 128]
BLUE = [0, 128, 255]

CARD_CONTENTS = [[i, j] for i in range(1, 13) for j in range(1, 5)]
card_contents = CARD_CONTENTS

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
done = False
flag = True

# MOVE_TIME = 0.5
MOVE_FRAME = 30

#card properties
prop_dic = {'ko':0, 'subko':1, 'tane':2, 'tane_ani':3, 'tan':4, 'tan_r':5, 'tan_b':6, 'kas':7}
PROP_DIC_LEN = 8
def property_array(idx_list, num = PROP_DIC_LEN):
    v = np.zeros(num, dtype = int)
    for idx in idx_list:
        v[idx] = v[idx] + 1
    return v

KOU = property_array([prop_dic['ko']])
SUBKOU = property_array([prop_dic['subko']])
TAN = property_array([prop_dic['tan']])
TAN_R = property_array([prop_dic['tan'], prop_dic['tan_r']])
TAN_B = property_array([prop_dic['tan'], prop_dic['tan_b']])
TANE = property_array([prop_dic['tane']])
TANE_ANI = property_array([prop_dic['tane'], prop_dic['tane_ani']])
kasu = property_array([prop_dic['kas']])
KYOKU = property_array([prop_dic['kas'], prop_dic['tane']])
CARD_INFO= [[KOU, TAN_R, kasu, kasu],
            [TANE, TAN_R, kasu, kasu],
            [KOU, TAN_R, kasu, kasu],
            [TANE, TAN, kasu, kasu],
            [TANE, TAN, kasu, kasu],
            [TANE_ANI, TAN_B, kasu, kasu],
            [TANE_ANI, TAN, kasu, kasu],
            [KOU, TANE, kasu, kasu],
            [KYOKU, TAN_B, kasu, kasu],
            [TANE_ANI, TAN_B, kasu, kasu],
            [SUBKOU, TANE, TAN, kasu],
            [KOU, kasu, kasu, kasu]]

def get_card_type(card):
    props = CARD_INFO[card.month - 1][card.order - 1]
    name_order = ['ko', 'tane', 'tan', 'kas']
    for name in name_order:
        if props[prop_dic[name]] == 1:
            return name
        elif props[prop_dic['subko']] == 1:
            return 'ko'
    print('Error: card %d %d has no type!' % (card.month, card.order))
    return None

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
        

#scoring rules
class Rules:
    def __init__(self, month, oya, deck):
        self.parent = deck
        self.patterns = [['猪鹿蝶', 5, property_array([prop_dic['tane_ani']] * 3)],
                         ['赤短', 6, property_array([prop_dic['tan_r']] * 3)],
                         ['青短', 6, property_array([prop_dic['tan_b']] * 3)]]
        self.kous = [['五光', 15, property_array([prop_dic['ko']] * 4 + [prop_dic['subko']])],
                     ['雨四光', 8, property_array([prop_dic['ko']] * 3 + [prop_dic['subko']])],
                     ['四光', 10, property_array([prop_dic['ko']] * 4)],
                     ['三光', 6, property_array([prop_dic['ko']] * 3)]]  
        self.kasu_lim = 10
        self.tane_lim = 5
        self.tan_lim = 5
        self.month = month
        self.oya = oya
        print('in Rules, month is %d' % month)
        # self.record_names = [pattern[0] for pattern in self.patterns] + ['ko', 'kas', 'tane', 'tan']
        self.records = {}
        self.new_patterns = []
        self.window_size = [6 * CARD_WIDTH, 1.5 * CARD_HEIGHT]
        self.window_pos_x = (WINDOW_WIDTH - self.window_size[0]) / 2
        self.window_pos_y = (WINDOW_HEIGHT - self.window_size[1]) / 2
        self.window_pos = [self.window_pos_x, self.window_pos_y] 
        self.font = pygame.font.Font("KosugiMaru-Regular.ttf", 40)
        self.state_dic = {'idle':0, 'pump':1, 'koikoi':2, 'score':3, 'end':4}
        self.state = self.state_dic['idle'] 
        self.text = ''
        self.pump_idx = 0
        self.color = WHITE
        self.back_color = BLACK
        self.boarder = 10
        self.koikoi_panel = YesNoPanel(self.font, 'こいこいしますか？',
                                       'はい', 'いいえ', self.color,
                                       self.back_color)
        self.koikoi_panel.set_center([WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2])
        self.score_panel = None
        self.total_point = 0
        self.card_num = DECK_SIZE
        self.is_human = self.parent.IsHuman()
        self.agent = self.parent.agent

    def IsNotIdle(self):
        return self.state != self.state_dic['idle']

    def Check(self, pattern, name):
        record = self.records.get(name)
        if record == None:
            self.records[name] = pattern
            return True
        else:
            val = record[1]
            if pattern[1] > val:
                self.records[name] = pattern
                return True
        return False

    def ToScoreState(self):
        self.UpdateScorePanel()
        self.state = self.state_dic['score']
    
    def Oyaken(self):
        text = '親権'
        val = 6
        pattern = [text, val, None]
        self.new_patterns = [pattern]
        self.records[text] = pattern
        if self.state == self.state_dic['idle']:
            print('change to state score!')
            self.ToScoreState()

    def CheckPatterns(self, in_arr, cards_prop):
        new_pattern = False
        new_patterns = []
        name_list = [pattern[0] for pattern in self.patterns]
        name_list = name_list + ['ko'] * len(self.kous)
        for name, pattern in zip(name_list, self.patterns + self.kous):
            if (in_arr >= pattern[2]).all():
                if self.Check(pattern[:-1], name):
                    print(name + 'is checked')
                    new_pattern = True
                    cards = []
                    for idx, i in enumerate(pattern[2]):
                        cards = cards + cards_prop[idx][:i]
                    new_patterns.append(pattern[:-1] + [cards])
        name_lists = [['kas', 'カス'], ['tane', 'タネ'], ['tan', '短冊']]
        lims = [self.kasu_lim, self.tane_lim, self.tan_lim]
        for name_list, lim in zip(name_lists, lims):
            idx_name = name_list[0]
            idx = prop_dic[idx_name]
            name = name_list[1]
            num = in_arr[idx]
            if num >= lim:
                diff = num - lim + 1
                pattern = [name, diff]
                if self.Check(pattern, name):
                    new_pattern = True
                    cards = cards_prop[idx]
                    new_patterns.append(pattern + [cards])
        name = '月札'
        val = 4
        count = 0
        recorded_order = []
        dis_cards = []
        for cards in cards_prop:
            for card in cards:
                if card.month == self.month:
                    if card.order not in recorded_order:
                        recorded_order.append(card.order)
                        count = count + 1
                        dis_cards.append(card)
        print('month card count : ' + str(count))
        if count == 4:
            pattern = [name, val]
            if self.Check(pattern, name):
                new_pattern = True
                cards = cards_prop[idx]
                new_patterns.append(pattern + [dis_cards])
        if new_pattern:
            self.new_patterns = new_patterns
            if self.new_patterns != [] and self.state == self.state_dic['idle']:
                print('change to state pump!')
                if self.card_num == 0:
                    self.ToScoreState()
                else:
                    self.state = self.state_dic['pump']
                self.pump_idx = 0
        return new_pattern

    def Collide(self, pos):
        return (pos[0] >= self.window_pos[0] and 
                pos[0] <= self.window_pos[0] + self.window_size[0] and
                pos[1] >= self.window_pos[1] and 
                pos[1] <= self.window_pos[1] + self.window_size[1])

    def ProcessInput(self, events, pressed_keys):
        if self.state == self.state_dic['koikoi']:
            if self.is_human:
                Res = self.koikoi_panel.ProcessInput(events, pressed_keys)
            else:
                print('Action with koikoi=True')
                Res = self.agent.Action(koikoi=True)
                print('Res: ' + str(Res))
            if Res == True:
                self.state = self.state_dic['idle']
            elif Res == False:
                self.state = self.state_dic['score']
                self.UpdateScorePanel()
                print('score panel is updated')
        elif self.state == self.state_dic['score']:
            # print('now in state score')
            Res = self.score_panel.ProcessInput(events, pressed_keys)
            if Res == True:
                self.state = self.state_dic['end']
                return True
        else:
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if self.state == self.state_dic['pump'] and self.Collide(pos):
                        print('window is clicked')
                        print('and the state is now pump')
                        self.pump_idx = self.pump_idx + 1
                        print('pump idx : ' + str(self.pump_idx))
                        print('new_patterns : ' + str(self.new_patterns))
                        if self.pump_idx == len(self.new_patterns):
                            self.state = self.state_dic['koikoi']
                            print('the state is now koikoi')
                            # self.state = self.state_dic['idle']
        return False

    def UpdateScorePanel(self):
        texts = []
        text_num = 8
        total_point = 0
        tlen = 6
        for idx_name in self.records:
            record = self.records.get(idx_name)
            if record != None:
                name = record[0]
                val = record[1]
                spacing = ''.join('　' for i in range(0, tlen - len(name)))
                point = str(val) + '文'
                texts.append(name + spacing + point)
                total_point = total_point + val
        print(record)
        print('now is in state %d' % self.state)
        print('number of scored patterns are %d' % len(texts))
        texts = texts + ['' for i in range(0, 8 - len(texts))]
        point_str = str(total_point)
        self.total_point = total_point
        texts.append('合計' + 
                     ''.join('　' for i in range(0, tlen - len(point_str))) + 
                     point_str + '文')
        self.score_panel = TextPanel(self.font, texts, self.color, self.back_color)
        self.score_panel.set_center(WINDOW_CENTER)

    def Update(self, card_num):
        self.card_num = card_num
    # if self.new_patterns != [] and self.state == self.state_dic['idle']:
    # print('change to state pump!')
    # self.state = self.state_dic['pump']
    # self.pump_idx = 0

    def PumpRender(self, screen):
        pygame.draw.rect(screen, BLACK, self.window_pos + self.window_size)
        pattern = self.new_patterns[self.pump_idx]
        texts = [pattern[0], str(pattern[1]) + '文']
        text_panel = TextPanel(self.font, texts, self.color, self.back_color)
        text_panel_x = self.window_pos_x + self.boarder + text_panel.width / 2
        text_panel_y = self.window_pos_y + self.window_size[1] / 2
        text_panel.set_center([text_panel_x, text_panel_y])
        text_panel.Render(screen)
        center_y = self.window_pos_y + self.window_size[1] / 2
        left = text_panel_x + text_panel.width / 2 + self.boarder + CARD_WIDTH / 2 + CARD_BOARDER
        right = self.window_pos_x + self.window_size[0] - self.boarder - CARD_WIDTH / 2 - CARD_BOARDER
        if pattern[2] != None: #Is Oyaken
            center_x = np.linspace(left, right, len(pattern[2])) 
            for x, card in zip(center_x, pattern[2]):
                card.Draw(screen, [x, center_y], location = 'center')
        # text_center_x = int(self.window_pos_x + BOARDER + text_rect.width / 2)
        # text_center_y = int(self.window_pos_y + self.window_size[1] / 2)
        # text_rect.center = [text_center_x, text_center_y]
        # screen.blit(text_surface, text_rect)


    def Render(self, screen):
        if self.state == self.state_dic['pump']:
            self.PumpRender(screen)
        elif self.state == self.state_dic['koikoi']:
            self.koikoi_panel.Render(screen)
        elif self.state == self.state_dic['score']:
            self.score_panel.Render(screen)

_image_library = {}
def get_image(path):
    global _image_library
    image = _image_library.get(path)
    if image == None:
        canonicalized_path = path.replace('/', os.sep).replace('\\', os.sep)
        image = pygame.image.load(canonicalized_path)
        image = pygame.transform.scale(image, FIG_SIZE)
        _image_library[path] = image
    return image

class Card:
    def __init__(self, content, pos):
        self.month = content[0]
        self.order = content[1]
        self.image = get_image('images/' + str(content[0]) + '_' + str(content[1]) + '.png')
        self.pos = pos
        self.fig_pos = self.get_fig_pos(pos)
        self.move = False
        self.frame = 0
        self.move_path = None
        self.selected = False
        self.scored_by_player = None
        self.to_scored_area = False
        self.in_pool_idx = None
        self.parent = None
        self.card_width = CARD_WIDTH + 2 * CARD_BOARDER
        self.card_height = CARD_HEIGHT + 2 * CARD_BOARDER

    def toggle_selected(self):
        self.selected = not self.selected

    def scored(self, player):
        self.scored_by_player = player

    def get_fig_pos(self, pos):
        return [pos[0] + CARD_BOARDER, pos[1] + CARD_BOARDER]

    def Collide(self, pos):
        return (pos[0] >= self.pos[0] 
                and pos[0] <= self.pos[0] + CARD_WIDTH
                and pos[1] >= self.pos[1]
                and pos[1] <= self.pos[1] + CARD_HEIGHT)

    def ProcessInput(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if self.Collide(pos):
                    print('card %d %d is clicked' % (self.month, self.order))
                    print('card type is ' + get_card_type(self))
                    return self
        return None

    def Update(self, dest_pos, scored_player = None):
        if not self.move and dest_pos != None:
            self.move = True
            move_x = np.linspace(self.pos[0], dest_pos[0], MOVE_FRAME)
            move_y = np.linspace(self.pos[1], dest_pos[1], MOVE_FRAME)
            self.move_path = [[int(x), int(y)] for x, y in zip(move_x, move_y)]
            self.frame = 0
        elif self.move:
            if self.frame == MOVE_FRAME:
                self.move = 0
                self.frame = 0
            else:
                self.pos = self.move_path[self.frame]
                self.fig_pos = self.get_fig_pos(self.pos)
                self.frame = self.frame + 1

    def Draw(self, screen, pos, location = 'topleft'):
        if location == 'center':
            pos = [pos[0] - self.card_width / 2,
                   pos[1] - self.card_height / 2]
        wrap_rect = pos + CARD_SIZE
        fig_pos = self.get_fig_pos(pos)
        fig_rect = fig_pos + FIG_SIZE
        if self.selected:
            pygame.draw.rect(screen, YELLOW, wrap_rect)
        else:
            pygame.draw.rect(screen, BLACK, wrap_rect)
        pygame.draw.rect(screen, WHITE, fig_rect)
        screen.blit(self.image, fig_pos)

    def Render(self, screen):
        self.Draw(screen, self.pos)

class SimpleAgent:
    def __init__(self, deck):
        print('simple agent is initialized')
        self.deck = deck
        self.cards = deck.cards
        self.pool = deck.pool
        self.opp_score = deck.opponent_scored
        self.state_dic = {'idle':0, 'actioned':1, 'match':2, 'koikoi':3}
        self.state = self.state_dic['idle']

    def Action(self, cards = None, koikoi = False):
        if koikoi:
            return self.KoiKoiAction()
        elif cards == None:
            return self.HandAction()
        else:
            return self.PoolAction(cards)
    
    def KoiKoiAction(self):
        return False

    def HandAction(self):
        return self.cards[0] 

    def PoolAction(self, cards):
        return cards[0]

class HumanAgent:
    def __init__(self, deck):
        self.deck = deck

class Deck:
    def __init__(self, card_list, y, month, oya, player, agent_type = 'Human'):
        self.oya = oya
        self.player = player
        self.cards = card_list
        for card in self.cards:
            card.parent = self.cards
        self.score_dic = {'ko':0, 'tane':1, 'tan':2, 'kas':3}
        self.scored_cards = [[] for i in range(0, len(self.score_dic))]
        self.scored_cards_render = []
        self.prop_arr = np.zeros(PROP_DIC_LEN, dtype=int)
        self.scored_cards_prop = [[] for i in range(0, PROP_DIC_LEN)]
        self.pool = None
        self.opponent_scored = None
        self.move = False
        self.deck_y = y
        self.right_corner = [WINDOW_WIDTH - BOARDER - CARD_WIDTH, y]
        self.left_corner = [BOARDER, y]
        self.overlap_ratio = 1 / 3
        self.overlap = int(self.overlap_ratio * CARD_WIDTH)
        self.type_spacing = 10
        self.agent_type = agent_type
        self.agent = self.SetAgent(agent_type)
        self.rules = Rules(month, oya, self)

    def IsHuman(self):
        return self.agent_type == 'Human'
    
    def SetAgent(self, agent_type):
        if self.IsHuman():
            return HumanAgent(self)
        else:
            return SimpleAgent(self)

    def ProcessInput(self, events, pressed_keys):
        if self.rules.IsNotIdle() and self.rules.state != self.rules.state_dic['end']:
            return self.rules.ProcessInput(events, pressed_keys)
        else:
            if self.IsHuman():
                for card in self.cards:
                    selected_card = card.ProcessInput(events, pressed_keys)
                    if selected_card != None:
                        print('deck get selected card!')
                        return selected_card
            else:
                selected_card = self.agent.Action()
                return selected_card
        return None

    def CheckPatterns(self):
        return self.rules.CheckPatterns(self.prop_arr, self.scored_cards_prop)

    def ScoreCard(self, card):
        print(get_card_type(card) + ' card %d %d is scored' % (card.month, card.order))
        type_name = get_card_type(card)
        type_idx = self.score_dic[type_name]
        card.parent = self
        info = CARD_INFO[card.month-1][card.order-1] 
        print('scored card info: ' + str(info))
        self.prop_arr = self.prop_arr + info
        print('prop_arr: ' + str(self.prop_arr))
        for idx, i in enumerate(info):
            if i == 1:
                self.scored_cards_prop[idx].append(card)
        print('type_idx in scored_cards is ' + str(type_idx))
        self.scored_cards[type_idx].append(card)
        self.scored_cards_render.append(card)

    def ScoredCardUpdate(self):
        [x, y] = self.right_corner
        for typed_cards in self.scored_cards:
            num = len(typed_cards)
            if num != 0:
                x = x - (num - 1) * self.overlap
                for idx, card in enumerate(typed_cards):
                    card.Update([x + idx * self.overlap, y])
                x = x - self.type_spacing - CARD_WIDTH

    def HandUpdate(self):
        [x, y] = self.left_corner
        for card in self.cards:
            card.Update([x, y])
            x = x + CARD_WIDTH + CARD_SPACING

    def Update(self, pool, opponent_scored):
        self.pool = pool
        self.opponent_scored = opponent_scored       
        for card in self.cards:
            card.Update(None)
        # if cards in pool is selected
        move = False
        for cards in self.scored_cards:
            for card in cards:
                card.Update(None)
                card.selected = False
                move = move or card.move
        if not move:
            self.ScoredCardUpdate()
        self.rules.Update(len(self.cards))

    def Render(self, screen):
        for card in self.cards:
            card.Render(screen)
        for card in self.scored_cards_render:
            card.Render(screen)
        self.rules.Render(screen)

class MonthPanel:
    def __init__(self, month, oya, scores, cards, center, color = WHITE,
                 back_color = BLACK):
        self.font = pygame.font.Font("KosugiMaru-Regular.ttf", 40)
        self.card = None
        for card in cards:
            if card.month == month and card.order == 4:
                self.card = card
        if self.card == None:
            print('Err: No month card representation exits')
        self.oya = oya
        self.center = center
        self.color = color
        self.back_color = back_color
        self.text = '月札'
        self.texts = [self.text]
        for idx, score in enumerate(scores):
            text = ''
            if idx == self.oya:
                text = '親'
            else:
                text = '子'
            self.texts.append(text + '　' + str(score) + '文')    
        self.surfs = []
        self.rects = []
        self.text_height = 0
        for text in self.texts:
            surf, rect = get_surf(self.font, text, color)
            self.surfs.append(surf)
            self.rects.append(rect)
            self.text_height = rect.height
        self.boarder = 10
        self.height = 2 * self.boarder + 5 * self.text_height + self.card.card_height
        self.width = 1.5 * self.card.card_width + 2 * self.boarder
        self.size = [self.width, self.height]
    
    def Render(self, screen):
        rect = pygame.Rect([0, 0] + self.size)
        rect.center = self.center
        pygame.draw.rect(screen, self.back_color, rect)
        y = self.center[1] - self.height / 2 + self.text_height + self.boarder 
        self.rects[1].center = [self.center[0], y]
        y = y + self.text_height + self.card.card_height / 2
        self.card.Draw(screen, [self.center[0], y], location = 'center')
        y = y + self.card.card_height / 2 + self.text_height / 2
        self.rects[0].center = [self.center[0], y]
        self.rects[2].center = [self.center[0], y + 1.5 * self.text_height] 
        for surf, rect in zip(self.surfs, self.rects):
            screen.blit(surf, rect)

class Round:
    def __init__(self, month, oya, scores, agent_types):
        random.shuffle(card_contents)
        self.next = self
        self.month = month
        self.oya = oya
        self.scores = scores
        cards = []
        self.player = self.oya
        self.last_scored_player = None
        #rest settings
        self.rest_max_size = len(card_contents) - 2 * DECK_SIZE - POOL_SIZE
        self.card_depth = 1
        self.rest_angle = 20
        self.dy = self.card_depth
        self.dx = self.card_depth * np.tan(np.deg2rad(self.rest_angle))
        self.rest_pos = [BOARDER, int((WINDOW_HEIGHT - CARD_HEIGHT) / 2)]
        for idx, content in enumerate(card_contents):
            if idx < len(CARD_POS):
                pos = CARD_POS[idx]
            else:
                x = self.rest_pos[0] + self.dx * (idx - len(CARD_POS) )
                y = self.rest_pos[1] + self.dy * (idx - len(CARD_POS)) 
                pos = [x, y]
            content = card_contents[idx]
            card = Card(content, pos)
            cards.append(card)
        center = [WINDOW_WIDTH - BOARDER - 2 * CARD_WIDTH, WINDOW_HEIGHT / 2]
        self.month_panel = MonthPanel(month, oya, scores, cards, center)
        corner_x = WINDOW_WIDTH - CARD_WIDTH - BOARDER
        self.agent_types = agent_types
        top_deck = Deck(cards[:DECK_SIZE], BOARDER, month, oya, 0, agent_types[0])
        bot_y = WINDOW_HEIGHT - CARD_HEIGHT - BOARDER
        bot_deck = Deck(cards[DECK_SIZE:2 * DECK_SIZE], bot_y, month, oya, 1, agent_types[1])
        self.decks = [top_deck, bot_deck]
        self.agents = [deck.agent for deck in self.decks]
        self.pool = []
        for idx, card in enumerate(cards[2 * DECK_SIZE:2 * DECK_SIZE + POOL_SIZE]):
            card.in_pool_idx = idx
            card.parent = self.pool
            self.pool.append(card)
        self.pool_avail_idx = [1] * POOL_SIZE + [0] * (POOL_WIDTH * 2 - POOL_SIZE) 
        self.temp_pool_avail_idx = self.pool_avail_idx.copy()
        self.rest = cards[2 * DECK_SIZE + POOL_SIZE:]
        for card in self.rest:
            card.parent = self.rest
        self.matched_cards = None
        self.state_dic = {'idle':0, 'match':1, 'second':2, 'match_second':3, 'koikoi':4, 'end':5}
        self.state = self.state_dic['idle']
        self.second_flip_state = False
        self.selected_card = None

    def toggle_player(self):
        self.player = 1 - self.player

    def in_match_state(self):
        return self.state == self.state_dic['match'] \
            or self.state == self.state_dic['match_second']
    
    def IsEnd(self):
        return self.state == self.state_dic['end']

    def GetScore(self):
        if self.state == self.state_dic['end']:
            return self.decks[self.player].rules.total_point
        else:
            print('access score not in end state!')

    def ProcessInput(self, events, pressed_keys):
        filtered_events = []
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                pass
            else:
                filtered_events.append(event)
        if self.in_match_state():
            for card in self.matched_cards:
                if self.decks[self.player].IsHuman():
                    pool_selected_card = card.ProcessInput(filtered_events, pressed_keys)
                    if pool_selected_card != None:
                        print('get selected card in pool')
                        self.matched_cards = [pool_selected_card]
                else:
                    card = self.agents[self.player].Action(self.matched_cards)
                    self.matched_cards = [card]
        elif self.state == self.state_dic['koikoi']:
            deck = self.decks[self.player]
            val = deck.ProcessInput(filtered_events, pressed_keys)
            if val == True:
                print('Go to end state in Round')
                self.state = self.state_dic['end']
        else:
            selected_card = None
            if self.state == self.state_dic['idle']:
                deck = self.decks[self.player]
                selected_card = deck.ProcessInput(filtered_events, pressed_keys)
            elif self.state == self.state_dic['koikoi']:
                deck = self.decks[self.last_scored_player]
                selected_card = deck.ProcessInput(filtered_events, pressed_keys)
            if selected_card != None:
                self.selected_card = selected_card
                month = self.selected_card.month
                self.matched_cards = self.CheckPool(month)

    def CheckPool(self, month):
        matched_cards = []
        for card in self.pool:
            if card.month == month:
                matched_cards.append(card)
        return matched_cards

    def GetPoolAvailIdx(self):
        for idx, val in enumerate(self.pool_avail_idx):
            if val == 0:
                self.pool_avail_idx[idx] = 1
                self.temp_pool_avail_idx[idx] = 1
                print('get pool idx %d' % idx)
                return idx

    def cover_pos_shift(self, pos):
        return [pos[0] - COVER_BOARDER, pos[1] - COVER_BOARDER]

    def move_card_to_pool(self, pos, idx = None):
        if not self.second_flip_state:
            self.second_flip_state = True
        deck = self.decks[self.player]
        origin = self.selected_card.parent
        self.selected_card.Update(pos)
        self.pool.append(self.selected_card)
        self.selected_card.parent = self.pool
        origin.remove(self.selected_card)
        # deck.cards.remove(self.selected_card)
        if idx != None:
            self.selected_card.in_pool_idx = idx
        if len(self.matched_cards) == 1:
            for card in [self.matched_cards[0], self.selected_card]:
                card.scored(self.player)
                deck.ScoreCard(card)
                if card.in_pool_idx != None:
                    self.temp_pool_avail_idx[card.in_pool_idx] = 0
                    card.in_pool_idx = None
                try:
                    self.pool.remove(card)
                except:
                    print('cannot remove card %d %d from pool' % (card.month, card.order))
        # self.toggle_player()
        self.selected_card = None
        deck.HandUpdate()
        self.state_transition_after_move()

    def ToIdleState(self):
        print('to idle state')
        deck = self.decks[self.player]
        if self.state != self.state_dic['koikoi'] and deck.CheckPatterns():
            print('change to state koikoi and now player is %d' % self.player)
            self.last_scored_player = self.player
            self.state = self.state_dic['koikoi']
        else:
            self.state = self.state_dic['idle']
            self.pool_avail_idx = self.temp_pool_avail_idx.copy()
            print('update pol_avail_idx')
            self.toggle_player()

    def state_transition_after_move(self):
        #state transition
        if self.state == self.state_dic['idle']:
            print('to state second')
            self.state = self.state_dic['second']
        elif self.state == self.state_dic['second']:
            self.ToIdleState()
            # self.state = self.state_dic['idle']
            # self.toggle_player()
        elif self.in_match_state():
            for card in self.pool:
                card.selected = False
            if self.state == self.state_dic['match_second']:
                self.ToIdleState()
            else:
                print('to state second')
                self.state = self.state_dic['second']

    def RestUpdate(self):
        if self.state == self.state_dic['second']:
            deck = self.decks[self.player]
            finished = True
            for card in deck.cards:
                if card.move == True:
                    finished = False
                    break
            if finished:
                self.selected_card = self.rest[0]
                self.matched_cards = self.CheckPool(self.selected_card.month)

    def CheckEmptyDecks(self):
        l = 0
        for deck in self.decks:
            l = l + len(deck.cards)
        if l == 0:
            if self.last_scored_player == None:
                print('oyaken!!')
                self.decks[self.oya].rules.Oyaken()
            else:
                print('last scored player would score')
                self.decks[self.last_scored_player].rules.ToScoreState()
            self.state = self.state_dic['koikoi']

    def Update(self):
        if self.state == self.state_dic['koikoi']:
            rules = self.decks[self.player].rules
            if rules.state == rules.state_dic['end']:
                self.state = self.state_dic['end']
            elif rules.state == rules.state_dic['idle']:
                self.ToIdleState()
        if self.selected_card != None:
            num = len(self.matched_cards)
            # if self.state != self.state_dic['match']:
                # print('%d cards are matched in game update' % num)
            if num == 0:
                idx = self.GetPoolAvailIdx()
                self.move_card_to_pool(MIDDLE_CARD_POS[idx], idx)
            elif num == 1:
                matched_card = self.matched_cards[0]
                print('card %d %d is matched' % (matched_card.month, matched_card.order))
                print('card type is ' + get_card_type(matched_card))
                pos = self.cover_pos_shift(matched_card.pos)
                self.move_card_to_pool(pos)
            else:
                if not self.in_match_state():
                    for card in self.matched_cards:
                        card.toggle_selected()
                    if self.state == self.state_dic['idle']:
                        self.state = self.state_dic['match']
                    elif self.state == self.state_dic['second']:
                        self.state = self.state_dic['match_second']
                    print('to match state')
        self.decks[0].Update(self.pool, self.decks[1].scored_cards)
        self.decks[1].Update(self.pool, self.decks[0].scored_cards)
        for card in self.pool:
            card.Update(None)
        self.RestUpdate()
        if self.state == self.state_dic['idle']:
            self.CheckEmptyDecks()

    def RestDrawPolygon(self, pos_list, num):
        dy = self.card_depth
        dx = self.card_depth * np.tan(np.deg2rad(self.rest_angle))
        # print('dx : %f, dy : %f' % (dx, dy))
        xs = dx * num
        ys = dy * num
        # print('xs : %f, ys : %f' % (xs, ys))
        new_pos_list = [[int(x + xs), int(y + ys)] for [x, y] in reversed(pos_list)]
        pos_list = pos_list + new_pos_list
        pygame.draw.polygon(screen, BLACK, pos_list)

    def RestRender(self, screen):
        num = len(self.rest)       
        # print('num of rest : %d' % num)
        dy = self.card_depth
        dx = self.card_depth * np.tan(np.deg2rad(self.rest_angle))
        depth = num * dy
        x = self.rest_pos[0] + dx * (self.rest_max_size - num)
        y = self.rest_pos[1] + dy * (self.rest_max_size - num)
        pygame.draw.rect(screen, GRAY, [x, y] + CARD_SIZE)
        left_bot = [x, y + CARD_HEIGHT]
        right_top = [x + CARD_WIDTH, y]
        right_bot = [x + CARD_WIDTH, y + CARD_HEIGHT]
        self.RestDrawPolygon([left_bot, right_bot], num)
        self.RestDrawPolygon([right_top, right_bot], num)

    def Render(self, screen):
        screen.fill(WHITE)
        self.RestRender(screen)
        for card in self.pool:
            card.Render(screen)
        for deck in self.decks:
            deck.Render(screen)
        for deck in self.decks:
            deck.rules.Render(screen)
        if self.selected_card != None:
            self.selected_card.Render(screen)
        self.month_panel.Render(screen)

    def Terminate(self):
        self.next = None

class Game:
    def __init__(self):
        self.next = self
        self.month = 1
        self.scores = [0, 0]
        self.oya = 1
        self.agent_types = ['Simple', 'Human']
        self.temp_round = Round(self.month, self.oya, self.scores, self.agent_types)
        
    def ProcessInput(self, events, pressed_keys):
        filtered_events = []
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                print('next round is called in Game')
                self.next = Game()
            else:
                filtered_events.append(event)
        self.temp_round.ProcessInput(filtered_events, pressed_keys)

    def Update(self):
        self.temp_round.Update()
        if self.temp_round.IsEnd():
            print('Round is ended in Game')
            player = self.temp_round.player
            self.scores[player] = self.scores[player] + self.temp_round.GetScore()
            print('scores : ' + str(self.scores))
            self.month = self.month % 12 + 1
            self.temp_round = Round(self.month, self.oya, self.scores, self.agent_types)

    def Render(self, screen):
        self.temp_round.Render(screen)

    def Terminate(self):
        self.next = None

def run_game(width, height, fps, starting_scene):
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    active_scene = starting_scene

    while active_scene != None:
        pressed_keys = pygame.key.get_pressed()
        
        # Event filtering 
        filtered_events = []
        for event in pygame.event.get():
            quit_attempt = False
            if event.type == pygame.QUIT:
                quit_attempt = True
            elif event.type == pygame.KEYDOWN:
                alt_pressed = pressed_keys[pygame.K_LALT] or \
                              pressed_keys[pygame.K_RALT]
                if event.key == pygame.K_ESCAPE:
                    quit_attempt = True
                elif event.key == pygame.K_F4 and alt_pressed:
                    quit_attempt = True
            
            if quit_attempt:
                pass
                active_scene.Terminate()
            else:
                filtered_events.append(event)
        
        active_scene.ProcessInput(filtered_events, pressed_keys)
        active_scene.Update()
        active_scene.Render(screen)
        
        active_scene = active_scene.next
        
        pygame.display.flip()
        clock.tick(fps)

run_game(WINDOW_WIDTH, WINDOW_HEIGHT, 60, Game())
