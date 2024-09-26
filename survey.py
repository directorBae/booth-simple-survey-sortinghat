import streamlit as st

# Streamlit 앱 제목 설정
st.title("간단한 설문조사")

# 설문조사 질문 1
question_1 = st.radio(
    "1. 오늘 하루 기분은 어떠신가요?",
    ('좋아요', '보통이에요', '별로에요')
)

# 설문조사 질문 2
question_2 = st.slider(
    "2. 오늘 몇 시간 동안 일하셨나요?",
    min_value=0, max_value=12, step=1
)

# 설문조사 질문 3
question_3 = st.text_input("3. 오늘 특별히 기억에 남는 일이 있나요?")

# 설문조사 질문 4
question_4 = st.selectbox(
    "4. 내일 계획은 어떻게 되시나요?",
    ('휴식', '일정 있음', '미정')
)

# 제출 버튼
if st.button("제출"):
    st.write("설문조사에 응답해주셔서 감사합니다!")
    st.write("응답 내용:")
    st.write(f"1. 기분: {question_1}")
    st.write(f"2. 일한 시간: {question_2} 시간")
    st.write(f"3. 기억에 남는 일: {question_3}")
    st.write(f"4. 내일 계획: {question_4}")

