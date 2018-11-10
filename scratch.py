from collections import defaultdict
def main(srdscr):

    def init():
        return 'Game'

    def not_game(state):
        responses = defaultdict(lambda: state)
        responses['Restart'], responses['Exit']='Init', 'Exit'
        return responses[action]

    def game():

        if action == 'Restart':
            return 'Init'
        if action == 'Exit':
            return 'Exit'
        #if successfully execute one step:
            #if win:
                return 'Win'
            #if loose:
                return 'Gameover'
        return 'Game'

    state_actions = {
        'Init': init,
        'Win': lambda: not_game('Win'),
        'Gameover': lambda: not_game('Gameover')
        'Game': game
    }
    #状态机开始循环
    while state != 'Exit':
        state = state_actions[state]()

