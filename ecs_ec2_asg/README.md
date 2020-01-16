
# ECS with EC2 autoscaling example

## Build
```
python3.7 -m venv .env
source .env/bin/activate
pip install -r requirements.txt
```

Synthesize the CloudFormation template by
```
cdk synth
```

## Deploy
(Optional) Set the account and region which you use to deploy the service:

```
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=ABCDEFGHIJK
export AWS_DEFAULT_REGION=us-east-1
```

To deploy the app, run

```
cdk deploy
```

Finally, you must update the ECS configuration. Basically, this script updates "Instance Protection" property of the ASG, and add capacity provider to the cluster. This operation currently cannot be done through CDK. Thus, here I use a simple Python script to do this.

```
export ASG_NAME=<your asg name>
export CLUSTER_NAME=<your cluster name>
python script.py $ASG_NAME $CLUSTER_NAME
```

## Clean up
When you are done with the app, do not forget to destroy it:

```
cdk destroy
```

## Test
- Open AWS console using your web browser.
- Go to "ECS" -> "Task Definitions".
- Choose the task that was created by this project. It should have a name starting with "CdkTutorialStack".
- From "Actions" choose Run Task
- Set parameters (see image below)
  * Choose appropriate entry in  "Cluster"
  * Type `6` in "Number of taksks"
  * Leave "Task Group" empty
  * For "Placement Templates", choose "AZ Balanced Spread"
- Click "Run Task"
- Let's check that the tasks are actually running in the cluster
  * Go to "ECS" -> "Clusters" and open your cluster
  * In the "ECS Instances" tab, verify that EC2 instances are created to run the tasks
  * In the "Tasks" tab, veryfy that 6 tasks that you just launched is indeed running
- Task will run for 300 seconds and will then terminate
  * Wait for about ~15 minutes until the ECS cluster automatically terminates EC2 instances

<img src="imgs/run_task.png" width="60%">
<img src="imgs/ecs_instances.png" width="60%">
<img src="imgs/task_list.png" width="60%">
