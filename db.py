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

def get_accountInfo_toaccId(accId):
    sql="SELECT*FROM account WHERE account_id=%s"
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(accId,))
        list=cursor.fetchone()
    except psycopg2.DatabaseError :
        list=()
    finally:
        cursor.close()
        connection.close()
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

def pass_reset_register(mail,code):
    sql = 'INSERT INTO reset_password VALUES(default, %s, %s)'
    
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        cursor.execute(sql, (mail,code))
        connection.commit()
    
    except psycopg2.DatabaseError:
        count = 0
    
    finally:
        cursor.close()
        connection.close()
        
    return 
    
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

def pass_certification_exe(mail, code):
    sql = "SELECT reset_id,mail,code from reset_password where mail = %s and code = %s"
    flg = False
    
    try :
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql,(mail,code))
        user = cursor.fetchone()
        
        if user != None:
            flg = True
            
    except psycopg2.DataError:
        flg = False
        
    return flg

def select_reset_pass(mail):
    sql = 'SELECT * FROM reset_password WHERE mail =%s'    
    
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

def update_password(password,salt,mail):
    sql = 'UPDATE account set pass = %s,salt = %s WHERE mail =%s'
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (password,salt,mail,))
        connection.commit()
        
    except psycopg2.DatabaseError:
        count = 0
    
    finally:
        cursor.close()
        connection.close()
    return
    
def delete_reset_password(mail):
    sql = 'DELETE FROM reset_password WHERE mail =%s'
    
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql,(mail,))
        connection.commit()
        
    except psycopg2.DatabaseError:
        count = 0
    
    finally:
        cursor.close()
        connection.close()
        
    return
    
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
    sql = 'INSERT INTO account VALUES(default, %s, %s, %s, %s, %s,null,%s,0,0)'
    icon_url='user_icon.png'
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (id,mail,name,password,salt,icon_url))
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

def getcomId_to_accId_joined(id):
    sql="SELECT community_id FROM register_community WHERE account_id=%s order by community_id asc"
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
    sql="SELECT event_id,title,to_char(start_day,'YYYY-FMMM-FMDD')as fmday,to_char(start_day,'YYYY-MM-DD') as start_day,to_char(end_day,'YYYY-MM-DD') as end_day,to_char(start_time,'HH:MM:SS') as start_time,to_char(end_time,'HH:MM:SS') as end_time,url,explanation,account_id,community_id FROM event  WHERE community_id=%s  and date_trunc('month',start_day)=%s ::date  order by start_day asc"
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

def getevent_to_accId(accId,id,day):
    sql="SELECT event_id,title,to_char(start_day,'YYYY-FMMM-FMDD')as fmday,to_char(start_day,'YYYY-MM-DD') as start_day,to_char(end_day,'YYYY-MM-DD') as end_day,to_char(start_time,'HH:MM:SS') as start_time,to_char(end_time,'HH:MM:SS') as end_time,url,explanation,account_id,community_id FROM event  WHERE account_id=%s and community_id=%s  and date_trunc('month',start_day)=%s ::date  order by start_day asc"
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(accId,id,day))
        list=cursor.fetchall()
    except psycopg2.DatabaseError:
        list=[]
    finally:
        cursor.close()
        connection.close()
    return list



def event_thread_info_search(eventId):
    sql="SELECT title,url,explanation from event where event_id=%s"
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(eventId,))
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

def join_community(account_id, community_id):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        sql = "INSERT INTO register_community (account_id, community_id, authority, community_authority, calendar_hidden_flag, favorite_list_flag, fan_point) VALUES (%s, %s, 1, 0, 0, 0, 0)"
        cursor.execute(sql, (account_id, community_id))
        connection.commit()
        return True
    except Exception as e:
        print(e)
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()

def delete_invitation(account_id, community_id):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        sql = "DELETE FROM invitation WHERE account_id = %s AND community_id = %s"
        cursor.execute(sql, (account_id, community_id))
        connection.commit()
        return True
    except Exception as e:
        print(e)
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()

