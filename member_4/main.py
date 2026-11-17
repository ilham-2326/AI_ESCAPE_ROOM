"""Member 4 entry point. Run: python main.py --random 7"""
import argparse
import os
import sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for folder in ("member_1", "member_2", "member_3"):
    sys.path.insert(0, os.path.join(ROOT, folder))
import pygame
from agent import Agent
from renderer import draw
from search import ALGORITHMS
from level_generator import random_level
from environment import load_level


def main():
    parser=argparse.ArgumentParser()
    group=parser.add_mutually_exclusive_group()
    group.add_argument('--level',type=int,choices=(1,2,3))
    group.add_argument('--random',type=int,default=None,metavar='SEED')
    args=parser.parse_args()
    try:
        env=load_level(args.level) if args.level else random_level(args.random if args.random is not None else 7)
    except (FileNotFoundError,ModuleNotFoundError) as exc:
        parser.error(f'Missing level files: {exc}. Use --random 7 until Member 1 levels/ is added.')
    pygame.init()
    screen=pygame.display.set_mode((1100,790))
    pygame.display.set_caption('AI Escape Room | Member 4')
    clock=pygame.time.Clock()
    agent=Agent(env)
    paused=True
    speed=5
    accumulator=0.0
    running=True
    while running:
        elapsed=min(clock.tick(60)/1000.0,0.25)
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False
            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE: running=False
                elif event.key==pygame.K_SPACE: paused=not paused
                elif event.key==pygame.K_r:
                    agent.reset();accumulator=0.0;paused=True
                elif event.key==pygame.K_UP: speed=min(30,speed+1)
                elif event.key==pygame.K_DOWN: speed=max(1,speed-1)
                elif event.key in (pygame.K_1,pygame.K_2,pygame.K_3,pygame.K_4):
                    algo=ALGORITHMS[event.key-pygame.K_1]
                    agent.algorithm=algo
                    agent._plan(replan=True)
        if not paused:
            accumulator+=elapsed
            if accumulator>=1.0/speed:
                accumulator-=1.0/speed
                agent.update()
        draw(screen,agent,paused,speed)
    pygame.quit()


if __name__=='__main__':
    main()
