from aws_cdk import (
    Stack,
    aws_lambda as _lambda, # Import the Lambda module
    CfnOutput,
    aws_s3 as s3,
    RemovalPolicy,
    aws_apigateway as apigateway,
    aws_s3_deployment as s3deploy,
)
import os
import shutil

from constructs import Construct

class HelloCdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 第一個 Lambda 函數
        function_one = _lambda.Function(
            self, "FunctionOne",
            runtime=_lambda.Runtime.NODEJS_20_X,
            handler="index.handler",
            code=_lambda.Code.from_inline(
                """
                exports.handler = async function(event) {
                    return {
                        statusCode: 200,
                        headers: {
                            "Access-Control-Allow-Origin": "*", // 允許所有來源
                        },
                        body: JSON.stringify('Hello from /path1!'),
                    };
                };
                """
            ),
        )

        # 第二個 Lambda 函數
        function_two = _lambda.Function(
            self, "FunctionTwo",
            runtime=_lambda.Runtime.NODEJS_20_X,
            handler="index.handler",
            code=_lambda.Code.from_inline(
                """
                exports.handler = async function(event) {
                    return {
                    statusCode: 200,
                    headers: {
                            "Access-Control-Allow-Origin": "*", // 允許所有來源
                    },
                    body: JSON.stringify('Hello from /path2!'),
                    };
                };
                """
            ),
        )

        # 創建 API Gateway
        api = apigateway.RestApi(
            self, "MultiPathApi",
            rest_api_name="MultiPathApi",
            default_cors_preflight_options={
                "allow_origins": ["*"],  # 設置允許的來源，例如 ['https://example.com']
                "allow_methods": ["GET", "POST", "OPTIONS"],  # 設置允許的 HTTP 方法
                "allow_headers": ["Content-Type", "Authorization"],  # 允許的標頭
            },

            deploy_options=apigateway.StageOptions(
                stage_name="prod"
            )
        )

        # 添加第一個路徑 /path1
        path1 = api.root.add_resource("path1")
        path1_integration = apigateway.LambdaIntegration(function_one)
        path1.add_method("GET", path1_integration)  # 支援 GET 方法

        # 添加第二個路徑 /path2
        path2 = api.root.add_resource("path2")
        path2_integration = apigateway.LambdaIntegration(function_two)
        path2.add_method("GET", path2_integration)  # 支援 GET 方法

        website_bucket = s3.Bucket(self, "WebsiteBucket",
            website_index_document="index.html",
            public_read_access=True,
            block_public_access=s3.BlockPublicAccess(block_public_policy=False),
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects = True
        )

        s3deploy.BucketDeployment(
            self, 
            "DeployWebsiteContent",
            sources=[s3deploy.Source.asset("./website")],  # 資料夾路徑
            destination_bucket=website_bucket,  # 目標存儲桶
        )

        # Define a CloudFormation output for your URL
        CfnOutput(self, "ApiUrl", value=api.url)
        CfnOutput(self, "BucketName", value=website_bucket.bucket_name)
        