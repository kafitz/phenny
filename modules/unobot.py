"""
Copyright 2010 Tamas Marki. All rights reserved.
Revised 2013 Kyle Fitzsimmons. http://kylefitz.com/

Redistribution and use in source and binary forms, with or without modification, are
permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice, this list of
      conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above copyright notice, this list
      of conditions and the following disclaimer in the documentation and/or other materials
      provided with the distribution.


[18:03] <Lako> .play w 3
[18:03] <unobot> TopMobil's turn. Top Card: [Y*]
[18:03] [Notice] -unobot- Your cards: [B4][B9][R4][G][GD2][YD2]
[18:03] [Notice] -unobot- Next: hatcher (5 cards) - Lako (2 cards)
"""

import time
import re
import random
from datetime import datetime, timedelta

random.seed()

# Remember to change these 3 lines or nothing will work
CHANNEL = '#opptestuno'
SCOREFILE = "/mnt/sdc1/ted/phenny/unoscores.txt"
# Only the owner (starter of the game) can call .unostop to stop the game.
# But this calls for a way to allow others to stop it after the game has been idle for a while.
# After this set time, anyone can stop the game via .unostop
# Set the time ___in minutes___ here: (default is 5 mins)
INACTIVE_TIMEOUT = 5

STRINGS = {
    'ALREADY_STARTED': 'Game already started by %s! Type .juno (.ju) to join!',
    'GAME_STARTED': 'UNO started by %s - Type .juno (.ju) to join!',
    'GAME_STOPPED': 'Game stopped.',
    'CANT_STOP': '%s is the game owner, you can\'t stop it! To force stop the game, please wait %s seconds.',
    'DEALING_IN': 'Dealing %s into the game as player #%s!',
    'JOINED': 'Dealing %s into the game as player #%s!',
    'ALREADY_JOINED': 'You have already joined the game, %s!',
    'ENOUGH': 'There are enough players, type .deal to start!',
    'NOT_STARTED': 'Game not started, type .uno to start!',
    'NOT_ENOUGH': 'Not enough players to deal yet.',
    'NEEDS_TO_DEAL': '%s needs to deal.',
    'ALREADY_DEALT': 'Game is already dealt.',
    'ON_TURN': 'It\'s %s\'s turn.',
    'DONT_HAVE': 'You don\'t have that card, %s',
    'DOESNT_PLAY': 'That card is not playable, please choose again.',
    'INVALID_CHOICE': 'Could not parse card choice. Please try again, %s',
    'UNO': 'UNO! %s has ONE card left!',
    'WIN': 'We have a winner! %s!!!! This game took %s',
    'DRAWN_ALREADY': 'You\'ve already drawn, either .pass or .play!',
    'DRAWS': '%s draws a card.',
    'DRAWN_CARD': 'Drawn card: %s',
    'DRAW_FIRST': '%s, you need to draw first!',
    'PASSED': '%s passed!',
    'NO_SCORES': 'No scores yet',
    'TOP_CARD': '%s\'s turn. Top Card: %s',
    'YOUR_CARDS': 'Your cards: %s',
    'NEXT_START': 'Next: ',
    'NEXT_PLAYER': '%s (%s cards)',
    'D2': '%s draws two and is skipped!',
    'CARDS': 'Cards: %s',
    'WD4': '%s draws four and is skipped!',
    'SKIPPED': '%s is skipped!',
    'REVERSED': 'Order reversed!',
    'GAINS': '%s gains %s points!',
    'SCORE_ROW': '#%s %s (%s points, %s games, %s won, %.2f points per game, %.2f percent wins)',
    'GAME_ALREADY_DEALT': 'Game has already been dealt, please wait until game is over or stopped.',
    'PLAYER_COLOR_ENABLED': 'Hand card colors \x0303enabled!\x03 Format: <COLOR>/[<CARD>].  Example: R/[D2] is a red Draw Two. Type \'.uno-help\' for more help.',
    'PLAYER_COLOR_DISABLED': 'Hand card colors \x0304disabled.',
    'DISABLED_PCE': 'Hand card colors is \x0304disabled\x03 for %s. To enable, \'.pce-on\'',
    'ENABLED_PCE': 'Hand card colors is \x0303enabled\x03 for %s. To disable, \'.pce-off\'',
    'PCE_CLEARED': 'All players\' hand card color setting is reset by %s.',
    'PLAYER_LEAVES': 'Player %s has left the game.',
    'OWNER_CHANGE': 'Owner %s has left the game. New owner is %s.',
    'UNOBOT_PLAYED': '%s plays %s\x03!',
}

