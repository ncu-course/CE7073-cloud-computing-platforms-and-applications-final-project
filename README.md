# God Bless You

"God Bless You" is a project designed to blend traditional fortune-telling practices with modern technology, using artificial intelligence (AI) and cloud services to provide real-time facial analysis and fortune-telling advice. This innovative solution addresses common challenges faced in traditional practices, such as:

- Lack of instant responses
- Limited consultation time
- Unsatisfactory consultation quality

With "God Bless You," users can experience convenient, instant, and high-quality fortune-telling services.

## Features
- Real-time facial analysis
- AI-driven fortune-telling advice
- Cloud-based architecture for scalability and reliability

## Technology Stack
This project utilizes AWS services and is built entirely using Infrastructure as Code (IaC).

## Setup Instructions

### 1. Create a Virtual Environment
To start, create a Python virtual environment:
```bash
$ python3 -m venv .venv
```

### 2. Activate the Virtual Environment
Activate the virtual environment:
```bash
$ source .venv/bin/activate
```

### 3. Install Dependencies
Once the virtual environment is activated, install the required dependencies:
```bash
$ pip install -r requirements.txt
```

### 4. Synthesize the CloudFormation Template
Generate the CloudFormation template for deployment:
```bash
$ cdk synth
```

### 5. Deploy the Application
Deploy the application and save the outputs to a file:
```bash
$ cdk deploy --outputs-file outputs.json
```

### 6. Upload Required Files
Run the script to upload necessary files:
```bash
$ python3 upload_file.py
```

### 7. Clean Up Resources
To destroy all deployed resources:
```bash
$ cdk destroy
```

## Notes
- Ensure that AWS CLI is configured with the appropriate credentials and permissions before deploying.
- Review the `requirements.txt` file to verify all required Python libraries are listed.

With "God Bless You," traditional fortune-telling meets modern technology for a seamless and enriched user experience.
