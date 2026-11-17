"""
demo_search.py - Member 2 demo (no Pygame needed)

  python demo_search.py              # algorithm comparison on all levels
  python demo_search.py --watch 3    # watch the agent escape level 3, replanning live
"""
import argparse
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(os.path.dirname(HERE), "member_1")]
from environment import load_level              # noqa: E402
from search import ALGORITHMS, navigate, plan   # noqa: E402


def compare():
    print(f"{'level':<6}{'leg':<8}{'algo':<10}{'cost':>6}{'steps':>7}{'expanded':>10}{'ms':>8}")
    for lv in (1, 2, 3):
        env = load_level(lv)
        env.door_open = True
        legs = {"S->K": (env.start, env.key_pos),
                "K->T": (env.key_pos, env.terminal_pos),
                "T->E": (env.terminal_pos, env.exit)}
        for leg, (a, b) in legs.items():
            for algo in ALGORITHMS:
                _, st = plan(env, a, b, algo)
                print(f"{lv:<6}{leg:<8}{algo:<10}{st['path_cost']:>6}"
                      f"{st['path_length']:>7}{st['nodes_expanded']:>10}{st['time_ms']:>8.2f}")
        print()
    # explored-area picture for the report
    env = load_level(3)
    for algo in ("bfs", "astar"):
        path, st, explored = plan(env, env.start, env.key_pos, algo, return_explored=True)
        print(f"Level 3 S->K  {algo}: expanded {st['nodes_expanded']} ('o' = explored, '*' = path)")
        pic = [list(r) for r in env.render(path).splitlines()]
        for (r, c) in explored:
            if pic[r][c] == ".":
                pic[r][c] = "o"
        print("\n".join("".join(r) for r in pic), "\n")


def watch(lv, algo, strategy, delay):
    env = load_level(lv)
    step, pos, total = 0, env.start, {"replans": 0, "waits": 0, "cost": 0}

    def draw(s, p, path):
        os.system("cls" if os.name == "nt" else "clear")
        print(f"Level {lv} | {algo} | {strategy} | step {s} | leg -> {label}")
        print(env.render(path, agent=p))
        time.sleep(delay)

    for i, (label, goal) in enumerate((("KEY", env.key_pos), ("TERMINAL", env.terminal_pos),
                                       ("EXIT", env.exit))):
        if i == 2:
            env.door_open = True
        log = navigate(env, pos, goal, algo, start_step=step,
                       obstacle_strategy=strategy, on_step=draw)
        step, pos = log["end_step"], log["end_pos"]
        total["replans"] += log["replans"]
        total["waits"] += log["waits"]
        total["cost"] += log["path_cost"]
        if not log["success"]:
            print("FAILED on leg", label)
            return
    print(f"\nESCAPED in {step} steps | path cost {total['cost']} | "
          f"replans {total['replans']} | waits {total['waits']}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--watch", type=int, choices=[1, 2, 3])
    ap.add_argument("--algo", default="astar", choices=ALGORITHMS)
    ap.add_argument("--strategy", default="wait_or_detour",
                    choices=["replan", "wait_or_detour"])
    ap.add_argument("--delay", type=float, default=0.12)
    a = ap.parse_args()
    watch(a.watch, a.algo, a.strategy, a.delay) if a.watch else compare()
