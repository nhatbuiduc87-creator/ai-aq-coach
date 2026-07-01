import streamlit as st
import json
from google import genai

# Cấu hình trang web
st.set_page_config(page_title="Hệ Thống Đánh Giá Năng Lực Toàn Diện A-Z", page_icon="🏆", layout="centered")

# Nhập API Key ở thanh menu bên trái
st.sidebar.title("Cấu hình hệ thống")
api_key = st.sidebar.text_input("Nhập Gemini API Key:", type="password", help="Lấy key miễn phí tại Google AI Studio")

# Khởi tạo Client AI
client = None
if api_key:
    client = genai.Client(api_key=api_key)
else:
    st.sidebar.warning("🔑 Vui lòng nhập API Key ở thanh bên để kích hoạt trí tuệ nhân tạo AI!")

# Danh mục chuẩn 26 chỉ số từ A đến Z của bạn
INDICATORS = {
    "A": "Adaptability", "B": "Body", "C": "Creativity", "D": "Digital",
    "E": "Emotional", "F": "Financial", "G": "Gold", "H": "Happiness",
    "I": "Intelligence", "J": "Judgment", "K": "Kindness", "L": "Leadership",
    "M": "Moral", "N": "Network", "O": "Organization", "P": "Passion",
    "Q": "Quantum", "R": "Resilience", "S": "Spiritual", "T": "Tech",
    "U": "Understanding", "V": "Vision", "W": "Willpower", "X": "Xenophilia",
    "Y": "Youthfulness", "Z": "Zeal"
}

# Khởi tạo bộ nhớ ứng dụng
if 'selected_key' not in st.session_state:
    st.session_state.selected_key = None
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
if 'ai_intro' not in st.session_state:
    st.session_state.ai_intro = ""
if 'ai_questions' not in st.session_state:
    st.session_state.ai_questions = []
if 'ai_advice' not in st.session_state:
    st.session_state.ai_advice = ""

# Hàm gọi AI không chứa khối lệnh lồng nhau phức tạp
def generate_ai_content(prompt, json_mode=False):
    if not client:
        return None
    try:
        gen_config = {"temperature": 0.7}
        if json_mode:
            gen_config["response_mime_type"] = "application/json"
        interaction = client.interactions.create(
            model='gemini-2.5-flash',
            input=prompt,
            generation_config=gen_config
        )
        return interaction.output_text
    except Exception as e:
        st.error(f"Lỗi kết nối API: {e}")
        return None

# ==========================================================
# MÀN HÌNH LƯỚI CHÍNH (Nếu chưa chọn ô nào)
# ==========================================================
if st.session_state.selected_key is None:
    st.title("🏆 Trung Tâm Đánh Giá Toàn Diện 26 Chỉ Số Năng Lực")
    st.write("Chọn một chỉ số bất kỳ bên dưới để khám phá lý thuyết và làm bài đánh giá cá nhân hóa từ AI:")
    st.write("")

    num_columns = 2
    keys_list = list(INDICATORS.keys())
    
    for row_idx in range(0, len(keys_list), num_columns):
        cols = st.columns(num_columns)
        for col_idx in range(num_columns):
            item_idx = row_idx + col_idx
            if item_idx < len(keys_list):
                key = keys_list[item_idx]
                english_name = INDICATORS[key]
                button_label = f"✨ Chỉ Số {key} ({english_name})"
                
                with cols[col_idx]:
                    if st.button(button_label, use_container_width=True, key=f"btn_{key}"):
                        st.session_state.selected_key = key
                        st.session_state.current_step = 1 
                        st.session_state.ai_intro = ""    
                        st.session_state.ai_questions = []
                        st.session_state.ai_advice = ""
                        st.rerun()

