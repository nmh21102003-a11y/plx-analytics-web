import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

st.set_page_config(page_title="Dashboard PLX", layout="wide")
st.title("📊 Dashboard Phân Tích Giá & Khối Lượng PLX")

EXCEL_FILE = "Du_lieu_PLX.xlsx"

if os.path.exists(EXCEL_FILE):
    # 1. Đọc dữ liệu
    df_price = pd.read_excel(EXCEL_FILE, sheet_name="Lịch sử giá")
    df_ma30 = pd.read_excel(EXCEL_FILE, sheet_name="Giá trung bình (30 ngày)")
    
    # Chuẩn hóa tên cột
    rename_dict = {
        "Mã": "Mã CP",
        "Mở cửa": "Giá mở cửa",
        "Cao nhất": "Giá cao nhất",
        "Thấp nhất": "Giá thấp nhất",
        "Đóng cửa": "Giá đóng cửa",
        "KL": "Khối lượng GD"
    }
    df_price = df_price.rename(columns=rename_dict)
    
    # Chuẩn hóa dữ liệu ngày tháng
    df_price['Ngày'] = pd.to_datetime(df_price['Ngày'])
    df_ma30['Ngày'] = pd.to_datetime(df_ma30['Ngày'])
    df = pd.merge(df_price, df_ma30, on="Ngày")
    
    # Lọc bỏ ngày không giao dịch và sắp xếp cũ -> mới
    df = df[df['Khối lượng GD'] > 0].sort_values("Ngày").copy()
    
    # Ép chuẩn định dạng ngày
    df['Ngày_chuẩn'] = df['Ngày'].dt.strftime('%d/%m/%Y')
    
    # 2. Thẻ chỉ số
    latest = df.iloc[-1]
    c1, c2, c3 = st.columns(3)
    c1.metric("Giá Đóng Cửa", f"{latest['Giá đóng cửa']:.2f} Nghìn đồng")
    c2.metric("Đường MA30", f"{latest['Giá trung bình (30 ngày giao dịch gần nhất)']:.2f} Nghìn đồng")
    c3.metric("Ngày cập nhật", latest['Ngày_chuẩn'])

    # 3. Vẽ biểu đồ 2 tầng (Được ngắt dòng an toàn để chống lỗi copy)
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, 
        subplot_titles=('Xu hướng Giá & MA30', 'Khối lượng giao dịch'), 
        row_width=[0.2, 0.7]
    )

    fig.add_trace(
        go.Scatter(x=df['Ngày_chuẩn'], y=df['Giá đóng cửa'], name='Giá đóng cửa', line=dict(color='#1f77b4', width=2)), 
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=df['Ngày_chuẩn'], y=df['Giá trung bình (30 ngày giao dịch gần nhất)'], name='MA30', line=dict(color='orange', width=2, dash='dash')), 
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(x=df['Ngày_chuẩn'], y=df['Khối lượng GD'], name='Volume', marker_color='gray'), 
        row=2, col=1
    )

    # Cấu hình Zoom và loại bỏ ngày nghỉ
    fig.update_layout(
        template="plotly_white", height=600, 
        yaxis=dict(title="Giá (Nghìn đồng)"), 
        hovermode="x unified", 
        dragmode="zoom"
    )
    
    fig.update_xaxes(type='category', fixedrange=False)
    fig.update_yaxes(fixedrange=False)

    st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})

    # 4. Bảng chi tiết
    st.subheader("📋 Bảng dữ liệu giao dịch")
    df_display = df.copy()
    
    # Cấu hình lại cột STT
    if 'STT' in df_display.columns:
        df_display = df_display.drop(columns=['STT'])
    df_display.insert(0, "STT", range(1, len(df_display) + 1))
    
    # Sắp xếp đúng 9 cột yêu cầu
    cols_order = [
        "STT", "Mã CP", "Ngày_chuẩn", "Giá mở cửa", "Giá cao nhất", 
        "Giá thấp nhất", "Giá đóng cửa", "Khối lượng GD", 
        "Giá trung bình (30 ngày giao dịch gần nhất)"
    ]
    col_names = {"Ngày_chuẩn": "Ngày"}
    
    df_final = df_display[cols_order].rename(columns=col_names)
    
    # Định dạng hiển thị chuẩn: 2 số thập phân và căn lề phải
    styled_df = df_final.style.format({
        'Giá mở cửa': "{:.2f}",
        'Giá cao nhất': "{:.2f}",
        'Giá thấp nhất': "{:.2f}",
        'Giá đóng cửa': "{:.2f}",
        'Khối lượng