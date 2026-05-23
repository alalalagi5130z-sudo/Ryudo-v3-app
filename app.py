import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# ページ設定
st.set_page_config(page_title="的中記録アプリ", layout="centered")

# タイトル
st.title("🎯 的中記録システム")

# スプレッドシートへの接続
conn = st.connection("gsheets", type=GSheetsConnection)

# 既存データの読み込み
try:
    existing_data = conn.read(ttl=0)
    df = pd.DataFrame(existing_data)
except Exception:
    df = pd.DataFrame(columns=["日時", "的中種別", "％", "メモ"])

# 入力フォーム
with st.form("input_form", clear_on_submit=True):
    st.write("### 記録の入力")
    
    # 1. ⭕️/❌ の選択
    hit_type = st.radio("結果を選択してください", ["⭕️ 的中", "❌ 不的中"], horizontal=True)
    
    # 2. ％のスライダー機能
    percentage = st.slider("数値を入力してください（％）", min_value=0, max_value=100, value=50, step=1)
    
    # 3. メモ入力
    note = st.text_input("メモ (任意)", "")
    
    # 送信ボタン
    submit_button = st.form_submit_button("データを確認に追加")

# セッション状態（一時保存用）の初期化
if "temp_data" not in st.session_state:
    st.session_state.temp_data = None

# フォームが送信されたら一時保存
if submit_button:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_row = {
        "日時": current_time,
        "的中種別": hit_type,
        "％": f"{percentage}%",
        "メモ": note
    }
    st.session_state.temp_data = new_row
    st.success(f"【確認】 {hit_type} | {percentage}% （{note}）を追加しました。下のボタンで確定してください。")

# 一時保存されたデータがある場合、確定保存ボタンを表示
if st.session_state.temp_data is not None:
    st.write("---")
    st.write("⚠️ まだスプレッドシートには保存されていません。")
    
    if st.button("✅ 記録をスプレッドシートに保存", type="primary"):
        with st.spinner("スプレッドシートに書き込み中..."):
            try:
                new_df = pd.DataFrame([st.session_state.temp_data])
                updated_df = pd.concat([df, new_df], ignore_index=True)
                
                # 安全な更新処理
                conn.update(data=updated_df)
                
                st.balloons()
                st.success("スプレッドシートへの保存が完了しました！🎉")
                
                st.session_state.temp_data = None
                st.rerun()
                
            except Exception as e:
                st.error("保存中にエラーが発生しました。SettingsのSecretsを確認してください。")
                st.code(str(e))
