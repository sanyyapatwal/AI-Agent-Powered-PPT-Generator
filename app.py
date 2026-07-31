#================= LOAD MODUlE =====================
import os
import time
import langchain
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from tavily import TavilyClient
import pytesseract as pyt
import numpy as np
import streamlit as st


#================= API-KEY=================
GOOGLE_API_KEY = st.sidebar.text_input("Google-API",type = "password")
GROQ_API_KEY = st.sidebar.text_input("Groq-API",type = "password")
TAVILY_API_KEY = st.sidebar.text_input("Tavily-API",type = "password")

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
os.environ["GROQ_API_KEY"] = GROQ_API_KEY
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY

ALL_API = (GOOGLE_API_KEY , GROQ_API_KEY , TAVILY_API_KEY)

if not all(ALL_API):
  st.sidebar.error("PASS API-KEYS")

elif all(ALL_API):
   #step 1: model call
  model = ChatGoogleGenerativeAI(
      model = "gemini-3.5-flash-lite",
      google_api_key = GOOGLE_API_KEY
  )
  st.sidebar.success("API KEYS LOADED SUCCESSFULLY")
  
elif any(ALL_API):
  st.sidebar.info("MUST PASS ALL API KEYS")

else:
  st.sidebar.info("LOADED")

   
#=================FRONT END==================
st.title("AI-Agent-Powered PPT Generator")

user_query = st.text_area("write your PPT topic or prompt:")


#================ASSESTS=========================
# step 2 : tools creation
# tool_1
def search_latest_info(query):
  """ this function search lastest news
  or content from website using tavily,
  helpful to check trending content"""


  client = TavilyClient(api_key = TAVILY_API_KEY)
  response = client.search(query)
  return response


# tool_2
def generate_image(img_prompt):
  """this fucntion helps to generate
  image using free api, with given
  img_prompt using pollinations"""

  url = f"https://image.pollinations.ai/{img_prompt}"
  #file handling
  import requests as r
  content = r.get(url).content
  with open(f"Image.jpeg",'wb') as f:
    f.write(content)

  from PIL import Image
  return url
# WITH TABS
tab1, tab2, tab3 = st.tabs(["GENERATE IMAGE",
                            "CHECK LATEST NEWS",
                            "GENERATE PPT"])


#==================Adv func=================

# detailed prompt generator
def prompt_generator(model,query):
  prompt = f"""your task is to give detailed prompt
  instructions fpr given.


  prompt:
  you are a professional ppt generator , where
  user will give the query and based on that,
  you a have to generate dynamic , HTML output
  based ppt with advanced CSS anf Dynamic UI and UX
  with ppt toggle button ,based on query take
  image refrence to generate and embed the same
  in ppt, using
  Image ref: url = https://images.unsplash.com/photo, 
  or url = https://image.pollinations.ai/, 
  make sure img src must be valid, and image must be
  present inside html, Generate 
  with image caption, and no mardowns
  user query given below : {query}
  """

  response = model.invoke(prompt)
  final_prompt = response.content[-1]['text']

  with open("ppt_prompt.txt",'w') as f:
    f.write(final_prompt)

  return final_prompt
if all(ALL_API) and user_query:
  agent = create_agent(
      model = model ,
      tools = [search_latest_info,
               generate_image])
  
  #=================DISPLAY AGENT================
  
  #st.sidebar.image(agent)
  
  #===================WITH TABS================
  
  with tab1:
    st.header("GENERATE IMAGE  GIVE PROMPT")
    if st.button("CLICK TO GENEARTE:",key="generate_img_button"):
      with st.spinner("Running Agent.."):
        data = f"https://image.pollinations.ai/{user_query}"
        import requests as r
        img_data = r.get(data)
        # time.sleep(3)
        st.image(data)
        #st.image("Image.jpeg")
  
  with tab2:
    st.header("CHECK LATEST NEWS")
    if st.button("FETCH NEWS: ", key="news_button"):
      with st.spinner("Running Agent.."):
  
  
       prompt= """give latest news India or world news realted 
       to tech , bussiness,jobs,or user requested output
       In Proper HTML News Templates"""+user_query
  
       response = agent.invoke({'messages':[{'role':"user",
                                             "content": prompt}]})
  
       code = response['messages'][-1].content[0]['text']
       st.html(code, width= "stretch",
              unsafe_allow_javascript= True)
  
  
  with tab3:
    st.header("CREATE PPT")
    if st.button("click to generate: ", key="generate_ppt_button"):
      with st.spinner("Running Agent.."):
        final_prompt = prompt_generator(model,user_query)
  
        response = agent.invoke({'messages':[{'role':"user",
                                        "content": final_prompt}]})
  
        code = response['messages'][-1].content[-1]['text']
        st.html(code, width="stretch",
                unsafe_allow_javascript=True)
        if st.download_button(label = "DOWNLOAD PPT",
                           data = code,
                           file_name = 'ppt.html',
                           mime = 'text/html'):
          st.success("PPT Downloaded Successfully!!!!!")
  
  
  
  

                    
