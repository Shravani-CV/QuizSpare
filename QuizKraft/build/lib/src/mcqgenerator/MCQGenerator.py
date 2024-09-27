import os
import json
import pandas as pd
import traceback
from dotenv import load_dotenv
from src.mcqgenerator.logger import logging
from src.mcqgenerator.utils import read_file, get_table_data

# Importing neccesaary libraries
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from langchain.callbacks import get_openai_callback

# Load enviornment variables
load_dotenv()

# Access the env variable like os.enviorn
key = os.getenv("OPENAI_API_KEY")


llm = ChatOpenAI(openai_api_key=key, model_name="gpt-3.5-turbo", temperature=0.7)


template = """
Text: {text}
You are an expert MCQ maker. Given the above text, it is your job to \
create a quiz of {number} multiple choice questions for {subject} students in {tone} tone.
Make sure the questions are not repeated and check all the questions to be confirming the text as well.
Make sure to format your response like RESPONSE_JSON below and use it as a guide. \
Ensure to make {number} MCQ's
### RESPONSE_JSON
{response_json}
"""

quiz_generation_prompt = PromptTemplate(
    input_variables=["text", "number", "tone", "subject", "response_json"],
    template=template
) 

quiz_chain = LLMChain(llm=llm, prompt=quiz_generation_prompt, output_key="quiz", verbose=True)


template2 = """
You are an expert english grammarian and writer. Given a Multiple Choice Quiz for {subject} students.\
You need to evaluate the complexity if the questions and give a complete analysis of the quiz. Only use at max words for complexity, 
if he quiz is not at per with the congnitive and analytical abilities of the students,\
update the quiz questions which needs to be changed and change the tone such that it perfectly fits the student abilities.
Quiz_MCQs:
{quiz}

Check from an expert English writer of the above quiz:
        
"""

quiz_evaluation_prompt = PromptTemplate(
    input_variables=["subject","quiz"],
    template=template2
)

review_chain = LLMChain(llm=llm, prompt=quiz_evaluation_prompt, output_key="review", verbose=True)


generate_evaluate_chain = SequentialChain(
    chains=[quiz_chain, review_chain], 
    input_variables=["text", "number", "tone", "subject", "response_json"], 
    output_variables=["quiz","review"], 
    verbose=True
)

