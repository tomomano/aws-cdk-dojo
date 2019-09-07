# ECS Simple Web app

Original TypeScript code: https://aws.amazon.com/blogs/compute/getting-started-with-the-aws-cloud-development-kit-for-amazon-ecs/

This is essentially a Python implementation of the above code, with some minor modifications.

## Project structure
  * `app.py`: This will be the main entry point of the app.
  * `tutorial/`: The tutorial is here.

## Preparations

### (Optional) Set account credentials by environmental variable
Set the account which you use to deploy the service:
```bash
$ export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
$ export AWS_SECRET_ACCESS_KEY=ABCDEFGHIJK
```

## Now, let's start coding!

### Initialize a project

This is almost certainly a routine task you have done many times, so I won't explain much.
Create a new directory where you will build your project:
```bash
$ mkdir ecs_simple_web_app
$ cd ecs_simple_web_app
$ cdk init app --language=python
```
Then,
```bash
source .env/bin/activate
pip install -r requirements.txt
```

Above commands will create a directory named `ecs_simple_web_app`. Delete it, since we do not need it for now.

### Install additional aws-cdk modules
We will use the following modules to construct our stack.
```bash
pip install aws_cdk.aws_ecs aws_cdk.aws_ec2 aws_cdk.aws_elasticloadbalancingv2
```

### Create app.py
Copy and paste the following code in `app.py`.
```python
#!/usr/bin/env python3
import os
from aws_cdk import core

class GreetingStack(core.Stack):
    def __init__(self, parent, name, **kwargs):
        super().__init__(parent, name, **kwargs)


app = core.App()
greeting = GreetingStack(
    app, 'greeting-stack',
    env={
        "region": "us-east-1",
        "account": os.environ["CDK_DEFAULT_ACCOUNT"], 
    }
)

app.synth()
```

### Add ECS constructs
Now, let's add ECS stacks. 

First, we define a cluster where application runs. Modify our `GreetingStack` as follows:

```python
from aws_cdk import (
    core,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2
)

class GreetingStack(core.Stack):
    def __init__(self, parent, name, **kwargs):
        super().__init__(parent, name, **kwargs)

        vpc = ec2.Vpc(self, 'GreetingVpc', max_azs=2)

        # create an ECS cluster
        cluster = ecs.Cluster(self, "Cluster", vpc=vpc)

        # add capacity to id
        cluster.add_capacity('greeter-capacity',
            instance_type=ec2.InstanceType('t2.micro'),
            min_capacity=3,
            max_capacity=3   
        )
```

We've created a VPC to hold app application resources, and created an ECS cluster with three `t2.micro` instances.

References:
  * [ec2.Vpc](https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ec2/Vpc.html)
  * [ecs.Cluster](https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ecs/Cluster.html)

Now, to see if everything is working correctly so far, let us run
```
cdk deploy
```
This will deploy a new ECS cluster (but no tasks/service running). If you go to your AWS console and navigate to the ECS page, you will find a newly defined cluster.

![ECS cluster](imgs/cluster.png)

