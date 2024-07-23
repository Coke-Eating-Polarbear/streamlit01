import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
#import datetime
import matplotlib.pyplot as plt
import matplotlib 
from io import BytesIO
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
# caching
# 인자가 바뀌지 않는 함수 실행 결과를 저장 후 크롬의 임시 저장 폴더에 저장 후 재사용
@st.cache_data
def get_stock_info():
    base_url =  "http://kind.krx.co.kr/corpgeneral/corpList.do"    
    method = "download"
    url = "{0}?method={1}".format(base_url, method)   
    df = pd.read_html(url, header=0,encoding="cp949")[0]
    df['종목코드']= df['종목코드'].apply(lambda x: f"{x:06d}")     
    df = df[['회사명','종목코드']]
    return df

def get_ticker_symbol(company_name):     
    df = get_stock_info()
    code = df[df['회사명']==company_name]['종목코드'].values    
    ticker_symbol = code[0]
    return ticker_symbol

# 코드 조각 추가
st.title('무슨 주식을 사야 부자가 되려나')
stock_name = st.sidebar.text_input("회사이름")
date_range = st.sidebar.date_input("시작일-종료일",[datetime.today(), datetime.today() + timedelta(days=1)])
button_result = st.sidebar.button("확인")
if button_result == True:
    ticker_symbol = get_ticker_symbol(stock_name)     
    start_p = date_range[0]               
    end_p = date_range[1] + timedelta(days=1)
    df = fdr.DataReader(f'KRX:{ticker_symbol}', start_p, end_p)
    df.index = df.index.date
    st.subheader(f"[{stock_name}] 주가 데이터")
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df.index,
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
            )
        ]
    )
    # 검색 시 나타나는 데이터
    st.dataframe(df.tail(7))
    st.plotly_chart(fig, use_container_width=True)

    excel_data = BytesIO()      
    df.to_excel(excel_data)

    csv_data = BytesIO()      
    df.to_csv(csv_data)

    st.download_button("CSV 파일 다운로드", 
        csv_data, file_name='stock_data.csv')

    st.download_button("엑셀 파일 다운로드", 
        excel_data, file_name='stock_data.xlsx')
    