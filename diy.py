# -*- coding: utf-8 -*-
"""
Created on Sat Nov 10 12:20:38 2018

@author: admin
"""
#%%
#-*- coding:utf-8 -*-

import curses
from random import randrange, choice # generate and place new tile
from collections import defaultdict
#%%
letter_codes = [ord(ch) for ch in 'WASDRQwasdrq']
actions = ['Up', 'Left', 'Down', 'Right', 'Restart', 'Exit']
actions_dict = dict(zip(letter_codes, actions*2))

def get_user_action(keyboard):
    char = 'N'
    while char not in letter_codes:
        char = keyboard.getch()
    return actions_dict[char]
def transpose(field):
   return [list(row) for row in zip(*field)]

def invert(field):
   return [row[::-1] for row in field]
#%%
class GameField(object):
    def __init__(self, height=4, width=4, win=2048):
        self.height = height
        self.width = width
        self.win_value = win
        self.score = 0
        self.highscore = 0
        self.reset()

    def reset(self):
       if self.score > self.highscore:
            self.highscore = self.score
       self.score = 0
       self.field = [[0 for _ in range(self.width)] for _ in range(self.height)]
       self.spawn()
       self.spawn()
        
    def move(self, direction):
        def move_row_left(row):
            def tighten(row): # squeese non-zero elements together
              new_row = [i for i in row if i != 0]
              new_row += [0 for _ in range(len(row)- len(new_row))]
              return new_row
          
            def merge(row):
                new_row = []
                pair = False
                for i in range(len(row)):
                    if pair:
                        new_row.append(2 * row[i])
                        pair = False
                    else:
                        if i < len(row) - 1 and row[i] == row[i+1]:
                            new_row.append(0)
                            pair = True
                        else:
                            new_row.append(row[i])
                    return new_row 
                return tighten(merge(row))
        moves = {}
        moves['Left'] = lambda field: [move_row_left(row) for row in self.field]
        moves['Right'] = lambda field: [move_row_left(row[::-1])[::-1] for row in self.field]
        moves['Up'] = lambda field: transpose([move_row_left(row) for row in transpose(self.field)])
        moves['Down'] = lambda field: transpose([move_row_left(row[::-1])[::-1] for row in transpose(self.field)])
        
        
        return moves[direction]

        

    def is_win(self):
        return any(any(i >= self.win_value for i in row) for row in self.field)
        
    def is_gameover(self):
        return not any(self.move_is_posseble(move) for move in actions)

    def draw(self, screen):
        help_string1 = '(W)Up (S)Down (A)Left (D)Right'
        help_string2 = '     (R)Restart (Q)Exit'
        gameover_string = '           GAME OVER'
        win_string = '          YOU WIN!'
        def cast(string):
            screen.addstr(string + '\n')
        def draw_hor_separator():
            line = '+------' * self.width + '+'
            cast(line)

        def draw_row(row):
            cast(''.join('|{:^5d} '.format(num) if num > 0 else '|      ' for num in row) + '|')

        screen.clear()


    def spawn(self):
        new_element = 4 if randrange(100) > 89 else 2
        (i, j) = choice([(i, j) for i in range(self.height) for j in range(self.width) if self.field[i][j] == 0])
        self.field[i][j] = new_element
        
    def move_is_possible(self, direction):
        def row_is_left_movable(row):
            def change(i):
                if row[i] == 0 and row[i+1] != 0:
                    return True
                if row[i] != 0 and row[i+1] == row[i]:
                    return True
                return False
            return any(change(i) for i in range(self.width-1))
            
        check = {}
        check['Left']  = lambda field:                              \
                any(row_is_left_movable(row) for row in field)

        check['Right'] = lambda field:                              \
                 check['Left'](invert(field))

        check['Up']    = lambda field:                              \
                check['Left'](transpose(field))

        check['Down']  = lambda field:                              \
                check['Right'](transpose(field))

        if direction in check:
            return check[direction](self.field)
        else:
            return False

#%%
def main(stdscr):
    def init():
        #重置游戏棋盘
        game_field.reset()
        return 'Game'

    def not_game(state):
        #画出 GameOver 或者 Win 的界面
        game_field.draw(stdscr)
        #读取用户输入得到action，判断是重启游戏还是结束游戏
        action = get_user_action(stdscr)
        responses = defaultdict(lambda: state) #默认是当前状态，没有行为就会一直在当前界面循环
        responses['Restart'], responses['Exit'] = 'Init', 'Exit' #对应不同的行为转换到不同的状态
        return responses[action]

    def game():
        #画出当前棋盘状态
        game_field.draw(stdscr)
        #读取用户输入得到action
        action = get_user_action(stdscr)

        if action == 'Restart':
            return 'Init'
        if action == 'Exit':
            return 'Exit'
        if game_field.move(action): # move successful
            if game_field.is_win():
                return 'Win'
            if game_field.is_gameover():
                return 'Gameover'
        return 'Game'


    state_actions = {
            'Init': init,
            'Win': lambda: not_game('Win'),
            'Gameover': lambda: not_game('Gameover'),
            'Game': game
        }

    curses.use_default_colors()

    # 设置终结状态最大数值为 2048
    game_field = GameField(win=2048)


    state = 'Init'

    #状态机开始循环
    while state != 'Exit':
        state = state_actions[state]()

curses.wrapper(main)
