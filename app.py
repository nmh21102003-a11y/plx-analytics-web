import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

st.set_page_config(page_title="Dashboard PLX", layout="wide")
st.title("📊 Dashboard Phân Tích Giá & Khối Lượng PLX")

EXCEL_FILE = "Du_lieu_PLX.xlsx"

if os.path.exists(EXCEL_FILE):
    # Đọc dữ liệu
    df_price = pd.read_excel(EXCEL_FILE, sheet_name="Lịch sử giá")
    df_ma30 = pd.read_excel(EXCEL_FILE, sheet_name="Giá trung bình (30 ngày)")
    
    # Chuẩn hóa ngày
    df_price['Ngày'] = pd.to_datetime(df_price['Ngày']).dt.strftime('%d/%m/%Y')
    df_ma30['Ngày'] = pd.to_datetime(df_ma30['Ngày']).dt.strftime('%d/%m/%Y')
    
    # Gộp dữ liệu
    df = pd.merge(df_price, df_ma30, on="Ngày")
    df = df[df['KL'] > 0].copy()
    
    # Thẻ chỉ số
    latest = df.iloc[-1]
    c1, c2, c3 = st.columns(3)
    c1.metric("Giá Đóng Cửa", f"{latest['Đóng cửa']:,} Nghìn đồng")
    c2.metric("Đường MA30", f"{latest['Giá trung bình (30 ngày giao dịch gần nhất)']:,.2f} Nghìn đồng")
    c3.metric("Ngày cập nhật", latest['Ngày'])

    # Vẽ biểu đồ
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, 
                        subplot_titles=('Xu hướng Giá & MA30', 'Khối lượng giao dịch'), 
                        row_width=[0.2, 0.7])

    fig.add_trace(go.Scatter(x=df['Ngày'], y=df['Đóng cửa'], name='Giá đóng cửa', line=dict(color='#1f77b4', width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['Ngày'], y=df['Giá trung bình (30 ngày giao dịch gần nhất)'], name='MA30', line=dict(color='orange', width=2, dash='dash')), row=1, col=1)
    fig.add_trace(go.Bar(x=df['Ngày'], y=df['KL'], name='Volume', marker_color='gray'), row=2, col=1)

    fig.update_layout(template="plotly_white", height=600, yaxis=dict(title="Giá (Nghìn đồng)"), hovermode="x unified", dragmode="zoom")
    fig.update_xaxes(fixedrange=False)
    fig.update_yaxes(fixedrange=False)

    st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})

    # CẤU HÌNH BẢNG CHI TIẾT THEO YÊU CẦU
    st.subheader("📋 Bảng dữ liệu giao dịch")
    
    # Sắp xếp để ngày mới nhất lên đầu
    df_display = df.sort_values("Ngày", ascending=False).copy()
    
    # Tạo cột STT bắt đầu từ 1
    df_display.insert(0, "STT", range(1, len(df_display) + 1))
    
    # Chọn và đổi tên cột theo yêu cầu của bạn
    cols_to_show = {
        "STT": "STT",
        "Mã": "Mã CP",
        "Ngày": "Ngày",
        "Mở cửa": "Mở cửa",
        "Cao nhất": "Cao nhất",
        "Thấp nhất": "Thấp nhất",
        "Đóng cửa": "Đóng cửa",
        "KL": "Khối lượng",
        "Giá trung bình (30 ngày giao dịch gần nhất)": "Giá trung bình"
    }
    
    st.dataframe(df_display[cols_to_show.keys()].rename(columns=cols_to_show), use_container_width=True)

else:
    st.error("Không tìm thấy file Excel!")