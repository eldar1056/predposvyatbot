# handle_messages -> handle_message -> handle_response -> handle_admin(stager/armeninan)_response

from code.commands import *
from code.settings import *


# Хранит в себе список сообщений и получателей и может отправить их
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

    # Копирует содержимое другого Response
    def add_res(self, another):
        if another.text is None or another.recipients is None:
            return

        if self.text is None:
            self.text = []
        if self.recipients is None:
            self.recipients = []

        if isinstance(another.text, str):
            self.text.append(another.text)
        elif isinstance(another.text, list):
            self.text += another.text

        if self.recipients is None and another.recipients is not None:
            self.recipients = []
        if isinstance(another.recipients, set):
            self.recipients.append(another.recipients)
        elif isinstance(another.recipients, list):
            self.recipients += another.recipients

    # Добавляет новое сообщение
    def add(self, text: str or list = None, recipients: set or list = None):
        self.add_res(Response(text, recipients))

    # Отправляет все сообщения соответствующим получателям
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
    elif get_armenian_id(chat_id, data) > 0:
        response = handle_armenian_response(text, get_armenian_id(chat_id, data), data)
    else:
        stage = get_stage_id(chat_id, data)
        if stage in range(-ARMENIAN_SIZE, STAGES_SIZE+1) and stage != 0:
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
            return Response('Введите номер группы в формате:'
                            'путь [номер группы] [прошлый/будущий/оба (оба по умолчанию)]')
        elif (not split_text[1].isdigit()) or (int(split_text[1]) not in range(1, GROUPS_SIZE+1)):
            return Response('Введите корректный номер группы в формате: путь [номер группы'
                            '(от 1 до ' + str(GROUPS_SIZE) + ' )] [прошлый/будущий/оба (оба по умолчанию)]')
        else:
            group_id = int(split_text[1])
            future = False
            finished = False
            if len(split_text) > 2:
                if split_text[2] in ["прошлый", "п", "пр", "прош", "finished", "fin", "past", "p", "fn"]:
                    finished = True
                elif split_text[2] in ["будущий", "б", "буд", "future", "fut", "fr"]:
                    future = True
                else:
                    future = True
                    finished = True
            else:
                future = True
                finished = True

            prefix = ""
            if future and not finished:
                prefix = "Будущий "
            if finished and not future:
                prefix = "Прошлый "

            return Response(prefix + "Путь группы " +
                            str(group_id) + ":\n" + data.groups[group_id].get_path(finished, future))
    elif split_text[0] in ["установить_путь", "уст_путь", "уст_п", "уп", "у_п", "установить_п",
                           "у_путь", "set_path", "s_path", "set_p", "s_p", "sp"]:
        if len(split_text) == 1:
            return Response('Введите номер группы в формате:установить_путь '
                            '[номер группы] [путь через /] [прошлый/будущий (будущий по умолчанию)]')
        elif (not split_text[1].isdigit()) or (int(split_text[1]) not in range(1, GROUPS_SIZE+1)):
            return Response('Введите корректный номер группы в формате:установить_путь [номер группы(от 1 до'
                            + str(GROUPS_SIZE) + ' )] [путь через /] [прошлый/будущий (будущий по умолчанию)]')
        else:
            group_id = int(split_text[1])
            if len(split_text) == 2:
                return Response("Введите путь в формате:установить_путь "
                                "[номер группы] [путь через /] [прошлый/будущий (будущий по умолчанию)]")
            else:
                path_arr = [0]

                if split_text[2] != "0":
                    path_arr = split_text[2].split('/')
                    for e in path_arr:
                        is_number = (e.isdigit or (e[0] == "-" and e[1:].isdigit()))
                        in_range = (int(e) in range(-ARMENIAN_SIZE, GROUPS_SIZE+1) and not int(e) == 0)
                        if not is_number or not in_range:
                            return Response("Введите путь через / "
                                            "(например 1/2/5/4 (уникальные числа от -" + str(ARMENIAN_SIZE) + " до "
                                            + str(GROUPS_SIZE) + " (без нуля)))")

                    if len(path_arr) > len(set(path_arr)):
                        return Response("Введите путь без повторяющихся чисел")

                future = True
                if len(split_text) > 3:
                    if split_text[3] in ["прошлый", "п", "пр", "прош", "finished", "fin", "past", "p", "fn"]:
                        future = False

                path = [int(path_arr[i]) for i in range(len(path_arr))]

                if future:
                    data.groups[group_id].future_path = path
                else:
                    data.groups[group_id].finished_path = path

                if data.groups[group_id].moving:
                    data.groups[group_id].location = data.groups[group_id].future_path[0]

                return Response(("Будущий " if future else "Прошлый ") + "путь группы "
                                + str(group_id) + ": " + data.groups[group_id].get_path(not future, future))
    elif split_text[0] in ["data", "d", "данные", "д"]:
        return Response("admins.txt:\n" + get_file_text("roles/admins.txt") +
                        "\narmenians.txt:\n" + get_file_text("roles/armenians.txt") +
                        "\nstagers.txt:\n" + get_file_text("roles/stagers.txt") +
                        "\ngroups_data.txt:\n" + get_file_text("groups_data.txt"))
    elif split_text[0] in ["н", "нач", "начало", "begin", "b", "beg", "beginning"]:
        if len(split_text) < 3 or \
                (not split_text[1].isdigit()) or (int(split_text[1]) not in range(1, GROUPS_SIZE+1)) \
                or (not (split_text[2].isdigit() or (split_text[2][0] == '-' and split_text[2][1:].isdigit())))\
                or (int(split_text[2]) not in range(-ARMENIAN_SIZE, STAGES_SIZE+1)):
            return Response('Введите запрос в формате:начало [номер группы] [номер этапа]')
        else:
            return handle_stager_response(text, int(split_text[2]), data)
    elif split_text[0] in ["к", "кон", "конец", "финиш", "finish", "fin", "f", "end"]:
        if len(split_text) < 4 or \
                (not split_text[1].isdigit()) or (int(split_text[1]) not in range(1, GROUPS_SIZE + 1)) \
                or (not (split_text[2].isdigit() or (split_text[2][0] == '-' and split_text[2][1:].isdigit()))) \
                or (int(split_text[2]) not in range(-ARMENIAN_SIZE, STAGES_SIZE + 1))\
                or not (split_text[3].isdigit() or (split_text[3][1:].isdigit() and split_text[3][0] == '-')):
            return Response('Введите запрос в формате:конец [номер группы] [номер этапа] [количество баллов]')
        else:
            if split_text[2][0] == '-':
                return handle_armenian_response(
                    split_text[0] + ' ' + split_text[1] + ' ' + split_text[3], int(split_text[2]), data
                )
            else:
                return handle_stager_response(
                    split_text[0] + ' ' + split_text[1] + ' ' + split_text[3], int(split_text[2]), data)
    elif split_text[0] in ['add', 'a', 'add_score', 'add_s', 'a_s', 'as', "добавить", "доб", "добавить_баллы",
                           "доб_бал", "доб_б", "д_б", "дб", "д_бал"]:
        if len(split_text) < 3 or (not split_text[1].isdigit()) or (int(split_text[1]) not in range(1, GROUPS_SIZE+1)):
            return Response('Введите кол-во баллов в формате:добавить_баллы [группа] [количество баллов]')
        elif not (split_text[2].isdigit() or (split_text[2][1:].isdigit() and split_text[2][0] == '-')):
            return Response('Введите кол-во баллов в формате:добавить_баллы [группа] [количество баллов (целое число)]')
        else:
            group_id = split_text[1]
            change = split_text[2]
            data.groups[int(group_id)].scores[0] += int(change)
            rec = set()
            add_recipients(rec, admins=True)
            return Response('Количество баллов ' + group_id + ' группы изменено на ' +
                            change + '. Текущий результат: ' + str(sum(data.groups[int(group_id)].scores) + sum(data.groups[int(group_id)].arm_scores)), rec)
    elif split_text[0] in ['статус', 'стат', 'с', 'status', 'stat', 's']:
        message = "Статус этапов:\n\n"
        # Этапы
        stages = [[] for i in range(STAGES_SIZE + 1)]
        occupied = [False for i in range(STAGES_SIZE + 1)]
        for group in data.groups.values():
            if group.location is not None and group.location in range(1, STAGES_SIZE + 1):
                stages[group.location].append(group.group_id)
                if not group.moving:
                    occupied[group.location] = True

        for i in range(1, STAGES_SIZE + 1):
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

        # Армяне
        stages = [[] for i in range(ARMENIAN_SIZE + 1)]
        occupied = [False for i in range(ARMENIAN_SIZE + 1)]
        for group in data.groups.values():
            if group.location is not None and group.location in range(-ARMENIAN_SIZE, 0):
                stages[-group.location].append(group.group_id)
                if not group.moving:
                    occupied[-group.location] = True

        for i in range(1, ARMENIAN_SIZE + 1):
            num = str(-i) + '. '
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
    elif split_text[0] in ['moving', 'set_moving', 'm', 'sm', 'движение', 'дв', 'движ', 'установить_движение', 'уд']:
        if len(split_text) < 2 or (not split_text[1].isdigit()) or (int(split_text[1]) not in range(1, GROUPS_SIZE+1)):
            return Response('Введите запрос в формате:движение [номер группы] [0/1]')
        else:
            group_id = int(split_text[1])

            moving = False
            if len(split_text) >= 3 and split_text[2] in ['yes', 'да', '+', '1', 'true']:
                moving = True

            data.groups[group_id].set_moving(moving)

            message = 'Группа ' + str(group_id)
            if moving:
                message += ' движется'
            else:
                message += ' стоит'
            return Response(message)

    elif split_text[0] == 'reset':
        data.__init__(True)
        if RESET_COUNT:
            reset_count()

        message = 'ВНИМАНИЕ! Данные сброшены до начальных значений.'
        rec = set()
        add_recipients(rec, admins=True)
        return Response(message, rec)
    elif split_text[0] in ['help*', 'h*', 'помощь*', 'п*', 'help+', 'h+', 'помощь+', 'п+']:
        return Response(get_file_text("help_text/admin+.txt"))
    elif split_text[0] in ["roles", "r", "роли", "р"]:
        return Response(data.get_roles())
    elif split_text[0] in ["count", "cnt", "счетчик", "счет", "сч", "get_count", "gcnt"]:
        return Response(str(get_count()))
    elif split_text[0] in ["set_count", "set_cnt", "scnt", "установить_счетчик", "уст_счет", "уссч"]:
        if len(split_text) < 2 or \
                not (split_text[1].isdigit() or (split_text[1][0] == '-' and split_text[1][1:].isdigit())):
            return Response('Введите число в формате: установить_счетчик [число]')
        else:
            num = int(split_text[1])
            set_count(num)

            return Response('Счетчик установлен на ' + str(get_count()))
    elif split_text[0] in ["reset_count", "reset_cnt", "rcnt", "обнулить_счетчик", "обн_счет", "обсч"]:
        reset_count()
        return Response('Счетчик обнулен')
    else:
        return Response('Недоступная команда: ' + split_text[0])


