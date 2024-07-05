import argparse
import subprocess
import os, psycopg2



""""
Script is made such that, by passing relevant option ,it will restore the both production and upgraded (if available) database and
set english language as active language for us. 
usage 1:
        Restore both databases
        options : 
            -r : request id 
            -n : host, example : me1, am1, as1, none if product master
            -d : name example  :tax , so final db name would be user_tax  
            -x : restoreoption : more control over restore , pass 0 to restore prod db, 1 to restore upg db, else, both db will be restored
        example:
            python3 restore_en.py -r 1478682 -d test -n me1
            Above command will resote both dbs for request id 1478682 and set english as active language.
        
usage 2: set english language in already restored database 
        example : python3 restore_en.py -o <database_name>
"""

def restore_db(cmd):
    try:
        subprocess.run(cmd.split(), check=True)
        return 1
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {cmd}")
        print(e)
        return 0

def _connect_db(db):
    conn = psycopg2.connect(database=db,
                            host="localhost",
                            port=os.environ.get('PGPORT'))
    return conn

def set_eng_lang(dbname):
    conn = _connect_db(dbname)
    cr = conn.cursor()

    try:
        cr.execute("""
                UPDATE res_lang
                SET active = 't'
                WHERE code = 'en_US';
            """)
        cr.execute("""UPDATE res_partner
                        SET lang = 'en_US'
                        WHERE id IN (
                            SELECT partner_id
                            FROM res_users
                            WHERE id = (
                                SELECT MIN(r.uid)
                                FROM res_groups_users_rel r
                                JOIN res_users u ON r.uid = u.id
                                WHERE u.active
                                AND r.gid = (
                                    SELECT res_id
                                    FROM ir_model_data
                                    WHERE module = 'base'
                                    AND name = 'group_system'
                                )
                            )
                        )
                    """)
        conn.commit()
        print("English language set!!! ")
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cr.close()
        conn.close()

def restore_and_set_eng(cmd):
    print("executing  :", cmd ,"\n")
    x = restore_db(cmd)
    if x:
        set_eng_lang(cmd.split()[-1])  

def get_restore_command(args):
    user = os.environ.get('USER')
    NAME = user +'_' + args.name if args.name else user + '_' + args.request
    CODE = "-n "+ args.code if args.code else ''
    prod_db = f"odoo-upgrade-restore-request {args.request} {CODE} -d {NAME}"
    upg_db = f"odoo-upgrade-restore-request {args.request} {CODE} -u -d {NAME}_upg"
    return prod_db,upg_db

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--request", help="request id")
    parser.add_argument("-n", "--code", help="server host")
    parser.add_argument("-d", "--name", help="name for database")
    parser.add_argument("-x", "--restoreoption", type=int, help="pass 0 to restore prod db, 1 to restore upg db, else both db will be restored")
    parser.add_argument("-o", "--dbname", help="Set english language for restored database")
    args = parser.parse_args()

    if args.dbname:
        set_eng_lang(args.dbname)
    else:
        if not args.request:
            print("Request id is required for restoring database.")
            return
        restore_commands = get_restore_command(args)
        if args.restoreoption is not None  and args.restoreoption in (0,1):
            opt = args.restoreoption
            restore_and_set_eng(restore_commands[opt])
        else:
            for cmd in restore_commands:
                restore_and_set_eng(cmd)

if __name__ == "__main__":
    main()
