# import getpass
import oracledb
import os
import csv
import configparser

cfg = configparser.ConfigParser()
cfg.read('conf.ini')

db_user = cfg.get('Database', 'user')
db_password = cfg.get('Database', 'password')
db_dsn = cfg.get('Database', 'dsn')

directories = cfg.options('Directories')

dir_paths = []

for d in directories:
    dir_paths.append(cfg.get('Directories', d))
    
scripts = cfg.options('Scripts')

scripts_paths = []

for s in scripts:
    scripts_paths.append(cfg.get('Scripts', s))



# userpwd = getpass.getpass("Enter password: ")
file_extensions = ['.pas', '.dfm', '.dpr', '.js', '.ts', '.xml', '.cs', '.sql']

with oracledb.connect(user=db_user, password=db_password, dsn=db_dsn) as connection:
    user_objects = []
    
    with connection.cursor() as cursor:
        for row in cursor.execute("select OBJECT_NAME, OBJECT_TYPE from user_objects where object_type in ('TABLE', 'VIEW', 'PROCEDURE', 'FUNCTION', 'TRIGGER', 'PACKAGE')"):
            user_objects.append(row)
            #print(row)
        # Remove object with names that collide with commmon occurences in text
        # user_objects.remove(('RD', 'TABLE'))
        
        # cursor.execute("delete from FAST_DEPENDIENCES")
        # connection.commit()
        
        with open(f'report_{db_user}.csv', 'w', newline='') as csvfile:                
            
            report = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            report.writerow(['object_name', 'object_type', 'source_name', 'additional_data'])
            
            report_data = []
            
            for dir_path in dir_paths:
                for root, dirs, files in os.walk(dir_path):
                    for filename in files:
                        # print(os.path.join(root, filename))
                        
                        file_path = os.path.join(root, filename)
                        
                        split_tup = os.path.splitext(filename)
                        
                        file_extension = split_tup[1]
                        
                        if file_extension in file_extensions:
                            try:
                                with open(file_path, 'r', errors='surrogateescape') as f:
                                    source = f.read()
                                    
                                    for object_name, object_type in user_objects:
                                        
                                        number_of_occurences = 0
                                        
                                        number_of_occurences += source.count(f"'{object_name}'")
                                        
                                        number_of_occurences += source.count(f"'{object_name}'".lower())
                                        
                                        if number_of_occurences > 0:
                                            report_data.append([object_name, object_type, file_path, number_of_occurences])
                                            # cursor.execute("insert into FAST_DEPENDIENCES values (:object_name, :object_type, :source_name, :additional_data)", [object_name, object_type, file_path, str(number_of_occurences)])
                                            print(object_name, object_type, file_path , number_of_occurences)
                                    # connection.commit()
                            except UnicodeDecodeError:
                                print('Unicode error in file ', file_path)
                            except Exception:
                                print('Other exception occured in file', file_path)
                                
            report.writerows(report_data)
    
        print('Starting execution of scripts')
        
        for s in scripts_paths:
            try:
                with open(s, 'r', errors='surrogateescape') as f:
                    source = f.read()
                    
                    print('Executing ', s)
                    cursor.execute(source)
                    connection.commit()
            except UnicodeDecodeError:
                print('Unicode error in file ', s)
            except Exception:
                print('Other exception occured in file', s)
        
            
                            
                            
                    
        