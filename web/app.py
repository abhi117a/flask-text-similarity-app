from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import spacy
import bcrypt

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.SimilarityDB
users = db["Users"]


class verifyData:
    def checkData(self, postData):
        if postData["uname"] != "" and postData["pword"] != "":
            return True
        else:
            return False

    def validateUser(self, postData):
        if users.find({"userName": postData["uname"]}).count != 0:
            return False
        else:
            return True

    def verifyPassword(self, postData):
        passWord = users.find({
            "userName": postData["uname"]
        })[0]["pword"]
        if passWord==postData["pword"]:
            return True

    def countTokens(self,postData):
        tokens = users.find({
            "userName": postData["uname"]
        })[0]["tokens"]
        return tokens

class Register(Resource):
    def post(self):
        postData = request.get_json()
        if verifyData.checkData(self, postData):
            if verifyData.validateUser(self, postData):
                users.insert({
                    "userName": postData["uname"],
                    "password": postData["pword"],
                    "tokens": 6
                })
                retJson = {"status": 200,
                           "Username": postData["uname"],
                           "message": "user is created"}
                return jsonify(retJson)
        else:
            retJson = {
                "status": 300,
                "message": "Data Incorrect cannot register user"
            }
            return jsonify(retJson)


class Detect(Resource):
    def post(self):
        postData = request.get_json()

        if verifyData.verifyPassword(self, postData):
            pass
        else:
            retJson = {"status": 301,
                       "message": "Wrong password"}
            return jsonify(retJson)
        if verifyData.countToken(postData["tokens"])<=0:
            retJson = {
                "status": 301,
                "message": "not enough tokens"
            }
            return jsonify(retJson)

        nlp = spacy.load("en_core_web_sm")
        text1 = nlp(postData["text1"])
        text2 = nlp(postData["text2"])

        ratio = text1.similarity(text2)
        retJson = {
            "status": 200,
            "similarity": ratio,
            "message": "success"
        }
        current_tokens = verifyData.countTokens(postData)
        users.update({
            "Username": postData["uname"]},
            {
            "$set": {
                "tokens": current_tokens-1
            }
        })
        return jsonify(retJson)


api.add_resource(Register, "/signup")
api.add_resource(Detect, "/detect")

if __name__ == "__main__":
    app.run()
