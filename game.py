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
WINDOW_SIZE_X = BOARDER * 2 + (CARD_SPACING + CARD_WIDTH) * 8 - CARD_SPACING + DECK_WIDTH
WINDOW_SIZE_Y = 4 * CARD_HEIGHT + 4 * MIDDLE_SPACING
WINDOW_SIZE = (WINDOW_SIZE_X, WINDOW_SIZE_Y)
WINDOW_RECT = pygame.Rect(0, 0, WINDOW_SIZE_X, WINDOW_SIZE_Y)
UP_CARD_POS = [[BOARDER + i * (CARD_SPACING + CARD_WIDTH), BOARDER] for i in range(0, 8)]
DOWN_CARD_POS = [[p[0], WINDOW_SIZE_Y - BOARDER - CARD_HEIGHT] for p in UP_CARD_POS]
MIDDLE_BUFFER = MIDDLE_SPACING + CARD_HEIGHT
POOL_WIDTH = 7
MIDDLE_CARD_X = [BOARDER + (i + 1) * (MIDDLE_SPACING + CARD_WIDTH) for i in range(0, POOL_WIDTH)]
MIDDLE_CARD_POS = [[x, BOARDER + i * MIDDLE_BUFFER] for x in MIDDLE_CARD_X for i in range(1, 3)]
CARD_POS = UP_CARD_POS + DOWN_CARD_POS + MIDDLE_CARD_POS[:8]
DECK_SIZE = 8
POOL_SIZE = 8

#card properties
prop_dic = {'kou':0, 'subkou':1, 'tane':2, 'tane_ani':3, 'tan':4, 'tan_r':5, 'tan_b':6, 'kasu':7}
PROP_DIC_LEN = 8
def property_array(idx_list, num = PROP_DIC_LEN):
    v = np.zeros(num, dtype = int)
    for idx in idx_list:
        v[idx] = v[idx] + 1
    return v

KOU = property_array([prop_dic['kou']])
SUBKOU = property_array([prop_dic['subkou']])
TAN = property_array([prop_dic['tan']])
TAN_R = property_array([prop_dic['tan'], prop_dic['tan_r']])
TAN_B = property_array([prop_dic['tan'], prop_dic['tan_b']])
TANE = property_array([prop_dic['tane']])
TANE_ANI = property_array([prop_dic['tane'], prop_dic['tane_ani']])
kasu = property_array([prop_dic['kasu']])
KYOKU = property_array([prop_dic['kasu'], prop_dic['tane']])
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
    name_order = ['kou', 'tane', 'tan', 'kasu']
    for name in name_order:
        if props[prop_dic[name]] == 1:
            return name
        elif props[prop_dic['subkou']] == 1:
            return 'kou'
    print('Error: card %d %d has no type!' % (card.month, card.order))
    return None

def get_surf(font, text, color = WHITE):
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    return surf, rect

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
        self.text_list = [q_text, y_text, n_text]
        self.surf_list = [self.q_surf, self.y_surf, self.n_surf]
        self.rect_list = [self.q_rect, self.y_rect, self.n_rect]
        lists = zip(self.text_list, self.surf_list, self.rect_list)
        for text, surf, rect in lists:
            surf, rect = get_surf(font, text, color)

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
        

