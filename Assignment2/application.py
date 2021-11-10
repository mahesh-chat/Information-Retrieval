from flask import Flask, render_template, request
from model import *

app = Flask(__name__,  template_folder='Frontend/',
            static_folder="Frontend/assets/")


@app.route('/', methods=["GET"])
def searchEngine():
    return render_template('index.html')


@app.route('/result', methods=["POST"])
def results():
    if request.method == "POST":
        searchTerm = request.form.get("search")
        try:
            if " and " in searchTerm.lower() or " or " in searchTerm.lower() or " not " in searchTerm.lower():
                heading = "Boolean Query"
                nonPosData = InfoRet.BoolRetrivalPos(searchTerm)
                PosData = InfoRet.BoolRetrivalPos(searchTerm)
            else:
                heading = "Single Phrase Query"
                nonPosData = InfoRet.searchNonPosIndex(searchTerm)
                PosData = InfoRet.searchPosIndex(searchTerm)
        except:
            return "No match found, Try queries like 'inverted' or 'index and inverted'"
    return render_template('results.html', searchTerm=searchTerm, nonPosData=nonPosData, PosData=PosData, heading=heading)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
