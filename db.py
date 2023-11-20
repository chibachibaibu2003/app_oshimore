
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

def get_accountInfo_toMail(mail):
    sql="SELECT*FROM account WHERE mail=%s"
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(mail,))
        list=cursor.fetchone()
    except psycopg2.DatabaseError :
        list=()
    finally:
        cursor.close()
        connection.close()
        # listはタプルです
    return list

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

def getcomId_to_accId(id):
    sql='SELECT community_id FROM register_community WHERE account_id=%s and calendar_hidden_flag=0 order by community_id asc'
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(id,))
        list=cursor.fetchall()
    except psycopg2.DatabaseError:
        list=[]
    finally:
        cursor.close()
        connection.close()
    return list


def getcomId_to_accId_invit(id):
    sql='SELECT community_id FROM invitation WHERE account_id=%s order by community_id asc'
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(id,))
        list=cursor.fetchall()
    except psycopg2.DatabaseError:
        list=[]
    finally:
        cursor.close()
        connection.close()
    return list

def getcomInfo_to_comId(id):
    sql="SELECT * FROM community WHERE community_id=%s"
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(id))
        list=cursor.fetchall()
    except psycopg2.DatabaseError:
        list=[]
    finally:
        cursor.close()
        connection.close()
    return list

def getevent_to_comId(id,day):
    sql="SELECT  event_id,title,to_char(start_day,'YYYY-FMMM-FMDD')as fmday,to_char(start_day,'YYYY-MM-DD') as start_day,to_char(end_day,'YYYY-MM-DD') as end_day,to_char(start_time,'HH:MM:SS') as start_time,to_char(end_time,'HH:MM:SS') as end_time,url,explanation,account_id,community_id FROM event WHERE community_id=%s and date_trunc('month',start_day)=%s ::date order by start_day asc"
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(id,day))
        list=cursor.fetchall()
    except psycopg2.DatabaseError:
        list=[]
    finally:
        cursor.close()
        connection.close()
    return list

def register_community(data):
    sql="insert into community values(default,%s,%s,%s,%s)"
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(data[0],data[1],data[2],data[3]))
        count=cursor.rowcount
        connection.commit()
    except psycopg2.DatabaseError :
        count=0
    finally:
        cursor.close()
        connection.close()
    return count

def get_community_id():
    sql="SELECT MAX(community_id) FROM community"
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql)
        id=cursor.fetchone()
        
    except psycopg2.DatabaseError :
        count=0
    finally:
        cursor.close()
        connection.close()
        # idはタプルです
    return id

def get_hidden_flag(com_id):
    sql="SELECT public_private FROM community WHERE community_id=%s"
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(com_id,))
        get_hidden_flag=cursor.fetchone()
        
    except psycopg2.DatabaseError :
        count=0
    finally:
        cursor.close()
        connection.close()
        #タプルです
    return get_hidden_flag

def join_community_master(data):
    sql="insert into register_community values(%s,%s,%s,%s,%s,%s,%s)"
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(data[0],data[1],data[2],data[3],data[4],data[5],data[6]))
        count=cursor.rowcount
        connection.commit()
    except psycopg2.DatabaseError :
        count=0
    finally:
        cursor.close()
        connection.close()
    return count

def get_comAuth(accId,comId):
    sql=" SELECT community_authority FROM register_community WHERE account_id=%s and community_id=%s"
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(accId,comId))
        comAuth=cursor.fetchone()
        
    except psycopg2.DatabaseError:
        comAuth=4
    finally:
        cursor.close()
        connection.close()
    return comAuth

"""
コミュニティ参加
"""
def join_community(account_id, community_id):
    sql = "INSERT INTO register_community (account_id, community_id) VALUES (%s, %s)"
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (account_id, community_id))
        connection.commit()
        return True
    except psycopg2.DatabaseError:
        return False
    finally:
        cursor.close()
        connection.close()
"""
参加拒否
"""

def reject_invitation(account_id, community_id):
    sql = "DELETE FROM invitation WHERE account_id = %s AND community_id = %s"
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (account_id, community_id))
        connection.commit()
        return True
    except psycopg2.DatabaseError:
        return False
    finally:
        cursor.close()
        connection.close()

def getcomtThread_list_tocomId(comId):
    sql="SELECT community_post.community_post_id, community_post.community_id, community_post.post, community_post.post_number, account.account_id, account.account_name, account.icon_url FROM community_post JOIN account ON community_post.account_id =account.account_id WHERE community_post.community_id=%s order by community_post.post_number asc"
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(comId,))
        list=cursor.fetchall()
    except psycopg2.DatabaseError:
        list=[]
    finally:
        cursor.close()
        connection.close()
    return list

def getcomThread_good(compostId,accId):
    sql="SELECT count(community_good_id) FROM community_good WHERE community_post_id=%s and account_id=%s"
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(compostId,accId))
        count=cursor.fetchone()
    except psycopg2.DatabaseError :
        count=0
    finally:
        cursor.close()
        connection.close()
    return count

def getcomThread_goodnum(compostId):
    sql="SELECT count(community_good_id) FROM community_good WHERE community_post_id=%s"
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(compostId,))
        count=cursor.fetchone()
    except psycopg2.DatabaseError :
        count=0
    finally:
        cursor.close()
        connection.close()
    return count

def getcommunity_select(comId):
    sql = 'SELECT * FROM community WHERE community_id = %s'
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql,(comId,))
        community_information = cursor.fetchone()
        
    
    finally:
        cursor.close()
        connection.close()
    
    return community_information


def community_update(com_id,com_name,fav_name,com_public,com_explanation):
    sql = 'UPDATE community SET community_id=%s,community_name=%s,favorite_name=%s,community_exp=%s,public_private=%s WHERE community_id=%s;'
    
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql,(com_id,com_name,fav_name,com_explanation,com_public,com_id))
        count = cursor.rowcount 
        connection.commit()
        
    except psycopg2.DatabaseError :
        count = 0
    
    finally :
        cursor.close()
        connection.close()
    
    return count
