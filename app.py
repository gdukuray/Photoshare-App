######################################
# author ben lawson <balawson@bu.edu> 
# Edited by: Craig Einstein <einstein@bu.edu>
# Edited by: Gahouray Dukuray <gdukuray@bu.edu>
######################################
# Some code adapted from 
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
#import flask.ext.login as flask_login
import flask_login
#for image uploading
from werkzeug import secure_filename
import os, base64
#for date
import datetime as dt

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'issasecret'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'talktomenice404' #CHANGE THIS TO YOUR MYSQL PASSWORD
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users") 
users = cursor.fetchall()

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users") 
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd
	return user


'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('hello.html', message='Logged out') 

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html') 

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register/", methods=['GET'])
def register():
	return render_template('improved_register.html', supress='True')  

@app.route("/register/", methods=['POST'])
def register_user():
	try:
		email=request.form.get('email')
		password=request.form.get('password')
		firstname=request.form.get('firstname')
		lastname=request.form.get('lastname')
		date_of_birth=request.form.get('date_of_birth')
		bio=request.form.get('bio')
		hometown=request.form.get('hometown')
		gender=request.form.get('gender')
		default_id = getUserIdFromEmail("default@default.com")
		
	except:
		print("couldn't find all tokens")
		#this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	if test:
                profilepic=request.files['profilepic']
                if profilepic.filename == '':
                        photo_data = getProfilePic(default_id)
                        print cursor.execute("INSERT INTO Users (email, password, firstname, lastname, date_of_birth, bio, hometown, gender, profilepic) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}')".format(email, password, firstname, lastname, date_of_birth, bio, hometown, gender, photo_data)) 
                else:
                        print "Full"
                        photo_data = base64.standard_b64encode(profilepic.read())
                        print cursor.execute("INSERT INTO Users (email, password, firstname, lastname, date_of_birth, bio, hometown, gender, profilepic) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}')".format(email, password, firstname, lastname, date_of_birth, bio, hometown, gender, photo_data))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('hello.html', name=email, message='Account Created!')
	else:
		print "couldn't find all tokens"
		return flask.redirect(flask.url_for('register'))
	
def getProfilePic(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT profilepic FROM Users WHERE user_id = ('{0}')".format(uid))
	return cursor.fetchone()[0]

def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)): 
		#this means there are greater than zero entries with that email
		return False
	else:
		return True
#end login code

