This repository provides an implementation of four decentralized group formation algorithms: Closest Available Neighbor First (CANF), Simple Random, Random Subset (RS), and Variable Neighborhood Search (VNS).

Authors:  Hamed Alimohammadzadeh(halimoha@usc.edu) and Shahram Ghandeharizadeh (shahram@usc.edu)

# Features

  * Four decentralized algorithms that construct fix-sized groups given either a synthetic or a real point cloud.  The size of a group is denoted as G.
  * Constructs symmetric groups.  This means the participation of a member (an FLS) in a group is reciprocated by all the members in that group.
  * An implementation of a synthetically generated point cloud (named OutRing) with known optimal solutions.
  * This implementation launches multiple processes.  Each process emulates a Flying Light Speck, FLS.  One may execute on a single server or execute it on multiple servers.  Both CloudLab and Amazon AWS are supported.


# Limitations
  * With large point clouds and the Linux operating system, the execution of the software may exhaust the max open files supported by the operating system.  See below, Error with Large Point Clouds, for how to resolve. 
  * No support for asymmetric groups.  In other words, each algorithm strives to ensure the participation of a member in a group is reciprocated by all the members in that group. 


# Clone
```
git clone https://github.com/flyinglightspeck/Group-Formation.git
```


# Running on a Laptop or a Server

This software was implemented and tested using Python 3.9.0.

We recommend using PyCharm, enabling the software to run across mutliple operating systems, e.g., Windows, MacOS, etc.

## Running using a (PyCharm) Terminal

Run ``bash setup.sh`` to install the requirements.

The variables specified in `config.py` control settings.  

If running on a laptop/server with a limited number of cores, set the 'NUMBER_OF_FLSS' and 'SAMPLE_SIZE' to a small value.  As a general guideline, their values should not exceed four times the number of physical cores.

This program is designed to scale horizontally across multiple servers and run with large point clouds. Each point is assigned to a Flying Light Speck, a process launched by this program.  

Run `server.py` after adjusting the settings of `config.py` (see below).  The decentralized algorithms may be invoked using synthetic point clouds generated by the Outring or with a real point cloud.  Consider each in turn.


## Running using virtual environment, Venv

You can use the `bash setup_venv.sh` script to create and activate a virtual environment or alternatively follow these steps to set it up manually.
First create a virtual environment using venv. You can use any name instead of env.

```
cd Group-Formation
python3.9 -m venv env
```

Then, activate the virtual environment.

```
source env/bin/activate
```

On windows use the following instead:

```
env/Scripts/activate.bat //In CMD
env/Scripts/Activate.ps1 //In Powershel
```

Install the requirements:

```
pip3 install -r requirements.txt
```

You can now run `server.py`. Finally, deactivate the virtual environment by running `deactivate` in the terminal.


## Outring
The Outring is a synthetically generated point cloud.  Set the value of `R` in `config.py` to a large value, say 1000, to generate sparse point clouds.  Such point clouds have known optimal solutions.  One may evaluate the implementation of the alternative algorithms to show they compute the optimal solution with an arbitrary number of FLSs and group sizes.

To run the Outring, set `TEST_ENABLED` to True and `SHAPE` to `outring`.  It will generate the synthetic point cloud in memory and invoke the algorithm specified by the parameter `H` in `config.py`.  The possible values of `H` are:  `canf`, `simpler`, `rs`, `vns`.

With the Outring, the number of points in a point cloud is specified by the value of `NUMBER_OF_FLSS` in `config.py`.  It should be a multiple of the group size `G`.  Otherwise, the program adjusts the value of `NUMBER_OF_FLSS` to be an even multiple of `G` and continues execution.

## A Point Cloud
We provide several point clouds, e.g., a Chess piece.  The value of variables SHAPE and TEST_ENABLED in config.py control the used point cloud used.  Set the `SHAPE` value to the shape name and set the `TEST_ENABLED` to `False`.  The repository comes with the following shapes (possible values of `SHAPE`): `bigbutterfly`, `butterfly`, `cat`, `chess`, `dragon`, `hat`, `racecar`, `skateboard`, `teapot`.

