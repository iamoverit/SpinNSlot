import datetime
import dataclasses
from django.conf import settings

@dataclasses.dataclass
class DaySlot:
    id: int
    day: datetime.date

def prepare_schedule(schedule, timeSlots, itemSlots):
    merged_cells = {}  # Словарь для хранения объединенных ячеек

    # Создаем структуру с флагами объединения
    for i, timeSlot in enumerate(timeSlots):
        for j, itemSlot in enumerate(itemSlots):
            userSlot = schedule.get(timeSlot.id, {}).get(itemSlot.id, None)
            if not userSlot:
                continue  # Пропускаем пустые ячейки
            
            # Если уже объединена, пропускаем
            if (i, j) in merged_cells:
                continue

            # Проверяем возможность объединения по горизонтали (вправо)
            for next_j in range(j, len(itemSlots)):
                for next_i in range(i, len(timeSlots)):
                    next_slot = schedule.get(timeSlots[next_i].id, {}).get(itemSlots[next_j].id, None)
                    if next_slot["type"] == userSlot["type"] and userSlot["type"] == "tournament" and next_slot["compare_by"] == userSlot["compare_by"]:
                        userSlot["colspan"] = next_j - j + 1
                        userSlot["rowspan"] = next_i - i + 1
                        merged_cells[(next_i, next_j)] = True  # Отмечаем ячейку как объединенную
                    else:
                        break  # Прерываем, если следующий слот отличается

            userSlot["merged"] = True  # По умолчанию не объединена
    return schedule

def get_week_range(selected_date):
    """
    Принимает дату и возвращает кортеж (дата_понедельника, дата_воскресенья)
    для недели, в которую входит выбранная дата.
    """
    if isinstance(selected_date, str):
        selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()

    # Определяем, какой день недели (0 = Понедельник, 6 = Воскресенье)
    weekday = selected_date.weekday()

    # Вычисляем понедельник и воскресенье
    monday = selected_date
    if settings.WEEK_START_FROM_MONDAY:
        monday = selected_date - datetime.timedelta(days=weekday)
    sunday = monday + datetime.timedelta(days=6)

    return monday, sunday


def week_date_iterator(start_date, end_date):
    """
    Генератор, который итерируется от start_date до end_date (включительно).
    """
    current_date = start_date
    while current_date <= end_date:
        yield current_date
        current_date += datetime.timedelta(days=1)