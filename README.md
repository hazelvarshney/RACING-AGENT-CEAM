# RACING AGENT - CEAM

# Overview

For this project, I created a 2D machine learning environment where our
model learns how to navigate through a race track.

# Sensors 

Our agent has 5 different sensors attached to it, each for a different
direction: front, front left, front right, left, and right. Each sensor
casts an outward ray from the car in the direction it is currently facing
and checks each cell one by one until it finds a wall.

# Actions

Our agent can perform 3 actions in total:


0 => Turn left
1 => Go straight
2 => Turn right


# Rewards

Our agent gets rewarded with a +1 for every waypoint it reaches, a +50 for
every lap it completes, and a -5 for crashing. It gets a -0.1 every step in
case it makes no progress, which forces our agent to keep moving.

# Exploration 

I set the epsilon to 0.9, meaning initially the agent focused more on
exploring rather than sensor readings. It started crashing less frequently
as it went through more and more episodes, because of epsilon decay.


# Why not other approaches?

I initially decided to use the gym package for creating the environment,
but later decided to switch to pygame because gym required DQN, which was
much more complex, and using pygame helped me understand the Reinforcement
Learning fundamentals better.

Keeping the number of actions less kept the Q-table small and easy to reason
about.

# Failures encountered

Initially, I did not assign a penalty for staying idle, which lead to the car
avoiding the -0.5 crashing penalty by just not moving at all. I later added a 
-0.1 penalty whenever the car stays idle so that it keeps moving.

