from aws_cdk import (
    core,
    aws_s3 as s3,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_lambda_event_sources as esources
)

class MyStack(core.Stack):

    def __init__(self, parent: core.App, name: str, **kwargs):
        super().__init__(parent, name, **kwargs)
        
        # prepare a S3 bucket to upload data
        bucket = s3.Bucket(
            self, "DataBucket",
            public_read_access=True,
            removal_policy=core.RemovalPolicy.DESTROY
        )

        # output generated bucket name
        core.CfnOutput(self, 'Bucket', value=bucket.bucket_name)

        # VPC for the ECS cluster
        vpc = ec2.Vpc(self, 'ClusterVpc', max_azs=2)

        # create an ECS cluster
        cluster = ecs.Cluster(self, "Cluster", vpc=vpc, cluster_name="thumb-cluster")

        # fargate task definition
        thumb_task_def = ecs.FargateTaskDefinition(
            self, "ffmpeg-thumb-task-definition",
            memory_limit_mib=512,
            cpu=256 # meanining .25 vCPU
        )

        # grant PUT operation to S3 bucket
        bucket.grant_write(thumb_task_def.task_role)

        thumb_container = thumb_task_def.add_container(
            'ffmpeg-thumb',
            image=ecs.ContainerImage.from_registry('rupakg/docker-ffmpeg-thumb'),
            logging=ecs.LogDriver.aws_logs(stream_prefix="ffmpeg-thumb")
        )

        thumb_container.add_port_mappings(
            ecs.PortMapping(container_port=8081)
        )

        # set environmental variable for this lambda
        on_upload_video_env = {
            "ECS_CLUSTER_NAME": cluster.cluster_name,
            "ECS_TASK_DEFINITION": thumb_task_def.family,
            "ECS_TASK_VPC_SUBNET_1": vpc.private_subnets[0].subnet_id,
            "ECS_TASK_VPC_SUBNET_2": vpc.private_subnets[1].subnet_id,
            "OUTPUT_S3_PATH": bucket.bucket_name + '/thumb',
            "OUTPUT_S3_AWS_REGION": 'us-east-1'
        }
        # define lambda function
        on_upload_video = _lambda.Function(
            self, 'onVideoUploadFunction',
            code=_lambda.AssetCode('./lambda'),
            handler='lambda_funcs.trigger_on_upload_video',
            runtime=_lambda.Runtime.PYTHON_3_7,
            environment=on_upload_video_env
        )
        
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

        # add S3 upload event
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

        # another lambda
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
                filters=[
                    s3.NotificationKeyFilter(prefix="thumb/", suffix=".png")
                ]
            )
        )


