import pandas as pd
import pymongo
import json
import certifi

def csv_to_mongodb(csv_file_path, database_name, collection_name, connection_string):
    try:
        # Read CSV file
        print("Reading CSV file...")
        df = pd.read_csv(csv_file_path)
        
        # Convert DataFrame to list of dictionaries
        records = df.to_dict('records')
        
        # Connect to MongoDB using TLS/SSL certificate
        client = pymongo.MongoClient(
            connection_string,
            tlsCAFile=certifi.where(),  # Add SSL certificate
            connect=False
        )
        
        # Test the connection
        print("Testing database connection...")
        client.admin.command('ping')
        print("Successfully connected to MongoDB!")
        
        db = client[database_name]
        collection = db[collection_name]
        
        # Insert documents
        print("Inserting records...")
        result = collection.insert_many(records)
        print(f"Successfully inserted {len(result.inserted_ids)} documents")
        
        # Close connection
        client.close()
        print("MongoDB connection closed")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Error type:", type(e).__name__)

if __name__ == "__main__":
    # Make sure your connection string includes all required parameters
    CONNECTION_STRING = "mongodb+srv://AliZamanKhan:AliZaman15@cluster0.fuhk5.mongodb.net/?retryWrites=true&w=majority"
    CSV_FILE_PATH = r"C:\Users\aliza\Desktop\Cash Hisotry.csv"
    DATABASE_NAME = "New"
    COLLECTION_NAME = "Cash History"
    
    print("Starting import process...")
    csv_to_mongodb(CSV_FILE_PATH, DATABASE_NAME, COLLECTION_NAME, CONNECTION_STRING)
    print("Process completed!")