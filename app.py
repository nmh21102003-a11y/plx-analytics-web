import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

st.set_page_config(page_title="Dashboard PLX Pro", layout="wide")
st.title("📊 Dashboard Phân Tích Kỹ Thuật PLX")

EXCEL_FILE = "Du_lieu_PLX.xlsx"

if os.path.exists(EXCEL_FILE):
    # 1. Đọc dữ liệu
    df_price = pd.read_excel(EXCEL_FILE, sheet_name="Lịch sử giá")
    df_ma30 = pd.read_excel(EXCEL_FILE, sheet_name="Giá trung bình (30 ngày)")
    
    df_price['Ngày'] = pd.to_datetime(df_price['Ngày'])
    df_ma30['Ngày'] = pd.to_datetime(df_ma30['Ngày'])
    
    # Gộp dữ liệu
    df = pd.merge(df_price, df_ma30, on="Ngày")
    df = df.sort_values("Ngày")
    df = df[df['Ngày'] >= '2026-05-15']

    # 2. HIỂN THỊ CÁC THẺ SỐ LIỆU NHANH (METRICS)
    latest = df.iloc[-1]
    st.markdown("### 📊 Chỉ số phiên gần nhất")
    c1, c2, c3 = st.columns(3)
    c1.metric("Giá Đóng Cửa", f"{latest['Đóng cửa']:,} VND")
    c2.metric("Đường MA30", f"{latest['Giá trung bình (30 ngày giao dịch gần nhất)']:,.2f} VND")
    c3.metric("Ngày Cập Nhật", latest['Ngày'].strftime('%d/%m/%Y'))

    # 3. VẼ BIỂU ĐỒ NẾN NHẬT & VOLUME
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, 
                        subplot_titles=('Biểu đồ Giá & MA30', 'Khối lượng (Volume)'), row_width=[0.2, 0.7])

    # Nến Nhật
    fig.add_trace(go.Candlestick(x=df['Ngày'], open=df['Mở cửa'], high=df['Cao nhất'], 
                                 low=df['Thấp nhất'], close=df['Đóng cửa'], name='Giá'), row=1, col=1)
    # Đường MA30
    fig.add_trace(go.Scatter(x=df['Ngày'], y=df['Giá trung bình (30 ngày giao dịch gần nhất)'], 
                             line=dict(color='orange', width=2), name='MA30'), row=1, col=1)
    # Khối lượng
    colors = ['#ef5350' if r['Đóng cửa'] < r['Mở cửa'] else '#26a69a' for _, r in df.iterrows()]
    fig.add_trace(go.Bar(x=df['Ngày'], y=df['KL'], marker_color=colors, name='Volume'), row=2, col=1)

    fig.update_layout(xaxis_rangeslider_visible=False, template="plotly_white", height=600)
    st.plotly_chart(fig, use_container_width=True)

    # 4. BẢNG DỮ LIỆU CHI TIẾT
    st.subheader("📋 Bảng Tra Cứu Chi Tiết")
    st.dataframe(df.sort_values("Ngày", ascending=False), use_container_width=True)

else:
    st.error("Không tìm thấy file Excel!")