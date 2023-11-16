from flask import Flask,Blueprint ,render_template,redirect,url_for,request,session
import random,string,db,datetime

user_bp=Blueprint('user',__name__,url_prefix='/user')

user_bp.secret_key=''.join(random.choices(string.ascii_letters,k=256))