#Useful Functions
def getFirstNameFromId(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT firstname From Users Where user_id = '{0}'".format(uid))
	return cursor.fetchone()[0]
def getFirstNameFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT firstname From Users Where email = '{0}'".format(email))
	res = cursor.fetchone()[0]
        result = res.encode('utf-8')
	return result
def getLastNameFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT lastname From Users Where email = '{0}'".format(email))
	res = cursor.fetchone()[0]
        result = res.encode('utf-8')
	return result
def getUserIdFromPicId(picture_id):
        cursor = conn.cursor()
	cursor.execute("SELECT user_id FROM Pictures WHERE picture_id = '{0}'".format(picture_id))
	return cursor.fetchall()[0][0]
def getUserIdFromAlbumId(album_id):
        cursor = conn.cursor()
	cursor.execute("SELECT user_id FROM Albums WHERE album_id = '{0}'".format(album_id))
	return cursor.fetchone()[0]
def getAlbumIdFromAlbumName(album_name):
        cursor = conn.cursor()
        cursor.execute("SELECT album_id FROM Albums WHERE name = '{0}'".format(album_name))
	return cursor.fetchone()[0]
def getPicId(photo_data):
        cursor = conn.cursor()
        cursor.execute("SELECT picture_id FROM Pictures WHERE imgdata = '{0}'".format(photo_data))
        return cursor.fetchone()[0]
def existingTag(tag):
        cursor = conn.cursor()
        if cursor.execute("SELECT description FROM Tags WHERE description = '{0}'".format(tag)):
                return True
        else:
                return False
def getPictureFromAlbum(album_id):
	cursor = conn.cursor()
	cursor.execute("SELECT picture_id, imgdata, caption FROM Pictures WHERE album_id = '{0}'".format(album_id))
	return cursor.fetchall()
def getAlbumNameFromId(album_id):
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM Albums WHERE album_id = '{0}'".format(album_id))
        res = cursor.fetchone()[0]
        result = res.encode('utf-8')
	return result
def getTagsFromPicId(picture_id):
        cursor = conn.cursor()
        cursor.execute("SELECT description FROM PictureTag WHERE picture_id = '{0}'".format(picture_id))
        return cursor.fetchone()
def getPicIdFromTag(text):
        cursor = conn.cursor()
        cursor.execute("SELECT picture_id FROM PictureTag WHERE description = '{0}'".format(text))
        return cursor.fetchone()[0]
def getPhotoFromTag(text):
        pic_id = getPicIdFromTag(text)
        cursor = conn.cursor()
        cursor.execute("SELECT imgdata, caption, user_id FROM Pictures WHERE picture_id = '{0}'".format(pic_id))
        return cursor.fetchone()[0]
def getPhotoIdFromTag(description):
        cursor = conn.cursor()
        cursor.execute("SELECT picture_id FROM PictureTag WHERE description = '{0}'".format(description))
        return cursor.fetchall()
def getPhotoFromPicId(picture_id):
        cursor = conn.cursor()
        cursor.execute("SELECT imgdata, caption, user_id FROM Pictures WHERE picture_id = '{0}'".format(picture_id))
        return cursor.fetchone()
def getCommentFromPicId(picture_id):
        cursor = conn.cursor()
	cursor.execute("SELECT text, email, date_comment_left, comment_id FROM Comments WHERE picture_id = '{0}'".format(picture_id))
        print(cursor.fetchall())
	return cursor.fetchall()
def getMostUsedTagByUser(user_id):
        cursor = conn.cursor()
        cursor.execute("SELECT description FROM PictureTag AS T1, Pictures AS P WHERE T1.picture_id = P.picture_id AND P.user_id = '{0}' GROUP BY T1.description ORDER BY COUNT(P.picture_id) desc limit 5".format(user_id))
#end Useful Functions

@app.route('/profile')
@flask_login.login_required
def protected():
        uid = getUserIdFromEmail(flask_login.current_user.id)
	return render_template('profile.html', name=flask_login.current_user.id, message="Here's your profile", profilepic=getProfilePic(uid), photos=getUsersPhotos(uid))

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		print caption
		tags = request.form.get('tags')
		tags = [x.strip('#') for x in tags.split(',')]
		photo_data = base64.standard_b64encode(imgfile.read())
		#this acutally gets the album id from the name
                try_album_id=request.form.get('name')
                album_id = int(try_album_id.encode('utf-8'))
                if album_id == "":
                        print ("couldn't find all tokens")
                        return flask.redirect(flask.url_for('upload'))
                else:
                        album_userid = getUserIdFromAlbumId(album_id)
                        if album_userid == uid:
                                cursor = conn.cursor()
                                cursor.execute("INSERT INTO Pictures (imgdata, user_id, caption, album_id) VALUES ('{0}', '{1}', '{2}', '{3}')".format(photo_data,uid,caption,album_id))
                                conn.commit()
                                picture_id = getPicId(photo_data)
                                cursor = conn.cursor()
                                for i in range(len(tags)):
                                        if existingTag(tags[i]):
                                                cursor.execute("INSERT INTO PictureTag (picture_id, description) VALUES ('{0}', '{1}')".format(picture_id, tags[i]))
                                        else:
                                                cursor.execute("INSERT INTO Tags (description) VALUES ('{0}')".format(tags[i]))
                                conn.commit()
                                return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPhotos(uid))
                        else:
                                return render_template('hello.html', name=flask_login.current_user.id, message='Log In To Your Own Account!')
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
                uid = getUserIdFromEmail(flask_login.current_user.id)
		return render_template('upload.html', albums=getUserAlbums(uid))
