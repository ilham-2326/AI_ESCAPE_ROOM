"""Member 5 Task 3: compare adaptive agent with a phase-wise plan-once baseline.

The baseline plans once per objective (key, terminal, door, exit) and never
replans within that objective. It waits for moving obstacles and fails if a
planned route becomes permanently invalid. Goal transitions still plan a new
route; this is NOT a single plan for the whole multi-goal escape room.
"""
from __future__ import annotations
import argparse, csv, json, random, sys, time
from pathlib import Path
from datetime import datetime, timezone
ROOT = Path(__file__).resolve().parents[1]
for folder in ('member_1','member_2','member_3','member_4','member_5'):
    sys.path.insert(0,str(ROOT/folder))
from agent import Agent, State
from environment import load_level
from search import ALGORITHMS
from evaluate import parse_seeds

class PlanOnceAgent(Agent):
    """No mid-objective replanning. Reuses original FSM/CSP integration."""
    def update(self):
        if self.state in (State.ESCAPED, State.FAILED): return
        self.step_count += 1
        events = self.env.tick(self.step_count, self.pos)
        for event in events:
            if event.kind == 'rule_changed':
                self._change_rules()
            elif event.kind == 'route_blocked':
                self.last_event = 'Corridor collapsed'
        if self.state == State.FAILED: return
        if self.state == State.SOLVE_PUZZLE:
            result = self.keypad.solve_current()
            if result.status == 'solved' and self.keypad.submit(result.code, result.revision):
                self.state = State.GO_TO_DOOR
                self.last_event = 'Keypad solved'
                self._plan()  # new objective, not replanning
            else:
                self.state = State.FAILED
                self.last_event = 'Puzzle unsolvable'
            return
        goal = self._goal()
        if self.pos == goal:
            self._arrived()
            return
        if self.path is None or self.path_index >= len(self.path):
            self.state = State.FAILED
            self.last_event = 'No planned route'
            return
        next_pos = self.path[self.path_index]
        if not self.env.in_bounds(next_pos) or self.env.is_wall(next_pos):
            self.state = State.FAILED
            self.last_event = 'Original route permanently blocked; no replanning'
            return
        if self.env.is_blocked(next_pos):
            self.waits += 1
            self.consecutive_waits += 1
            self.last_event = 'Waiting on original route'
            return
        self.pos = next_pos
        self.path_cost_total += self.env.cost(self.pos)
        self.path_index += 1
        self.consecutive_waits = 0
        if self.pos == goal: self._arrived()

def trial(level, algorithm, seed, mode, max_steps):
    random.seed(seed)
    started = time.perf_counter()
    row = dict(level=level,algorithm=algorithm,seed=seed,agent_type=mode,success=False,
               final_state='NOT_STARTED',completion_time_seconds=None,simulation_steps=0,
               path_cost=0,states_explored=0,replans=0,waits=0,error='')
    agent = None
    try:
        agent = (Agent if mode=='adaptive' else PlanOnceAgent)(load_level(level,seed=seed),algorithm=algorithm)
        for _ in range(max_steps):
            if agent.state in (State.ESCAPED,State.FAILED): break
            agent.update()
        row.update(success=agent.state==State.ESCAPED,
                   final_state=agent.state.name if agent.state in (State.ESCAPED,State.FAILED) else 'TIMEOUT',
                   simulation_steps=agent.step_count,path_cost=agent.path_cost_total,
                   states_explored=agent.nodes_expanded,replans=agent.replans,waits=agent.waits)
    except Exception as e:
        row['final_state']='ERROR'
        row['error']=f'{type(e).__name__}: {e}'
        if agent is not None:
            for attr,col in [('step_count','simulation_steps'),('path_cost_total','path_cost'),('nodes_expanded','states_explored'),('replans','replans'),('waits','waits')]:
                row[col]=getattr(agent,attr,0)
    row['completion_time_seconds']=round(time.perf_counter()-started,8)
    return row

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--seeds',type=parse_seeds,default=list(range(1,31))+[44])
    p.add_argument('--max-steps',type=int,default=3000)
    p.add_argument('--output-dir',type=Path,default=ROOT/'member_5'/'results')
    a=p.parse_args()
    if len(a.seeds)<30: p.error('At least 30 seeds required')
    a.output_dir.mkdir(parents=True,exist_ok=True)
    rows=[]
    for level in (1,2,3):
        for algo in ALGORITHMS:
            for seed in a.seeds:
                for mode in ('adaptive','plan_once'):
                    rows.append(trial(level,algo,seed,mode,a.max_steps))
        print('Completed level',level,flush=True)
    with (a.output_dir/'baseline_raw.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    import statistics as st
    summary=[]
    for algo in ALGORITHMS:
        for mode in ('adaptive','plan_once'):
            subset=[r for r in rows if r['algorithm']==algo and r['agent_type']==mode]
            successes=[r for r in subset if r['success']]
            rec={'algorithm':algo,'agent_type':mode,'trials':len(subset),'successes':len(successes),'success_rate_pct':round(100*len(successes)/len(subset),2)}
            for metric in ('simulation_steps','path_cost','states_explored','replans','waits','completion_time_seconds'):
                # successful-only means avoid interpreting partial failed paths as full completion costs
                values=[float(r[metric]) for r in successes]
                rec[f'{metric}_success_mean']=round(st.mean(values),4) if values else ''
                rec[f'{metric}_success_sd']=round(st.stdev(values),4) if len(values)>1 else ''
            summary.append(rec)
    with (a.output_dir/'baseline_summary.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
    (a.output_dir/'baseline_metadata.json').write_text(json.dumps({'generated_utc':datetime.now(timezone.utc).isoformat(),'seeds':a.seeds,'max_steps':a.max_steps,'trials':len(rows),'baseline_definition':'One plan per FSM navigation objective, never replan mid-objective; wait for moving obstacles, fail on permanent route invalidation. Rule changes and objective transitions still trigger new planning.'},indent=2))
    for rec in summary: print(rec['algorithm'],rec['agent_type'],rec['successes'],'/',rec['trials'])
if __name__=='__main__': main()