With a large point cloud, one may want to use a small number of its points as a starting point. Set `SAMPLE_SIZE` to a smaller number of points and the system will sample a specified number of points from the point cloud to run an algorithm.  If the value of `SAMPLE_SIZE` is set to zero, all points of the specified point cloud will be used.


# Running on Multiple Servers: Amazon AWS
First, set up a cluster of servers. Ideally, the total number of cores of the servers should equal or be greater than the number of points in the point cloud (number of FLSs).

Set up a multicast domain (For more information on how to create a multicast domain see aws docs: https://docs.aws.amazon.com/vpc/latest/tgw/manage-domain.html)

Add your instances to the multicast domain. Use the value of MULTICAST_GROUP_ADDRESS in the constants.py for the group address.

Ensure you allow all UDP, TCP, and IGMP(2) traffic in your security group.

After setting up AWS, modify the following files based on the comments:

`constants.py`

`aws_vars.sh`

`scripts/var.sh`

Configure the experiment(s) you want to run by modifying `gen_conf.py`.

Use the `scripts/init` to clone the repository and set up the project by running `setup.sh` on each server.

Upload your AWS key pair to the primary instance.

Finally, run the `nohup_run.sh` script on the primary instance to run the experiment(s).

After the experiments are finished, you can download the results using `scripts/download.sh`

Use `file.py` to post-process the results and generate the metrics


# Running on Multiple Servers: CloudLab


# Error with Large Point Clouds
If you encountered an error regarding not enough fds, increase max open files system-wide to be able to run a large point cloud:

``sudo vim /etc/sysctl.conf``

Add the following line:

``fs.file-max = 9999``

``sudo sysctl -p``

Reload terminal and then run this command:

``ulimit -n 9999``

# Citations

Hamed Alimohammadzadeh, Heather Culbertson, and Shahram Ghandeharizadeh. 2024. An Evaluation of Decentralized Group Formation Techniques for Flying Light Specks. In Proceedings of the 5th ACM International Conference on Multimedia in Asia (MMAsia '23). Association for Computing Machinery, New York, NY, USA, Article 84, 1–7. https://doi.org/10.1145/3595916.3626460

BibTex:
```
@inproceedings{10.1145/3595916.3626460, 
author = {Alimohammadzadeh, Hamed and Culbertson, Heather and Ghandeharizadeh, Shahram}, 
title = {An Evaluation of Decentralized Group Formation Techniques for Flying Light Specks}, 
year = {2024}, 
isbn = {9798400702051}, 
publisher = {Association for Computing Machinery}, 
address = {New York, NY, USA}, 
url = {https://doi.org/10.1145/3595916.3626460}, 
doi = {10.1145/3595916.3626460}, 
abstract = {Group formation is fundamental for 3D displays that use Flying Light Specks, FLSs, to illuminate shapes and provide haptic interactions. An FLS is a drone with light sources that illuminates a shape. Groups of G FLSs may implement reliability techniques to tolerate FLS failures, provide kinesthetic haptic feedback in response to a user’s touch, and facilitate a divide and conquer approach to challenges such as localizing FLSs to render a shape. This paper evaluates four decentralized techniques to form groups. An FLS implements a technique autonomously using asynchronous communication and without a global clock. We evaluate these techniques using synthetic point clouds with known optimal solutions and real point clouds. Obtained results show a technique named Random Subset (RS) is superior when constructing small groups (G ≤ 5) while a different technique named Closest Available Neighbor First (CANF) is superior when constructing large groups (G ≥ 10).}, 
booktitle = {Proceedings of the 5th ACM International Conference on Multimedia in Asia}, 
articleno = {84}, 
numpages = {7}, 
location = {Tainan, Taiwan}, 
series = {MMAsia '23} 
}
```
