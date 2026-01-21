import sys
import random
from collections import deque
from colorama import init
init()

WALL = 0
ROAD = 1
ENTRANCE = 2
EXIT = 3
TRAP = 4

C_RESET = "\x1b[0m"
C_DIM = "\x1b[2m"
C_WALL = "\x1b[90m"
C_ROAD = "\x1b[97m"
C_ENT = "\x1b[92m"
C_EXIT = "\x1b[91m"
C_TRAP = "\x1b[93m"

def make_grid(h, w, fill=WALL):
    return [[fill for _ in range(w)] for _ in range(h)]

def neighbors_cell(r, c, ch, cw):
    if r > 0: yield (r - 1, c)
    if r + 1 < ch: yield (r + 1, c)
    if c > 0: yield (r, c - 1)
    if c + 1 < cw: yield (r, c + 1)

def carve_simple_guaranteed_path(g, seed=None):
    if seed is not None:
        random.seed(seed)

    h = len(g)
    w = len(g[0])

    s1 = random.randrange(4)
    s2 = random.randrange(4)
    while s2 == s1:
        s2 = random.randrange(4)

    def pick_border_point(side):
        if side == 0:
            return (0, random.randrange(w))
        if side == 1:
            return (h - 1, random.randrange(w))
        if side == 2:
            return (random.randrange(h), 0)
        return (random.randrange(h), w - 1)

    ent = pick_border_point(s1)
    ex = pick_border_point(s2)
    while ex == ent:
        ex = pick_border_point(s2)

    def step_inside(p):
        r, c = p
        if r == 0: return (1, c)
        if r == h - 1: return (h - 2, c)
        if c == 0: return (r, 1)
        return (r, w - 2)

    a = step_inside(ent)
    b = step_inside(ex)

    r1, c1 = a
    r2, c2 = b

    def carve_point(r, c):
        g[r][c] = ROAD

    carve_point(r1, c1)

    if random.choice([True, False]):
        step = 1 if r2 >= r1 else -1
        for r in range(r1, r2 + step, step):
            carve_point(r, c1)
        step = 1 if c2 >= c1 else -1
        for c in range(c1, c2 + step, step):
            carve_point(r2, c)
    else:
        step = 1 if c2 >= c1 else -1
        for c in range(c1, c2 + step, step):
            carve_point(r1, c)
        step = 1 if r2 >= r1 else -1
        for r in range(r1, r2 + step, step):
            carve_point(r, c2)

    er, ec = ent
    xr, xc = ex
    g[er][ec] = ENTRANCE
    g[xr][xc] = EXIT

    ar, ac = a
    br, bc = b
    g[ar][ac] = ROAD
    g[br][bc] = ROAD

    return g

def find_points(g):
    sr = sc = er = ec = None
    h = len(g)
    w = len(g[0])
    for r in range(h):
        for c in range(w):
            if g[r][c] == ENTRANCE:
                sr, sc = r, c
            elif g[r][c] == EXIT:
                er, ec = r, c
    return (sr, sc), (er, ec)

def alive_path_exists(g):
    (sr, sc), (er, ec) = find_points(g)
    if sr is None or er is None:
        return False

    h = len(g)
    w = len(g[0])

    dist = [[[-1] * 3 for _ in range(w)] for _ in range(h)]
    q = deque()

    dist[sr][sc][0] = 0
    q.append((sr, sc, 0))

    while q:
        r, c, t = q.popleft()
        if (r, c) == (er, ec):
            return True

        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nr, nc = r + dr, c + dc
            if not (0 <= nr < h and 0 <= nc < w):
                continue

            v = g[nr][nc]
            if v == WALL:
                continue

            nt = t + (1 if v == TRAP else 0)
            if nt > 2:
                continue

            if dist[nr][nc][nt] == -1:
                dist[nr][nc][nt] = dist[r][c][t] + 1
                q.append((nr, nc, nt))

    return False

def add_traps(g, seed=None, max_traps=5):
    if seed is not None:
        random.seed(seed + 1000003)

    h = len(g)
    w = len(g[0])

    k = random.randint(0, max_traps)

    candidates = []
    for r in range(h):
        for c in range(w):
            if g[r][c] == ROAD:
                candidates.append((r, c))

    random.shuffle(candidates)

    placed = 0
    attempts = 0
    limit = max(200, len(candidates) * 2)

    while placed < k and attempts < limit and candidates:
        attempts += 1
        r, c = candidates.pop()

        g[r][c] = TRAP
        if alive_path_exists(g):
            placed += 1
        else:
            g[r][c] = ROAD

    return g

