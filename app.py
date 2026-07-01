import streamlit as st
import json
from google import genai
from google.genai import types
import plotly.graph_objects as go

# Cấu hình trang web công khai
st.set_page_config(page_title="AI AQ Coach", page_icon="🧠", layout="centered")

# Nhập API Key trực tiếp trên giao diện để bảo mật và sử dụng miễn phí
st.sidebar.title("Cấu hình AI")
api_key = st.sidebar.text_input("Nhập Gemini API Key:", type="password", help="Lấy key miễn phí tại Google AI Studio")

# Khởi tạo Client Gemini nếu có API Key
client = None
if api_key:
    client = genai.Client(api_key=api_key)
else:
    st.sidebar.warning("🔑 Vui lòng nhập API Key ở thanh bên để kích hoạt trí tuệ nhân tạo AI!")

# Khởi tạo trạng thái ứng dụng (Quản lý luồng chuyển màn hình)
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
if 'ai_intro' not in st.session_state:
    st.session_state.ai_intro = ""
if 'ai_questions' not in st.session_state:
    st.session_state.ai_questions = []
if 'ai_advice' not in st.session_state:
    st.session_state.ai_advice = ""

st.title("🧠 AI AQ Coach - Phát Triển Năng Lực Thích Ứng")
st.write("---")

# Hàm gọi AI sử dụng cấu trúc Interactions API mới nhất của Google
def generate_ai_content(prompt, json_mode=False):
    if not client:
        return None
    try:
        # Cấu hình trả về định dạng
        config = types.GenerateContentConfig(
            response_mime_type="application/json" if json_mode else "text/plain",
            temperature=0.7
        )
        # Sử dụng API tương tác mới: client.interactions.create thay vì client.models.generate_content
        interaction = client.interactions.create(
            model='gemini-2.5-flash',
            input=prompt,
            config=config
        )
        # Trả về kết quả đầu ra dạng văn bản
        return interaction.output_text
    except Exception as e:
        st.error(f"Lỗi kết nối API mới: {e}")
        return None

# ==========================================================
# BƯỚC 1: TỔNG QUAN & BIỂU HIỆN (AI Tự Động Tạo Nội Dung)
# ==========================================================
if st.session_state.current_step == 1:
    st.header("📘 Bước 1: Tổng Quan & Biểu Hiện Chỉ Số AQ")
    
    if client and not st.session_state.ai_intro:
        with st.spinner("AI đang biên soạn nội dung tổng quan độc quyền cho bạn..."):
            prompt = "Viết một bài tổng quan ngắn gọn về chỉ số thích ứng AQ. Bao gồm: 1. Định nghĩa ngắn. 2. Tầm quan trọng. 3. Ba biểu hiện của người AQ cao và ba biểu hiện của người AQ thấp. Định dạng bằng Markdown đẹp mắt."
            st.session_state.ai_intro = generate_ai_content(prompt)
            
    if st.session_state.ai_intro:
        st.markdown(st.session_state.ai_intro)
    else:
        st.info("Hãy nhập API Key ở menu bên trái để AI tự động tạo nội dung tổng quan sinh động.")
        
    st.write("---")
    if st.button("👉 Tiếp tục: Tạo bài trắc nghiệm bằng AI", type="primary", use_container_width=True):
        st.session_state.current_step = 2
        st.rerun()

