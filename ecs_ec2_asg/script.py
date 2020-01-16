import boto3
import argparse

def main(autoscaling_group_name: str, ecs_cluster_name: str, capacity_provider_name: str = "CapacityProvider"):
    """

    """
    client = boto3.client("autoscaling")

    print("Updating ASG configuration...")
    # first, change Instance Protection setting of the asg
    resp = client.update_auto_scaling_group(
        AutoScalingGroupName=autoscaling_group_name,
        NewInstancesProtectedFromScaleIn=True,
    )
    # get the ARN of the ASG
    resp = client.describe_auto_scaling_groups(
        AutoScalingGroupNames=[autoscaling_group_name]
    )
    asg_arn = resp['AutoScalingGroups'][0]['AutoScalingGroupARN']
    print("Done.")

    # next, add capacity provider
    client = boto3.client("ecs")
    print("Adding capacity provider to the ECS cluster...")
    resp = client.create_capacity_provider(
        name=capacity_provider_name,
        autoScalingGroupProvider={
            'autoScalingGroupArn': asg_arn,
            'managedScaling': {
                'status': 'ENABLED',
                'targetCapacity': 100,
                'minimumScalingStepSize': 1,
                'maximumScalingStepSize': 100,
            },
            'managedTerminationProtection': 'ENABLED',
        },
    )
    client.put_cluster_capacity_providers(
        cluster=ecs_cluster_name,
        capacityProviders=[capacity_provider_name],
        defaultCapacityProviderStrategy=[
            {
                'capacityProvider': capacity_provider_name,
                'weight': 1,
                'base': 0
            },
        ]
    )
    print("Done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'autoscaling_group_name', type=str,
    )
    parser.add_argument(
        'ecs_cluster_name', type=str
    )

    args = parser.parse_args()
    main(args.autoscaling_group_name, args.ecs_cluster_name)