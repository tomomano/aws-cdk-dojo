import os
import boto3

ECS_CLUSTER_NAME = os.environ["ECS_CLUSTER_NAME"]
ECS_TASK_DEFINITION = os.environ["ECS_TASK_DEFINITION"]
ECS_TASK_VPC_SUBNET_1 = os.environ["ECS_TASK_VPC_SUBNET_1"]
ECS_TASK_VPC_SUBNET_2 = os.environ["ECS_TASK_VPC_SUBNET_2"]
OUTPUT_S3_PATH = os.environ["OUTPUT_S3_PATH"]
OUTPUT_S3_AWS_REGION = os.environ["OUTPUT_S3_AWS_REGION"]

def trigger_on_upload_video(event, context):

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    s3_video_url = f"https://s3.amazonaws.com/{bucket}/{key}"
    thumbnail_file = os.path.splitext(key)[0] + ".png"
    frame_pos = '00:02' # we use constant value here for demonstration

    run_thumbnail_generate_task(s3_video_url, thumbnail_file, frame_pos)

def run_thumbnail_generate_task(s3_video_url, thumbnail_file, frame_pos):
    
    client = boto3.client('ecs')

    response = client.run_task(
        cluster=ECS_CLUSTER_NAME,
        taskDefinition=ECS_TASK_DEFINITION,
        launchType='FARGATE',
        count=1,
        platformVersion='LATEST',
        networkConfiguration={
            'awsvpcConfiguration': {
                'subnets': [
                    ECS_TASK_VPC_SUBNET_1,
                    ECS_TASK_VPC_SUBNET_2
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
                            'value': s3_video_url
                        },
                        {
                            'name': 'OUTPUT_THUMBS_FILE_NAME',
                            'value': thumbnail_file
                        },
                        {
                            'name': 'POSITION_TIME_DURATION',
                            'value': frame_pos
                        },
                        {
                            'name': 'OUTPUT_S3_PATH',
                            'value': OUTPUT_S3_PATH
                        },
                        {
                            'name': 'AWS_REGION',
                            'value': OUTPUT_S3_AWS_REGION
                        }
                    ]
                }
            ]
        }
    )

    
    