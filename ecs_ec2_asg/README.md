
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

Finally, you must update the ECS configuration. Basically, this script updates "Instance Protection" property of the ASG, and add capacity provider to the cluster. This operation currently cannot be done through CDK. Thus, here I use a simple Python script to do this.

```
export ASG_NAME<your asg name>
export CLUSTER_NAME=<your cluster name>
python script.py $ASG_NAME $CLUSTER_NAME
```