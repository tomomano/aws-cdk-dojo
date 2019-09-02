from aws_cdk import (
    core,
    aws_cloudfront as cfront,
    aws_route53 as route53,
    aws_route53_targets,
    aws_s3 as s3,
    aws_certificatemanager as acm
)
from dataclasses import dataclass

@dataclass
class StaticSiteProps:
    domain_name: str
    site_sub_domain: str
    certificate_arn: str

class StaticSite(core.Construct):

    def __init__(self, parent: core.Construct, name: str, props: StaticSiteProps) -> None:
        super().__init__(parent, name)

        site_domain = props.site_sub_domain + '.' + props.domain_name

        # Content bucket
        site_bucket = s3.Bucket(
            self, "SiteBucket",
            bucket_name=site_domain,
            website_index_document="index.html",
            website_error_document="error.html",
            public_read_access=True,
            removal_policy=core.RemovalPolicy.DESTROY
        )

        core.CfnOutput(self, 'Bucket', value=site_bucket.bucket_name)

        #cloudfront distribution that provies HTTPS
        distribution = cfront.CloudFrontWebDistribution(
            self, 'SiteDistribution',
            origin_configs=[
                cfront.SourceConfiguration(
                behaviors=[cfront.Behavior(is_default_behavior=True)],
                s3_origin_source=cfront.S3OriginConfig(s3_bucket_source=site_bucket)
                )
            ],
            alias_configuration=cfront.AliasConfiguration(
                acm_cert_ref=props.certificate_arn,
                names=[site_domain],
                ssl_method=cfront.SSLMethod.SNI,
                security_policy=cfront.SecurityPolicyProtocol.TLS_V1_1_2016
            )
        )

        core.CfnOutput(self, 'DistributionID', value=distribution.distribution_id)

        # Route 53 alias record for the CloudFront distribution
        zone = route53.HostedZone.from_lookup(
            self, 'MyHostedZone',
            domain_name=props.domain_name
        )

        # Add a A record to the hosted zone
        route53.ARecord(
            self, 'SiteAliasRecord',
            zone=zone,
            record_name=site_domain,
            target=route53.AddressRecordTarget.from_alias(
                aws_route53_targets.CloudFrontTarget(distribution)
            )
        )

