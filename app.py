from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.imdb.com/search/title/?release_date=2021-01-01,2021-12-31')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here

table = soup.find('div',attrs={'class':'lister list detail sub-list'})
find_row = table.findAll('div',attrs={'class':'lister-item mode-advanced'})
row_length = len(find_row)

temp = [] #initiating a list 

for i in range(1, row_length):
#insert the scrapping process here
    title = table.find_all('h3',attrs= {'class': 'lister-item-header'})[i]
    title = title.find('a').text
    
    rating = table.find_all('div',attrs= {'class': 'inline-block ratings-imdb-rating'})[i]
    rating = rating.find('strong').text
    
    metascore =table.find('span', attrs ={'class' : 'metascore'}).text.strip() if table.find('span', attrs ={'class' : 'metascore'}) else '0'

    value = table.find_all('p', attrs = {'class':'sort-num_votes-visible'})[i]
    votes = value.find('span', attrs = {'name': 'nv'}).text

    temp.append((title,rating,metascore,votes))

temp

#change into dataframe
imdb = pd.DataFrame(temp, columns = ('Film_Title','IMDB_Rating','Metascore','Votes'))

#insert data wrangling here

imdb['Votes'] = imdb['Votes'].str.replace(",","")
imdb['Votes'] = imdb['Votes'].astype('int64')
imdb['IMDB_Rating'] = imdb['IMDB_Rating'].astype('float64')
imdb['Metascore'] = imdb['Metascore'].astype('int64')
imdb['n_IMDB_Rating'] = imdb['IMDB_Rating']*10

imdb_ratingXmeta = imdb[((imdb['Metascore']!=0) & (imdb['n_IMDB_Rating']!=0))].loc[:,['Film_Title','Metascore','n_IMDB_Rating']].sort_values('n_IMDB_Rating',ascending=False)

imdb_ratingXmetascore = imdb_ratingXmeta.sort_values('n_IMDB_Rating',ascending=False).set_index('Film_Title')


#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{imdb_ratingXmetascore[["n_IMDB_Rating","Metascore"]].mean().round(2)}' #be careful with the " and ' 


	# generate plot
	ax = imdb_ratingXmetascore.head(7).plot(figsize = (15,5)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)