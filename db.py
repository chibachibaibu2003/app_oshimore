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

def join_community(account_id, community_id):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        sql = "INSERT INTO register_community (account_id, community_id, authority, community_authority, calendar_hidden_flag, favorite_list_flag, fan_point) VALUES (%s, %s, 1, 1, 0, 0, 0)"
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

def search_users(query):
    """
    ユーザー名またはユーザーIDで部分一致検索を行い、該当するユーザーのリストを返す。
    """
    connection = get_connection()
    cursor = connection.cursor()
    try:
        # ユーザー名またはユーザーIDで検索
        sql = "SELECT account_name, user_id, icon_url FROM account WHERE account_name LIKE %s OR user_id LIKE %s"
        cursor.execute(sql, (f'%{query}%', f'%{query}%'))
        users = cursor.fetchall()
        return [{'account_name': user[0], 'user_id': user[1], 'icon_url': user[2]} for user in users]
    except Exception as e:
        print(e)
        return []
    finally:
        cursor.close()
        connection.close()

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
    sql = 'UPDATE account SET del_flag=%s WHERE account_id=%s;'
    
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql,(1,accId))
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
