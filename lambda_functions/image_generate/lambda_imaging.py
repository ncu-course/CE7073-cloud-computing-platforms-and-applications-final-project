import botocore
import base64
import io
import json
import logging
import boto3
# from PIL import Image
from botocore.exceptions import ClientError


class ImageError(Exception):
    "Custom exception for errors returned by Amazon Titan Image Generator G1"

    def __init__(self, message):
        self.message = message


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Bedrock Runtime client used to invoke and question the models
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1'
)


def lambda_handler(event, context):
    print('botocore vertion: {0}'.format(botocore.__version__))
    print('boto3 vertion: {0}'.format(boto3.__version__))
    print("Event:", event)  # Debugging: 查看完整的事件結構

    # 獲取 HTTP 請求的 body
    body = event.get("body")
    print("Body:", body)
    if not body:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing request body"}),
            'headers': {
                "Access-Control-Allow-Origin": "*"
            }
        }

    # 解析 body 中的 JSON
    try:
        body_json = json.loads(body)  # 將字符串轉換為字典
    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid JSON format"}),
            'headers': {
                "Access-Control-Allow-Origin": "*"
            }
        }

    question = """
    The following is a conversation between a user and a chatbot about the user's fortune:

    """
    # question += """
    #
    # Bot: Welcome to the chat!
    # User: I would like to know my love fortune
    # Bot: Of course! I can tell your fortune, but I will need your birthdate, time, and location.
    # User: my birth day is 2003/11/30
    # I was born in Taiwan
    # """
    # 提取 question 字段
    question += body_json.get("question")
    # print("Question:", question)
    question += """

    Based on this conversation, generate a detailed description of an image that represents the user's fortune. 
    The description should be vivid, visually appealing, suitable for generating a creative image, and not longer than 512 characters. 
    Do not continue the conversation. Focus on creating an image description only.
    """
    print("Question:", question)

    # # lambda test 格式
    # question = event.get("question")
    # print("Question:", question)

    # 模型api請求範例
    # api = {
    #     "modelId": "amazon.titan-text-lite-v1",
    #     "contentType": "application/json",
    #     "accept": "application/json",
    #     "body": "{\"inputText\":\"Tell me about Paris.\",\"textGenerationConfig\":{\"maxTokenCount\":4096,\"stopSequences\":[],\"temperature\":0,\"topP\":1}}"
    # }

    # 定義模型 ID
    model_id = "amazon.titan-text-lite-v1"

    # 構建請求主體
    model_body = {
        "inputText": question,
        "textGenerationConfig": {
            "maxTokenCount": 90,
            "stopSequences": [],
            "temperature": 0.7,
            "topP": 1
        }
    }

    # 調用模型
    model_body_json = json.dumps(model_body)
    response = bedrock_runtime.invoke_model(
        body=model_body_json,
        contentType='application/json',
        accept='application/json',
        modelId=model_id
    )

    # 處理回應
    response_body = response["body"].read()  # 讀取流中的數據
    content_type = response["contentType"]  # 獲取返回數據的 MIME 類型
    # performance_latency = response["performanceConfigLatency"]  # 獲取性能設置

    # 解析返回的 JSON 數據
    image_prompt = ""
    if content_type == "application/json":
        result = json.loads(response_body)
        print("Generated Text:", result)
        image_prompt = result.get("results")[0].get("outputText")
        print("Image Prompt:", image_prompt)

    # 模型api請求範例
    # api = {
    # "modelId": "amazon.titan-image-generator-v2:0",
    # "contentType": "application/json",
    # "accept": "application/json",
    # "body": "{\"textToImageParams\":{\"text\":\"this is where you place your input text\"},\"taskType\":\"TEXT_IMAGE\",\"imageGenerationConfig\":{\"cfgScale\":8,\"seed\":42,\"quality\":\"standard\",\"width\":1024,\"height\":1024,\"numberOfImages\":3}}"
    # }

    # 定義模型 ID
    model_id = "amazon.titan-image-generator-v2:0"

    # 構建請求主體
    model_body = {
        "taskType": "TEXT_IMAGE",
        "textToImageParams": {
            "text": image_prompt,
            # "negativeText": "string"
        },
        "imageGenerationConfig": {
            "numberOfImages": 1,
            "height": 768,
            "width": 768,
            # "cfgScale": float,
            # "seed": int
        }
    }

    try:
        logger.info(
            "Generating image with Amazon Titan Image Generator G1 model %s", model_id)

        # 調用模型
        model_body_json = json.dumps(model_body)
        response = bedrock_runtime.invoke_model(
            body=model_body_json,
            contentType='application/json',
            accept='application/json',
            modelId=model_id
        )

        # 處理回應
        print("Response: ", response)
        response_body = json.loads(response.get("body").read())
        base64_image = response_body.get("images")[0]
        base64_bytes = base64_image.encode('ascii')
        image_bytes = base64.b64decode(base64_bytes)
        encoded_image_for_frontend = base64.b64encode(
            image_bytes).decode('utf-8')
        print("encoded_image_for_frontend: ", encoded_image_for_frontend)

        finish_reason = response_body.get("error")
        if finish_reason is not None:
            raise ImageError(
                f"Image generation error. Error is {finish_reason}")

        logger.info(
            "Successfully generated image with Amazon Titan Image Generator G1 model %s", model_id)

        # image = Image.open(io.BytesIO(image_bytes))
        # image.show()

        return {
            'statusCode': 200,
            'body': json.dumps({"image_base64": encoded_image_for_frontend}),
            'headers': {
                "Access-Control-Allow-Origin": "*"
            }
        }
    except ClientError as err:
        message = err.response["Error"]["Message"]
        logger.error("A client error occurred: %s", message)
        print("A client error occured: " + format(message))
    except ImageError as err:
        logger.error(err.message)
        print(err.message)
