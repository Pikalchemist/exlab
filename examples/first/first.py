from exlab.lab import Lab
from exlab.utils.path import basepath


basedir = basepath(__file__)

lab = Lab(basedir, defaults='config.yml', help='Simple example')

lab.parameter('dataset').import_key('datasets', 'data.yml')
lab.parameter('learner').import_file(['learners', 'learners2'])

lab.filter('learners/*').parameter('dataset').import_key('datasets', 'data.yml')

lab.load()
