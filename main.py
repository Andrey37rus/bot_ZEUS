#  найти бота!
# auto-py-to-exe для компиляции online


import webbrowser
import os
import pythoncom
import pyautogui as pg
from telebot import types
import telebot
from win32ctypes.core import ctypes
import ctypes
import win32security
import win32api
from ntsecuritycon import *
import subprocess
import sys
import pyautogui
import time
import win32com.client
from fuzzywuzzy import fuzz
import json

token = ''

bot = telebot.TeleBot(token)


def AdjustPrivilege(priv, enable=1):
    """Функция дает привилегии для выключение, перезагрузки и спящего режима компьютера!
    Вспомогательная функция! Для основных функций shotdown, mode_sleep, restart"""

    # Get the process token
    flags = TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY
    htoken = win32security.OpenProcessToken(win32api.GetCurrentProcess(), flags)
    # Get the ID for the system shutdown privilege.
    idd = win32security.LookupPrivilegeValue(None, priv)
    # Now obtain the privilege for this process.
    # Create a list of the privileges to be added.
    if enable:
        newPrivileges = [(idd, SE_PRIVILEGE_ENABLED)]
    else:
        newPrivileges = [(idd, 0)]
    # and make the adjustment
    win32security.AdjustTokenPrivileges(htoken, 0, newPrivileges)


def markup():
    """
    Создание нижней клавиатуры с кнопкой /stop

    :return: markup
    """
    mark = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn0 = types.KeyboardButton("/start")
    btn1 = types.KeyboardButton("🔊")
    btn2 = types.KeyboardButton("🔉")
    btn3 = types.KeyboardButton("⏹️")
    btn4 = types.KeyboardButton("▶️")
    btn5 = types.KeyboardButton("🔇")
    btn6 = types.KeyboardButton("🛑")
    btn7 = types.KeyboardButton("🔄")
    btn8 = types.KeyboardButton("💤")
    btn9 = types.KeyboardButton("🎮")
    btn10 = types.KeyboardButton("🎬")
    mark.add(btn0, btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9, btn10)
    return mark


@bot.message_handler(commands=['start'])
def start(message: telebot.types.Message) -> None:
    text = "Привет! Меня зовут ZEUS\n" \
           "Я умею управлять мультимедией:\n" \
           "▶️ - плей\n" \
           "⏹️ - стоп\n" \
           "🔊 - звук громче\n" \
           "🔉 - звук тише\n" \
           "🔇 - без звука\n" \
           "Еще я могу:\n" \
           "🎮 - запустить игру\n" \
           "🎬 - включить фильм\n" \
           "А также:\n" \
           "🛑 - выключить компьютер\n" \
           "🔄 - перезагрузить компьютер\n" \
           "💤 - спящий режим\n" \
           "Добро пожаловать!😊"
    bot.send_message(message.chat.id, text=text)
    bot.send_message(message.chat.id, "Выберете кнопку пожалуйста", reply_markup=markup())


@bot.message_handler(content_types=['text'])
def commands(message):
    """Выбор функции и обработка"""

    list_keys = {
        '🔊': vol,
        '🔉': vol,
        '⏹️': stop,
        '▶️': play,
        '🔇': soundless,
        "🛑": shutdown,
        "🔄": restart,
        "💤": sleep_mode,
        "🎮": games,
        "🎬": movie
    }

    text = message.text

    for k, v in list_keys.items():
        if k == text:
            list_keys[k](message, k)
            return
    else:
        bot.send_message(message.chat.id, 'Выберете кнопку пожалуйста', reply_markup=markup())


def movie(*args):
    """функция по запросу фильма
    запрашивает название фильма и передает имя в следующую функ get_movie"""
    message = args[0]
    # bot.send_message(message.chat.id, 'not implemented yet', reply_markup=markup())
    mess = bot.send_message(message.chat.id, "Введите название фильма")
    bot.register_next_step_handler(mess, get_movie)


