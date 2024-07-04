"""
This script connects to a PostgreSQL database and performs python + sql logic on it.
Below is example of Whats and Hows.

Usage:
    python script_name.py <database_name>

Example:
    python3 test_psql.py database_name

Author:
    aksi@odoo.com
"""

import os
import sys
import psycopg2

def connect_to_db(db_name):
    """
    Connects to the PostgreSQL database.
    """
    try:
        conn = psycopg2.connect(
            database=db_name,
            host="localhost",
            user=os.environ.get('PGUSER'),
            password=os.environ.get('PGPASSWORD'),
            port=os.environ.get('PGPORT')
        )
        return conn
    except psycopg2.Error as e:
        print(f"Unable to connect to database: {e}")
        sys.exit(1)

def main():
    """
    Main function to execute the template script.
    """
    try:
        db_name = sys.argv[1]
    except IndexError:
        print("Error: Database name required.")
        sys.exit(1)

    conn = connect_to_db(db_name)
    """
    Example:
    Here, we update the translations in a specific database view, based on translation mappings provided in a dictionary.
    """
    translated_vals = {
        'de_CH': [{'source': '<strong>Due Date:</strong><br/>',
                    'value': '<strong>Fällig am:</strong>'},
                {'source': '<strong>Source:</strong><br/>',
                    'value': '<strong>Quelle:</strong>'}],
        'de_DE': [{'source': '<strong>Due Date:</strong><br/>',
                    'value': '<strong>Fällig am:</strong>'},
                {'source': '<strong>Source:</strong><br/>',
                    'value': '<strong>Quelle:</strong>'}],
    }

    view_id = 34
    try:
        cr = conn.cursor()

        replace_query = "arch_db::text"
        for items in translated_vals.values():
            for item in items:
                replace_query = f"replace({replace_query}, '{item['value']}', '{item['value']}<br/>')"
        cr.execute(f"UPDATE ir_ui_view SET arch_db = {replace_query}::jsonb WHERE id = %s",[view_id])
        conn.commit()

        print("Update successful.")
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error updating view: {e}")
    finally:
        cr.close()

    conn.close()
    print("Closed DB connection.")

if __name__ == "__main__":
    main()
