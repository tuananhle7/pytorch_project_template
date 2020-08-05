# My PyTorch project setup for running experiments on Openmind

Make sure you have `python` installed on Openmind.
Conda works fine for me (didn't need Singularity so far), but that's maybe because I just use standard Python packages without complex dependencies.
I usually have a `tmux` session on Openmind that is always running, and with 1 or 2 live interactive sessions.

## Single run

Running
```
python run.py
```
saves checkpoints to `save/<path_base>/checkpoints/` where `<path_base>` is specified by `util.get_path_base_from_args` given `run.py`'s args.
It always picks up from the latest checkpoint `save/<path_base>/checkpoints/latest.pt`.
You can run this on an Openmind interactive session or locally.

## Running a hyperparameter sweep

### Luke's om-repeat script
On openmind, run the following commands to install Luke's [om-repeat](https://github.com/insperatum/openmind-tools) script:

```
cd ~
git clone git@github.com:insperatum/openmind-tools.git
echo 'export PATH="$HOME/openmind-tools/bin:$PATH"' >> ~/.bashrc
```

This allows you to queue jobs using standard `sbatch` by queueing 2h jobs with dependencies until the script finishes.
Since the run script always picks up from the latest checkpoint, it should be fine as long as the `--save-interval` value is small enough.
There is a way to catch the termination signal and save checkpoints based on that but it's not really necessary.

### The actual sweep
Running
```
python sweep.py --cluster
```
on Openmind queues the jobs as defined by the `sweep.get_sweep_argss`.
In this example, I'm looping over 3 random seeds x 2 number of hidden units in the first layer x 2 number of hidden units in the second layer of a multilayer perceptron.

Change `util.get_path_base_from_args` accordingly so that the folder names of your models are sensible.
For instance, if you're sweeping only over the seed, while other hyperparameters are fixed, you can just set `path_base` to be the `seed` and not include the other hyperparameters.

If you don't provide `--cluster`, the jobs are just run sequentially on the current machine (interactive session on Openmind or local machine).

Provide `--rm` option to remove the `save/` folder before running the sweep.

Standard out and standard error logs are saved in `save/<path_base>/logs`.


## Plotting

Running
```
python plot.py
```
iterates over folders in `save/` plots losses (and potentially other stuff) to `save/<path_base>/...`.

If you provide the `--repeat` flag, it does this in an infinite loop.
I usually just start another interactive session and run an infinite plotting script there to track training progress.