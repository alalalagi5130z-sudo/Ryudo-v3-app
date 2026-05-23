import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_gsheets import GSheetsConnection  # スプレッドシート連携用

# --- 1. 基本設定・デザイン ---
st.set_page_config(page_title="弓道 究極管理 V3", layout="wide")
st.markdown("""
    <style>
    .stButton>button { height: 80px; font-size: 30px !important; border-radius: 10px; }
    .condition-box { padding: 10px; border: 1px solid #ddd; border-radius: 5px; background-color: #f0f2f6; }
    </style>
    """, unsafe_allow_html=True)

# スプレッドシート接続設定 (4枚目の写真で見えているあなたのURLを入れてあります)
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1j42siVXTqnFqTg1P70JGiZcfsxa66_Apxq606T_y-fE/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

if "temp_results" not in st.session_state:
    st.session_state.temp_results = []

# --- 2. データ読み込み関数 ---
def load_data():
    try:
        df = conn.read(spreadsheet=SPREADSHEET_URL, ttl="0s")
        if df.empty:
            return pd.DataFrame(columns=['日付', '結果', '射数', '的中数', '的中率', '場所', '種類', '弓力', '天気', '弦', '体調', 'メモ'])
        return df
    except:
        return pd.DataFrame(columns=['日付', '結果', '射数', '的中数', '的中率', '場所', '種類', '弓力', '天気', '弦', '体調', 'メモ'])

df = load_data()

st.title("🏹 弓道 究極管理 V3")

# --- 3. 入力セクション ---
st.subheader("📝 本日の記録")
col1, col2 = st.columns([2, 1])

with col1:
    st.write("### 的中入力")
    b1, b2 = st.columns(2)
    if b1.button("⭕️", use_container_width=True): st.session_state.temp_results.append("○")
    if b2.button("❌", use_container_width=True): st.session_state.temp_results.append("×")
    
    st.info(f"【現在の入力】 {' '.join(st.session_state.temp_results)}")
    if st.button("1つ消す"): 
        if st.session_state.temp_results: st.session_state.temp_results.pop()
        st.rerun()

with col2:
    rec_date = st.date_input("日付を選択", datetime.now().date())
    place = st.selectbox("練習場所", ["県立武道館", "武道センター", "ホームグラウンド", "その他"])
    
    with st.expander("🌟 コンディション詳細 (C案)", expanded=True):
        bow_power = st.number_input("弓力 (kg)", 0.0, 30.0, 15.0, 0.5)
        weather = st.selectbox("天気", ["晴れ", "曇り", "雨", "風", "屋内"])
        string_type = st.text_input("使用弦", "響")
        condition = st.slider("体調 (1:不調〜5:絶好調)", 1, 5, 3)
    
    note = st.text_input("メモ")

    if st.button("✅ 記録をスプレッドシートに保存", type="primary", use_container_width=True):
        if not st.session_state.temp_results:
            st.warning("的中を入力してください")
        else:
            h, s = st.session_state.temp_results.count("○"), len(st.session_state.temp_results)
            new_row = pd.DataFrame([{
                "日付": rec_date.strftime("%Y-%m-%d"),
                "結果": "".join(st.session_state.temp_results),
                "射数": s, "的中数": h, "的中率": round(h/s*100, 1),
                "場所": place, "弓力": bow_power, "天気": weather,
                "弦": string_type, "体調": condition, "メモ": note
            }])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(spreadsheet=SPREADSHEET_URL, data=updated_df)
            st.balloons()
            st.session_state.temp_results = []
            st.success("スプレッドシートに保存しました！")
            st.rerun()

st.divider()

# --- 4. 履歴表示 ---
if not df.empty:
    st.subheader("📊 過去の記録")
    st.dataframe(df.iloc[::-1], use_container_width=True)
