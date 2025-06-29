#!/usr/bin/env python3
"""
Check the actual structure of the captions database.
"""

import sqlite3
import os

def check_database():
    db_path = "captions.db"
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} does not exist")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # List all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"Database: {db_path}")
        print(f"Tables found: {len(tables)}")
        print("-" * 40)
        
        for table in tables:
            table_name = table[0]
            print(f"\nTable: {table_name}")
            
            # Get table schema
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE name='{table_name}';")
            schema = cursor.fetchone()
            if schema:
                print(f"Schema: {schema[0]}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"Row count: {count}")
            
            # Show sample data
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
                sample_rows = cursor.fetchall()
                
                # Get column names
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                col_names = [col[1] for col in columns]
                
                print(f"Columns: {col_names}")
                print("Sample data:")
                for i, row in enumerate(sample_rows):
                    print(f"  Row {i+1}: {row}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    check_database()