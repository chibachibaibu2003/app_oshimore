from flask import Flask, render_template,redirect,url_for,request,session
import datetime
import random,string,db

app = Flask(__name__)
app.secret_key=''.join(random.choices(string.ascii_letters,k=256))
""" 
マイページ画面・現在日時
"""
@app.route('/')
def top():
    dt=datetime.datetime.now()
    session['month']=dt.month
    session['year']=dt.year
    searchDay=datetime.date(dt.year,dt.month,1)
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
    searchDay=f"{dt.year}-{dt.month}-"
    return render_template('user/menu.html', month=dt.month, year=dt.year, datas=datas, invitations=invitations, eventList=eventList, num1=len(comIdList), searchDay=searchDay)

""" 
マイページ画面・前の月へ
"""
@app.route('/monthback')
def monthback():
    session['month']-=1
    if(session['month']==0):
        session['month']=12
        session['year']-=1
    
    searchDay=datetime.date(session['year'],session['month'],1)
    datas=[]
    invitations=[]
    eventList=[]
    changeday=False
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
    return render_template('user/menu.html',month=session['month'],year=session['year'],datas=datas,invitations=invitations,eventList=eventList,num1=len(comIdList),searchDay=searchDay)

""" 
マイページ画面・次の月へ
"""
@app.route('/monthnext')
def monthnext():
    session['month']+=1
    if(session['month']==13):
        session['month']=1
        session['year']+=1
        
    searchDay=datetime.date(session['year'],session['month'],1)
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
    return render_template('user/menu.html',month=session['month'],year=session['year'],datas=datas,invitations=invitations,eventList=eventList,num1=len(comIdList),searchDay=searchDay)

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
        dt=datetime.datetime.now()
        session['month']=dt.month
        session['year']=dt.year
        searchDay=datetime.date(dt.year,dt.month,1)
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
        searchDay=f"{dt.year}-{dt.month}-"
        return render_template('user/menu.html', month=dt.month, year=dt.year, datas=datas, invitations=invitations, eventList=eventList, num1=len(comIdList), searchDay=searchDay)
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)