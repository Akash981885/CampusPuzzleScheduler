from __future__ import annotations

from dataclasses import dataclass
from math import inf

from src.models import Assignment, CourseClass, Problem, Room


@dataclass(frozen=True)
class OptimizerResult:
    assignments: dict[str, Assignment]
    unscheduled: dict[str, str]

    @property
    def total_waste(self) -> int:
        return sum(item.wasted_seats for item in self.assignments.values())


def optimize_rooms_for_fixed_slots(
    problem: Problem,
    class_time_slots: dict[str, str],
) -> OptimizerResult:
    class_by_id = {course.id: course for course in problem.classes}
    assignments: dict[str, Assignment] = {}
    unscheduled: dict[str, str] = {
        course.id: "no graph-colored time slot available"
        for course in problem.classes
        if course.id not in class_time_slots
    }

    for slot in problem.time_slots:
        slot_classes = [
            class_by_id[class_id]
            for class_id, slot_id in class_time_slots.items()
            if slot_id == slot.id and class_id in class_by_id
        ]
        slot_assignments, slot_unscheduled = _assign_slot_with_dp(
            slot.id, slot_classes, problem.rooms
        )
        assignments.update(slot_assignments)
        unscheduled.update(slot_unscheduled)

    return OptimizerResult(assignments=assignments, unscheduled=unscheduled)


def _assign_slot_with_dp(
    time_slot_id: str,
    classes: list[CourseClass],
    rooms: tuple[Room, ...],
) -> tuple[dict[str, Assignment], dict[str, str]]:
    if not classes:
        return {}, {}

    ordered_classes = sorted(classes, key=lambda course: (-course.students, course.id))
    feasible_rooms = {
        course.id: [index for index, room in enumerate(rooms) if room.capacity >= course.students]
        for course in ordered_classes
    }

    unscheduled = {
        course.id: "no room has enough seats"
        for course in ordered_classes
        if not feasible_rooms[course.id]
    }
    schedulable = [course for course in ordered_classes if feasible_rooms[course.id]]

    dp: dict[tuple[int, int], tuple[int, list[tuple[str, int]]]] = {(0, 0): (0, [])}
    for index, course in enumerate(schedulable, start=1):
        next_dp: dict[tuple[int, int], tuple[int, list[tuple[str, int]]]] = {}
        for (previous_index, mask), (cost, path) in dp.items():
            if previous_index != index - 1:
                continue
            for room_index in feasible_rooms[course.id]:
                bit = 1 << room_index
                if mask & bit:
                    continue
                room = rooms[room_index]
                new_cost = cost + (room.capacity - course.students)
                key = (index, mask | bit)
                if new_cost < next_dp.get(key, (inf, []))[0]:
                    next_dp[key] = (new_cost, path + [(course.id, room_index)])
        dp = next_dp
        if not dp:
            remaining = schedulable[index - 1 :]
            for blocked in remaining:
                unscheduled[blocked.id] = "not enough distinct feasible rooms in this time slot"
            break

    if not dp:
        return {}, unscheduled

    best_cost, best_path = min(dp.values(), key=lambda item: item[0])
    del best_cost
    assignments = {
        class_id: Assignment(
            class_id=class_id,
            time_slot_id=time_slot_id,
            room_id=rooms[room_index].id,
            wasted_seats=rooms[room_index].capacity - next(
                course.students for course in schedulable if course.id == class_id
            ),
        )
        for class_id, room_index in best_path
    }
    return assignments, unscheduled
