from profit_df import profit_summary
import streamlit as st

@st.cache
def get_df():
    return profit_summary()
df = get_df().set_index(['date_ms'])

option = st.sidebar.selectbox('Competitor', df['competitor_name'].unique())
# # print(option)
df = df[df['competitor_name'] == option]
df.loc['Total',['cg', 'cp', 'profit', 'mw']]= df.sum(axis=0, skipna=True)
for col in ['cg', 'cp', 'profit']:
    df[col] = df[col].apply(lambda x: '${0:,.0f}'.format(x).replace('$-', '-$'))
# df = df

st.dataframe(df)





