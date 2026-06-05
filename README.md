# Cosmos3-Super-Text2Image AI 圖像生成系統 (HW3)

本專案是一個集成了 **React 獨立網頁應用 (HTML5)**、**Streamlit Python 互動平台** 以及 **Android 行動應用程式 (APK)** 的三合一文字生圖（Text-to-Image）展示系統。

## 🌟 核心功能特色
1. **🌐 React 網頁版 (HTML)**：嵌入以 React + Tailwind CSS 打造的高質感 UI 介面，內建多種生成風格、畫布比例，以及專屬的 **「AI 影像後製微調面板」**（可調整亮度、對比、飽和度與模糊度）。
2. **🐍 Streamlit 內建版 (Python)**：支援透過 API 金鑰連線 Hugging Face `nvidia/Cosmos3-Super-Text2Image` 實體生圖，亦具備高耐用性的 Demo 模擬生圖模式。
3. **📱 Android APK 下載**：提供透過 WebIntoApp 打包的 `.apk` 行動端安裝檔，可於 Android 裝置上下載並直接安裝。

---

## 📂 專案結構
```text
├── index.html                   # React 互動網頁版主程式
├── streamlit.py                 # Streamlit 多功能整合平台 (主入口)
├── requirements.txt             # Python 依賴清單 (Streamlit Cloud 自動偵測)
├── .gitignore                   # 排除大型檔案之 git 設定
└── jameswangAPP 1.0/            # 行動端封裝資源目錄
    ├── android/
    │   └── app-release.apk      # 已建置完成的 Android APK 檔
    └── readme.txt               # WebIntoApp 打包資訊說明檔
```

---

## 🛠️ 本地執行方式

### 1. 安裝 Python 依賴環境
請確保本機已安裝 Python 3.8+，並在終端機中執行：
```bash
pip install -r requirements.txt
```

### 2. 啟動 Streamlit 本地伺服器
```bash
streamlit run streamlit.py
```
啟動後會自動開啟瀏覽器頁面 `http://localhost:8501`。

---

## 🚀 部署至 Streamlit Community Cloud

您可以直接將此 Git 專案庫推送到 GitHub，並在 Streamlit Cloud 上免費託管：

1. 登入 [Streamlit Community Cloud](https://share.streamlit.io/)。
2. 點選 **"Create app"**。
3. 選擇您在 GitHub 上的本專案 Repository (`machinejameswang/APP`)、Branch 選擇 `maim` (或您當前的分支)，主入口檔案 (Main file path) 輸入 `streamlit.py`。
4. 點選 **"Deploy!"** 即可上線。

### 🔑 配置 Hugging Face API Token (選填)
若希望使用真實的 Cosmos3 進行圖像生成：
- 在 Streamlit Cloud 應用管理後台，進入 **Settings -> Secrets**。
- 加入以下環境變數金鑰設定：
  ```toml
  HF_TOKEN = "您的_Hugging_Face_API_Token"
  ```
- 系統將會自動且安全地載入金鑰進行 API 生成。
