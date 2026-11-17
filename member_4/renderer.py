"""Member 4 Pygame renderer: responsive grid, path overlay and HUD."""
import pygame

COLORS = {
    '#': (51, 65, 85), '.': (28, 42, 58), '~': (131, 92, 52),
    'C': (153, 103, 48), 'S': (39, 85, 119), 'K': (174, 135, 39),
    'T': (103, 76, 151), 'D': (156, 70, 68), 'E': (42, 130, 97),
}
BG = (13, 20, 31)
TEXT = (235, 240, 246)
MUTED = (163, 177, 196)


def draw(screen, agent, paused=False, speed=5):
    env = agent.env
    screen.fill(BG)
    width, height = screen.get_size()
    side = 290
    margin = 24
    tile = max(8, min((width-side-2*margin)//env.w, (height-2*margin)//env.h))
    ox, oy = margin, margin
    font = pygame.font.SysFont('arial', 18)
    small = pygame.font.SysFont('arial', 15)
    heading = pygame.font.SysFont('arial', 23, bold=True)
    for r in range(env.h):
        for c in range(env.w):
            p = (r,c)
            ch = env.grid[r][c]
            rect = pygame.Rect(ox+c*tile, oy+r*tile, tile-1, tile-1)
            pygame.draw.rect(screen, COLORS.get(ch, COLORS['.']), rect, border_radius=2)
            if ch == 'D' and env.door_open:
                pygame.draw.rect(screen, (40, 132, 100), rect, border_radius=2)
    for p in agent.explored:
        if p != agent.pos and env.grid[p[0]][p[1]] != '#':
            x,y=ox+p[1]*tile+tile//2,oy+p[0]*tile+tile//2
            pygame.draw.circle(screen,(74,102,134),(x,y),max(2,tile//7))
    if agent.path:
        for p in agent.path[agent.path_index:]:
            x,y=ox+p[1]*tile+tile//2,oy+p[0]*tile+tile//2
            pygame.draw.circle(screen,(92,199,238),(x,y),max(3,tile//5))
    for p in env.obstacles.values():
        x,y=ox+p[1]*tile+tile//2,oy+p[0]*tile+tile//2
        pygame.draw.circle(screen,(243,112,107),(x,y),max(4,tile//3))
    x,y=ox+agent.pos[1]*tile+tile//2,oy+agent.pos[0]*tile+tile//2
    pygame.draw.circle(screen,(253,211,96),(x,y),max(5,tile//3))
    pygame.draw.circle(screen,(255,255,255),(x,y),max(5,tile//3),2)
    sx=width-side+8
    screen.blit(heading.render('AI ESCAPE ROOM',True,TEXT),(sx,28))
    info=[
        ('State',agent.state.name.replace('_',' ')),
        ('Algorithm',agent.algorithm.upper()),
        ('Steps',str(agent.step_count)),
        ('Key collected','YES' if agent.has_key else 'NO'),
        ('Keypad solved','YES' if agent.keypad.solved else 'NO'),
        ('Door open','YES' if env.door_open else 'NO'),
        ('Nodes expanded',str(agent.nodes_expanded)),
        ('Replans',str(agent.replans)),
        ('Waits',str(agent.waits)),
        ('Travel cost',str(agent.path_cost_total)),
        ('Speed',f'{speed} steps/sec'),
        ('Simulation','PAUSED' if paused else 'RUNNING'),
    ]
    yy=90
    for label,value in info:
        screen.blit(small.render(label,True,MUTED),(sx,yy))
        screen.blit(font.render(value,True,TEXT),(sx,yy+19))
        yy+=47
    yy=max(yy+12,height-150)
    screen.blit(small.render('Latest event:',True,MUTED),(sx,yy))
    message=agent.last_event
    for i in range(0,len(message),32):
        screen.blit(small.render(message[i:i+32],True,TEXT),(sx,yy+22+(i//32)*20))
    screen.blit(small.render('SPACE pause | R reset | 1-4 algo',True,MUTED),(margin,height-45))
    screen.blit(small.render('UP/DOWN speed | ESC quit',True,MUTED),(margin,height-24))
    pygame.display.flip()
