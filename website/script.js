// Photo Upload Logic
let baseRoute = ""; // 初始化 baseRoute
// 從 config.json 讀取 baseRoute
fetch("config.json")
  .then((response) => {
    if (!response.ok) {
      throw new Error("無法加載 config.json");
    }
    return response.json();
  })
  .then((config) => {
    baseRoute = config.baseRoute; // 假設 JSON 文件中有 baseRoute 字段
    if (!baseRoute) {
      throw new Error("config.json 中缺少 baseRoute");
    }
  })
  .catch((error) => {
    document.getElementById("result").innerText =
      "配置加載失敗: " + error.message;
  });

const photoInput = document.getElementById("photoInput");
const imageOutput = document.getElementById("imageOutput");
const imageclassifyOutput = document.getElementById("imageclassifyOutput");
const textOutput = document.getElementById("textOutput");
const fortuneImage = document.getElementById("fortuneImage");

function displayImage(imagePath) {
  imageclassifyOutput.innerHTML = `<img src="${imagePath}" alt="Specified Local Photo">`;
}

function displayClassficationImage(base64Image) {
  const imageclassifyOutput = document.getElementById("imageclassifyOutput");
  const imgElement = document.createElement("img");
  imgElement.src = `data:image/png;base64,${base64Image}`;
  imgElement.alt = "Classfication Image";
  imgElement.style.maxWidth = "100%";
  imgElement.style.maxHeight = "100%";
  imageclassifyOutput.innerHTML = ""; // 清空之前的內容
  imageclassifyOutput.appendChild(imgElement);
}

function displayClassficationMessage(message) {
  // 創建文字元素
  const textElement = document.createElement("p");
  textElement.textContent = message;

  // 將文字元素添加到 imageclassifyOutput
  const imageclassifyOutput = document.getElementById("imageclassifyOutput");
  imageclassifyOutput.appendChild(textElement);
}

photoInput.addEventListener("change", (event) => {

  const apiUrl = `${baseRoute}classify`; // 拼接完整路徑
  const file = event.target.files[0];
  if (file) {
    console.log("Selected File:", file);
    const reader = new FileReader();
    reader.onload = function (e) {
      console.log("FileReader onload triggered"); // 檢查 FileReader 是否成功讀取
      const base64String = e.target.result.split(",")[1]; // 提取 Base64 字串部分
      console.log("Base64 Encoded String:", base64String); // 檢查 Base64 字串

      // !觸發lambda function，將圖片傳給sagemaker
      fetch(apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          path: "/invocations",
          body: {
            input_data: {
              base64_image: base64String,
            },
          },
        }),
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          return response.json(); // 解析返回的 JSON
        })
        .then((data) => {
          console.log("Lambda Response:", data);
          if (data.most_similar_image) {
            // !顯示圖片
            console.log("Most Similar Image:", data.most_similar_image);
            displayClassficationImage(data.most_similar_image);
          }
          if (data.type) {
            // !顯示分類結果
            console.log("Image Type:", data.type);
            if (data.type == "1") {
              //displayClassficationMessage("You are a good person!");
              displayBotMessage(
                "Here is your physiognomy classification result: You are a good person!"
              );
            } else {
              //displayClassficationMessage("You are a bad person!");
              displayBotMessage(
                "Here is your physiognomy classification result: You are a bad person!"
              );
            }
            // displayClassficationMessage(`Image Type: ${data.type}`);

            chatWidget.style.display = "flex";
            openChatButton.style.display = "none";
          }
        })
        .catch((error) => {
          console.error("Error calling Lambda:", error);
        });
      // !等待sagemaker回傳True/False結果
    };
    reader.readAsDataURL(file);

    // setTimeout(() => {
    //     displayClassficationMessage("Your fortune analysis result: You have a bright future!");
    // }, 2000);
  }
});

// Chat Widget Logic
const chatWidget = document.getElementById("chatWidget");
const openChatButton = document.getElementById("openChat");
const closeChatButton = document.getElementById("closeChat");
const chatInput = document.getElementById("chatInput");
const sendButton = document.getElementById("sendButton");
const chatBody = document.getElementById("chatBody");

// Open chat widget
openChatButton.addEventListener("click", () => {
  chatWidget.style.display = "flex";
  openChatButton.style.display = "none";
});

// Close chat widget
closeChatButton.addEventListener("click", () => {
  chatWidget.style.display = "none";
  openChatButton.style.display = "block";
});

function displayUserMessage(userMessage) {
  const userMessageElement = document.createElement("p");
  userMessageElement.classList.add("user-message"); // 使用者訊息樣式
  userMessageElement.textContent = `User: ${userMessage}`;
  chatBody.appendChild(userMessageElement);

  // 確保滾動條始終位於底部
  chatBody.scrollTop = chatBody.scrollHeight;
}

