from __future__ import annotations

from dataclasses import dataclass

from src.constraints import assignment_is_valid
from src.models import Assignment, Problem


@dataclass(frozen=True)
class GreedyResult:
    assignments: dict[str, Assignment]
    unscheduled: dict[str, str]

    @property
    def total_waste(self) -> int:
        return sum(item.wasted_seats for item in self.assignments.values())


def solve_greedy(problem: Problem) -> GreedyResult:
    class_by_id = {course.id: course for course in problem.classes}
    rooms_in_input_order = list(problem.rooms)
    classes_by_difficulty = sorted(
        problem.classes,
        key=lambda course: (course.students, len(course.groups), course.id),
        reverse=True,
    )

    assignments: dict[str, Assignment] = {}
    unscheduled: dict[str, str] = {}

    for course in classes_by_difficulty:
        placed = False
        for slot in problem.time_slots:
            for room in rooms_in_input_order:
                if assignment_is_valid(course, room, slot.id, assignments, class_by_id):
                    assignments[course.id] = Assignment(
                        class_id=course.id,
                        time_slot_id=slot.id,
                        room_id=room.id,
                        wasted_seats=room.capacity - course.students,
                    )
                    placed = True
                    break
            if placed:
                break
        if not placed:
            max_capacity = max(room.capacity for room in problem.rooms)
            if course.students > max_capacity:
                unscheduled[course.id] = (
                    f"needs {course.students} seats, largest room has {max_capacity}"
                )
            else:
                unscheduled[course.id] = "no conflict-free room and time slot found"

    return GreedyResult(assignments=assignments, unscheduled=unscheduled)