def handle_stager_response(text: str, stage_id: int, data: Data):
    split_text = text.split()
    if split_text[0] == 'me':
        return Response('stager')
    if split_text[0] in ["н", "нач", "начало", "begin", "b", "beg", "beginning"]:
        if len(split_text) == 1:
            return Response('Введите номер группы в формате:начало [номер группы]')
        elif (not split_text[1].isdigit()) or (int(split_text[1]) not in range(1, GROUPS_SIZE+1)):
            return Response('Введите корректный номер группы в'
                            ' формате:начало [номер группы(от 1 до ' + str(GROUPS_SIZE) + ' )]')
        else:
            group_id = int(split_text[1])
            data.groups[group_id].arrival(stage_id)

            message = 'Группа ' + str(group_id) + ' начала проходить ' + str(stage_id) + ' этап'

            rec = add_recipients(admins=True)
            if stage_id > 0:
                for stager in data.stagers[stage_id]:
                    rec.add(stager.chat_id)
            else:
                for armenian in data.armenians[stage_id]:
                    rec.add(armenian.chat_id)

            return Response(message, rec)
    elif split_text[0] in ["к", "кон", "конец", "финиш", "finish", "fin", "f", "end"]:
        if len(split_text) == 1:
            return Response('Введите номер группы в формате:конец [номер группы] [количество баллов]')
        elif (not split_text[1].isdigit()) or (int(split_text[1]) not in range(1, GROUPS_SIZE+1)):
            return Response('Введите корректный номер группы в формате:'
                            'конец [номер группы(от 1 до ' + str(GROUPS_SIZE) + ' )] [количество баллов]')
        elif len(split_text) < 3:
            return Response('Введите количество баллов в формате: конец '
                            '[номер группы] [количество баллов]')
        elif (not (split_text[2].isdigit() or (split_text[2][1:].isdigit() and split_text[2][0] == '-'))) or\
                (int(split_text[2]) not in range(0, 11)):
            return Response('Введите корректное количество баллов в формате:конец '
                            '[номер группы] [количество баллов (целое число от 0 до 10)]')
        else:
            group_id = int(split_text[1])
            score = int(split_text[2])

            finished = False

            rec = add_recipients(admins=True)
            if stage_id > 0:
                if stage_id in data.groups[group_id].finished_path:
                    finished = True

                data.groups[group_id].scores[stage_id] = score

                for stager in data.stagers[stage_id]:
                    rec.add(stager.chat_id)
            else:
                data.groups[group_id].arm_scores[-stage_id] = score

                for armenian in data.armenians[stage_id]:
                    rec.add(armenian.chat_id)

            data.groups[group_id].finish_location(stage_id)
            message = 'Группа ' + str(group_id) + ' завершила ' \
                      + str(stage_id) + ' этап с результатом: ' + str(score)

            resp = Response(message, rec)

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

                        resp.add(jam_message, add_recipients(admins=True))
                        break

            return resp
    else:
        return Response('Недоступная команда: ' + split_text[0])


