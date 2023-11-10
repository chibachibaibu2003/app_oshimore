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


if __name__ == "__main__":
    app.run(debug=True)