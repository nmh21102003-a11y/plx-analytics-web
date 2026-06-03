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
        # CƠ CẤU CỔ ĐÔNG & VỐN ĐIỀU LỆ
        # ==========================================
        st.markdown("---")
        st.subheader("🥧 Cơ cấu cổ đông & Quy mô vốn")
        
        col1, col2 = st.columns([1.5, 2])
        
        with col1:
            labels = ['Ủy ban Quản lý vốn nhà nước', 'ENEOS Corporation', 'Cổ đông khác']
            values = [75.87, 13.00, 11.13] 
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=labels, 
                values=values, 
                hole=0.4, 
                textinfo='label+percent',
                textposition='inside',
                marker=dict(colors=['#1f77b4', '#ff7f0e', '#2ca02c'])
            )])
            fig_pie.update_layout(showlegend=False, margin=dict(t=10, b=10, l=0, r=0), height=300)
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Thẻ nhấn mạnh Vốn điều lệ
            st.success("🏢 **Vốn điều lệ Tập đoàn:** 12.938 tỷ đồng (Tương đương hơn 1,29 tỷ cổ phiếu)")
            
            st.info('''
            **💡 Ghi chú cấu trúc cổ đông:**
            - **Ủy ban Quản lý vốn Nhà nước (CMSC):** Nắm giữ 75,87%, đại diện sở hữu Nhà nước chi phối toàn diện, đảm bảo định hướng an ninh năng lượng.
            - **ENEOS Corporation:** Nắm giữ 13,00%, đối tác chiến lược từ Nhật Bản, hỗ trợ nâng cao năng lực quản trị, vận hành và kỹ thuật.
            - **Cổ đông khác:** Nắm giữ 11,13%, bao gồm các quỹ đầu tư, tổ chức tài chính và các cổ đông đại chúng trên thị trường.
            ''')
        st.markdown("---")
        # ==========================================

        # 7. Bảng chi tiết
        st.subheader("📋 Bảng dữ liệu giao dịch")
        df_display = df.copy()
        
        if 'STT' in df_display.columns:
            df_display = df_display.drop(columns=['STT'])
        df_display.insert(0, "STT", range(1, len(df_display) + 1))
        
        cols_order = ["STT", "Mã CP", "Ngày_chuẩn", "Giá mở cửa", "Giá cao nhất", "Giá thấp nhất", "Giá đóng cửa", "Khối lượng GD", "Giá trung bình (30 ngày giao dịch gần nhất)"]
        valid_cols = [c for c in cols_order if c in df_display.columns]
        df_final = df_display[valid_cols].rename(columns={"Ngày_chuẩn": "Ngày"})
        
        format_dict = {}
        for c in ["Giá mở cửa", "Giá cao nhất", "Giá thấp nhất", "Giá đóng cửa", "Giá trung bình (30 ngày giao dịch gần nhất)"]:
            if c in df_final.columns:
                format_dict[c] = "{:.2f}"
        if "Khối lượng GD" in df_final.columns:
            format_dict["Khối lượng GD"] = lambda x: f"{int(x):,}".replace(",", ".") if pd.notna(x) else ""
        
        styled_df = df_final.style.format(format_dict)
        st.dataframe(styled_df, use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ Phát hiện lỗi bất thường từ dữ liệu Excel: {e}")
        st.warning("Bạn hãy chụp lại khung đỏ này gửi tôi nhé!")
else:
    st.error("Không tìm thấy file Excel!")