## Now, let's start coding!

### Initialize a project
Create a new directory where you will build your project:
```bash
$ mkdir s3_lambda_ecs
```

`cd` into it and initialize a CDK project:
```bash
$ cd s3_lambda_ecs
$ cdk init app --language=python
```
This command will create a directory named `s3_lambda_ecs`. Delete it, since we do not need it for now.

Then install dependencies by pip:
```bash
source .env/bin/activate
pip install -r requirements.txt
```

### Install additional aws-cdk modules
```bash
pip install aws-cdk.aws-lambda aws-cdk.aws-dynamodb aws-cdk.aws-s3 aws_cdk.aws_ecs aws_cdk.aws_ec2
```

### Create app.py

Copy and paste the following code in `app.py`.
```python
import os
from aws_cdk import core

from my_stack import MyStack

app = core.App()
MyStack(
    app, "s3-lambda-ecs",
    env={
        "region": "us-east-1",
        "account": os.environ["CDK_DEFAULT_ACCOUNT"], 
    }
)

app.synth()
```
This will be the entry point of our AWS application stack. Below, we will construct `MyStack` stack.

### Create my_stack.py
Create a file named `my_stack.py`. First, let's import python modules that we will use in the stack:
```
from aws_cdk import (
    core,
    aws_s3 as s3,
    aws_ec2 as ec2,
    aws_ecs as ecs
)
```

To initialize our stack, copy and paste the following code.
```python
class MyStack(core.Stack):

    def __init__(self, parent: core.App, name: str, **kwargs):
        super().__init__(parent, name, **kwargs)
```

### Create a S3 bucket
Next, we prepare a S3 bucket to upload data. Add the following lines to `MyStack`:
```python
# prepare a S3 bucket to upload data
bucket = s3.Bucket(
   self, "S3Bucket",
   public_read_access=True,
   removal_policy=core.RemovalPolicy.DESTROY
)

# output generated bucket name
core.CfnOutput(self, 'Bucket', value=bucket.bucket_name)
```

### Create a ECS task definition that performs thumbnail generation
Next, we define a ECS task definition using Fargate instance type.

First, we need a VPC:
```python
# VPC for the ECS cluster
vpc = ec2.Vpc(self, 'ClusterVpc', max_azs=2)
```
Then we define a new cluster and attach the above VPC to it:
```python
# create an ECS cluster
cluster = ecs.Cluster(self, "Cluster", vpc=vpc, cluster_name="thumb-cluster")
```

Next, we make a task definition using Fargate instance type:
```python
# fargate task definition
thumb_task_def = ecs.FargateTaskDefinition(
    self, "ffmpeg-thumb-task-definition",
    memory_limit_mib=512,
    cpu=256 # meanining .25 vCPU
)
```
To allow the container to write data to S3 bucket, we grant a permission:
```python
# grant PUT operation to S3 bucket
bucket.grant_write(thumb_task_def.task_role)
```

Next, we prepare a container that run within this task:
```python
thumb_container = thumb_task_def.add_container(
    'ffmpeg-thumb',
    image=ecs.ContainerImage.from_registry('rupakg/docker-ffmpeg-thumb'),
    logging=ecs.LogDriver.aws_logs(stream_prefix="ffmpeg-thumb")
)

thumb_container.add_port_mappings(
    ecs.PortMapping(container_port=8081)
)
```
Here, we specified that the container logs should be forwarded to AWS log driver, so that you can see the log in your CloudWatch console.

### Check what we have done so far
To check if everything is working correctly so far, run `cdk deploy` to deploy our current stack.

Once deployment finishes, first go to your S3 console, and confirm that an empty new bucket, whose name should start with `s3-lambda-ecs-databucket`, is created.

To do a test run below, we need to upload a random mp4 video. Prepare your own mp4 movie, and upload it with the file name `random.mp4`.

Next, go to your ECS console, and confirm that a new cluster named `thumb-cluster` is created. This cluster should be empty now.

Then, in `Task Definition`, you should find an item whose name should start wtih `s3lambdaecsffmpegthumbtaskdefinition`. Open the task definition, and make sure that the properties that we defined (such as CPU limits and port mappings) in our CDK code were indeed reflected here.

Now, let's run a task from Python code! This Python code will eventually go to the Lambda handler that we will define later.

From your local Python interpreter (>3,7) with `boto3` library installed, run the following script. **Remember to replace the values represented as `<XXX>` with your own settins.**

```python
import boto3
session = boto3.Session(profile_name=<YOUR PROFILE NAME>)
client = session.client('ecs')

response = client.run_task(
    cluster='thumb-cluster',
    taskDefinition='<YOUR TASK DEFINITION NAME>',
    launchType='FARGATE',
    count=1,
    platformVersion='LATEST',
    networkConfiguration={
      'awsvpcConfiguration': {
          'subnets': [
              '<YOUR SUBNET 1>',
              '<YOUR SUBNET 2>'
          ],
          'assignPublicIp': 'ENABLED'
      }
    },
    overrides={
        'containerOverrides': [
            {
                'name': 'ffmpeg-thumb',
                'environment': [
                    {
                        'name': 'INPUT_VIDEO_FILE_URL',
                        'value': 'https://<YOUR S3 BUCKET NAME>.s3.amazonaws.com/random.mp4'
                    },
                    {
                        'name': 'OUTPUT_THUMBS_FILE_NAME',
                        'value': "random.png"
                    },
                    {
                        'name': 'POSITION_TIME_DURATION',
                        'value': "00:02"
                    },
                    {
                        'name': 'OUTPUT_S3_PATH',
                        'value': "<YOUR S3 BUCKET NAME>/thumb"
                    },
                    {
                        'name': 'AWS_REGION',
                        'value': "us-east-1"
                    }
                ]
            }
        ]
    }
)
```

