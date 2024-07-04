import os, sys, psycopg2
from pprint import pprint
import json


try:
    db = sys.argv[1]
except IndexError:
    print("requires DB name")
    exit()

conn = psycopg2.connect(database=db,
                        host="localhost",
                        user=os.environ.get('PGUSER'),
                        password=os.environ.get('PGPASSWORD'),
                        port=os.environ.get('PGPORT'))

cr = conn.cursor()

try:  
    # Sample dictionary
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
    replace_query = "arch_db::text"
    for items in translated_vals.values():
        for item in items:
            replace_query = f"replace({replace_query}, '{item['value']}', '{item['value']}<br/>')"

    cr.execute(f"UPDATE ir_ui_view SET arch_db = {replace_query}::jsonb WHERE id = %s",[view_id])
    
except Exception as e:
    conn.rollback()
    print(f"Error: {e}")
finally:
    print("\n closing DB connection ")
    cr.close()
    conn.close()
   