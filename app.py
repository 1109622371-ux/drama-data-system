import streamlit as st
import pandas as pd
import os
import datetime

st.set_page_config(page_title="短剧账号数据查询后台", layout="wide")

# ==================== 1. 账号权限配置表 ====================
USER_PERMISSIONS = {
    "admin": {"password": "888", "accounts": ["*"], "name": "管理员（总控）"},
    "Cqiuy": {
        "password": "147258", 
        "accounts": [
            "一位正在努力的小人物", 
            "努力面对一切", 
            "天赐的安排", 
            "少在意看法", 
            "溪风晚晚", 
            "特工567", 
            "特工678", 
            "特工777"
        ], 
        "name": "Cqiuy运营团队"
    },
}

# ==================== 2. 登录状态管理 ====================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

if not st.session_state.logged_in:
    st.title("🔐 短剧运营数据查询后台 - 登录")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 请输入您的登录凭证")
        input_user = st.text_input("用户名")
        input_pass = st.text_input("密码", type="password")
        if st.button("登录", use_container_width=True):
            if input_user in USER_PERMISSIONS and USER_PERMISSIONS[input_user]["password"] == input_pass:
                st.session_state.logged_in = True
                st.session_state.username = input_user
                st.rerun()
            else:
                st.error("用户名或密码错误，请重新输入！")
    st.stop()

# ==================== 3. 主界面（登录成功后） ====================
current_user_info = USER_PERMISSIONS[st.session_state.username]
st.sidebar.success(f"欢迎您，{current_user_info['name']}！")
if st.sidebar.button("退出登录"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

st.title("📊 短剧账号数据自助查询系统")

# 侧边栏文件上传（支持多选）
uploaded_files = st.sidebar.file_uploader("上传 Excel 报表（可多选）", type=["xlsx", "xls"], accept_multiple_files=True)

@st.cache_data
def load_all_data(uploaded_files_list):
    all_dfs = []
    
    # 1. 如果用户在网页端上传了文件，优先使用网页上传的
    if uploaded_files_list:
        for file in uploaded_files_list:
            try:
                xls = pd.ExcelFile(file)
                for sheet in xls.sheet_names:
                    temp_df = pd.read_excel(file, sheet_name=sheet)
                    all_dfs.append(temp_df)
            except Exception as e:
                pass
    
    # 2. 否则，自动加载 GitHub 目录下的所有 Excel 文件
    else:
        excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx') or f.endswith('.xls')]
        for file in excel_files:
            try:
                xls = pd.ExcelFile(file)
                for sheet in xls.sheet_names:
                    temp_df = pd.read_excel(file, sheet_name=sheet)
                    all_dfs.append(temp_df)
            except Exception as e:
                pass
                
    if all_dfs:
        combined_df = pd.concat(all_dfs, ignore_index=True)
        # 统一处理日期格式，方便后续筛选
        if '日期' in combined_df.columns:
            combined_df['日期_parsed'] = pd.to_datetime(combined_df['日期'], errors='coerce').dt.date
        return combined_df
    return None

df = load_all_data(uploaded_files)

if df is not None:
    if '视频号昵称' in df.columns:
        # 数据权限过滤
        allowed_accounts = current_user_info["accounts"]
        if "*" in allowed_accounts:
            available_accounts = sorted(df['视频号昵称'].dropna().unique().tolist())
        else:
            available_accounts = [acc for acc in allowed_accounts if acc in df['视频号昵称'].values]
        
        if not available_accounts:
            st.warning("系统中暂未找到分配给您的账号数据（请检查 Excel 中的视频号昵称是否匹配）。")
            st.stop()
            
        st.divider()
        st.header("🔍 账号数据查询与筛选")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            selected_account = st.selectbox("选择要查看的视频号：", available_accounts)
        
        acc_df = df[df['视频号昵称'] == selected_account].copy()
        
        # 自定义时间段筛选
        if '日期_parsed' in acc_df.columns and not acc_df['日期_parsed'].isna().all():
            valid_dates = acc_df['日期_parsed'].dropna()
            min_date = valid_dates.min()
            max_date = valid_dates.max()
            
            with col_f2:
                date_range = st.date_input(
                    "选择自定义时间段：",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date
                )
            
            if isinstance(date_range, tuple) and len(date_range) == 2:
                start_d, end_d = date_range
                acc_df = acc_df[(acc_df['日期_parsed'] >= start_d) & (acc_df['日期_parsed'] <= end_d)]
        else:
            with col_f2:
                st.info("当前数据中未检测到标准日期格式，已展示全部时间。")

        # 计算核心指标
        total_videos = len(acc_df)
        total_video_views = acc_df['视频播放量'].sum() if '视频播放量' in acc_df.columns else 0
        total_drama_views = acc_df['剧集播放量'].sum() if '剧集播放量' in acc_df.columns else 0
        total_revenue = acc_df['广告收益'].sum() if '广告收益' in acc_df.columns else 0.0
        mounted_dramas = acc_df['剧目名称'].nunique() if '剧目名称' in acc_df.columns else 0
        
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("发布视频数", f"{total_videos:,}")
        col2.metric("视频播放量", f"{total_video_views:,}")
        col3.metric("剧集播放量", f"{total_drama_views:,}")
        col4.metric("广告收益 (元)", f"{total_revenue:,.2f}")
        col5.metric("挂载剧目数", f"{mounted_dramas}")
        
        st.subheader(f"📌 [{selected_account}] 挂载剧目及收益明细")
        if '剧目名称' in acc_df.columns:
            drama_summary = acc_df.groupby('剧目名称').agg(
                视频数量=('视频ID', 'count') if '视频ID' in acc_df.columns else ('视频播放量', 'count'),
                视频播放量=('视频播放量', 'sum'),
                剧集播放量=('剧集播放量', 'sum'),
                广告收益=('广告收益', 'sum')
            ).reset_index().sort_values(by='广告收益', ascending=False)
            
            st.dataframe(drama_summary, use_container_width=True)
        
        with st.expander("查看详细视频明细"):
            st.dataframe(acc_df, use_container_width=True)
    else:
        st.error("表格中未找到【视频号昵称】列，请检查表头。")
else:
    st.info("👈 请在左侧上传 Excel 数据文件，或在 GitHub 仓库中放入 Excel 表格。")
