import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

st.set_page_config(page_title="Dashboard PLX Pro", layout="wide")
st.title("📊 Dashboard Phân Tích Kỹ Thuật PLX")

EXCEL_FILE = "Du_lieu_PLX.xlsx"

if os.path.exists(EXCEL_FILE):
    # Đọc dữ liệu
    df = pd.read_excel(EXCEL_FILE, sheet_name="Lịch sử giá")
    df['Ngày'] = pd.to_datetime(df['Ngày'])
    df = df.sort_values("Ngày")
    
    # Lọc từ ngày 15/5/2026
    df = df[df['Ngày'] >= '2026-05-15']

    # Tạo biểu đồ 2 tầng: Nến Nhật (trên) và Volume (dưới)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.03, subplot_titles=('Biểu đồ Giá (Nến Nhật)', 'Khối lượng giao dịch'), 
                        row_width=[0.2, 0.7])

    # 1. Vẽ Nến Nhật
    fig.add_trace(go.Candlestick(x=df['Ngày'], open=df['Mở cửa'], high=df['Cao nhất'], 
                                 low=df['Thấp nhất'], close=df['Đóng cửa'], name='Giá'), row=1, col=1)

    # 2. Vẽ Khối lượng (Cột xanh/đỏ)
    colors = ['#ef5350' if row['Đóng cửa'] < row['Mở cửa'] else '#26a69a' for _, row in df.iterrows()]
    fig.add_trace(go.Bar(x=df['Ngày'], y=df['KL'], marker_color=colors, name='Volume'), row=2, col=1)

    fig.update_layout(xaxis_rangeslider_visible=False, template="plotly_white", height=700)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Không tìm thấy file dữ liệu!")