# ==========================================================
# BƯỚC 2: BÀI TRẮC NGHIỆM ĐỘNG (AI Thiết Kế Câu Hỏi Tình Huống)
# ==========================================================
elif st.session_state.current_step == 2:
    st.header("📝 Bước 2: Trắc Nghiệm Tình Huống AQ Thực Tế")
    st.write("Các tình huống dưới đây được AI tạo ngẫu nhiên dựa trên các bối cảnh đời sống thực tế:")
    
    if client and not st.session_state.ai_questions:
        with st.spinner("AI đang thiết kế bộ câu hỏi tình huống ngẫu nhiên cho bạn..."):
            prompt = """
            Tạo 3 câu hỏi trắc nghiệm tình huống thực tế để đo lường chỉ số thích ứng AQ. 
            Trả về kết quả dưới dạng JSON là một danh sách các đối tượng, mỗi đối tượng có cấu trúc:
            {"question": "Nội dung tình huống...", "options": {"1": "Lựa chọn tệ nhất (1 điểm)", "2": "Lựa chọn kém (2 điểm)", "3": "Lựa chọn trung bình (3 điểm)", "4": "Lựa chọn tốt (4 điểm)", "5": "Lựa chọn xuất sắc (5 điểm)"}}
            Lưu ý: Chỉ trả về chuỗi JSON hợp lệ, không kèm giải thích hoặc ký tự markdown.
            """
            raw_json = generate_ai_content(prompt, json_mode=True)
            if raw_json:
                try:
                    st.session_state.ai_questions = json.loads(raw_json)
                except:
                    st.error("AI trả về sai cấu trúc câu hỏi. Vui lòng bấm thử lại.")

    if st.session_state.ai_questions:
        score = 0
        for i, item in enumerate(st.session_state.ai_questions):
            st.markdown(f"**Câu {i+1}: {item['question']}**")
            opts = item['options']
            choice = st.radio(
                f"Chọn cách xử lý của bạn cho câu {i+1}:",
                options=list(opts.keys()),
                format_func=lambda x: opts[x],
                key=f"ai_q_{i}",
                label_visibility="collapsed"
            )
            score += int(choice)
            st.write("")
            
        st.session_state.total_score = score
        st.session_state.max_score = len(st.session_state.ai_questions) * 5
    else:
        st.info("Vui lòng cung cấp API Key hợp lệ để AI tạo câu hỏi trắc nghiệm.")

    st.write("---")
    col_back, col_next = st.columns(2)
    with col_back:
        if st.button("⬅️ Quay lại bước 1", use_container_width=True):
            st.session_state.current_step = 1
            st.rerun()
    with col_next:
        if st.button("📊 Gửi câu trả lời để AI phân tích", type="primary", use_container_width=True):
            st.session_state.current_step = 3
            st.rerun()

# ==========================================================
# BƯỚC 3: GIẢI PHÁP CẢI THIỆN & BIỂU ĐỒ TRỰC QUAN (AI Nhận Xét)
# ==========================================================
elif st.session_state.current_step == 3:
    st.header("🎯 Bước 3: Phân Tích Kết Quả & Giải Pháp Từ AI")
    
    score = st.session_state.get('total_score', 0)
    max_score = st.session_state.get('max_score', 15)
    
    # Định nghĩa vùng hiển thị biểu đồ đồng hồ tốc độ an toàn
    x_range = [0, 1]
    y_range = [0, 1]
    chart_domain = dict(x=x_range, y=y_range)
    
    # Tạo biểu đồ Gauge Chart trực quan hiển thị kết quả điểm số
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = chart_domain,
        title = {'text': "Thang đo chỉ số AQ cá nhân", 'font': {'size': 18}},
        gauge = {
            'axis': {'range': [0, max_score], 'tickwidth': 1, 'tickcolor': "black"},
            'bar': {'color': "#1f77b4"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, max_score * 0.4], 'color': '#ff9999'},      # Vùng AQ Thấp (Màu đỏ)
                {'range': [max_score * 0.4, max_score * 0.8], 'color': '#ffff99'}, # Vùng AQ Trung bình (Màu vàng)
                {'range': [max_score * 0.8, max_score], 'color': '#99ff99'}      # Vùng AQ Cao (Màu xanh)
            ],
        }
    ))
    fig.update_layout(height=260, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)
    
    if client and not st.session_state.ai_advice:
        with st.spinner("AI đang phân tích sâu hành vi và lập chiến lược cải thiện riêng cho bạn..."):
            prompt = f"Người dùng vừa làm bài trắc nghiệm AQ đạt số điểm {score} trên tổng số {max_score} điểm. Hãy đưa ra nhận xét cá nhân hóa về điểm mạnh, điểm yếu trong năng lực thích ứng của họ và đề xuất 3 hành động cụ thể, thực tế để họ nâng cao chỉ số AQ này."
            st.session_state.ai_advice = generate_ai_content(prompt)
            
    if st.session_state.ai_advice:
        st.markdown(st.session_state.ai_advice)
    else:
        st.info("Vui lòng kết nối API Key để nhận phân tích chi tiết từ chuyên gia AI.")

    st.write("---")
    if st.button("🔄 Làm lại với bộ câu hỏi mới", use_container_width=True):
        st.session_state.current_step = 1
        st.session_state.ai_questions = []
        st.session_state.ai_advice = ""
        st.rerun()
