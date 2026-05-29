from __future__ import annotations

from dataclasses import dataclass

from src.constraints import classes_conflict
from src.models import CourseClass, Problem


ConflictGraph = dict[str, set[str]]


@dataclass(frozen=True)
class GraphColoringResult:
    graph: ConflictGraph
    colors: dict[str, int]
    time_slots: dict[str, str]
    unscheduled: dict[str, str]


def build_conflict_graph(classes: tuple[CourseClass, ...]) -> ConflictGraph:
    graph: ConflictGraph = {course.id: set() for course in classes}
    for index, left in enumerate(classes):
        for right in classes[index + 1 :]:
            if classes_conflict(left, right):
                graph[left.id].add(right.id)
                graph[right.id].add(left.id)
    return graph


def welsh_powell_color(graph: ConflictGraph) -> dict[str, int]:
    ordered_nodes = sorted(graph, key=lambda node: (-len(graph[node]), node))
    colors: dict[str, int] = {}

    for node in ordered_nodes:
        unavailable = {colors[neighbor] for neighbor in graph[node] if neighbor in colors}
        color = 0
        while color in unavailable:
            color += 1
        colors[node] = color

    return colors


def assign_graph_time_slots(problem: Problem) -> GraphColoringResult:
    graph = build_conflict_graph(problem.classes)
    colors = welsh_powell_color(graph)
    sorted_slots = list(problem.time_slots)
    time_slots: dict[str, str] = {}
    unscheduled: dict[str, str] = {}

    for class_id, color in colors.items():
        if color < len(sorted_slots):
            time_slots[class_id] = sorted_slots[color].id
        else:
            unscheduled[class_id] = (
                f"color {color} has no available time slot; add more slots"
            )

    return GraphColoringResult(
        graph=graph,
        colors=colors,
        time_slots=time_slots,
        unscheduled=unscheduled,
    )
