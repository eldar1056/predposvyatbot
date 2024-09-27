import telegram.constants
from telegram.ext import ContextTypes
from code.settings import *
from code.utility import *


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_response(update, "logs/start_log.txt", "")
    await update.message.reply_text('Привет!\n\nЭтот бот был сделан для проведения предпосвята фопф32x. '
                                    'С его помощью можно отслеживать прогресс прохождения этапов группами.\n\n'
                                    'Карта предпосвята: https://yandex.ru/maps/-/CDHXFP7c\n\nЧтобы получить описание'
                                    ' возможных команд, нажмите на /help')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Берет текст из help_text/*.txt для соответствующей роли
    message = ''
    data = Data()

    chat_id = update.message.chat_id
    if is_admin(chat_id, data):
        message = get_file_text("help_text/admin.txt")
    else:
        arm_id = get_armenian_id(chat_id, data)
        if arm_id >= 0:
            message = get_file_text("help_text/armenian.txt").replace(
                '{GROUPS_SIZE}', str(GROUPS_SIZE)).replace('{stage_name}', str(ARMENIAN_NAMES[arm_id]))
        else:
            stage = get_stage_id(chat_id, data)
            if stage in range(STAGES_SIZE+1):
                message = get_file_text("help_text/stager.txt")
                message = message.replace('{stage_id}', str(stage)).replace(
                    '{stage_name}', STAGE_NAMES[stage]).replace('{GROUPS_SIZE}', str(GROUPS_SIZE))
            else:
                message = get_file_text("help_text/nobody.txt")
        message += get_file_text("help_text/default.txt")

    await update.message.reply_text(message, parse_mode=telegram.constants.ParseMode.HTML)


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Для каждой группы дает статус чем они сейчас занимаются, сколько всего баллов, сколько конкурсов завершили
    data = Data()

    message = 'Статус групп:\n\n'
    for group in data.groups.values():
        loc = group.location
        if loc is None:
            if group.future_path is not None and len(group.future_path > 0):
                loc = group.future_path[0]
            else:
                loc = 0

        num = str(group.group_id) + '. '
        if len(num) == 3:
            num += '  '
        message += num

        position = ''
        if len(group.future_path) == 0 or (group.future_path == [0]):
            position = "Закончили"
        elif loc == 0:
            position = "Стоит"
        elif group.moving:
            message += RIGHT_ARROW
            # position += RIGHT_ARROW + ' '  # "движется"
            if len(group.finished_path) > 0 and group.finished_path != [0]:
                last_finished = ""
                for i in range(len(group.finished_path)-1, -1, -1):
                    last_finished = str(group.finished_path[i]) + last_finished
                    if group.finished_path[i] > 0:
                        break
                    elif i > 0:
                        last_finished = "/" + last_finished

                position += last_finished + '->'  # " от " + str(group.finished_path[0]) + " этапа"
            # if loc == 2:
            #     message += " ко "
            # else:
            #     message += " к "
            position += str(group.location)  # + " этапу."
        else:
            # message += " проходит "
            # if loc == 0:
            #     message += "#армяне."
            # else:
            message += STANDING_MAN
            position = str(loc)  # + " этап."
        finished = str(len([stage for stage in group.finished_path if stage != 0]))
        if group.finished_path == [0]:
            finished = '0'

        #print(len(position))
        # Выравнивание строки, чтобы красиво выглядело
        if len(position) == 1:
            position = 9 * ' ' + position + 8 * ' '
        if len(position) == 2:
            position = 8 * ' ' + position + 7 * ' '
        elif len(position) == 3:
            position = 7 * ' ' + position + 6 * ' '
        elif len(position) == 4:
            if position[1] == '-':
                position = 7 * ' ' + position + 4 * ' '
            else:
                position = 5 * ' ' + position + 6 * ' '
        elif len(position) == 5:
            position = 5 * ' ' + position + 4 * ' '
        elif len(position) == 9:
            position += 4 * ' '

        message += position
        message += "Баллы: " + str(sum(group.scores)) + ". Этапы: " + finished + ".\n"

    # Для админов(и не только) дополнительная информация о пробках
    if is_admin(update.message.chat_id, data) or get_stage_id(update.message.chat_id, data) != 0:
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
    # Список этапников и армян
    data = Data()

    message = 'Этапы\n\n'
    for i in range(1, STAGES_SIZE+1):
        message += str(i) + '. ' + str(STAGE_NAMES[i]) + ": "
        for stager in data.stagers[i]:
            message += stager.username + ', '
        message = message[:-2]
        message += '\n\n'

    if ARMENIAN_SIZE > 0:
        message += '#армяне\n\n'
        for i in range(1, ARMENIAN_SIZE+1):
            message += str(i) + '. ' + str(ARMENIAN_NAMES[i]) + ": "
            for armenian in data.armenians[-i]:
                message += armenian.username + ', '
            message = message[:-2]
            if i < ARMENIAN_SIZE:
                message += '\n\n'

    await update.message.reply_text(message)


async def scores_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Дает список с расписанными баллами для всех групп
    data = Data()

    message = 'Баллы групп:\n\n'
    for i in range(1, GROUPS_SIZE+1):
        message += str(i) + ". " + str(sum(data.groups[i].scores))

        second_part = ''
        for j in range(1, STAGES_SIZE+1):
            # print(i, j, data.groups[i].scores[j])
            if data.groups[i].scores[j] != 0:
                second_part += str(data.groups[i].scores[j]) + '(' + str(j) + ') + '
        for j in range(1, ARMENIAN_SIZE+1):
            if data.groups[i].scores[j+STAGES_SIZE] != 0:
                second_part += str(data.groups[i].arm_scores[j]) + '(-' + str(j) + ') + '
        if data.groups[i].scores[0] != 0:
            second_part += str(data.groups[i].scores[0]) + '(другое) + '

        second_part = second_part[:-2]

        if second_part != '':
            message += ' = ' + second_part

        message += "\n\n"

    await update.message.reply_text(message)
