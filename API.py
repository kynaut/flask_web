import os
import subprocess
import socket
import hashlib
import math
import json
import requests
from redis import Redis, RedisError
from hashlib import md5
from flask import Flask, request, jsonify

app = Flask(__name__)

def hostname_resolves(hostname):
    try:
        socket.gethostbyname(hostname)
        return 1
    except socket.error:
        return 0

try:
	if  hostname_resolves('rediscontainer') == 1:
		print("Attempting to connect to docker redis")
		r = Redis(host="rediscontainer", port=6379)
	else:
		print("Attempting to connect to localhost redis")
		r = Redis(host="localhost", port=6379)
except:
	print("Failed to connect to redis")

#Index page
@app.route("/")
def hello():
    html = "<h3>Hello {name}!</h3>" \
        "<b>Hostname:</b> {hostname}<br/r>"
    return html.format(name='world', hostname='localhost') 

# Factorial
def fact(n):    
    if n > 0:
        return n * fact(n-1)
    else: 
        return 1
@app.route("/factorial/<string:user_input>")
def factorial_resp(user_input):
    try:
        converted_int = int(user_input)                 #Flask cannot handle negative integer input by default, accept input as string then convert to int to handle negative values
    except ValueError:                                  
        return "Invalid input. No integer detected."    #handles input validation for non-number input
    if converted_int >= 0:
        return jsonify(
            input = converted_int,
            output = fact(converted_int)
        )
    else:
        return "Invalid input. Must be a non-negative integer."                          #handles input validation to ensure positive integer input
        
# MD5
@app.route('/md5/<string:string>', methods=['GET'])
def getMD5(string):
    md5Hash = hashlib.md5(str(string).encode('utf-8')).hexdigest()
    return jsonify({'input':string, 'output':md5Hash})

# Fibonacci
@app.route('/fibonacci/<string:xy>', methods=['GET'])
def fibonacci(xy):
    try:
        x = int(xy)
        if x >= 0:
            a = 0
            b = 1
            fib_array = [a,b]
        
            while b <= x:
                a,b = b, a+b
                fib_array.append(b)
        
            fib_array = fib_array[:-1]
        
        elif x < 0:                                                                         #handles input validation to ensure positive integer input
            return jsonify("Error! Please enter a number greater than 0.")              
        
        return jsonify({'input':x, 'output':fib_array})
    except Exception as e:
        return jsonify("Error! Please enter a whole number greater than 0.")

# Is this digit prime?
def is_prime(n):
  if n == 2 or n == 3: return True
  if n < 2 or n%2 == 0: return False
  if n < 9: return True
  if n%3 == 0: return False
  r = int(n**0.5)
  f = 5
  while f <= r:
    if n%f == 0: return False
    if n%(f+2) == 0: return False
    f +=6
  return True
@app.route('/is-prime/<string:input_int>')
def prime_check(input_int):
    try:
        converted_int = int(input_int)                 #Flask cannot handle negative integer input by default, accept input as string then convert to int to handle negative values
    except ValueError:                                  
        return "Invalid input. No integer detected."    #handles input validation for non-number input
    if converted_int >= 0:
        return jsonify(
            input = converted_int,
            output = is_prime(converted_int)
        )
    else:
        return "Invalid input. Must be a non-negative integer."                          #handles input validation to ensure positive integer input

# Slack Alert
@app.route('/slack-alert/<string:msg>', methods=['GET'])
def post_to_slack(msg):
    webhook_url = 'https://hooks.slack.com/services/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'
    data = {'text': msg}
    response = requests.post(webhook_url, data=json.dumps(
        data), headers={'Content-Type': 'application/json'})

    if response.status_code != 200:
        raise ValueError(
            'Request to slack returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )
    
    return ("\"%s\" was posted in the #hewasnumber1 Slack Channel" % msg)

@app.route('/kv-record', methods=['POST', 'PUT'])
def kv_record():

    #Initialize JSON payload
    _JSON = {                                                           
        'key': None,
        'value': None,
        'result': False,
        'error': None
    }

    #Decode JSON payload from post request, check for valid payload syntax
    try:                                                                
        data = request.data.decode('utf-8')
        payload = json.loads(data)
        _JSON['key'] = payload['key']
        _JSON['value'] = payload['value']
    except:
        _JSON['error'] = "Missing or malformed JSON in client request."
        return jsonify(_JSON), 400

    #Update Redis DB with new kv pair
    if request.method == 'POST' or request.method == 'PUT':

        if r.set(_JSON['key'], _JSON['value']) == False:
            _JSON['error'] = "There was a problem creating the value in Redis."
            return jsonify(_JSON), 400
        else:
            _JSON['result'] = True
            return jsonify(_JSON), 200

# Retrieve value of a given key
@app.route('/kv-retrieve/<string:key>', methods=['GET'])
def kv_retrieve(key):

    # Initialize JSON Values
    payload = {
        'Input': key,
        'result': False,
        'error': 'N/A'
    }

    # Verify server accessible
    try:
        test_value = r.get(key)
    except RedisError:
        payload['error'] = "Cannot connect to redis."
        return jsonify(payload), 400

    # Verify value exists or return a 404 error
    if test_value == None:
        payload['error'] = "Key does not exist."
        return jsonify(payload), 404
    else:
        payload['Value'] = test_value.decode("utf-8")

    #Return payload with key/value pair
    payload['result'] = True
    return jsonify(payload), 200

   

app.debug = True
app.run(host='0.0.0.0', port=5000)