#end photo uploading code

#photo functions
def getAllPhotos():
	cursor = conn.cursor()
	cursor.execute("SELECT picture_id ,imgdata, caption FROM Pictures")
	return cursor.fetchall()

@app.route('/deletephoto', methods=['POST'])
@flask_login.login_required
def deletephoto():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	picture_id=request.args.get('values')
	picture_id=int(picture_id.encode('utf-8'))
	picture_userid=getUserIdFromPicId(picture_id)
	cursor = conn.cursor()
	if picture_userid == uid:
		cursor.execute("DELETE FROM Pictures WHERE picture_id = '{0}'".format(picture_id))
		conn.commit()
		album_name=request.args.get('values')
                album_name=album_name.encode('utf-8')
                album_id = getAlbumIdFromAlbumName(album_name)
                print("album_id")
                print("album_id: ",album_id)
		all_pictures=getPictureFromAlbum(album_id)
		return render_template('photos.html', message='Perished!', photos=all_pictures)
	else:
		return render_template('hello.html', name=flask_login.current_user.id, message=' Log Into Your Own Account!')
	
#begin Album Functions
def getUserAlbums(uid):
        cursor = conn.cursor()
        cursor.execute("SELECT album_id, name, date_of_creation FROM Albums WHERE user_id = '{0}'".format(uid))
        return cursor.fetchall()

@app.route('/createalbum', methods=['GET', 'POST'])
@flask_login.login_required
def createalbum():
        user_id = getUserIdFromEmail(flask_login.current_user.id)
        if request.method == 'POST':
                album_name=request.form.get('name')
                print(album_name)
                if album_name == "":
                        print ("couldn't find all tokens")
                        #this prints to shell, end users will not see this (all print statements go to shell)
                        return flask.redirect(flask.url_for('createalbum'))
                else:
                        date_of_creation=dt.datetime.today().strftime("%Y-%m-%d")
                        user_id = getUserIdFromEmail(flask_login.current_user.id)
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO Albums (name, user_id, date_of_creation) VALUES ('{0}', '{1}', '{2}')".format(album_name,user_id,date_of_creation))
                        conn.commit()
                        return render_template('albums.html', name=flask_login.current_user.id, message='Your Album has been created!', albums=getUserAlbums(user_id))
        else:
                return render_template('createalbum.html', name=flask_login.current_user.id, albums=getUserAlbums(user_id))

#only user can delete their own album
@app.route('/deletealbum', methods=['POST'])
@flask_login.login_required
def deletealbum():
        uid = getUserIdFromEmail(flask_login.current_user.id)
        album_name=request.args.get('values')
	album_name=album_name.encode('utf-8')
        album_id = getAlbumIdFromAlbumName(album_name)
        album_uid = getUserIdFromAlbumId(album_id)
        if album_uid == uid:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Albums WHERE album_id = '{0}'".format(album_id))
                conn.commit()
                return render_template('albums.html', name=flask_login.current_user.id, message='You Have Deleted an Album!')
        else:
                return render_template('hello.html', name=flask_login.current_user.id, message='Users Can Delete Their Own Albums ONLY!')

@app.route('/albums', methods=['GET'])
@flask_login.login_required
def showAlbums():
        uid = getUserIdFromEmail(flask_login.current_user.id)
        cursor = conn.cursor()
        cursor.execute("SELECT album_id FROM Albums WHERE user_id = '{0}'".format(uid))
        album_id = cursor.fetchall()[0][0]
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM Albums WHERE album_id = '{0}'".format(album_id))
        album = cursor.fetchall()
        photo = getPictureFromAlbum(album_id)
        cursor = conn.cursor()
        cursor.execute("SELECT picture_id, imgdata, caption FROM Pictures WHERE album_id = '{0}'".format(album_id))
        photo = cursor.fetchall()
        return render_template('albums.html', name=flask_login.current_user.id, message='Here are Your Albums', albums=album, photos=photo)

