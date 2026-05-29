# Campus Puzzle Scheduler

This is the software component for the M603 Advanced Algorithms project. It builds a best-effort university timetable while enforcing the hard constraints from the brief:

- no professor is booked for two classes at the same time
- no student group is booked for two classes at the same time
- no room is double-booked
- every scheduled class fits inside its assigned room
- room capacity waste is minimized where possible

## Run

```bash
python main.py
```

To use another dataset:

```bash
python main.py --data data/constraints.json
```

Run the verification tests:

```bash
python -m unittest discover -s tests
```

## Structure

- `data/constraints.json` contains classes, rooms, time slots, and student group mappings.
- `src/greedy_solver.py` implements the Stage 1 greedy baseline.
- `src/graph_engine.py` builds the conflict graph and applies Welsh-Powell graph coloring.
- `src/optimizer.py` assigns rooms with dynamic programming after time slots are fixed.
- `src/backtracker.py` performs the recursive best-effort search.
- `main.py` runs every stage and prints the conflict report.

## Algorithm Notes

Stage 1 sorts classes by difficulty, using enrolment size first because large classes have fewer feasible rooms. It then takes the first time-slot and input-order room pair that does not break a hard constraint, so it is fast but does not optimize room waste.

Stage 2 creates a conflict graph. Each class is a node, and an edge means the two classes share a professor or at least one student group. Welsh-Powell coloring assigns high-degree classes first, producing time groups where adjacent classes cannot overlap.

Running `python main.py` prints the graph coloring result as a safe time-slot map, plus the unsafe classes if there are not enough colors/time slots.

Stage 3 fixes the graph-colored time slots and optimizes room allocation one slot at a time. The dynamic programming state is `(class_index, used_room_mask)`, and the recurrence chooses a feasible unused room with minimum added waste. This avoids directly enumerating every full room allocation when a slot has multiple classes.

Stage 4 uses backtracking for tight cases. It orders classes by graph degree and enrolment, tries smallest suitable rooms first, prunes branches that cannot beat the best schedule found, and returns the best partial schedule if a complete one is not found within the search limits.

## Manual Fix Log

If the final report contains `Unscheduled` classes, a university manager can inspect the reason beside each class. Typical fixes are adding a larger room, opening another time slot, splitting an oversized class, or manually moving a low-priority class after consulting the professor and affected student groups.