class UnoBot:
    def __init__(self):
        self.colored_card_nums = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'R', 'S', 'D2']
        self.special_scores = {'R' : 20, 'S' : 20, 'D2' : 20, 'W' : 50, 'WD4' : 50}
        self.colors = 'RGBY'
        self.special_cards = ['W', 'WD4']
        self.players = dict()
        self.owners = dict()
        self.players_pce = dict()  # Player color enabled hash table
        self.playerOrder = list()
        self.game_on = False
        self.currentPlayer = 0
        self.topCard = None
        self.way = 1
        self.drawn = False
        self.scoreFile = SCOREFILE
        self.deck = list()
        self.prescores = list()
        self.dealt = False
        self.lastActive = datetime.now()
        self.timeout = timedelta(minutes=INACTIVE_TIMEOUT)

    def start(self, phenny, owner):
        owner = owner.lower()
        if self.game_on:
            phenny.msg(CHANNEL, STRINGS['ALREADY_STARTED'] % self.game_on)
        else:
            self.lastActive = datetime.now()
            self.game_on = owner
            self.deck = list()
            phenny.msg(CHANNEL, STRINGS['GAME_STARTED'] % owner)
            self.players = dict()
            self.players[owner] = list()
            self.playerOrder = [owner]
            if self.players_pce.get(owner, 0):
                phenny.notice(owner, STRINGS['ENABLED_PCE'] % owner)

    def stop(self, phenny, input):
        nickk = (input.nick).lower()
        tmptime = datetime.now()
        if nickk == self.game_on or tmptime - self.lastActive > self.timeout:
            phenny.msg(CHANNEL, STRINGS['GAME_STOPPED'])
            self.game_on = False
            self.dealt = False
        elif self.game_on:
            phenny.msg(CHANNEL, STRINGS['CANT_STOP'] % (self.game_on, self.timeout.seconds - (tmptime - self.lastActive).seconds))

    def join_uno(self, phenny, input, player='human'):
        if player == 'bot':
            nickk = phenny.nick
        else:
            nickk = (input.nick).lower()
        if self.game_on:
            if not self.dealt:
                if nickk not in self.players:
                    self.players[nickk] = list()
                    self.playerOrder.append(nickk)
                    self.lastActive = datetime.now()
                    if self.players_pce.get(nickk, 0):
                        phenny.notice(nickk, STRINGS['ENABLED_PCE'] % nickk)
                    if self.deck:
                        for i in xrange(0, 7):
                            self.players[nickk].append(self.getCard(phenny))
                        phenny.msg(CHANNEL, STRINGS['DEALING_IN'] % (nickk, self.playerOrder.index(nickk) + 1))
                    else:
                        phenny.msg(CHANNEL, STRINGS['JOINED'] % (nickk, self.playerOrder.index(nickk) + 1))
                        if len(self.players) == 2 and phenny.nick not in self.players:
                            phenny.msg(CHANNEL, STRINGS['ENOUGH'])
                else:
                    phenny.msg(CHANNEL, STRINGS['ALREADY_JOINED'] % nickk)
            else:
                phenny.msg(CHANNEL, STRINGS['GAME_ALREADY_DEALT'])
        else:
            phenny.msg(CHANNEL, STRINGS['NOT_STARTED'])

    def deal(self, phenny, input):
        botOn = False
        nickk = (input.nick).lower()
        if not self.game_on:
            phenny.msg(CHANNEL, STRINGS['NOT_STARTED'])
            return
        if nickk != self.game_on:
            phenny.msg(CHANNEL, STRINGS['NEEDS_TO_DEAL'] % self.game_on)
            return
        if len(self.deck):
            phenny.msg(CHANNEL, STRINGS['ALREADY_DEALT'])
            return
        if len(self.players) < 2:
            self.join_uno(phenny, input, 'bot')
            botOn = True
        self.startTime = datetime.now()
        self.lastActive = datetime.now()
        self.deck = self.createnewdeck()
        for i in xrange(0, 7):
            for p in self.players:
                self.players[p].append(self.getCard(phenny))
        self.topCard = self.getCard(phenny)
        # Make sure the starting top card is not wild
        while self.topCard in ['W', 'WD4']:
            self.deck.append(self.topCard)
            random.shuffle(self.deck)
            self.topCard = self.getCard(phenny)
        end_index = len(self.players.keys()) - 1
        # Notice everyone their cards to start (unless bot is on)
        if botOn is False:
            for player in range(0, end_index):
                phenny.notice(self.playerOrder[player], STRINGS['YOUR_CARDS'] % self.renderCards(self.playerOrder[player], self.players[self.playerOrder[player]], 0))
        # Randomize the starting player by finding a valid random index to be called by self.playerOrder list
        self.currentPlayer = random.randint(0, end_index)
        self.cardPlayed(phenny, self.topCard)
        self.showOnTurn(phenny, input)
        self.dealt = True

    def play(self, phenny, input):
        pl = self.currentPlayer
        nickk = (input.nick).lower()
        if not self.game_on or not self.deck:
            return
        if nickk != self.playerOrder[self.currentPlayer]:
            phenny.msg(CHANNEL, STRINGS['ON_TURN'] % self.playerOrder[self.currentPlayer])
            return
        # card_command = str(input).upper().split(' ', 1)
        # card = card_command[1]
        # card_color = re.match('\w', card).group()
        # card_digit = re.match('(\w)(\s)\d', card).group()
        # phenny.say(card_digit)
        # raw_card_list = [z.strip() for z in re.split('(\d.*)', card)]
        # tok = filter(None, raw_card_list)
        tok = [z.strip() for z in str(input).upper().split(' ')]
        # phenny.say(str(tok))
        # if len(tok) != 2:
        if len(tok) != 3:
            return
        searchcard = str()
        if tok[1] in self.special_cards and tok[2] in self.colors:
            searchcard = tok[1]
        elif tok[1] in self.colors:
            searchcard = (tok[1] + tok[2])
        else:
            phenny.msg(CHANNEL, STRINGS['INVALID_CHOICE'] % self.playerOrder[pl])
            return
        if searchcard not in self.players[self.playerOrder[pl]]:
            phenny.msg(CHANNEL, STRINGS['DONT_HAVE'] % self.playerOrder[pl])
            return
        playcard = (tok[1] + tok[2])
        if not self.cardPlayable(playcard):
            phenny.msg(CHANNEL, STRINGS['DOESNT_PLAY'])
            return

        self.drawn = False
        self.players[self.playerOrder[self.currentPlayer]].remove(searchcard)

        self.incPlayer()
        self.cardPlayed(phenny, playcard)

        if len(self.players[self.playerOrder[pl]]) == 1:
            phenny.msg(CHANNEL, STRINGS['UNO'] % self.playerOrder[pl])
        elif len(self.players[self.playerOrder[pl]]) == 0:
            phenny.msg(CHANNEL, STRINGS['WIN'] % (self.playerOrder[pl], (datetime.now() - self.startTime)))
            self.gameEnded(phenny, self.playerOrder[pl])
            return

        self.lastActive = datetime.now()
        self.showOnTurn(phenny, input)

    def draw(self, phenny, input):
        nickk = (input.nick).lower()
        if not self.game_on or not self.deck:
            return
        if nickk != self.playerOrder[self.currentPlayer]:
            phenny.msg(CHANNEL, STRINGS['ON_TURN'] % self.playerOrder[self.currentPlayer])
            return
        if self.drawn:
            phenny.msg(CHANNEL, STRINGS['DRAWN_ALREADY'])
            return
        self.drawn = True
        phenny.msg(CHANNEL, STRINGS['DRAWS'] % self.playerOrder[self.currentPlayer])
        c = self.getCard(phenny)
        self.players[self.playerOrder[self.currentPlayer]].append(c)
        self.lastActive = datetime.now()
        phenny.notice(nickk, STRINGS['DRAWN_CARD'] % self.renderCards (nickk, [c], 0))

    # this is not a typo, avoiding collision with Python's pass keyword
    def passs(self, phenny, input):
        nickk = (input.nick).lower()
        if not self.game_on or not self.deck:
            return
        if nickk != self.playerOrder[self.currentPlayer]:
            phenny.msg(CHANNEL, STRINGS['ON_TURN'] % self.playerOrder[self.currentPlayer])
            return
        if not self.drawn:
            phenny.msg(CHANNEL, STRINGS['DRAW_FIRST'] % self.playerOrder[self.currentPlayer])
            return
        self.drawn = False
        phenny.msg(CHANNEL, STRINGS['PASSED'] % self.playerOrder[self.currentPlayer])
        self.incPlayer()
        self.lastActive = datetime.now()
        self.showOnTurn(phenny, input)

    def top10(self, phenny, input):
        nickk = (input.nick).lower()
        self.rankings("ppg")
        i = 1
        for z in self.prescores[:10]:
            if self.game_on or self.deck:
                phenny.msg(nickk, STRINGS['SCORE_ROW'] % (i, z[0], z[3], z[1], z[2], float(z[3])/float(z[1]), float(z[2])/float(z[1])*100))
            else:
                phenny.msg(nickk, STRINGS['SCORE_ROW'] % (i, z[0], z[3], z[1], z[2], float(z[3])/float(z[1]), float(z[2])/float(z[1])*100))
            i += 1

    def createnewdeck(self):
        ret = list()
        for a in self.colored_card_nums:
            for b in self.colors:
                ret.append(b + a)
        for a in self.special_cards:
            ret.append(a)
            ret.append(a)

        if len(self.playerOrder) <= 4:
            ret *= 2
            random.shuffle(ret)
        elif len(self.playerOrder) > 4:
            ret *= 3
            random.shuffle(ret)
        elif len(self.playerOrder) > 6:
            ret *= 4
            random.shuffle(ret)

        random.shuffle(ret)
        return ret

    def getCard(self, phenny):
        ret = self.deck[0]
        self.deck.pop(0)
        if not self.deck:
            phenny.say('Reshuffling deck...')
            self.deck = self.createnewdeck()
        return ret

    def showOnTurn(self, phenny, input=input):
        phenny.msg(CHANNEL, STRINGS['TOP_CARD'] % (self.playerOrder[self.currentPlayer], self.renderCards(None, [self.topCard], 1)))
        phenny.notice(self.playerOrder[self.currentPlayer], STRINGS['YOUR_CARDS'] % self.renderCards(self.playerOrder[self.currentPlayer], self.players[self.playerOrder[self.currentPlayer]], 0))
        msg = STRINGS['NEXT_START']
        tmp = self.currentPlayer + self.way
        if tmp == len(self.players):
            tmp = 0
        if tmp < 0:
            tmp = len(self.players) - 1
        arr = list()
        while tmp != self.currentPlayer:
            arr.append(STRINGS['NEXT_PLAYER'] % (self.playerOrder[tmp], len(self.players[self.playerOrder[tmp]])))
            tmp = tmp + self.way
            if tmp == len(self.players):
                tmp = 0
            if tmp < 0:
                tmp = len(self.players) - 1
        msg += ' - '.join(arr)
        phenny.notice(self.playerOrder[self.currentPlayer], msg)

        # Check to see if it's the unobot's turn to play
        try:
            if self.playerOrder[self.currentPlayer] == phenny.nick.lower():
                self.robotPlay(phenny)
        except: pass # Not bot's turn

    def robotPlay(self, phenny):
        nickk = phenny.nick.lower()
        numbers = [] # List of card numbers (or 'D2', 'S', and 'R')
        self.drawn = False
        card_chosen = False

        # Set up loop in case bot needs to draw and try again (break when variable is set)
        while card_chosen is False:
            blues = []
            greens = []
            reds = []
            yellows = []
            wilds = []
            colors = []
            card_list = self.players[nickk]
            for card in card_list:
                color = card[0]
                digits = card[1:]
                if color is not "W":
                    if color == "B":
                        blues.append(card)
                    if color == "G":
                        greens.append(card)
                    if color == "R":
                        reds.append(card)
                    if color == "Y":
                        yellows.append(card)
                    numbers.append(digits)
                    if color not in colors:
                        colors.append(color)
                elif color == "W":
                    wilds.append(card)

            tc_color = self.topCard[0]
            tc_number = self.topCard[1:]
            color_matches = False
            number_matches = False
            if tc_color in colors:
                color_matches = True
            if tc_number in numbers:
                number_matches = True
            # Function to select only the needed color list of cards
            search_list = self.whichColors(blues, greens, reds, yellows, tc_color)
            
            # print card_list
            # print "Matching color list of numbers in hand: ", search_list

            # Determine how to play next card
            # (if top card matches both a color or number held in hand)
            if color_matches == True and number_matches == True:
                print "Color match: ", color_matches, "/ Number match: ", number_matches
                # Coin flip to decide whether to play by card color or number (weighted 60/40 to number)
                coin_flip = random.random()
                if coin_flip < 0.6: # Play by number
                    print "Coin flip: play by number"
                    for card in card_list:
                        if card[1:] == tc_number:
                            playcard = card
                            self.drawn = False
                            break
                    break
                else: # Play by color
                    print "Coin flip: play by color"
                    playcard = self.chooseHighestColorCard(phenny, search_list)
                    self.drawn = False
                    break
            elif color_matches == True and number_matches == False:
                print "Color match: ", color_matches, "/ Number match: ", number_matches
                playcard = self.chooseHighestColorCard(phenny, search_list)
                self.drawn = False
                break
            elif color_matches == False and number_matches == True:
                print "Color match: ", color_matches, "/ Number match: ", number_matches
                for card in card_list:
                    if str(card[1:]) == str(tc_number):
                        playcard = card
                        self.drawn = False
                        break
                break
            else: # Nothing matches; draw
                if wilds:
                    color_list = []
                    if reds:
                        color_list.append('R')
                    if blues:
                        color_list.append('B')
                    if greens:
                        color_list.append('G')
                    if yellows:
                        color_list.append('Y')
                    if color_list is None:
                        color_list = ['R', 'B', 'G', 'Y']
                    wild_color = random.choice(color_list)
                    print "wild color choice: " + str(wild_color)
                    playcard = random.choice(wilds)
                    self.drawn = False
                    break
                elif self.drawn is True:
                    print "No matching card drawn, passing..."
                    break
                elif self.drawn is False:
                    print "Color match: ", color_matches, "/ Number match: ", number_matches
                    c = self.getCard(phenny)
                    print "Drawing card... ", c
                    self.players[self.playerOrder[self.currentPlayer]].append(c)
                    self.lastActive = datetime.now()
                    phenny.say(STRINGS['DRAWS'] % nickk)
                    self.drawn = True


        if self.drawn is False:
            self.players[self.playerOrder[self.currentPlayer]].remove(playcard)
            if playcard[0] == 'W':
                playcard = playcard + wild_color
            phenny.say(STRINGS['UNOBOT_PLAYED'] % (nickk, self.renderCards(None, playcard, 1)))
            # Check if unobot has uno or won
            if len(self.players[self.playerOrder[self.currentPlayer]]) == 1:
                phenny.msg(CHANNEL, STRINGS['UNO'] % self.playerOrder[self.currentPlayer])
            elif len(self.players[self.playerOrder[self.currentPlayer]]) == 0:
                phenny.msg(CHANNEL, STRINGS['WIN'] % (self.playerOrder[self.currentPlayer], (datetime.now() - self.startTime)))
                self.gameEnded(phenny, self.playerOrder[self.currentPlayer])
                return
            self.incPlayer()
            self.cardPlayed(phenny, playcard)
        elif self.drawn is True:
            self.incPlayer()
            phenny.say('%s passes to %s.' % (nickk, self.playerOrder[self.currentPlayer]))
        self.drawn = False
        self.showOnTurn(phenny)

    def chooseHighestColorCard(self, phenny, color_list):
        '''Choose the highest digit card from a specific color suite, then wild if 
            doesn't exist, lastly draw'''
        card_list = sorted(color_list)
        index = -1
        # If no matching cards exist in hand, draw
        if len(card_list) == 0:
            c = self.getCard(phenny)
            self.players[self.playerOrder[self.currentPlayer]].append(c)
            self.lastActive = datetime.now()
            return
        # Search for highest number card in the list (iterates sorted list in reverse)
        for card in range(0, len(card_list)):
            last_card = card_list[index]
            last_card_number = last_card[1:]
            if last_card_number.isdigit():
                return last_card
                index += -1
        # If a card without a number exists in the list, then play a special card (returns last card in list)
        return random.choice(card_list)

    def whichColors(self, blues, greens, reds, yellows, tc_color):
        if tc_color == "B":
            return blues
        if tc_color == "G":
            return greens
        if tc_color == "R":
            return reds
        if tc_color == "Y":
            return yellows

    def showCards(self, phenny, user):
        user = user.lower()
        if not self.game_on or not self.deck:
            return
        msg = STRINGS['NEXT_START']
        tmp = self.currentPlayer + self.way
        if tmp == len(self.players):
            tmp = 0
        if tmp < 0:
            tmp = len(self.players) - 1
        arr = list()
        k = len(self.players)
        while k > 0:
            arr.append(STRINGS['NEXT_PLAYER'] % (self.playerOrder[tmp], len(self.players[self.playerOrder[tmp]])))
            tmp = tmp + self.way
            if tmp == len(self.players):
                tmp = 0
            if tmp < 0:
                tmp = len(self.players) - 1
            k-=1
        msg += ' - '.join(arr)
        if user not in self.players:
            phenny.notice(user, msg)
        else:
            phenny.notice(user, STRINGS['YOUR_CARDS'] % self.renderCards(user, self.players[user], 0))
            phenny.notice(user, msg)

    def renderCards(self, nick, cards, is_chan):
        nickk = nick
        if nick:
            nickk = (nick).lower()
        self.ret = list()
        
        def color_processor(c):
            t = '\x03'
            if c[0] == 'W':
                t += '15,01'
            elif c[0] == 'B':
                t += '00,02'
            elif c[0] == 'Y':
                t += '01,08'
            elif c[0] == 'G':
                t += '00,03'
            elif c[0] == 'R':
                t += '00,04'
            if not is_chan:
                if self.players_pce.get(nickk, 0):
                    t += '%s/[%s]  ' % (c[0], c[1:])
                else:
                    t += '[%s%s]' % (c[0], c[1:])
            else:
                t += '[%s%s]' % (c[0], c[1:])
            t += ""
            self.ret.append(t)

        if isinstance(cards, list):
            for card in sorted(cards):
                color_processor(card)
        else:
            card = cards
            color_processor(card)
        
        return ''.join(self.ret)

    def cardPlayable(self, card):
        if card[0] == 'W' and card[-1] in self.colors:
            return True
        if self.topCard[0] == 'W':
            return card[0] == self.topCard[-1]
        return (card[0] == self.topCard[0]) or (card[1] == self.topCard[1])

    def cardPlayed(self, phenny, card):
        if card[1:] == 'D2':
            phenny.msg(CHANNEL, STRINGS['D2'] % self.playerOrder[self.currentPlayer])
            z = [self.getCard(phenny), self.getCard(phenny)]
            phenny.notice(self.playerOrder[self.currentPlayer], STRINGS['CARDS'] % self.renderCards(self.playerOrder[self.currentPlayer], z, 0))
            self.players[self.playerOrder[self.currentPlayer]].extend(z)
            self.incPlayer()
        elif card[:2] == 'WD':
            phenny.msg(CHANNEL, STRINGS['WD4'] % self.playerOrder[self.currentPlayer])
            z = [self.getCard(phenny), self.getCard(phenny), self.getCard(phenny), self.getCard(phenny)]
            phenny.notice(self.playerOrder[self.currentPlayer], STRINGS['CARDS'] % self.renderCards(self.playerOrder[self.currentPlayer], z, 0))
            self.players[self.playerOrder[self.currentPlayer]].extend(z)
            self.incPlayer()
        elif card[1] == 'S':
            phenny.msg(CHANNEL, STRINGS['SKIPPED'] % self.playerOrder[self.currentPlayer])
            self.incPlayer()
        elif card[1] == 'R' and card[0] != 'W':
            phenny.msg(CHANNEL, STRINGS['REVERSED'])
            if len(self.players) > 2:
                self.way = -self.way
                self.incPlayer()
                self.incPlayer()
            else:
                self.incPlayer()

        if card[0] == 'W':
            new_card = str(card[-1]) + '*'
            card = new_card
        self.topCard = card

    def gameEnded(self, phenny, winner):
        try:
            score = 0
            for player_nick, cards in self.players.iteritems():               
                for card in cards:
                    if card[0] == 'W':
                        score += self.special_scores[card]
                    elif card[1] in [ 'S', 'R', 'D' ]:
                        score += self.special_scores[card[1:]]
                    else:
                        score += int(card[1])
                if cards:
                    phenny.msg(CHANNEL, '%s held: %s' % (player_nick, self.renderCards(player_nick, cards, 1)))
            phenny.msg(CHANNEL, STRINGS['GAINS'] % (winner, score))
            self.saveScores(self.players.keys(), winner, score, (datetime.now() - self.startTime).seconds)
        except Exception, e:
            print 'Score error: %s' % e            
        self.players = dict()
        self.playerOrder = list()
        self.game_on = False
        self.currentPlayer = 0
        self.topCard = None
        self.way = 1
        self.dealt = False


    def incPlayer(self):
        self.currentPlayer = self.currentPlayer + self.way
        if self.currentPlayer == len(self.players):
            self.currentPlayer = 0
        if self.currentPlayer < 0:
            self.currentPlayer = len(self.players) - 1

    def saveScores(self, players, winner, score, time):
        from copy import copy
        prescores = dict()
        try:
            f = open(self.scoreFile, 'r')
            for l in f:
                t = l.replace('\n', '').split(' ')
                if len (t) < 4: continue
                if len (t) == 4: t.append(0)
                prescores[t[0]] = [t[0], int(t[1]), int(t[2]), int(t[3]), int(t[4])]
            f.close()
        except: pass
        for p in players:
            p = p.lower()
            if p not in prescores:
                prescores[p] = [ p, 0, 0, 0, 0 ]
            prescores[p][1] += 1
            prescores[p][4] += time
        prescores[winner][2] += 1
        prescores[winner][3] += score
        try:
            f = open(self.scoreFile, 'w')
            for p in prescores:
                f.write(' '.join ([str(s) for s in prescores[p]]) + '\n')
            f.close()
        except Exception, e:
            print 'Failed to write score file %s' % e

    # Custom added functions ============================================== #
    def rankings(self, rank_type):
        from copy import copy
        self.prescores = list()
        try:
            f = open(self.scoreFile, 'r')
            for l in f:
                t = l.replace('\n', '').split(' ')
                if len(t) < 4: continue
                self.prescores.append(copy (t))
                if len(t) == 4: t.append(0)
            f.close()
        except: pass
        if rank_type == "ppg":
            self.prescores = sorted(self.prescores, lambda x, y: cmp((y[1] != '0') and (float(y[3]) / int(y[1])) or 0, (x[1] != '0') and (float(x[3]) / int(x[1])) or 0))
        elif rank_type == "pw":
            self.prescores = sorted(self.prescores, lambda x, y: cmp((y[1] != '0') and (float(y[2]) / int(y[1])) or 0, (x[1] != '0') and (float(x[2]) / int(x[1])) or 0))

    def showTopCard_demand(self, phenny):
        if not self.game_on or not self.deck:
            return
        phenny.reply(STRINGS['TOP_CARD'] % (self.playerOrder[self.currentPlayer], self.renderCards(None, [self.topCard], 1)))

    def leave(self, phenny, input):
        nickk = (input.nick).lower()
        self.remove_player(phenny, nickk)

    def remove_player(self, phenny, nick):
        if not self.game_on:
            return

        user = self.players.get(nick, None)
        if user is not None:
            numPlayers = len(self.playerOrder)

            self.playerOrder.remove(nick)
            del self.players[nick]

            if self.way == 1 and self.currentPlayer == numPlayers - 1:
                self.currentPlayer = 0
            elif self.way == -1:
                if self.currentPlayer == 0:
                    self.currentPlayer = numPlayers - 2
                else:
                    self.currentPlayer -= 1

            phenny.msg(CHANNEL, STRINGS['PLAYER_LEAVES'] % nick)
            if numPlayers == 2 and self.dealt or numPlayers == 1:
                phenny.msg(CHANNEL, STRINGS['GAME_STOPPED'])
                self.game_on = None
                self.dealt = None
                return

            if self.game_on == nick:
                self.game_on = self.playerOrder[0]
                phenny.msg(CHANNEL, STRINGS['OWNER_CHANGE'] % (nick, self.playerOrder[0]))

            if self.dealt:
                phenny.msg(CHANNEL, STRINGS['TOP_CARD'] % (self.playerOrder[self.currentPlayer], self.renderCards(None, [self.topCard], 1)))

    def enablePCE(self, phenny, nick):
        nickk = nick.lower()
        if not self.players_pce.get(nickk, 0):
            self.players_pce.update({ nickk : 1})
            phenny.notice(nickk, STRINGS['PLAYER_COLOR_ENABLED'])
        else:
            phenny.notice(nickk, STRINGS['ENABLED_PCE'] % nickk)

    def disablePCE(self, phenny, nick):
        nickk = nick.lower()
        if self.players_pce.get(nickk, 0):
            self.players_pce.update({ nickk : 0})
            phenny.notice(nickk, STRINGS['PLAYER_COLOR_DISABLED'])
        else:
            phenny.notice(nickk, STRINGS['DISABLED_PCE'] % nickk)

    def isPCEEnabled(self, phenny, nick):
        nickk = nick.lower()
        if not self.players_pce.get(nickk, 0):
            phenny.notice(nickk, STRINGS['DISABLED_PCE'] % nickk)
        else:
            phenny.notice(nickk, STRINGS['ENABLED_PCE'] % nickk)

    def PCEClear(self, phenny, nick):
        nickk = nick.lower()
        if not self.owners.get(nickk, 0):
            self.players_pce.clear()
            phenny.msg(CHANNEL, STRINGS['PCE_CLEARED'] % nickk)

    def unostat(self, phenny, input):
        text = input.group().lower().split()

        if len(text) != 3:
            phenny.say("Invalid input for stats command. Try '.unostats ppg 10' to show the top 10 ranked by points per game. You can also show rankings by percent-wins 'pw'.")
            return

        if text[1] == "pw" or text[1] == "ppg":
            self.rankings(text[1])
            self.rank_assist(phenny, input, text[2], "SCORE_ROW")

        if not self.prescores:
            phenny.say(STRINGS['NO_SCORES'])

    def rank_assist(self, phenny, input, nicknum, ranktype):
        nickk = (input.nick).lower()
        if nicknum.isdigit():
            i = 1
            s = int(nicknum)
            for z in self.prescores[:s]:
                phenny.msg(nickk, STRINGS[ranktype] % (i, z[0], z[3], z[1], z[2], float(z[3])/float(z[1]), float(z[2])/float(z[1])*100))
                i += 1
        else:
            j = 1
            t = str(nicknum)
            for y in self.prescores:
                if y[0] == t:
                    phenny.say(STRINGS[ranktype] % (j, y[0], y[3], y[1], y[2], float(y[3])/float(y[1]), float(y[2])/float(y[1])*100))
                j += 1

