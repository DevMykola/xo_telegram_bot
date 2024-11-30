import telebot
from telebot import types

import classes
from config import TOKEN, X, O

bot = telebot.TeleBot(TOKEN)
symbols = {'x': X, 'o': O}

games = {}

@bot.message_handler(commands=['xo'])
def xo(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton('X', callback_data='select:x'),
        types.InlineKeyboardButton('O', callback_data='select:o'),
    )
    bot.reply_to(message, 'X чи O', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('select:'))
def game_starts(call):
    game = str(call.message.message_id) + '|' + str(call.message.chat.id)
    games[game] = {}
    games[game]['walks'] = 'x'

    if call.data == 'select:x':
        games[game]['x'] = call.from_user.id
        games[game]['o'] = 0
        message_text = f'{symbols["x"]} {call.from_user.first_name} ходить'
        list = [str(i) for i in range(1, 10)]
        games[game]['field'] = list
        markup = classes.XO.field(list)
            
    if call.data == 'select:o':
        games[game]['o'] = call.from_user.id
        message_text = f'{symbols["o"]} {call.from_user.first_name} очікує суперника'
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('X', callback_data='to_join'))
        
    bot.edit_message_text(message_text, call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'to_join')
def join_to_game(call):
    game = str(call.message.message_id) + '|' + str(call.message.chat.id)
    games[game]['x'] = call.from_user.id
    list = [str(i) for i in range(1, 10)]
    games[game]['field'] = list
    markup = classes.XO.field(list)
    message_text = (
        f'{symbols["x"]} {call.from_user.first_name}\n'
        f'🆚️\n{symbols["o"]} {bot.get_chat(games[game]["o"]).first_name}\n\n'
        f'{symbols["x"]} {call.from_user.first_name} ходить'
    )
    bot.edit_message_text(message_text, call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('walk:'))
def walk(call):
    game = str(call.message.message_id) + '|' + str(call.message.chat.id)

    if call.data.split(':')[1] in ['x', 'o']:
        return

    if games[game]['o'] == 0 and games[game]['walks'] == 'o':
        games[game]['o'] = call.from_user.id

    if call.from_user.id not in [games[game]['x'], games[game]['o']]:
        return bot.answer_callback_query(call.id, "Ти не є учасником цієї гри")
    
    if games[game]['walks'] == 'x' and games[game]['x'] == call.from_user.id:
        games[game]['field'][int(call.data.split(':')[1]) - 1] = 'x'
        
    elif games[game]['walks'] == 'o' and games[game]['o'] == call.from_user.id:
        games[game]['field'][int(call.data.split(':')[1]) - 1] = 'o'

    else:
        return bot.answer_callback_query(call.id, "Це не твій хід")
    
    if classes.XO.does_win(games[game]['field'], games[game]['walks']):
        lost = ['x', 'o']
        lost.remove(games[game]['walks'])
        results = classes.XO.get_results(games[game]['field'])
        text = (
            f'{symbols[games[game]["walks"]]}{bot.get_chat(call.from_user.id).first_name} 🏆\n'
            f'{symbols[lost[0]]}{bot.get_chat(games[game][lost[0]]).first_name}\n\n'
            f'{results}'
        )
        del games[game]
        markup = types.InlineKeyboardMarkup()
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("tg channel", callback_data=f"tgc"))
        return bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)
    
    if classes.XO.draw(games[game]['field']):
        results = classes.XO.get_results(games[game]['field'])
        text = (
            f'{symbols["x"]}{bot.get_chat(games[game]["x"]).first_name}\n'
            '🤝\n'
            f'{symbols["o"]}{bot.get_chat(games[game]["o"]).first_name}'
            '\n\n'
            f'{results}'
        )
        del games[game]
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("tg channel", callback_data=f"tgc"))
        return bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

    walks = ['x', 'o']
    walks.remove(games[game]['walks'])
    games[game]['walks'] = walks[0]

    if games[game]['o'] == 0 and games[game]['walks'] == 'o':
        text = (
            f'{symbols["x"]} {bot.get_chat(games[game]["x"]).first_name} очікує на суперника\n\n'
            f'{symbols[walks[0]]} ходить'
        )
    else:
        text = (
            f'{symbols["x"]} {bot.get_chat(games[game]["x"]).first_name}\n'
            f'🆚️\n{symbols["o"]} {bot.get_chat(games[game]["o"]).first_name}\n\n'
            f'{symbols[walks[0]]} {bot.get_chat(games[game][walks[0]]).first_name} ходить'
        )
    markup = classes.XO.field(games[game]['field'])
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

 
if __name__ == "__main__":
    while True:
        try:
            bot.polling(allowed_updates=['message', 'callback_query'], skip_pending=True)
        except Exception as e:
            print(e)
         