@app.route('/photos/<album_id>', methods=['GET'])
def PhotosInAlbum(album_id):
	all_pictures=getPictureFromAlbum(album_id)
	album_name=getAlbumNameFromId(album_id)
	return render_template('photos.html', albums=album_name, photos=all_pictures)

#@app.route('/allalbums/<album_id>', methods=['GET'])
def getAllAlbums():
	cursor = conn.cursor()
	cursor.execute("SELECT album_id, name, firstname FROM Albums, Users")
        return cursor.fetchall()
	#return render_template('allalbums.html', message="Here are All the Albums on Photoshare", albums=album)

#friends
def getUserFriends(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT f_firstname, f_lastname FROM UserFriends WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall()

@app.route('/friends', methods=['GET'])
@flask_login.login_required
def friends():
        uid = getUserIdFromEmail(flask_login.current_user.id)
        return render_template('friends.html', name=flask_login.current_user.id, message='Here are Your Friends', friends=getUserFriends(uid))

@app.route('/newfriend', methods=['GET'])
@flask_login.login_required
def newfriend():
        uid = getUserIdFromEmail(flask_login.current_user.id)
        f_email=request.args.get('values')
        f_email=f_email.encode('utf-8')
        f_firstname = getFirstNameFromEmail(f_email)
        f_lastname = getLastNameFromEmail(f_email)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO UserFriends (f_email, user_id, f_firstname, f_lastname) VALUES ('{0}', '{1}', '{2}', '{3}')".format(f_email,uid,f_firstname,f_lastname))
        conn.commit()
        return render_template('friends.html', name=flask_login.current_user.id, message='New Friend Added!', friends=getUserFriends(uid))

@app.route('/findfriends')
@flask_login.login_required
def search():
	return render_template('findfriends.html')

@app.route('/findfriends', methods=['POST'])
@flask_login.login_required
def findfriends():
        try:
                f_firstname=request.form.get('f_firstname')
		f_lastname=request.form.get('f_lastname')
	except:
                print ("couldn't find all tokens")
                return flask.redirect(flask.url_for('friends'))
        uid = getUserIdFromEmail(flask_login.current_user.id)
        cursor = conn.cursor()
        cursor.execute("SELECT email, firstname, lastname, gender FROM Users WHERE firstname = '{0}' AND lastname = '{1}'".format(f_firstname, f_lastname))
        return render_template('findfriends.html', name=flask_login.current_user.id, message='Search Results', Results=cursor.fetchall())
#end friends functions

#likes
@app.route('/likes/<picture_id>', methods=['GET'])
@flask_login.login_required
def likes(picture_id):
        cursor = conn.cursor()
	cursor.execute("SELECT email FROM Likes WHERE picture_id='{0}'".format(picture_id))
	likes=cursor.fetchall()
	cursor.execute("SELECT count(user_id) FROM Likes WHERE picture_id = '{0}'".format(picture_id))
	numberoflike = cursor.fetchall()[0]
	return render_template('likes.html', message="People Who Liked This Picture", users=likes, photoID=picture_id, number=numberoflike)

@app.route('/likes/<picture_id>', methods=['POST'])
@flask_login.login_required
def userLikes(picture_id):
	uid=getUserIdFromEmail(flask_login.current_user.id)
	email=flask_login.current_user.id
	cursor = conn.cursor()
	cursor.execute("INSERT INTO Likes (user_id, email, picture_id) VALUES ('{0}', '{1}','{2}')".format(uid, email, picture_id))
	conn.commit()
	cursor.execute("SELECT email FROM Likes WHERE picture_id='{0}'".format(picture_id))
	likes=cursor.fetchall()
	cursor.execute("SELECT count(email) FROM Likes WHERE picture_id = '{0}'".format(picture_id))
	numberoflike = cursor.fetchall()[0]
	return render_template('likes.html', message="People Who liked This Picture", users=likes, photoID=picture_id, number=numberoflike)
#end likes

#tags
@app.route('/tags/<picture_id>', methods=['GET', 'POST'])
@flask_login.login_required
def viewTags(picture_id):
        if request.method == 'GET':
                photo_tags=getTagsFromPicId(picture_id)
                all_tags = []
                if photo_tags == None:
                        return render_template('tags.html', message="This Image Has No Tags!", tags=all_tags)
                else:
                        for i in range(len(photo_tags)):
                                all_tags.append(photo_tags[i])
                        return render_template('tags.html', message="Here are the Tags!", tags=all_tags)
        else:
                return render_template('tags.html', message="Here are the Tags!", tags=all_tags)

@app.route('/pictureWithTag/<description>', methods=['GET'])
@flask_login.login_required
def pictureWithTag(description):
        uid = getUserIdFromEmail(flask_login.current_user.id)
        #don't want 103548 pictures, so do it by picture_id
        number_of_pics = getPhotoIdFromTag(description)
        pic_ids = []
        for i in range(len(number_of_pics)):
               pic_ids.append(number_of_pics[i][0]) 
        all_pics = []
        print(len(pic_ids))
        for x in range(len(pic_ids)):
                all_pics.append(getPhotoFromPicId(pic_ids[x]))
        return render_template('TagsAll.html', name=flask_login.current_user.id, message="Photos with this tag", photos=all_pics, tags=description)

def inTags(description):
        cursor = conn.cursor()
        cursor.execute("SELECT description FROM Tags")
        all_tags = cursor.fetchall()
        checklist = []
        for i in range(len(all_tags)):
                checklist.append(all_tags[i][0].encode('utf-8'))
        print(checklist)
        if description in checklist:
                return True
        else:
                return False
        
@app.route('/searchtags', methods=['POST', 'GET'])
def searchTags():
        search = request.form.get('search')
        if request.method == 'POST':
                result = [x.encode('utf-8') for x in search.split(' ')]
                photo = []
                for i in range(len(result)):
                        photo_id_list = []
                        if inTags(result[i]) == True:
                                photo_id_list.append(getPhotoIdFromTag(result[i]))
                                pic_id_extract = []
                                for j in photo_id_list:
                                        for x in range(len(j)):
                                                pic_id_extract.append(j[x][0])
                                for k in range(len(pic_id_extract)):
                                        photo.append(getPhotoFromPicId(pic_id_extract[k]))
                                return render_template('searchtags.html', message="Here are the search result", results=result, photos=photo)
                        else:
                                return render_template('searchtags.html', message="This Tag Doesn't Exist In Our Database")
        else:
                return render_template('searchtags.html')

@app.route('/populartags', methods=['GET'])
def populartags():
        cursor = conn.cursor()
        cursor.execute("SELECT description FROM PictureTag AS T1, Pictures AS P WHERE T1.picture_id = P.picture_id GROUP BY T1.description ORDER by COUNT(P.picture_id)")
        pop_tags = cursor.fetchall()
        tag = []
        for x in range(len(pop_tags)):
                tag.append(pop_tags[x][0])
        return render_template('populartags.html', tags=tag, message="Check out what everyone's obsessed with!")

@app.route('/youmayalsolike/<user_id>', methods=['GET'])
@flask_login.login_required
def youmayalsolike(user_id):
        most_used = getMostUsedTagByUser(user_id)
        cursor = conn.cursor()
        cursor.execute("SELECT picture_id FROM Pictures")
        all_photos = cursor.fetchall()
        tags = {}
	for i in all_photos:
		for j in most_used:
			cursor=conn.cursor()			
			cursor.execute("SELECT picture_id from Pictures AS P, PictureTag AS T1 WHERE T1.description = '{0}' AND T1.picture_id = '{1}' AND T1.picture_id=P.picture_id".format(j,i[0]))
			tags=cursor.fetchall()
			for k in tags:
				if k[0] not in tags:
					tags[k[0]] = 1
				else:
					tags[k[0]]+=1
        final_tags = sorted(tags.items(), key=operator.itemgetter(1))
        photo = []
        for key, value in final_tags:
                cursor = conn.cursor()
                cursor.execute("SELECT picture_id, imgdata FROM Pictures WHERE picture_id = '{0}'".format(key))
                photo.append(cursor.fetchall())
        return render_template('/youmayalsolike.html', photos=photo, tags=most_used)
#end tags

#comments
@app.route('/comments/<picture_id>', methods=['GET'])
def comments(picture_id):
        print("g")
	try:
		uid = getUserIdFromEmail(flask_login.current_user.id)
		return render_template('comments.html', message="Leave a comment!", addComment="True", name=flask_login.current_user.id, picture_id=picture_id)
	except:
		return render_template('comments.html', message="Leave a comment!", addComment="True", picture_id=picture_id)

@app.route('/userComment/<picture_id>', methods=['POST'])
def userComment(picture_id):
        print("g")
	text=request.form.get('comment')
	uid = getUserIdFromEmail(flask_login.current_user.id)
	email = flask_login.current_user.id
	date_comment_left=dt.datetime.today().strftime("%Y-%m-%d")
	photo_userid=getUserIdFromPicId(picture_id)
	if uid == None:
                email = 'visitor'
		cursor = conn.cursor()
		cursor.execute("INSERT INTO Comments(text, email, date_comment_left, picture_id) VALUES ('{0}', '{1}', '{2}', '{3}')".format(text, email, date_comment_left, picture_id))
		conn.commit()
	else:
		cursor = conn.cursor()
		cursor.execute("INSERT INTO Comments(text, email, date_comment_left, picture_id, user_id) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}')".format(text, email, date_comment_left, picture_id, uid))
		conn.commit()
	return render_template('comments.html', message="Comment created!", name=flask_login.current_user.id, comments=getCommentFromPicId(picture_id))
#end comments

#user activity
'''We'll measure the contribution of a user
as the number of photos they have uploaded plus the number of comments
   they have left
for photos belonging to other users. The top 10 users should be reported.'''
#gather contributions
def constribution():
        user_act = []
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, COUNT(user_id) FROM Comments AS C GROUP BY C.user_id")
        for x in cursor:
                user_act.append([x[0], x[1]])
        cursor = conn.cursor()
        cursor.execute("SELECT picture_id, COUNT(user_id) FROM Pictures AS P GROUP BY P.picture_id")
        for y in cursor:
                for z in user_act:
                        if y[0] == z[0]:
                                z[1] = z[1]+y[1]
                        else:
                                z[1] = z[1]
        return user_act

#user for key in top_users to get element
def Itemget(item):
        return item[1]
#get user ids of top users
def top_users():
        user_act = constribution()
        userlist = sorted(user_act, key=Itemget)
        top = []
        final = []
        for i in range(len(userlist)):
                if userlist[i][0] != None:
                        top.append(userlist[i])
        if len(top) >= 10:
                top = top[-9:]
                for j in top:
                        final.append(j[0])
        else:
                for k in top:
                        final.append(k[0])
#show function on website        
@app.route('/top10users', methods=['GET'])
@flask_login.login_required
def top10users():
        top10user_id = top_users()
        top10user_profiles = []
        for k in top10user_id:
                if k != None:                        
                        cursor = conn.cursor()
                        cursor.execute("SELECT email FROM Users WHERE user_id = '{0}'".format(k))
                        top10user_profiles.append(cursor.fetchone())
                else:
                        render_template('top10users.html', users=top10user_profiles)
        return render_template('top10users.html', users=top10user_profiles)

#end user activity

#default page  
@app.route("/", methods=['GET'])
def hello():
        photo = getAllPhotos()
        album = getAllAlbums()
	return render_template('hello.html', message='Welcome to Photoshare', albums=album, photos=photo)

if __name__ == "__main__":
	#this is invoked when in the shell  you run 
	#$ python app.py 
	app.run(port=8088, debug=True)
