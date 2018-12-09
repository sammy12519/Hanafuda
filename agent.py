import random
from operator import itemgetter
from rule import * 

class BaseAgent:
    def __init__(self):
        # print('base agent is initialized')
        self.deck = None
        self.cards = []
        self.pool = []
        self.patterns_inited = False
        # self.opp_rules = deck.opp_rules
        # self.opp_scored_cards = deck.opp_scored_cards
        # self.opp_scored_cards_prop = deck.opp_scored_cards_prop
        # self.opp_prop_arr = deck.opp_prop_arr

    def GetInfo(self, deck): 
        self.deck = deck
        self.cards = deck.cards
        self.pool = deck.pool
        self.rules = deck.rules
        self.scored_cards = deck.scored_cards
        self.scored_cards_prop = deck.scored_cards_prop
        self.scored_cards_1d = deck.scored_cards_render
        self.prop_arr = deck.prop_arr
        self.opp_rules = deck.opp_rules
        self.opp_scored_cards = deck.opp_scored_cards
        self.opp_scored_cards_prop = deck.opp_scored_cards_prop
        self.opp_scored_cards_1d = deck.opp_scored_cards_render
        self.opp_prop_arr = deck.opp_prop_arr
        self.prop_remain = None
        self.avail_cards = None
        self.patterns = None

    def PrintSelfInfo(self):
        print('in print self info =======================================')
        if self.pool == None:
            return
        self.PrintCards('hand', self.cards)


    def PrintOppInfo(self):
        print('in print opp info ========================================')
        if self.pool == None:
            return
        self.PrintCards('pool', self.pool)
        print('opp scored cards: ')
        for cards in self.opp_scored_cards:
            self.PrintCards('cards', cards)
        # print('opp scored prop: ' + str(self.opp_scored_cards_prop))
        print('opp prop arr: ' + str(self.opp_prop_arr))

    def PrintCards(self, name, cards):
        if cards == None:
            return
        print(name + ': ', end = '')
        for card in cards:
            print('(%d,%d) ' % (card.month, card.order), end = '')
        print(' ')

    def GetCardProp(self, card):
        return CARD_INFO[card.month-1][card.order-1]

    def NumMonthInHand(self, card):
        num = 0
        c_list = []
        for c in self.cards:
            if c.month == card[0]:
                num = num + 1
                c_list.append(c)
        return num, c_list

    def InHand(self, card):
        return self.InCards(card, self.cards)

    def InPool(self, card):
        return self.InCards(card, self.pool)

    def InCards(self, card, cards):
        for c in cards:
            if c.month == card[0] and c.order == card[1]:
                return c
        return None

    def FindMatchCards(self):
        matching = {}
        for card in self.cards:
            match = []
            for pcard in self.pool:
                if card.month == pcard.month:
                    match.append(pcard)
            if match != []:
                matching[card] = match
        return matching

    # def Update(self):
    def CheckRemain(self):
        prop_remain = [[] for i in range(0, PROP_DIC_LEN)]
        avail_cards = [[1 for j in range(0, 4)] for i in range(0, 12)]
        for card in self.scored_cards_1d + self.opp_scored_cards_1d:
            avail_cards[card.month - 1][card.order - 1] = 0
        # print('remain cards: ')
        for i in range(0, 12):
            for j in range(0, 4):
                if avail_cards[i][j] == 1:
                    # print('(%d,%d)' %(i, j), end = '')
                    for idx, val in enumerate(CARD_INFO[i][j]):
                        if val == 1:
                            prop_remain[idx].append([i, j])
        prop_remain = np.asarray(prop_remain)
        return prop_remain, avail_cards

    def InitPatterns(self):
        patterns = []
        for pattern in self.rules.patterns + self.rules.kous:
            patterns.append([pattern[2], pattern[1], pattern[0]])
        self.patterns = patterns

    def CheckProgress(self, in_arr, decided = False):
        if not self.patterns_inited:
            self.InitPatterns()
        progress = []
        for pattern in self.patterns:
            ref_prop = pattern[0]
            diff = np.zeros(len(ref_prop), dtype=int)
            if not (in_arr >= ref_prop).all():
                mask = ref_prop > 0
                diff[mask] = (ref_prop[mask] - in_arr[mask])
                diff[diff < 0] = 0
                progress.append([diff, pattern[1], pattern[2]])
            else:
                if decided:
                    self.pattern.remove(pattern)
        name_list = ['kasu', 'tane', 'tan']
        lims = [self.rules.kasu_lim, self.rules.tane_lim, self.rules.tan_lim]
        for name, lim in zip(name_list, lims):
            idx = prop_dic[name]
            diff = np.zeros(len(ref_prop), dtype=int)
            if in_arr[idx] >= lim:
                diff[idx] = 1
            else:
                diff[idx] = lim - in_arr[idx]
            progress.append([diff, 1, name])
        self.progress = progress
        # print('progress: ' + str(progress))
        return progress 

    def CheckSelfProgress(self):
        return self.CheckProgress(self.prop_arr, decided=False)

    def CheckOppProgress(self):
        return self.CheckProgress(self.opp_prop_arr, decided=False)