def getcomname_tocomId(comId):
    sql="SELECT community_name FROM community where community_id=%s"
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(comId,))
        name=cursor.fetchone()
    except psycopg2.DatabaseError :
        name='コミュニティスレッド'
    finally:
        cursor.close()
        connection.close()
    return name
    
def getcomtThread_list_tocomId(comId):
    sql="SELECT community_post.community_post_id, community_post.community_id, community_post.post, community_post.post_number, account.account_id, account.account_name, account.icon_url FROM community_post JOIN account ON community_post.account_id =account.account_id WHERE community_post.community_id=%s and community_post.delete_flag=0 order by community_post.post_number asc"
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

def geteventThread_list_toeventId(eventId):
    sql="SELECT event_post.event_post_id, event_post.event_id, event_post.post, account.account_id, account.account_name FROM event_post JOIN account ON event_post.account_id =account.account_id WHERE event_post.event_id=%s and event_post.delete_flag=0 order by event_post.event_post_id asc"
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(eventId,))
        list=cursor.fetchall()
    except psycopg2.DatabaseError:
        list=[]
    finally:
        cursor.close()
        connection.close()
    return list
    
def geteventThread_good(eventId,accId):
    sql="SELECT count(event_good_id) FROM event_good WHERE event_post_id=%s and account_id=%s"
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(eventId,accId))
        count=cursor.fetchone()
    except psycopg2.DatabaseError :
        count=0
    finally:
        cursor.close()
        connection.close()
    return count

def report_event(postid,userid,category,reason):
    sql="INSERT INTO event_post_report VALUES(default,%s,%s,%s,%s)"
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(postid,userid,category,reason))
        count=cursor.rowcount
        connection.commit()
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
"""
コミュニティ編集
"""
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

def get_community_data(community_id):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        sql = "SELECT * FROM community WHERE community_id = %s"
        cursor.execute(sql, (community_id,))
        community_data = cursor.fetchone()
        return community_data
    except Exception as e:
        print(e)
        return None
    finally:
        cursor.close()
        connection.close()

def search_users(query, accId, comId):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        sql = """
        SELECT a.account_name, a.user_id, a.icon_url, a.account_id FROM account a WHERE (a.account_name LIKE %s OR a.user_id LIKE %s) and a.ban_flag != 1 and a.del_flag != 1 and a.account_id != %s and a.account_auth!=1
        and NOT EXISTS (
            SELECT 1 
            FROM register_community rc
            WHERE rc.community_id = %s AND rc.account_id = a.account_id
        )"""

        keyword = '%' + query + '%'
        cursor.execute(sql, (keyword, keyword, accId, comId))
        users = cursor.fetchall()

        return [{'account_name': user[0], 'user_id': user[1], 'icon_url': user[2]} for user in users]
    except Exception as e:
        print("エラー:", e)
        return []
    finally:
        cursor.close()
        connection.close()
        
def report_user_search(query,accId):
    sql="SELECT account_name, user_id, icon_url,account_id FROM account WHERE (account_name LIKE %s OR user_id LIKE %s) and ban_flag!=1 and del_flag!=1 and account_id!=%s"
    try:
        connection = get_connection()
        cursor = connection.cursor()
        keyword='%'+query+'%'
        cursor.execute(sql,(keyword,keyword,accId))
        community_information = cursor.fetchall()
    except psycopg2.DatabaseError:
        community_information=[]
    finally:
        cursor.close()
        connection.close()
    return community_information

def report_community_search(query):
    sql="SELECT * FROM community WHERE community_name LIKE %s OR favorite_name LIKE %s"
    try:
        connection = get_connection()
        cursor = connection.cursor()
        keyword='%'+query+'%'
        cursor.execute(sql,(keyword,keyword))
        community_information = cursor.fetchall()
    except psycopg2.DatabaseError:
        community_information=[]
    finally:
        cursor.close()
        connection.close()
    return community_information
    
