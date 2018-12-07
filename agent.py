import random

class BaseAgent:
    def __init__(self, deck):
        # print('base agent is initialized')
        self.deck = deck
        self.cards = deck.cards
        self.pool = deck.pool
        self.opp_rules = deck.opp_rules
        self.opp_scored_cards = deck.opp_scored_cards
        self.opp_scored_cards_prop = deck.opp_scored_cards_prop
        self.opp_prop_arr = deck.opp_prop_arr

    def UpdateOppInfo(self):
        self.pool = self.deck.pool
        self.opp_rules = self.deck.opp_rules
        self.opp_scored_cards = self.deck.opp_scored_cards
        self.opp_scored_cards_prop = self.deck.opp_scored_cards_prop
        self.opp_prop_arr = self.deck.opp_prop_arr

    def PrintOppInfo(self):
        print('in print opp info ========================================')
        self.PrintCards('pool', self.pool)
        print('opp scored cards: ')
        for cards in self.opp_scored_cards:
            self.PrintCards('cards', cards)
        # print('opp scored prop: ' + str(self.opp_scored_cards_prop))
        print('opp prop arr: ' + str(self.opp_prop_arr))

    def PrintCards(self, name, cards):
        print(name + ': ', end = '')
        for card in cards:
            print('(%d,%d) ' % (card.month, card.order), end = '')
        print(' ')

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

class SimpleAgent(BaseAgent):
    def __init__(self, deck):
        BaseAgent.__init__(self, deck)
        # print('simple agent is initialized')

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
        if len(self.cards) == 0:
            # print('no cards on hand in Action !!!')
            return 
        return self.cards[0] 

    def PoolAction(self, cards):
        return cards[0]

class RandomAgent(BaseAgent):
    def __init__(self, deck):
        BaseAgent.__init__(self, deck)
        # print('Random agent is initialized')
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

class HumanAgent(BaseAgent):
    def __init__(self, deck):
        BaseAgent.__init__(self, deck)
