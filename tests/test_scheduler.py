from __future__ import annotations

import unittest

from src.backtracker import solve_with_backtracking
from src.constraints import classes_conflict
from src.io_utils import read_problem
from src.models import CourseClass, Problem, Room, TimeSlot


class SchedulerTests(unittest.TestCase):
    def test_backtracking_solution_respects_hard_constraints(self) -> None:
        problem = read_problem("data/constraints.json")
        result = solve_with_backtracking(problem, time_limit_seconds=1)
        class_by_id = {course.id: course for course in problem.classes}
        room_by_id = {room.id: room for room in problem.rooms}

        self.assertEqual(len(result.assignments), len(problem.classes))
        for assignment in result.assignments.values():
            course = class_by_id[assignment.class_id]
            room = room_by_id[assignment.room_id]
            self.assertGreaterEqual(room.capacity, course.students)

        scheduled = list(result.assignments.values())
        for index, left_assignment in enumerate(scheduled):
            for right_assignment in scheduled[index + 1 :]:
                if left_assignment.time_slot_id != right_assignment.time_slot_id:
                    continue
                self.assertNotEqual(left_assignment.room_id, right_assignment.room_id)
                left = class_by_id[left_assignment.class_id]
                right = class_by_id[right_assignment.class_id]
                self.assertFalse(classes_conflict(left, right))

    def test_oversized_class_is_reported_unscheduled(self) -> None:
        problem = Problem(
            classes=(
                CourseClass(
                    id="BIG101",
                    title="Oversized Lecture",
                    professor="Prof A",
                    students=999,
                    groups=("G1",),
                ),
            ),
            rooms=(Room(id="R1", campus="Test", capacity=20),),
            time_slots=(TimeSlot(id="MON-09", day="Monday", start="09:00", end="10:00"),),
            student_groups={"G1": ("BIG101",)},
        )

        result = solve_with_backtracking(problem, time_limit_seconds=1)

        self.assertFalse(result.complete)
        self.assertEqual(result.assignments, {})
        self.assertIn("BIG101", result.unscheduled)
        self.assertIn("largest room", result.unscheduled["BIG101"])


if __name__ == "__main__":
    unittest.main()
