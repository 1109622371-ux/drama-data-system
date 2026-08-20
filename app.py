import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="短剧账号数据查询后台", layout="wide")

# ==================== 1. 账号权限配置表 ====================
USER_PERMISSIONS = {
    "admin": {"password": "888", "accounts": ["*"], "name": "管理员（总控）"},
    "Cqiuy": {
        "password": "147258", 
        "accounts": [
            "积极向上799", 
            "努力向上799", 
            "困到不睡觉1987", 
            "爱吃鱼的魔镜", 
            "少在意看法", 
            "特工777", 
            "天赐的安排", 
            "特工678", 
            "特工567", 
            "一位正在努力的小人物",
            "二丫头3037",
            "鸟语9273729937",
            "天生牛马123123",
            # 保留之前用过的一些旧账号，防止报错
            "努力面对一切", 
            "溪风晚晚"
        ], 
        "name": "Cqiuy运营团队"
    },
    "260460352": {
        "password": "147258", 
        "accounts": [
            "木瓜的短剧", 
            "幽幽的短剧", 
            "琥珀的短剧", 
            "丫丫的短剧", 
            "流星的短剧", 
            "华丽的草莓", 
            "空空的短剧",
            "心香的短剧"
        ], 
        "name": "260460352运营团队"
    },
    "wkftianlon": {
        "password": "wkf.534577554",
        "accounts": [
            "别划走短剧"
        ],
        "name": "wkftianlon运营团队"
    },
    "sph6X0oBZDqy0pd": {
        "password": "lw910703",
        "accounts": [
            "金秋4498"
        ],
        "name": "sph6X0oBZDqy0pd运营团队"
    },
    "jiruxue": {
        "password": "123456",
        "accounts": [
            "姬如雪1449"
        ],
        "name": "姬如雪运营团队"
    },
    "sphXjQxLY0ir5sq": {
        "password": "Aa3633238",
        "accounts": [
            "可可77922375"
        ],
        "name": "可可运营团队"
    },
    "liulin": {
        "password": "17803252000",
        "accounts": [
            "剧社放映官"
        ],
        "name": "剧社放映官运营团队"
    },
    "xiaridefeng": {
        "password": "wang929568677",
        "accounts": [
            "多多蔓剧"
        ],
        "name": "多多蔓剧运营团队"
    },
    "xiao5024yin": {
        "password": "y502412345",
        "accounts": [
            "王华英6302"
        ],
        "name": "王华英运营团队"
    },
    "Z2767942982": {
        "password": "2454695953",
        "accounts": [
            "小地漫剧"
        ],
        "name": "小地漫剧运营团队"
    },
    "gegechangfa2015": {
        "password": "dongxue198697",
        "accounts": [
            "格格长发"
        ],
        "name": "格格长发运营团队"
    },
    "dsww3588": {
        "password": "dsww3588",
        "accounts": [
            "西瓜夜剧场"
        ],
        "name": "西瓜夜剧场运营团队"
    },
    "W478340463": {
        "password": "wjy130810",
        "accounts": [
            "Junyu0810"
        ],
        "name": "Junyu0810运营团队"
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

uploaded_files = None
if st.session_state.username == "admin":
    uploaded_files = st.sidebar.file_uploader("上传 Excel 报表（管理员专属）", type=["xlsx", "xls"], accept_multiple_files=True)

# 增加一个清理缓存/刷新数据的按钮
if st.sidebar.button("🔄 刷新并加载最新数据"):
    st.cache_data.clear()
    st.success("缓存已清除，数据已更新！")
    st.rerun()

if st.sidebar.button("退出登录"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

st.title("📊 短剧账号数据自助查询系统")

def load_all_data(uploaded_files_list):
    all_dfs = []
    
    # 1. 网页端上传的文件
    if uploaded_files_list:
        for file in uploaded_files_list:
            try:
                xls = pd.ExcelFile(file)
                for sheet in xls.sheet_names:
                    temp_df = pd.read_excel(file, sheet_name=sheet)
                    all_dfs.append(temp_df)
            except:
                pass
                
    # 2. 自动加载 GitHub 根目录下所有的 .xlsx 和 .xls 文件
    excel_files = [f for f in os.listdir('.') if f.lower().endswith(('.xlsx', '.xls'))]
    for file in excel_files:
        try:
            xls = pd.ExcelFile(file)
            for sheet in xls.sheet_names:
                temp_df = pd.read_excel(file, sheet_name=sheet)
                all_dfs.append(temp_df)
        except:
            pass
                
    if all_dfs:
        combined_df = pd.concat(all_dfs, ignore_index=True)
        return combined_df
    return None

df = load_all_data(uploaded_files)

if df is not None:
    if '视频号昵称' in df.columns:
        allowed_accounts = current_user_info["accounts"]
        if "*" in allowed_accounts:
            available_accounts = sorted(df['视频号昵称'].dropna().unique().tolist())
        else:
            available_accounts = [acc for acc in allowed_accounts if acc in df['视频号昵称'].values]
        
        if not available_accounts:
            st.warning("系统中暂未找到分配给您的账号数据（请确保已上传包含该视频号的 Excel 表格）。")
            st.stop()
            
        st.divider()
        st.header("🔍 账号数据查询与筛选")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            selected_account = st.selectbox("选择要查看的视频号：", available_accounts)
            
        acc_df = df[df['视频号昵称'] == selected_account].copy()

        # 智能匹配日期列
        date_col = None
        for col in acc_df.columns:
            if '日期' in str(col) or '时间' in str(col):
                date_col = col
                break
        
        if date_col:
            unique_dates = sorted([str(d) for d in acc_df[date_col].dropna().unique().tolist()])
            with col_f2:
                selected_date = st.selectbox("选择统计日期/周期：", ["全部时间"] + unique_dates)
            if selected_date != "全部时间":
                acc_df = acc_df[acc_df[date_col].astype(str) == selected_date]

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
        
        st.subheader("📋 详细视频明细数据")
        st.dataframe(acc_df, use_container_width=True)
    else:
        st.error("表格中未找到【视频号昵称】列，请检查表头。")
else:
    st.info("👈 请在左侧上传 Excel 数据文件，或在 GitHub 仓库中放入 Excel 表格。")
