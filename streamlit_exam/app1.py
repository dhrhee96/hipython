import streamlit as st 

st.title("안녕하세요")  
# 브라우저에 텍스트 출력
st.write("hello streamlit!")

st.divider()
# 사용자 입력을 받는요소
name=st.text_input('이름:')

st.write(name)


### pandas
import pandas as pd
df=pd.read_csv('./data/pew.csv')
df.info()
st.write(df.head())


#### 버튼
def btn1_click():
    st.write('능지수준 ㅋㅋㅋㅋ')

st.write('')
#btn1=st.button('클릭하세요',on_click=btn1_click)  # 클릭하면 새로고침됨
btn1=st.button('클릭하세요')
if btn1:
    btn1_click()
