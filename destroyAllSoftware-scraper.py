# -*- coding: utf-8 -*-
#!/usr/bin/env python
'''
	
	Dependencies
		- requests (pip install requests)
		- BeautifulSoup (pip install bs4)

	Use a virtual environment if you can.

	IMPORTANT NOTES:
		- Please refactor and modularize code if using in production. 
		- Make ample use of try/except
		- Keep in mind scraped web text is utf-8 encoding
		- Your OS may not support file names with special characters so make changes if needed


		- Code below is not optimized (for lack of time). Pls submit PR with changes and optimizations
	
	© 2018 **********
'''

import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://www.destroyallsoftware.com'
SCREENCAST_URL = 'https://www.destroyallsoftware.com/screencasts/catalog'

#grab the catalogue page html
request = requests.get(SCREENCAST_URL)
html = request.text

#Iniitialise bs4 with html.parser
#beautiful soup basically takes the raw html and creates virtual DOM-like tree out of it to make queries fast
soup = BeautifulSoup(html, 'html.parser')

#find all <a> tags in the page because that leads to the video page
headlines = soup.find_all('a')

#count variable is unnecessary but using to keep track of number of videos
count = 0

'''
	There are over 100 <a> tags on the page but we need only the special ones which lead to the videos.
	Check the page source in dev console to see why
'''
for h in headlines:
	
	#grab the relative url by reading href attribute
	href = h.get('href')
	
	#this check CAN be made better.
	if 'catalog' in str(href) and str(href) != '/screencasts/catalog':
		count += 1

		#The variable names below can be made more readable and relevant

		#create a request to grab the html of the video page
		new_req = requests.get(BASE_URL + str(href))
		new_html = new_req.text
		new_soup = BeautifulSoup(new_html, 'html.parser')

		#find the text of the <h2> tags. This will be our filename for the mp4 video and accompanying text file
		headline = new_soup.find('h2').text

		#since the headline will be used as filename, your OS may not allo some of these special characters. 
		headline = headline.replace('/', '-')
		headline = headline.replace(',', '-')
		headline = headline.replace(':', '-')

		
		#Grab the text occuring below every video. See the page source in dev console so see my why I chose class="details"
		snippet = new_soup.find("div", {"class": "details"})
		snippet_text = snippet.find_next('p').text

		#text file filename. The video file will have same name except with mp4 extention.
		fname_text = headline + ".txt"

		#open text file in 'w' write mode and dump the snippet text into it. UTF-8 encoding to handle special characters
		with open(fname_text, 'w') as f:
			f.write(snippet_text.encode('utf-8'))


		#The code below is for downloading he videos. 

		'''
			If you the page source, the developer has. not included the video source in the <video> tag.
			He/She adds the video url on page load to prevent scrapers from getting the URL.
			The url is thus hidden in the <script> tag. 
			Using python string find to get the url
		'''
		
		#The URL starts immediately after 'source.src = "''....Grabbing the start index
		start = new_html.find('source.src = "')
		#Grab the end index of the URL
		end = new_html.find('";', start, len(new_html))

		#URL is from [start + len(source.src = "), end]
		vid_url =  new_html[start+14:end]
		
		#make a GET request to fetch the video data
		video_data = requests.get(vid_url)

		#download the video by opening a file in 'write binary' mode
		fname_video = headline +'.mp4'
		with open(fname_video, 'wb') as f:
			for chunk in video_data:
				f.write(chunk)
		
		