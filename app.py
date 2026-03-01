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
uploaded_files = st.