class SimpleAgent(BaseAgent):
    def __init__(self):
        BaseAgent.__init__(self)
        self.name = 'Simple'
        # print('simple agent is initialized')

    def Action(self, cards = None, koikoi = False):
        # self.PrintOppInfo()
        if self.deck == None:
            return
        # self.PrintCards('Deck cards: ', self.deck.cards)
        # self.PrintSelfInfo()
        if koikoi:
            return self.KoiKoiAction()
        elif cards == None:
            return self.HandAction()
        else:
            return self.PoolAction(cards)
    
    def KoiKoiAction(self):
        return False

    def HandAction(self):
        if len(self.cards) == 0:
            # print('no cards on hand in Action !!!')
            return 
        return self.cards[0] 

    def PoolAction(self, cards):
        return cards[0]

class RandomAgent(BaseAgent):
    def __init__(self):
        BaseAgent.__init__(self)
        # print('Random agent is initialized')
        self.name = 'Random'
        self.pool_card = None

    def Action(self, cards = None, koikoi = False):
        # self.PrintOppInfo()
        if koikoi:
            return self.KoiKoiAction()
        elif cards == None:
            return self.HandAction()
        else:
            return self.PoolAction(cards)
    
    def KoiKoiAction(self):
        return False

    def HandAction(self):
        if len(self.cards) == 0 or self.pool == None:
            # print('no cards on hand in Action !!!')
            return 
        matching = self.FindMatchCards()
        if len(matching) == 0:
            return random.choice(self.cards)
        else:
            card = random.choice(list(matching.keys()))
            return card 

    def PoolAction(self, cards):
        return random.choice(cards)

class HungWeiAgent(BaseAgent):
    def __init__(self):
        BaseAgent.__init__(self)
        # print('Random agent is initialized')
        self.name = 'HungWei'
        self.has_pool_card = False
        self.pool_card = None

    def Action(self, cards = None, koikoi = False):
        # self.PrintOppInfo()
        if koikoi:
            return self.KoiKoiAction()
        elif cards == None:
            return self.HandAction()
        else:
            return self.PoolAction(cards)
    
    def KoiKoiAction(self):
        return False

    def BestMatch(self, card, matched_cards, progress):
        card_prop = self.GetCardProp(card)
        matched_cards_prop = [self.GetCardProp(c) for c in matched_cards]
        best_choice = None
        best_gain = -100000
        best_idx = -1
        for idx, c in enumerate(matched_cards_prop):
            for [diff, val, name] in progress:
                total = c + card_prop
                mask = diff > 0
                result = diff[mask] - total[mask]
                result[result < 0] = 0
                gain = diff[mask] - result
                gain_val = val * np.sum(gain) / np.sum(diff)
                if gain_val > best_gain:
                    best_gain = gain_val
                    best_choice = c
                    best_idx = idx
        return matched_cards[best_idx], best_gain

    def HandAction(self):
        if len(self.cards) == 0 or self.pool == None:
            # print('no cards on hand in Action !!!')
            return 
        matching = self.FindMatchCards()
        prop_remain, avail_cards = self.CheckRemain()
        progress = self.CheckSelfProgress()
        opp_progress = self.CheckOppProgress()
        if len(matching) == 0:
            return random.choice(self.cards)
        else:
            pool_cards = []
            vals = []
            for key in list(matching.keys()):
                pool_card, val = self.BestMatch(key, matching[key], progress)
                pool_cards.append(pool_card)
                vals.append(val)
            idx = np.argmax(vals)
            card = list(matching.keys())[idx]
            # print('pool_cards-------------------')
            # print(pool_cards)
            if len(matching[card]) >= 2:
                self.pool_card = pool_cards[idx]
                self.has_pool_card = True
            return card 

    def PoolAction(self, cards):
        if self.has_pool_card:
            self.has_pool_card = False
            # print('Has pool card : (%d,%d)' % (self.pool_card.month, self.pool_card.order))
            return self.pool_card
        else:
            return random.choice(cards)

