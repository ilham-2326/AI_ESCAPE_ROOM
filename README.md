# 🔐 AI Escape Room

An autonomous AI agent that escapes a dynamic grid-world room: it **finds a key, solves a keypad puzzle, unlocks the door and reaches the exit**, while guards patrol, floors collapse and puzzle rules change mid-run.

Built for **CSCI218 – Foundations of AI** at the University of Wollongong in Dubai.

---

## 🎯 What we're doing
We combine three core AI techniques in one agent:

| Technique | Used for |
|---|---|
| **Search** (BFS, Dijkstra, Greedy, A\*) | Planning paths through the room |
| **Adaptive replanning** | Reacting to collapsing routes and moving guards |
| **Constraint Satisfaction (CSP)** | Cracking the 4-digit keypad code |
| **Finite State Machine (FSM)** | Deciding what to do next |

## ⚙️ How it works
```
FIND_KEY → GO_TO_TERMINAL → SOLVE_PUZZLE → GO_TO_DOOR → GO_TO_EXIT → ESCAPED
                 ▲                              │
                 └──────── rule changed ────────┘
```
- **Guards** (temporary block): the agent waits or takes a short detour  
- **Collapsing floor** (permanent block): the agent replans from where it is  
- **Rule change**: the old code becomes invalid, so the agent goes back and re-solves  
- **Keypad CSP:** 4 digits, sum = 20, first digit > third, all digits different (solved with backtracking + forward checking)

## 💡 Why it's useful
It shows how an agent can **plan, adapt and reason under changing conditions**, the same problem behind robot navigation, game AI, warehouse automation and scheduling. It also lets us compare the algorithms fairly in the same environment.

## 🏗️ Architecture
```
        Pygame GUI / Evaluation
                  │
          Agent (FSM) ── member_4
           │         │
   Search ─┘         └─ CSP Solver
  member_2              member_3
       │
  Environment ── member_1
  (map, guards, collapses, rule changes)
```

## 📁 Repository Structure
```
AI_ESCAPE_ROOM/
├── member_1/   environment.py, levels/, level_generator.py, tests/
├── member_2/   search.py, demo_search.py, benchmark_search.py
├── member_3/   csp_solver.py, keypad.py, benchmark.py, results/
├── member_4/   agent.py, main.py, renderer.py, test_agent.py
└── member_5/   evaluate.py, raw_results.csv
```

## 👥 Team
| Member | Area | Folder |
|---|---|---|
| Ilham shaikh          | Environment, levels & dynamic events | [`member_1/`](member_1/) |
| Anasha Khan            | Search algorithms & replanning | [`member_2/`](member_2/) |
| Amir Hussain khan      | CSP keypad solver | [`member_3/`](member_3/) |
| Mohammed Ahmed Noumnan | FSM agent, integration & GUI | [`member_4/`](member_4/) |
| Zaid Rehman            | Evaluation & experiments | [`member_5/`](member_5/) |

## 🚀 Run it
```bash
pip install pygame
python member_4/main.py --level 3      # levels 1–3, or --random 7
python member_5/evaluate.py            # headless experiments
```
**Controls:** `Space` pause · `R` reset · `1–4` switch algorithm · `↑/↓` speed · `Esc` quit

## 📊 Key Results
**All 372 test runs escaped** (3 levels × 4 algorithms × 31 seeds).

- **A\*** found the lowest-cost path on every level.
- On the Hard level, A\* explored about **3.5× fewer states than Dijkstra**.
- Forward checking cut the keypad solver's search on hard puzzles from **~143 attempts to ~6**.
