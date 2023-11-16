from flask import Flask, render_template,redirect,url_for,request,session
import random,string,db,datetime
from admin import admin_bp
from user import user_bp

app = Flask(__name__)
app.secret_key=''.join(random.choices(string.ascii_letters,k=256))

app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)

@app.route('/')
def index():
    session['msg']=''
    return render_template('index.html')

""" 
マイページ画面・現在日時
"""

@app.route('/top/<int:checkcal>')
def top(checkcal):
    if (checkcal!=1):
        print('test')
        dt=datetime.datetime.now()
        session['month']=dt.month
        session['year']=dt.year
    searchDay=datetime.date(session['year'],session['month'],1)
    msg=session['msg']
    session['msg']=''
    datas=[]
    invitations=[]
    eventList=[]
    
    comIdList=db.getcomId_to_accId(1)
    comIdList2=db.getcomId_to_accId_invit(1)
    if(len(comIdList)!=0):
        for comId in comIdList:
            datas.append(db.getcomInfo_to_comId(comId))
            eventList.append(db.getevent_to_comId(comId,searchDay))
    if(len(comIdList2)!=0):
        for comId in comIdList2:
            invitations.append(db.getcomInfo_to_comId(comId))
    searchDay=f"{session['year']}-{session['month']}-"
    return render_template('user/menu.html', month=session['month'], year=session['year'], datas=datas, invitations=invitations, eventList=eventList, num1=len(comIdList), searchDay=searchDay, msg=msg)

""" 
マイページ画面・前の月へ
"""
@app.route('/monthback')
def monthback():
    session['month']-=1
    if(session['month']==0):
        session['month']=12
        session['year']-=1
    
    return redirect(url_for('top',checkcal=1))
""" 
マイページ画面・次の月へ
"""
@app.route('/monthnext')
def monthnext():
    session['month']+=1
    if(session['month']==13):
        session['month']=1
        session['year']+=1
    
    return redirect(url_for('top',checkcal=1))
    
@app.route('/register_community',methods=['POST'])
def register_community():
    com_name=request.form.get('com_name')
    fav_name=request.form.get('fav_name')
    com_pub=request.form.get('com_public')
    com_explanation=request.form.get('com_explanation')
    data=[com_name,fav_name,com_explanation,com_pub]
    count=db.register_community(data)
    if (count==1):
        com_id=db.get_community_id()
        hidden_flag=db.get_hidden_flag(com_id)
        data=[1,com_id[0],1,1,hidden_flag[0],0,0]
        count=db.join_community_master(data)
        msg='コミュニティを作成しました！'
    else:
        msg='コミュニティを作成できませんでした。'
    session['msg']=msg
    return redirect(url_for('top',checkcal=0))


@app.route('/community/<int:id>/<int:checkcal>')
def community(id,checkcal):
    if (checkcal!=1):
        dt=datetime.datetime.now()
        session['month']=dt.month
        session['year']=dt.year
    searchDay=datetime.date(session['year'],session['month'],1)
    datas=[]
    invitations=[]
    eventList=[]
    community_thread_list=[]
    community_thread_list_all=[]
    cnt=0
    
    comIdList=db.getcomId_to_accId(1)
    comIdList2=db.getcomId_to_accId_invit(1)
    if(len(comIdList)!=0):
        for comId in comIdList:
            datas.append(db.getcomInfo_to_comId(comId))
    if(len(comIdList2)!=0):
            for comId in comIdList2:
                invitations.append(db.getcomInfo_to_comId(comId))
    session['comId']=id
    eventList.append(db.getevent_to_comId(id,searchDay))
    searchDay=f"{session['year']}-{session['month']}-"
    community_thread_list=db.getcomtThread_list_tocomId(id)
    
    for data in community_thread_list:
        goodcheck=db.getcomThread_good(data[0],data[4])
        good_num=db.getcomThread_goodnum(data[0])
        community_thread_list_all.append([data[0],data[1],data[2],data[3],data[4],data[5],data[6],goodcheck[0],good_num[0]])
        cnt+=1
    print(community_thread_list_all)
    print(session['comId'])
    return render_template('user/community.html', month=session['month'], year=session['year'], datas=datas, invitations=invitations, eventList=eventList, num1=1, searchDay=searchDay,thread_list=community_thread_list_all)

""" 
コミュニティ画面・前の月へ
"""
@app.route('/com_monthback')
def com_monthback():
    session['month']-=1
    if(session['month']==0):
        session['month']=12
        session['year']-=1
    
    return redirect(url_for('community',id=session['comId'],checkcal=1))

""" 
マイページ画面・次の月へ
"""

@app.route('/com_monthnext')
def com_monthnext():
    session['month']+=1
    if(session['month']==13):
        session['month']=1
        session['year']+=1
    
    return redirect(url_for('community',id=session['comId'],checkcal=1))

if __name__ == "__main__":
    app.run(debug=True)