class CompleteAgent(BaseAgent):
    def __init__(self):
        BaseAgent.__init__(self)
        # print('Random agent is initialized')
        self.name = 'Complete'
        self.has_pool_card = False
        self.pool_card = None

    def Action(self, cards = None, koikoi = False):
        # self.PrintOppInfo()
        if koikoi:
            return self.KoiKoiAction()
        elif cards == None:
            return self.HandAction()
        else:
            return self.PoolAction(cards)
    
    def KoiKoiAction(self):
        return False

    def BestMatch(self, card, matched_cards, progress):
        card_prop = self.GetCardProp(card)
        matched_cards_prop = [self.GetCardProp(c) for c in matched_cards]
        best_choice = None
        best_gain = -100000
        best_idx = -1
        for idx, c in enumerate(matched_cards_prop):
            for [diff, val, name] in progress:
                total = c + card_prop
                mask = diff > 0
                result = diff[mask] - total[mask]
                result[result < 0] = 0
                gain = diff[mask] - result
                gain_val = val * np.sum(gain) / np.sum(diff)
                if gain_val > best_gain:
                    best_gain = gain_val
                    best_choice = c
                    best_idx = idx
        return matched_cards[best_idx], best_gain

    def HandAction(self):
        if len(self.cards) == 0 or self.pool == None:
            # print('no cards on hand in Action !!!')
            return 
        matching = self.FindMatchCards()
        prop_remain, avail_cards = self.CheckRemain()
        progress = self.CheckSelfProgress()
        opp_progress = self.CheckOppProgress()
        if len(matching) == 0:
            return random.choice(self.cards)
        else:
            pool_cards = []
            vals = []
            for key in list(matching.keys()):
                pool_card, val = self.BestMatch(key, matching[key], progress)
                pool_cards.append(pool_card)
                vals.append(val)
            idx = np.argmax(vals)
            card = list(matching.keys())[idx]
            # print('pool_cards-------------------')
            # print(pool_cards)
            if len(matching[card]) >= 2:
                self.pool_card = pool_cards[idx]
                self.has_pool_card = True
            return card 

    def PoolAction(self, cards):
        if self.has_pool_card:
            self.has_pool_card = False
            # print('Has pool card : (%d,%d)' % (self.pool_card.month, self.pool_card.order))
            return self.pool_card
        else:
            return random.choice(cards)

