import http.server
import json
from urllib.parse import urlparse, parse_qs
from langchain.document_loaders import CSVLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.chat_models import ChatOpenAI
from processquery import CSVQueryProcessor
import constants
import os
import argparse
import csv
import sys

# gives api key
os.environ["OPENAI_API_KEY"] = constants.API_KEY

NICKNAME_FILE = "nickname_data.json"

CSV_FILES_DIR = "csv_files"

if not os.path.exists(CSV_FILES_DIR):
    os.makedirs(CSV_FILES_DIR)

class CSVQueryHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):

        query_params = parse_qs(urlparse(self.path).query)
        csv_filename = query_params.get('csv_filename', [''])[0]
        query = query_params.get('query', [''])[0]
        nickname = query_params.get('nickname', [''])[0]

        processor = CSVQueryProcessor()
        result = processor.process_query(csv_filename, query)

        # Store nickname information in the dictionary - write to disk and read back from it

        # each time any update happens write it out to disk, any updates are in the file
        # at the start first thing you do, read the dictionary in beginning in order to save it
        # provide a function, that returns the dictionary state
        

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        response_data = json.dumps({"result": result})
        self.wfile.write(response_data.encode())

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        post_data = json.loads(post_data)

        nickname = post_data.get('nickname', '')
        csv_data = post_data.get('csv_data', [])

        # Save CSV data on the server
        save_csv_data_on_server(nickname, csv_data)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        response_data = json.dumps({"message": "CSV data saved on server."})
        self.wfile.write(response_data.encode())

def save_csv_data_on_server(nickname, csv_data):
    filename = os.path.join(CSV_FILES_DIR, f"{nickname}.csv")
    with open(filename, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerows(csv_data)

def delete_csv_data_on_server(nickname):
    filename = os.path.join(CSV_FILES_DIR, f"{nickname}.csv")
    if os.path.exists(filename):
        os.remove(filename)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HTTP server for CSV queries.")
    parser.add_argument("port", type=int, help="Port number for the HTTP server.")
    args = parser.parse_args()

    PORT = args.port

    with http.server.HTTPServer(("", PORT), CSVQueryHandler) as httpd:
        print("Server started at port", PORT)
        httpd.serve_forever()
