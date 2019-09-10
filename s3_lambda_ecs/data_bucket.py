from aws_cdk import (
    core,
    aws_s3 as s3,
)

class DataBucket(core.Construct):
    """
    this construct defines a simple S3 bucket, to store movie data and their thumbnails.
    By connecting this bucket with lambda stack, lambda will invoke functions to handle uploaded data
    """

    @property
    def data_bucket(self):
        return self._data_bucket

    def __init__(self, parent: core.Construct, name: str) -> None:
        super().__init__(parent, name)

        bucket = s3.Bucket(
            self, "S3Bucket",
            public_read_access=True,
            removal_policy=core.RemovalPolicy.DESTROY
        )

        # output generated bucket name
        core.CfnOutput(self, 'Bucket', value=bucket.bucket_name)

        self._data_bucket = bucket