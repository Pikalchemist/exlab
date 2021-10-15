# ExLab
**EXperimental LABoratory** is a research oriented framework helping to setup experiments, store results, log serizalize and unserialize data, and plot graphs.

# Getting started

First of all, install the package either using pip:

    pip install exlab

Or from the git repository:

    pip install -r ./requirements.txt
    pip install -e .

A base example of how to use ExLab is provided in `examples/first/first.py` in the git repository.

# Components

## Laboratory

You can create Lab and Experiment to manage your experimental settings, load and instantiate objects and save your results.

## Serialization

To serialize an object, it has to be subclass of  `Serializable` and overrides the `_serialize(self, serializer)` and `_deserialize(cls, dict_, serializer, obj=None)` methods to inplement the intended behaviour.