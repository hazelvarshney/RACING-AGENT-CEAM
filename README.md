# RACING AGENT - CEAM

For the following project, I created a 2D machine learning environment where our model learns how to navigate through a race track. 
Our agent has 5 different sensors attached to it, each for different directions such as front, front left, front right, left, and right.
Each sensor casts an outward ray from the car in the direction it is currently facing and checks each cell one by one until it finds a wall.

Our agent can perform 3 actions in total, which is:
0 => Turn left
1 => Go straight
2 => Turn right

Our agent gets rewarded with a +1 for every waypoint it reaches, a +50 for every lap it completes, and a -5 for crashing.
It gets a -0.1 every step in case it makes no progress, which forces our agent to keep moving.

I set the epsilon to 0.9, meaning initially the agent focused more on exploring rather than sensor readings.
It started crashing less frequently as it went through more and more episodes, because of epsilon decay.

I initially decided to use the gym package for creating the environment, but later decided to switch to pygame because gym required DQN, which 
was much more complex and using pygame helped me understand the Reinforcement Learning fundamentals better. 
