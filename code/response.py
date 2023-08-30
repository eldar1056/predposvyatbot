import copy

from code.commands import *
from code.settings import *


class Response:
    def __init__(self, text: str or list = None, recipients: set or list = None):
        if isinstance(text, str):
            self.text = [text]
        elif isinstance(text, list):
            self.text = text
        else:
            self.text = None

        if isinstance(recipients, set):
            self.recipients = [recipients]
        elif isinstance(recipients, list):
            self.recipients = recipients
        else:
            self.recipients = None

    async def send(self, bot: Bot):
        if bot is None or self.text is None:
            return

        for i in range(len(self.text)):
            await send_message(self.text[i], bot, self.recipients[i])


def handle_response(chat_id: int, text: str):
    data = Data()

    response = Response()
    if is_admin(chat_id, data):
        response = handle_admin_response(text, data)
    elif is_armenian(chat_id, data):
        response = handle_armenian_response(text, data)
    else:
        stage = determine_stage(chat_id, data)
        if stage in range(1, SIZE+1):
            response = handle_stager_response(text, stage, data)

    if response is not None and response.text is not None and response.text != [None]:
        data.store()

    return response


def handle_admin_response(text: str, data: Data):
    split_text = text.split()
    if split_text[0] == "me":
        return Response('admin')
    elif split_text[0] in ["путь", "path", "п", "p"]:
        if len(split_text) == 1:
            return Response('Введите номер группы в формате:путь [номер группы] [прошлый/будущий (будущий по умолчанию)]')
        elif (not split_text[1].isdigit()) or (int(split_text[1]) not in range(1, SIZE)):
            return Response('Введите корректный номер группы в формате:'
                            'путь [номер группы(от 1 до ' + str(SIZE) + ' )] [прошлый/будущий (будущий по умолчанию)]')
        else:
            group_id = int(split_text[1])
            future = True
            if len(split_text) > 2:
                if split_text[2] in ["прошлый", "п", "finished", "f", "past", "p"]:
                    future = False

            return Response(("Будущий " if future else "Прошлый ") + "путь группы " +
                            str(group_id) + ": " + data.groups[group_id].get_path(future))
    elif split_text[0] in ["установить_путь", "уст_путь", "уст_п", "уп", "у_п", "установить_п", "у_путь", "set_path", "s_path", "set_p", "s_p", "sp"]:
        if len(split_text) == 1:
            return Response('Введите номер группы в формате:установить_путь '
                            '[номер группы] [путь через -] [прошлый/будущий (будущий по умолчанию)]')
        elif (not split_text[1].isdigit()) or (int(split_text[1]) not in range(1, SIZE+1)):
            return Response('Введите корректный номер группы в формате:установить_путь [номер группы(от 1 до'
                            + str(SIZE) + ' )] [путь через -] [прошлый/будущий (будущий по умолчанию)]')
        else:
            group_id = int(split_text[1])
            if len(split_text) == 2:
                return Response("Введите путь в формате:установить_путь "
                                "[номер группы] [путь через -] [прошлый/будущий (будущий по умолчанию)]")
            else:
                path_arr = [-1]

                if split_text[2] != "-1":
                    path_arr = split_text[2].split('-')
                    for e in path_arr:
                        if not e.isdigit() or int(e) not in range(SIZE+1):
                            return Response("Введите путь через - "
                                            "(например 1-2-5-4 (уникальные числа от 0 до " + str(SIZE) + "))")

                    if len(path_arr) > len(set(path_arr)):
                        return Response("Введите путь без повторяющихся чисел")

                future = True
                if len(split_text) > 3:
                    if split_text[3] in ["прошлый", "п", "finished", "f", "past", "p"]:
                        future = False

                path = [int(path_arr[i]) for i in range(len(path_arr))]

                if future:
                    data.groups[group_id].future_path = path
                else:
                    data.groups[group_id].finished_path = path

                if data.groups[group_id].moving:
                    data.groups[group_id].location = data.groups[group_id].future_path[0]

                return Response(("Будущий " if future else "Прошлый ") + "путь группы "
                                + str(group_id) + ": " + data.groups[group_id].get_path(future))
    elif split_text[0] in ["data", "d", "данные", "д"]:
        return Response("admins.txt:\n" + get_file_text("roles/admins.txt") +
                        "\narmenians.txt:\n" + get_file_text("roles/armenians.txt") +
                        "\nstagers.txt:\n" + get_file_text("roles/stagers.txt") +
                        "\ngroups_data.txt:\n" + get_file_text("groups_data.txt"))
    elif split_text[0] in ["н", "нач", "начало", "begin", "b", "beg", "beginning"]:
        if len(split_text) < 3 or \
                (not split_text[1].isdigit()) or (int(split_text[1]) not in range(1, SIZE+1)) \
                or (not split_text[2].isdigit()) or (int(split_text[2]) not in range(SIZE+1)):
            return Response('Введите запрос в формате:начало [номер группы] [номер этапа]')
        else:
            return handle_stager_response(text, int(split_text[2]), data)
    elif split_text[0] in ["к", "кон", "конец", "финиш", "finish", "fin", "f", "end"]:
        if len(split_text) < 4 or \
                (not split_text[1].isdigit()) or (int(split_text[1]) not in range(1, SIZE + 1)) \
                or (not split_text[2].isdigit()) or (int(split_text[2]) not in range(SIZE + 1))\
                or not (split_text[3].isdigit() or (split_text[3][1:].isdigit() and split_text[3][0] == '-')):
            return Response('Введите запрос в формате:конец [номер группы] [номер этапа] [количество баллов]')
        else:
            return handle_stager_response(
                split_text[0] + ' ' + split_text[1] + ' ' + split_text[3], int(split_text[2]), data)
    elif split_text[0] in ['add', 'a', 'add_score', 'add_s', 'a_s', 'as', "добавить", "доб", "добавить_баллы", "доб_бал", "доб_б", "д_б", "дб", "д_бал"]:
        if len(split_text) < 3 or (not split_text[1].isdigit()) or (int(split_text[1]) not in range(1, SIZE+1)):
            return Response('Введите кол-во баллов в формате:добавить_баллы [группа] [количество баллов]')
        elif not (split_text[2].isdigit() or (split_text[2][1:].isdigit() and split_text[2][0] == '-')):
            return Response('Введите кол-во баллов в формате:добавить_баллы [группа] [количество баллов (целое число)]')
        else:
            group_id = split_text[1]
            change = split_text[2]
            data.groups[int(group_id)].scores[SIZE+1] += int(change)
            rec = set()
            add_recipients(rec, admins=True)
            return Response('Количество баллов ' + group_id + ' группы изменено на ' +
                            change + '. Текущий результат: ' + str(sum(data.groups[int(group_id)].scores)), rec)
    elif split_text[0] in ['статус', 'стат', 'с', 'status', 'stat', 's']:
        message = "Статус этапов:\n\n"
        stages = [[] for i in range(SIZE + 1)]
        occupied = [False for i in range(SIZE + 1)]
        for group in data.groups.values():
            if group.location is not None and group.location in range(SIZE + 1):
                stages[group.location].append(group.group_id)
                if not group.moving:
                    occupied[group.location] = True

        for i in range(SIZE + 1):
            num = str(i) + '. '
            if len(num) == 3:
                num += "  "
            message += num
            if len(stages[i]) == 0:
                message += CHECK_MARK + ' Свободен\n'
            else:
                if not occupied[i]:
                    message += RIGHT_ARROW + " "
                else:
                    message += CROSS_MARK + " "
                for group_id in stages[i]:
                    message += str(group_id) + ', '
                message = message[:-2]
                message += '\n'

        return Response(message)
    elif split_text[0] == 'reset':
        data.__init__(True)
        message = 'ВНИМАНИЕ! Данные сброшены до начальных значений.'
        rec = set()
        add_recipients(rec, admins=True)
        return Response(message, rec)
    elif split_text[0] in ['help*', 'h*', 'помощь*', 'п*', 'help+', 'h+', 'помощь+', 'п+']:
        return Response(get_file_text("help_text/admin+.txt"))
    elif split_text[0] in ["roles", "r", "роли", "р"]:
        return Response(data.get_roles())
    else:
        return Response('Недоступная команда: ' + split_text[0])


