import os
from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    CfnOutput,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    aws_logs as logs,
)
from constructs import Construct


class ChatbotStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # DynamoDB table for chat history with encryption
        chat_table = dynamodb.Table(
            self,
            "ChatHistory",
            partition_key=dynamodb.Attribute(
                name="sessionId", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="timestamp", type=dynamodb.AttributeType.NUMBER
            ),
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            point_in_time_recovery=True,
            removal_policy=RemovalPolicy.RETAIN,
            time_to_live_attribute="ttl",
        )

        # DynamoDB table for users
        users_table = dynamodb.Table(
            self,
            "Users",
            partition_key=dynamodb.Attribute(
                name="username", type=dynamodb.AttributeType.STRING
            ),
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            point_in_time_recovery=True,
            removal_policy=RemovalPolicy.RETAIN,
        )

        # DynamoDB table for chat summaries
        summaries_table = dynamodb.Table(
            self,
            "ChatSummaries",
            partition_key=dynamodb.Attribute(
                name="username", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="sessionId", type=dynamodb.AttributeType.STRING
            ),
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            point_in_time_recovery=True,
            removal_policy=RemovalPolicy.RETAIN,
            time_to_live_attribute="ttl",
        )

        # Lambda layer for dependencies
        lambda_layer = lambda_.LayerVersion(
            self,
            "ChatDependencies",
            code=lambda_.Code.from_asset("lambda/layer"),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_11],
            description="Dependencies for chat handler",
        )

        # Lambda function for chat handling
        chat_handler = lambda_.Function(
            self,
            "ChatHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="index.handler",
            code=lambda_.Code.from_asset("lambda/chat"),
            timeout=Duration.seconds(30),
            memory_size=512,
            layers=[lambda_layer],
            environment={
                "CHAT_TABLE_NAME": chat_table.table_name,
                "USERS_TABLE_NAME": users_table.table_name,
                "SUMMARIES_TABLE_NAME": summaries_table.table_name,
                "LLM_PROVIDER": os.getenv("LLM_PROVIDER", "bedrock"),
                "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
                "DATA_RETENTION_DAYS": os.getenv("DATA_RETENTION_DAYS", "30"),
                "SYSTEM_PROMPT": os.getenv(
                    "SYSTEM_PROMPT", "You are a helpful AI assistant."
                ),
            },
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        # Grant DynamoDB permissions
        chat_table.grant_read_write_data(chat_handler)
        users_table.grant_read_write_data(chat_handler)
        summaries_table.grant_read_write_data(chat_handler)

        # Grant Bedrock permissions if using Bedrock
        if os.getenv("LLM_PROVIDER", "bedrock") == "bedrock":
            chat_handler.add_to_role_policy(
                iam.PolicyStatement(
                    actions=["bedrock:InvokeModel"],
                    resources=["*"],
                )
            )

        # API Gateway with API key authentication
        api = apigateway.RestApi(
            self,
            "ChatbotApi",
            rest_api_name="Privacy Chatbot API",
            description="Privacy-focused chatbot API",
            deploy_options=apigateway.StageOptions(
                stage_name="prod",
                logging_level=apigateway.MethodLoggingLevel.ERROR,
                data_trace_enabled=False,  # Don't log request/response bodies
            ),
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
            ),
        )

        # API Key
        api_key = api.add_api_key("ChatbotApiKey", api_key_name="chatbot-api-key")

        usage_plan = api.add_usage_plan(
            "ChatbotUsagePlan",
            name="Standard",
            throttle=apigateway.ThrottleSettings(rate_limit=10, burst_limit=20),
        )

        usage_plan.add_api_key(api_key)
        usage_plan.add_api_stage(stage=api.deployment_stage)

        # API endpoints
        auth = api.root.add_resource("auth")
        register = auth.add_resource("register")
        login = auth.add_resource("login")
        
        chat = api.root.add_resource("chat")
        summaries = api.root.add_resource("summaries")
        
        # Auth endpoints
        register.add_method(
            "POST",
            apigateway.LambdaIntegration(chat_handler),
            api_key_required=True,
        )
        
        login.add_method(
            "POST",
            apigateway.LambdaIntegration(chat_handler),
            api_key_required=True,
        )
        
        # Chat endpoint
        chat.add_method(
            "POST",
            apigateway.LambdaIntegration(chat_handler),
            api_key_required=True,
        )
        
        # Summaries endpoint
        summaries.add_method(
            "GET",
            apigateway.LambdaIntegration(chat_handler),
            api_key_required=True,
        )

        # Outputs
        CfnOutput(
            self,
            "ApiUrl",
            value=api.url,
            description="API Gateway URL",
        )

        CfnOutput(
            self,
            "ApiKeyId",
            value=api_key.key_id,
            description="API Key ID (retrieve value from AWS Console)",
        )
