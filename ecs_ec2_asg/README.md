
# ECS with EC2 autoscaling example

## Build
```
python3 -m venv .env
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

When you are done with the app, do not forget to destroy it:

```
cdk destroy
```