import json
import boto3

def modify_outputs_file(input_file: str, output_file: str):
    """
    讀取 outputs.json，提取 ApiUrl 並保存到新文件
    """
    with open(input_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    # 提取 ApiUrl 並保存到新文件
    modified_data = {}
    for stack_name, outputs in data.items():
        if "ApiUrl" in outputs:  # 檢查 ApiUrl 是否存在
            modified_data["baseRoute"] = outputs["ApiUrl"]

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(modified_data, file, indent=4)

def get_bucket_name_from_outputs(input_file: str) -> str:
    """
    從 outputs.json 提取 BucketName
    """
    with open(input_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    for stack_name, outputs in data.items():
        if "BucketName" in outputs:  # 檢查 BucketName 是否存在
            return outputs["BucketName"]

    raise ValueError("BucketName not found in outputs.json")

def upload_to_s3(file_path: str, bucket_name: str, object_key: str):
    """
    將文件上傳到 S3
    """
    s3_client = boto3.client("s3")
    try:
        s3_client.upload_file(file_path, bucket_name, object_key)
        print(f"文件已成功上傳到 S3: s3://{bucket_name}/{object_key}")
    except Exception as e:
        print(f"上傳失敗: {e}")

# 文件路徑
input_file = "outputs.json"
output_file = "config.json"

# 提取 BucketName
s3_bucket = get_bucket_name_from_outputs(input_file)

# S3 Object Key
s3_object_key = "config.json"

# 執行改寫與上傳
modify_outputs_file(input_file, output_file)
upload_to_s3(output_file, s3_bucket, s3_object_key)