def get_movie(message):
    """открываеться файл со словарем фильмом, это словарь где ключь это число списка записанных в файл от 1 до 100000
    {ключ 1 это место в словаре значение ключа это список в котором лежит название фильма и ссылка на страницу.

    list_film хранит фильммы которые выбранны из файла по запросу. где ключ это прорядковый номер как в файле выше,
     значение название фильма и ссылка на страницу как в файле.

     создаються инлайн кнопки и счетчик и строка с текстом. где текст это по номеру счетчика и название фильма,
     инлайн кнопки это номер счетчика и callback  с порядковым номером из словаря.
     """
    movie_name = message.text

    with open('films_new_new.json', 'r', encoding="UTF-8") as file:
        box = json.load(file)

    list_films = {}
    for k, v in box.items():
        fuzzz = fuzz.WRatio(v[0], movie_name)
        if fuzzz > 87:
            list_films[k] = v
    if len(list_films.keys()) > 0:

        keyboard = types.InlineKeyboardMarkup()
        count = 1
        text = ''
        for key, val in list_films.items():
            text += f'{count}. {val[0]}\n'
            keyboard.add(types.InlineKeyboardButton(text=str(count), callback_data=key))
            count += 1

        bot.send_message(message.chat.id, text, reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "Фильмы по Вашему запросу не найдены")
        bot.send_message(message.chat.id, "Попробуйте снова", reply_markup=markup())


def games(*args):
    """функция строит путь абсолютный до рабочего стола и потом до папки games на рабочем столе
     создает инлайн кнопки сколько есть файлов в папке games при нажатие на выбранную кнопку с программой(игры)
     отсылает в функцию func_coll
     в конце вызывает reply кнопки с основным меню
     иначе просит у пользователя создать папку.
     """

    message = args[0]
    path = os.path.abspath(os.path.join('..', 'games'))
    path_f_l_b = os.path.abspath(os.path.join('..', 'Games'))
    path_l_b = os.path.abspath(os.path.join('..', 'GAMES'))
    if os.path.isdir(path):
        keyboard = types.InlineKeyboardMarkup()
        for file in os.listdir(path):
            x = os.path.join(path, file)
            game_name = os.path.splitext(file)[0]
            keyboard.add(types.InlineKeyboardButton(text=game_name, callback_data=x))

        bot.send_message(message.chat.id, 'Выберете игру', reply_markup=keyboard)
    elif os.path.isdir(path_f_l_b):
        keyboard = types.InlineKeyboardMarkup()
        for file in os.listdir(path_f_l_b):
            x = os.path.join(path_f_l_b, file)
            game_name = os.path.splitext(file)[0]
            keyboard.add(types.InlineKeyboardButton(text=game_name, callback_data=x))

        bot.send_message(message.chat.id, 'Выберете игру', reply_markup=keyboard)
    elif os.path.isdir(path_l_b):
        keyboard = types.InlineKeyboardMarkup()
        for file in os.listdir(path_l_b):
            x = os.path.join(path_l_b, file)
            game_name = os.path.splitext(file)[0]
            keyboard.add(types.InlineKeyboardButton(text=game_name, callback_data=x))

        bot.send_message(message.chat.id, 'Выберете игру', reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, 'Создайте папку (Games или GAMES или games) на рабочем столе и добавте ярлыки игр'
                                          'которые хотите запускать с помощью бота')


@bot.callback_query_handler(func=lambda call: True)
def func_call(call):
    """функция получает callback от иглайн кнопок и преобразует его в string.
        если string это путь то запускакеться функция start_game  с параметром string.
        иначе если string == play то запускаться func_x запуск плеера.
        иначе значит это порядковый номер в словаре с фильмами и запускается функция start_film с аргументами string и
        call.message.
        после выхода из функции отправляется меню  сосновными кнопками.
    """
    string = call.data

    if os.path.exists(string):
        start_game(string)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Выберете игру', reply_markup=None)
        bot.send_message(call.message.chat.id, 'Выберете кнопку пожалуйста', reply_markup=markup())
    elif string == 'PLAY':
        func_x()
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Начать просмотр?', reply_markup=None)
        bot.send_message(call.message.chat.id, 'Выберете кнопку пожалуйста', reply_markup=markup())
    else:
        start_film(string, call.message)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=call.message.text, reply_markup=None)


def start_film(num, message):
    """
    Функция принимает порядковый номер из словаря с фильмами и message
    открывает файл со словарем с фильмами и берет из него попоряд. номеру ссылку на фильм и открывает ее в браузере.
    Далее создается инлайн кнопка play и отправляется.
    """
    with open('films_new_new.json', 'r', encoding="UTF-8") as file:
        box = json.load(file)
    url = box[num][1]

    webbrowser.open(url)

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='PLAY', callback_data="PLAY"))
    bot.send_message(message.chat.id, 'Начать просмотр?', reply_markup=keyboard)


