# -- coding: utf-8 --
from simplexml import dumps
import simplexml
from flask import Flask, make_response, request, render_template
from flask_restful import Resource, Api, reqparse, abort
from xml.etree.ElementTree import fromstring
import datetime
import os
import requests
import LSTM.Classifier2

classList = []


app = Flask(__name__, template_folder='./static/')
api = Api(app, default_mediatype='application/xml')

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
		requestXmlRoot = fromstring(request.data)

		print(requestXmlRoot.find("jss").text)
		print(requestXmlRoot.find("option").find("startTerm").text)
		print(requestXmlRoot.find("option").find("headhunter").text)

		# print(LSTM.Classifier2.classify(requestXmlRoot.find("jss").text))

		industry = LSTM.Classifier2.classify(requestXmlRoot.find("jss").text)
		print(industry)
		url = "http://api.saramin.co.kr/job-search?keywords=" + industry + "&deadline=" + \
			  str((datetime.datetime.now()+datetime.timedelta(days=int(requestXmlRoot.find("option").find("startTerm").text))))	+ ""
		print(url)
		response = requests.get(url)

		tree = fromstring(response.text)
		# print(tree.find("jobs").findall("job")[0].find("company").find("name").attrib['href'])

		jobList  = tree.find("jobs").findall("job")

		trList = ""

		for job in jobList:
			jobLink = job.find("url").text
			companyName = job.find("company").find("name").text
			companyLink = job.find("company").find("name").attrib['href']
			startTime = str(datetime.datetime.fromtimestamp(int(job.find("opening-timestamp").text)))
			endTime = str(datetime.datetime.fromtimestamp(int(job.find("expiration-timestamp").text)))
			salary = job.find('salary').text

			position = job.find("position")
			title = position.find("title").text
			location = position.find("location").text
			industry = position.find("industry").text
			category = position.find("job-category").text
			req_exp = position.find("experience-level").text
			req_edu = position.find("required-education-level").text

			# print(jobLink)
			# print(companyName)
			# print(companyLink)
			# print(startTime)
			# print(endTime)
			# print(title)
			# print(location)
			# print(industry)
			# print(category)
			# print(req_exp)
			# print(req_edu)

			tr = "<tr>"
			tr += "<td>"
			tr += "<b><a target='_blank' href='"+jobLink+"'>"+title+"</a></b>"
			tr += "</td>"

			tr += "<td>"
			tr += "<a target='_blank' href='"+companyLink+"'>"+companyName+"</a>"
			tr += "</td>"

			tr += "<td>" + startTime + "</td>"
			tr += "<td>" + endTime + "</td>"
			tr += "<td>" + location + "</td>"
			if industry is not None:
				tr += "<td>" + industry + "</td>"
			if category is not None:
				tr += "<td>" + category + "</td>"
			tr += "<td>" + req_exp + "</td>"
			tr += "<td>" + req_edu + "</td>"
			tr += "<td>" + salary + "</td>"
			tr += "</tr>"
			trList += tr


		return trList

# api.add_resource(User, '/users')
api.representations['application/xml'] = output_xml

if __name__ == '__main__':
	app.run(debug=True, host="0.0.0.0", port=int(os.getenv('VCAP_APP_PORT', '10000')))