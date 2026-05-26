import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# 1. Cấu hình tiêu đề và giao diện trang web
st.set_page_config(page_title="Dashboard Phân Tích PLX", layout="wide")
st.title("📈 Dashboard Phân Tích Số Liệu Cổ Phiếu PLX")
st.markdown("Công cụ tự động hóa theo dõi xu hướng giá đóng cửa và đường MA30 từ ngày 15/05/2026.")

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

        # LỆNH LỌC: Chỉ lấy dữ liệu từ ngày 15/05/2026 trở đi
        df_filtered = df_merged[df_merged['Ngày'] >= '2026-05-15']

        if not df_filtered.empty:
            # Tự động tìm tên cột MA30 trong file dữ liệu
            ma30_col = [c for c in df_filtered.columns if '30' in c][0]
            
            # Thêm các thẻ chỉ số nhanh (Metrics) hiển thị biến động giá ngày mới nhất
            latest_row = df_filtered.iloc[-1]
            prev_row = df_filtered.iloc[-2] if len(df_filtered) > 1 else latest_row
            
            st.markdown("### 📊 Chỉ số cập nhật phiên gần nhất")
            col1, col2, col3 = st.columns(3)
            with col1:
                price_delta = float(latest_row['Giá đóng cửa'] - prev_row['Giá đóng cửa'])
                st.metric(label="Giá Đóng Cửa Hàng Ngày", value=f"{latest_row['Giá đóng cửa']:,} VND", delta=f"{price_delta:+,} VND")
            with col2:
                ma30_delta = float(latest_row[ma30_col] - prev_row[ma30_col])
                st.metric(label="Giá Đường MA30", value=f"{latest_row[ma30_col]:,.2f} VND", delta=f"{ma30_delta:+,.2f} VND")
            with col3:
                st.metric(label="Ngày Cập Nhật Số Liệu", value=latest_row['Ngày'].strftime('%d/%m/%Y'))

            # 3. Vẽ biểu đồ tương tác đường Giá hàng ngày và đường MA30
            st.subheader("Biểu đồ Xu hướng Giá và MA30 (Từ 15/05/2026)")
            fig = go.Figure()

            # Đường giá đóng cửa hàng ngày (Màu xanh dương)
            fig.add_trace(go.Scatter(
                x=df_filtered['Ngày'], 
                y=df_filtered['Giá đóng cửa'], 
                mode='lines+markers', 
                name='Giá đóng cửa hàng ngày',
                line=dict(color='#1f77b4', width=2.5),
                marker=dict(size=6)
            ))

            # Đường MA30 (Màu cam đứt nét)
            fig.add_trace(go.Scatter(
                x=df_filtered['Ngày'], 
                y=df_filtered[ma30_col], 
                mode='lines+markers', 
                name='Đường MA30',
                line=dict(color='#ff7f0e', width=2, dash='dash'),
                marker=dict(size=6)
            ))

            fig.update_layout(
                xaxis_title="Thời gian",
                yaxis_title="Mức giá (VND)",
                hovermode="x unified",
                template="plotly_white",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )

            st.plotly_chart(fig, use_container_width=True)
            
            # Hiển thị thêm bảng số liệu thô phía dưới để tra cứu giá hàng ngày
            st.subheader("📋 Bảng Tra Cứu Giá Hàng Ngày và MA30 Chi Tiết")
            df_display = df_filtered.copy()
            df_display['Ngày'] = df_display['Ngày'].dt.strftime('%d/%m/%Y')
            
            # Chỉ hiển thị các cột quan trọng, xếp ngày mới nhất lên trên đầu
            display_cols = ["Mã", "Ngày", "Giá đóng cửa", ma30_col]
            st.dataframe(df_display[display_cols].sort_values("Ngày", ascending=False), use_container_width=True)
            
        else:
            st.warning("Trong file Excel không có dữ liệu nào từ ngày 15/05/2026 trở đi.")

    except Exception as e:
        st.error(f"Có lỗi xảy ra khi xử lý file dữ liệu: {e}")
else:
    st.warning(f"Hệ thống chưa tìm thấy file '{EXCEL_FILE}' được tải lên kho lưu trữ.")