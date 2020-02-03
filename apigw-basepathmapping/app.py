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
class StackProps:
    domain_name: str
    certificate_arn: str

class FirstStack(core.Stack):

    def __init__(self, scope: core.App, id: str, props: StackProps, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        api1 = apigw.RestApi(self, 'api1')
        api2 = apigw.RestApi(self, 'api2')
        domain = apigw.DomainName(
            self, "domain",
            domain_name=props.domain_name,
            certificate=acm.Certificate.from_certificate_arn(
                self, 'cert', props.certificate_arn
            ),
            endpoint_type=apigw.EndpointType.REGIONAL,
        )
        domain.add_base_path_mapping(api1, base_path="api1")
        domain.add_base_path_mapping(api2, base_path="api2")

        route53.ARecord(
            self, "AliasRecord",
            zone=route53.HostedZone.from_lookup(
                self, 'zone', domain_name=props.domain_name
            ),
            target=route53.RecordTarget.from_alias(
                route53_targets.ApiGatewayDomain(domain)
            )
        )

        # handler for random request
        hello_handler = _lambda.Function(
            self, 'LambdaHandler',
            runtime=_lambda.Runtime.PYTHON_3_7,
            handler="hello.handler",
            code=_lambda.Code.from_asset('lambda'),
        )
        api1.root.add_method("GET", apigw.LambdaIntegration(hello_handler))
        api2.root.add_method("GET", apigw.LambdaIntegration(hello_handler))

app = core.App()
FirstStack(
    app, "FirstStack",
    env={
        "region": "us-east-1",
        "account": os.environ["CDK_DEFAULT_ACCOUNT"], 
    },
    props=StackProps(
        domain_name=os.environ["DOMAIN_NAME"],
        certificate_arn=os.environ["CERTIFICATE_ARN"],
    )
)
app.synth()
