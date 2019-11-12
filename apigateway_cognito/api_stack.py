from aws_cdk import (
    core,
    aws_lambda as _lambda,
    aws_dynamodb as ddb,
    aws_apigateway as apigw,
    aws_cognito as cognito
)

class ApigatewayCognitoStack(core.Stack):

    def __init__(self, scope: core.App, id: str, cognito_arn: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # create Cognito user pool
        user_pool = cognito.UserPool(
            self, "testUserPool",
            auto_verified_attributes=[cognito.UserPoolAttribute.EMAIL],
            sign_in_type=cognito.SignInType.EMAIL
        )
        cfn_user_pool = user_pool.node.default_child
        cfn_user_pool.policies = 

        # create REST API resource
        api = apigw.RestApi(self, 'my_API')

        # new resource - /test
        test_resource = api.root.add_resource('test')

        # Cognito authorizer
        cfn_authorizer = apigw.CfnAuthorizer(
            self, "my_cognito",
            name='API_authorizer',
            type='COGNITO_USER_POOLS',
            identity_source='method.request.header.Authorization',
            rest_api_id=api.rest_api_id,
            provider_arns=[cognito_arn]
        )

        # lambda handler
        hello_world_handler = _lambda.Function(
            self, 'my_handler',
            code=_lambda.AssetCode('lambda'),
            handler='index.handler',
            runtime=_lambda.Runtime.PYTHON_3_7
        )

        # attach GET method
        hello_world_integration = apigw.LambdaIntegration(hello_world_handler)
        meth = test_resource.add_method("GET", hello_world_integration,
            authorization_type=apigw.AuthorizationType.COGNITO
        )
        meth.node.find_child('Resource').add_property_override('AuthorizerId', cfn_authorizer.ref)