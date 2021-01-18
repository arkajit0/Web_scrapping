from flask import Flask, render_template, request,jsonify
# from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
# import pymongo

app = Flask(__name__)

@app.route('/', methods=['GET'])
def homepage():
    return render_template('index.html')

@app.route('/scrapping', methods=['POST'])
def review_scrap():
    if request.method == 'POST':
        search_product = request.form['product'].replace(" ","")
        try:
            flipkart_url = "https://www.flipkart.com/search?q=" + search_product
            uclient = uReq(flipkart_url)
            flipkart_page = uclient.read()
            uclient.close()
            flipkart_html = bs(flipkart_page, 'html.parser')

            bigboxes = flipkart_html.findAll("div", {"class": "_2pi5LC col-12-12"})
            product_link = "https://www.flipkart.com" + bigboxes[2].div.div.div.a['href']

            prodRes = requests.get(product_link)
            prod_html = bs(prodRes.text, "html.parser")

            review_product = prod_html.find_all("div", {"class": "col JOpGWq"})
            review_product_link = "https://www.flipkart.com" + review_product[0].findAll("a", href=True)[-1]['href']

            reviewRes = requests.get(review_product_link)
            review_html = bs(reviewRes.text, "html.parser")

            review_boxes = review_html.findAll("div", {"class": "_1AtVbE col-12-12"})
            review = []

            # client = pymongo.MongoClient("")
            # db = client.Project_Scrapping
            # COLLECTION_NAME = "Product_Reviews"
            # collection = db[COLLECTION_NAME]
            for reviews in review_boxes[4:]:
                try:
                    name = reviews.findAll("p", {"class": "_2sc7ZR _2V5EHH"})[0].text
                except:
                    name = ''
                try:
                    rating = reviews.findAll("div", {"class": "_3LWZlK _1BLPMq"})[0].text

                except:
                    rating = 'No Rating'

                try:
                    commentHead = reviews.findAll("p", {"class": "_2-N8zT"})[0].text
                except:
                    commentHead = 'No Comment Heading'
                try:
                    custComment = reviews.findAll("div", {"class": "t-ZTKy"})[0].text
                except:
                    custComment = 'No Customer Comment'

                mydict = {"Product": search_product, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}  # saving that detail to a dictionary
                # x = table.insert_one(mydict) #insertig the dictionary containing the rview comments to the collection
                if mydict == {"Product": search_product, "Name": '', "Rating": 'No Rating', "CommentHead": 'No Comment Heading',
                          "Comment": 'No Customer Comment'}:
                    pass
                else:
                    review.append(mydict)  # appending the comments to the review list
            # review_results = collection.insert_many(review)
            return render_template('results.html', review=review)
        except:
            return "something went wrong"

if __name__ == '__main__':
    app.run(debug=True)
