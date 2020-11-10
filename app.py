from profit_df import profit_summary
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

@st.cache
def get_df():
    return profit_summary()
df = get_df().set_index(['date_ms'])

# filtered df
option = st.sidebar.selectbox('Competitor', df['competitor_name'].unique())
df1 = df[df['competitor_name'] == option]
df1.loc['Total',['cg', 'cp', 'profit', 'mw']] = df1.sum(axis=0, skipna=True)
for col in ['cg', 'cp', 'profit']:
    df[col] = df[col].apply(lambda x: '${0:,.0f}'.format(x).replace('$-', '-$'))
st.dataframe(df1)

# bar chart
option = st.sidebar.selectbox('Start Date', df.index.unique())
df1 = df.reset_index()
df1 = df1[df1['date_ms'] == option]
df1 = df1.groupby(['date_ms', 'competitor_name'], as_index=False)['mw'].sum().sort_values('mw')
x = df1['competitor_name'].values.tolist()
y = df1['mw'].values.tolist()
fig, ax = plt.subplots()

ax.barh(x, y, align='center')



plt.show()
st.pyplot()