unobot = UnoBot ()

def uno(phenny, input):
    unobot.start(phenny, input.nick)
uno.commands = ['uno', 'unostart']
uno.priority = 'low'
uno.thread = False
uno.rate = 0

def unostop(phenny, input):
    unobot.stop(phenny, input)
unostop.commands = ['unostop']
unostop.priority = 'low'
unostop.thread = False
unostop.rate = 0

def join_uno(phenny, input):
    unobot.join_uno(phenny, input)
join_uno.rule = '^(.juno|.ju)$'
join_uno.priority = 'low'
join_uno.thread = False
join_uno.rate = 0

def deal(phenny, input):
    unobot.deal(phenny, input)
deal.commands = ['deal']
deal.priority = 'low'
deal.thread = False
deal.rate = 0

def play(phenny, input):
    unobot.play(phenny, input)
play.commands = ['play', 'p', 'pl']
play.priority = 'low'
play.thread = False
play.rate = 0

def draw(phenny, input):
    unobot.draw(phenny, input)
draw.commands = ['draw', 'd', 'dr']
draw.priority = 'low'
draw.thread = False
draw.rate = 0

def passs(phenny, input):
    unobot.passs(phenny, input)
passs.commands = ['pass', 'pa']
passs.priority = 'low'
passs.thread = False
passs.rate = 0

