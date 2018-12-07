# -*- coding: utf-8 -*-
import pygame
import os
import random
import numpy as np
from agent import *
from rule import *
from widget import *

#init pygame
pygame.init()
pygame.font.init()

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

CARD_CONTENTS = [[i, j] for i in range(1, 13) for j in range(1, 5)]
card_contents = CARD_CONTENTS

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
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

class Deck:
    def __init__(self, card_list, y, month, oya, player, agent_type = 'Human'):
        self.oya = oya
        self.player = player
        self.cards = card_list
        for card in self.cards:
            card.parent = self.cards
        self.score_dic = {'kou':0, 'tane':1, 'tan':2, 'kasu':3}
        self.scored_cards = [[] for i in range(0, len(self.score_dic))]
        self.scored_cards_render = []
        self.prop_arr = np.zeros(PROP_DIC_LEN, dtype=int)
        self.scored_cards_prop = [[] for i in range(0, PROP_DIC_LEN)]
        self.pool = None
        self.opp_rules = None
        self.opp_scored_cards = None
        self.opp_scored_cards_prop = None
        self.opp_prop_arr = None 
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
        elif agent_type == 'Simple':
            return SimpleAgent(self)
        else:
            return RandomAgent(self)

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

    def Update(self, pool, opp_rules, opp_scored_cards,
               opp_scored_cards_prop, opp_prop_arr):
        self.pool = pool
        self.opp_rules = opp_rules
        self.opp_scored_cards = opp_scored_cards
        self.opp_scored_cards_prop = opp_scored_cards_prop
        self.opp_prop_arr = opp_prop_arr
        # self.agent.UpdateOppInfo()
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
        self.state_dic = {'idle':0, 'match':1, 'second':2, 'match_second':3, 'koikoi':4, 'end':5, 'pre_idle':6}
        self.state = self.state_dic['idle']
        self.second_flip_state = False
        self.selected_card = None
        self.wait_time = 30
        self.time_count = 0

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
                    if card in self.matched_cards:
                        self.matched_cards = [card]
                    else:
                        print('Err: Agent is trying to pick an illegal card from pool')
                        quit()
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
            self.state = self.state_dic['pre_idle']
            # self.state = self.state_dic['idle']
            self.pool_avail_idx = self.temp_pool_avail_idx.copy()
            print('update pol_avail_idx')

    def PreIdleToIdle(self):
        if self.state == self.state_dic['pre_idle']:
            self.time_count = self.time_count + 1
            if self.time_count == self.wait_time:
                self.time_count = 0
                self.state = self.state_dic['idle']
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
        self.PreIdleToIdle()
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
        for i in range(0, 2):
            self.decks[i].Update(self.pool, self.decks[1-i].rules,
                                 self.decks[1-i].scored_cards,
                                 self.decks[1-i].scored_cards_prop,
                                 self.decks[1-i].prop_arr)
        for deck in self.decks:
            deck.agent.UpdateOppInfo()
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
        self.agent_types = ['Random', 'Human']
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
