from code.settings import *


class Group:
    def __init__(self, group_id: int, start_location: int):
        self.group_id = group_id
        self.finished_path = [-1]
        self.future_path = [((i+group_id-1) % SIZE)+1 for i in range(SIZE)]
        self.location = start_location
        self.moving = True
        self.scores = [0 for i in range(SIZE+2)]

    def arrival(self, location_id: int):
        self.location = location_id
        self.moving = False

    def finish_location(self, location_id: int):
        if location_id not in self.finished_path:
            if self.finished_path == [-1]:
                self.finished_path = []
            self.finished_path.append(location_id)

        erase_ids = [i for i in range(len(self.future_path) - 1, -1, -1) if self.future_path[i] == location_id]
        for erase_id in erase_ids:
            self.future_path.pop(erase_id)

        if len(self.future_path) == 0:
            self.future_path = [-1]

        self.moving = True
        self.location = self.future_path[0]

    def get_path(self, future=True):
        path = self.finished_path
        if future:
            path = self.future_path

        if len(path) == 0:
            return '-1'

        str_path = str(path[0])
        for i in range(1, len(path)):
            str_path += "-" + str(path[i])
        return str_path
