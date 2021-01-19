#!/usr/bin/env python
# coding: utf-8

# # Mineração de dados

# ## Trabalho 01 - Construção de dataset com scraping

# ### Rômulo Ferreira
# ### 378612
# ### Engenharia de Computação

# ## Codigo completo

# In[33]:


#importações
from time import sleep
import requests
import pandas as pd
import csv
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from msedge.selenium_tools import Edge, EdgeOptions
import json

def get_tweet_data(card):
    apelido = card.find_element_by_xpath('.//span').text
    
    try:
        username = card.find_element_by_xpath('.//span[contains(text(),"@")]').text
    except NoSuchElementException:
        return
    
    try:
        data_postagem = card.find_element_by_xpath('.//time').get_attribute('datetime')
    except NoSuchElementException:
        return
    
    try:
        img = card.find_element_by_xpath('.//div[2]/div[2]/div[2]//img[@class="css-9pa8cd"]')
        link_img = img.get_attribute("src")
    except NoSuchElementException:
        return
    
    respondendo = card.find_element_by_xpath('.//div[2]/div[2]/div[1]').text
    comentario = card.find_element_by_xpath('.//div[2]/div[2]/div[2]').text  
    
    comentarios_num = card.find_element_by_xpath('.//div[@data-testid="reply"]').text
    retweets_num = card.find_element_by_xpath('.//div[@data-testid="retweet"]').text
    curtidas_num = card.find_element_by_xpath('.//div[@data-testid="like"]').text
    
    tweet = (apelido, username, data_postagem, respondendo, comentario, link_img, comentarios_num, retweets_num, curtidas_num)
    return tweet

options = EdgeOptions()
options.use_chromium = True
options.headless = True
driver = Edge(options=options)

driver.get('https://twitter.com/search?q=vacina&src=typed_query')

driver.find_element_by_link_text('Mais recentes').click()

data = []
tweet_ids = set()
last_position = driver.execute_script("return window.pageYOffset;")
scrolling = True
scroll_attempt = 0
i = 0
while scrolling:
    page_cards = driver.find_elements_by_xpath('//div[@data-testid="tweet"]')
    for card in page_cards[-15:]:
        tweet = get_tweet_data(card)
        if tweet:
            tweet_id = ''.join(tweet)
            if tweet_id not in tweet_ids:
                tweet_ids.add(tweet_id)
                data.append(tweet)
            
    while i<50:
        i += 1
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        sleep(2)
        curr_position = driver.execute_script("return window.pageYOffset;")
        if last_position == curr_position:
            scroll_attempt += 1
            
            # end of scroll region
            if scroll_attempt == 3:
                scrolling = False
                break
            else:
                sleep(2)
        else:
            last_position = curr_position
            break
    if i == 50:
        scrolling = False


driver.close()


# #### Salvando dados como json

# In[34]:


js = json.dumps(data)
fp = open('vacine_tweets9.json', 'w')
fp.write(js)
fp.close()


# In[35]:


df = pd.read_json('vacine_tweets9.json')


# ##### Renomeado as colunas do DataFrame

# In[36]:


df.columns = ['Apelido','Username','Data/Hora','Respondendo','Texto', 'link_img','Comentarios','Retweets','Likes']


# #### Transformando arquivo JSON em CSV

# In[37]:


df.to_csv('vacine_tweets_csv9.csv', index=None,encoding='utf-8')


# ### Informações sobre o dataset

# ## Unindo datasets em um só

# In[14]:


df1 = pd.read_csv('vacine_tweets_csv6.csv')
df1


# In[15]:


df2 = pd.read_csv('vacine_tweets_csv9.csv')
df2


# In[16]:


frames = [df1, df2]


# In[17]:


df_final = pd.concat(frames)


# In[18]:


df_final.to_csv('vacine_tweets_completo1.csv', index=None,encoding='utf-8')


# In[19]:


df_final.shape


# In[21]:


df_final.head(-5)


# In[281]:


df_final.info()


# <b><i>Linhas na coluna texto que tem valor NaN</i><b>

# In[267]:


for i in range(len(df_final)):
    if (pd.isnull(df_final["Apelido"].iloc[i])):
        print("Null em index", i)


# In[268]:


for i in range(len(df_final)):
    if (pd.isnull(df_final["Texto"].iloc[i])):
        print("Null em index", i)


# In[269]:


for i in range(len(df_final)):
    if (pd.isnull(df_final["Respondendo"].iloc[i])):
        print("Null em index", i)


# In[270]:


for i in range(len(df_final)):
    if (pd.isnull(df_final["Comentarios"].iloc[i])):
        print("Null em index", i)


# In[271]:


for i in range(len(df_final)):
    if (pd.isnull(df_final["Retweets"].iloc[i])):
        print("Null em index", i)


# In[272]:


for i in range(len(df_final)):
    if (pd.isnull(df_final["Likes"].iloc[i])):
        print("Null em index", i)


# <b><i>Transformando NaN em zero</i><b>

# In[282]:


df_final['Apelido'] = df_final['Apelido'].fillna("")
df_final['Texto'] = df_final['Texto'].fillna("")
df_final['Respondendo'] = df_final['Respondendo'].fillna("")
df_final['Comentarios'] = df_final['Comentarios'].fillna(0)
df_final['Retweets'] = df_final['Retweets'].fillna(0)
df_final['Likes'] = df_final['Likes'].fillna(0)


# In[283]:


df_final.info()


# In[284]:


df_final.head(10)


# <b><i>Tentando consertar as colunas, Likes e Retweets removendo a palavra 'mil' para converter em float em seguida</i><b>

# In[285]:


for i, row in df_final.iterrows():
    r = row["Likes"].split()[0]
    #df_final["Likes"].iloc[i] = r
    print(i, r)


# In[286]:


df_final['Likes'].dtype


# <b><i>Consertando os índices</i></b>

# In[287]:


df_final.reset_index(level=0, drop=True, inplace=True)


# In[288]:


for index, row in df_final.iterrows() :
    print(index, row['Likes'], df_final["Likes"].dtype)


# In[289]:


for index, row in df_final.iterrows() :
    print(index, row['Retweets'], df_final["Retweets"].dtype)


# <b><i> Mudando manualmente valores de linhas </i><b>

# In[290]:


df_final["Likes"].iloc[3] = "1200"
df_final["Likes"].iloc[18] = "4200"
df_final["Likes"].iloc[41] = "1500"
df_final["Likes"].iloc[113] = "6900"

df_final["Retweets"].iloc[18] = "1100"


# <b><i> Convertendo as colunas Likes e Retweets em float64 </i><b>

# In[291]:


df_final.astype({'Likes': 'float64','Retweets':'float64'}).dtypes
df_final = df_final.astype({'Likes': 'float64','Retweets':'float64'})


# In[292]:


for index, row in df_final.iterrows() :
    print(index, row['Likes'], df_final["Retweets"].dtype)


# In[293]:


df_final.info()


# In[294]:


df_final.head(-5)


# In[ ]:


df_final.head(-5)