def user_detail(user_id):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        # ユーザー情報の取得
        user_info_sql = "SELECT account_id, account_name, user_id, icon_url, profile FROM account WHERE user_id = %s"
        cursor.execute(user_info_sql, (user_id,))
        user_info = cursor.fetchone()

        # 推しリストの取得
        oshi_list_sql = """
        SELECT c.favorite_name
        FROM community c
        INNER JOIN register_community rc ON c.community_id = rc.community_id
        WHERE rc.account_id = %s AND rc.favorite_list_flag = 0
        """
        cursor.execute(oshi_list_sql, (user_info[0],))  # user_infoからaccount_idを渡す
        oshi_list = cursor.fetchall()
        if user_info:
            # ユーザー情報と推しリストを辞書形式で返す
            return {
                'account_id': user_info[0],
                'account_name': user_info[1],
                'user_id': user_info[2],
                'icon_url': user_info[3],
                'profile': user_info[4],
                'oshi_list': [oshi_name[0] for oshi_name in oshi_list]  # 推しリストを追加
            }
        return None
    except Exception as e:
        print(e)
        return None


"""
アカウント退会
"""
def account_withdraw(accId):
    sql = 'UPDATE account SET del_flag=%s,mail=%s WHERE account_id=%s;'
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql,(1,accId,accId))
        count = cursor.rowcount 
        connection.commit()
        
    except psycopg2.DatabaseError :
        count = 0
    
    finally :
        cursor.close()
        connection.close()
    return count
  
def community_search(keyword):
    sql = 'SELECT community_id,community_name,favorite_name,community_exp FROM community WHERE favorite_name LIKE %s AND public_private = 0 OR community_name LIKE %s AND public_private = 0'
    
    try:
        connection=get_connection()
        cursor=connection.cursor()
        keyword = '%'+keyword+'%'
        cursor.execute(sql,(keyword,keyword,))
        result=cursor.fetchall()
    except psycopg2.DatabaseError :
        result = None
    finally:
        cursor.close()
        connection.close()
    return result

def select_community(id):
    sql = 'SELECT community_id,community_name,favorite_name,community_exp FROM community WHERE community_id = %s'
    
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(id,))
        result=cursor.fetchone()
    except psycopg2.DatabaseError :
        result = None
    finally:
        cursor.close()
        connection.close()
    return result
    

def community_delete(comId):
    sql="delete from community where community_id =%s"
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(comId,))
        count=cursor.rowcount
        connection.commit()
    except psycopg2.DatabaseError:
        count=0
    finally:
        cursor.close()
        connection.close()
    
    return count

def register_community_delete(comId):
    sql="delete from register_community where community_id=%s"
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(comId,))
        count=cursor.rowcount
        connection.commit()
    except psycopg2.DatabaseError:
        count=0
    finally:
        cursor.close()
        connection.close()
    
    return count

def remove_register_community(accId,comId):
    sql="delete from register_community where account_id=%s and community_id=%s"
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(accId,comId))
        count=cursor.rowcount
        connection.commit()
    except psycopg2.DatabaseError:
        count=0
    finally:
        cursor.close()
        connection.close()
    
    return count

def count_community_member_num(comId):
    sql="select*from register_community where community_id=%s"
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(comId,))
        count=cursor.rowcount
    except psycopg2.DatabaseError :
        count=0
    finally:
        cursor.close()
        connection.close()
    return count

def get_nextReader_num(comId):
    sql="select account_id ,max(fan_point)from register_community where community_id=%s group by account_id"
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(comId,))
        count=cursor.fetchone()
    except psycopg2.DatabaseError :
        count=[[]]
    finally:
        cursor.close()
        connection.close()
    return count
    
