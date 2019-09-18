# Tutorial

This project was inspired by [this blog](https://serverless.com/blog/serverless-application-for-long-running-process-fargate-lambda/) from serverless.com.

I implemented a very similar type of ECS application explained in the above link, using AWS CDK on Python.

## Project structure
  * `app.py`: This will be the main entry point of the app.
  * `my_stack.py`: An application stack is defined here.
  * `lambda/lambda_funcs.py`: Lambda function handlers are defined here.

## Frequently used command list
Set the account which you use to deploy the service:
```
$ export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
$ export AWS_SECRET_ACCESS_KEY=ABCDEFGHIJK
```

## Now, let's start coding!

### Initialize a project
Create a new directory where we will build our new project:
```bash
$ mkdir s3_lambda_ecs
```

`cd` into it and initialize a CDK project:
```bash
$ cd s3_lambda_ecs
$ cdk init app --language=python
```
This command will create a directory named `s3_lambda_ecs`. Delete it, since we do not need it for now.

Then install Python dependencies by pip:
```bash
source .env/bin/activate
pip install -r requirements.txt
```

### Install additional aws-cdk modules
```bash
pip install aws-cdk.aws-lambda aws-cdk.aws-dynamodb aws-cdk.aws-s3 aws_cdk.aws_ecs aws_cdk.aws_ec2 aws_cdk.aws_lambda_event_sources
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
This will be the entry point of our AWS application stack. Below, we will construct `MyStack` stack. As you can see, we will deploy our service in `us-east-1` region. Change it if necessary.

### Create my_stack.py
Create a file named `my_stack.py`. First, let's import python modules that we will use in the stack:
```python
from aws_cdk import (
    core,
    aws_s3 as s3,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_lambda_event_sources as esources
)
```

Let's initialize our stack:
```python
class MyStack(core.Stack):

    def __init__(self, parent: core.App, name: str, **kwargs):
        super().__init__(parent, name, **kwargs)
```

### Create a S3 bucket
Now, we prepare a S3 bucket to upload data. Add the following lines to `MyStack`:
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

To allow the container to write data to S3 bucket, we grant a permission to the ECS task role:
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
To check if everything is working correctly so far, run `cdk deploy` to deploy our stack.

Once deployment finishes, first go to your S3 console, and confirm that an empty new bucket, whose name should start with `s3-lambda-ecs-databucket`, is created.

To do a test run below, we need to upload a random mp4 video. Prepare your own mp4 movie, and upload it with the file name `random.mp4`.

Next, go to your ECS console, and confirm that a new cluster named `thumb-cluster` is created. This cluster should be empty now.

Then, in `Task Definition`, you should find an item whose name should start wtih `s3lambdaecsffmpegthumbtaskdefinition`. Open the task definition, and make sure that the properties that we defined in our CDK code (such as CPU limits and port mappings) were indeed reflected here.

Now, let's run a task programatically using Python code! This Python code will eventually go to the Lambda handler that we will define later.

From your local Python interpreter (>=3.7 recommended) with `boto3` library installed, run the following script. **Remember to replace the values represented as `<XXX>` with your own settins.**

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

Now, let's automate what we did above, i.e. running the ECS task automatically by creating a Lambda function.

First, prepare environmental variables that we will need to pass to Lambda:
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
See `lambda/lambda_functs.py` to see the handler function. It is essentially the same code that we run just before, with some modifications so that it fits in Lambda.

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
The bottom two rules regarding `iam:PassRole` of task execution role and task role are not intuitive. Indeed, I (author) still do not know why they are necessary. All I know is that Lambda cannot start ECS task without them. For more information, see the following links:
  * https://lobster1234.github.io/2017/12/03/run-tasks-with-aws-fargate-and-lambda/
  * https://serverfault.com/questions/945596/why-does-aws-lambda-need-to-pass-ecstaskexecutionrole-to-ecs-task

Let's deploy and test it! Run `cdk deploy`. When deployment is complete, go to your Lambda console. Then, to define a test environment, click `Test` buton on the top-left of the page, and then configure the event. To do so, choose "S3PutEvent" as the event template, and modify the following parts shown below:

![Lambda event configuration](imgs/lambda_event.png)

Once this is created, click `Test` to invoke Lambda function. Then, go to your ECS console and make sure that a new task is running. Finally, go to your S3 and validate that the thumbnail image was created! Nice!!

### Adding S3 upload event
Now, to automatically invoke the above Lambda function when a file gets uploaded, we add a event lister:
```python
on_upload_video.add_event_source(
    esources.S3EventSource(
        bucket,
        events=[
            s3.EventType.OBJECT_CREATED
        ],
        filters=[
            s3.NotificationKeyFilter(suffix=".mp4")
        ]
    )
)
```

Run `cdk deploy` and go to S3 console. Upload a random mp4 video and check that the new event indeed fires a lamunda function (and subsequently ECS task).

### Add another Lambda function...
To get notification that a thumbnail is generated, let's make another Lambda function.

Add the following handler function to `lambda_funcs.py`:
```python
def trigger_on_thumbnail_creation(event, context):

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    print(json.dumps(event))
    print(f"A new thumbnail file was generated at 'https://s3.amazonaws.com/{bucket}/{key}'.")
```

Then, register this in Lambda:
```python
on_thumb_creation = _lambda.Function(
    self, 'OnThumbnailCreation',
    code=_lambda.AssetCode('./lambda'),
    handler='lambda_funcs.trigger_on_thumbnail_creation',
    runtime=_lambda.Runtime.PYTHON_3_7,
)
on_thumb_creation.add_event_source(
    esources.S3EventSource(
        bucket,
        events=[
            s3.EventType.OBJECT_CREATED
        ],
        rules=[
            s3.NotificationKeyFilter(prefix="thumb/", suffix=".png")
        ]
    )
)
```

Run `cdk deploy` and upload a random video to the S3 bucket. Then, go to "CloudWatch" > "Logs", and find a entry that begins with `/aws/lambda/s3-lambda-ecs-OnThumbnailCreation`. Go into the log list, and find a line that reads "A new thumbnail file was generated at 'https://s3.amazonaws.com/XXX/YYY".

That's it! We've created a integrated app that combines S3, Lambda and ECS, and defined a automated task runner that processes mp4 videos. All in a `serverless` way!