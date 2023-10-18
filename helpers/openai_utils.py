import os
import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains import LLMChain
from dotenv import dotenv_values

openai_api_key = os.getenv('OPENAI_API_TOKEN') if os.getenv('OPENAI_API_TOKEN') else dotenv_values(".env")[
    'OPENAI_API_TOKEN']

template = f"""
    You are a helpful assistant programmed to generate questions based on any text provided. For every chunk of text you receive, you're tasked with designing 5 distinct questions.

    For clarity and ease of processing, structure your response in a way that emulates a Python list of lists. 

    Your output should be shaped as follows:

    1. A question contains more than 12 words.
    2. A question unic and has sense

    Your output should mirror this structure:
    [
        "Generated Question 1",
        "Generated Question 2",
        ...
    ]

    It is crucial that you adhere to this format as it's optimized for further Python processing.

    """


def get_openai_data(text):

    try:
        system_message_prompt = SystemMessagePromptTemplate.from_template(template)
        human_message_prompt = HumanMessagePromptTemplate.from_template("{text}")
        chat_prompt = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt]
        )
        chain = LLMChain(
            llm=ChatOpenAI(openai_api_key=openai_api_key),
            prompt=chat_prompt,
        )
        return chain.run(text)
    except Exception as e:
        if "AuthenticationError" in str(e):
            st.error("Incorrect API key provided. Please check and update your API key.")
            st.stop()
        else:
            st.error(f"An error occurred: {str(e)}")
            st.stop()