class HeuristicAgent(BaseAgent):
    def __init__(self):
        BaseAgent.__init__(self)
        # print('Random agent is initialized')
        self.name = 'HungWei'
        self.has_pool_card = False
        self.pool_card = None

    def Action(self, cards = None, koikoi = False):
        # self.PrintOppInfo()
        if koikoi:
            return self.KoiKoiAction()
        elif cards == None:
            return self.HandAction()
        else:
            return self.PoolAction(cards)
    
    def KoiKoiAction(self):
        return False

    def IsPossibleProgress(self, diff, prop_remain, avail_cards):
        mask = diff > 0
        ref = diff[mask]
        remain = prop_remain[mask]
        remain_num = np.array([len(r) for r in remain], dtype=int) 
        gap = ref - remain_num
        if (gap <= 0).all():
            return [c for r in remain for c in r]
        else:
            return None

    def EvaluateDecision(self, new_prop_arr, prop_remain, avail_cards, opp_progress):
        mid_progress = self.CheckProgress(new_prop_arr)
        # print(mid_progress)
        candidates = []
        new_progress = []
        for np in mid_progress:
            can = self.IsPossibleProgress(np[0], prop_remain, avail_cards) 
            if can != None:
                new_progress.append(np)
                candidates.append(can)
        score = self.EvaluateProgress(new_progress, candidates, avail_cards, opp_progress)
        return score

    def EvaluatePattern(self, diff, val, can):
        num = np.sum(diff)
        unknown_num = 0
        unknown_match_num = 0
        in_hand_num = 0
        in_pool_num = 0
        in_pool_match_num = 0
        for c in can:
            if self.InHand(c):
                in_hand_num = in_hand_num + 1
            else:
                if self.InPool(c):
                    in_pool_num = in_pool_num + 1
                    if self.NumMonthInHand(c) != 0:
                        in_pool_match_num = in_pool_match_num + 1
                else:
                    unknown_num = unknown_num + 1
                    if self.NumMonthInHand(c) != 0:
                        unknown_match_num = unknown_match_num + 1
        ratio = in_hand_num * 0.8 + unknown_match_num * 0.5 + in_pool_match_num * 0.6 / num 
        return ratio * val

    def EvaluateProgress(self, progress, candidates, avail_cards, opp_progress):
        score = 0
        for [diff, val, name], can in zip(progress, candidates):
            num = np.sum(diff)
            unknown_num = 0
            unknown_match_num = 0
            in_hand_num = 0
            in_pool_num = 0
            in_pool_match_num = 0
            for c in can:
                if self.InHand(c):
                    in_hand_num = in_hand_num + 1
                else:
                    if self.InPool(c):
                        in_pool_num = in_pool_num + 1
                        if self.NumMonthInHand(c) != 0:
                            in_pool_match_num = in_pool_match_num + 1
                    else:
                        unknown_num = unknown_num + 1
                        if self.NumMonthInHand(c) != 0:
                            unknown_match_num = unknown_match_num + 1
            ratio = in_hand_num * 0.8 + unknown_match_num * 0.5 + in_pool_match_num * 0.6 / num 
            score = score + ratio * val
        return score

    def BestMatch(self, card, matched_cards, prop_remain, avail_cards,  progress, opp_progress):
        card_prop = self.GetCardProp(card)
        matched_cards_prop = [self.GetCardProp(c) for c in matched_cards]
        best_choice = None
        best_score = -100000
        best_idx = -1
        for idx, c in enumerate(matched_cards_prop):
            for [diff, val, name] in progress:
                total = c + card_prop
                new_avail_cards = avail_cards.copy()
                new_avail_cards[card.month-1][card.order-1] = 0
                matched_card = matched_cards[idx]
                new_avail_cards[matched_card.month-1][matched_card.order-1] = 0
                score = self.EvaluateDecision(self.prop_arr + total, prop_remain, new_avail_cards, opp_progress)
                if score > best_score:
                    best_score = score
                    best_choice = c
                    best_idx = idx
        return matched_cards[best_idx], best_score

    def HandAction(self):
        if len(self.cards) == 0 or self.pool == None:
            # print('no cards on hand in Action !!!')
            return 
        matching = self.FindMatchCards()
        prop_remain, avail_cards = self.CheckRemain()
        progress = self.CheckSelfProgress()
        opp_progress = self.CheckOppProgress()
        if len(matching) == 0:
            return random.choice(self.cards)
        else:
            pool_cards = []
            vals = []
            for key in list(matching.keys()):
                pool_card, val = self.BestMatch(key, matching[key], prop_remain, avail_cards,  progress, opp_progress)
                pool_cards.append(pool_card)
                vals.append(val)
            idx = np.argmax(vals)
            card = list(matching.keys())[idx]
            # print('pool_cards-------------------')
            # print(pool_cards)
            if len(matching[card]) >= 2:
                self.pool_card = pool_cards[idx]
                self.has_pool_card = True
            return card 

    def PoolAction(self, cards):
        if self.has_pool_card:
            self.has_pool_card = False
            # print('Has pool card : (%d,%d)' % (self.pool_card.month, self.pool_card.order))
            return self.pool_card
        else:
            return random.choice(cards)

