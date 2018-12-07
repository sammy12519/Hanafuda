import numpy as np
import pygame
from widget import *

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

#scoring rules
class Rules:
    def __init__(self, month, oya, deck):
        self.parent = deck
        self.patterns = [['猪鹿蝶', 5, property_array([prop_dic['tane_ani']] * 3)],
                         ['赤短', 6, property_array([prop_dic['tan_r']] * 3)],
                         ['青短', 6, property_array([prop_dic['tan_b']] * 3)]]
        self.kous = [['五光', 15, property_array([prop_dic['kou']] * 4 + [prop_dic['subkou']])],
                     ['雨四光', 8, property_array([prop_dic['kou']] * 3 + [prop_dic['subkou']])],
                     ['四光', 10, property_array([prop_dic['kou']] * 4)],
                     ['三光', 6, property_array([prop_dic['kou']] * 3)]]  
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
        self.no_koikoi = False
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
        name_list = name_list + ['kou'] * len(self.kous)
        for name, pattern in zip(name_list, self.patterns + self.kous):
            if (in_arr >= pattern[2]).all():
                if self.Check(pattern[:-1], name):
                    print(name + 'is checked')
                    new_pattern = True
                    cards = []
                    for idx, i in enumerate(pattern[2]):
                        cards = cards + cards_prop[idx][:i]
                    new_patterns.append(pattern[:-1] + [cards])
        name_lists = [['kasu', 'カス'], ['tane', 'タネ'], ['tan', '短冊']]
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
                    self.no_koikoi = True
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
                            if self.no_koikoi:
                                self.ToScoreState()
                            else:
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

    def Render(self, screen):
        if self.state == self.state_dic['pump']:
            self.PumpRender(screen)
        elif self.state == self.state_dic['koikoi']:
            self.koikoi_panel.Render(screen)
        elif self.state == self.state_dic['score']:
            self.score_panel.Render(screen)
