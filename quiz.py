import streamlit as st
import pandas as pd
import numpy as np
import openai
from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
import re

openai.api_key = "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"
questions = []

template = """
You are an expert quiz maker for technical fields. Let's think step by step and
create a quiz with {num_questions} {quiz_type} questions about the following concept/content: {quiz_context}.

The format of the quiz could be one of the following:
- Multiple-choice: 
- Questions:
    <Question1>: <a. Answer 1>, <b. Answer 2>, <c. Answer 3>, <d. Answer 4>
    <Question2>: <a. Answer 1>, <b. Answer 2>, <c. Answer 3>, <d. Answer 4>
    ....
- Answers:
    <Answer1>: <a|b|c|d>
    <Answer2>: <a|b|c|d>
    ....
    Example:
    - Questions:
    - 1. What is the time complexity of a binary search tree?
        a. O(n)
        b. O(log n)
        c. O(n^2)
        d. O(1)
    - Answers: 
        1. b
- True-false:
    - Questions:
        <Question1>: <True|False>
        <Question2>: <True|False>
        .....
    - Answers:
        <Answer1>: <True|False>
        <Answer2>: <True|False>
        .....
    Example:
    - Questions:
        - 1. What is a binary search tree?
        - 2. How are binary search trees implemented?
    - Answers:
        - 1. True
        - 2. False
- Open-ended:
- Questions:
    <Question1>: 
    <Question2>:
- Answers:    
    <Answer1>:
    <Answer2>:
Example:
    Questions:
    - 1. What is a binary search tree?
    - 2. How are binary search trees implemented?
    
    - Answers: 
        1. A binary search tree is a data structure that is used to store data in a sorted manner.
        2. Binary search trees are implemented using linked lists.
"""

def get_response(prompt_question):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a helpful research and\
            programming assistant"},
                  {"role": "user", "content": prompt_question}]
    )
    
    return response.choices[0].message.content

def display_quiz():
    user_responses = []
    for i, question in enumerate(questions, start=1):
        st.subheader(f"Question {i}")
        st.write(question['question'])
        
        selected_option = st.radio("Choose an option:", question['options'], key=f"question_{i}", index=None)

        user_responses.append({'question': question['question'], 'selected_option': selected_option})

        st.write(f"You selected: {selected_option}")
    return user_responses

def get_score(user_responses):
    score = 0
    st.subheader(f"Answers")
    col1, col2, col3 = st.columns([3,3,1])
    for i, q in enumerate(questions, 1):
        status = "Wrong"
        if user_responses[i-1]['selected_option'] == q['correct_answer']:
            score += 1
            status = "Correct"
        col1.write(f"Q{i}.Answer : {q['correct_answer']} ")
        col2.write(f"Selected Option : {user_responses[i-1]['selected_option']}")
        col3.write(f"{status}")
    st.markdown(f"## Your Score: {score}/{len(questions)}")

def convert_response(quiz_response):
    inp = quiz_response
    req = inp.strip('\n').split("\n\n")
    q = req[1:-1]
    q[0] = q[0].split("Questions:\n")[1]
    answers = req[-1].split('\n')
    
    mp = {
        'a' : 0,
        'b' : 1,
        'c' : 2,
        'd' : 3
    }
    
    for i in range(1, len(answers)):
        answers[i] = answers[i].split('.')[1].split(' ')[1]
    
    result = []
    for i in range(len(q)):
        question = " ".join(q[i].split('\n')[0].split('.')[1].split(' ')[1:])
        options = []
        for j in range(1, 5):
            options.append(" ".join(q[i].split('\n')[j].split('.')[1].split(' ')[1:]))
        result.append({
            "question": question,
            "options": options,
            "correct_option": answers[1 + i],
            "correct_answer": options[mp[answers[1 + i]]]
        })

    return result

def ai_get_questions(quiz_topic,num_questions):
    prompt = PromptTemplate.from_template(template)
    prompt.format(num_questions=num_questions, quiz_type="multiple-choice", quiz_context=quiz_topic)
    chain = LLMChain(llm=ChatOpenAI(temperature=0.0,openai_api_key=openai.api_key),prompt=prompt)
    quiz_response = chain.run(num_questions=num_questions, quiz_type="multiple-choice", quiz_context=quiz_topic)
    quiz_response = quiz_response + '\n'
    return quiz_response

def main():
    st.title('AI Powered Quiz App')
    quiz_topic = st.text_input("Enter Quiz Topic:")
    num_questions = st.slider("Select Number of Questions", 4, 10)
    st.markdown("Answer the following questions:")
    quiz_response = ai_get_questions(quiz_topic,num_questions)
    gpt_questions = convert_response(quiz_response)
    questions.extend(gpt_questions)

    if 'clicked' not in st.session_state:
        st.session_state.clicked = False

    def click_button():
        st.session_state.clicked = True

    st.button('Start', on_click=click_button)

    if st.session_state.clicked:
        user_responses = display_quiz()
        if st.button('Submit'):
            get_score(user_responses)   

if __name__ == "__main__":
    main()
