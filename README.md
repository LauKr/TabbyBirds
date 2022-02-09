A small flappy bird game written in python.


We use a neural network utilizing the NEAT (NeuroEvolution of Augmenting Topologies) module. Resources: [GitHub](https://github.com/CodeReclaimers/neat-python), [initial paper](http://nn.cs.utexas.edu/downloads/papers/stanley.ec02.pdf), [other paper](http://nn.cs.utexas.edu/downloads/papers/stanley.cec02.pdf)

As inputs we basically only need the bird y-position and the position of one pipe, e.g. the top pipe. To simplify the evolution process for the AI we also pass the bottom pipe, so that the algorithm doesn't has to figure out the pipe gap -> 3 neurons. 

The output is very simple, it's only a "jump" or "don't jump", so only one neuron.
