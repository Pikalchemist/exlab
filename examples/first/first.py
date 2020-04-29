from exlab.lab import Lab
from exlab.utils.path import basepath


basedir = basepath(__file__)

lab = Lab(basedir, defaults='config.yml', help='Simple example')

lab.parameter('dataset').key('datasets', 'data.yml')
lab.parameter('learner').config('learners')

lab.filter('learners/*').parameter('dataset').key('datasets', 'data.yml')

lab.load()
