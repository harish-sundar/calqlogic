from flask import Flask, render_template, request
from pprint import pprint
import http.client
import json
import urllib.parse
import csv

app = Flask(__name__)


def get_query_result(csv_filename, query, server_address, server_port):
    # Create a connection to the HTTP server
    conn = http.client.HTTPConnection(server_address, server_port)

    # Prepare the query parameters
    params = urllib.parse.urlencode({"csv_filename": csv_filename, "query": query})

    # Construct the complete URL with the path and query parameters
    url = f"/?{params}"

    # Make a GET request to the server
    conn.request("GET", url)

    # Get the response from the server
    response = conn.getresponse()

    # Read and parse the response data as JSON
    result_data = json.loads(response.read())

    # prints only the result
    formatted_answer = result_data['result']

    # Close the connection to the server
    conn.close()

    return formatted_answer

# Function to convert the inputted String to CSV

def convert_string_to_csv(input_string):
    # Split the input string into rows based on newline character
    rows = input_string.strip().split('\n')

    # Create a list to hold the rows of CSV data
    csv_data = []

    # Write each row to the CSV data list, removing newline characters
    for row in rows:
        csv_data.append(row.strip().split(','))

    return csv_data

@app.route('/', methods=['GET', 'POST'])

def index():
    if request.method == 'POST':
        # Get user input from the form
        user_data = request.form['user_data']

        # Convert the user input to CSV format
        csv_data = convert_string_to_csv(user_data)

        # Save the CSV-formatted data to a file
        output_file = "output.csv"

        # Write rows to a CSV file
        try:
            with open(output_file, 'w', encoding='utf-8', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerows(csv_data)

            print(f"CSV data has been saved to {output_file}.")
        except Exception as e:
            print(f"Error occurred while saving the CSV data: {e}")

        # Ask for a query
        query = request.form['query']

        # Server address and port
        server_address = "127.0.0.1" 
        server_port = 8000 

        # Get the result from the server
        result = get_query_result(output_file, query, server_address, server_port)

        # Render the results template
        return render_template('results.html', query=query, result=result)

    return render_template('index.html')

if __name__ == "__main__":
   app.run()
