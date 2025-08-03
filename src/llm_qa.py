from src import get_prompt
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
import os
from dotenv import load_dotenv
load_dotenv()

def get_chatmodel():
    llm = HuggingFaceEndpoint(
    repo_id="mistralai/Mistral-7B-Instruct-v0.3",
    huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
    task="text-generation",  # better than conversational
    temperature=0.2,
    max_new_tokens=1000
    )
    chatmodel = ChatHuggingFace(llm=llm)
    return chatmodel