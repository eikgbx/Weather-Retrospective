#streamlit run D:\PYTHON\main.py

import streamlit as st
import pandas as pd
from wordcloud import WordCloud

st.title('Weather Retrospective')
st.write("暂时只支持省会城市！")

query_type = st.selectbox("请选择查询类型：", ("城市", "月份", "城市温度", "月份温度", "下雪查询"))

# 读取csv文件
df = pd.read_csv('weather.csv', encoding='gbk')

# 将日期列转换为datetime对象，方便后续处理
# 日期和星期之间以空格分隔
df[['日期', '星期']] = df['日期'].str.split(' ', expand=True, n=1)
df['日期'] = pd.to_datetime(df['日期'])

# 提取月份信息
df['月份'] = df['日期'].dt.month

# 获取所有的城市名
cities = df['城市'].unique().tolist()

if query_type == "城市":
    # 用户可以在下拉菜单中选择一个或多个城市，也可以在输入框中手动输入城市名
    city = st.multiselect("请选择或输入城市名称：", options=cities)
    if city:
        for c in city:
            month = st.slider(f"请选择 {c} 的月份：", min_value=1, max_value=12, key=f"{c}_slider")
            data = df[(df['城市'] == c) & (df['月份'] == month)]
            data = data.set_index('日期')

            # 创建一个新的DataFrame，用于绘制折线图
            chart_data = pd.DataFrame()
            chart_data['最高气温'] = data['最高气温']
            chart_data['最低气温'] = data['最低气温']

            # 绘制折线图
            st.line_chart(chart_data)

            # 将当日天气的内容用空格连接起来
            words = ' '.join(data['当日天气'])

            # 创建一个词云对象
            wc = WordCloud(font_path='SimHei.ttf', background_color="white", max_words=1000)

            # 使用分词后的天气数据生成词云
            wc.generate(words)

            # 将词云转换为图像
            image = wc.to_image()

            # 显示词云图
            st.image(image)

            # 显示城市在各个月份出现最多的天气、最高气温和最低气温
            weather_summary = df[df['城市'] == c].groupby('月份').agg(
                最常出现的天气=('当日天气', lambda x: x.value_counts().index[0]),
                最高气温=('最高气温', 'max'),
                最低气温=('最低气温', 'min')
            )
            st.write(weather_summary)


elif query_type == "月份":
    month = st.number_input("请输入月份（1-12）：", min_value=1, max_value=12, step=1)
    if month:
        data = df[df['月份'] == month].groupby('城市').agg(
            最常出现的天气=('当日天气', lambda x: x.value_counts().index[0]),
            最高气温=('最高气温', 'max'),
            最低气温=('最低气温', 'min')
        )
        st.write(data)

        if st.button("懒人按钮"):
            # 定义一个度量来决定哪些城市是最好的
            best_cities = data[(data['最高气温'] >= 20) & (data['最高气温'] <= 30) &
                               (data['最低气温'] >= 10) & (data['最低气温'] <= 20) &
                               ((data['最常出现的天气'] == '晴天') | (data['最常出现的天气'] == '多云'))]

            # 如果有超过三个城市满足条件，只选择前三个
            if len(best_cities) > 3:
                best_cities = best_cities[:3]

            # 如果有城市满足条件，显示推荐的城市
            if len(best_cities) > 0:
                st.write(f"如果您懒得想，这边推荐您可以在{month}月去{', '.join(best_cities.index)}。")
            else:  # 如果没有城市满足条件，显示默认建议
                st.write("如果您懒得想，可以多喝热水，在家休息0x0.")



elif query_type == "城市温度":
    city = st.multiselect("请选择或输入城市名称：", options=cities)
    temp_high = st.number_input("请输入最高气温：")
    temp_low = st.number_input("请输入最低气温：")
    if city and temp_high and temp_low:
        for c in city:
            data = df[(df['城市'] == c) & (df['最高气温'] <= temp_high) & (df['最低气温'] >= temp_low)].groupby('月份').agg(
                最常出现的天气=('当日天气', lambda x: x.value_counts().index[0])
            )
            st.write(f"{c}的数据：")
            st.write(data)


elif query_type == "月份温度":
    month = st.number_input("请输入月份（1-12）：", min_value=1, max_value=12, step=1)
    temp_high = st.number_input("请输入最高气温：")
    temp_low = st.number_input("请输入最低气温：")
    if month and temp_high and temp_low:
        data = df[(df['月份'] == month) & (df['最高气温'] <= temp_high) & (df['最低气温'] >= temp_low)].groupby('城市').agg(
            最常出现的天气=('当日天气', lambda x: x.value_counts().index[0])
        )
        st.write(data)

elif query_type == "下雪查询":
    city = st.multiselect("请选择或输入城市名称：", options=cities)
    if city:
        for c in city:
            snow_months = df[(df['城市'] == c) & (df['当日天气'].str.contains('雪'))]['月份'].unique()
            if len(snow_months) > 0:
                st.write(f"{c}在以下月份有下雪的记录：{', '.join(map(str, sorted(snow_months)))}。")
            else:
                st.write(f"{c}没有下雪的记录。")