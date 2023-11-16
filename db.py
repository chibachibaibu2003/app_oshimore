import os, psycopg2, string, random, hashlib

def get_connection():
    url = os.environ['DATABASE_URL']
    connection = psycopg2.connect(url)
    return connection

def get_salt():
    charset = string.ascii_letters+ string.digits
    salt = ''.join(random.choices(charset, k=10))
    return salt

def get_hash(password, salt):
    b_pw = bytes(password, 'utf-8')
    b_salt = bytes(salt, 'utf-8')
    hashed_password = hashlib.pbkdf2_hmac('sha256', b_pw, b_salt, 1250).hex()
    return hashed_password

def login(mail,password):
    sql = "SELECT pass,salt FROM account WHERE mail = %s"
    flg = False
    
    try :
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql,(mail,))
        user = cursor.fetchone()
        
        if user != None:
            salt = user[1]
            hashed_password = get_hash(password, salt)

            if hashed_password == user[0]:  
                flg = True
                
    except psycopg2.DataError:
        flg = False
        
    finally :
        cursor.close()
        connection.close()
        
    return flg

def get_account_id(id):
    b_id = bytes(id,'utf-8')
    account_id = hashlib.pdk

def temporary_register(mail,name,password,salt,code):
    sql = 'INSERT INTO temporary_account VALUES(default, %s, %s, %s, %s,%s)'
    
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        cursor.execute(sql, (mail,name,password, salt, code))
        count = cursor.rowcount #更新件数を取得
        connection.commit()
    
    except psycopg2.DatabaseError:
        count = 0
    
    finally:
        cursor.close()
        connection.close()
        
    return count
    
def create_code():
    code = random.randint(1000,9999)
    return code
    
def certification_mail(mail, code):
    sql = "SELECT temporary_id,mail,code from temporary_account where mail = %s and code = %s"
    flg = False
    
    try :
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql,(mail,code,))
        user = cursor.fetchone()
        
        if user != None:
            flg = True
            
    except psycopg2.DataError:
        flg = False
        
    return flg

def select_temporary(mail):
    sql = 'SELECT temporary_id,mail,account_name,pass,salt FROM temporary_account WHERE mail =%s'    
    
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (mail,))
        use = cursor.fetchone()
        connection.commit()

    except psycopg2.DatabaseError:
        count = 0
    
    finally:
        cursor.close()
        connection.close()
        
    return use

def insert_user(id,mail,name,password,salt):
    sql = 'INSERT INTO account VALUES(default, %s, %s, %s, %s, %s,null,null,0,0)'
    
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        cursor.execute(sql, (id,mail,name,password,salt,))
        count = cursor.rowcount #更新件数を取得
        connection.commit()
    except psycopg2.DatabaseError:
        count = 0
    
    finally:
        cursor.close()
        connection.close()
        
    return count

def delete_certification(mail):
    sql = "DELETE FROM temporary_account WHERE mail = %s"
    flg = False
    
    try :
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql,(mail,))
        count = cursor.rowcount #更新件数を取得
        connection.commit()
            
    except psycopg2.DataError:
        count = 0
    
    finally :
         cursor.close()
         connection.close()
    return count

def address_check_first(mail):
    sql = "SELECT * FROM account WHERE mail = %s"
    flg = True
    
    try:
        connection = get_connection()
        cursor = connection.cursor()    
        cursor.execute(sql, (mail,))
        count = cursor.rowcount #更新件数を取得
        connection.commit()
        if count != 0:
            flg = False
    
    except psycopg2.DatabaseError:
        count = 0
    
    finally:
        cursor.close()
        connection.close()
        
    return flg

def address_check_second(mail):
    sql = "select * from temporary_account WHERE mail = %s"
    flg = False
    
    try:
        connection = get_connection()
        cursor = connection.cursor()    
        cursor.execute(sql, (mail,))
        count = cursor.rowcount #更新件数を取得
        connection.commit()
        if count == 0:
            flg = True
    
    except psycopg2.DatabaseError:
        count = 0
    
    finally:
        cursor.close()
        connection.close()
        print(flg)
    return flg