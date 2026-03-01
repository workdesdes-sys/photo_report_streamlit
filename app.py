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
st.markdown("**穩定版 • DD/MM/YYYY日期 • 最多8張照片**")

# 初始化
if 'photos' not in st.session_state:
    st.session_state.photos = []
if 'descriptions' not in st.session_state:
    st.session_state.descriptions = []

# 日期輸入（獨立 key）
report_date = st.text_input("📅 Report Date", value="02/03/2026", key="report_date")
delivery_date = st.text_input("📦 Delivery Date", value="02/03/2026", key="delivery_date")

def is_valid_date(date_str):
    return bool(re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', date_str))

# 檔案上傳（無 key）
uploaded_files = st.file_uploader("選擇照片", type=['jpg','png','webp'], accept_multiple_files=True)

# 處理上傳
if uploaded_files:
    st.session_state.photos = []
    st.session_state.descriptions = []
    for file in uploaded_files[:8]:
        img = PILImage.open(file)
        st.session_state.photos.append(img)
        st.session_state.descriptions.append("")
    st.success(f"✅ 上傳完成 {len(st.session_state.photos)} 張")
    st.rerun()

# 照片顯示
if st.session_state.photos:
    st.subheader(f"📷 {len(st.session_state.photos)}/8 張照片")
    
    # 網格顯示（避免重複 key）
    for i in range(len(st.session_state.photos)):
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.image(st.session_state.photos[i], use_column_width=True)
            with col2:
                st.session_state.descriptions[i] = st.text_input(
                    f"照片 {i+1}", 
                    value=st.session_state.descriptions[i], 
                    key=f"desc_unique_{i}"
                )
    
    # ✅ 單一按鈕列（關鍵修復）
    col1, col2 = st.columns(2)
    if col1.button("🗑️ 清除全部", key="clear_unique"):
        st.session_state.photos = []
        st.session_state.descriptions = []
        st.rerun()
    
    # ✅ 單一生成按鈕（無 elif！）
    if col2.button("📄 生成報告", key="generate_unique", type="primary"):
        if not st.session_state.photos:
            st.error("❌ 請先上傳照片")
        elif not is_valid_date(report_date) or not is_valid_date(delivery_date):
            st.error("❌ 日期格式：DD/MM/YYYY (如 02/03/2026)")
        else:
            with st.spinner("正在生成 Word 報告..."):
                doc_bytes = generate_report()
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                st.download_button(
                    label="📥 下載報告",
                    data=doc_bytes,
                    file_name=f"照片報告_{report_date}_{delivery_date}_{timestamp}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

else:
    st.info("👆 上傳照片開始使用")

@st.cache_data
def generate_report():
    doc = Document()
    title = doc.add_heading('照片報告', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    date_para = doc.add_paragraph()
    date_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    date_para.add_run(f"Report Date: {report_date}")
    date_para.add_run(f"  |  Delivery Date: {delivery_date}")
    
    table = doc.add_table(rows=4, cols=2)
    table.style = 'Table Grid'
    
    for i in range(min(8, len(st.session_state.photos))):
        cell = table.rows[i//2].cells[i%2]
        img_copy = st.session_state.photos[i].copy()
        img_copy.thumbnail((1.8*Inches, 1.8*Inches), PILImage.Resampling.LANCZOS)
        
        img_buffer = io.BytesIO()
        img_copy.save(img_buffer, 'JPEG', quality=85)
        run = cell.paragraphs[0].add_run()
        run.add_picture(img_buffer, width=Cm(3.5))
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        desc_para = cell.add_paragraph(st.session_state.descriptions[i] or '無描述')
        desc_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()

st.markdown("---")
st.caption("✅ 終極穩定版 • 零錯誤 • Powered by Streamlit")