def handle_armenian_response(text: str, arm_id: int, data: Data):
    if text == 'me':
        return Response('armenian')

    split_text = text.split()
    if split_text[0] in ["к", "кон", "конец", "финиш", "finish", "fin", "f", "end"]:
        if len(split_text) == 1:
            return Response('Введите номер группы в формате:конец [номер группы] [количество баллов]')
        elif (not split_text[1].isdigit()) or (int(split_text[1]) not in range(1, GROUPS_SIZE + 1)):
            return Response('Введите корректный номер группы в формате:'
                            'конец [номер группы(от 1 до ' + str(GROUPS_SIZE) + ' )] [количество баллов]')
        elif len(split_text) < 3:
            return Response('Введите количество баллов в формате: конец '
                            '[номер группы] [количество баллов]')
        elif (not (split_text[2].isdigit() or (split_text[2][1:].isdigit() and split_text[2][0] == '-'))) or \
                (int(split_text[2]) not in range(0, 4)):
            return Response('Введите корректное количество баллов в формате:конец '
                            '[номер группы] [количество баллов (целое число от 0 до 3)]')

    return handle_stager_response(text, arm_id, data)


async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    if message_type != 'private':
        return

    text = update.message.text.lower()

    chat_id = update.message.chat.id

    if text.split()[0] in ['вопрос', 'request']:
        message = (text[7:]).replace('\n', ' ').strip()
        log_response(update, "logs/question_log.txt", message)
        await update.message.reply_text('Ваше сообщение принято. Спасибо!')
        return

    messages = text.split('\n')

    print(f'User ({chat_id}) in {message_type}: "{text}"')

    for message in messages:
        await handle_message(message, chat_id, update, context)


async def handle_message(text: str, chat_id: int, update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = Response()

    if text in ["да", "д", "конечно", "разумеется", "так точно", "yes", "y", "yep", "ok", "ок", "+"]:
        log_response(update, "logs/answer_log.txt", "Yes")
        response.text = ['Принято']
        if COUNT_YES:
            count_up()
        if ALERT_YES:
            await send_message("Got yes from @" + update.message.chat.username, context.bot, {ELDAR})
    elif text in ["нет", "н", "иди нафиг", "no", "n", "nope", "-"]:
        log_response(update, "logs/answer_log.txt", "No")
        response.text = ['Принято']
        if COUNT_NO:
            count_up()
        if ALERT_NO:
            response.recipients = [{chat_id}]
            await send_message("Got no from @" + update.message.chat.username, context.bot, {ELDAR})
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

    if response is None or response.text is None or response.text == [None] or response.text == '' \
            or response.text == ['']:
        response = handle_response(chat_id, text)

    if response is not None:
        if response.recipients is None or response.recipients == [None]:
            response.recipients = [{chat_id}]

        await response.send(context.bot)