def change_community_reader(accId,comId):
    sql="update register_community set authority=1 , community_authority=1 where account_id=%s and community_id=%s"
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(accId,comId))
        count=cursor.rowcount
        connection.commit()
    except psycopg2.DatabaseError:
        count=0
    finally:
        cursor.close()
        connection.close()
    return count

        

def search_join_community(account_id, community_id):
    sql = "INSERT INTO register_community VALUES (%s, %s, 0, 0, 0, 0, 0)"
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
        
def community_join_check(account_id,community_id):
    sql = "SELECT * FROM register_community WHERE account_id = %s and community_id = %s"
    flg = False
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(account_id,community_id,))
        count=cursor.fetchone()

    except psycopg2.DatabaseError :
        flg = False
    finally:
        cursor.close()
        connection.close()
        if count !=None:
            flg = True
    return flg
#参加している場合True
        
def report_community(community_id,user_id,category,reason):
    sql = "INSERT INTO  community_report values(default, %s,%s,%s,%s)"
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (community_id,user_id,category,reason,))
        connection.commit()
        return True
    except psycopg2.DatabaseError:
        return False
    finally:
        cursor.close()
        connection.close()

def insert_invitation(community_id, account_id):
    """
    指定されたコミュニティIDとアカウントIDを使用して、招待データをデータベースに挿入する。
    """
    connection = get_connection()
    cursor = connection.cursor()
    try:
        # 招待データの挿入
        sql = "INSERT INTO invitation (community_id, account_id) VALUES (%s, %s)"
        cursor.execute(sql, (community_id, account_id))
        connection.commit()  # 変更をコミット
        return True  # 挿入成功
    except Exception as e:
        print(e)
        connection.rollback()  # エラーが発生したらロールバック
        return False  # 挿入失敗
    finally:
        cursor.close()
        connection.close()


"""
いいね機能(いいね取り消し)
"""
def community_post_good(postId,accId):
    sql="insert into community_good values(default,%s,%s)"
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(postId,accId))
        count=cursor.rowcount
        connection.commit()
    except psycopg2.DatabaseError:
        count=0
    finally:
        cursor.close()
        connection.close()
    return count

def community_post_good_del(postId,accId):
    sql="delete from community_good where community_post_id=%s and account_id=%s"
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(postId,accId))
        count=cursor.rowcount
        connection.commit()
    except psycopg2.DatabaseError:
        count=0
    finally:
        cursor.close()
        connection.close()
    return count


def event_post_good(postId,accId):
    sql="insert into event_good values(default,%s,%s)"
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(postId,accId))
        count=cursor.rowcount
        connection.commit()
    except psycopg2.DatabaseError:
        count=0
    finally:
        cursor.close()
        connection.close()
    return count

def event_post_good_del(postId,accId):
    sql="delete from event_good where event_post_id=%s and account_id=%s"
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(postId,accId))
        count=cursor.rowcount
        connection.commit()
    except psycopg2.DatabaseError:
        count=0
    finally:
        cursor.close()
        connection.close()
    return count

def community_post(accId,comId,post,post_day):
    sql="INSERT INTO community_post values(default,%s,%s,%s,0,%s,0)"
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(accId,comId,post,post_day))
        count=cursor.rowcount
        connection.commit()
    except psycopg2.DatabaseError:
        count=0
    finally:
        cursor.close()
        connection.close()
    return count


def event_thread_post(accId,eventId,post,post_day):
    sql="INSERT INTO event_post values(default,%s,%s,%s,0,%s,0)"
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(accId,eventId,post,post_day))
        count=cursor.rowcount
        connection.commit()
    except psycopg2.DatabaseError:
        count=0
    finally:
        cursor.close()
        connection.close()
    return count


def insert_community_post_report(post_id, reporter_id, report_category, report_reason):
    sql = """
    INSERT INTO community_post_report (community_post_id, reporter_id, post_report_category, post_report_reason)
    VALUES (%s, %s, %s, %s)
    """
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        if report_category != 'その他':
            report_reason = ""
        
        cursor.execute(sql, (post_id, reporter_id, report_category, report_reason))
        connection.commit()
        return True
    except psycopg2.DatabaseError as e:
        print(e)
        return False
    finally:
        cursor.close()
        connection.close()

  
