from __future__ import annotations

import argparse
from pathlib import Path

from src.backtracker import solve_with_backtracking
from src.graph_engine import assign_graph_time_slots
from src.greedy_solver import solve_greedy
from src.io_utils import read_problem
from src.optimizer import optimize_rooms_for_fixed_slots
from src.reporting import print_graph_slot_map, print_schedule_report, summarize


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Campus Puzzle Scheduler")
    parser.add_argument(
        "--data",
        default="data/constraints.json",
        help="Path to the scheduling constraints JSON file.",
    )
    parser.add_argument(
        "--backtracking-seconds",
        type=float,
        default=5.0,
        help="Maximum seconds for the best-effort backtracking stage.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    problem = read_problem(Path(args.data))

    print("Campus Puzzle Scheduler")
    print("=" * 24)
    print(f"Classes: {len(problem.classes)}")
    print(f"Rooms: {len(problem.rooms)}")
    print(f"Time slots: {len(problem.time_slots)}")
    print()

    greedy = solve_greedy(problem)
    print("Stage 1 - Greedy Baseline")
    print(summarize(greedy.assignments, len(problem.classes)))
    if greedy.unscheduled:
        print(f"Unscheduled by greedy: {len(greedy.unscheduled)}")
    print()

    graph = assign_graph_time_slots(problem)
    edge_count = sum(len(neighbors) for neighbors in graph.graph.values()) // 2
    print("Stage 2 - Conflict Graph and Welsh-Powell Coloring")
    print(f"Conflict edges: {edge_count}")
    print(f"Colors/time groups used: {max(graph.colors.values(), default=-1) + 1}")
    print(f"Classes without graph time slot: {len(graph.unscheduled)}")
    print("Safe time-slot map:")
    print_graph_slot_map(graph, problem.classes, problem.time_slots)
    print()

    optimized = optimize_rooms_for_fixed_slots(problem, graph.time_slots)
    print("Stage 3 - DP Room Allocation")
    print(summarize(optimized.assignments, len(problem.classes)))
    print(f"Waste improvement over greedy: {greedy.total_waste - optimized.total_waste}")
    if optimized.unscheduled:
        print(f"Unscheduled after DP: {len(optimized.unscheduled)}")
    print()

    backtracked = solve_with_backtracking(
        problem,
        time_limit_seconds=args.backtracking_seconds,
    )
    print("Stage 4 - Backtracking Best Effort")
    print(summarize(backtracked.assignments, len(problem.classes)))
    print(f"Complete solution: {'yes' if backtracked.complete else 'no'}")
    print(f"Search nodes visited: {backtracked.nodes_visited}")
    print()

    print("Final Conflict Report")
    print("-" * 21)
    print_schedule_report(
        backtracked.assignments,
        backtracked.unscheduled,
        problem.classes,
        problem.rooms,
        problem.time_slots,
    )


if __name__ == "__main__":
    main()
