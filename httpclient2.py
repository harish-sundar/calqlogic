from flask import Flask, render_template, request, redirect, url_for
import http.client
import json
import urllib.parse
import os
from io import StringIO
import csv


app = Flask(__name__)

# loads preloaded csv files
nicknames = []
csv_files_directory = "csv_files"
for filename in os.listdir(csv_files_directory):
    if filename.endswith(".csv"):
        nicknames.append(filename.replace(".csv", ""))

print(nicknames)

# checks csv format
def validate_csv_format(csv_data):
    try:
        csv_stream = StringIO(csv_data)
        csv_reader = csv.reader(csv_stream)

        header = next(csv_reader)
        if not header:
            return False

        for row in csv_reader:
            if len(row) != len(header):
                return False
            
        return True
    except Exception as e:
        return False

# Create a connection to the HTTP server to get a query result from GPT
def get_query_result(csv_filename, query, server_address, server_port):

    conn = http.client.HTTPConnection(server_address, server_port)

    params = urllib.parse.urlencode({"csv_filename": csv_filename, "query": query})

    url = f"/?{params}"

    conn.request("GET", url)

    response = conn.getresponse()

    result_data = json.loads(response.read())

    formatted_answer = result_data['result']

    conn.close()

    return formatted_answer

def save_csv_data_on_server(nickname, csv_data, server_address, server_port):
    conn = http.client.HTTPConnection(server_address, server_port)

    post_data = json.dumps({"nickname": nickname, "csv_data": csv_data})
    headers = {'Content-type': 'application/json'}

    conn.request("POST", "/", body=post_data, headers=headers)

    response = conn.getresponse()

    response_data = json.loads(response.read())

    conn.close()

    return response_data

# Function to convert the inputted String to CSV
def convert_string_to_csv(input_string):
    rows = input_string.strip().split('\n')

    csv_data = []

    for row in rows:
        csv_data.append(row.strip().split(','))

    return csv_data

# gets the user data and nickname to save it as an saves the data in server
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_data = request.form['user_data']
        nickname = request.form['nickname']

        if not nickname and not user_data:
            error_message = "No new CSV data provided."
            return render_template('error.html', error_message=error_message)
        if not nickname:
            error_message = "Please provide a name for dataset."
            return render_template('error.html', error_message=error_message)

        if nickname in nicknames:
            error_message = "Dataset already exists."
            return render_template('error.html', error_message=error_message)

        if user_data:
            if not validate_csv_format(user_data):
                error_message = "Invalid CSV format. Please make sure the data is comma-separated and consistent."
                return render_template('error.html', error_message=error_message)
             
            csv_data = convert_string_to_csv(user_data)
            server_address = "127.0.0.1"
            server_port = 8001

            save_csv_data_on_server(nickname, csv_data, server_address, server_port)
            nicknames.append(nickname)

        return redirect(url_for('query', nickname=nickname))
    
    return render_template('index1.html')

# gets the nickname for csv and query and provides an answer using api
@app.route('/query', methods=['GET', 'POST'])
def query():
    if request.method == 'POST':
        nickname = request.form['nickname']
        user_query = request.form['query']

        server_address = "127.0.0.1"
        server_port = 8001 

        if nickname in nicknames:
            csv_filename = f"{nickname}.csv"
            query_result = get_query_result(csv_filename, user_query, server_address, server_port)
            return render_template('results.html', query=user_query, result=query_result)
        else:
            error_message = "CSV data not found for the given name."
            return render_template('error.html', nickname=nickname, error_message=error_message)

    return render_template('index2.html', nickname=request.args.get('nickname'))

# shows a page to delete a csv
@app.route('/delete', methods=['GET'])
def show_delete_page():
    return render_template('delete.html')

# deletes a csv and sends info to server
@app.route('/delete', methods=['POST'])
def delete():
    nickname = request.form['nickname']
    if nickname in nicknames:
        csv_filename = f"{nickname}.csv"
        csv_files_directory = "csv_files"

        file_path = os.path.join(csv_files_directory, csv_filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            nicknames.remove(nickname)
            return redirect(url_for('view_data'))
        else:
            error_message = "Dataset not found for deletion."
            return render_template('error.html', error_message=error_message)

    return redirect(url_for('query', nickname=nickname))

# views all datasets
@app.route('/view_data', methods=['GET'])
def view_data():
    return render_template('data.html', nicknames=nicknames)


if __name__ == "__main__":
    app.run()