def event_register(title,start_day,end_day,start_time,end_time,url,explanation,account_id,community_id):
    sql="INSERT INTO event VALUES(default,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(title,start_day,end_day,start_time,end_time,url,explanation,account_id,community_id))
        count=cursor.rowcount
        connection.commit()
    except psycopg2.DatabaseError:
        count=0
    finally:
        cursor.close()
        connection.close()

    return count

def event_info_search(eventId):
    sql="SELECT event_id,title,start_day,end_day,start_time,end_time,url,explanation,account_id from event where event_id=%s"
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (eventId,))
        event_info = cursor.fetchone()
    finally:
        cursor.close()
        connection.close()
    return event_info


def event_update(event_id,title,start_day,end_day,start_time,end_time,url,explanation):
    sql = 'UPDATE event SET title=%s,start_day=%s,end_day=%s,start_time=%s,end_time=%s,url=%s,explanation=%s WHERE event_id=%s;'

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (title,start_day,end_day,start_time,end_time,url,explanation,event_id))
        count = cursor.rowcount
        connection.commit()

    except psycopg2.DatabaseError:
        count = 0
    finally:
        cursor.close()
        connection.close()
    return count

def get_user_profile(account_id):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM account WHERE account_id = %s", (account_id,))
        user_info = cursor.fetchone()
        return user_info
        print("情報取得時のセッション情報:", user_info)
    except Exception as e:
        print("Error fetching user profile:", e)
        return None
    finally:
        cursor.close()
        connection.close()

def update_user_profile(account_id, new_user_id, account_name, profile, icon_url, oshi_list_settings):
    print("これまでのセッション情報:", account_id, new_user_id, account_name, profile, icon_url, oshi_list_settings)
    connection = get_connection()
    cursor = connection.cursor()
    try:
        # ユーザー情報の更新
        cursor.execute("UPDATE account SET user_id = %s, account_name = %s, profile = %s, icon_url = %s WHERE account_id = %s",
                       (new_user_id, account_name, profile, icon_url, account_id))

        # 推しリスト設定の更新
        for oshi_id, is_public in oshi_list_settings.items():
            cursor.execute("UPDATE register_community SET favorite_list_flag = %s WHERE account_id = %s AND community_id = %s",
                    (is_public, account_id, oshi_id))

        connection.commit()
        return True
    except Exception as e:
        print("Error updating user profile:", e)
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()

