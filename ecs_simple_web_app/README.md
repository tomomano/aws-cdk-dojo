# ECS Simple Web App

Original TypeScript code: https://aws.amazon.com/blogs/compute/getting-started-with-the-aws-cloud-development-kit-for-amazon-ecs/

This is essentially a Python implementation of the above code, with some minor modifications.

## Deploy

## Build
Install Python dependencies:
```bash
python3 -m venv .env
source .env/bin/activate
pip install -r requirements.txt
```

You can build the CloudFormation template by:
```bash
$ cdk synth
```

Deploy the application stack by:
```bash
$ cdk deploy
```

When you are done with the app, do not forget to destroy it:
```bash
cdk destroy
```

## Test
Once deployment is complete (which will take several minutes), try to access the `ExternalDNS` URL (which will be shown in the output of cdk deploy) using your browser. You will see a nice message with random greeting and name, which will change each time you refresh the page!

![Result](tutorial/imgs/result.png)