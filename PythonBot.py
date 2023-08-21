from typing import Any
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Text, Command
from aiogram import F
from aiogram.filters import BaseFilter
import random


# Вместо BOT TOKEN HERE нужно вставить токен вашего бота,
# полученный у @BotFather
BOT_TOKEN: str = ''


admin_ids: list[int] = []




# Создаем объекты бота, диспетчера и юзера
bot: Bot = Bot(token=BOT_TOKEN)
dp: Dispatcher = Dispatcher()
users: dict = {'id':{
              'in_game': False,
              'secret_number': None,
              'attempts': None,
              'total_games': 0,
              'wins': 0,
              'percent': 0}}
ATTEMPTS: int=8

def get_random_number()->int: return random.randint(1,100)

def new_user(message: Message):
    if message.from_user.id not in users: 
        users[message.from_user.id]={
              'in_game': False,
              'secret_number': None,
              'attempts': None,
              'total_games': 0,
              'wins': 0,
              'percent': 0}
    return True

# Этот хэндлер будет срабатывать на команду "/start"
@dp.message(Command(commands=["start"]))
async def process_start_command(message: Message):
    await message.answer('Привет!\nЯ бот, с которым можно сыграть в игру "Угадай число"!\nУ тебя будут команды /start, /cancel и /stat!\nСыграем? ')
    print(message.from_user.id)
    new_user(message)




class IsAdmin(BaseFilter):
    def __init__(self, admin_ids: list[int]) -> None:
        self.admin_ids = admin_ids

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in self.admin_ids

class NumbersInMessage(BaseFilter):
    async def __call__(self, message: Message) -> bool | dict[str, list[int]]:
        
        numbers=[]
        for word in message.text.split():
            normalizedWord=word.replace('.', '').replace(',','').strip()
            if normalizedWord.isdigit():
                numbers.append(int(normalizedWord))
        if numbers:
            return{'numbers': numbers}
        return False
    


#Этот хендлер будет работать, когда в сообщениях есть числа
@dp.message(Text(startswith='Найди числа', ignore_case=True), NumbersInMessage())

async def process_found_numbers(message:Message, numbers: list[int]):
 await message.answer(
     text=f'Нашел: {", ".join(str(num) for num in numbers)} ' )
 


#Этот хендлер будет работать, когда чисел в сообщении нет
@dp.message(Text(startswith='Найди числа', ignore_case=True))

async def process_didnt_find_numbers(message:Message):
    await message.answer(
        text='Не нашел чисел в твоем сообщении :(('
    )

# Этот хэндлер будет срабатывать на команду "/help"
@dp.message(Command(commands=["help"]))
async def process_help_command(message: Message):
    await message.answer(f'Правила игры:\n\nЯ загадываю число от 1 до 100, '
                         f'а тебе нужно его угадать\nУ тебя есть {ATTEMPTS} '
                         f'попыток\n\nДоступные команды:\n/help - правила '
                         f'игры? статистику и список команд\n/cancel - выйти из игры\n'
                         f'/stat - посмотреть статистику\nCыграем?')

# Этот хэндлер будет срабатывать на команду "/stat"
@dp.message(Command(commands=['stat']))
async def process_stat_command(message: Message):
            new_user(message)
            await message.answer(f'Всего игр сыграно: {users[message.from_user.id]["total_games"]}\n'
                            f'Игр выиграно: {users[message.from_user.id]["wins"]}\n'
                         f'Это {users[message.from_user.id]["percent"]*100}%!')
    

# Этот хэндлер будет срабатывать на команду "/cancel"
@dp.message(Command(commands=['cancel']))
async def process_cancel_command(message: Message):
    if new_user(message) or users[message.from_user.id]['in_game']:
        await message.answer('Ты вышел из игры. Если захочешь сыграть '
                             'снова - напиши об этом')
        users[message.from_user.id]['in_game']=False
    else:
        await message.answer('А мы и так не играем. '
                             'Может, перекинемся разок?')

