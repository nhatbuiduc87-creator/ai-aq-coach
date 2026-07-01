import streamlit as st
import json
from google import genai

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
    "A": "Adaptability",
    "B": "Body",
    "C": "Creativity",
    "D": "Digital",
    "E": "Emotional",
    "F": "Financial",
    "G": "Gold",
    "H": "Happiness",
    "I": "Intelligence",
    "J": "Judgment",
    "K": "Kindness",
    "L": "Leadership",
    "M": "Moral",
    "N": "Network",
    "O": "Organization",
    "P": "Passion",
    "Q": "Quantum",
    "R": "Resilience",
    "S": "Spiritual",
    "T": "Tech",
    "U": "Understanding",
    "V": "Vision",
    "W": "Willpower",
    "X": "Xenophilia",
    "Y": "Youthfulness",
    "Z": "Zeal"
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
# GIAO DIỆN CHÍNH: LƯỚI 26 Ô HIỂN THỊ ĐẦY ĐỦ TÊN CHỈ SỐ
# ==========================================================
if st.session_state.selected_key is None:
    st.title("🏆 Trung Tâm Đánh Giá Toàn Diện 26 Chỉ Số Năng Lực")
    st.write("Chọn một chỉ số bất kỳ bên dưới để khám phá lý thuyết và làm bài đánh giá cá nhân hóa từ AI:")
    st.write("")

    # Chia lưới thành 2 cột lớn để hiển thị trọn vẹn tên tiếng Anh của chỉ số [2]
    num_columns = 2
    keys_list = list(INDICATORS.keys())
    
    for row_idx in range(0, len(keys_list), num_columns):
        cols = st.columns(num_columns)
        for col_idx in range(num_columns):
            item_idx = row_idx + col_idx
            if item_idx < len(keys_list):
                key = keys_list[item_idx]
                english_name = INDICATORS[key]
                
                # Nút bấm hiển thị định dạng: "A (Adaptability)"
                button_label = f"✨ Chỉ Số {key} ({english_name})"
                
                with cols[col_idx]:
                    if st.button(button_label, use_container_width=True):
                        st.session_state.selected_key = key
                        st.session_state.current_step = 1 
                        st.session_state.ai_intro = ""    
                        st.session_state.ai_questions = []
                        st.session_state.ai_advice = ""
                        st.rerun()

# ==========================================================
# LUỒNG TRẢI NGHIỆM ĐỘNG KHI NGƯỜI DÙNG BẤM VÀO MỘT CHỈ SỐ
# ==========================================================
else:
    current_key = st.session_state.selected_key
    current_name = INDICATORS[current_key]
    
    st.title(f"📊 Hệ Thống Phân Tích: {current_key} ({current_name})")
    
    # Nút bấm quay lại bảng lưới 26 ô chính
    if st.button("⬅️ Quay lại Danh Mục 26 Chỉ Số", use_container_width=False):
        st.session_state.selected_key = None
        st.rerun()
        
    st.write("---")

    # --- BƯỚC 1: TỔNG QUAN & BIỂU HIỆN CHỈ SỐ ---
    if st.session_state.current_step == 1:
        st.header(f"📘 Bước 1: Tổng Quan & Biểu Hiện Của {current_key} Index")
        
        if client and not st.session_state.ai_intro:
            with st.spinner(f"Chuyên gia AI đang phân tích chuyên sâu chỉ số {current_key} ({current_name})..."):
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

    # --- BƯỚC 2: BÀI TRẮC NGHIỆM ĐỘNG DO AI THIẾT KẾ ---
    elif st.session_state.current_step == 2:
        st.header(f"📝 Bước 2: Bài Đánh Giá Trắc Nghiệm {current_key} Index")
        st.write("Hãy chọn phương án phản ánh chính xác nhất xu hướng hành vi thực tế của bạn:")
        
        if client and not st.session_state.ai_questions:
            with st.spinner("AI đang thiết lập bộ câu hỏi tình huống ngẫu nhiên dành riêng cho bạn..."):
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

    # --- BƯỚC 3: HIỂN THỊ ĐIỂM SỐ VÀ PHƯƠNG ÁN CẢI THIỆN ---
    elif st.session_state.current_step == 3:
        st.header("🎯 Bước 3: Kết Quả Định Vị Năng Lực & Kế Hoạch Cải Thiện")
        
        score = st.session_state.get('total_score', 0)
        max_score = st.session_state.get('max_score', 15)
        
        # Thống kê điểm số cơ bản sạch sẽ, trực quan
        st.metric(label=f"Tổng điểm {current_key} Index của bạn", value=f"{score} / {max_score}")
        
        # Tính toán tỷ lệ phần trăm để nạp vào thanh tiến trình (Progress Bar)
        progress_ratio = float(score) / float(max_score)
        st.progress(progress_ratio)
        
        # Tính toán văn bản xếp hạng theo cấu trúc phẳng an toàn không lỗi thụt lề
        status_text = f"🚀 Xếp loại: Mức độ {current_key} Index Xuất sắc (Bậc thầy năng lực)"
        is_low = score <= (max_score * 0.4)
        is_mid = score > (max_score * 0.4) and score <= (max_score * 0.8)
        
        if is_low:
            status_text = f"⚠️ Xếp loại: Mức độ {current_key} Index cơ bản (Cần chú trọng nâng cấp)"
        if is_mid:
            status_text = f"⚡ Xếp loại: Mức độ {current_key} Index Khá tốt (Còn không gian phát triển)"
            
        # Hiển thị kết quả bằng ô thông báo
        st.info(status_text)
        st.write("")
        
        if client and not st.session_state.ai_advice:
            with st.spinner("AI đang lên chiến lược hành động cá nhân hóa dành riêng cho bạn..."):