def handle_stager_response(text: str, stage_id: int, data: Data):
    split_text = text.split()
    if split_text[0] == 'me':
        return Response('stager')
    if split_text[0] in ["н", "нач", "начало", "begin", "b", "beg", "beginning"]:
        if len(split_text) == 1:
            return Response('Введите номер группы в формате:начало [номер группы]')
        elif (not split_text[1].isdigit()) or (int(split_text[1]) not in range(1, SIZE+1)):
            return Response('Введите корректный номер группы в'
                            ' формате:начало [номер группы(от 1 до ' + str(SIZE) + ' )]')
        else:
            group_id = int(split_text[1])
            data.groups[group_id].arrival(stage_id)
            message = 'Группа ' + str(group_id) + ' начала проходить ' + str(stage_id) + ' этап'

            rec = set()
            if stage_id in range(1, SIZE+1):
                for stager in data.stagers[stage_id]:
                    rec.add(stager.chat_id)
            elif stage_id == 0:
                for armenian in data.armenians:
                    rec.add(armenian.chat_id)
            for admin in data.admins:
                rec.add(admin)

            return Response(message, rec)
    elif split_text[0] in ["к", "кон", "конец", "финиш", "finish", "fin", "f", "end"]:
        if len(split_text) == 1:
            return Response('Введите номер группы в формате:конец [номер группы] [количество баллов]')
        elif (not split_text[1].isdigit()) or (int(split_text[1]) not in range(1, SIZE+1)):
            return Response('Введите корректный номер группы в формате:'
                            'конец [номер группы(от 1 до ' + str(SIZE) + ' )] [количество баллов]')
        elif len(split_text) < 3:
            return Response('Введите количество баллов в формате: конец '
                            '[номер группы] [количество баллов]')
        elif not (split_text[2].isdigit() or (split_text[2][1:].isdigit() and split_text[2][0] == '-')):
            return Response('Введите корректное количество баллов в формате:конец '
                            '[номер группы] [количество баллов (целое число)]')
        else:
            group_id = int(split_text[1])
            score = int(split_text[2])

            finished = False
            if stage_id in data.groups[group_id].finished_path:
                finished = True

            data.groups[group_id].finish_location(stage_id)
            data.groups[group_id].scores[stage_id] = score
            message = 'Группа ' + str(group_id) + ' завершила ' \
                      + str(stage_id) + ' этап с результатом: ' + str(score)
            rec = set()
            if stage_id in range(1, SIZE+1):
                for stager in data.stagers[stage_id]:
                    rec.add(stager.chat_id)
            elif stage_id == 0:
                for armenian in data.armenians:
                    rec.add(armenian.chat_id)

            for admin in data.admins:
                rec.add(admin)

            if not finished:
                jams = find_jam(data)
                for jam in jams:
                    if group_id in jam.groups:
                        jam_message = 'ВНИМАНИЕ! ПРОБКИ:\n'
                        for jam in jams:
                            jam_message += str(jam.stage) + " этап: "
                            for group in jam.groups:
                                jam_message += str(group) + ', '
                            jam_message = jam_message[:-2]
                            jam_message += '\n'

                        jam_rec = set()
                        add_recipients(jam_rec, admins=True)
                        message = [message, jam_message]
                        rec = [rec, jam_rec]
                        break

            return Response(message, rec)
    else:
        return Response('Недоступная команда: ' + split_text[0])


