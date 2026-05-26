import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# 1. Cấu hình tiêu đề và giao diện trang web
st.set_page_config(page_title="Dashboard Phân Tích PLX", layout="wide")
st.title("📈 Dashboard Phân Tích Số Liệu Cổ Phiếu PLX")
st.markdown("Công cụ tự động hóa theo dõi xu hướng giá đóng cửa và đường trung bình 30 ngày (MA30).")

# Tên file Excel cố định trong hệ thống
EXCEL_FILE = "Du_lieu_PLX.xlsx"

# 2. Tự động kiểm tra và đọc file dữ liệu
if os.path.exists(EXCEL_FILE):
    try:
        # Đọc dữ liệu từ file Excel có sẵn
        df_price = pd.read_excel(EXCEL_FILE, sheet_name="Lịch sử giá")
        df_ma30 = pd.read_excel(EXCEL_FILE, sheet_name="Giá trung bình (30 ngày)")

        # Chuẩn hóa định dạng cột Ngày
        df_price['Ngày'] = pd.to_datetime(df_price['Ngày'])
        df_ma30['Ngày'] = pd.to_datetime(df_ma30['Ngày'])

        # Gộp dữ liệu từ 2 sheet lại làm một
        df_merged = pd.merge(df_price, df_ma30, on=["Mã", "Ngày"], how="inner")
        df_merged = df_merged.sort_values("Ngày")

        # 3. Vẽ biểu đồ tương tác luôn cho mọi người xem
        st.subheader("Biểu đồ Xu hướng Giá và MA30")
        fig = go.Figure()

        # Đường giá đóng cửa
        fig.add_trace(go.Scatter(
            x=df_merged['Nickel_ngay'] if 'Nickel_ngay' in df_merged else df_merged['Ngày'], 
            y=df_merged['Giá đóng cửa'], 
            mode='lines', 
            name='Giá đóng cửa',
            line=dict(color='#1f77b4', width=2.5)
        ))

        # Đường MA30
        fig.add_trace(go.Scatter(
            x=df_merged['Nickel_ngay'] if 'Nickel_ngay' in df_merged else df_merged['Ngày'], 
            y=df_merged['Giá trung bình (30 ngày giao dịch gần nhất)'], 
            mode='lines', 
            name='Đường MA30',
            line=dict(color='#ff7f0e', width=2, dash='dash')
        ))

        fig.update_layout(
            xaxis_title="Thời gian",
            yaxis_title="Mức giá (Nghìn VND)",
            hovermode="x unified",
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Có lỗi xảy ra khi xử lý file dữ liệu. Hãy chắc chắn file Excel có đúng 2 tên sheet là 'Lịch sử giá' và 'Giá trung bình (30 ngày)'. Chi tiết: {e}")
else:
    st.warning(f"Hệ thống chưa tìm thấy file '{EXCEL_FILE}' được tải lên kho lưu trữ.")