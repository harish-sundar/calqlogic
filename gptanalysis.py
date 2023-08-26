import http.server
import socketserver
import os
import argparse
import constants
from langchain.document_loaders import CSVLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.chat_models import ChatOpenAI
import json
from urllib.parse import urlparse, parse_qs

os.environ["OPENAI_API_KEY"] = constants.API_KEY

def main():
    parser = argparse.ArgumentParser(description="script to query CSV data using langchain.")
    parser.add_argument("csv_filename", help="name of csv file")
    parser.add_argument("query", help="query for csv file")
    args = parser.parse_args()

    # Use the query_csv function to query the CSV data and get the result
    result = query_csv(args.csv_filename, args.query)

    # Print the result
    print(result)

def run_server(port=8000):
    class CustomHTTPHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory="./", **kwargs)

        def do_GET(self):
            QueryHandler(self.rfile, self.wfile, self).handle()

    with socketserver.TCPServer(("", port), CustomHTTPHandler) as httpd:
        print(f"Serving at port {port}")
        httpd.serve_forever()


if __name__ == "__main__":
    run_server()
