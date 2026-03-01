import streamlit as st
from docx import Document
from docx.shared import Inches
from PIL import Image as PILImage
import io
from datetime import datetime

st.set_page_config(layout="wide")
st.title("📸 照片報告生成器")

if "photos" not in st.session_state:
    st.session_state.photos = []
if "descriptions" not in st.session_state:
    st.session_state.descriptions = []

# 日期
col1, col2 = st.columns(2)
report_date = col1.text_input("Report Date", "02/03/2026")
delivery_date = col2.text_input("Delivery Date", "02/03/2026")

# 上傳
uploaded_files = st.file_uploader("選擇照片", 
    type=['jpg','png'], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files[:8]:
        img = PILImage.open(file)
        st.session_state.photos.append(img)
        st.session_state.descriptions.append("")
    st.rerun()

# 顯示照片
if st.session_state.photos:
    for i, photo in enumerate(st.session_state.photos):
        st.image(photo, use_column_width=True)
        st.session_state.descriptions[i] = st.text_input(
            f"描述 {i+1}", 
            value=st.session_state.descriptions[i],
            key=f"d{i}"
        )
    
    if st.button("生成報告"):
        doc = Document()
        doc.add_heading('照片報告', 0)
        doc.add_paragraph(f"Report Date: {report_date}")
        doc.add_paragraph(f"Delivery Date: {delivery_date}")
        
        for i, photo in enumerate(st.session_state.photos[:8]):
            img_copy = photo.copy()
            img_copy.thumbnail((2*Inches, 2*Inches))
            img_buffer = io.BytesIO()
            img_copy.save(img_buffer, 'JPEG')
            run = doc.add_paragraph().add_run()
            run.add_picture(img_buffer)
            doc.add_paragraph(st.session_state.descriptions[i] or "無描述")
        
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        
        st.download_button("下載 Word", buffer.getvalue(), 
                          f"報告_{datetime.now().strftime('%Y%m%d')}.docx")
        
        if st.button("清除"):
            st.session_state.photos = []
            st.session_state.descriptions = []
            st.rerun()
