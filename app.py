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
        
        # TÍNH TOÁN BIẾN ĐỘNG & % THAY ĐỔI CHO BẢNG ĐIỆN TỬ
        df['Biến động'] = df['Giá đóng cửa'].diff()
        df['% Thay đổi'] = (df['Biến động'] / df['Giá đóng cửa'].shift(1)) * 100
        df['Màu_Vol'] = df['Biến động'].apply(lambda x: '#ff3747' if x < 0 else '#00b050') # Đỏ / Xanh lá
        
        df['Ngày_chuẩn'] = df['Ngày'].dt.strftime('%d/%m/%Y')
        
        # 5. THẺ CHỈ SỐ NÂNG CẤP
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        
        delta_price = latest['Giá đóng cửa'] - prev['Giá đóng cửa']
        delta_ma30 = latest['Giá trung bình (30 ngày giao dịch gần nhất)'] - prev['Giá trung bình (30 ngày giao dịch gần nhất)']
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Giá Đóng Cửa", f"{latest['Giá đóng cửa']:.2f} Nghìn đồng", f"{delta_price:.2f} Nghìn đồng")
        c2.metric("Đường MA30", f"{latest['Giá trung bình (30 ngày giao dịch gần nhất)']:.2f} Nghìn đồng", f"{delta_ma30:.2f} Nghìn đồng")
        c3.metric("Ngày cập nhật", latest['Ngày_chuẩn'])

        # 6. VẼ BIỂU ĐỒ 
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, 
                            subplot_titles=('Xu hướng Giá & MA30', 'Khối lượng giao dịch'), 
                            row_width=[0.2, 0.7])

        fig.add_trace(go.Scatter(x=df['Ngày_chuẩn'], y=df['Giá đóng cửa'], name='Giá đóng cửa', line=dict(color='#0055ba', width=2.5)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df['Ngày_chuẩn'], y=df['Giá trung bình (30 ngày giao dịch gần nhất)'], name='MA30', line=dict(color='#f58b00', width=2, dash='dot')), row=1, col=1)
        
        fig.add_trace(go.Bar(x=df['Ngày_chuẩn'], y=df['Khối lượng GD'], name='Volume', marker_color=df['Màu_Vol']), row=2, col=1)

        fig.update_layout(
            template="plotly_white", height=600, 
            hovermode="x unified", dragmode="zoom",
            margin=dict(l=20, r=20, t=40, b=20)
        )
        fig.update_yaxes(title_text="Giá (Nghìn đồng)", gridcolor='rgba(0,0,0,0.05)', row=1, col=1)
        fig.update_yaxes(gridcolor='rgba(0,0,0,0.05)', row=2, col=1)
        fig.update_xaxes(type='category', fixedrange=False, gridcolor='rgba(0,0,0,0.05)')

        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})

        # ==========================================
        # GIAO DIỆN CƠ CẤU CỔ ĐÔNG (PHỐI MÀU MỚI: XANH - VÀNG CAM - XÁM)
        # ==========================================
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; margin-bottom: 25px; color: #222; font-weight: 600;'>Quy mô Vốn & Cơ cấu Cổ đông</h3>", unsafe_allow_html=True)
        
        st.markdown("""
            <div style="background-color: #ffffff; padding: 25px; border-radius: 8px; 
                        box-shadow: 0 4px 20px rgba(0,0,0,0.05); text-align: center; 
                        max-width: 750px; margin: 0 auto 30px auto; border-top: 4px solid #0055ba;">
                <p style="font-size: 13px; margin-bottom: 5px; color: #777; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">
                    Vốn điều lệ Tập đoàn
                </p>
                <h2 style="margin: 0; color: #0055ba; font-size: 34px; font-weight: 700;">
                    12.938.780.810.000 VNĐ
                </h2>
                <p style="font-size: 14px; margin-top: 5px; color: #666;">
                    Tương đương <b style="color: #222;">1.293.878.081</b> cổ phiếu
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        col_left, col_center, col_right = st.columns([1, 2, 1])
        with col_center:
            labels = ['Bộ Tài Chính', 'Cổ đông nước ngoài', 'Cổ đông khác']
            values = [75.87, 14.10, 10.03] 
            
            # Phối màu mới mang lại cảm giác cực kỳ sang trọng
            colors = ['#0055ba', '#ff9f00', '#e0e0e0'] # Xanh lam (SSI) - Vàng Cam (Ngoại) - Xám nhạt
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=labels, values=values, hole=0.45, 
                textinfo='percent', textposition='inside', hoverinfo='label+percent',
                marker=dict(colors=colors, line=dict(color='#ffffff', width=2.5))
            )])
            
            fig_pie.update_layout(
                showlegend=True, 
                legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5, font=dict(color="#444")),
                margin=dict(t=10, b=20, l=0, r=0), height=350,
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        # ==========================================

        # 7. BẢNG CHI TIẾT (CHUẨN BẢNG ĐIỆN TỬ: XANH ĐỎ & ẨN INDEX)
        st.subheader("📋 Bảng dữ liệu giao dịch")
        df_display = df.copy()
        
        if 'STT' in df_display.columns:
            df_display = df_display.drop(columns=['STT'])
        df_display.insert(0, "STT", range(1, len(df_display) + 1))
        
        # Bổ sung cột % Thay đổi vào danh sách hiển thị
        cols_order = ["STT", "Mã CP", "Ngày_chuẩn", "Giá mở cửa", "Giá cao nhất", "Giá thấp nhất", "Giá đóng cửa", "% Thay đổi", "Khối lượng GD", "Giá trung bình (30 ngày giao dịch gần nhất)"]
        valid_cols = [c for c in cols_order if c in df_display.columns]
        df_final = df_display[valid_cols].rename(columns={"Ngày_chuẩn": "Ngày"})
        
        # Hàm tô màu chữ cho tỷ lệ phần trăm
        def color_percent(val):
            if pd.isna(val): return ""
            if val > 0: return 'color: #00b050; font-weight: bold;' # Xanh lá
            elif val < 0: return 'color: #ff3747; font-weight: bold;' # Đỏ
            return 'color: #f58b00; font-weight: bold;' # Vàng tham chiếu
            
        format_dict = {}
        for c in ["Giá mở cửa", "Giá cao nhất", "Giá thấp nhất", "Giá đóng cửa", "Giá trung bình (30 ngày giao dịch gần nhất)"]:
            if c in df_final.columns:
                format_dict[c] = "{:.2f}"
                
        if "% Thay đổi" in df_final.columns:
            format_dict["% Thay đổi"] = lambda x: f"+{x:.2f}%" if x > 0 else f"{x:.2f}%" if pd.notna(x) else ""
            
        if "Khối lượng GD" in df_final.columns:
            format_dict["Khối lượng GD"] = lambda x: f"{int(x):,}".replace(",", ".") if pd.notna(x) else ""
        
        # Áp dụng định dạng và tô màu
        try:
            styled_df = df_final.style.format(format_dict).map(color_percent, subset=['% Thay đổi'])
        except:
            # Fallback cho phiên bản Pandas cũ hơn
            styled_df = df_final.style.format(format_dict).applymap(color_percent, subset=['% Thay đổi'])
            
        # hide_index=True giúp loại bỏ cột số đếm mặc định bên trái cùng của hệ thống
        st.dataframe(styled_df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"⚠️ Phát hiện lỗi bất thường từ dữ liệu Excel: {e}")
        st.warning("Bạn hãy chụp lại khung đỏ này gửi tôi nhé!")
else:
    st.error("Không tìm thấy file Excel!")