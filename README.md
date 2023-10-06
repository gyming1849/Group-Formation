# Group-Formation

## Clone
``git clone https://github.com/flyinglightspeck/Group-Formation.git``


## Running locally

Run ``bash setup.sh`` to set up the project.

Modify the `cong.py` to your desired configuration, then run `server.py`.

For using the shape point clouds, set the `SHAPE` value to the shape name and set the `TEST_ENABLED` to `False`. Otherwise, set the `TEST_ENABLED` to True and `SHAPE` to `test` for running the algorithm on the outring point cloud.

For shapes, use `SAMPLE_SIZE` to sample a smaller number of points from the point cloud. If set to zero, all points will be used.

For the outring point cloud, modify `NUMBER_OF_FLSS`, and 'R'.

If running on limited resources, set the 'NUMBER_OF_FLSS' and 'SAMPLE_SIZE' to a small value, not more than four times the number of physical cores.


## Running on AWS
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


## Large Point Clouds
If you encountered an error regarding not enough fds, increase max open files system-wide to be able to run a large point cloud:

``sudo vim /etc/sysctl.conf``

Add the following line:

``fs.file-max = 9999``

``sudo sysctl -p``

Reload terminal and then run this command:

``ulimit -n 9999``
