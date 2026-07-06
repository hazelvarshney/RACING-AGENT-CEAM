import numpy as np
import matplotlib.pyplot as plt
from racing_ml import RacingEnv, WIDTH, HEIGHT

LEARNING_RATE = 0.1
DISCOUNT      = 0.95
EPSILON       = 0.9
EPS_DECAY     = 0.9995
EPSILON_MIN   = 0.01
HM_EPISODES   = 5000


env       = RacingEnv()
q_table   = {}
episode_rewards = []
epsilon   = EPSILON

for episode in range(HM_EPISODES):
    obs            = env.reset()
    episode_reward = 0

    if obs not in q_table:
        q_table[obs] = [np.random.uniform(-5, 0) for i in range(3)]

    for step in range(300):
        if np.random.random() > epsilon:
            action = np.argmax(q_table[obs])
        else:
            action = np.random.randint(0, 3)

        new_obs, reward, done, info = env.step(action)

        if new_obs not in q_table:
            q_table[new_obs] = [np.random.uniform(-5, 0) for i in range(3)]

        current_q    = q_table[obs][action]
        max_future_q = np.max(q_table[new_obs])
        new_q        = (1 - LEARNING_RATE) * current_q + LEARNING_RATE * (reward + DISCOUNT * max_future_q)
        q_table[obs][action] = new_q

        obs             = new_obs
        episode_reward += reward

        if done:
            break

    episode_rewards.append(episode_reward)
    epsilon = max(epsilon * EPS_DECAY, EPSILON_MIN)

    if episode % 500 == 0:
        print(f"episode {episode}, epsilon {epsilon:.3f}, reward {episode_reward:.1f}")

import pygame
import sys
import math

CELL = 30

def run_trained_agent(q_table, env):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH * CELL, HEIGHT * CELL))
    pygame.display.set_caption("Trained Q-Learning Agent")
    clock  = pygame.time.Clock()

    from f1_game import draw_track, draw_f1_car


    track_surf = pygame.Surface((WIDTH * CELL, HEIGHT * CELL))
    draw_track(track_surf, env.grid)

    obs  = env.reset()
    done = False

    while True:
        clock.tick(10)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    obs  = env.reset()
                    done = False

        if not done:
            if obs in q_table:
                action = np.argmax(q_table[obs])
            else:
                action = np.random.randint(0, 3)

            obs, reward, done, info = env.step(action)


        heading_to_angle = {0: 270, 1: 315, 2: 0, 3: 45,
                            4: 90,  5: 135, 6: 180, 7: 225}
        angle = heading_to_angle[env.heading]


        px = env.c * CELL + CELL // 2
        py = env.r * CELL + CELL // 2

        screen.blit(track_surf, (0, 0))
        draw_f1_car(screen, px, py, angle)
        pygame.display.flip()

        if done:
            pygame.time.wait(1000)
            obs  = env.reset()
            done = False
moving_avg = np.convolve(episode_rewards, np.ones(50)/50, mode='valid')
plt.plot(moving_avg)
plt.title("Q-Learning Racing Agent — Reward per Episode")
plt.xlabel("Episode")
plt.ylabel("Reward")
plt.show()
run_trained_agent(q_table, env)

