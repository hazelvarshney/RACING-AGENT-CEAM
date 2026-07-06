import numpy as np

HEIGHT = 20
WIDTH = 30
OUTER = 2
INNER = 6
CELL = 30

HEADINGS = [(-1,0), (-1,1), (0,1), (1,1), (1,0), (1,-1), (0,-1), (-1,-1)]

def make_track():
    grid = np.zeros((HEIGHT, WIDTH), dtype=int)
    grid[OUTER:HEIGHT - OUTER, OUTER:WIDTH - OUTER] = 1
    grid[INNER:HEIGHT - INNER, INNER:WIDTH - INNER] = 0
    start_row = HEIGHT - OUTER - 1
    mid_col   = WIDTH // 2
    grid[start_row, mid_col - 1:mid_col + 2] = 2
    return grid

def ontrack(grid, r, c):
    if r<0 or r>= HEIGHT or c<0 or c >= WIDTH:
        return False
    return grid[r, c] >= 1
def car(grid, r, c, heading, action):
    if action == 0:
        heading = (heading -1)%8
    elif action == 2:
        heading = (heading +1)%8

    dr,dc = HEADINGS[heading]
    new_r = r + dr
    new_c = c + dc

    if not ontrack(grid, new_r, new_c):
        return r,c, heading, True

    return new_r, new_c, heading, False
if __name__ == "__main__":
    track = make_track()
    print("value at (17,10):", track[17, 10])
    print("value at (17,11):", track[17, 11])
    print("GRID_H:", track.shape[0], "GRID_W:", track.shape[1])
if __name__ == "__main__":
    track = make_track()

    r, c, heading = 17, 10, 2
    new_r, new_c, new_heading, crashed = car(track, r, c, heading, 1)
    print(f"straight: ({r},{c}) -> ({new_r},{new_c}), crashed={crashed}")

    r, c, heading = 2, 10, 0
    new_r, new_c, new_heading, crashed = car(track, r, c, heading, 1)
    print(f"into wall: ({r},{c}) -> ({new_r},{new_c}), crashed={crashed}")

MAX_SENSOR = 6
N_BINS     = 4

def cast_ray(grid, r, c, direction_idx):
    dr, dc = HEADINGS[direction_idx]
    for dist in range(1, MAX_SENSOR + 1):
        rr = r + dr * dist
        cc = c + dc * dist
        if not ontrack(grid, rr, cc):
            return dist - 1
    return MAX_SENSOR

def get_observation(grid, r, c, heading):
    dirs = [
        heading,              # front
        (heading - 1) % 8,   # front left
        (heading + 1) % 8,   # front right
        (heading - 2) % 8,   # left
        (heading + 2) % 8,   # right
    ]
    obs = []
    for d in dirs:
        raw    = cast_ray(grid, r, c, d)
        binned = min(int(raw / (MAX_SENSOR / N_BINS)), N_BINS - 1)
        obs.append(binned)
    return tuple(obs)
def build_waypoints():
    cl     = OUTER + (INNER - OUTER) // 2
    top    = cl
    bottom = HEIGHT - 1 - cl
    left   = cl
    right  = WIDTH - 1 - cl
    mid    = WIDTH // 2

    wp = []
    for c in range(left, mid + 2):          wp.append((bottom, c))
    for r in range(bottom, top - 1, -1):    wp.append((r, right))
    for c in range(right, left - 1, -1):    wp.append((top, c))
    for r in range(top, bottom + 1):        wp.append((r, left))
    for c in range(left, mid - 1):          wp.append((bottom, c))
    return wp

def build_wp_lookup(grid, waypoints):
    lookup   = {}
    wp_array = np.array(waypoints)
    for r in range(HEIGHT):
        for c in range(WIDTH):
            if grid[r, c] >= 1:
                dists          = np.sum((wp_array - np.array([r, c])) ** 2, axis=1)
                lookup[(r, c)] = int(np.argmin(dists))
    return lookup

REWARD_PROGRESS = 1.0
REWARD_LAP      = 50.0
REWARD_CRASH    = -5.0
REWARD_TIME     = -0.1
MAX_STEPS       = 300

class RacingEnv:
    def __init__(self):
        self.grid      = make_track()
        self.waypoints = build_waypoints()
        self.n_wp      = len(self.waypoints)
        self.lut       = build_wp_lookup(self.grid, self.waypoints)

    def reset(self):
        self.r        = self.waypoints[0][0]
        self.c        = self.waypoints[0][1]
        self.heading  = 2        # facing East
        self.steps    = 0
        self.last_wp  = 0
        self.progress = 0
        return get_observation(self.grid, self.r, self.c, self.heading)

    def step(self, action):
        self.steps += 1
        self.r, self.c, self.heading, crashed = car(
            self.grid, self.r, self.c, self.heading, action
        )

        if crashed:
            obs = get_observation(self.grid, self.r, self.c, self.heading)
            return obs, REWARD_CRASH, True, "crash"

        curr_wp = self.lut.get((self.r, self.c), self.last_wp)
        diff    = (curr_wp - self.last_wp) % self.n_wp

        if 0 < diff <= 5:
            reward        = REWARD_PROGRESS
            self.progress += 1
            self.last_wp  = curr_wp
            if self.progress >= self.n_wp:
                obs = get_observation(self.grid, self.r, self.c, self.heading)
                return obs, REWARD_LAP, True, "lap_complete"
        else:
            reward       = REWARD_TIME
            self.last_wp = curr_wp

        done = self.steps >= MAX_STEPS
        obs  = get_observation(self.grid, self.r, self.c, self.heading)
        return obs, reward, done, "timeout" if done else ""



if __name__ == "__main__":
    env = RacingEnv()
    obs = env.reset()
    print("start obs:", obs)
    print("start pos:", env.r, env.c, "heading:", env.heading)

    for i in range(5):
        obs, reward, done, info = env.step(1)
        print(f"step {i}: pos=({env.r},{env.c}) reward={reward} done={done} info={info}")
