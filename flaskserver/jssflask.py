from simplexml import dumps
import simplexml
from flask import Flask, make_response, request, render_template
from flask_restful import Resource, Api, reqparse, abort
from xml.etree.ElementTree import fromstring
import os
import requests


app = Flask(__name__, template_folder='./static/')
api = Api(app, default_mediatype='application/xml')
# api.representations['application/xml'] = output_xml

classList = []

@app.route("/")
def index():
	return render_template("index.html")

@api.representation('application/xml')
def output_xml(data, code, headers=None):
	resp = make_response(dumps({'response':data}), code)
	resp.headers.extend(headers or {})
	return resp

@api.resource('/jss')
class User(Resource):
	def post(self):
		# json_data = request.get_json(force=True)

		# code = json_data['code']
		# classList.append({"name":name, "code":code})
		industry = "경영"
		url = "http://api.saramin.co.kr/job-search?keywords=" + industry
		response = requests.get(url)

		tree = fromstring(response.text)
		print(tree.find("jobs").findall("job")[0].find("company").find("name").attrib['href'])

		jobList  = tree.find("jobs").findall("job")

		tdList = []

		for job in jobList:
			companyName = job.find("company").find("name").text
			companyLink = job.find("company").find("name").attrib['href']


			td = "<td>"

			td += "</td>"


		return {'status': "success", "messcode": "insert class"}

# api.add_resource(User, '/users')



if __name__ == '__main__':
	import simplexml
	import requests

	industry = "경영"
	url = "http://api.saramin.co.kr/job-search?keywords=" + industry
	response = requests.get(url)

	dic = simplexml.loads(response.text)

	print(dic['job-search']['jobs']['job'][0])
	job = dic['job-search']['jobs']['job'][0]
	url = job['url']
	company = job['company']
	print(company)
	print("-----")
	companyname = company['name']
	print(companyname)
	#app.run(debug=True, host="0.0.0.0", port=int(os.getenv('VCAP_APP_PORT', '10000')))