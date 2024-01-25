This repository provides an implementation of four decentralized group formation algorithms: Closest Available Neighbor First (CANF), Simple Random, Random Subset (RS), and Variable Neighborhood Search (VNS).

Authors:  Hamed Alimohammadzadeh(halimoha@usc.edu) and Shahram Ghandeharizadeh (shahram@usc.edu)

# Features

  * Four decentralized algorithms that construct arbitrary sized groups given either a synthetic or a real point cloud.  The size of a group is denoted as G.
  * Constructs symmetric groups.  This means the participation of a member (an FLS) in a group is reciprocated by all the members in that group.
  * An implementation of OutRing with known optimal solutions for its sparse settings.


# Limitations
  * With large point clouds, the execution of the software may exhaust the max open files supported by the operating system.  See below for how to resolve. 
  * No support for asymmetric groups.  In other words, each algorithm strives to ensure the participation of a member in a group is reciprocated by all the members in that group. 



# Clone
``git clone https://github.com/flyinglightspeck/Group-Formation.git``


# Running locally

Run ``bash setup.sh`` to set up the project.

The variables specified in `config.py` control settings.  Once these are adjusted (see below), run `server.py`.

Group-Formation may be used with either a synthetic point cloud (Outring) or an actual point cloud.  We provide several point clouds, e.g., a Chess piece.  The value of variables SHAPE and TEST_ENABLED in config.py control the setting.  For using the shape point clouds, set the `SHAPE` value to the shape name and set the `TEST_ENABLED` to `False`. Otherwise, set the `TEST_ENABLED` to True and `SHAPE` to `test` for running the algorithm on the synthetically generated Outring point cloud.

For shapes, use `SAMPLE_SIZE` to sample a smaller number of points from the point cloud. If set to zero, all points will be used.

For the outring point cloud, modify `NUMBER_OF_FLSS`, and 'R'.

If running on limited resources, set the 'NUMBER_OF_FLSS' and 'SAMPLE_SIZE' to a small value, not more than four times the number of physical cores.


# Running on Amazon AWS
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
