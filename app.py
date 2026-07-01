import streamlit as st
import json
from google import genai
import plotly.graph_objects as go

# Cấu hình trang web rộng rãi, trực quan
st.set_page_config(page_title="Hệ Thống Đánh Giá Năng Lực Toàn Diện A-Z", page_icon="🏆", layout="centered")

# Nhập API Key ở góc trái màn hình để bảo mật
st.sidebar.title("Cấu hình hệ thống")
api_key = st.sidebar.text_input("Nhập Gemini API Key:", type="password", help="Lấy key miễn phí tại Google AI Studio")

# Khởi tạo Client Gemini nếu có API Key
client = None
if api_key:
    client = genai.Client(api_key=api_key)
else:
    st.sidebar.warning("🔑 Vui lòng nhập API Key ở thanh bên để kích hoạt trí tuệ nhân tạo AI!")

# Định nghĩa danh mục chuẩn 26 chỉ số từ A đến Z của bạn
INDICATORS = {
    "A": "Adaptability (Khả năng Thích ứng)",
    "B": "Body (Năng lực Thể chất & Sức khỏe)",
    "C": "Creativity (Khả năng Sáng tạo)",
    "D": "Digital (Năng lực Số & Công nghệ số)",
    "E": "Emotional (Trí tuệ Cảm xúc - EQ)",
    "F": "Financial (Thông minh Tài chính - FQ)",
    "G": "Gold (Tư duy Đặt mục tiêu & Giá trị cốt lõi)",
    "H": "Happiness (Chỉ số Hạnh phúc - HQ)",
    "I": "Intelligence (Trí thông minh - IQ)",
    "J": "Judgment (Năng lực Phán đoán & Ra quyết định)",
    "K": "Kindness (Trí tuệ Trắc ẩn & Lòng tốt)",
    "L": "Leadership (Năng lực Lãnh đạo)",
    "M": "Moral (Chỉ số Đạo đức - MQ)",
    "N": "Network (Năng lực Xây dựng Mối quan hệ)",
    "O": "Organization (Kỹ năng Tổ chức & Quản lý)",
    "P": "Passion (Chỉ số Đam mê & Nhiệt huyết)",
    "Q": "Quantum (Tư duy Đột phá & Nhảy vọt)",
    "R": "Resilience (Năng lực Vượt khó & Kiên cường - AQ)",
    "S": "Spiritual (Trí thông minh Tâm linh - SQ)",
    "T": "Tech (Năng lực Công nghệ & Kỹ thuật)",
    "U": "Understanding (Năng lực Thấu hiểu & Đồng cảm)",
    "V": "Vision (Tư duy Tầm nhìn & Chiến lược)",
    "W": "Willpower (Sức mạnh Ý chí & Nghị lực)",
    "X": "Xenophilia (Lòng hiếu khách & Cởi mở với văn hóa mới)",
    "Y": "Youthfulness (Tư duy Tươi trẻ & Đổi mới)",
    "Z": "Zeal (Sự Hăng hái & Lòng nhiệt thành)"
}

# Khởi tạo trạng thái ứng dụng (Quản lý dữ liệu động)
if 'selected_key' not in st.session_state:
    st.session_state.selected_key = None     # Chưa chọn chữ cái nào
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1        # Mặc định luồng bắt đầu từ Bước 1
if 'ai_intro' not in st.session_state:
    st.session_state.ai_intro = ""
if 'ai_questions' not in st.session_state:
    st.session_state.ai_questions = []
if 'ai_advice' not in st.session_state:
    st.session_state.ai_advice = ""

# Hàm gọi AI hỗ trợ sinh nội dung động
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
# GIAO DIỆN CHÍNH: LƯỚI 26 Ô CHỈ SỐ HOÀN THIỆN
# ==========================================================
if st.session_state.selected_key is None:
    st.title("🏆 Trung Tâm Đánh Giá Toàn Diện 26 Chỉ Số Năng Lực")
    st.write("Chọn một chỉ số bất kỳ bên dưới để khám phá lý thuyết và làm bài đánh giá cá nhân hóa từ AI:")
    st.write("")

    # Sắp xếp 26 ô vuông theo dạng lưới (Mỗi hàng chứa tối đa 4 ô để hiển thị chữ rõ hơn)
    num_columns = 4
    keys_list = list(INDICATORS.keys())
    
    for row_idx in range(0, len(keys_list), num_columns):
        cols = st.columns(num_columns)
        for col_idx in range(num_columns):
            item_idx = row_idx + col_idx
            if item_idx < len(keys_list):
                key = keys_list[item_idx]
                full_name = INDICATORS[key]
                
                # Hiển thị nút bấm cho từng chỉ số
                with cols[col_idx]:
                    if st.button(f"✨ Chỉ Số {key}\n\n{key} Index", use_container_width=True):
                        st.session_state.selected_key = key
                        st.session_state.current_step = 1 # Reset về bước 1 cho chỉ số mới
                        st.session_state.ai_intro = ""    # Xóa dữ liệu cũ
                        st.session_state.ai_questions = []
                        st.session_state.ai_advice = ""
                        st.rerun()

