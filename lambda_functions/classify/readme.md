# 使用指南

## 文件結構

- **dockerfile**: 包含用於構建 Docker 映像的指令碼。
- **local_test_inference.py**: 推理的 Python 腳本。
- **train_pics/**: 圖片的資料夾。

## 前置要求

在開始之前，請確保您已安裝以下軟體：

1. [Docker](https://www.docker.com/)（建議使用最新版本）
2. Python 3.9（可選，用於測試推理）

## 步驟

### 1. 構建 Docker 映像

打開終端機，導航到包含 **dockerfile** 的目錄，執行以下命令：

```bash
docker build -t your_image_name .
```

這將使用 Dockerfile 構建一個名為 `your_image_name` 的映像。

### 2. 上傳到 AWS ECR

前往 AWS console , create repostiry , 他會教你如何pull image上去
