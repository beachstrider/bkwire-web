import os
import subprocess
from subprocess import Popen, PIPE
import boto3
import argparse

#Setup flags here
parser = argparse.ArgumentParser(
    description='Daily Pacer Download Service',
    epilog='Example: python daily_import_v3.py')

parser.add_argument("--db-backup",
                    dest='dbd',
                    help="Create a database backup and store in S3",
                    required=False,
                    action='store_true')

parser.add_argument("--db-import",
                    dest='dbi',
                    help="Download database backup from S3 and import to target DB",
                    required=False,
                    action='store_true')                    
args = parser.parse_args()

class dbDump:
    def __init__(dself):
        dself.mysql_db_user = os.environ['MYSQL_DB_USER']
        dself.mysql_db_password = os.environ['MYSQL_DB_PASSWORD']
        dself.mysql_db_host = os.environ['MYSQL_DB_HOST']
        dself.mysql_db_database = os.environ['MYSQL_DB_DATABASE']
        dself.mysql_db_host_backup = 'prd-db-bpwa.cfssvqzbjpuu.us-west-2.rds.amazonaws.com'
        dself.filename = 'mysql_db_backup_prd.sql.gz'

    def db_dump(dself):
        #  mysqldump
        f = open(dself.filename, 'w+')
        
        table_ignore_names = ['users', 'bankruptcies_watchlist', 'companies_watchlist', 'user_notifications', 'user_industries']
        table_ignore = " ".join(f"--ignore-table={dself.mysql_db_database}.{str(item)}" for item in table_ignore_names)
        p1_args = ['mysqldump', '-h', dself.mysql_db_host_backup, '-u', dself.mysql_db_user, '-p'+dself.mysql_db_password, table_ignore, dself.mysql_db_database]

        try:
            pipe1 = Popen(p1_args, stdout=PIPE)
            
            p2_args = ['gzip', '-9']
            pipe2 = Popen(p2_args, stdin=pipe1.stdout, stdout=f)

            pipe2.wait()
            pipe1.wait()
        
            print(f"[+] Creating File: {dself.filename}")
        except Exception as e:
            print(f"Database backup failed: {e}")

    def db_import_dump(dself):
        filename = 'mysql_db_backup_prd.sql'
        #  mysqldump
        command = f"mysql -h {dself.mysql_db_host} -u {dself.mysql_db_user} -p{dself.mysql_db_password} {dself.mysql_db_database} < {filename}"
        try:
            out = subprocess.run(f"gunzip {dself.filename}", shell=True)
            print(out)
            print(f"[+] File Unzipped: {filename}")
        except Exception as e:
            print(f"Database Unzip failed: {e}")
            exit(1) 
            
        try:
            with open("mysql_db_backup_prd.sql", "r") as f:
                lines = f.readlines()
            with open("mysql_db_backup_prd.sql", "w") as f:
                for line in lines:
                    if line.strip() == "SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;":
                        pass
                    elif line.strip() == "SET @@SESSION.SQL_LOG_BIN= 0;":
                        pass
                    elif line.strip() == "SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ '';":
                        pass
                    else:
                        f.write(line)
            print(f"SQL File edit success")
        except Exception as e:
            print(f"SQL File edit failed: {e}")

        try:
            out = subprocess.run(command, shell=True)
            print(out)

            print(f"[+] Database Import success: {filename}")
        except Exception as e:
            print(f"Database Import failed: {e}")
            exit(1)

        os.remove(filename)

class awsS3transfer:
    def __init__(aself):
        aself.aws_key = os.environ['AWS_ACCESS_KEY_ID']
        aself.aws_secret = os.environ['AWS_SECRET_ACCESS_KEY']
        aself.mysql_bucket = 'prd-bkwire-db-backup'
        aself.mysql_db_database = os.environ['MYSQL_DB_DATABASE']
        aself.filename = 'mysql_db_backup_prd.sql.gz'

    def upload_backup_to_s3(aself):
        # Upload the file
        print("[+] Uploading S3 File")
        s3_client = boto3.client('s3', aws_access_key_id=aself.aws_key, aws_secret_access_key=aself.aws_secret)
      
        file_name = aself.filename
        obj_name = file_name
        try:
            s3_client.upload_file(file_name, aself.mysql_bucket, obj_name)
        except Exception as e:
            print(e)
            return False
        print("[+] Complete")

        print("[+] Cleaning up")
        os.remove(aself.filename)
        return True

    def download_backup_from_s3(aself):
        # Upload the file
        print("[+] Downloading S3 File")
        s3_client = boto3.client('s3', aws_access_key_id=aself.aws_key, aws_secret_access_key=aself.aws_secret)
      
        file_name = aself.filename
        obj_name = file_name
        try:
            s3_client.download_file(aself.mysql_bucket, obj_name, file_name)
        except Exception as e:
            print(e)
            return False
        print("[+] Complete")

        return True

def database_backup():
    print(f"[+] Starting DB Backup...")
    db1 = dbDump()
    db1.db_dump()    
    aws1 = awsS3transfer()
    aws1.upload_backup_to_s3()

def database_import():
    print(f"[+] Starting DB Import...")
    aws1 = awsS3transfer()
    aws1.download_backup_from_s3()

    # Import backup
    db1 = dbDump()
    db1.db_import_dump()    
        
def main():
    if args.dbd:
        database_backup()
    if args.dbi:
        database_import()


# MAIN
if __name__ == '__main__':
    main()