def generate_maze(height, width, seed=None, traps=True):
    if seed is not None:
        random.seed(seed)

    height = int(height)
    width = int(width)

    if height < 5 or width < 5:
        raise ValueError("Maze size must be at least 5x5. Example: python maze.py 5 5")

    g = make_grid(height, width, WALL)

    ch = (height - 1) // 2
    cw = (width - 1) // 2

    if ch <= 1 or cw <= 1:
        g = carve_simple_guaranteed_path(g, seed=seed)
        if traps:
            g = add_traps(g, seed=seed, max_traps=5)
        return g

    for cr in range(ch):
        for cc in range(cw):
            r = 2 * cr + 1
            c = 2 * cc + 1
            if 0 <= r < height and 0 <= c < width:
                g[r][c] = ROAD

    visited = [[False] * cw for _ in range(ch)]
    start_cr = random.randrange(ch)
    start_cc = random.randrange(cw)

    stack = [(start_cr, start_cc)]
    visited[start_cr][start_cc] = True

    while stack:
        cr, cc = stack[-1]
        unvis = []
        for nr, nc in neighbors_cell(cr, cc, ch, cw):
            if not visited[nr][nc]:
                unvis.append((nr, nc))

        if not unvis:
            stack.pop()
            continue

        nr, nc = random.choice(unvis)

        r1, c1 = 2 * cr + 1, 2 * cc + 1
        r2, c2 = 2 * nr + 1, 2 * nc + 1
        wr, wc = (r1 + r2) // 2, (c1 + c2) // 2
        g[wr][wc] = ROAD

        visited[nr][nc] = True
        stack.append((nr, nc))

    border_candidates = []

    def add_candidate(br, bc, ar, ac):
        if 0 <= br < height and 0 <= bc < width and 0 <= ar < height and 0 <= ac < width:
            if g[ar][ac] == ROAD:
                border_candidates.append(((br, bc), (ar, ac)))

    for c in range(width):
        add_candidate(0, c, 1, c)
        add_candidate(height - 1, c, height - 2, c)
    for r in range(height):
        add_candidate(r, 0, r, 1)
        add_candidate(r, width - 1, r, width - 2)

    if not border_candidates:
        g = carve_simple_guaranteed_path(g, seed=seed)
        if traps:
            g = add_traps(g, seed=seed, max_traps=5)
        return g

    adj_points = [a for (_, a) in border_candidates]

    def bfs_from(src):
        dist = [[-1] * width for _ in range(height)]
        q = deque([src])
        dist[src[0]][src[1]] = 0
        while q:
            r, c = q.popleft()
            d = dist[r][c]
            for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < height and 0 <= nc < width:
                    if dist[nr][nc] == -1 and g[nr][nc] == ROAD:
                        dist[nr][nc] = d + 1
                        q.append((nr, nc))
        return dist

    a0 = random.choice(adj_points)
    d0 = bfs_from(a0)
    a1 = max(adj_points, key=lambda p: d0[p[0]][p[1]])
    d1 = bfs_from(a1)
    a2 = max(adj_points, key=lambda p: d1[p[0]][p[1]])

    def border_for_adj(adj):
        for (b, a) in border_candidates:
            if a == adj:
                return b
        return None

    ent_border = border_for_adj(a1)
    exit_border = border_for_adj(a2)

    if ent_border is None or exit_border is None or ent_border == exit_border:
        ent_border, _ = random.choice(border_candidates)
        exit_border, _ = random.choice(border_candidates)
        while exit_border == ent_border:
            exit_border, _ = random.choice(border_candidates)

    er, ec = ent_border
    xr, xc = exit_border
    g[er][ec] = ENTRANCE
    g[xr][xc] = EXIT

    if traps:
        g = add_traps(g, seed=seed, max_traps=5)
        if not alive_path_exists(g):
            for r in range(height):
                for c in range(width):
                    if g[r][c] == TRAP:
                        g[r][c] = ROAD

    return g

def print_maze(g, use_numbers=False, with_color=True):
    h = len(g)
    w = len(g[0]) if h else 0

    if use_numbers:
        for r in range(h):
            print(" ".join(str(g[r][c]) for c in range(w)))
        return

    for r in range(h):
        line = []
        for c in range(w):
            v = g[r][c]
            if v == WALL:
                ch = "█"
                line.append((C_DIM + C_WALL + ch + C_RESET) if with_color else ch)
            elif v == ROAD:
                ch = " "
                line.append((C_ROAD + ch + C_RESET) if with_color else ch)
            elif v == ENTRANCE:
                ch = "S"
                line.append((C_ENT + ch + C_RESET) if with_color else ch)
            elif v == EXIT:
                ch = "E"
                line.append((C_EXIT + ch + C_RESET) if with_color else ch)
            elif v == TRAP:
                ch = "T"
                line.append((C_TRAP + ch + C_RESET) if with_color else ch)
            else:
                line.append("?")
        print("".join(line))

def main(argv):
    if len(argv) < 3:
        print("Usage: python maze.py H W [--seed N] [--numbers] [--no-color] [--no-traps]")
        return 1

    try:
        H = int(argv[1])
        W = int(argv[2])
    except ValueError:
        print("Error: H and W must be integers. Example: python maze.py 21 41")
        return 2

    seed = None
    use_numbers = False
    with_color = True
    traps = True

    i = 3
    while i < len(argv):
        if argv[i] == "--seed" and i + 1 < len(argv):
            try:
                seed = int(argv[i + 1])
            except ValueError:
                print("Error: --seed must be an integer. Example: --seed 123")
                return 2
            i += 2
        elif argv[i] == "--numbers":
            use_numbers = True
            i += 1
        elif argv[i] == "--no-color":
            with_color = False
            i += 1
        elif argv[i] == "--no-traps":
            traps = False
            i += 1
        else:
            i += 1

    try:
        g = generate_maze(H, W, seed=seed, traps=traps)
    except ValueError as e:
        print(f"Error: {e}")
        return 2

    print_maze(g, use_numbers=use_numbers, with_color=with_color)
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))