Now we will deploy a simple microservices stack onto this cluster. The final application architecture would be like this below (image from the original [tutorial](https://aws.amazon.com/blogs/compute/getting-started-with-the-aws-cloud-development-kit-for-amazon-ecs/)):

![application-architecture](https://d2908q01vomqb2.cloudfront.net/1b6453892473a467d07372d45eb05abc2031647a/2018/12/13/greeter-network.png)

### Add new ECS services

#### Add "name" service

We first define a "name" service, which returns random name upon request. We will use [nathanpeck/name](https://hub.docker.com/r/nathanpeck/name/) container. Add the following lines to `GreetStack`:
```python
# Name service
name_task_definition = ecs.Ec2TaskDefinition(self, "name-task-definition")

name_container = name_task_definition.add_container(
   'name',
   image=ecs.ContainerImage.from_registry('nathanpeck/name'),
   memory_limit_mib=128
)

name_container.add_port_mappings(ecs.PortMapping(
   container_port=3000
))

name_service = ecs.Ec2Service(self, "name-service",
   cluster=cluster,
   desired_count=2,
   task_definition=name_task_definition
)
```

And check the newly added resources in the stack:
```bash
$ cdk diff
...
Resources
[+] AWS::IAM::Role name-task-definition/TaskRole nametaskdefinitionTaskRole50FE
[+] AWS::ECS::TaskDefinition name-task-definition nametaskdefinition6907
[+] AWS::ECS::Service name-service/Service nameserviceService8015
```

References:
  * [ecs.Ec2TaskDefinition](https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ecs/Ec2TaskDefinition.html)
  * [ecs.Ec2Service](https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ecs/Ec2Service.html)

#### Add "greeting" service

Similarly, we add "greeting" service, to which we attach [nathanpeck/greeting](https://hub.docker.com/r/nathanpeck/greeting/) container.

Add the following lines to `GreetStack`:
```python
# Greeting service
greeting_task_definition = ecs.Ec2TaskDefinition(self, "greeting-task-definition")

greeting_container = greeting_task_definition.add_container(
   'greeting',
   image=ecs.ContainerImage.from_registry('nathanpeck/greeting'),
   memory_limit_mib=128
)

greeting_container.add_port_mappings(ecs.PortMapping(
   container_port=3000
))

greeting_service = ecs.Ec2Service(self, "greeting-service",
   cluster=cluster,
   desired_count=1,
   task_definition=greeting_task_definition
)
```

#### Add internal load balancers
Now we add internal load balancers, which handles the requests to "name" and "greeting" service.

Add the following lines to `GreetStack`:
```python
# Internal load balancer for the backend services
internal_listener = internal_lb.add_listener('PublicListener',
   port=80,
   open=True
)

internal_listener.add_target_groups('default',
   target_groups=[elbv2.ApplicationTargetGroup(
         self, 'default',
         vpc=vpc,
         protocol=elbv2.ApplicationProtocol.HTTP,
         port=80
   )]
)

internal_listener.add_targets('name',
   port=80,
   path_pattern='/name*',
   priority=1,
   targets=[name_service]
)

internal_listener.add_targets('greeting',
   port=80,
   path_pattern='/greeting*',
   priority=2,
   targets=[greeting_service]
)
```

References:
  * (aws_elasticloadbalancingv2.ApplicationLoadBalancer)[https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_elasticloadbalancingv2/ApplicationLoadBalancer.html]
  * (aws_elasticloadbalancingv2.ApplicationListener)[https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_elasticloadbalancingv2/ApplicationListener.html#aws_cdk.aws_elasticloadbalancingv2.ApplicationListener]
  * (aws_elasticloadbalancingv2.ApplicationTargetGroup)[https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_elasticloadbalancingv2/ApplicationTargetGroup.html]

#### Add front-facing service

Next, we add a front-facing service named "greeter", where we use [nathanpeck/greeter ](https://hub.docker.com/r/nathanpeck/greeter/) container. This will accept HTTP connections and sends a request to the internal load balancer.

Add the following lines to `GreetStack`:

```python
# Greeter service
greeter_task_definition = ecs.Ec2TaskDefinition(self, "greeter-task-definition")

greeter_container = greeter_task_definition.add_container(
   'greeter',
   image=ecs.ContainerImage.from_registry('nathanpeck/greeter'),
   memory_limit_mib=128,
   environment={
         "GREETING_URL": 'http://' + internal_lb.load_balancer_dns_name + '/greeting',
         "NAME_URL": 'http://' + internal_lb.load_balancer_dns_name + '/name'
   }
)

greeter_container.add_port_mappings(ecs.PortMapping(
   container_port=3000
))

greeter_service = ecs.Ec2Service(self, "greeter-service",
   cluster=cluster,
   desired_count=2,
   task_definition=greeter_task_definition
)
```

Then we add load balancer:

```python
# Internet facing load balancer for the frontend services
external_lb = elbv2.ApplicationLoadBalancer(self, 'external',
   vpc=vpc,
   internet_facing=True
)

external_listener = external_lb.add_listener('PublicListener',
   port=80,
   open=True
)

external_listener.add_targets('greeter',
   port=80,
   targets=[greeter_service]
)
```

### Define some CloudFormation outputs
Finally, add the following lines to `GreetStack`, so that we know what are the resulting DNS addresses.

```python
# output dns addresses
self.internal_dns = core.CfnOutput(self, 'InternalDNS',
   export_name='greeter-app-internal',
   value=internal_lb.load_balancer_dns_name
)
self.external_dns = core.CfnOutput(self, 'ExternalDNS',
   export_name='ExternalDNS',
   value=external_lb.load_balancer_dns_name
)
```

#### Deploy!
Now, your application stack is complete. Run
```
cdk deploy
```

Once deployment is complete (which will take several minutes), try to access the `ExternalDNS` (which will be shown in the output of cdk deploy) using your browser. You will see a nice message with random greeting and name, which will change each time you refresh the page!

![Result](imgs/result.png)