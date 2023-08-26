import http.server
import socketserver
import json
from urllib.parse import urlparse, parse_qs
from langchain.document_loaders import CSVLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.chat_models import ChatOpenAI
import os
import argparse
import constants

os.environ["OPENAI_API_KEY"] = constants.API_KEY

class CSVQueryProcessor:
    def process_query(self, csv_filename, query):
        loader = CSVLoader(csv_filename)
        index = VectorstoreIndexCreator().from_loaders([loader])
        result = index.query(query, llm=ChatOpenAI())
        return result

class CSVQueryHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Extract the query string from the request URL
        query_string = urlparse(self.path).query

        # Get the parameters from the query string
        query_params = parse_qs(query_string)
        csv_filename = query_params.get('csv_filename', [''])[0]
        query = query_params.get('query', [''])[0]

        # Create an instance of CSVQueryProcessor
        processor = CSVQueryProcessor()

        # Process the query using CSVQueryProcessor
        result = processor.process_query(csv_filename, query)

        # Send response to the client
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        # Send the result as JSON in the response
        response_data = json.dumps({"result": result})
        self.wfile.write(response_data.encode())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "HTTP server for CSV queries.")
    parser.add_argument("port", type = int, help = "Port number for the HTTP server.")
    args = parser.parse_args()

    # Start the HTTP server
    PORT = args.port

    with socketserver.TCPServer(("", PORT), CSVQueryHandler) as httpd:
        print("Server started at port", PORT)
        httpd.serve_forever()
