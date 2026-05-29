from __future__ import annotations

from dataclasses import dataclass
from time import monotonic

from src.constraints import assignment_is_valid
from src.graph_engine import build_conflict_graph
from src.models import Assignment, Problem


@dataclass(frozen=True)
class BacktrackingResult:
    assignments: dict[str, Assignment]
    unscheduled: dict[str, str]
    complete: bool
    nodes_visited: int
    total_waste: int


def solve_with_backtracking(
    problem: Problem,
    *,
    time_limit_seconds: float = 5.0,
    node_limit: int = 200_000,
) -> BacktrackingResult:
    class_by_id = {course.id: course for course in problem.classes}
    graph = build_conflict_graph(problem.classes)
    ordered_classes = sorted(
        problem.classes,
        key=lambda course: (-len(graph[course.id]), -course.students, course.id),
    )
    rooms_by_fit = sorted(problem.rooms, key=lambda room: (room.capacity, room.id))
    largest_room = max(room.capacity for room in problem.rooms)

    best_assignments: dict[str, Assignment] = {}
    best_waste = 10**12
    nodes_visited = 0
    started = monotonic()

    def is_better(candidate: dict[str, Assignment]) -> bool:
        nonlocal best_waste
        candidate_waste = sum(item.wasted_seats for item in candidate.values())
        if len(candidate) > len(best_assignments):
            return True
        return len(candidate) == len(best_assignments) and candidate_waste < best_waste

    def remember(candidate: dict[str, Assignment]) -> None:
        nonlocal best_assignments, best_waste
        if is_better(candidate):
            best_assignments = dict(candidate)
            best_waste = sum(item.wasted_seats for item in candidate.values())

    def dfs(index: int, current: dict[str, Assignment]) -> bool:
        nonlocal nodes_visited
        nodes_visited += 1
        remember(current)

        if nodes_visited >= node_limit or monotonic() - started >= time_limit_seconds:
            return False
        if index == len(ordered_classes):
            return True
        if len(current) + (len(ordered_classes) - index) < len(best_assignments):
            return False

        course = ordered_classes[index]
        if course.students > largest_room:
            return dfs(index + 1, current)

        candidates: list[tuple[int, str, str, Assignment]] = []
        for slot in problem.time_slots:
            for room in rooms_by_fit:
                if assignment_is_valid(course, room, slot.id, current, class_by_id):
                    assignment = Assignment(
                        class_id=course.id,
                        time_slot_id=slot.id,
                        room_id=room.id,
                        wasted_seats=room.capacity - course.students,
                    )
                    candidates.append(
                        (assignment.wasted_seats, slot.id, room.id, assignment)
                    )

        for _, __, ___, assignment in sorted(candidates):
            current[course.id] = assignment
            if dfs(index + 1, current):
                return True
            del current[course.id]

        return dfs(index + 1, current)

    complete = dfs(0, {})
    unscheduled: dict[str, str] = {}
    for course in problem.classes:
        if course.id in best_assignments:
            continue
        if course.students > largest_room:
            unscheduled[course.id] = (
                f"needs {course.students} seats, largest room has {largest_room}"
            )
        else:
            unscheduled[course.id] = "manual intervention required after best-effort search"

    return BacktrackingResult(
        assignments=best_assignments,
        unscheduled=unscheduled,
        complete=complete and len(best_assignments) == len(problem.classes),
        nodes_visited=nodes_visited,
        total_waste=sum(item.wasted_seats for item in best_assignments.values()),
    )