#scoring rules
class Rules:
    def __init__(self, month):
        self.patterns = [[u'猪鹿蝶', 5, property_array([prop_dic['tane_ani']] * 3)],
                         [u'赤短', 6, property_array([prop_dic['tan_r']] * 3)],
                         [u'青短', 6, property_array([prop_dic['tan_b']] * 3)]]
        self.kous = [[u'三光', 6, property_array([prop_dic['kou']] * 3)],
                     [u'四光', 10, property_array([prop_dic['kou']] * 4)],
                     [u'五光', 15, property_array([prop_dic['kou']] * 4 + [prop_dic['subkou']])],
                     [u'雨四光', 8, property_array([prop_dic['kou']] * 3 + [prop_dic['subkou']])]]
        self.kasu_lim = 10
        self.tane_lim = 5
        self.tan_lim = 5
        self.month = month
        self.records = {}
        self.new_patterns = []
        self.window_size = [7 * CARD_WIDTH, 1.5 * CARD_HEIGHT]
        self.window_pos_x = (WINDOW_SIZE_X - self.window_size[0]) / 2
        self.window_pos_y = (WINDOW_SIZE_Y - self.window_size[1]) / 2
        self.window_pos = [self.window_pos_x, self.window_pos_y] 
        self.font = pygame.font.Font("KosugiMaru-Regular.ttf", 40)
        self.state_dic = {'idle':0, 'pump':1, 'koikoi':2}
        self.state = self.state_dic['idle'] 
        self.text = ''
        self.pump_idx = 0

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

    def CheckPatterns(self, in_arr, cards_prop):
        new_pattern = False
        new_patterns = []
        name_list = [pattern[0] for pattern in self.patterns]
        name_list = name_list + ['kou'] * len(self.kous)
        for name, pattern in zip(name_list, self.patterns + self.kous):
            if (in_arr >= pattern[2]).all():
                if self.Check(pattern[:-1], name):
                    print(name + 'is checked')
                    new_pattern = True
                    cards = []
                    for idx, i in enumerate(pattern[2]):
                        cards.append(cards_prop[idx][:i])
                    new_patterns.append(pattern[:-1] + [cards])
        # for kou in self.kous:
            # if (in_arr > pattern[2]).all():
                # name = 'kou'
                # if self.Check(pattern[:-1], name):
                    # new_pattern = True
                    # cards = []
                    # for idx, i in pattern[2]:
                        # cards.append(cards_prop[idx][:i])
                    # new_patterns.append(pattern[:-1])
        name_lists = [['kasu', u'カス'], ['tane', u'タネ'], ['tan', u'短冊']]
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
        if new_pattern:
            self.new_patterns = new_patterns
        return new_pattern

    def Collide(self, pos):
        return (pos[0] >= self.window_pos[0] and 
                pos[0] <= self.window_pos[0] + self.window_size[0] and
                pos[1] >= self.window_pos[1] and 
                pos[1] <= self.window_pos[1] + self.window_size[1])

    def ProcessInput(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if self.Collide(pos):
                    print('window is clicked')
                    if self.state == self.state_dic['pump']:
                        self.pump_idx = self.pump_idx + 1
                        if self.pump_idx == len(self.new_patterns):
                            # self.state = self.state_dic['koikoi']
                            self.state = self.state_dic['idle']

    def Update(self):
        if self.new_patterns != [] and self.state == self.state_dic['idle']:
            self.state = self.state_dic['pump']
            self.pump_idx = 0

    def Render(self, screen):
        if self.state == self.state_dic['pump']:
            pygame.draw.rect(screen, BLACK, self.window_pos + self.window_size)
            pattern = self.new_patterns[self.pump_idx]
            text = pattern[0] + '\n' + str(pattern[1]) + '文'
            text_surface = self.font.render(text, True, WHITE)
            text_rect = text_surface.get_rect()
            text_center_x = int(self.window_pos_x + BOARDER + text_rect.width / 2)
            text_center_y = int(self.window_pos_y + self.window_size[1] / 2)
            text_rect.center = [text_center_x, text_center_y]
            screen.blit(text_surface, text_rect)
        elif self.state == self.state_dic['koikoi']:
            question = u'こいこいしますか？'
            q_surf = self.font.render(text, True, WHITE)
            q_rect = q_surf.get_rect()


COVER_BOARDER = 10

#colors
WHITE = [255, 255, 255]
YELLOW = [255, 255, 0]
BLACK = [0, 0, 0]
GRAY = [128, 128, 128]
BLUE = [0, 128, 255]

CARD_CONTENTS = [[i, j] for i in range(1, 13) for j in range(1, 5)]
card_contents = CARD_CONTENTS

screen = pygame.display.set_mode((WINDOW_SIZE_X, WINDOW_SIZE_Y))
done = False
flag = True

# MOVE_TIME = 0.5
MOVE_FRAME = 30

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
        self.image = get_image(str(content[0]) + '_' + str(content[1]) + '.png')
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

    def Render(self, screen):
        wrap_rect =self. pos + CARD_SIZE
        fig_rect = self.fig_pos + FIG_SIZE
        if self.selected:
            pygame.draw.rect(screen, YELLOW, wrap_rect)
        else:
            pygame.draw.rect(screen, BLACK, wrap_rect)
        pygame.draw.rect(screen, WHITE, fig_rect)
        screen.blit(self.image, self.fig_pos)

class Deck:
    def __init__(self, card_list, y, month):
        self.rules = Rules(month)
        self.cards = card_list
        for card in self.cards:
            card.parent = self.cards
        self.score_dic = {'kou':0, 'tane':1, 'tan':2, 'kasu':3}
        self.scored_cards = [[] for i in range(0, len(self.score_dic))]
        self.prop_arr = np.zeros(PROP_DIC_LEN, dtype=int)
        self.scored_cards_prop = [[] for i in range(0, PROP_DIC_LEN)]
        self.pool = None
        self.opponent_scored = None
        self.move = False
        self.deck_y = y
        self.right_corner = [WINDOW_SIZE_X - BOARDER - CARD_WIDTH, y]
        self.left_corner = [BOARDER, y]
        self.overlap_ratio = 1 / 3
        self.overlap = int(self.overlap_ratio * CARD_WIDTH)
        self.type_spacing = 10

    def ProcessInput(self, events, pressed_keys):
        for card in self.cards:
            selected_card = card.ProcessInput(events, pressed_keys)
            if selected_card != None:
                print('deck get selected card!')
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
        self.rules.Update()

    def Render(self, screen):
        for card in self.cards:
            card.Render(screen)
        for cards in self.scored_cards:
            for card in cards:
                card.Render(screen)
        self.rules.Render(screen)


class Round:
    def __init__(self, month):
        random.shuffle(card_contents)
        self.next = self
        self.month = month
        cards = []
        self.player = 1
        #rest settings
        self.rest_max_size = len(card_contents) - 2 * DECK_SIZE - POOL_SIZE
        self.card_depth = 1
        self.rest_angle = 20
        self.dy = self.card_depth
        self.dx = self.card_depth * np.tan(np.deg2rad(self.rest_angle))
        self.rest_pos = [BOARDER, int((WINDOW_SIZE_Y - CARD_HEIGHT) / 2)]
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
        corner_x = WINDOW_SIZE_X - CARD_WIDTH - BOARDER
        top_deck = Deck(cards[:DECK_SIZE], BOARDER, month)
        bot_y = WINDOW_SIZE_Y - CARD_HEIGHT - BOARDER
        bot_deck = Deck(cards[DECK_SIZE:2 * DECK_SIZE], bot_y, month)
        self.decks = [top_deck, bot_deck]
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
        self.state_dic = {'idle':0, 'match':1, 'second':2, 'match_second':3, 'koikoi':4}
        self.state = self.state_dic['idle']
        self.second_flip_state = False
        self.selected_card = None

    def toggle_player(self):
        self.player = 1 - self.player

    def in_match_state(self):
        return self.state == self.state_dic['match'] \
            or self.state == self.state_dic['match_second']

    def ProcessInput(self, events, pressed_keys):
        filtered_events = []
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.next = Round(self.month % 12 + 1)
            else:
                filtered_events.append(event)
        if self.in_match_state():
            for card in self.matched_cards:
                pool_selected_card = card.ProcessInput(filtered_events, pressed_keys)
                if pool_selected_card != None:
                    print('get selected card in pool')
                    self.matched_cards = [pool_selected_card]
        else:
            selected_card = None
            if self.state == self.state_dic['idle']:
                deck = self.decks[self.player]
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
            for card in [self.selected_card, self.matched_cards[0]]:
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

    def Update(self):
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
        if self.selected_card != None:
            self.selected_card.Render(screen)

    def Terminate(self):
        self.next = None

# class Game:
    # def __init__(self):
        # self.rounds = Round()

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
                active_scene.Terminate()
            else:
                filtered_events.append(event)
        
        active_scene.ProcessInput(filtered_events, pressed_keys)
        active_scene.Update()
        active_scene.Render(screen)
        
        active_scene = active_scene.next
        
        pygame.display.flip()
        clock.tick(fps)

run_game(WINDOW_SIZE_X, WINDOW_SIZE_Y, 60, Round(12))