# ==========================================================
# LUỒNG XỬ LÝ ĐỘNG CHO CHỈ SỐ ĐƯỢC CHỌN
# ==========================================================
else:
    current_key = st.session_state.selected_key
    current_name = INDICATORS[current_key]
    
    st.title(f"📊 Hệ Thống Phân Tích Chỉ Số: {current_name}")
    
    # Nút quay về màn hình lưới chính
    if st.button("⬅️ Quay lại Menu 26 Chỉ Số", use_container_width=False):
        st.session_state.selected_key = None
        st.rerun()
        
    st.write("---")

    # --- BƯỚC 1: TỔNG QUAN & BIỂU HIỆN ĐỘNG THEO CHỈ SỐ ---
    if st.session_state.current_step == 1:
        st.header(f"📘 Bước 1: Tổng Quan & Biểu Hiện Của {current_key} Index")
        
        if client and not st.session_state.ai_intro:
            with st.spinner(f"Chuyên gia AI đang phân tích chuyên sâu chỉ số {current_name}..."):
                prompt = f"Viết một bài tổng quan ngắn gọn về chỉ số {current_name}. Bao gồm các mục: 1. Định nghĩa khoa học. 2. Tầm quan trọng trong cuộc sống/sự nghiệp. 3. Ba biểu hiện rõ nét của người đạt điểm cao và ba biểu hiện của người điểm thấp ở chỉ số này. Định dạng Markdown rõ ràng, dễ nhìn."
                st.session_state.ai_intro = generate_ai_content(prompt)
                
        if st.session_state.ai_intro:
            st.markdown(st.session_state.ai_intro)
        else:
            st.info("Hãy nhập API Key ở menu bên trái để kích hoạt bộ não AI phân tích chỉ số này.")
            
        st.write("---")
        if st.button("👉 Tiếp tục: Làm bài trắc nghiệm tình huống", type="primary", use_container_width=True):
            st.session_state.current_step = 2
            st.rerun()

    # --- BƯỚC 2: BÀI TRẮC NGHIỆM ĐỘNG THEO CHỈ SỐ ---
    elif st.session_state.current_step == 2:
        st.header(f"📝 Bước 2: Bài Đánh Giá Trắc Nghiệm {current_key} Index")
        st.write("Hãy chọn phương án phản ánh chính xác nhất xu hướng hành vi thực tế của bạn:")
        
        if client and not st.session_state.ai_questions:
            with st.spinner("AI đang thiết lập bộ câu hỏi tình huống thực tế dành riêng cho bạn..."):
                prompt = f"""
                Tạo 3 câu hỏi trắc nghiệm tình huống thực tế khác nhau để đo lường cụ thể mức độ của chỉ số {current_name}. 
                Trả về kết quả dưới dạng cấu trúc JSON chính xác là một danh sách các đối tượng, mỗi đối tượng gồm:
                {{"question": "Mô tả một tình huống giả định thực tế đòi hỏi chỉ số này...", "options": {{"1": "Phương án xử lý tương ứng mức 1 điểm (Thấp)", "2": "Phương án tương ứng mức 2 điểm", "3": "Phương án tương ứng mức 3 điểm", "4": "Phương án tương ứng mức 4 điểm", "5": "Phương án tương ứng mức 5 điểm (Xuất sắc)"}}}}
                Lưu ý: Chỉ trả về chuỗi văn bản JSON hợp lệ, tuyệt đối không kèm dấu nháy ngược markdown hay lời giải thích ngoài lề.
                """
                raw_json = generate_ai_content(prompt, json_mode=True)
                if raw_json:
                    try:
                        st.session_state.ai_questions = json.loads(raw_json)
                    except:
                        st.error("Hệ thống nhận diện sai cấu trúc JSON từ AI. Vui lòng bấm làm mới ở cuối trang.")

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

    # --- BƯỚC 3: GIẢI PHÁP CẢI THIỆN ĐỘNG & BIỂU ĐỒ ---
    elif st.session_state.current_step == 3:
        st.header("🎯 Bước 3: Phân Tích Kết Quả & Chiến Lược Cải Thiện")
        
        score = st.session_state.get('total_score', 0)
        max_score = st.session_state.get('max_score', 15)
        
        # Sửa triệt để lỗi SyntaxError bằng mảng cố định an toàn
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': f"Thang điểm định vị {current_key} Index", 'font': {'size': 18}},
            gauge = {
                'axis': {'range': [0, max_score], 'tickwidth': 1},
                'bar': {'color': "#1f77b4"},
                'bgcolor': "white",
                'borderwidth': 2,
