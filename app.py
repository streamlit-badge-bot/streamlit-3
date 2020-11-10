from profit_df import profit_summary
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

@st.cache
def get_df():
    return profit_summary()
df0 = get_df().set_index(['date_ms'])


st.image('curio_logo.png', use_column_width=True)

# filtered df
df = df0.copy()
option = st.selectbox('Competitor', df['competitor_name'].unique())
df = df[df['competitor_name'] == option]
df.loc['Total', ['cg', 'cp', 'profit', 'mw']] = df.sum(axis=0, skipna=True)
for col in ['cg', 'cp', 'profit']:
    df[col] = df[col].apply(lambda x: '${0:,.0f}'.format(x).replace('$-', '-$'))
st.dataframe(df)
