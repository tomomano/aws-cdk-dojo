from aws_cdk import (
    core,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_certificatemanager as acm,
    aws_route53 as route53,
    aws_route53_targets as route53_targets,
)
import os
from dataclasses import dataclass

@dataclass
class DomainStackProps:
    domain_name: str
    certificate_arn: str

handler_func = """
import json

def handler(event, context):
    print('request: {}'.format(json.dumps(event)))
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': 'Hello, CDK! You have hit {}'.format(event['path'])
    }
"""

class DomainStack(core.Stack):
    """
    This stack defines a domain for API Gateway resources, and link it with Route53
    """
    def __init__(self, scope: core.App, id: str, props: DomainStackProps, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        domain = apigw.DomainName(
            self, "domain",
            domain_name=props.domain_name,
            certificate=acm.Certificate.from_certificate_arn(
                self, 'cert', props.certificate_arn
            ),
            endpoint_type=apigw.EndpointType.REGIONAL,
        )
        self.domain = domain

        route53.ARecord(
            self, "AliasRecord",
            zone=route53.HostedZone.from_lookup(
                self, 'zone', domain_name=props.domain_name
            ),
            target=route53.RecordTarget.from_alias(
                route53_targets.ApiGatewayDomain(domain)
            )
        )

class FirstAPI(core.Stack):
    """
    First API, hosted under '/api1' base path
    """
    def __init__(self, scope: core.App, id: str, domain: apigw.DomainName, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        api = apigw.RestApi(self, 'api1')
        domain.add_base_path_mapping(api, base_path="api1")

        hello_handler = _lambda.Function(
            self, 'LambdaHandler',
            runtime=_lambda.Runtime.PYTHON_3_7,
            handler="index.handler",
            code=_lambda.Code.from_inline(handler_func),
        )
        api.root.add_method("GET", apigw.LambdaIntegration(hello_handler))

class SecondAPI(core.Stack):
    """
    Second API, hosted under 'api2' base path
    """
    def __init__(self, scope: core.App, id: str, domain: apigw.DomainName, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        api = apigw.RestApi(self, 'api2')
        domain.add_base_path_mapping(api, base_path="api2")

        hello_handler = _lambda.Function(
            self, 'LambdaHandler',
            runtime=_lambda.Runtime.PYTHON_3_7,
            handler="index.handler",
            code=_lambda.Code.from_inline(handler_func),
        )
        api.root.add_method("GET", apigw.LambdaIntegration(hello_handler))

app = core.App()
domain_stack = DomainStack(
    app, "DomainStack",
    env={
        "region": "us-east-1",
        "account": os.environ["CDK_DEFAULT_ACCOUNT"],
    },
    props=DomainStackProps(
        domain_name=os.environ["DOMAIN_NAME"],
        certificate_arn=os.environ["CERTIFICATE_ARN"],
    )
)

first_api = FirstAPI(app, "FirstAPI",
    env={
        "region": "us-east-1",
        "account": os.environ["CDK_DEFAULT_ACCOUNT"],
    },
    domain=domain_stack.domain,
)

second_api = SecondAPI(app, "SecondAPI",
    env={
        "region": "us-east-1",
        "account": os.environ["CDK_DEFAULT_ACCOUNT"],
    },
    domain=domain_stack.domain,
)

app.synth()
