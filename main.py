import os
from dotenv import load_dotenv
load_dotenv()

os.environ['GOOGLE_API_KEY']=os.getenv('GOOGLE_API_KEY')

#for tracing
os.environ['LANGCHAIN_API_KEY']=os.getenv('LANGCHAIN_API_KEY')
os.environ['LANGSMITH_TRACING']=os.getenv('LANGSMITH_TRACING')
os.environ['LANGSMITH_ENDPOINT']=os.getenv('LANGSMITH_ENDPOINT')
os.environ['LANGSMITH_PROJECT']=os.getenv('LANGSMITH_PROJECT')


from langchain_community.document_loaders import YoutubeLoader
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate



import streamlit as st
import validators


prompt=ChatPromptTemplate.from_messages(
    [
        ('system','''You are an expert multilingual content analyst.

Your task is to create a detailed, information-rich summary of the provided content.

Requirements:
- Preserve all  topics and sections.
- Retain  all facts, explanations, examples, definitions, arguments, and conclusions.
- Do not omit key details .
- Remove repetition .
- Keep technical terms, names, numbers, statistics, and dates when present.
- Maintain the original meaning and context.
- If the content contains steps, processes, or instructions, preserve them in order.
- If multiple topics are discussed, create separate sections for each topic.
- Write in clear  language.

Output format:
# Overview
A concise overview of the content.

# Main Topics
For each  topic:
## Topic Name
- Key points
- details in depth
- Examples (if present)

# Important Facts
- Fact 1
- Fact 2
- Fact 3

# Key Takeaways
- Most important conclusions and insights
 '''),
        ('user','{document}')
    ]
)

def get_transcript(url:str)->str:
    """Given a youtube video url it will generate transcript required to generate summary"""
    try:
        loader=YoutubeLoader.from_youtube_url(url,add_video_info=False)
        docs=loader.load()

        return docs[0].page_content
    except Exception as e:
        print(e)

def get_doc_from_url(url:str)->str:
    """given a non youtube url it will generate the doc needed to summarize"""
    try:
        loader=UnstructuredURLLoader(urls=[url])
        docs=loader.load()        
        return "\n".join([doc.page_content for doc in docs])
    
    except Exception as e:
        print(e)
    

st.sidebar.title('Settings')
gemini_key=st.sidebar.text_input(label='Your gemini api key from google ai studio',type='password')

st.title('Basic youtube  or docs url summarizer 🦜 ')
entered_url=st.text_input(label='Enter a valid url',placeholder='eg. youtube.com/watch?v=....')

if gemini_key:
    llm=ChatGoogleGenerativeAI(model='gemini-3.1-flash-lite',api_key=gemini_key,streaming=True)

else:
    llm=ChatGoogleGenerativeAI(model='gemini-3.1-flash-lite',streaming=True)


chain=prompt|llm

if entered_url:
    if validators.url(entered_url):
        if 'youtube'  in str(entered_url) or 'youtu.be' in str(entered_url):
            with st.spinner("Getting transcript..."):  
                transcript=get_transcript(entered_url)
            st.write(f"No of words in video's transcript : {len(transcript.split())}")

            with st.spinner("Getting summary..."):  
                try:               
                    response=chain.stream({'document':transcript})
                except Exception as e:
                    st.exception(f'Error occured {e}')
                    st.stop()
             

            placeholder = st.empty()
            final_response = ""

            for chunk in response:
                print("--------------")
                try:
                    final_response += chunk.text
                    print(chunk)
                    placeholder.markdown(final_response + "▌")
                    

                except Exception as e:
                    print(e)



        else:
            with st.spinner("Getting docs..."): 
                docs=get_doc_from_url(entered_url)
                    
            st.write(f"No of words in docs : {len(docs.split())}")


            with st.spinner("Getting summary..."):  
                try:               
                    response=chain.stream({'document':docs})
                except Exception as e:
                    st.exception(f'Error occured {e}')
                    st.stop()

           
            placeholder = st.empty()
            final_response = ""

            for chunk in response:
                print("--------------")
                try:
                    final_response += chunk.text
                    placeholder.markdown(final_response + "▌")
                    print(final_response)

                except Exception as e:
                    print(e)



    else:
        st.error("don't be smart enter a valid url")



