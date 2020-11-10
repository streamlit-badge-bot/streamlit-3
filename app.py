from profit_df import profit_summary
import streamlit as st
import pandas as pd


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