function displayBotMessage(botMessage) {
  console.log("Bot Message:", botMessage);
  botMessage = botMessage.replace("\nBot: ", ""); // 移除換行符
  const botMessageElement = document.createElement("p");
  botMessageElement.classList.add("bot-message"); // 機器人訊息樣式
  botMessageElement.textContent = `Bot: ${botMessage}`;
  chatBody.appendChild(botMessageElement);

  // 確保滾動條始終位於底部
  chatBody.scrollTop = chatBody.scrollHeight;
}

// 函數來擷取所有的聊天紀錄
function getChatHistory() {
  const messages = chatBody.querySelectorAll("p"); // 選取所有的 <p> 元素
  const chatHistory = [];
  messages.forEach((message) => {
    chatHistory.push(message.textContent); // 將每個訊息的文本內容添加到陣列中
  });
  return chatHistory.join("\n"); // 將陣列轉換為字串，並使用換行符分隔
}

// Send chat message
sendButton.addEventListener("click", () => {
  const apiUrl = `${baseRoute}chat`; // 拼接完整路徑

  const userMessage = chatInput.value.trim();
  console.log("User Message:", userMessage);
  if (userMessage) {
    // 使用者訊息
    displayUserMessage(userMessage);
    chatInput.value = "";

    const chat_history = getChatHistory();
    console.log("Chat History:\n", chat_history);

    // !串接Bedrock LLM模型
    fetch(apiUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json", // 必須設置 Content-Type 為 application/json
      },
      body: JSON.stringify({
        question: chat_history, // 將使用者問題封裝為 JSON 格式
      }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json(); // 解析返回的 JSON
      })
      .then((data) => {
        console.log("Lambda Response:", data);
        const answer = data.Answer; // 從回應中提取 Answer
        displayBotMessage(answer); // 顯示回應
      })
      .catch((error) => {
        console.error("Error calling Lambda:", error);
        displayBotMessage("An error occurred while processing your request.");
      });
  }
});

chatInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault(); // 防止預設的 Enter 行為（如換行）
    const userMessage = chatInput.value.trim();
    console.log("User Message:", userMessage);

    if (userMessage) {
      // 使用者訊息
      displayUserMessage(userMessage);
      chatInput.value = "";

      const chat_history = getChatHistory();
      console.log("Chat History:\n", chat_history);

      // !串接Bedrock LLM模型
      const apiUrl = `${baseRoute}chat`; // 拼接完整路徑

      fetch(apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json", // 必須設置 Content-Type 為 application/json
        },
        body: JSON.stringify({
          question: chat_history, // 將使用者問題封裝為 JSON 格式
        }),
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          return response.json(); // 解析返回的 JSON
        })
        .then((data) => {
          console.log("Lambda Response:", data);
          const answer = data.Answer; // 從回應中提取 Answer
          displayBotMessage(answer); // 顯示回應
        })
        .catch((error) => {
          console.error("Error calling Lambda:", error);
          displayBotMessage("An error occurred while processing your request.");
        });
    }
  }
});

// 函數來擷取所有的聊天紀錄
function getChatHistory2() {
  const messages = chatBody.querySelectorAll("p"); // 選取所有的 <p> 元素
  const chatHistory = [];
  messages.forEach((message) => {
    let msg = message.textContent;
    msg = msg.replace("User: ", ""); // 移除使用者訊息前綴
    msg = msg.replace("Bot: ", ""); // 移除機器人訊息前綴
    chatHistory.push(msg); // 將每個訊息的文本內容添加到陣列中
  });
  return chatHistory.join("\n"); // 將陣列轉換為字串，並使用換行符分隔
}

// Logic to display a specific local image in imageOutput
function displayFortuneImage(base64Image) {
  const imageOutput = document.getElementById("imageOutput");
  const imgElement = document.createElement("img");
  imgElement.src = `data:image/png;base64,${base64Image}`;
  imgElement.alt = "Fortune Image";
  imgElement.style.maxWidth = "100%";
  imgElement.style.maxHeight = "100%";
  imageOutput.innerHTML = ""; // 清空之前的內容
  imageOutput.appendChild(imgElement);
}

fortuneImage.addEventListener("click", () => {
  // 測試擷取聊天紀錄
  const chat_history = getChatHistory();
  console.log("Chat History:\n", chat_history);

  // !將聊天紀錄作為輸入觸發lambda呼叫bedrock LLM模型
  const apiUrl = `${baseRoute}image_generate`; // 拼接完整路徑

  fetch(apiUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question: chat_history,
    }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json(); // 解析返回的 JSON
    })
    .then((data) => {
      console.log("Lambda Response:", data);
      // console.log("Image Base64:", data.image_base64);
      if (data.image_base64) {
        // 顯示圖片
        displayFortuneImage(data.image_base64);
      } else {
        console.error("Image processing failed:", data.message);
      }
    })
    .catch((error) => {
      console.error("Error calling Lambda:", error);
    });
});