def unotop10(phenny, input):
    unobot.top10(phenny, input)
unotop10.commands = ['unotop10']
unotop10.priority = 'low'
unotop10.thread = False
unotop10.rate = 0

def show_user_cards(phenny, input):
    unobot.showCards(phenny, input.nick)
show_user_cards.commands = ['cards', 'ca']
show_user_cards.priority = 'low'
show_user_cards.thread = False
show_user_cards.rate = 0

def top_card(phenny, input):
    unobot.showTopCard_demand(phenny)
top_card.commands = ['top']
top_card.priority = 'low'
top_card.thread = False
top_card.rate = 0

def leave(phenny, input):
    unobot.leave(phenny, input)
leave.commands = ['leave']
leave.priority = 'low'
leave.thread = False
leave.rate = 0

def remove_on_part(phenny, input):
    unobot.remove_player(phenny, input.nick)
remove_on_part.event = 'PART'
remove_on_part.rule = '.*'
remove_on_part.priority = 'low'
remove_on_part.thread = False
remove_on_part.rate = 0

def remove_on_quit(phenny, input):
    unobot.remove_player(phenny, input.nick)
remove_on_quit.event = 'QUIT'
remove_on_quit.rule = '.*'
remove_on_quit.priority = 'low'
remove_on_quit.thread = False
remove_on_quit.rate = 0

