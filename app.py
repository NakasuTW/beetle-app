import streamlit as st
from ultralytics import YOLO
from PIL import Image

# ==========================================
# 1. 網頁基本設定 (需放在最上方)
# ==========================================
st.set_page_config(page_title="昆蟲辨識小助理", page_icon="🪲", layout="wide")
# ✨ 【魔法 1】：初始化 Session State 來儲存歷史紀錄
if 'history' not in st.session_state:
    st.session_state.history = []
# ==========================================
# 2. 建立昆蟲資料庫字典
# ==========================================
# 這裡的 Key 必須對應你 YOLO 模型的 class name
INSECT_DB = {
    "Gymnopleurus": {
        "chinese_name": "推糞金龜",
        "family": "金龜子科 (Scarabaeidae)",
        "appearance": "黑色或古銅色，體表常具金屬光澤，後足特化略顯彎曲。",
        "meaning": "自然界的勤勞清道夫",
        "season": "春季至秋季",
        "distribution": "常見於台灣低中海拔林緣、牛羊放牧草地。",
        "warning": "安全無毒。",
        "eco_value": "將動物糞便製成糞球埋入地下，能加速物質循環、改良土壤，對維持台灣本土生態多樣性有極大貢獻。"
    },
    "Anomalocera olivacea insularis": {
        "chinese_name": "細腳騷金龜",
        "family": "金龜子科 (Scarabaeidae)",
        "appearance": "體表具明亮金屬光澤（常見綠色、藍色或藍紫色等型態），為大型金龜，其中、後腳脛節內側密生叢毛。",
        "meaning": "穿梭於林間的閃耀寶石",
        "season": "春季至秋季",
        "distribution": "台灣特有種。主要分布於台灣低、中海拔山區林緣。",
        "warning": "安全無毒。",
        "eco_value": "成蟲喜歡訪花以及吸食樹液與腐果，除了參與森林環境的有機物質循環外，亦能協助部分植物進行授粉，對維持生態多樣性有益。"
    },
    "Cyphochilus crataceus": {
        "chinese_name": "白金龜",
        "family": "金龜子科 (Scarabaeidae)",
        "appearance": "體表密布極特殊的白色鱗片，呈現出非常純白、不透明的視覺效果，是自然界中最白的生物結構之一。",
        "meaning": "自然界中最純粹的白",
        "season": "春季至夏季",
        "distribution": "分布於台灣低中海拔山區與林緣。",
        "warning": "安全無毒。",
        "eco_value": "屬於植食性昆蟲，為森林生態系食物鏈的一環。其獨特的超白鱗片光學結構，近年來常成為科學家研發新型環保超白塗料與仿生材料的重要靈感來源。"
    },
    "Epitrichius cupreipes": {
        "chinese_name": "黃肩長腳花金龜",
        "family": "金龜子科 (Scarabaeidae)",
        "appearance": "頭部與前胸背板多呈紅褐色並帶有微弱金屬光澤，翅鞘周圍具有明顯的黃色斑紋，且後腳特化得較為細長。",
        "meaning": "穿梭花叢間的長腿舞者",
        "season": "春末至夏季",
        "distribution": "常見於台灣中低海拔山區與闊葉林緣。",
        "warning": "安全無毒。",
        "eco_value": "成蟲白天極度活躍，經常在花叢間飛舞並訪花吸食花蜜。牠們是協助森林與山區野生植物授粉的重要昆蟲之一，對維護台灣本土植物相的繁衍功不可沒。"
    },
    "Gametis forticula formosana": {
        "chinese_name": "臺灣小綠花金龜",
        "family": "金龜子科 (Scarabaeidae)",
        "appearance": "體色變化極大（常見有綠色、銅綠色、黑褐色等），最明顯的特徵是翅鞘上散布著不規則的白色斑點，且體表常布滿細絨毛。",
        "meaning": "點綴花叢的星點小精靈",
        "season": "春季至秋季 (約 4 到 10 月最為活躍)",
        "distribution": "台灣特有亞種。廣泛分布於台灣平地至中低海拔山區，在野外極為常見。",
        "warning": "安全無毒。",
        "eco_value": "成蟲具有強烈的趨花性，白天常成群聚集在花朵上吸食花蜜或花粉，是自然界中極為重要的授粉昆蟲；幼蟲則以土壤中的腐植質為食，能有效促進有機物質循環，對維持環境生態平衡很有幫助。"
    },
    "Thaumastopeus shanghaicus": {
        "chinese_name": "暗藍扁騷金龜",
        "family": "金龜子科 (Scarabaeidae)",
        "appearance": "體表呈現極具光澤的金屬綠色，體型較大且背部略呈扁平，宛如閃耀的綠寶石，部分個體邊緣會帶有微弱的紅銅色光澤。",
        "meaning": "穿梭於樹冠的綠寶石",
        "season": "夏季至秋季",
        "distribution": "常見於台灣低至中海拔山區及次生林林緣。",
        "warning": "安全無毒。",
        "eco_value": "成蟲極度喜愛吸食殼斗科等樹木的汁液與過熟腐果，是森林冠層中常見的訪客，對於維持森林生態系的物質循環扮演著重要角色。"
    }
}


