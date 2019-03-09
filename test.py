from flask import Flask,request

app = Flask(__name__)

@app.route("/")
def home():
	print dict(request.headers),type(request.headers)
	return "thank you"

if __name__ == '__main__':
	app.run('0.0.0.0',port=5000,debug=True)