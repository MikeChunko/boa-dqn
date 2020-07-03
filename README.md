# boa-dqn

Applies a Deep Q Network to solve a game of Snake. Currently the DQN is able to eat the food an average of three times by the end of a 200 game training batch, with a high score of eleven. The DQN can clearly avoid walls and get food but has a difficult time avoiding the snake's tail.

The weights determined from training are stored in `weights.hdf5`, though there is currently no way to make the DQN use saved weights.

The implementation of Snake is a modified version of https://github.com/MikeChunko/boa.

To run and train, make sure you have the keras, numpy, and pygame libraries installed, clone the repo, and run `python boa.py`.

Run `python boa.py --help` for a complete list of options.