# class HungWeiAgent(BaseAgent):
    # def __init__(self):
        # BaseAgent.__init__(self)
        # # print('Random agent is initialized')
        # self.name = 'HungWei'
        # self.has_pool_card = False
        # self.pool_card = None

    # def Action(self, cards = None, koikoi = False):
        # # self.PrintOppInfo()
        # if koikoi:
            # return self.KoiKoiAction()
        # elif cards == None:
            # return self.HandAction()
        # else:
            # return self.PoolAction(cards)
    
    # def KoiKoiAction(self):
        # return False

    # def IsPossibleProgress(self, diff, prop_remain, avail_cards):
        # mask = diff > 0
        # ref = diff[mask]
        # remain = prop_remain[mask]
        # remain_num = np.array([len(r) for r in remain], dtype=int) 
        # gap = ref - remain_num
        # if (gap <= 0).all():
            # return [c for r in remain for c in r]
        # else:
            # return None

    # def EvaluateSelfProgress(self, prop_remain, avail_cards):
        # mid_progress = self.CheckProgress(self.prop_arr)
        # candidates = []
        # new_progress = []
        # p_info = []
        # for np in mid_progress:
            # can = self.IsPossibleProgress(np[0], prop_remain, avail_cards) 
            # if can != None:
                # new_progress.append(np)
                # candidates.append(can)
                # p_score, in_hand_list, in_pool_match_list, in_pool_list = self.EvaluatePattern(np[0], np[1], can)
                # p_info.append([np, p_score, in_hand_list, in_pool_match_list, in_pool_list])
        # return p_info

    # def EvaluatePattern(self, diff, val, can):
        # num = np.sum(diff)
        # unknown_num = 0
        # unknown_match_num = 0
        # in_hand_num = 0
        # in_pool_num = 0
        # in_pool_match_num = 0
        # in_hand_list = []
        # in_pool_list = []
        # in_pool_match_list = []
        # for c in can:
            # in_hand = self.InHand(c)
            # if in_hand != None:
                # in_hand_num = in_hand_num + 1
                # in_hand_list.append(in_hand)
            # else:
                # if self.InPool(c) != None:
                    # in_pool_num = in_pool_num + 1
                    # n, in_pool_match = self.NumMonthInHand(c)
                    # if n != 0:
                        # in_pool_match_num = in_pool_match_num + 1
                        # in_pool_list.append(c)
                        # in_pool_match_list.append(in_pool_match)
                # else:
                    # unknown_num = unknown_num + 1
                    # n, unknown_match = self.NumMonthInHand(c)
                    # if n != 0:
                        # unknown_match_num = unknown_match_num + 1
        # ratio = in_hand_num * 0.8 + unknown_match_num * 0.5 + in_pool_match_num * 0.6 / num 
        # score = ratio * val
        # return score, in_hand_list, in_pool_match_list, in_pool_list

    # def HandAction(self):
        # if len(self.cards) == 0 or self.pool == None:
            # # print('no cards on hand in Action !!!')
            # return 
        # matching = self.FindMatchCards()
        # prop_remain, avail_cards = self.CheckRemain()
        # progress = self.CheckSelfProgress()
        # opp_progress = self.CheckOppProgress()
        # if len(matching) == 0:
            # return random.choice(self.cards)
        # else:
            # choice = None
            # pool_choice = None
            # best_choice = None
            # second_choice = None
            # third_choice = None
            # best_pool = None
            # second_pool = None
            # third_pool = None
            # for card in list(matching.keys()):
                # matches = matching[card]
                # p_info = self.EvaluateSelfProgress(prop_remain, avail_cards)
                # p_info = sorted(p_info, key=itemgetter(1))
                # for [p, score, in_hand_list, in_pool_match_list, in_pool] in p_info:
                    # for in_pool_matches in in_pool_match_list:
                        # print('in pool matches : ' + str(in_pool_matches))
                        # if card in in_pool_matches:
                            # if card in in_hand_list:
                                # best_choice = card
                                # for match in matches:
                                    # debug = True
                                    # if match in in_pool:
                                        # best_pool = match
                                        # debug = False
                                    # if debug:
                                        # print('in pool match is selected but no corresponding pool')
                            # else:
                                # second_choice = card
                                # for match in matches:
                                    # debug = True
                                    # if match in in_pool:
                                        # second_pool = match    
                                        # debug = False
                                    # if debug:
                                        # print('in pool match is selected but no corresponding pool')
                        # elif card in in_hand_list:
                            # third_choice = card
                    # if best_choice != None:
                        # choice = best_choice
                        # pool_choice = best_pool
                        # break
                    # elif second_choice != None:
                        # choice = second_choice
                        # pool_choice = second_pool
                        # break
                    # elif third_choice != None:
                        # choice = third_choice
                        # break
            # if len(matching[choice]) >= 2 and pool_choice != None:
                # self.pool_card = pool_choice
                # self.has_pool_card = True
            # return choice

    # def PoolAction(self, cards):
        # if self.has_pool_card:
            # self.has_pool_card = False
            # # print('Has pool card : (%d,%d)' % (self.pool_card.month, self.pool_card.order))
            # return self.pool_card
        # else:
            # return random.choice(cards)

class HumanAgent(BaseAgent):
    def __init__(self):
        BaseAgent.__init__(self)
        self.name = 'Human'
