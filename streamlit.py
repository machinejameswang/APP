import streamlit as st
import requests
import io
import random
import time
from PIL import Image
import os
import streamlit.components.v1 as components

# -----------------------------------------------------------------------------
# 1. 頁面基本設定 (支援手機與桌機 RWD)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Cosmos3-Super-Text2Image 生成器",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自訂 CSS 讓介面更具科技感與美觀
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #A78BFA, #818CF8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .sub-title {
        font-size: 1rem;
        color: #9CA3AF;
        margin-bottom: 1.5rem;
    }
    .footer {
        text-align: center;
        margin-top: 3rem;
        color: #6B7280;
        font-size: 0.8rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #1e1e24;
        border-radius: 8px 8px 0px 0px;
        gap: 8px;
        padding-top: 10px;
        padding-bottom: 10px;
        padding-left: 20px;
        padding-right: 20px;
        color: #c9d1d9;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        background-color: #312e81 !important;
        border-bottom: 2px solid #818cf8 !important;
        color: #ffffff !important;
    }
</style>
""", unsafe_style_with_html=True)

# -----------------------------------------------------------------------------
# 2. 側邊欄設定：API 金鑰與模型資訊
# -----------------------------------------------------------------------------
st.sidebar.title("🛠️ 設定與憑證")

# 安全讀取 API Key (優先從 Streamlit Secrets 讀取，若無則提供網頁輸入欄位)
hf_token = st.secrets.get("HF_TOKEN", "")

if not hf_token:
    st.sidebar.warning("⚠️ 未偵測到系統環境變數 HF_TOKEN")
    hf_token = st.sidebar.text_input(
        "請輸入您的 Hugging Face API Token",
        type="password",
        help="請至 Hugging Face -> Settings -> Tokens 申請一個具有 Read 權限的 Token"
    )
else:
    st.sidebar.success("🔑 已從 Secrets 安全載入 HF_TOKEN")

st.sidebar.markdown("---")
st.sidebar.subheader("🤖 模型資訊")
st.sidebar.info(
    "**模型名稱**:\n`nvidia/Cosmos3-Super-Text2Image`\n\n"
    "**模型類型**:\nNVIDIA Cosmos 64B 物理 AI 圖像生成專門模型。"
)

# -----------------------------------------------------------------------------
# 3. 主頁面標題與作業資訊
# -----------------------------------------------------------------------------
st.markdown("<div class='main-title'>🎨 Cosmos3-Super-Text2Image 圖像生成器</div>", unsafe_style_with_html=True)
st.markdown("<div class='sub-title'>使用 Streamlit + Hugging Face 打造的 AI 圖像生成系統</div>", unsafe_style_with_html=True)

# 作業基本資訊欄
with st.expander("📝 HW3 作業連結與說明 (點擊展開)", expanded=True):
    st.markdown("""
    * **作業目標**：使用 Gemini Canvas 輔助建立 Cosmos3-Super-Text2Image 文字生圖 App
    * **GitHub 專案庫**：[https://github.com/machinejameswang/APP/](https://github.com/machinejameswang/APP/)
    * **Streamlit 線上展示**：[https://your-app-name.streamlit.app](https://your-app-name.streamlit.app) *(請於部署後手動更新此網址)*
    """)

# -----------------------------------------------------------------------------
# 4. 創建分頁 (Tabbed Layout)
# -----------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["🌐 React 網頁版 (HTML)", "🐍 Streamlit 內建版 (Python)", "📱 Android APK 下載"])

# ---- Tab 1: React 網頁版 ----
with tab1:
    st.markdown("### 🌐 React 網頁版即時體驗")
    st.caption("以下區域直接嵌入並運行了 React+Tailwind CSS 設計的 `index.html`，具備流暢動畫與影像後製微調面板。")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(script_dir, "index.html")
    
    if os.path.exists(html_path):
        try:
            with open(html_path, "r", encoding="utf-8") as f:
                html_code = f.read()
            # 渲染 HTML，高度設為 950px 以適配大部分內容，並開啟捲軸
            components.html(html_code, height=950, scrolling=True)
        except Exception as e:
            st.error(f"讀取 index.html 失敗: {str(e)}")
    else:
        st.error("找不到 index.html 檔案，請確認檔案已放置於專案根目錄。")

# ---- Tab 2: Streamlit 內建版 ----
with tab2:
    st.markdown("### 🐍 Streamlit 內建 Python 生成器")
    st.caption("此分頁使用 Python API 連線 Hugging Face Inference API 進行即時生圖。若無 Token 則可使用 Unsplash 模擬體驗模式。")
    
    # 使用者輸入區
    prompt = st.text_area(
        "✍️ 請輸入英文圖像提示詞 (Prompt)",
        value="A stunning glass tower floating above Taipei mist, neon reflection, botanical gardens on balconies, photorealistic 8k",
        placeholder="描述您腦海中的畫面...",
        height=100,
        key="streamlit_prompt"
    )
    
    # 進階參數控制區
    st.markdown("### ⚙️ 進階生成參數")
    col1, col2 = st.columns(2)
    
    with col1:
        image_style = st.selectbox(
            "🎨 圖像風格 (Image Style)",
            [
                "🌌 Cyberpunk (賽博朋克)", 
                "📸 Photorealistic (寫實攝影)", 
                "🎎 Anime Art (日系動漫)", 
                "🧙 Fantasy Art (奇幻插畫)", 
                "🎨 Oil Painting (古典油畫)", 
                "無特定風格"
            ],
            key="streamlit_style"
        )
        aspect_ratio = st.selectbox(
            "📐 畫布長寬比 (Aspect Ratio)",
            ["1:1 (正方形)", "16:9 (寬螢幕)", "9:16 (手機直式)", "4:3 (標準)"],
            key="streamlit_ratio"
        )
    
    with col2:
        negative_prompt = st.text_input(
            "🚫 排除事物 (Negative Prompt)",
            value="blurry, low quality, distorted, extra limbs, bad anatomy",
            key="streamlit_negative"
        )
        
        # 種子碼 (Seed) 設定
        use_random_seed = st.checkbox("隨機種子碼 (Random Seed)", value=True, key="streamlit_random_seed")
        if use_random_seed:
            seed = random.randint(1, 99999999)
            st.number_input("種子碼 (Seed)", value=seed, disabled=True, key="streamlit_seed_disabled")
        else:
            seed = st.number_input("種子碼 (Seed)", min_value=1, max_value=99999999, value=123456, key="streamlit_seed")
    
    API_URL = "https://api-inference.huggingface.co/models/nvidia/Cosmos3-Super-Text2Image"
    
    if st.button("🚀 開始生成圖像 (Generate)", type="primary", use_container_width=True, key="streamlit_generate_btn"):
        if not prompt.strip():
            st.error("⚠️ 請輸入圖像提示詞 (Prompt) 後再進行生成！")
        else:
            # 根據風格優化 Prompt
            style_prompts = {
                "🌌 Cyberpunk (賽博朋克)": "cyberpunk, neon, futuristic city",
                "📸 Photorealistic (寫實攝影)": "photorealistic, cinematic portrait, highly detailed",
                "🎎 Anime Art (日系動漫)": "anime illustration, vibrant color palette, masterpiece",
                "🧙 Fantasy Art (奇幻插畫)": "gorgeous digital concept art, fantasy landscape",
                "🎨 Oil Painting (古典油畫)": "textured oil painting, brush strokes, museum grade art",
                "無特定風格": ""
            }
            
            style_suffix = style_prompts.get(image_style, "")
            final_prompt = f"{prompt}, {style_suffix}" if style_suffix else prompt
            
            # 解析長寬比對應尺寸
            width, height = 1024, 1024
            if aspect_ratio == "16:9 (寬螢幕)":
                width, height = 1216, 688
            elif aspect_ratio == "9:16 (手機直式)":
                width, height = 688, 1216
            elif aspect_ratio == "4:3 (標準)":
                width, height = 1024, 768
    
            # 建立請求 payload
            payload = {
                "inputs": final_prompt,
                "parameters": {
                    "negative_prompt": negative_prompt,
                    "seed": seed,
                    "width": width,
                    "height": height
                }
            }
    
            # 呼叫 API 流程
            st.info("⏳ 正在向 Hugging Face 傳送生成請求...")
            progress_bar = st.progress(10)
    
            api_success = False
            image_result = None
    
            if not hf_token.strip():
                # 無 Token 自動切換至 Demo 模式
                progress_bar.progress(50)
                st.warning("💡 您未輸入 Hugging Face Token，系統將自動啟動 **「Demo 模擬體驗模式」**。")
                time.sleep(1)
            else:
                try:
                    headers = {"Authorization": f"Bearer {hf_token}"}
                    response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
                    progress_bar.progress(80)
    
                    if response.status_code == 200:
                        image_result = Image.open(io.BytesIO(response.content))
                        api_success = True
                    elif response.status_code == 503:
                        st.warning("⏳ HF 伺服器正在載入此 64B 模型 (503)。系統已自動退避至 **「Demo 模擬生圖」** 供您預覽。")
                    else:
                        st.error(f"❌ API 失敗。狀態碼: {response.status_code}")
                        st.info("💡 系統已自動切換至 **「Demo 模擬生圖」** 以利您的作業流程演示。")
                except Exception as e:
                    st.error(f"❌ 連線異常: {str(e)}")
    
            progress_bar.progress(100)
    
            # 渲染結果
            st.subheader("✨ 生成結果")
            if api_success and image_result:
                st.image(image_result, caption=f"Seed: {seed} | 風格: {image_style}", use_container_width=True)
                
                # 提供下載按鈕
                buf = io.BytesIO()
                image_result.save(buf, format="PNG")
                st.download_button(
                    label="💾 下載此圖片 (PNG)",
                    data=buf.getvalue(),
                    file_name=f"cosmos3_output_{seed}.png",
                    mime="image/png",
                    key="streamlit_download_real"
                )
            else:
                # 顯示高品質 Demo 圖片
                style_tags = {
                    "🌌 Cyberpunk (賽博朋克)": "cyberpunk",
                    "📸 Photorealistic (寫實攝影)": "nature",
                    "🎎 Anime Art (日系動漫)": "anime",
                    "🧙 Fantasy Art (奇幻插畫)": "fantasy",
                    "🎨 Oil Painting (古典油畫)": "painting",
                    "無特定風格": "scenery"
                }
                tag = style_tags.get(image_style, "scenery")
                
                # 使用穩定的靜態高畫質展示圖源
                mock_images = {
                    "cyberpunk": "https://images.unsplash.com/photo-1508739773434-c26b3d09e071",
                    "nature": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e",
                    "anime": "https://images.unsplash.com/photo-1578632767115-351597cf2477",
                    "fantasy": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23",
                    "painting": "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119",
                    "scenery": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe"
                }
                img_url = mock_images.get(tag, mock_images["scenery"])
                final_img_url = f"{img_url}?auto=format&fit=crop&w={width}&h={height}&q=80&sig={seed % 1000}"
    
                st.image(final_img_url, caption=f"【Demo 模式】台北城市浮空塔 (Seed: {seed})", use_container_width=True)
                st.info("ℹ️ 此為高性能模擬畫面。若要使用真實 Cosmos3 生成，請至側邊欄填入您的有效 Hugging Face Token。")

# ---- Tab 3: Android APK 下載 ----
with tab3:
    st.markdown("### 📱 Android 行動端 App 下載 (APK)")
    st.caption("您可以下載已包裝完成的 Android APK 檔案，直接在行動裝置上安裝並運行此生圖 App。")
    
    # 使用表格與區塊呈現 APK 資訊
    st.markdown("""
    <div style="background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; margin-bottom: 20px;">
        <h4 style="color: #58a6ff; margin-top: 0; margin-bottom: 15px;">📦 APK 檔案規格資訊</h4>
        <table style="width: 100%; border-collapse: collapse; font-size: 0.9rem;">
            <tr style="border-bottom: 1px solid #21262d;">
                <td style="padding: 10px 0; color: #8b949e; width: 40%;">應用程式名稱 (App Name)</td>
                <td style="padding: 10px 0; color: #c9d1d9; font-weight: bold;">jameswangAPP</td>
            </tr>
            <tr style="border-bottom: 1px solid #21262d;">
                <td style="padding: 10px 0; color: #8b949e;">套件包名 (Package Name)</td>
                <td style="padding: 10px 0; color: #c9d1d9; font-family: monospace;">com.mycompany.jameswangapp</td>
            </tr>
            <tr style="border-bottom: 1px solid #21262d;">
                <td style="padding: 10px 0; color: #8b949e;">版本號碼 (Version)</td>
                <td style="padding: 10px 0; color: #c9d1d9;">1.0 (Mode: Free App)</td>
            </tr>
            <tr style="border-bottom: 1px solid #21262d;">
                <td style="padding: 10px 0; color: #8b949e;">檔案大小 (File Size)</td>
                <td style="padding: 10px 0; color: #c9d1d9;">753 KB (極致輕量化網頁封裝)</td>
            </tr>
            <tr>
                <td style="padding: 10px 0; color: #8b949e;">打包建置來源</td>
                <td style="padding: 10px 0; color: #c9d1d9;"><a href="https://webintoapp.com" target="_blank" style="color: #58a6ff; text-decoration: none;">WebIntoApp.com</a></td>
            </tr>
        </table>
    </div>
    """, unsafe_style_with_html=True)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    apk_path = os.path.join(script_dir, "jameswangAPP 1.0", "android", "app-release.apk")
    
    if os.path.exists(apk_path):
        try:
            with open(apk_path, "rb") as f:
                apk_bytes = f.read()
            
            st.download_button(
                label="📥 點擊此處立即下載 Android APK 檔案",
                data=apk_bytes,
                file_name="jameswangAPP.apk",
                mime="application/vnd.android.package-archive",
                use_container_width=True,
                key="apk_download_btn"
            )
            st.success("🎉 APK 檔案載入成功！點擊上方按鈕即可下載安裝。")
        except Exception as e:
            st.error(f"讀取 APK 檔案失敗: {str(e)}")
    else:
        st.warning(f"⚠️ 找不到 APK 實體檔案，預期路徑為: `{apk_path}`。請確認資料夾名稱與路徑是否正確。")

    st.markdown("""
    ---
    #### 💡 安裝與啟用步驟：
    1. **下載檔案**：點選上方的「下載 Android APK」按鈕，將檔案下載至您的 Android 手機或平板。
    2. **允許安裝未知來源**：
       - 在安裝時若系統跳出「安全性封鎖」提示，請點選 **「設定」**。
       - 啟用 **「允許來自此來源的應用程式」** (Allow installation from unknown sources)。
    3. **完成安裝**：回到安裝介面點擊「安裝」，完成後案頭即可出現 **jameswangAPP** 圖示，打開即可直接使用！
    """)

# -----------------------------------------------------------------------------
# 5. 頁尾
# -----------------------------------------------------------------------------
st.markdown("<div class='footer'>© 2026 Cosmos3-Super-Text2Image Streamlit App. All rights reserved.</div>", unsafe_style_with_html=True)