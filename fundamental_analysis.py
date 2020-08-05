import argparse
import json
import os
import urllib.request

def printv(msg):
    if args.verbose:
        print(msg)

parser = argparse.ArgumentParser(description='Perform a fundamental analysis of a compagny')
parser.add_argument('symbol', type=str, help='The company symbol')
parser.add_argument('-k', '--apikey', type=str, help='Alpha Vantage API key', default='demo')
parser.add_argument('-u', '--update', action='store_true', default=False,
                    help='Update cached company data')
parser.add_argument('-v', '--verbose', action='store_true', default=False,
                    help='Show additional traces')

args = parser.parse_args()
# convert company symbol to uppercase
args.symbol = args.symbol.upper()

# create cache directory if it doesn't exit
cache_dir = './cache'
if not os.path.exists(cache_dir):
    printv('Creating cache folder')
    os.mkdir(cache_dir)

if args.update:
    # fetch company data
    response = urllib.request.urlopen("https://www.alphavantage.co/query?function=OVERVIEW&symbol=" + args.symbol + "&apikey=demo")
    data = json.load(response) 
    # store company data as json
    outfile = open(os.path.join(cache_dir, args.symbol + '.json'), 'w')
    json.dump(data, outfile, indent=4)
    printv('Successfuly downloaded company data')
else:
    printv('Getting cached company data')
    infile = open(os.path.join(cache_dir, args.symbol + '.json'))
    data = json.load(infile)

printv(data)