def func_x():
    """
    Функция симулирующая управление мыши.
    Сначала берет разрешение экрана в px, затеми ставит мышь по цепнтру экрана, затем скролит вниз, делает двойной щелчек
    левой клавишей мыши открывая плеер на весь экран, затем делает один щелчек левой кнопкой мыши для запуска плеера.

    """
    # get the screen resolution
    screenWidth, screenHeight = pyautogui.size()

    # calculate the x and y coordinates to move the mouse to the center
    x = screenWidth // 2
    y = screenHeight // 2

    # move the mouse to the center of the screen
    pyautogui.moveTo(x, y)

    # Scrolls down 100 pixels
    pyautogui.scroll(-1100)
    time.sleep(2)

    # move left 100 pixels
    pyautogui.moveRel(-350, 0)

    # Double clicks the left mouse button
    pyautogui.doubleClick()
    time.sleep(2)

    # Clicks the left mouse button
    pyautogui.click(button='left')


def start_game(path):
    """функция принимает путь до ярдыка, с помощью библиотеки берет из ярлыка данные ввиде прямого пути до файла .exe
    и запускает его после чего возвращаеться обратно в func_call"""

    pythoncom.CoInitializeEx(0)
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(path)
    if os.path.splitext(path)[1] == '.lnk':
        subprocess.Popen(shortcut.Targetpath)
        # print(shortcut.Targetpath)
    else:
        subprocess.Popen((['open', shortcut.Targetpath]))


def sleep_mode(*args):
    """Спящий режим"""
    message = args[0]
    try:
        bot.send_message(message.chat.id, 'Спящий режим активирован', reply_markup=markup())
        AdjustPrivilege(SE_SHUTDOWN_NAME)
        win32api.SetSystemPowerState(True, True)
        return
    except:
        Exception()


def restart(*args):
    """Перезагрузка системы"""
    message = args[0]
    try:
        bot.send_message(message.chat.id, 'Перезагрузка системы', reply_markup=markup())
        AdjustPrivilege(SE_SHUTDOWN_NAME)
        user32 = ctypes.WinDLL('user32')
        user32.ExitWindowsEx(0x00000002, 0x00000000)
        return
    except:
        Exception()


def shutdown(*args):
    """Завершение работы"""

    message = args[0]
    try:
        bot.send_message(message.chat.id, 'Выключение', reply_markup=markup())
        AdjustPrivilege(SE_SHUTDOWN_NAME)
        user32 = ctypes.WinDLL('user32')
        user32.ExitWindowsEx(0x00000008, 0x00000000)
        return
    except:
        Exception()


def vol(message, k):
    """Функция определяющая прибавление громкости или убавляющая. Создает клавиптуру"""

    mark_up = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn_1 = types.KeyboardButton('2')
    btn_2 = types.KeyboardButton('5')
    btn_3 = types.KeyboardButton('10')
    btn_4 = types.KeyboardButton('15')
    btn_5 = types.KeyboardButton('20')
    mark_up.add(btn_1, btn_2, btn_3, btn_4, btn_5)

    mess = bot.send_message(message.chat.id, 'Выберете кнопку пожалуйста', reply_markup=mark_up)
    if k == '🔊':
        bot.register_next_step_handler(mess, turn_up)
    else:
        bot.register_next_step_handler(mess, turn_down)


def turn_up(message):
    """Функция прибавляющая звук в зависимости от выбранной кнопки, проверка на правильность ввода"""

    num = int(message.text)
    pg.press(['volumeup'], num // 2)
    bot.send_message(message.chat.id, 'Выберете кнопку пожалуйста', reply_markup=markup())


def turn_down(message):
    """делает звук тише в x2"""

    num = int(message.text)
    pg.press(['volumedown'], num // 2)
    bot.send_message(message.chat.id, 'Выберете кнопку пожалуйста', reply_markup=markup())


def play(*args):
    """Play or Pause"""

    message = args[0]
    pg.press(['playpause'])
    bot.send_message(message.chat.id, 'Выберете кнопку пожалуйста', reply_markup=markup())


def soundless(*args):
    """Делает комп без звука, со звуком"""

    message = args[0]
    pg.press(['volumemute'])
    bot.send_message(message.chat.id, 'Выберете кнопку пожалуйста', reply_markup=markup())


def stop(*args):
    """Play or Pause"""

    message = args[0]
    pg.press(['playpause'])
    bot.send_message(message.chat.id, 'Выберете кнопку пожалуйста', reply_markup=markup())


def main():
    """
    Функция запускающая телеграм бот.

    """
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
        main()


if __name__ == "__main__":
    main()

# Заметки!
# добавить кнопку скриншот экрана

