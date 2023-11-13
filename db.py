import os,psycopg2,string,random
from flask import session

def get_connection():
    url=os.environ['DATABASE_URL']
    connection=psycopg2.connect(url)
    return connection

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