"""
events.py - dynamic-event configuration for each level (Member 1).

Keys
  obstacle_patrol : {obstacle_id: [cells...]}  loop, first cell = map 'M' position,
                    consecutive cells must be adjacent. The guard moves one cell
                    per tick and turns around if the agent is in its way.
  collapse        : {"step": s, "cells": [...]}  'C' tiles that become walls at step s
  rule_change     : {"step": s}                  emits a "rule_changed" event for the
                                                 CSP / FSM (Members 3 & 4)
Obstacle ids are assigned M1, M2, ... in reading order (top-to-bottom, left-to-right).
"""

def _back_and_forth(cells):
    """[a,b,c,d] -> [a,b,c,d,c,b] so the obstacle walks a line and returns."""
    return list(cells) + list(cells[-2:0:-1])

LEVEL_EVENTS = {
    # Level 1 - EASY: static, no dynamic elements (baseline)
    1: {},

    # Level 2 - MEDIUM: one guard in the corridor to the terminal,
    # the short route to the key collapses at step 8.
    2: {
        "obstacle_patrol": {
            "M1": _back_and_forth([(9, c) for c in range(5, 11)]),
        },
        "collapse": {"step": 8, "cells": [(5, 9)]},
    },

    # Level 3 - HARD: two guards, the obvious route collapses at step 6,
    # mud on the detour, puzzle rules change at step 70.
    3: {
        "obstacle_patrol": {
            "M1": _back_and_forth([(9, c) for c in range(11, 19)]),
            "M2": _back_and_forth([(17, c) for c in range(13, 7, -1)]),
        },
        "collapse": {"step": 6, "cells": [(5, 7)]},
        "rule_change": {"step": 70},
    },
}
