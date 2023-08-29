from telegram.ext import ContextTypes
from code.settings import *
from code.utility import *


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_response(update, "logs/start_log.txt", "")
    await update.message.reply_text('Привет!\n\nЭтот бот был сделан для проведения предпосвята фопф32x. '
                                    'С его помощью можно отслеживать прогресс прохождения этапов группами.\n\n'
                                    'Чтобы получить описание возможных команд, нажмите на /help')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = ''
    data = Data()

    chat_id = update.message.chat_id
    if is_admin(chat_id, data):
        message = get_file_text("help_text/admin.txt")
    else:
        if is_armenian(chat_id, data):
            message = get_file_text("help_text/armenian.txt")
        else:
            stage = determine_stage(chat_id, data)
            if stage in range(SIZE+1):
                message = get_file_text("help_text/stager.txt")
                message = message.replace('{stage_id}', str(stage)).replace('{stage_name}', STAGE_NAMES[stage])
            else:
                message = get_file_text("help_text/nobody.txt")
        message += get_file_text("help_text/default.txt")

    await update.message.reply_text(message)


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = Data()

    message = 'Статус\n\n'
    for group in data.groups.values():
        loc = group.location
        if loc is None:
            loc = group.future_path[0]

        message += str(group.group_id) + " гр - "

        if len(group.future_path) == 0 or (group.future_path == [-1]):
            message += "завершила путь."
        elif loc == -1:
            message += " стоит"
        elif group.moving:
            message += right_arrow + ' '  # "движется"
            if len(group.finished_path) > 0 and group.finished_path != [-1]:
                message += str(group.finished_path[-1]) + '//'  # " от " + str(group.finished_path[-1]) + " этапа"
            # if loc == 2:
            #     message += " ко "
            # else:
            #     message += " к "
            message += str(group.location)  # + " этапу."
        else:
            # message += " проходит "
            if loc == 0:
                message += "#армяне."
            else:
                message += str(loc)  # + " этап."
        finished = str(len(group.finished_path))
        if group.finished_path == [-1]:
            finished = '0'
        message += ". Баллы: " + str(sum(group.scores)) + ". Этапы: " + finished + ".\n"

    if is_admin(update.message.chat_id, data):
        jams = find_jam(data)
        if len(jams) == 0:
            message += "\nПробок нет\n"
        else:
            message += "\nПробки:\n"
            for jam in jams:
                message += str(jam.stage) + " этап: "
                for group in jam.groups:
                    message += str(group) + ', '
                message = message[:-2]
                message += '\n'

    await update.message.reply_text(message)


async def stages_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = Data()

    message = 'Этапы\n\n'
    for i in range(1, SIZE+1):
        message += str(i) + '. ' + str(STAGE_NAMES[i]) + ": "
        for stager in data.stagers[i]:
            message += stager.username + ', '
        message = message[:-2]
        message += '\n\n'

    message += "#армяне: "
    for armenian in data.armenians:
        message += armenian.username + ', '
    message = message[:-2]

    await update.message.reply_text(message)


async def scores_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = Data()

    message = 'Баллы:\n\n'
    for i in range(1, SIZE+1):
        message += str(i) + " группа - " + str(sum(data.groups[i].scores))

        second_part = ''
        separator = ')'
        for j in range(1, SIZE+1):
            if data.groups[i].scores[j] != 0:
                second_part += str(j) + separator + str(data.groups[i].scores[j]) + ', '
        if data.groups[i].scores[0] != 0:
            second_part += '#армяне' + separator + str(data.groups[i].scores[0]) + ', '
        if data.groups[i].scores[SIZE+1] != 0:
            second_part += 'другое' + separator + str(data.groups[i].scores[SIZE+1]) + ', '

        second_part = second_part[:-2]

        if second_part != '':
            message += ': ' + '\n' + second_part

        message += "\n\n"

    await update.message.reply_text(message)
