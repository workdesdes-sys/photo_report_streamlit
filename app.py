import streamlit as st
from docx import Document
from docx.shared import Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from PIL import Image as PILImage
import io
from datetime import datetime
import re

st.set_page_config(page_title="照片報告生成器", page_icon="📸", layout="wide")

st.title("📸 照片報告生成器")
st.markdown("**文字輸入日期 + 最多8張照片 → Word報告**")

# 初始化
if 'photos' not in st.session_state:
    st.session_state.photos = []
if 'descriptions' not in st.session_state:
    st.session_state.descriptions = []

# 日期輸入
col1, col2 = st.columns(2)
with col1:
    report_date = st.text_input("📅 Report Date", value=datetime.now().strftime("%d/%m/%Y"), 
                               placeholder="02/03/2026")
with col2:
    delivery_date = st.text_input("📦 Delivery Date", value=datetime.now().strftime("%d/%m/%Y"), 
                                  placeholder="02/03/2026")

# 日期驗證
def is_valid_date(date_str):
    return re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', date_str) is not None

# 🔧 單一 file_uploader（無 key）
uploaded_files = st.file_uploader("選擇照片 (JPG/PNG/WebP)", 
                                 type=['jpg','jpeg','png','webp'], 
                                 accept_multiple_files=True)

# 處理上傳
if uploaded_files:
    remaining = 8 - len(st.session_state.photos)
    for file in uploaded_files[:remaining]:
        img = PILImage.open(file)
        st.session_state.photos.append(img)
        st.session_state.descriptions.append("")
    st.rerun()

# 照片顯示與編輯
if st.session_state.photos:
    st.subheader(f"📷 已選擇 {len(st.session_state.photos)}/8 張")
    
    for i, (photo, desc) in enumerate(zip(st.session_state.photos, st.session_state.descriptions)):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.image(photo, caption=f"照片 {i+1}", use_column_width=True)
        with col2:
            st.text_input(f"描述 {i+1}", value=desc, key=f"desc_{i}", 
                         on_change=lambda i=i: setattr(st.session_state.descriptions, i, st.session_state[f"desc_{i}"]))
    
    # 🔧 單一按鈕（解決重複問題）
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ 清除全部"):
            st.session_state.photos.clear()
            st.session_state.descriptions.clear()
            st.rerun()
    with col2:
        if st.button("📄 生成報告"):
            if len(st.session_state.photos) == 0:
                st.error("請先上傳照片！")
            elif not is_valid_date(report_date) or not is_valid_date(delivery_date):
                st.error("請檢查日期格式：DD/MM/YYYY")
            else:
                generate_report(report_date, delivery_date)

else:
    st.info("👆 上傳最多8張照片開始使用")

# 生成報告
@st.cache_data
def generate_report(report_date, delivery_date):
    doc = Document()
    
    # 標題
    title = doc.add_heading('照片報告', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 日期
    date_para = doc.add_paragraph()
    date_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    date_para.add_run(f"Report Date: {report_date}  |  Delivery Date: {delivery_date}")
    
    # 照片表格
    table = doc.add_table(rows=4, cols=2)
    table.style = 'Table Grid'
    
    for i in range(min(8, len(st.session_state.photos))):
        cell = table.rows[i//2].cells[i%2]
        img_copy = st.session_state.photos[i].copy()
        img_copy.thumbnail((2*Inches, 2*Inches), PILImage.Resampling.LANCZOS)
        
        img_buffer = io.BytesIO()
        img_copy.save(img_buffer, 'JPEG', quality=90)
        run = cell.paragraphs[0].add_run()
        run.add_picture(img_buffer, width=Cm(4))
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        desc_para = cell.add_paragraph(st.session_state.descriptions[i] or '無描述')
        desc_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    
    return buffer.getvalue()

# 下載按鈕（單獨區域）
if st.session_state.photos:
    if st.button("⬇️ 下載 Word 報告", type="primary"):
        if is_valid_date(report_date) and is_valid_date(delivery_date):
            doc_data = generate_report(report_date, delivery_date)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            st.download_button(
                "📥 下載檔案",
                doc_data,
                f"照片報告_{report_date}_{delivery_date}_{timestamp}.docx",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        else:
            st.error("請修正日期格式！")

st.markdown("---")
st.markdown("*穩定版 • DD/MM/YYYY日期 • Powered by Streamlit* [web:115]")
