from aws_cdk import (
    Stack,
    aws_lambda as _lambda, # Import the Lambda module
    CfnOutput,
    aws_iam as iam,  # Import IAM module
    aws_s3 as s3,
    RemovalPolicy,
    aws_apigateway as apigateway,
    aws_s3_deployment as s3deploy,
    Duration
)

from constructs import Construct

class HelloCdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        function_chat = _lambda.Function(
            self, "FunctionChat",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="lambda_chat.lambda_handler",
            code=_lambda.Code.from_asset("lambda_functions/chat"),
        )

        # 添加 Bedrock 訪問權限到 Lambda 函數角色
        function_chat.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonBedrockFullAccess")
        )

        function_image_generate = _lambda.Function(
            self, "FunctionImageGenerate",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="lambda_imaging.lambda_handler",
            code=_lambda.Code.from_asset("lambda_functions/image_generate"),
            timeout = Duration.seconds(30)

        )

        # 添加 Bedrock 訪問權限到 Lambda 函數角色
        function_image_generate.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonBedrockFullAccess")
        )


        function_classify = _lambda.DockerImageFunction(
            self, "FunctionClassify",
            code=_lambda.DockerImageCode.from_image_asset("lambda_functions/classify"),
            memory_size=1024,
            timeout = Duration.seconds(15)
        )

        # 創建 API Gateway
        api = apigateway.RestApi(
            self, "MultiPathApi",
            rest_api_name="MultiPathApi",
            default_cors_preflight_options={
                "allow_origins": ["*"],  # 設置允許的來源，例如 ['https://example.com']
                "allow_methods": ["*"],  # 設置允許的 HTTP 方法
                "allow_headers": ["*"],  # 允許的標頭
            },

            deploy_options=apigateway.StageOptions(
                stage_name="prod"
            )
        )

        path_chat = api.root.add_resource("chat")
        path_chat_integration = apigateway.LambdaIntegration(function_chat)
        path_chat.add_method("POST", path_chat_integration)

        path_image_generate = api.root.add_resource("image_generate")
        path_image_generate_integration = apigateway.LambdaIntegration(function_image_generate)
        path_image_generate.add_method("POST", path_image_generate_integration)

        path_classify = api.root.add_resource("classify")
        path_classify_integration = apigateway.LambdaIntegration(function_classify)
        path_classify.add_method("POST", path_classify_integration)

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
        