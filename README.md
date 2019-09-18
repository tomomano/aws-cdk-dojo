# AWS CDK Dojo

This is a collection of example projects using AWS CDK. These projects are intended for those who are getting started with AWS CDK and looking for concrete and realistic examples to build their own app. All stacks are written in Python.

Some of the projects are re-implementation of the [official aws-cd-examples repository](https://github.com/aws-samples/aws-cdk-examples) using Python (original code in TypeScript).

Other projects are my original, with inspirations from other online tutorials.

**Dojo** stands for "training gym" in Japanese :punch:

## Projects

| Name      | Description | Level |
| ----------- | ----------- | ----- |
| static-site | We will create a simple static web site using S3. Then we will connect the bucket with CloudFront and enable HTTPS communitation. (re-implementation of [this](https://github.com/aws-samples/aws-cdk-examples/tree/master/typescript/static-site) in Python)| 1 |
| api-cors-lambda-crud-dynamodb | We will create a simple set of APIs using Lambda and API Gateway, which manipulates DynamoDB tables. (re-implementation of [this](https://github.com/aws-samples/aws-cdk-examples/tree/master/typescript/api-cors-lambda-crud-dynamodb) in Python)| 1 |
| ecs_simple_web_app | We will create a simple ECS app, which accepts a simple API and prints a greeting message. We will also attach a load balancer. (Inspired by [this blog]( https://aws.amazon.com/blogs/compute/getting-started-with-the-aws-cloud-development-kit-for-amazon-ecs/)) | 2 |
| ecs_simple_web_app | We will create a simple ECS app, which automatically generates a thumbanil whena movie is uploaded to S3 bucket. (Inspired by [this blog](https://serverless.com/blog/serverless-application-for-long-running-process-fargate-lambda/))| 2 |

## Tutorials
For each project, you should be able to deploy the app out of the box just by cloning the repo and running a few commands (see README of each project).

If you would like to learn how to build the program from scrach, a brief step-by-step build procedure is described in `tutorial/` directory of each project.

## Disclaimer
The project here are just examples for learning, and not at all intended for production.

## Contact me
If you have any questions or find any bugs, please submit an issue :wink: