# Dockerfile
# Ideal Dockerfile for AWS Lambda with Python 3.10

FROM public.ecr.aws/lambda/python:3.10

# Set working directory
WORKDIR /var/task

# Copy necessary files
COPY local_test_inference.py ./
COPY requirements.txt ./
COPY train_pics /var/task/train_pics

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Define Lambda's entry point
CMD ["local_test_inference.lambda_handler"]
