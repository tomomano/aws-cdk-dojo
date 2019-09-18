# ECS task execution with Lambda and S3
This project was inspired by [this blog](https://serverless.com/blog/serverless-application-for-long-running-process-fargate-lambda/) from serverless.com.

I implemented a very similar type of ECS application explained in the above link, using AWS CDK on Python.

## Build
```bash
python3 -m venv .env
source .env/bin/activate
pip install -r requirements.txt
```
Synthesize the CloudFormation template by
```bash
cdk synth
```

## Deploy
(Optional) Set the account which you use to deploy the service:
```bash
$ export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
$ export AWS_SECRET_ACCESS_KEY=ABCDEFGHIJK
```
To deploy the app, run
```bash
cdk deploy
```

When you are done with the app, do not forget to destroy it:
```bash
cdk destroy
```

## Test
The stack will create a S3 bucket, whose name should begin with `s3-lambda-ecs-databucket`. Upload a random .mp4 movie to it, and wait a minute or two. Refresh your S3 console, and you should find that a thumbanil of the movie (with file name `<movie base name>.png` was created for you!

If you want to see how the process is running, go to the ECS console and find a cluster named `thumb-cluster`.

## Project structure
  * `app.py`: This will be the main entry point of the app.
  * `my_stack.py`: An application stack is defined here.
  * `lambda/lambda_funcs.py`: Lambda function handlers are defined here.