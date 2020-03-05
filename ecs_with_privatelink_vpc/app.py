import os
from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_autoscaling as autoscaling
)

class EcsCluster(core.Stack):

    def __init__(self, scope: core.Construct, name: str, **kwargs) -> None:
        super().__init__(scope, name, **kwargs)

        # prepare VPC
        vpc = ec2.Vpc(
            self, "CustomVpc",
            cidr="10.0.0.0/16",
            max_azs=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="PublicSubnet",
                    cidr_mask=26,
                    subnet_type=ec2.SubnetType.PUBLIC,
                )
            ],
            nat_gateways=0,
        )

        # create Amazon ECS cluster
        cluster = ecs.Cluster(
            self, "CdkTutorial_Cluster",
            vpc=vpc,
        )

        # step 2 - create the auto scaling resources
        asg = autoscaling.AutoScalingGroup(
            self, "CdkTutorial_ASG",
            instance_type=ec2.InstanceType('t2.micro'),
            machine_image=ecs.EcsOptimizedImage.amazon_linux2(),
            vpc=vpc,
            max_capacity=10,
            min_capacity=0,
        )
        asg.add_user_data(
            f"echo ECS_CLUSTER={cluster.cluster_name} >> /etc/ecs/ecs.config"
        )
        cluster.add_auto_scaling_group(asg)

        # step 3 - task definition
        task_def = ecs.Ec2TaskDefinition(
            self, "CdkTutorial_TaskDefinition",
            network_mode=ecs.NetworkMode.BRIDGE,
        )
        container = task_def.add_container(
            "CdkTutorialContainer",
            image=ecs.ContainerImage.from_asset(
                os.path.join(os.path.dirname(__file__), "docker")
            ),
            command=["--cpu", "1", "--vm-bytes", "128M", "--timeout", "300s"], # simulated load, consuming 1 CPU and 128MB of RAM
            memory_reservation_mib=256,
        )

app = core.App()
EcsCluster(
    app, "CdkTutorialStack",
    env={
        "region": os.environ["CDK_DEFAULT_REGION"],
        "account": os.environ["CDK_DEFAULT_ACCOUNT"], 
    }
)
app.synth()
