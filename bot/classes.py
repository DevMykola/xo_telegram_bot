from telebot import types

from config import X as x_symbol
from config import O as o_symbol

class XO:

    def field(dict):
        markup = types.InlineKeyboardMarkup(row_width=3)
        count = 0
        button_list = []
        for i in dict:
            i = str(i)
            if i == 'x':
                text = x_symbol
            elif i == 'o':
                text = o_symbol
            else:
                text = 'ㅤ'
            button_list.append(types.InlineKeyboardButton(text, callback_data=f'walk:{i}'))
            count += 1
            if count == 3:
                count = 0
                markup.add(button_list[0], button_list[1], button_list[2],)
                button_list.clear()
        return markup

    def does_win(field, who_walks):
        results = [
            field[0] + field[1] + field[2],
            field[3] + field[4] + field[5],
            field[6] + field[7] + field[8],
            field[0] + field[3] + field[6],
            field[1] + field[4] + field[7],
            field[2] + field[5] + field[8],
            field[0] + field[4] + field[8],
            field[2] + field[4] + field[6],
        ]
        if who_walks*3 in results:
            return True
        
        return False
    
    def get_results(field):
        result_text = ''
        count = 0
        string = ''
        for i in field:
            if i not in ['x', 'o']:
                i = '⬜'
            string += i
            count += 1
            if count == 3:
                count = 0
                result_text += string + '\n'
                string = ''
        result_text = result_text.replace('x', x_symbol).replace('o', o_symbol)

        return result_text

    def draw(field):
        if field.count('x') + field.count('o') == 9:
            return True
        
        return False