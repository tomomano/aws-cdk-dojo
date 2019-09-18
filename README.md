# AWS CDK Dojo

This is a collection of example projects using AWS CDK. All stacks are written in Python.

Some of the projects are re-implementation of the [official aws-cd-examples repository](https://github.com/aws-samples/aws-cdk-examples) using Python (original code in TypeScript).

Other projects are my original, with inspirations from other online tutorials.

## Projects

| Name      | Description | Level |
| ----------- | ----------- | ----- |
| static-site | We will create a simple static web site using S3. Then we will connect the bucket with CloudFront and enable HTTPS communitation. | 1 |
| api-cors-lambda-crud-dynamodb | We will create a simple API using Lambda and API Gateway, which manipulates DynamoDB tables | 1 |
| ecs_simple_web_app | We will create a simple ECS app, which accepts a simple API and prints a greeting message. We will also attach a load balancer. | 2 |
| ecs_simple_web_app | We will create a simple ECS app, which automatically generates a thumbanil whena movie is uploaded to S3 bucket. | 2 |