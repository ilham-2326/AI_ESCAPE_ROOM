"""
demo_environment.py - Member 1 demo (no Pygame needed)

  python demo_environment.py            # show all 3 levels + event schedule
  python demo_environment.py --play 3   # animate level 3's dynamics in the terminal
"""
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from environment import load_level  # noqa: E402

NAMES = {1: "EASY (static)", 2: "MEDIUM (1 guard + collapse)",
         3: "HARD (2 guards + collapse + rule change)"}


def show_all():
    for lv in (1, 2, 3):
        env = load_level(lv)
        print(f"=== Level {lv}: {NAMES[lv]}  ({env.h}x{env.w}) ===")
        env.print_grid()
        print("events:", env.event_schedule(), "\n")


def play(lv, steps, delay):
    env = load_level(lv)
    for s in range(1, steps + 1):
        events = env.tick(s)
        os.system("cls" if os.name == "nt" else "clear")
        print(f"Level {lv}  step {s}")
        env.print_grid()
        for e in events:
            if e.kind != "obstacle_moved":
                print(f"  >>> EVENT: {e.kind} {e.data}")
        time.sleep(delay)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--play", type=int, choices=[1, 2, 3])
    ap.add_argument("--steps", type=int, default=40)
    ap.add_argument("--delay", type=float, default=0.15)
    a = ap.parse_args()
    play(a.play, a.steps, a.delay) if a.play else show_all()
