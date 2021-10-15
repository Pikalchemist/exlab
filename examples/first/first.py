from exlab.lab.lab import Lab
from exlab.lab.counter import EpisodeAbsoluteIterationCounter
from exlab.utils.path import basepath


basedir = basepath(__file__)

# First we init the laboratory
lab = Lab(basedir, defaults='defaults.yml', help='Simple example')

# Each Lab possesses a set of parameters
# We define here if our lab needs foreign imports

# The field infos.dataset will be used to import a dataset from the file data.yml
lab.parameter('infos.dataset').import_key('datasets', 'data.yml')
# The field learner will be used to import a file for folders learners or learners2 (first matching)
lab.parameter('learner').import_file(['learners', 'learners2'])

# The field dataset from any config file in the learners folder will be used to import a dataset
# from the file data.yml
lab.filter('learners/*').parameter('dataset').import_key('datasets', 'data.yml')

# We load here our config and apply our foreign key imports
# A Lab provides a way to count your iterations with a counter
# Here we use an EpisodeAbsoluteIterationCounter, we count both episodes (a set of iterations) and iterations
# Absolute means the iteration number does not revert to 0 when the episode changes
lab.load(counter=EpisodeAbsoluteIterationCounter)


# We need to define a callback function to be executed by our lab
# We can also only use the loading mechanism from exlab and use custom code here
def run(exp):
    # An Experiment instance will be provided to this function
    # We will just print the learner used for this experiment
    print(exp.config['learner'])

# At last we execute the Lab
# Depending on configuration, it will run one or multiple experiments with different parameters
# They can be executed sequencially or in multiple threads
lab.run(run)
