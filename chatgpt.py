import os
import sys
import argparse
import constants
from langchain.document_loaders import TextLoader
from langchain.document_loaders import CSVLoader
from langchain.document_loaders import DirectoryLoader

from langchain.indexes import VectorstoreIndexCreator
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI

os.environ["OPENAI_API_KEY"] = constants.API_KEY

def main(csv_filename, query):
    loader = CSVLoader(csv_filename)
    index = VectorstoreIndexCreator().from_loaders([loader])

    print(index.query(query, llm=ChatOpenAI()))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="script to query CSV data using langchain.")
    parser.add_argument("csv_filename", help="name of csv file")
    parser.add_argument("query", help="query for csv file")
    args = parser.parse_args()

    main(args.csv_filename, args.query)
