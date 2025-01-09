# local_test_inference.py
import boto3
import cv2
import numpy as np
import json
import math
import base64
import os
from flask import Flask, request, jsonify

# Lambda Handler


def lambda_handler(event, context):
    body = event.get("body")
    body_json = json.loads(body)
    try:
        if body_json["path"] == "/ping":
            return {"statusCode": 200, "body": "Service is up and running!",     "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",  # 確保支持 CORS
            }
            }

        elif body_json["path"] == "/invocations":
            request_body = json.dumps(body_json["body"])
            input_image = input_fn(request_body)
            prediction = predict_fn(input_image, None)
            response = output_fn(prediction)
            return {"statusCode": 200, "body": json.dumps(response), 
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*",  # 確保支持 CORS
                    }
            }

        else:
            return {"statusCode": 404, "body": "Path not found",
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*",  # 確保支持 CORS
                    }
            }

    except Exception as e:
        return {"statusCode": 400, "body": json.dumps({"error": str(e)}),
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",  # 確保支持 CORS
                }
        }

# Model initialization


def model_fn(model_dir):
    global image_dir
    # Local directory for stored images
    image_dir = os.path.join(model_dir, "train_pics")
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    return None

# Process input request


def input_fn(request_body):
    request = json.loads(request_body)
    input_data = request.get("input_data")
    if "base64_image" in input_data:
        return decode_base64_image(input_data["base64_image"])
    elif "s3_bucket" in input_data and "s3_key" in input_data:
        return read_image_from_s3(input_data["s3_bucket"], input_data["s3_key"])
    else:
        raise ValueError("Missing required fields in input data")

# Should not be used
# Load image from S3


def read_image_from_s3(bucket_name, s3_key):
    s3 = boto3.client("s3")
    response = s3.get_object(Bucket=bucket_name, Key=s3_key)
    image_data = response['Body'].read()
    return cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)

# Decode Base64 image


def decode_base64_image(base64_str):
    image_data = base64.b64decode(base64_str)
    return cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)

# Incode Base64 image


def incode_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        base64_string = base64.b64encode(image_file.read()).decode('utf-8')
    return base64_string

# Extract image features


def extract_features(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    sift = cv2.SIFT_create()
    _, descriptors = sift.detectAndCompute(gray, None)
    return [list(desc) for desc in descriptors] if descriptors is not None else []

# Calculate average distance


def average_distance(descriptors1, descriptors2):
    min_len = min(len(descriptors1), len(descriptors2))
    return sum(
        math.sqrt(sum((a - b) ** 2 for a,
                  b in zip(descriptors1[i], descriptors2[i])))
        for i in range(min_len)
    ) / min_len

# Inference logic


def predict_fn(input_image, model):
    input_features = extract_features(input_image)
    if not input_features:
        raise ValueError("Cannot extract features from input image")

    min_distance = float("inf")
    most_similar_image = None

    for image_file in os.listdir(image_dir):
        image_path = os.path.join(image_dir, image_file)
        image = cv2.imread(image_path)
        if image is None:
            continue
        features = extract_features(image)
        if not features:
            continue
        distance = average_distance(input_features, features)
        if distance < min_distance:
            min_distance = distance
            most_similar_image = image_file
    result = {
        "most_similar_image": incode_base64_image(os.path.join(image_dir, most_similar_image)),
        "type": 0 if 'b.jpg' in str(most_similar_image) or 'b.png' in str(most_similar_image) or 'b.jpeg' in str(most_similar_image) else 1
    }
    return result

# Format output


def output_fn(prediction):
    return prediction

# Initialize model


def initialize():
    model_fn("/var/task/")


initialize()