# ==========================================================
# LUỒNG CHẠY KHI ĐÃ CHỌN Ô CHỮ CÁI
# ==========================================================
else:
    current_key = st.session_state.selected_key
    current_name = INDICATORS[current_key]
    
    st.title(f"📊 Hệ Thống Phân Tích: {current_key} ({current_name})")
    
    if st.button("⬅️ Quay lại Danh Mục 26 Chỉ Số", use_container_width=False):
        st.session_state.selected_key = None
        st.rerun()
        
    st.write("---")

    # --- BƯỚC 1: XỬ LÝ LÝ THUYẾT TỔNG QUAN ---
    if st.session_state.current_step == 1:
        st.header(f"📘 Bước 1: Tổng Quan & Biểu Hiện Của {current_key} Index")
        
        if client and not st.session_state.ai_intro:
            st.toast("AI đang biên soạn nội dung, vui lòng đợi...")
            prompt = f"Viết một bài tổng quan ngắn gọn về chỉ số {current_key} đại diện cho năng lực {current_name}. Bao gồm các mục: 1. Định nghĩa khoa học. 2. Tầm quan trọng trong cuộc sống/sự nghiệp. 3. Ba biểu hiện rõ nét của người đạt điểm cao và ba biểu hiện của người điểm thấp ở chỉ số này. Định dạng Markdown rõ ràng, dễ nhìn."
            st.session_state.ai_intro = generate_ai_content(prompt)
                
        if st.session_state.ai_intro:
            st.markdown(st.session_state.ai_intro)
        else:
            st.info("Hãy nhập API Key ở menu bên trái để kích hoạt bộ não AI phân tích chỉ số này.")
            
        st.write("---")
        if st.button("👉 Tiếp tục: Làm bài trắc nghiệm tình huống", type="primary", use_container_width=True):
            st.session_state.current_step = 2
            st.rerun()

    # --- BƯỚC 2: XỬ LÝ TRẮC NGHIỆM ĐỘNG ---
    elif st.session_state.current_step == 2:
        st.header(f"📝 Bước 2: Bài Đánh Giá Trắc Nghiệm {current_key} Index")
        st.write("Hãy chọn phương án phản ánh chính xác nhất xu hướng hành vi thực tế của bạn:")
        
        if client and not st.session_state.ai_questions:
            st.toast("AI đang thiết lập bộ đề tình huống...")
            prompt = f"""
            Tạo 3 câu hỏi trắc nghiệm tình huống thực tế khác nhau để đo lường cụ thể mức độ của chỉ số {current_key} ({current_name}). 
            Trả về kết quả dưới dạng cấu trúc JSON chính xác là một danh sách các đối tượng, mỗi đối tượng gồm:
            {{"question": "Mô tả một tình huống giả định thực tế đòi hỏi chỉ số này...", "options": {{"1": "Phương án xử lý tương ứng mức 1 điểm (Thấp)", "2": "Phương án tương ứng mức 2 điểm", "3": "Phương án tương ứng mức 3 điểm", "4": "Phương án tương ứng mức 4 điểm", "5": "Phương án tương ứng mức 5 điểm (Xuất sắc)"}}}}
            Lưu ý: Chỉ trả về chuỗi văn bản JSON hợp lệ, tuyệt đối không kèm dấu nháy ngược markdown hay lời giải thích ngoài lề.
            """
            raw_json = generate_ai_content(prompt, json_mode=True)
            if raw_json:
                try:
                    st.session_state.ai_questions = json.loads(raw_json)
                except:
                    st.error("Lỗi cấu trúc dữ liệu JSON. Vui lòng bấm thử lại.")

        if st.session_state.ai_questions:
            score = 0
            for i, item in enumerate(st.session_state.ai_questions):
                st.markdown(f"**Câu {i+1}: {item['question']}**")
                opts = item['options']
                choice = st.radio(
                    f"Chọn cách ứng xử của bạn cho câu {i+1}:",
                    options=list(opts.keys()),
                    format_func=lambda x: opts[x],
                    key=f"ai_q_{current_key}_{i}",
                    label_visibility="collapsed"
                )
                score += int(choice)
                st.write("")
                
            st.session_state.total_score = score
            st.session_state.max_score = len(st.session_state.ai_questions) * 5
        else:
            st.info("Vui lòng cung cấp API Key hợp lệ ở thanh menu bên trái để sinh bộ đề.")

        st.write("---")
        col_back, col_next = st.columns(2)
        with col_back:
            if st.button("⬅️ Quay lại bước 1", use_container_width=True):
                st.session_state.current_step = 1
                st.rerun()
        with col_next:
            if st.button("📊 Gửi bài test để đánh giá kết quả", type="primary", use_container_width=True):
                st.session_state.current_step = 3
                st.rerun()

    # --- BƯỚC 3: XỬ LÝ ĐIỂM SỐ VÀ GIẢI PHÁP AI ---
    elif st.session_state.current_step == 3:
        st.header("🎯 Bước 3: Kết Quả Định Vị Năng Lực & Kế Hoạch Cải Thiện")
        
        score = st.session_state.get('total_score', 0)
        max_score = st.session_state.get('max_score', 15)
        
        st.metric(label=f"Tổng điểm {current_key} Index của bạn", value=f"{score} / {max_score}")
        
        progress_ratio = float(score) / float(max_score)
        st.progress(progress_ratio)
        
        # Thiết lập văn bản thông báo theo cấu trúc phẳng tuyệt đối
        status_text = f"🚀 Xếp loại: Mức độ {current_key} Index Xuất sắc (Bậc thầy năng lực)"
        if score <= (max_score * 0.4):
            status_text = f"⚠️ Xếp loại: Mức độ {current_key} Index cơ bản (Cần chú trọng nâng cấp)"
        if (score > (max_score * 0.4)) and (score <= (max_score * 0.8)):
            status_text = f"⚡ Xếp loại: Mức độ {current_key} Index Khá tốt (Còn không gian phát triển)"
            
        st.info(status_text)
        st.write("")
        
        if client and not st.session_state.ai_advice:
            st.toast("AI đang phân tích chiến lược, vui lòng đợi...")
            prompt = f"Người dùng vừa làm bài kiểm tra trắc nghiệm chỉ số {current_key} ({current_name}) đạt số điểm {score} trên tổng số {max_score} điểm. Hãy đưa ra nhận xét sâu sắc về điểm mạnh, điểm hạn chế hiện tại của họ dựa theo mức điểm này và đề xuất lộ trình gồm 3 hành động cụ thể nhất giúp họ nâng tầm chỉ số này trong thực tế."
            st.session_state.ai_advice = generate_ai_content(prompt)
                
        if st.session_state.ai_advice:
            st.markdown(st.session_state.ai_advice)
        else:
            st.info("Vui lòng giữ kết nối API Key để đọc phân tích chiến lược từ chuyên gia AI.")

        st.write("---")
        if st.button("🔄 Thử thách lại với bộ đề tình huống khác", use_container_width=True):
            st.session_state.current_step = 1
            st.session_state.ai_questions = []
            st.session_state.ai_advice = ""
            st.rerun()