def handle_armenian_response(text: str, data: Data):
    if text == 'me':
        return Response('armenian')
    return handle_stager_response(text, 0, data)


async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    if message_type != 'private':
        return

    text = update.message.text.lower()

    if text.split()[0] in ['вопрос', 'request']:
        message = (text[7:]).replace('\n', ' ').strip()
        log_response(update, "logs/question_log.txt", message)
        return

    messages = text.split('\n')

    chat_id = update.message.chat.id

    print(f'User ({chat_id}) in {message_type}: "{text}"')

    for message in messages:
        await handle_message(message, chat_id, update, context)


async def handle_message(text: str, chat_id: int, update: Update, context: ContextTypes.DEFAULT_TYPE):
    if text in ["да", "д", "конечно", "разумеется", "так точно", "yes", "y", "yep", "ok", "ок", "+", "1"]:
        log_response(update, "logs/answer_log.txt", "Yes")
        return
    elif text in ["нет", "н", "иди нафиг", "no", "n", "nope", "-", "0"]:
        log_response(update, "logs/answer_log.txt", "No")
        return
    elif text in ['статус', 'стат', 'с', 'status', 'stat', 's']:
        await status_command(update, context)
        return
    elif text in ['помощь', 'help', 'h']:
        await help_command(update, context)
        return
    elif text in ['start']:
        await start_command(update, context)
        return
    elif text in ['scores']:
        await scores_command(update, context)
        return
    elif text in ['stages']:
        await stages_command(update, context)
        return

    response = handle_response(chat_id, text)

    if response is not None:
        if response.recipients is None or response.recipients == [None]:
            response.recipients = [{chat_id}]

        await response.send(context.bot)
