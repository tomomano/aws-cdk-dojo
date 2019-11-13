from aws_cdk import (
    core,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_cognito as cognito
)
import random, string

class ApigatewayCognitoStack(core.Stack):

    def __init__(self, scope: core.App, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # create Cognito user pool
        user_pool = cognito.UserPool(
            self, "testUserPool",
            auto_verified_attributes=[cognito.UserPoolAttribute.EMAIL],
            sign_in_type=cognito.SignInType.EMAIL
        )
        cfn_user_pool = user_pool.node.default_child
        cfn_user_pool.policies = {
            "passwordPolicy": {
                "minimumLength": 8,
                "requireLowercase": True,
                "requireNumbers": True,
                "requireUppercase": True,
                "requireSymbols": False
            }
        }

        # attach a domain
        # random.seed(20191113)
        # random_domain = ''.join(random.choice(string.ascii_lowercase) for i in range(20))
        # cfn_user_pool_domain = cognito.CfnUserPoolDomain(
        #     self, "testUserPoolDomain",
        #     domain=random_domain,
        #     user_pool_id=user_pool.user_pool_id
        # )

        # create pool client
        pool_client = cognito.CfnUserPoolClient(
            self, 'testUserPoolClient',
            user_pool_id=user_pool.user_pool_id,
            supported_identity_providers=["COGNITO"],
            generate_secret=False,
            refresh_token_validity=1,
            explicit_auth_flows=["USER_PASSWORD_AUTH"],
            allowed_o_auth_flows_user_pool_client=True,
            allowed_o_auth_flows=["implicit"],
            allowed_o_auth_scopes=["email", "openid", "aws.cognito.signin.user.admin"],
            callback_ur_ls=["http://localhost"],
            logout_ur_ls=["http://localhost"]
        )
        # output some stuff
        core.CfnOutput(self, "User Pool ID", value=user_pool.user_pool_id)
        core.CfnOutput(self, "Pool Client ID", value=pool_client.ref)
        # core.CfnOutput(self, "User pool domain", value=cfn_user_pool_domain.domain)

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
            provider_arns=[user_pool.user_pool_arn]
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