# Этот хэндлер будет срабатывать на согласие пользователя сыграть в игру
@dp.message(Text(text=['Да', 'Давай', 'Сыграем', 'Игра', 'Ага',
                       'Играть', 'Хочу играть', 'Сука', 'А давай', 'Была не была', 'Хуй тебе', 'Поехали', 'Ок'], ignore_case=True))
async def process_positive_answer(message: Message):
    if new_user(message) and not users[message.from_user.id]['in_game']:
        await message.answer('Ура!\n\nЯ загадал число от 1 до 100, '
                             'попробуй угадать! У тебя есть 8 попыток!')
        users[message.from_user.id]['in_game'] = True
        users[message.from_user.id]['secret_number'] = get_random_number()
        users[message.from_user.id]['attempts'] = ATTEMPTS
    else:
        await message.answer('Пока мы играем в игру я могу '
                             'реагировать только на числа от 1 до 100 '
                             'и команды /cancel и /stat')
        


# Этот хэндлер будет срабатывать на отказ пользователя сыграть в игру
@dp.message(Text(text=['Нет', 'Не', 'Не хочу', 'Не буду', 'Пошел в жопу', 'Пошёл в жопу'], ignore_case=True))
async def process_negative_answer(message: Message):
    if new_user(message) and not users[message.from_user.id]['in_game']:
        await message.answer('На нет и суда нет! Но если что, я всегда готов!')
    else:
        await message.answer('Мы же сейчас с тобой играем. Присылай, '
                             'пожалуйста, числа от 1 до 100')
        


# Этот хэндлер будет срабатывать на отправку пользователем чисел от 1 до 100
@dp.message(lambda x: x.text and x.text.isdigit() and 1 <= int(x.text) <= 100)
async def process_numbers_answer(message: Message):
    if new_user(message) and users[message.from_user.id]['in_game']:
        if int(message.text) == users[message.from_user.id]['secret_number']:
            await message.answer('Ура!!! Ты угадал число!\n\n'
                                 'Может, сыграем еще?')
            users[message.from_user.id]['in_game'] = False
            users[message.from_user.id]['total_games'] += 1
            users[message.from_user.id]['wins'] += 1
            users[message.from_user.id]['percent']=users[message.from_user.id]['wins']/users[message.from_user.id]['total_games']
        elif int(message.text) > users[message.from_user.id]['secret_number']:
            await message.answer('Мое число меньше')
            users[message.from_user.id]['attempts'] -= 1
        elif int(message.text) < users[message.from_user.id]['secret_number']:
            await message.answer('Мое число больше')
            users[message.from_user.id]['attempts'] -= 1

        if users[message.from_user.id]['attempts'] == 0:
            await message.answer(f'К сожалению, у тебя больше не осталось '
                                 f'попыток. Ты проиграл :(\n\nМое число '
                                 f'было {users[message.from_user.id]["secret_number"]}\n\nДавай '
                                 f'сыграем еще?')
            users[message.from_user.id]['in_game'] = False
            users[message.from_user.id]['total_games'] += 1
            users[message.from_user.id]['percent']=users[message.from_user.id]['wins']/users[message.from_user.id]['total_games']
    else:
        await message.answer('Мы еще не играем. Хотите сыграть?')



# Этот хэндлер будет срабатывать на остальные любые сообщения
@dp.message()
async def process_other_text_answers(message: Message):
    if new_user(message) and users[message.from_user.id]['in_game']:
        await message.answer('Мы же сейчас с тобой играем. '
                             'Присылай, пожалуйста, числа от 1 до 100')
    else:
        await message.answer('Я довольно ограниченный бот, давай '
                             'просто сыграем в игру?')

# Этот хэндлер будет срабатывать, если апдейт от админа
@dp.message(IsAdmin(admin_ids))
async def answer_if_admins_update(message: Message):
    await message.answer(text='Вы админ')


# Этот хэндлер будет срабатывать, если апдейт не от админа
@dp.message()
async def answer_if_not_admins_update(message: Message):
    await message.answer(text='Вы не админ')
    



if __name__ == '__main__':
    dp.run_polling(bot)