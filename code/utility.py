import telegram

from code.data import Data
from telegram import Update, Bot
import datetime
from code.settings import *


def log_response(update: Update, filename: str, message: str = ""):
    chat_id = update.message.chat_id
    username = update.message.chat.username
    now = update.message.date + datetime.timedelta(hours=3)
    date = now.strftime("%H:%M:%S, %d/%m/%Y")
    entry = str(chat_id) + ' @' + username + ' ' + date + " " + message + '\n'
    with open(filename, "a", encoding="utf-8") as file:
        file.write(entry)


def is_admin(chat_id: int, data: Data):
    if chat_id in data.admins:
        return True
    return False


def is_armenian(chat_id: int, data: Data):
    for armenian in data.armenians:
        if chat_id == armenian.chat_id:
            return True
    return False


def determine_stage(chat_id: int, data: Data):
    for stage in data.stagers.values():
        for stager in stage:
            if chat_id == stager.chat_id:
                return stager.stage_id
    return -1


def get_file_text(filename: str):
    message = ''
    with open(filename, encoding="utf-8") as file:
        for line in file:
            message += line.strip() + '\n'
    return message


async def send_message(text: str, bot: Bot, recipients=None, admins=False, stagers=False, armenians=False):
    if text is None or text == '':
        return

    if recipients is None:
        recipients = set()

    add_recipients(recipients, admins, stagers, armenians)

    for chat in recipients:
        await bot.send_message(chat, text, parse_mode=telegram.constants.ParseMode.HTML)

    if len(recipients) > 0:
        line = 'Message sent:\n recipients:'
        for recipient in recipients:
            line += str(recipient) + ', '
        line = line[:-2]
        line += '\n text:'
        line += text
        print(line)


def add_recipients(recipients: set, admins=False, stagers=False, armenians=False):
    if not (admins or stagers or armenians):
        return recipients

    data = Data()
    if admins:
        for admin in data.admins:
            recipients.add(admin)
    if stagers:
        for stage in data.stagers.values():
            for stager in stage:
                recipients.add(stager.chat_id)
    if armenians:
        for armenian in data.armenians:
            recipients.add(armenian.chat_id)

    return recipients


class Jam:
    def __init__(self, stage_id: int, groups: list):
        self.stage = stage_id
        self.groups = groups


def find_jam(data: Data):
    jams = []

    current_groups = [[] for i in range(SIZE+1)]
    for group in data.groups.values():
        if group.location is not None and group.location in range(SIZE+1):
            current_groups[group.location].append(group.group_id)

    for i in range(SIZE+1):
        if len(current_groups[i]) > 1:
            jams.append(Jam(i, current_groups[i]))

    return jams


def fill(text: str, n: int, char: str = ' ', align_left=True):
    size = len(text)
    if n < size:
        return text

    appendix = char * (n - size)
    if align_left:
        return text + appendix
    else:
        return appendix + text

