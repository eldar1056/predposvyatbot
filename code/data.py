from code.group import Group
from code.settings import *


def get_lines(filename: str):
    lines = []
    with open(filename) as file:
        for line in file:
            lines.append(line.strip())
    return lines


class Stager:
    def __init__(self, array):
        self.chat_id = int(array[0])
        self.username = array[1]
        self.stage_id = int(array[2])


class Data:
    def __init__(self, erase_data=False):
        self.stagers = {}
        self.admins = []
        self.armenians = []
        self.groups = {}

        if erase_data:
            self.groups = {i: Group(i, i) for i in range(1, SIZE + 1)}
            import_roles(self)
            store_data(self)
        else:
            import_data(self)

    def check_collisions(self):
        ids = []
        collisions = []
        for admin in self.admins:
            if admin in ids:
                collisions.append(admin)
            else:
                ids.append(admin)
        for armenian in self.armenians:
            if armenian.chat_id in ids:
                collisions.append(armenian.chat_id)
            else:
                ids.append(armenian.chat_id)
        for key in self.stagers.keys():
            for stager in self.stagers[key]:
                if stager.chat_id in ids:
                    collisions.append(stager.chat_id)
                else:
                    ids.append(stager.chat_id)

        return collisions

    def get_roles(self):
        line = 'admins:'
        if len(self.admins) == 0:
            line += '[]'
        else:
            line += '['
            for admin in self.admins:
                line += str(admin) + ', '
            line = line[:-2]
            line += ']'
        line += "\nstagers:\n"
        for key, stagers in self.stagers.items():
            line += str(key) + '.['

            if len(stagers) > 0:
                for stager in stagers:
                    line += 'chat_id=' + str(stager.chat_id) + \
                            ' username=' + stager.username + ' stage_id=' + str(stager.stage_id) + ', '
                line = line[:-2]

            line += ']\n'

        line += "armenians:"
        if len(self.armenians) == 0:
            line += '[]'
        else:
            line += '['
            for armenian in self.armenians:
                line += 'chat_id=' + str(armenian.chat_id) + ' username=' + armenian.username + ', '
            line = line[:-2]
            line += ']'

        return line

    def store(self, change_roles=False):
        store_data(self, change_roles)


def import_data(data: Data):
    import_roles(data)

    data.groups = {}
    with open("groups_data.txt") as file:
        for line in file:
            if line.strip() == '':
                continue

            split_line = line.split()
            group_id = int(split_line[0])
            finished_path = [-1]
            if split_line[1] != '-1':
                finished_path = [int(loc) for loc in split_line[1].split('-')]
            future_path = [-1]
            if split_line[2] != '-1':
                future_path = [int(loc) for loc in split_line[2].split('-')]
            group_location = int(split_line[3])
            group_moving = False
            if split_line[4] == "True":
                group_moving = True
            scores = [int(score) for score in split_line[5:]]

            data.groups[group_id] = Group(group_id, group_location)
            data.groups[group_id].finished_path = finished_path
            data.groups[group_id].future_path = future_path
            data.groups[group_id].moving = group_moving
            data.groups[group_id].scores = scores


def import_roles(data: Data):
    data.stagers = {i: [] for i in range(1, SIZE + 1)}
    data.admins = [int(line.strip()) for line in get_lines("roles/admins.txt") if not line.strip() == '']
    data.armenians = [Stager([line.split()[0], line.split()[1], 0])
                      for line in get_lines("roles/armenians.txt") if not line.strip() == '']

    stager_lines = get_lines("roles/stagers.txt")
    for line in stager_lines:
        if line.strip() == '':
            continue
        split_line = line.split()
        data.stagers[int(split_line[2])].append(Stager(split_line))

    col = data.check_collisions()
    if len(col) > 0:
        print("Collisions detected:", col)


def store_roles(data: Data):
    with open("roles/stagers.txt", "w") as stagers_file:
        for stager in data.stagers:
            stagers_file.write(str(stager.chat_id) + stager.username + str(stager.stage_id) + '\n')
    with open("roles/armenians.txt", "w") as armenians_file:
        for armenian in data.armenians:
            armenians_file.write(str(armenian.chat_id) + armenian.username + '\n')
    with open("roles/admins.txt", "w") as admins_file:
        for admin in data.admins:
            admins_file.write(str(admin) + '\n')


def store_data(data: Data, change_roles=False):
    if change_roles:
        store_roles(data)

    with open("groups_data.txt", "w") as file:
        for group in data.groups.values():
            file.write(str(group.group_id) + ' ' + group.get_path(False) +
                       ' ' + group.get_path(True) + ' ' + str(group.location) + ' ' + str(group.moving))
            for score in group.scores:
                file.write(' ' + str(score))
            file.write('\n')
