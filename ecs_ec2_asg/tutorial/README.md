## Now, let's start coding!

### Initialize a project
Create a new directory where we will build our new project:
```bash
$ mkdir ecs_ec2_asg
```

`cd` into it and initialize a CDK project:
```bash
$ cd ecs_ec2_asg
$ cdk init app --language=python
```
This command will create a directory named `ecs_ec2_asg`. Delete it, since we do not need it for now.

Then install Python dependencies by pip:
```bash
source .env/bin/activate
pip install -r requirements.txt
```

### Install additional aws-cdk modules
```bash
pip install aws_cdk.aws_ecs aws_cdk.aws_ec2
```