import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

st.set_page_config(page_title="Dashboard PLX", layout="wide")
st.title("📊 Dashboard Phân Tích Giá & Khối Lượng PLX")

EXCEL_FILE = "Du_lieu_PLX.xlsx"

if os.path.exists(EXCEL_FILE):
    try:
        # 1. Đọc dữ liệu
        df_price = pd.read_excel(EXCEL_FILE, sheet_name="Lịch sử giá")
        df_ma30 = pd.read_excel(EXCEL_FILE, sheet_name="Giá trung bình (30 ngày)")
        
        # 2. TỰ ĐỘNG SỬA LỖI TÊN CỘT TRONG EXCEL
        for c in df_price.columns:
            c_up = str(c).upper()
            if "MỞ" in c_up: df_price.rename(columns={c: "Giá mở cửa"}, inplace=True)
            elif "CAO" in c_up: df_price.rename(columns={c: "Giá cao nhất"}, inplace=True)
            elif "THẤP" in c_up: df_price.rename(columns={c: "Giá thấp nhất"}, inplace=True)
            elif "ĐÓNG" in c_up: df_price.rename(columns={c: "Giá đóng cửa"}, inplace=True)
            elif "KHỐI" in c_up or "KL" in c_up: df_price.rename(columns={c: "Khối lượng GD"}, inplace=True)
            elif "MÃ" in c_up: df_price.rename(columns={c: "Mã CP"}, inplace=True)
        
        for c in df_ma30.columns:
            if "TRUNG BÌNH" in str(c).upper() or "30" in str(c):
                df_ma30.rename(columns={c: "Giá trung bình (30 ngày giao dịch gần nhất)"}, inplace=True)

        # 3. ÉP KIỂU DỮ LIỆU SỐ
        cols_to_numeric = ["Giá mở cửa", "Giá cao nhất", "Giá thấp nhất", "Giá đóng cửa", "Khối lượng GD"]
        for col in cols_to_numeric:
            if col in df_price.columns:
                df_price[col] = pd.to_numeric(df_price[col], errors='coerce')
        
        if "Giá trung bình (30 ngày giao dịch gần nhất)" in df_ma30.columns:
            df_ma30["Giá trung bình (30 ngày giao dịch gần nhất)"] = pd.to_numeric(df_ma30["Giá trung bình (30 ngày giao dịch gần nhất)"], errors='coerce')

        # 4. Gộp dữ liệu
        df_price['Ngày'] = pd.to_datetime(df_price['Ngày'])
        df_ma30['Ngày'] = pd.to_datetime(df_ma30['Ngày'])
        df = pd.merge(df_price, df_ma30, on="Ngày")
        
        # Lọc bỏ ngày nghỉ và sắp xếp Cũ -> Mới
        df = df[df['Khối lượng GD'] > 0].sort_values("Ngày").copy()
        df['Ngày_chuẩn'] = df['Ngày'].dt.strftime('%d/%m/%Y')
        
        # 5. Thẻ chỉ số
        latest = df.iloc[-1]
        c1, c2, c3 = st.columns(3)
        c1.metric("Giá Đóng Cửa", f"{latest['Giá đóng cửa']:.2f} Nghìn đồng")
        c2.metric("Đường MA30", f"{latest['Giá trung bình (30 ngày giao dịch gần nhất)']:.2f} Nghìn đồng")
        c3.metric("Ngày cập nhật", latest['Ngày_chuẩn'])

        # 6. Vẽ biểu đồ giá
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, 
                            subplot_titles=('Xu hướng Giá & MA30', 'Khối lượng giao dịch'), 
                            row_width=[0.2, 0.7])

        fig.add_trace(go.Scatter(x=df['Ngày_chuẩn'], y=df['Giá đóng cửa'], name='Giá đóng cửa', line=dict(color='#1f77b4', width=2)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df['Ngày_chuẩn'], y=df['Giá trung bình (30 ngày giao dịch gần nhất)'], name='MA30', line=dict(color='orange', width=2, dash='dash')), row=1, col=1)
        fig.add_trace(go.Bar(x=df['Ngày_chuẩn'], y=df['Khối lượng GD'], name='Volume', marker_color='gray'), row=2, col=1)

        fig.update_layout(template="plotly_white", height=600, yaxis=dict(title="Giá (Nghìn đồng)"), hovermode="x unified", dragmode="zoom")
        fig.update_xaxes(type='category', fixedrange=False)
        fig.update_yaxes(fixedrange=False)

        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})

        # ==========================================
        # GIAO DIỆN CƠ CẤU CỔ ĐÔNG & VỐN ĐIỀU LỆ CAO CẤP
        # ==========================================
        st.markdown("<br><hr style='margin-bottom: 20px;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; margin-bottom: 30px; color: #333;'>🥧 Quy mô Vốn & Cơ cấu Cổ đông</h3>", unsafe_allow_html=True)
        
        # Thiết kế khối hiển thị Vốn điều lệ chuẩn phong cách Dashboard tài chính
        st.markdown("""
            <div style="background-color: #f8f9fa; padding: 25px; border-radius: 12px; 
                        box-shadow: 0 4px 10px rgba(0,0,0,0.05); text-align: center; 
                        max-width: 800px; margin: 0 auto 30px auto; border-left: 6px solid #2b5ce6;">
                <p style="font-size: 15px; margin-bottom: 5px; color: #666; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">
                    Vốn điều lệ Tập đoàn
                </p>
                <h2 style="margin: 0; color: #1f4e79; font-size: 34px; font-weight: 700;">
                    12.938.780.810.000 VNĐ
                </h2>
                <p style="font-size: 15px; margin-top: 5px; color: #888;">
                    (Tương đương 1.293.878.081 cổ phiếu)
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Sử dụng cột để khống chế chiều rộng của biểu đồ tròn (tránh bị phình to)
        # Tỷ lệ 1-2-1 tạo ra một cột trung tâm chiếm 50% màn hình, ép biểu đồ vào chính giữa
        col_left, col_center, col_right = st.columns([1, 2, 1])
        
        with col_center:
            labels = ['Bộ Tài Chính', 'Cổ đông nước ngoài', 'Cổ đông khác']
            values = [75.87, 14.10, 10.03] 
            colors = ['#2b5ce6', '#8e8e8e', '#d9d9d9'] # Xanh lam, Xám, Bạc
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=labels, 
                values=values, 
                hole=0.55, # Mở rộng lõi để viền mỏng hơn, hiện đại hơn
                textinfo='percent',
                textposition='inside',
                hoverinfo='label+percent',
                marker=dict(
                    colors=colors, 
                    line=dict(color='#ffffff', width=2.5) # Thêm viền phân cách trắng sắc nét
                )
            )])
            
            fig_pie.update_layout(
                showlegend=True, 
                legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5),
                margin=dict(t=10, b=20, l=0, r=0), 
                height=380,
                paper_bgcolor="rgba(0,0,0,0)", # Xóa nền biểu đồ để tiệp màu với trang web