Once you run this code, go to your ECS console. In your "thumb-cluster", you will find that a new task is running. You can see the execution log by going to the "Logs" tab of the task menu.

Once the container finishes running, go to your S3 console and confirm that a thumbnail image was created in your bucket. Sweet!!

### Building a lambda handler

Now, let's automate the ECS task initiation by creating a Lambda function.


First, prepare environmental variables that we will pass to Lambda:
```python
on_upload_video_env = {
    "ECS_CLUSTER_NAME": cluster.cluster_name,
    "ECS_TASK_DEFINITION": thumb_task_def.family,
    "ECS_TASK_VPC_SUBNET_1": vpc.private_subnets[0].subnet_id,
    "ECS_TASK_VPC_SUBNET_2": vpc.private_subnets[1].subnet_id,
    "OUTPUT_S3_PATH": bucket.bucket_name + '/thumb',
    "OUTPUT_S3_AWS_REGION": 'us-east-1'
}
```
Then define a Lambda function:
```python
on_upload_video = _lambda.Function(
    self, 'onVideoUploadFunction',
    code=_lambda.AssetCode('./lambda'),
    handler='lambda_funcs.trigger_on_upload_video',
    runtime=_lambda.Runtime.PYTHON_3_7,
    environment=on_upload_video_env
)
```
We will need to grant permissions for the Lambda function so that it can access to S3 and ECS.
```python
# grant read permission
bucket.grant_read(on_upload_video)
# gran permission to execute ECS jobs
on_upload_video.add_to_role_policy(
    iam.PolicyStatement(
        effect=iam.Effect.ALLOW,
        resources=["*"],
        actions=['ecs:RunTask']
    )
)
on_upload_video.add_to_role_policy(
    iam.PolicyStatement(
        effect=iam.Effect.ALLOW,
        resources=[thumb_task_def.execution_role.role_arn],
        actions=['iam:PassRole']
    )
)
on_upload_video.add_to_role_policy(
    iam.PolicyStatement(
        effect=iam.Effect.ALLOW,
        resources=[thumb_task_def.task_role.role_arn],
        actions=['iam:PassRole']
    )
)
```
The bottom two rules regarding task definition's execution role and task role are not intuitive. Indeed, author still do not know why they are necessary. All I know is that Lambda cannot start ECS task without them. For more information, see the following links:
  * https://lobster1234.github.io/2017/12/03/run-tasks-with-aws-fargate-and-lambda/
  * https://serverfault.com/questions/945596/why-does-aws-lambda-need-to-pass-ecstaskexecutionrole-to-ecs-task

By the way, here is the contents of the Lambda function handler (`lambda/lambda_funcs.py`):
```python
import os
import boto3

ECS_CLUSTER_NAME = os.environ["ECS_CLUSTER_NAME"]
ECS_TASK_DEFINITION = os.environ["ECS_TASK_DEFINITION"]
ECS_TASK_VPC_SUBNET_1 = os.environ["ECS_TASK_VPC_SUBNET_1"]
ECS_TASK_VPC_SUBNET_2 = os.environ["ECS_TASK_VPC_SUBNET_2"]
OUTPUT_S3_PATH = os.environ["OUTPUT_S3_PATH"]
OUTPUT_S3_AWS_REGION = os.environ["OUTPUT_S3_AWS_REGION"]

def trigger_on_upload_video(event, context):

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    s3_video_url = f"https://s3.amazonaws.com/{bucket}/{key}"
    thumbnail_file = os.path.splitext(key)[0] + ".png"
    frame_pos = '00:02' # we use constant value here for demonstration

    run_thumbnail_generate_task(s3_video_url, thumbnail_file, frame_pos)

def run_thumbnail_generate_task(s3_video_url, thumbnail_file, frame_pos):
    
    client = boto3.client('ecs')

    response = client.run_task(
        cluster=ECS_CLUSTER_NAME,
        taskDefinition=ECS_TASK_DEFINITION,
        launchType='FARGATE',
        count=1,
        platformVersion='LATEST',
        networkConfiguration={
            'awsvpcConfiguration': {
                'subnets': [
                    ECS_TASK_VPC_SUBNET_1,
                    ECS_TASK_VPC_SUBNET_2
                ],
                'assignPublicIp': 'ENABLED'
                }
        },
        overrides={
            'containerOverrides': [
                {
                    'name': 'ffmpeg-thumb',
                    'environment': [
                        {
                            'name': 'INPUT_VIDEO_FILE_URL',
                            'value': s3_video_url
                        },
                        {
                            'name': 'OUTPUT_THUMBS_FILE_NAME',
                            'value': thumbnail_file
                        },
                        {
                            'name': 'POSITION_TIME_DURATION',
                            'value': frame_pos
                        },
                        {
                            'name': 'OUTPUT_S3_PATH',
                            'value': OUTPUT_S3_PATH
                        },
                        {
                            'name': 'AWS_REGION',
                            'value': OUTPUT_S3_AWS_REGION
                        }
                    ]
                }
            ]
        }
    )
```

Let's deploy and test it!

When deployment is complete, go to your Lambda console. Then, to define a test environment, click `Test` on the top left, and then configure the event. To do so, choose "S3PutEvent" as the event template, and modify the following parts shown below:

![Lambda event configuration](imgs/lambda_event.png)

Once this is run, click `Test` to invoke Lambda function. Then, go to your ECS console and make sure that a new task is running. Finally, go to your S3 and validate that the thumbnail image was created!

