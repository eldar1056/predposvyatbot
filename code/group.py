from code.settings import *


# Информация о положении группы и ее оценках. Хранятся пройденный и будущий путь группы в массивах
class Group:
    def __init__(self, group_id: int, start_location: int):
        self.group_id: int = group_id
        self.finished_path: list[int] = [0]
        self.future_path: list[int] = [((i+group_id-1) % STAGES_SIZE)+1 for i in range(STAGES_SIZE)]
        self.location: int = start_location
        self.moving: bool = True
        self.scores: list[int] = [0 for i in range(STAGES_SIZE+1)]
        self.arm_scores: list[int] = [0 for i in range(ARMENIAN_SIZE+1)]

    # Когда происходит начало на этапе
    def arrival(self, location_id: int):
        self.location = location_id
        self.moving = False

    # Когда происходит конец на этапе
    def finish_location(self, location_id: int):
        if location_id not in self.finished_path:
            if self.finished_path == [0]:
                self.finished_path = []
            self.finished_path.append(location_id)

        erase_ids = [i for i in range(len(self.future_path) - 1, -1, -1) if self.future_path[i] == location_id]
        for erase_id in erase_ids:
            self.future_path.pop(erase_id)

        if len(self.future_path) == 0:
            self.future_path = [0]

        self.moving = True
        self.location = self.future_path[0]

    # Получить строку с прошлым или будущим путем группы
    def get_path(self, finished=True, future=False) -> str:
        if not future and not finished:
            return '0'
        if len(self.future_path) == 0 and len(self.finished_path) == 0:
            return '0'

        str_path = ""

        if finished and len(self.finished_path) != 0:
            if future and finished:
                str_path += "Прошлый: "
            str_path += str(self.finished_path[0])
            for i in range(1, len(self.finished_path)):
                str_path += "/" + str(self.finished_path[i])
        if future and len(self.future_path) != 0:
            if future and finished:
                str_path += "\nБудущий: "
            str_path += str(self.future_path[0])
            for i in range(1, len(self.future_path)):
                str_path += "/" + str(self.future_path[i])

        return str_path

    def set_moving(self, moving: bool):
        self.moving = moving
