#!/usr/bin/env python3
import os
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

        internal_lb = elbv2.ApplicationLoadBalancer(self, "internal",
            vpc=vpc,
            internet_facing=False    
        )

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

        # Internet facing load balancer fo the frontend services
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

        # output dns addresses
        self.internal_dns = core.CfnOutput(self, 'InternalDNS',
            export_name='greeter-app-internal',
            value=internal_lb.load_balancer_dns_name
        )
        self.external_dns = core.CfnOutput(self, 'ExternalDNS',
            export_name='ExternalDNS',
            value=external_lb.load_balancer_dns_name
        )


app = core.App()
greeting = GreetingStack(
    app, 'greeting-stack',
    env={
        "region": "us-east-1",
        "account": os.environ["CDK_DEFAULT_ACCOUNT"], 
    }
)

app.synth()
