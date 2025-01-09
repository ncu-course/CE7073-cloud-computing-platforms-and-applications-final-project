import json
import botocore
import boto3

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

    # 提取 question 字段
    question = "Bot: I'm a renowned Chinese feng shui master known as 'Xuan Dao Ju Shi,' well-versed in the art of geomancy, the principles of Yin-Yang and the Five Elements, as well as the teachings of the I Ching. Additionally, I am skilled in physiognomy, capable of discerning a person's fate and fortunes through the study of facial features and complexion. My mission is to help people adjust their energy fields, identify the most auspicious places for living and business, and bring harmony and prosperity to their lives. My reputation precedes me, making me a highly respected master known throughout the region.\n"
    question += body_json.get("question")
    print("Question:", question)

    # lambda test 格式
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
    model_id = "amazon.titan-text-express-v1"

    # 構建請求主體
    model_body = {
        "inputText": question,
        "textGenerationConfig": {
            "maxTokenCount": 300,
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
    if content_type == "application/json":
        result = json.loads(response_body)
        print("Generated Text:", result)
        output_text = result.get("results")[0].get("outputText")
        print("Output Text:", output_text)

        return {
            'statusCode': 200,
            'body': json.dumps({"Answer": output_text}),
            'headers': {
                "Access-Control-Allow-Origin": "*"
            }
        }
    else:
        print("Unsupported content type:", content_type)
