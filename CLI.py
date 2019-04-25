import sys
import requests
import pip
import argparse
import json
import urllib.parse
quote_plus = urllib.parse.quote_plus

parser = argparse.ArgumentParser()
#python CLI.py -u 35.226.71.167 -e md5 -a test -m GET
parser.add_argument('-u', '--api_ip', default="127.0.0.1", help="Sets IP for REST API")
parser.add_argument('-e', '--endpoint', default="/", help="Sets the endpoint to run against")
parser.add_argument('-a', '--request_argument', default="", help="Parameters to send on request")
parser.add_argument('-m', '--http_method', default="GET", help="Sets the browser method (GET, PUT, POST)")
args = parser.parse_args()

# Output the variables using
print "Using:"
print "* API IP: "+args.api_ip
print "* Endpoint: "+args.endpoint
print "* HTTP Method: "+args.http_method
print "* Request Argument: "+args.request_argument

# Check if endpoint is available
if  args.endpoint not in {"md5", "factorial", "fibonacci", "is-prime", "slack-alert", "kv-record", "kv-retrieve"}:
    (sys.exit("Incorrect Endpoint. Available endpoints are: md5, factorial, fibonacci, is-prime, slack-alert, kv-record, kv-retrieve. If you need help, rerun this program with -h."))

url = "http://"+args.api_ip+":5000/"+args.endpoint

if args.endpoint == "kv-record":
    if args.http_method.lower() == "post":
         resp = requests.post(url, json=json.parse(args.request_argument))
    elif args.http_method.lower() == "put":
         resp = requests.put(url, json=json.parse(args.request_argument))
    else:
        sys.exit("HTTP Method must be PUT or POST for kv-record. If you need help, rerun this program with -h.")
else:
    if args.http_method.lower() == "get":
        if args.request_argument == "":
            resp = requests.get(url)
        else:
            resp = requests.get(url+"/"+args.request_argument)
    else:
        sys.exit("HTTP method must be GET unless you are running against the KV-Record endpoint. If you need help, rerun this program with -h.")

print (resp.content)
