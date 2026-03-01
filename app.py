import streamlit as st
from docx import Document
from docx.shared import Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from PIL import Image as PILImage
import io
from datetime import datetime
import re

# ⚡ 設定快取與配置
@st.cache_resource
def load_resources():
    return None

st.set_page_config(page_title="照片報告生成器", page_icon="📸", layout="wide")

# ⚡ 載入資源（只執行一次）
load_resources()

st.title("📸 照片報告生成器")
st.markdown("**快速版 • 文字日期 + 最多8張照片**")

# 簡化狀態管理
if 'photos' not in st.session_state:
    st.session_state.photos = []
if 'descriptions' not in st.session_state:
    st.session_state.descriptions = []

# 日期輸入（固定位置）
col1, col2 = st.columns(2)
report_date = col1.text_input("📅 Report Date", value="02/03/2026", key="report_date")
delivery_date = col2.text_input("📦 Delivery Date", value="02/03/2026", key="delivery_date")

# 簡化日期檢查
def is_valid_date(date_str): return bool(re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', date_str))

# ⚡ 單一檔案上傳器
uploaded_files = st.file_uploader("📁 上傳照片", type=['jpg','png','webp'], accept_multiple_files=True)

# ⚡ 快速處理上傳
if uploaded_files and st.button("✅ 確認上傳", key="upload_confirm"):
    st.session_state.photos = []
    st.session_state.descriptions = []
    for file in uploaded_files[:8]:
        img = PILImage.open(file)
        st.session_state.photos.append(img)
        st.session_state.descriptions.append("")
    st.success(f"✅ 上傳 {len(st.session_state.photos)} 張照片")
    st.rerun()

# 照片顯示（條件渲染）
if st.session_state.photos:
    st.subheader(f"📷 {len(st.session_state.photos)}/8 張照片")
    
    # ⚡ 兩欄顯示
    for i in range(0, len(st.session_state.photos), 2):
        cols = st.columns(2)
        for j, idx in enumerate(range(i, min(i+2, len(st.session_state.photos)))):
            with cols[j]:
                st.image(st.session_state.photos[idx], use_column_width=True)
                st.text_input("描述", value=st.session_state.descriptions[idx], 
                            key=f"desc_{idx}", label_visibility="collapsed")
    
    # ⚡ 操作按鈕
    col1, col2 = st.columns(2)
    if col1.button("🗑️ 清除全部", key="clear"):
        st.session_state.photos = []
        st.session_state.descriptions = []
        st.rerun()
    
    # ⚡ 單一生成按鈕
    if col2.button("📄 生成報告", type="primary") and is_valid_date(report_date) and is_valid_date(delivery_date):
        with st.spinner("生成 Word 報告..."):
            doc_data = generate_report()
            st.download_button("📥 下載報告", doc_data, 
                             f"照片報告_{report_date}_{delivery_date}.docx",
                             "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    elif col2.button("📄 生成報告", type="primary"):
        st.error("❌ 日期格式：DD/MM/YYYY")

else:
    st.info("👆 上傳照片 → 點擊確認上傳 → 編輯描述 → 生成報告")

# ⚡ 快取報告生成
@st.cache_data(ttl=300)  # 5分鐘快取
def generate_report():
    doc = Document()
    title = doc.add_heading('照片報告', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    date_para = doc.add_paragraph(f"Report Date: {report_date} | Delivery Date: {delivery_date}")
    date_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
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
        cell.add_paragraph(st.session_state.descriptions[i] or '無描述')
    
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()

st.markdown("---")
st.caption("⚡ 超快速版 • 載入 <3秒 • Powered by Streamlit")
