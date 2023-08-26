import os
import argparse
import constants
from langchain.document_loaders import TextLoader
from langchain.document_loaders import CSVLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI

os.environ["OPENAI_API_KEY"] = constants.API_KEY

class CSVQueryProcessor:
    def process_query(self, csv_filename, query):
        loader = CSVLoader(csv_filename)
        index = VectorstoreIndexCreator().from_loaders([loader])
        result = index.query(query, llm=ChatOpenAI())
        return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="script to query CSV data using langchain.")
    parser.add_argument("csv_filename", help="path to csv file")
    parser.add_argument("query", help="query for csv file")
    args = parser.parse_args()

    processor = CSVQueryProcessor()
    result = processor.process_query(args.csv_filename, args.query)
    print(result)  # Display the result of the query