# ==========================================
# 3. 載入模型
# ==========================================
@st.cache_resource
def load_model():
    return YOLO('best.pt')
model = load_model()

# ==========================================
# 4. 側邊欄設計 (Sidebar) - 動態歷史紀錄
# ==========================================
with st.sidebar:
    st.markdown("### 🌐 選擇語言")
    language = st.selectbox("", ["中文", "English", "日本語", "한국어"], label_visibility="collapsed")
    
    st.markdown("### 功能選項")
    source_option = st.radio("選擇來源", ["拍照", "上傳圖片"])
    
    # ✨ 【魔法 2】：將 Session State 裡的資料動態渲染成手風琴選單
    st.markdown("### 歷史記錄")
    if len(st.session_state.history) == 0:
        st.info("尚無辨識紀錄")
    else:
        # 使用 reversed 讓最新辨識的結果排在最上面
        for idx, record in enumerate(reversed(st.session_state.history)):
            with st.expander(f"🪲 {record['class_name']}"):
                # 顯示 AI 畫好框的縮圖
                st.image(record['image'], caption="辨識圖片", use_container_width=True)
                # 顯示分數點列，還原參考圖風格
                st.markdown(f"• **{record['class_name']}** (信心分數：{record['confidence']:.2f})")

# ==========================================
# 5. 主畫面設計 (Main Page)
# ==========================================
st.title("🪲 昆蟲辨識小助理")
st.write("探索自然世界，學習昆蟲知識，感受生態之美！")
st.markdown("---")

image = None
if source_option == "上傳圖片":
    st.markdown("### 📥 上傳圖片")
    uploaded_file = st.file_uploader("請上傳昆蟲圖片", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image = Image.open(uploaded_file)
elif source_option == "拍照":
    st.markdown("### 📷 拍攝圖片")
    camera_file = st.camera_input("請拍攝昆蟲")
    if camera_file:
        image = Image.open(camera_file)

# ==========================================
# 6. 辨識與結果顯示
# ==========================================
if image is None:
    st.info("請先上傳或拍攝圖片")
else:
    st.image(image, caption='圖片預覽', width=500)

    if st.button('開始辨識', type="primary"):
        st.markdown("### 辨識結果")
        
        with st.spinner('辨識中，請稍候...'):
            results = model(image)
            res_plotted = results[0].plot()
            boxes = results[0].boxes
            
            st.markdown("---")
            st.image(res_plotted, channels="BGR", caption='AI 偵測結果', width=500)
            
            if len(boxes) > 0:
                top_class_id = int(boxes[0].cls[0])
                confidence = float(boxes[0].conf[0])
                class_name = model.names[top_class_id]
                
                st.markdown(f"**物種學名： {class_name}** (信心分數：{confidence:.2f})")
                
                info = INSECT_DB.get(class_name, None)
                if info:
                    st.markdown(f"**中文名稱**：{info['chinese_name']}")
                    st.markdown(f"**屬性**：{info['family']}")
                    st.markdown(f"**外觀特徵**：{info['appearance']}")
                    st.markdown(f"**生態意涵**：{info['meaning']}")
                    st.markdown(f"**生長季節**：{info['season']}")
                    st.markdown(f"**分佈**：{info['distribution']}")
                    st.markdown(f"**毒性警告**：{info['warning']}")
                    st.markdown(f"**環保與保育資訊**：{info['eco_value']}")
                else:
                    st.warning(f"目前資料庫中尚未建檔『{class_name}』的詳細百科資訊。")

                # ✨ 【魔法 3】：成功辨識後，將資料打包存入 Session State 中
                st.session_state.history.append({
                    "class_name": class_name,
                    "confidence": confidence,
                    "image": res_plotted  # 儲存畫好 AI 框線的圖片，這樣歷史紀錄看起來更專業
                })
                
            else:
                st.warning("圖片中沒有偵測到已知的昆蟲。")
                
st.markdown("---")
st.caption("✨ 探索自然，從身邊的昆蟲開始！保護野生動物，維護生態多樣性。")