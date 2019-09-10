from aws_cdk import (
    core,
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_ecs as ecs
)

class LambdaTrigger(core.Construct):

    def __init__(self, parent: core.Construct, name: str, bucket: s3.IBucket, ecs ) -> None:
        super().__init__(parent, name)

        # set environmental variable for this lambda
        on_upload_video_env = {
            "ECS_CLUSTER_NAME": ""
            "ECS_TASK_DEFINITION": 'itemID',
            "ECS_TASK_VPC_SUBNET_1": '',
            "ECS_TASK_VPC_SUBNET_2": "",
            "OUTPUT_S3_PATH": "",
            "OUTPUT_S3_AWS_REGION": ""
        }

        on_upload_video = _lambda.Function(
            self, 'onVideoUploadFunction',
            code=_lambda.AssetCode('./'),
            handler='lambda_funcs.trigger_on_upload_video',
            runtime=_lambda.Runtime.PYTHON_3_7,
            environment=on_upload_video_env
        )