def get_oshi_list(account_id):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            SELECT c.community_id, c.favorite_name, rc.favorite_list_flag
            FROM community c
            JOIN register_community rc ON c.community_id = rc.community_id
            WHERE rc.account_id = %s""", (account_id,))
        oshi_list = cursor.fetchall()
        return [{'community_id': oshi[0], 'favorite_name': oshi[1], 'is_public': oshi[2] == 0} for oshi in oshi_list]
    except Exception as e:
        print(e)
        return []
    finally:
        cursor.close()
        connection.close()

def event_delete(event_id):
    sql = "DELETE FROM event WHERE event_id=%s"
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (event_id,))
        count = cursor.rowcount
        connection.commit()
    except psycopg2.DatabaseError:
        count = 0
    finally:
        cursor.close()
        connection.close()
    return count

def select_event_post_by_id(event_id):
    sql = "SELECT event_post_id FROM event_post WHERE event_id=%s"
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (event_id,))
        event_post_id = cursor.fetchone()
    except psycopg2.DatabaseError:
        event_post_id = []
    finally:
        cursor.close()
        connection.close()

    return event_post_id

def event_post_delete(event_id):
    sql = 'UPDATE event_post SET delete_flag=1 WHERE event_id=%s;'

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (event_id,))
        count = cursor.rowcount
        connection.commit()

    except psycopg2.DatabaseError:
        count = 0

    finally:
        cursor.close()
        connection.close()
    return count

def event_post_report_delete(event_post_id):
    sql = "DELETE FROM event_post_report WHERE event_post_id=%s"
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (event_post_id,))
        count = cursor.rowcount
        connection.commit()
    except psycopg2.DatabaseError:
        count = 0
    finally:
        cursor.close()
        connection.close()
    return count

def event_good_delete(event_post_id):
    sql = "DELETE FROM event_good WHERE event_post_id=%s"
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (event_post_id,))
        count = cursor.rowcount
        connection.commit()
    except psycopg2.DatabaseError:
        count = 0
    finally:
        cursor.close()
        connection.close()
    return count
  
def check_user_id_exists(user_id):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM account WHERE user_id = %s", (user_id,))
        count = cursor.fetchone()[0]
        return count > 0
    except Exception as e:
        print(e)
        return False
    finally:
        cursor.close()
        connection.close()

def update_authority(member_id, new_authority):
    sql = "UPDATE register_community SET authority = %s WHERE account_id = %s"
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (new_authority, member_id))
        connection.commit()

        print(f"Updated authority for account_id {member_id} to {new_authority}")  # 更新結果をプリント

    except Exception as e:
        print(f"Error in update_authority: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()
    return True

def update_community_authority(member_id, new_community_authorty):
    sql = "UPDATE register_community SET community_authority = %s WHERE account_id = %s"
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (new_community_authorty, member_id))
        connection.commit()
    except Exception as e:
        print(e)
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()
    return True

def get_members_with_auth():
    sql = """
    SELECT DISTINCT a.account_id, a.account_name, rc.authority, rc.community_authority
    FROM account a
    JOIN register_community rc ON a.account_id = rc.account_id
    """
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql)
        members = cursor.fetchall()
        return members
    except Exception as e:
        print(e)
        return []
    finally:
        cursor.close()
        connection.close()
def get_community_members(community_id):
    """
    指定されたコミュニティIDに基づいて、そのコミュニティのメンバー情報を取得します。
    """
    sql = """
    SELECT a.account_id, a.account_name, rc.authority, rc.community_authority
    FROM account a
    JOIN register_community rc ON a.account_id = rc.account_id
    WHERE rc.community_id = %s
    AND rc.community_authority != 1
    """
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (community_id,))
        members = cursor.fetchall()
        return [
            {
                'account_id': member[0],
                'account_name': member[1],
                'authority': member[2],
                'community_authority': member[3]
            }
            for member in members
        ]
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        cursor.close()
        connection.close()

        
def event_postList_toaccId(accId):
    sql="select*from event_post where account_id=%s"
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(accId,))
        result=cursor.fetchall()
    except psycopg2.DatabaseError :
        result = []
    finally:
        cursor.close()
        connection.close()
    return result

def event_reportList_toPostId(postId):
    sql="select event_post_report.reporter_id, event_post_report.post_report_reason, event_post_report.post_report_category, event_post.post, event_post.post_day from event_post join event_post_report on event_post_report.event_post_id =event_post.event_post_id where event_post.event_post_id=%s"
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(postId,))
        result=cursor.fetchone()
        cnt=cursor.rowcount
        if (cnt==0):
            result=0
    except psycopg2.DatabaseError :
        result = 0
    finally:
        cursor.close()
        connection.close()
    return result

def ban_user_toaccId(accId):
    sql="update account set ban_flag=1 where account_id=%s"
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        cursor.execute(sql, (accId,))
        count = cursor.rowcount #更新件数を取得
        connection.commit()
    
    except psycopg2.DatabaseError:
        count = 0
    
    finally:
        cursor.close()
        connection.close()
        
    return count

def ban_userList_search():
    sql="select distinct on (account.account_id) account.account_name , account.user_id , event_post_report.event_post_id from account join event_post on account.account_id=event_post.account_id join event_post_report on event_post.event_post_id =event_post_report.event_post_id where account.ban_flag!=1 and account.del_flag!=1"
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,())
        result=cursor.fetchall()
    except psycopg2.DatabaseError :
        result = []
    finally:
        cursor.close()
        connection.close()
    return result

def del_event_toaccId(accId):
    sql="delete from event_post where account_id=%s "
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        cursor.execute(sql, (accId,))
        count = cursor.rowcount #更新件数を取得
        connection.commit()
    
    except psycopg2.DatabaseError:
        count = 0
    
    finally:
        cursor.close()
        connection.close()
        
    return count

def del_comThread_toaccId(accId):
    sql="delete from community_post where account_id=%s"
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        cursor.execute(sql, (accId,))
        count = cursor.rowcount #更新件数を取得
        connection.commit()
    
    except psycopg2.DatabaseError:
        count = 0
    
    finally:
        cursor.close()
        connection.close()
    return count

def getcom_info_list(accId):
    sql='SELECT register_community.community_id,community.community_name,register_community.calendar_hidden_flag FROM register_community INNER JOIN community ON register_community.account_id=%s AND register_community.community_id=community.community_id ORDER BY register_community.community_id ASC'
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(accId,))
        list=cursor.fetchall()
    except psycopg2.DatabaseError:
        list=[]
    finally:
        cursor.close()
        connection.close()
    return list

def calendar_hidden(comId,account_id,calendar_hidden_flag):
    sql = 'UPDATE register_community SET calendar_hidden_flag=%s WHERE account_id=%s and community_id=%s;'

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (calendar_hidden_flag,account_id,comId,))
        count = cursor.rowcount
        connection.commit()

    except psycopg2.DatabaseError:
        count = 0

    finally:
        cursor.close()
        connection.close()
    return count


def community_post_reportList(comId):
    sql="select community_post.account_id,community_post.community_post_id,community_post_report.post_report_category,community_post_report.post_report_reason,community_post.post from community join community_post on community.community_id =community_post.community_id join community_post_report on community_post.community_post_id=community_post_report.community_post_id where community_post.delete_flag=0 and community.community_id=%s"
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(comId,))
        result=cursor.fetchall()
    except psycopg2.DatabaseError :
        result = []
    finally:
        cursor.close()
        connection.close()
    return result

def del_community_post(postId):
    sql="delete from community_post where community_post_id=%s"
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (postId,))
        count = cursor.rowcount 
        connection.commit()
    
    except psycopg2.DatabaseError:
        count = 0
    
    finally:
        cursor.close()
        connection.close()
    return count

def account_id_search(id):
    sql="SELECT account_id FROM register_community WHERE community_id = %s and community_authority = 1"
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(id,))
        result=cursor.fetchone()
    except psycopg2.DatabaseError :
        result = []
    finally:
        cursor.close()
        connection.close()
    return result

def user_id_search(id):
    sql="SELECT user_id FROM account WHERE account_id = %s"
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(id,))
        result=cursor.fetchone()
    except psycopg2.DatabaseError :
        result = []
    finally:
        cursor.close()
        connection.close()
    return result

def report_count(id):
    sql="SELECT * from community_report WHERE community_id = %s"
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(id,))
        result=cursor.fetchall()
    except psycopg2.DatabaseError :
        result = []
    finally:
        cursor.close()
        connection.close()
    return result

def ban_community(id):
    sql="delete from community where community_id=%s"
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,(id,))
        count=cursor.rowcount
        connection.commit()
    except psycopg2.DatabaseError:
        count=0
    finally:
        cursor.close()
        connection.close()
    return count


def del_community_post_reportList(postId):
    sql="delete from community_post_report where community_post_id=%s"
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        cursor.execute(sql, (postId,))
        count = cursor.rowcount 
        connection.commit()
    
    except psycopg2.DatabaseError:
        count = 0
    
    finally:
        cursor.close()
        connection.close()
    return count


