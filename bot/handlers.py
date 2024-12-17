import traceback
import aiogram

from modules.Games import XO

from aiogram import F, types, Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from config import TOKEN, X, O

bot = Bot(token=TOKEN)
router = Router()

def field_markup(field):
    return types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text=field[k], callback_data=f'walk:{k}') for k in list(field.keys())[j:j+3]] for j in range(0, len(field.values()), 3)
    ])
    
def result_text(field):
    text = ''
    string = ''
    count = 0
    for i in field.values():
        string += i
        count += 1
        if count == 3:
            text += string + '\n'
            string = ''
            count = 0
    return text

@router.message(Command('xo'))
async def xo(message: Message) -> None:
    await message.answer(
        f'{X} чи {O}',
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[[
            types.InlineKeyboardButton(text=X, callback_data='select:x'),
            types.InlineKeyboardButton(text=O, callback_data='select:o')
        ]])
    )
    
@router.callback_query(lambda call: call.data.startswith('select:'))
async def game_starts(callback: CallbackQuery):
    game_id = str(callback.message.message_id) + '|' + str(callback.message.chat.id)
    xo = XO(game_id, x_symbol=X, o_symbol=O)

    if callback.data == 'select:x':
        xo.x_user_id_is(callback.from_user.id)
        return await bot.edit_message_text(
            text=f'{xo.symbols["x"]} {callback.from_user.first_name} ходить',
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            reply_markup=field_markup(xo.field())
        )

    if callback.data == 'select:o':
        xo.o_user_id_is(callback.from_user.id)
        return await bot.edit_message_text(
            text=f'{xo.symbols["o"]} {callback.from_user.first_name} очікує суперника',
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[[
                types.InlineKeyboardButton(text='X', callback_data='join')
            ]])
        )

@router.callback_query(lambda call: call.data.startswith('join'))
async def join_to_game(callback: CallbackQuery):
    game_id = str(callback.message.message_id) + '|' + str(callback.message.chat.id)
    xo = XO(game_id, x_symbol=X, o_symbol=O)
    xo.x_user_id_is(callback.from_user.id)
    o_user = await bot.get_chat(int(xo.o_user_id))
    message_text = (
        f'{xo.symbols["x"]} {callback.from_user.first_name}\n'
        f'🆚️\n{xo.symbols["o"]} {o_user.first_name}\n\n'
        f'{xo.symbols["x"]} {callback.from_user.first_name} ходить'
    )
    await bot.edit_message_text(
        message_text,
        chat_id=callback.message.chat.id, 
        message_id=callback.message.message_id, 
        reply_markup=field_markup(xo.field())
    )

@router.callback_query(lambda call: call.data.startswith('walk:'))
async def walk(callback: CallbackQuery):
    game_id = str(callback.message.message_id) + '|' + str(callback.message.chat.id)
    xo = XO(game_id, x_symbol=X, o_symbol=O)

    if xo.o_user_id == "None" and xo.who_walk() == 'o':
        xo.o_user_id_is(callback.from_user.id)

    if str(callback.from_user.id) not in [str(xo.o_user_id), str(xo.x_user_id)]:
        return await bot.answer_callback_query(callback.id, "Ти не є учасником цієї гри")
    
    if xo.who_walk() == 'x' and xo.x_user_id == callback.from_user.id:
        xo.make_move(callback.data.split(':')[1])
        
    elif xo.who_walk() == 'o' and xo.o_user_id == callback.from_user.id:
        xo.make_move(callback.data.split(':')[1]) 

    else:
        return await bot.answer_callback_query(callback.id, "Це не твій хід")
    
    if xo.does_win():
        win = ['x', 'o']
        win.remove(xo.who_walk())
        result = result_text(xo.field())
        result = result.replace('x', xo.symbols['x']).replace('o', xo.symbols['o']).replace('ㅤ', '⬜')
        win_user = await bot.get_chat(callback.from_user.id)
        lost_user = await bot.get_chat(int(xo.users[xo.who_walk()]))
        text = (
            f'{xo.symbols[win[0]]}{win_user.first_name} 🏆\n'
            f'{xo.symbols[xo.who_walk()]}{lost_user.first_name}\n\n'
            f'{result}'
        )
        xo.del_game()
        markup = types.InlineKeyboardMarkup(inline_keyboard=[[
            types.InlineKeyboardButton(text="tg channel", callback_data=f"tgc")
        ]])
        
        return await bot.edit_message_text(text, chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=markup)
    
    if xo.draw():
        result = result_text(xo.field())
        result = result.replace('x', xo.symbols['x']).replace('o', xo.symbols['o'])
        x_user = await bot.get_chat(xo.x_user_id)
        o_user = await bot.get_chat(xo.o_user_id)
        text = (
            f'{xo.symbols["x"]}{x_user.first_name}\n'
            '🤝\n'
            f'{xo.symbols["o"]}{o_user.first_name}'
            '\n\n'
            f'{result}'
        )
        xo.del_game()
        markup = types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text="tg channel", callback_data=f"tgc")]])
        return await bot.edit_message_text(text, chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=markup)

    if xo.o_user_id == "None" and xo.who_walk() == 'o':
        x_user = await bot.get_chat(xo.x_user_id)
        text = (
            f'{xo.symbols["x"]} {x_user.first_name} очікує на суперника\n\n'
            f'{xo.symbols["o"]} ходить'
        )
    else:
        x_user = await bot.get_chat(xo.x_user_id)
        o_user = await bot.get_chat(xo.o_user_id)
        walk_user = await bot.get_chat(xo.users[xo.who_walk()])
        text = (
            f'{xo.symbols["x"]} {x_user.first_name}\n'
            f'🆚️\n{xo.symbols["o"]} {o_user.first_name}\n\n'
            f'{xo.symbols[xo.who_walk()]} {walk_user.first_name} ходить'
        )
    await bot.edit_message_text(text, chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=field_markup(xo.field()))