def remove_on_kick(phenny, input):
    unobot.remove_player(phenny, input.nick)
remove_on_kick.event = 'KICK'
remove_on_kick.rule = '.*'
remove_on_kick.priority = 'low'
remove_on_kick.thread = False
remove_on_kick.rate = 0

def remove_on_nickchg(phenny, input):
    unobot.remove_player(phenny, input.nick)
remove_on_nickchg.event = 'NICK'
remove_on_nickchg.rule = '.*'
remove_on_nickchg.priority = 'low'
remove_on_nickchg.thread = False
remove_on_nickchg.rate = 0

def unostats(phenny, input):
    unobot.unostat(phenny, input)
unostats.commands = ['unostats']
unostats.priority = 'low'
unostats.thread = False
unostats.rate = 0

def uno_help(phenny, input):
    phenny.reply("For rules, examples, and getting started: http://j.mp/esl47K")
uno_help.commands = ['uno-help']
uno_help.priority = 'low'
uno_help.thread = False
uno_help.rate = 0

def uno_pce_on(phenny, input):
    unobot.enablePCE(phenny, input.nick)
uno_pce_on.commands = ['pce-on']
uno_pce_on.priority = 'low'
uno_pce_on.thread = False
uno_pce_on.rate = 0

def uno_pce_off(phenny, input):
    unobot.disablePCE(phenny, input.nick)
uno_pce_off.commands = ['pce-off']
uno_pce_off.priority = 'low'
uno_pce_off.thread = False
uno_pce_off.rate = 0

def uno_ispce(phenny, input):
    unobot.isPCEEnabled(phenny, input.nick)
uno_ispce.commands = ['pce']
uno_ispce.priority = 'low'
uno_ispce.thread = False
uno_ispce.rate = 0

def uno_pce_clear(phenny, input):
    unobot.PCEClear(phenny, input.nick)
uno_pce_clear.commands = ['.pce-clear']
uno_pce_clear.priority = 'low'
uno_pce_clear.thread = False
uno_pce_clear.rate = 0

if __name__ == '__main__':
    print __doc__.strip()