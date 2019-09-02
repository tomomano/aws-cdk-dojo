#!/usr/bin/env python3

import os
from aws_cdk import core
from static_site import StaticSite
from static_site import StaticSiteProps

"""
This stack relies on getting the domain name from CDK context.
Use 'cdk synth -c domain=mystaticsite.com -c subdomain=www'
Or add the following to cdk.json:
{
    "context": {
        "domain": "mystaticsite.com",
        "subdomain": "www",
        "certificate_arn": "arnABCXYZ"
    }
}
"""

class MyStaticSiteStack(core.Stack):

    def __init__(self, parent: core.App, name: str, **kwargs):
        super().__init__(parent, name, **kwargs)

        StaticSite(
            self, 'StaticSite',
            props=StaticSiteProps(
                domain_name=self.node.try_get_context('domain'),
                site_sub_domain=self.node.try_get_context('subdomain'),
                certificate_arn=self.node.try_get_context('certificate_arn')
            )
        )

app = core.App()
MyStaticSiteStack(
    app, "static-site", 
    env={
        "region": "us-east-1",
        "account": os.environ["CDK_DEFAULT_ACCOUNT"], 
    }
)

app.synth()
