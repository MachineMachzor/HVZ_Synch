from enum import auto
from fastapi.param_functions import File
from flask import Flask
from fastapi import FastAPI, Depends, BackgroundTasks, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.sql.expression import true
from sqlalchemy.sql.sqltypes import String
import config
from pydantic import BaseModel
from database import SessionLocal, engine, SessionLocalUserPass, engineUserPass, SessionMissions, engineMissions
from sqlalchemy.orm import Session 
from models import hvzPlayer, userPass, missions
import models
import sqlite3
import nest_asyncio
from pyngrok import ngrok
import uvicorn
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
#Hashing passwords
import bcrypt #https://stackoverflow.com/questions/40577867/bcrypt-checkpw-returns-typeerror-unicode-objects-must-be-encoded-before-checkin#:~:text=TypeError%3A%20Unicode-objects%20must%20be%20encoded%20before%20checking%20The,password%20and%20hashed_password%20must%20be%20both%20bytes%20strings. 
from starlette.middleware.sessions import SessionMiddleware
import uuid 
import traceback
from starlette.responses import FileResponse
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint
import sys
"""
todo (solved): Current problem: We can login, but global vars don't work to see if we're logged in since it'll globally change the webpage. We need a specific check (similar to row cooresponding with id when clicked in the table) for a specific person to be logged in
^fixed with sessions


TODO (done): Names are unique, but we'll record stats by first getting the id, get the name, look it up in the table, then update those values like that. Can just be one function apicall that does this, then we'll have all the data stuff to do whatever
TODO (done): Also know how to update the table
TODO: (sped thru but kinda done) Badges (make an easy way to add more without direct coding, website apicall or something)
TODO: (Done) Humanize and Zombinize doesn't work for some reason (fixed)
TODO: Users click sign up to be on the table, they'll be approved (could even do a discord webhook)
"""


app = FastAPI() #Init
app.add_middleware(SessionMiddleware, secret_key="some-secret-stringl")
# app.add_middleware(SessionMiddleware, secret_key="example")



#Specify our templates dir

# ngrok http -subdomain=inconshreveable 8000
# RUN THIS
ngrok_tunnel = ngrok.connect(8000, bind_tls=True) #bind_tls=True is https secure
print('Public URL:', ngrok_tunnel.public_url)

#Authorize the API
scope = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file'
    ]
file_name = r'D:\HVZ-main\client.json'
creds = ServiceAccountCredentials.from_json_keyfile_name(file_name,scope)
gClient = gspread.authorize(creds)

# Sheet name
googleSheetName = "HVZ Web"
#Fetch the sheet
# sheet = gClient.open(googleSheetName).sheet1
pp = pprint.PrettyPrinter() #pprint() provided by PrettyPrinter() beautifies the JSON response.

# UPDATE Cell with our link
# RUN THIS
# sheet.update_cell(1,1,ngrok_tunnel.public_url)






# nest_asyncio.apply()


#THIS COMMENTED CODE DOESN'T WORK SINCE WE'RE USING FastAPI and not FLASK
# app = Flask(__name__)
# run_with_ngrok(app)

#Creating the db
models.Base.metadata.create_all(bind=engine)
models.Base.metadata.create_all(bind=engineUserPass)
models.Base.metadata.create_all(bind=engineMissions)


#Look inside our templates folder
templates = Jinja2Templates(directory=r"D:\HVZ-main")

#Check if incoming data equals this, if so don't use it
noneVal = "none"
tagsBad = -1 

invalidPassMessage = "Invalid password"



#From the documentation
#Get our database
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_userPass_db():
    try:
        db = SessionLocalUserPass()
        yield db
    finally:
        db.close()

def get_missions_db():
    try:
        db = SessionMissions()
        yield db
    finally:
        db.close()

def verifyAdmin(request):
    try:
        #Session = deals with each UNIQUE user on the site (each "request session")
        loggedInSession = request.session.get('logged_in')
        userLogged = request.session.get("username")
        
        #Check if this user is an admin
        conn = sqlite3.connect("userPass.db")
        conn.row_factory = sqlite3.Row #Make data indexable rows
        cursor = conn.cursor() #Write to the db

        #
        cursor.execute(f"""
            SELECT isAdmin FROM userPass where username='{userLogged}'
        """)
        isAdmin = cursor.fetchall() 
        
        if len(isAdmin) >= 1:
            if isAdmin[0]['isAdmin'] == True:
                request.session['isAdmin'] = True
            else:
                request.session['isAdmin'] = False
        else:
            request.session['isAdmin'] = False #If no admin value even filled in, they're not an admin
        isAdmin = request.session.get('isAdmin')
        return isAdmin
        
        # if userLogged == "t": #The username "t" will always have admin rights (this doesn't work)
        #     request.session['isAdmin'] = True
            
    except:
        pass #keyerror exception
    return False #Keyerror, user isn't an admin

def verifyPresidentOrVP(request):
    try:
        #Session = deals with each UNIQUE user on the site (each "request session")
        loggedInSession = request.session.get('logged_in')
        userLogged = request.session.get("username")
        
        #Check if this user is an admin
        conn = sqlite3.connect("userPass.db")
        conn.row_factory = sqlite3.Row #Make data indexable rows
        cursor = conn.cursor() #Write to the db

        #
        cursor.execute(f"""
            SELECT presidentOrVP FROM userPass where username='{userLogged}'
        """)
        presidentOrVP = cursor.fetchall() 
        
        if len(presidentOrVP) >= 1:
            if presidentOrVP[0]['presidentOrVP'] == True:
                request.session['presidentOrVP'] = True
            else:
                request.session['presidentOrVP'] = False
        else:
            request.session['presidentOrVP'] = False #If no admin value even filled in, they're not an admin
        presidentOrVP = request.session.get('presidentOrVP')
        return presidentOrVP
            
    except:
        pass #keyerror exception
    return False #Keyerror, user isn't an admin


oauthScheme = OAuth2PasswordBearer(tokenUrl="token")
#Any port with token at the end
@app.post("/token")
async def token_generate(form_data: OAuth2PasswordRequestForm = Depends()):
    print(form_data)
    return {"access_token":form_data.username, "token_type":"bearer"} #Whenever someone req a token, give it data and give it type bearer


#Making the icon
favicon_path = r"D:/HVZ-main/iconTopLeft.ico"


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse(favicon_path)

@app.get('/{path:path}/favicon.ico', include_in_schema=False)
async def favicon_all(path: str):
    return FileResponse(favicon_path)

# isLoggedIn = False
# usernameForLogin = "" #If they do login, this fill be filled with a username, and we'll check the username in the DB to see if they're an admin
# isAdmin = False
# SOLVED above problem with request.session

# TODO: Find out why the request.session in the logout post method doesn't update the key for the request

#"/" base route, meaning homepage
#http://127.0.0.1:8000/docs#/
#Docs created automatically
@app.get("/")
def homepage(request: Request, db: Session = Depends(get_db), db2: Session = Depends(get_userPass_db)):
    global isLoggedIn, usernameForLogin, isAdmin
    """
    Has the table of humans and...ZOMBIES AHAHAH (View only)

    Variable "modify":"noModify" is used in layout.html to NOT display Add Player, Delete all, etc
    """
    # request.session['isAdmin'] = False #Have these session keys initialized, we can't init login here since we can't update it here
    # request.session['username'] = ""

    #For HVZ table with stats
    headers = ['Name', 'Tagged By', 'Tags', 'Moderator', "Days Alive"]
    # print(uuid.uuid4().hex[:8].upper())

    # Should codes to turn people into a zombie be similar to "164EFDD8" or "taco13294"



    conn = sqlite3.connect("userPass.db")
    conn.row_factory = sqlite3.Row #Make data indexable rows
    cursor = conn.cursor() #Write to the db
    loggedInSession = False
    isAdmin = False
    userLogged = ""
    isOnTableOrSignedUp = False
    isPresident = verifyPresidentOrVP(request)

    try:
        #Session = deals with each UNIQUE user on the site (each "request session")
        loggedInSession = request.session.get('logged_in')
        userLogged = request.session.get("username")
        

        
        if userLogged != "":
            #Check if this user is an admin
            conn = sqlite3.connect("userPass.db")
            conn.row_factory = sqlite3.Row #Make data indexable rows
            cursor = conn.cursor() #Write to the db

            #
            cursor.execute(f"""
                SELECT isAdmin FROM userPass where username='{userLogged}'
            """)
            isAdmin = cursor.fetchall() 
            # print(isAdmin)
            
            if len(isAdmin) >= 1:
                if isAdmin[0]['isAdmin'] == True:
                    request.session['isAdmin'] = True
                else:
                    request.session['isAdmin'] = False
            else:
                request.session['isAdmin'] = False #If no admin value even filled in, they're not an admin
            isAdmin = request.session.get('isAdmin')
            

            conn2 = sqlite3.connect("hvz.db")
            conn2.row_factory = sqlite3.Row #Make data indexable rows
            cursor2 = conn2.cursor() #Write to the db

            cursor2.execute(f"""
                SELECT name FROM hvzPlayers WHERE name='{userLogged}'
            """)
            userInTable = cursor2.fetchone()

            cursor.execute(f"""
                SELECT signedUp FROM userPass WHERE username='{userLogged}'
            """)
            signedUp = cursor.fetchone()['signedUp']
            if userInTable == None and isAdmin == False and (signedUp == 0 or signedUp == None): #If the user IS NOT on the table currently and isn't an admin AND they haven't already clicked sign up
                isOnTableOrSignedUp = True
        else:
            print("No user logged in")
            


        
        
        # if userLogged == "t": #The username "t" will always have admin rights (this doesn't work)
        #     request.session['isAdmin'] = True
            
    except:
        traceback.print_exc() #keyerror exception
        pass


    #Load all players from db
    conn = sqlite3.connect("hvz.db")
    conn.row_factory = sqlite3.Row #Make data indexable rows
    cursor = conn.cursor() #Write to the db
    curId = 1

    players = db.query(hvzPlayer)
    users = db2.query(userPass)
    for player in players:
        #Always refresh id's to be 1,2,3 (normal primary key id doesn't do this, we need this for the table)...
        name = player.name
        if name != None:
            cursor.execute(f"""
                UPDATE hvzPlayers SET readjustingId =  {curId} WHERE name = '{name}'
            """)
            curId += 1
    secretKey = ""
    for player in players:
        for user in users:
            if player.name == user.username and player.name == userLogged:
                secretKey = user.secretKey

    #Check if the announcements username is inserted
    # cursor.execute(f"""
    #     SELECT announcement FROM hvzPlayers WHERE name = '{config.ridiculousAnnouncementName}'
    # """)

    # Fetch the announcements
    cursor.execute(f"""
        SELECT announcement FROM hvzPlayers WHERE announcementId == 1
    """)
    
    # INSERT INTO stock (symbol, company) VALUES ('AAPL', 'Apple');
    announcements = cursor.fetchone()
    

    #Creates a spot in the player database for the announcements
    #With this, we have to realize that it's a new player, so don't give this recognition by saying if name != None (the object, or string)
    if announcements == None or announcements == "None":
        cursor.execute(f"""
            INSERT INTO hvzPlayers (announcementId, announcement) VALUES (1, ' ')
        """)
    # print(f"Announcement: {announcements}")


    cursor.close()
    conn.commit()

    gameInfo = [0, 0, 0] # TotalPlayers, numHumans, numZombies 

    




    # for player in players: #For each player in the game (in the table, players, list)
    #     if player.team == "Human":
    #         gameInfo[1] += 1
    #     elif player.team == "Zombie":
    #         gameInfo[2] += 1
    #     gameInfo[0] += 1

    # Load all users from login
    users = db2.query(userPass)
    print(f"Logged in: {loggedInSession}")

    return templates.TemplateResponse("home.html", 
    {"request": request, 
    "headers":headers,
    "players":players,
    "users": users,
    "gameInfo": gameInfo,
    "logged_in": loggedInSession, #Get the boolean if logged in
    "username": userLogged,
    "isAdmin": isAdmin,
    "isPresident": isPresident,
    "cursor": cursor,
    "isOnTableOrSignedUp": isOnTableOrSignedUp,
    "secretKey": secretKey,
    "modify":"noModify"})


@app.get("/weeklong")
def homepage(request: Request, db: Session = Depends(get_db), db2: Session = Depends(get_userPass_db)):
    global isLoggedIn, usernameForLogin, isAdmin
    """
    Has the table of humans and...ZOMBIES AHAHAH (View only)

    Variable "modify":"noModify" is used in layout.html to NOT display Add Player, Delete all, etc
    """
    # request.session['isAdmin'] = False #Have these session keys initialized, we can't init login here since we can't update it here
    # request.session['username'] = ""

    #For HVZ table with stats
    headers = ['Profile', 'Name', 'Team', 'Tagged By', 'Tags', 'Moderator', "Days Alive"]
    # print(uuid.uuid4().hex[:8].upper())

    # Should codes to turn people into a zombie be similar to "164EFDD8" or "taco13294"



    conn = sqlite3.connect("userPass.db")
    conn.row_factory = sqlite3.Row #Make data indexable rows
    cursor = conn.cursor() #Write to the db
    loggedInSession = False
    isAdmin = False
    userLogged = ""
    isOnTableOrSignedUp = False
    isPresident = verifyPresidentOrVP(request)

    try:
        #Session = deals with each UNIQUE user on the site (each "request session")
        loggedInSession = request.session.get('logged_in')
        userLogged = request.session.get("username")
        

        
        if userLogged != "":
            #Check if this user is an admin
            conn = sqlite3.connect("userPass.db")
            conn.row_factory = sqlite3.Row #Make data indexable rows
            cursor = conn.cursor() #Write to the db

            #
            cursor.execute(f"""
                SELECT isAdmin FROM userPass where username='{userLogged}'
            """)
            isAdmin = cursor.fetchall() 
            # print(isAdmin)
            
            if len(isAdmin) >= 1:
                if isAdmin[0]['isAdmin'] == True:
                    request.session['isAdmin'] = True
                else:
                    request.session['isAdmin'] = False
            else:
                request.session['isAdmin'] = False #If no admin value even filled in, they're not an admin
            isAdmin = request.session.get('isAdmin')
            

            conn2 = sqlite3.connect("hvz.db")
            conn2.row_factory = sqlite3.Row #Make data indexable rows
            cursor2 = conn2.cursor() #Write to the db

            cursor2.execute(f"""
                SELECT name FROM hvzPlayers WHERE name='{userLogged}'
            """)
            userInTable = cursor2.fetchone()

            cursor.execute(f"""
                SELECT signedUp FROM userPass WHERE username='{userLogged}'
            """)
            signedUp = cursor.fetchone()['signedUp']
            if userInTable == None and isAdmin == False and (signedUp == 0 or signedUp == None): #If the user IS NOT on the table currently and isn't an admin AND they haven't already clicked sign up
                isOnTableOrSignedUp = True
        else:
            print("No user logged in")
            


        
        
        # if userLogged == "t": #The username "t" will always have admin rights (this doesn't work)
        #     request.session['isAdmin'] = True
            
    except:
        traceback.print_exc() #keyerror exception
        pass


    #Load all players from db
    conn = sqlite3.connect("hvz.db")
    conn.row_factory = sqlite3.Row #Make data indexable rows
    cursor = conn.cursor() #Write to the db
    curId = 1

    players = db.query(hvzPlayer)
    users = db2.query(userPass)
    for player in players:
        #Always refresh id's to be 1,2,3 (normal primary key id doesn't do this, we need this for the table)...
        name = player.name
        if name != None:
            cursor.execute(f"""
                UPDATE hvzPlayers SET readjustingId =  {curId} WHERE name = '{name}'
            """)
            curId += 1
    secretKey = ""
    humansCount = 0
    zombiesCount = 0
    for player in players:
        for user in users:
            if player.name == user.username and player.name == userLogged:
                secretKey = user.secretKey
            
            if player.name == user.username:
                if player.team == "Human" or player.hiddenOZ == True:
                    humansCount += 1
                else:
                    zombiesCount += 1

    
    totalCount = humansCount + zombiesCount

    #Check if the announcements username is inserted
    # cursor.execute(f"""
    #     SELECT announcement FROM hvzPlayers WHERE name = '{config.ridiculousAnnouncementName}'
    # """)

    # Fetch the announcements
    cursor.execute(f"""
        SELECT announcement FROM hvzPlayers WHERE announcementId == 1
    """)
    
    # INSERT INTO stock (symbol, company) VALUES ('AAPL', 'Apple');
    announcements = cursor.fetchone()
    

    #Creates a spot in the player database for the announcements
    #With this, we have to realize that it's a new player, so don't give this recognition by saying if name != None (the object, or string)
    if announcements == None or announcements == "None":
        cursor.execute(f"""
            INSERT INTO hvzPlayers (announcementId, announcement) VALUES (1, ' ')
        """)
    # print(f"Announcement: {announcements}")


    cursor.close()
    conn.commit()

    gameInfo = [0, 0, 0] # TotalPlayers, numHumans, numZombies 

    




    # for player in players: #For each player in the game (in the table, players, list)
    #     if player.team == "Human":
    #         gameInfo[1] += 1
    #     elif player.team == "Zombie":
    #         gameInfo[2] += 1
    #     gameInfo[0] += 1

    # Load all users from login
    users = db2.query(userPass)

    return templates.TemplateResponse("weeklong.html", 
    {"request": request, 
    "headers":headers,
    "players":players,
    "users": users,
    "gameInfo": gameInfo,
    "logged_in": loggedInSession, #Get the boolean if logged in
    "username": userLogged,
    "isAdmin": isAdmin,
    "isPresident": isPresident,
    "cursor": cursor,
    "userInTable": userInTable,
    "isOnTableOrSignedUp": isOnTableOrSignedUp,
    "signedUp": signedUp,
    "secretKey": secretKey,
    "humansCount": humansCount,
    "zombiesCount": zombiesCount,
    "totalCount": totalCount,
    "modify":"noModify"})





@app.get("/login")
def loginPage(request: Request):
    """
    Redirects them to the page to login (submit their info)
    """
    return templates.TemplateResponse("login.html",
    {"request": request})



@app.get("/logout")
def logoutReq(request: Request):
    # request.session.pop('logged_in')
    request.session['logged_in'] = False #Make this false and reload the page
    # print(f"AdminBefore? {request.session['isAdmin']}")
        
    try:
        request.session['isAdmin'] = False
        request.session['username'] = "" #Also reset the username to nothing since they're logged out
    except:
        pass #Was never an admin
    # print(f"AdminAfter? {request.session['isAdmin']}")
    
    # print(dir(request.session))
    # print(f"Req LOGOUT: {request.session['logged_in']}")

    return templates.TemplateResponse("redirectBackToMainPage.html",
    {"request": request})

@app.get("/profile")
def profile(request: Request, db: Session = Depends(get_db), db2: Session = Depends(get_userPass_db)):
    """
    If the user is logged in, this will be their profile page
    """
    conn = sqlite3.connect("hvz.db") #Using this DB to update true values
    conn.row_factory = sqlite3.Row #Make data indexable rows
    cursor = conn.cursor() #Write to the db

    conn2 = sqlite3.connect("userPass.db") #Using this DB to update true values
    conn2.row_factory = sqlite3.Row #Make data indexable rows
    cursor2 = conn2.cursor() #Write to the db

    tableObjectPlayer = None



    if request.get('logged_in') == False:
        return "userNotLoggedIn"
    user =  request.session.get("username") #Get the loggin in username
    players = db.query(hvzPlayer)
    playerObj = None
    users = db2.query(userPass)
    
    for player in players:
        if player.name == user:
            tableObjectPlayer = player
            if player.tags != None:
                if player.tags >= 3:
                    cursor2.execute(f"""
                        UPDATE userPass SET playerTagsBadge = {True} WHERE username = '{player.name}'; 
                    """)
                    
            if player.daysAliveCount != None:
                if player.daysAliveCount >= 3:
                    cursor2.execute(f"""
                        UPDATE userPass SET daysAliveBadge = {True} WHERE username =  '{player.name}'; 
                    """)
            if player.hiddenOZ != None:
                if player.hiddenOZ == True:
                    cursor2.execute(f"""
                        UPDATE userPass SET hiddenOzBadge = {True} WHERE username =  '{player.name}'; 
                    """)
            break #Break anyways, we already found the session
    cursor.close()
    cursor2.close()
    conn.commit()
    conn2.commit()
    
    conn = sqlite3.connect("userPass.db") #Using this DB to update true values
    conn.row_factory = sqlite3.Row #Make data indexable rows
    cursor = conn.cursor() #Write to the db

    cursor.execute(f"""
        SELECT * FROM userPass where username = "{user}";
    """)
    playerObj = cursor.fetchone()
    print(f"tableObjectPlayer['customTeam'] {tableObjectPlayer.customTeam}")
    if playerObj != None: #This has to equal user, which is the session logged in, so plr has to be logged in
        return templates.TemplateResponse("profile.html",
        {"request": request,
        "user": user,
        "playerObj":playerObj,
        "tableObjectPlayer": tableObjectPlayer,
        "users": users})

class profileApiCall(BaseModel):
    webPass: str 
    profilePic: str

class changeTeam(BaseModel):
    team: str


@app.post("/profileApiCall")
def profileApi(request: Request, profileApiCall: profileApiCall):
    if profileApiCall.webPass != config.webMasterPass:
        return invalidPassMessage
    # print("inProfileApiCall")
    # print(profileApiCall.profilePic)
    #with the given user, insert their profile picture into the db
    user =  request.session.get("username")


    conn = sqlite3.connect("userPass.db")
    conn2 = sqlite3.connect("hvz.db")
    conn2.row_factory = sqlite3.Row #Make data indexable rows
    conn.row_factory = sqlite3.Row #Make data indexable rows
    cursor = conn.cursor() #Write to the db
    cursor2 = conn2.cursor() #Write to the db
    
    cursor.execute(f"""
        UPDATE userPass SET profilePic='{profileApiCall.profilePic}' WHERE username='{user}'
    """)

    cursor2.execute(f"""
        UPDATE hvzPlayers SET profilePic='{profileApiCall.profilePic}' WHERE name='{user}'
    """)

    conn2.commit()
    cursor2.close()

    conn.commit()
    cursor.close()
    print("profileAdded")
    
    return "profileAdded"
    

@app.post("/updateTeam")
def updateTeam(request: Request, changeTeam: changeTeam):
    user =  request.session.get("username")

    conn = sqlite3.connect("hvz.db")
    conn.row_factory = sqlite3.Row #Make data indexable rows
    cursor = conn.cursor() #Write to the db

    cursor.execute(f"""
        UPDATE hvzPlayers SET customTeam='{changeTeam.team}' WHERE name='{user}'
    """)
    conn.commit()
    cursor.close()
    print(f"teamUpdated for {user}")
    return "teamUpdated"




@app.get("/register")
def loginPage(request: Request):
    """
    Redirects them to the page to register (submit their info)
    """
    return templates.TemplateResponse("register.html",
    {"request": request})


class registerCriteria(BaseModel):
    username: str
    password: str
    passwordReenter: str

class loginCriteria(BaseModel):
    username: str
    password: str

class usernameToAcceptReject(BaseModel):
    username: str

class secretKeyCriteria(BaseModel):
    secretKey: str #For other person

class changeAnnouncementsReq(BaseModel):
    webPass: str 
    announcements: str



@app.post("/changeAnnouncements")
def changeAnnouncements(plrReq : changeAnnouncementsReq):
    if plrReq.webPass != config.webMasterPass:
        return invalidPassMessage

    conn = sqlite3.connect("hvz.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(f"""
        UPDATE hvzPlayers SET announcement = '{plrReq.announcements}' WHERE announcementId = 1"""
        )
    
    cursor.close()
    conn.commit()
    print("Announcements Changed")
    return "Changed"


@app.get("/announcements")
def announcements(request: Request):
    conn = sqlite3.connect("hvz.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT announcement FROM hvzPlayers WHERE announcementId = 1") #Announcements is at const id=1
    announcements = cursor.fetchone()['announcement']
    isAdmin = verifyAdmin(request) #See if the current logged in user is an admin

    print(f"announcements: {announcements}")
    return templates.TemplateResponse("announcements.html",
    {"request": request,
    "announcements": announcements,
    "isAdmin": isAdmin})



@app.post("/apiVerifyRegister")
def verifyRegister(registerPerson: registerCriteria):
    conn = sqlite3.connect("userPass.db")
    conn.row_factory = sqlite3.Row #Make data indexable rows
    cursor = conn.cursor() #Write to the db

    cursor.execute("""
        SELECT username FROM userPass
    """)
    usersList = cursor.fetchall() #Fetches all usernames in a list
    # print(usersList)
    
    #Passwords don't match
    if registerPerson.password != registerPerson.passwordReenter:
        cursor.close() 
        print(f"passwords don't match")
        return "Passwords do not match"
        # return {
        #     "code": "failed",
        #     "message": "passwords don't match"
        # } 
    
    for user in usersList:
        #Entered user already in list
        if registerPerson.username == user['username']: #If the given username equals a username already in the db
            print(f"username: {registerPerson.username} -> already in db") 
            cursor.close()
            return "userInDb"
            # return {
            # "code": "failed",
            # "message": "username already exists"
            # } 

    if " " in registerPerson.username: #Make sure there's no spaces in their username
        return "No spaces in a username"

    hashedPass = bcrypt.hashpw(registerPerson.password.encode('utf-8'), bcrypt.gensalt()).decode("utf-8") #Decode at the end to prevent encoding twice
    #Triple quotes used for single inner quotes to work as intended (to make it a string)
    secretKey = uuid.uuid4().hex[:8].upper() #Potential problem: Could give us a key already in the DB. Solution: Get all keys, while the generated key is in list of used keys - make a new key.
    
    #Generated from the select pfp and the console.log link
    defaultImg = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/4gIoSUNDX1BST0ZJTEUAAQEAAAIYAAAAAAQwAABtbnRyUkdCIFhZWiAAAAAAAAAAAAAAAABhY3NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAA9tYAAQAAAADTLQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlkZXNjAAAA8AAAAHRyWFlaAAABZAAAABRnWFlaAAABeAAAABRiWFlaAAABjAAAABRyVFJDAAABoAAAAChnVFJDAAABoAAAAChiVFJDAAABoAAAACh3dHB0AAAByAAAABRjcHJ0AAAB3AAAADxtbHVjAAAAAAAAAAEAAAAMZW5VUwAAAFgAAAAcAHMAUgBHAEIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFhZWiAAAAAAAABvogAAOPUAAAOQWFlaIAAAAAAAAGKZAAC3hQAAGNpYWVogAAAAAAAAJKAAAA+EAAC2z3BhcmEAAAAAAAQAAAACZmYAAPKnAAANWQAAE9AAAApbAAAAAAAAAABYWVogAAAAAAAA9tYAAQAAAADTLW1sdWMAAAAAAAAAAQAAAAxlblVTAAAAIAAAABwARwBvAG8AZwBsAGUAIABJAG4AYwAuACAAMgAwADEANv/bAEMAAwICAgICAwICAgMDAwMEBgQEBAQECAYGBQYJCAoKCQgJCQoMDwwKCw4LCQkNEQ0ODxAQERAKDBITEhATDxAQEP/bAEMBAwMDBAMECAQECBALCQsQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEP/AABEIACoAKgMBIgACEQEDEQH/xAAaAAACAwEBAAAAAAAAAAAAAAAABAMFBgIH/8QAKRAAAQMDAgYBBQEAAAAAAAAAAQIDBAAFERIhBhMUMUFRIgcVcYGRYf/EABoBAAIDAQEAAAAAAAAAAAAAAAAFAwQGAQL/xAAmEQABAwMDBAIDAAAAAAAAAAABAAIRAwQhQVFhBRIxgRNxYtHw/9oADAMBAAIRAxEAPwDzeiioZchuJGckOnCUJJO9WmtLyGt8lAE4C01n4JvF60JjFpC3MaEuKxqJAIAPs77d9qpZkSRAkuRJSNDjZKVAEEfojYitvwHxK1xNFjWyRAbgSZa258N6WNKRyitSVpJSUqQ4psN7KSQdQJ0kmqj6hQI9sv8A0EZUVSWWQkmO9zUE6lHOQhIGe4SBgAgVm7C+vT1B9pdgAjTGOQZyPXvdNZXV0+5fRuBEfwjf7WZooorRJyiq2/pLtudYSN1pJz6AGasqgmMtvNYdGUpOogef8qa3qCjVbUOhlSUpLwGiTK0HCE613LgrhRq+tJZ5f3G3tym9ltJSqOULJ8gK1/Ht8j+aRusCRbLjIgSlBTjK9JUDkLHcKB9EEH91OlUOOiDY+ljRWunUjDeQhmUtXM1DJOnJCUq/AAFIPPPSHC8+4pxxXdSjknxSi0YfkLm4ae4wfye5wIP0YI3AVi96LV6U4VHuBDi8Yz2uDjLZ4BE6ZEariiiimKppeSuclQ6VltYxuVLxUIcuZID1vjOoz8kKdOFD0dqeorhAcIKMjIMJWY9NkrPJtEdlogDl9QpQyPOSM9/5UkqZOe0GPZ40cpGF4kKUFH3uNqmorwKTQQduT+8+0ZIAJMDkxnWN8efKSQ7dioBcVgJzuQ54/lO0UVIhf//Z"
    cursor.execute(
        f"""INSERT INTO userPass(username, password, profilePic, secretKey) VALUES ('{registerPerson.username}', "{hashedPass}", "{defaultImg}", "{secretKey}")"""
    )

    conn.commit() #Commit our changes

    cursor.close()   
    return f"successful"

@app.post("/rejectIntoWeeklong")
def rejectIntoWeeklong(usernameToAcceptReject: usernameToAcceptReject):

    conn = sqlite3.connect("userPass.db")
    conn.row_factory = sqlite3.Row #Make data indexable rows
    cursor = conn.cursor() #Write to the db

    #Just sign them up
    cursor.execute(f"""
        UPDATE userPass SET signedUp={False} WHERE username='{usernameToAcceptReject.username}'
    """)
    conn.commit()
    cursor.close()

    return "addedToRequestTable"



@app.post("/acceptIntoWeeklong")
def acceptIntoWeeklong(usernameToAcceptReject: usernameToAcceptReject):
    """
    Given a username, accept them into the weeklong
    """
    users = sqlite3.connect("userPass.db")
    players = sqlite3.connect("hvz.db")
    players.row_factory = sqlite3.Row
    users.row_factory = sqlite3.Row
    
    cursor = users.cursor()
    cursor2 = players.cursor()

    cursor.execute(f"""
        SELECT * FROM userPass WHERE username='{usernameToAcceptReject.username}'
    """)
    user = cursor.fetchone()
    if user == None:
        return "User not found"
    
    cursor2.execute(f"""
        INSERT INTO hvzPlayers (name, profileImg, team, tags, daysAliveCount) VALUES ('{usernameToAcceptReject.username}', '{user['profilePic']}', 'Human', 0, 0)
    """)
    
    players.commit()
    cursor2.close()
    cursor.close()
    return "Accepted"



@app.post("/apiLogin")
def verifyRegister(loginPerson: loginCriteria, request: Request):
    global isLoggedIn, usernameForLogin #for accessing the vars
    """
    Given a username and a password, verify if it's in the database
    If true, set theirLoggedIn=True, else, give an error
    """

    conn = sqlite3.connect("userPass.db")
    conn.row_factory = sqlite3.Row #Make data indexable rows
    cursor = conn.cursor() #Write to the db

    cursor.execute(f"""
        SELECT password FROM userPass where username='{loginPerson.username}'
    """)
    password = cursor.fetchall() #Fetches all usernames in a list
    if len(password) == 1:
        if bcrypt.checkpw(loginPerson.password.encode('utf-8'), password[0]['password'].encode('utf-8')): #Check if the inputted loginPerson entered a password equal to the password already in the DB for the username
            
            
            #Set this user to be logged in where it's their username in the db (means this person is logged in)
            # cursor.execute(f"""
            #     UPDATE userPass SET isLoggedIn = {True} WHERE username = "{loginPerson.username}"
            # """)
            request.session['logged_in'] = True #For this current session, the user is logged in
            request.session['username'] = loginPerson.username
            
            conn.commit()
            cursor.close()


            return "success" #If so return success
            

    cursor.close()
    return "Username does not exist or password is incorrect" #If not, return error



@app.post("/checkSecretKey")
def verifySecretKey(secretKey: secretKeyCriteria, request: Request):
    conn = sqlite3.connect("userPass.db")
    conn.row_factory = sqlite3.Row #Make data indexable rows
    cursor = conn.cursor() #Write to the db


    #From our userPass db (just holds info specific to each user) if we find a user with the secret key
    cursor.execute(f"""
        SELECT username FROM userPass where secretKey='{secretKey.secretKey}'
    """)

    username = cursor.fetchall() #If this is 1, then a username has this secret key
    if len(username) == 1:
        makePlayerZombie = username[0]['username'] #Get the username
        cursor.close()
        conn = sqlite3.connect("hvz.db") #From our table of players
        conn.row_factory = sqlite3.Row #Make data indexable rows
        cursor = conn.cursor() #Write to the db

        cursor.execute(f""" 
            SELECT name FROM hvzPlayers where name='{makePlayerZombie}'
        """)

        foundUser = cursor.fetchall()  #Given the username, now search the table of active players. If they're active, make them a zombie
        

        cursor.execute(f""" 
            SELECT team FROM hvzPlayers where name='{makePlayerZombie}'
        """)

        foundTeam = cursor.fetchall() #We want to make sure they're not already a zombie
        
        
        if len(foundUser) == 1: #If the player IS in the table (if this isn't, the function won't return/do anything)
            if foundTeam[0]['team'] == "Human":
                # UPDATE hvzPlayers SET name = 'Jordan' WHERE readjustingId =  1;
                cursor.execute(f""" 
                    UPDATE hvzPlayers SET team='Zombie' WHERE name='{makePlayerZombie}'
                """)
                cursor.close()
                conn.commit()

                #Add 1 to the tags of the current logged in user since they guessed the secret key
                addOneTagToThisUser = request.session.get("username")
                conn = sqlite3.connect("hvz.db")
                conn.row_factory = sqlite3.Row #Make data indexable rows
                cursor = conn.cursor() #Write to the db

                cursor.execute(f"""
                    SELECT tags FROM hvzPlayers WHERE name =  '{addOneTagToThisUser}'
                """)
                playerTags = int(cursor.fetchone()[0]) + 1 #Get the current value there and just add 1
                print(playerTags)
                cursor.execute(f"""
                    UPDATE hvzPlayers SET tags = '{playerTags}' WHERE name =  '{addOneTagToThisUser}'
                """)

        


                cursor.execute(f"""
                    SELECT hiddenOZ FROM hvzPlayers where name = '{addOneTagToThisUser}'
                """)
                hiddenOZ = bool(cursor.fetchone()[0])  
                if hiddenOZ:
                    taggedPersonName = "Hidden OZ"
                else:
                    taggedPersonName = addOneTagToThisUser
                
                cursor.execute(f"""
                    UPDATE hvzPlayers SET taggedBy = '{taggedPersonName}' WHERE name = '{makePlayerZombie}'
                """)

                conn.commit()
                cursor.close()

                return "success"



                # cursor.close()

                cursor.close() #Close our connection, then COMMIT (push) everything onto the db
                conn.commit()
                return "success"
                # print(f"addOneTagToThisUser: {addOneTagToThisUser}")
                #And return the user found that had their secret key found to a zombie
                # return [addOneTagToThisUser,makePlayerZombie]
        

@app.get("/missions")
def missions(request: Request, db: Session = Depends(get_missions_db)):
    
    headers = ['Date Time Location', "Description"]
    isAdmin = verifyAdmin(request) #See if the current logged in user is an admin
    # allMissions = db.query(missions) #TODO: Problem line


    conn = sqlite3.connect("missions.db")
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()

    cursor.execute(""" SELECT * FROM missions
    """)

    allMissions = cursor.fetchall()

    curId = 1

    #Update the readjustId param
    for mission in allMissions:
        #A normal id isn't readjusting itself when an element is deleted, so this ensures that this happens
        cursor.execute(f"""
            UPDATE missions SET readjustingId = {curId} WHERE id = {mission['id']}""")
        curId += 1
    

    cursor.close()
    conn.commit()
    
     
    return templates.TemplateResponse("missions.html",
    {"request": request,
    "headers": headers,
    "isAdmin": isAdmin,
    "allMissions": allMissions})
    # "allMissions": allMissions})






# @app.get("/modifyWebsitePort")
# def modifyWebSitePort(request: Request, db: Session = Depends(get_db)):
#     """
#     Able to modify the zombies and humans table with this port
#     NOTE that this is stupid, or maybe it isn't not sure. Ideally, we'd use an admin login check to modify the site, but this is TODO
#     """

#     #For HVZ table with stats
#     headers = ['Name', 'Team', 'Tagged By', 'Tags', 'Moderator', 'Days Alive']

#     #Load all players into db
#     players = db.query(hvzPlayer)


#     return templates.TemplateResponse("view.html", 
#     {"request": request, 
#     "headers":headers,
#     "players":players,
#     "modify":"yesModify"}) #"view":"NoView" means we don't wanna show buttons and stuff to modify


#Model what our api request looks like (specify the info in the json payload)
class AddPlayerRequest(BaseModel):
    webPass: str
    name: str #We only need a name to add them


class ChangePlayerRequest(BaseModel):
    #NOTE: No one will pass the int id for someone, our program will do this somehow (with getting the row for the table)
    #But we need an identifier since names aren't unique (NAH, names are unique, but we'll record stats from this id, get the name, look it up in the table, then update those values like that)
    id: int
    name: str
    team: str
    taggedBy: str
    tags: int
    daysAliveCount: int


class IncrementDecrementTag(BaseModel):
    username: str #Just need the id since we'll fetch the tag for the id

class deleteAll(BaseModel):
    webPass: str #At least have a password for this

class approveBaseClass(BaseModel):
    webPass: str #At least have a password for this
    name: str


class changeAttribute(BaseModel):
    username: str


class hiddenOZUser(BaseModel):
    username: str

class zombinizeOrHumanize(BaseModel):
    username: str
    team: str # "Zombie" "Human"

class addMissionTemplate(BaseModel):
    webPass: str 
    dateAndTime: str
    description: str 

@app.post("/incDaysEveryday")
def incDaysEveryday(plrReq : deleteAll):
    """
    This will be ran at 12am everyday to increase the days survived
    """
    conn = sqlite3.connect("hvz.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor() #Connect to our db


    cursor.execute(f"""
        SELECT * FROM hvzPlayers
    """)

    players = cursor.fetchall()
    for player in players:
        curDaysAlive = player['daysAliveCount']
        # notOz = (player['hiddenOZ'] == False or player['hiddenOZ'] == None) #not oz
        isAHuman = player['team'] == 'Human' or player['hiddenOZ'] == True
        print(f"{player['name']} {isAHuman}")
        # team = 
        if curDaysAlive == None:
            curDaysAlive = 1 #0 = None, so we just make it 1 to inc their survived days
        else:
            curDaysAlive += 1 #Otherwise just add 1
        if isAHuman: #notOz -> would just give away the OZ lmao
            cursor.execute(f"""
                UPDATE hvzPlayers SET daysAliveCount = '{curDaysAlive}' WHERE name =  "{player['name']}"
            """)

    
    cursor.close() #Close our connection, then COMMIT (push) everything onto the db
    conn.commit()
    return "Updated everyones daysAlive by 1 ;)"

# Note the trash security here. We tried to supply a pass, but that doesn't work. Just make sure the current logged in user is an admin
@app.get("/printSecretKeysPage")
def printSecretKeysPage(request: Request, db: Session = Depends(get_db), db2: Session = Depends(get_userPass_db)):
    # if plrReq.webPass != config.webMasterPass:
    #     return invalidPassMessage
    
    user = request.session.get("username")
    players = db.query(hvzPlayer)
    users = db2.query(userPass)
    isAdmin = verifyAdmin(request)

    return templates.TemplateResponse("printSecretKeysPage.html",
    {"request": request,
    "players": players,
    "users": users,
    "isAdmin": isAdmin})

@app.get("/viewSignedUpPlayers")
def viewPlayersSignedUp(request: Request, db: Session = Depends(get_db), db2: Session = Depends(get_userPass_db)):
    players = db.query(hvzPlayer)
    users = db2.query(userPass)
    playersInTable = []

    for player in players:
        playersInTable.append(player.name)

    # print(playersInTable)
    isAdmin = verifyAdmin(request)
    
    return templates.TemplateResponse("viewPlayersSignedUp.html",
    {"request": request,
    "users": users,
    "isAdmin": isAdmin,
    "playersInTable": playersInTable})

@app.post("/requestToPlayApiCall")
def requestToPlayApiCall(plrRequest: deleteAll, request: Request):
    if config.webMasterPass != plrRequest.webPass:
        return invalidPassMessage
    conn = sqlite3.connect("userPass.db")
    conn.row_factory = sqlite3.Row #Make data indexable rows
    cursor = conn.cursor() #Write to the db

    user =  request.session.get("username")

    #Just sign them up
    cursor.execute(f"""
        UPDATE userPass SET signedUp={True} WHERE username='{user}'
    """)
    conn.commit()
    cursor.close()

    return "addedToRequestTable"



@app.post("/getAnnouncements")
def getAnnouncements(plrReq : deleteAll):
    if plrReq.webPass != config.webMasterPass:
        return invalidPassMessage
    conn = sqlite3.connect("hvz.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(f"""
        SELECT announcement FROM hvzPlayers WHERE announcementId == 1
    """)
    # INSERT INTO stock (symbol, company) VALUES ('AAPL', 'Apple');
    announcements = cursor.fetchone()['announcement']
    return announcements

@app.post("/makeOZ")
def makeOZ(plrReq : hiddenOZUser):
    conn = sqlite3.connect("hvz.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(f"""
        SELECT hiddenOz from hvzPlayers where name='{plrReq.username}'
    """)
    hiddenOzTrueFalse = cursor.fetchone()['hiddenOz']
    print(hiddenOzTrueFalse)
    if hiddenOzTrueFalse == None or hiddenOzTrueFalse == 0:
        hiddenOzTrueFalse = True
    else:
        hiddenOzTrueFalse = False #If it's true, switch to false


    cursor.execute(f"""
        UPDATE hvzPlayers SET hiddenOz = {hiddenOzTrueFalse} WHERE name='{plrReq.username}'
    """)
    # Make them a zombie
    cursor.execute(f"""
        UPDATE hvzPlayers SET team = 'Zombie' WHERE name='{plrReq.username}'
    """)
    # UPDATE hvzPlayers SET hiddenOz = true WHERE readjustingId = 1

    cursor.close()
    conn.commit()


    return "Changed"




#Tag count += 1
@app.post("/addTag")
def incTag(plrRequest: IncrementDecrementTag):
    """
    Increments a players tag given id
    
    """
    conn = sqlite3.connect("hvz.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor() #Connect to our db

    cursor.execute(f"""
        SELECT tags FROM hvzPlayers WHERE name =  '{plrRequest.username}'
    """)
    playerTags = int(cursor.fetchone()[0]) + 1 #Get the current value there and just add 1
    print(playerTags)
    # print(playerTags)
    cursor.execute(f"""
        UPDATE hvzPlayers SET tags = '{playerTags}' WHERE name =  '{plrRequest.username}'
    """)
    cursor.close() #Close our connection, then COMMIT (push) everything onto the db
    conn.commit()

    return playerTags #We'll use this to update the page dynamically (without refreshing)

@app.post("/decTag")
def decTag(plrRequest: IncrementDecrementTag):
    """
    Decrements a players tag given id
    
    """
    conn = sqlite3.connect("hvz.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor() #Connect to our db

    cursor.execute(f"""
        SELECT tags FROM hvzPlayers WHERE name =  '{plrRequest.username}'
    """)
    playerTags = int(cursor.fetchone()[0]) - 1 #Get the current value there and just sub 1
    print(playerTags)
    # print(playerTags)
    cursor.execute(f"""
        UPDATE hvzPlayers SET tags = '{playerTags}' WHERE name =  '{plrRequest.username}'
    """)
    cursor.close() #Close our connection, then COMMIT (push) everything onto the db
    conn.commit()

    return playerTags

#For the secret key tags increase and zombinize (turn plr into zombie)
class secretChange(BaseModel):
    webPass: str
    name: str #This name shifts between the original and the zombie
    nameOfOriginalTagger: str #This is for when we want to update the taggedBy (go check the /secretAddTag api call in html)

#For the secret key adding tags
@app.post("/secretAddTag")
def secretAddTag(plrRequest: secretChange):
    """
    Decrements a players tag given name 
    
    """
    conn = sqlite3.connect("hvz.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor() #Connect to our db

    cursor.execute(f"""
        SELECT team FROM hvzPlayers WHERE name = '{plrRequest.name}'
    """)
    team = cursor.fetchone()['team']
    if team == "Zombie": #Only if the player entering the secret key is a zombie

        cursor.execute(f"""
            SELECT tags FROM hvzPlayers WHERE name = '{plrRequest.name}'
        """)
        playerTags = int(cursor.fetchone()[0]) + 1 #Get the current value there and just sub 1
        print(playerTags)
        # print(playerTags)
        cursor.execute(f"""
            UPDATE hvzPlayers SET tags = '{playerTags}' WHERE name = '{plrRequest.name}'
        """)
        cursor.close() #Close our connection, then COMMIT (push) everything onto the db
        conn.commit()

        return "success"
    return "Player entering secret key is a zombie"

@app.post("/secretZombinize")
def secretZombinize(plrRequest: secretChange):
    conn = sqlite3.connect("hvz.db")
    conn.row_factory = sqlite3.Row #Make data indexable rows
    cursor = conn.cursor() #Write to the db



    #Just update their team
    cursor.execute(f"""
            UPDATE hvzPlayers SET team = 'Zombie' WHERE name = '{plrRequest.name}'
    """)

    #Then their taggedby
    cursor.execute(f"""
            UPDATE hvzPlayers SET taggedBy = '{plrRequest.nameOfOriginalTagger}' WHERE name = '{plrRequest.name}'
    """)

    #We want the id of the Zombie to set their ID on the website
    cursor.execute(f"""
        SELECT id FROM hvzPlayers WHERE name='{plrRequest.name}'
    """)
    idZombie = cursor.fetchone()['id']

    #We want the id of the Human also just to return it for html realtime updating purposes
    cursor.execute(f"""
        SELECT id FROM hvzPlayers WHERE name='{plrRequest.nameOfOriginalTagger}'
    """)
    print(plrRequest.nameOfOriginalTagger)

    idHuman = cursor.fetchone()['id']-1

    #Now we want the incremented tags
    cursor.execute(f"""
        SELECT tags FROM hvzPlayers WHERE readjustingId = {idHuman}
    """)
    tags = cursor.fetchone()['tags']

    cursor.close()
    conn.commit()
    return f"{idZombie}T{idHuman}T{tags}"

@app.post("/zombinizeOrHumanize")
def zombinizeOrHumanize(plrRequest: zombinizeOrHumanize):
    conn = sqlite3.connect("hvz.db")
    conn.row_factory = sqlite3.Row #Make data indexable rows
    cursor = conn.cursor() #Write to the db

    cursor.execute(f"""
        UPDATE hvzPlayers SET team = '{plrRequest.team}' WHERE name = '{plrRequest.username}'
    """)
    cursor.close()
    conn.commit()
    return "success"



@app.post("/addMission")
def addMission(addMission : addMissionTemplate):
    if addMission.webPass != config.webMasterPass:
        return invalidPassMessage
    
    conn = sqlite3.connect("missions.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(f"""
        INSERT INTO missions (dateAndTime, description) VALUES ('{addMission.dateAndTime}', '{addMission.description}')
    """)

    cursor.close()
    conn.commit()
    print("missionAdded")
    return "Mission Added"

@app.post("/delMission")
def delMission(delMission : changeAttribute):
    if delMission.webPass != config.webMasterPass:
        return invalidPassMessage
    conn = sqlite3.connect("missions.db")
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()

    cursor.execute(f"""
        DELETE FROM missions WHERE readjustingId = {delMission.id}
    """)
    cursor.close()
    conn.commit()
    print("deleted mission")
    return "deleted mission"
    
    

@app.post("/modPlayer")
def modPlayerOnWeb(plrRequest: changeAttribute):
    
    username = plrRequest.username

    #Now go to the userPass db after getting the username from the table
    conn = sqlite3.connect("hvz.db")
    conn.row_factory = sqlite3.Row #Access items by ['attributeName']
    cursor = conn.cursor() #Connect to our db

    cursor.execute(f"""
        SELECT ifMod FROM hvzPlayers where name='{username}'
    """)
    modStatus = bool(cursor.fetchone()[0]) #Fetches all usernames in a list

    # if modStatus == None:
    #     modStatus = False
    modStatus = not modStatus
    # print(modStatus)
    # return "Test"
    cursor.execute(f"""
        UPDATE hvzPlayers SET ifMod = {modStatus} WHERE name = '{username}'
    """)
    conn.commit()
    cursor.close()
    return "SwappedModStatus"

    


@app.post("/deModPlayer")
def modPlayerOnWeb(plrRequest: changeAttribute):
    if plrRequest.webPass != config.webMasterPass:
        return invalidPassMessage

    

    conn = sqlite3.connect("hvz.db")
    conn.row_factory = sqlite3.Row #Access items by ['attributeName']
    cursor = conn.cursor() #Connect to our db
    
    #First get the name
    cursor.execute(f"""
        SELECT name FROM hvzPlayers WHERE readjustingId = {plrRequest.id}
    """)

    username = cursor.fetchone()['name'] #name = username since they're in the table
    cursor.close()

    #Now go to the userPass db after getting the username from the table
    conn = sqlite3.connect("userPass.db")
    conn.row_factory = sqlite3.Row #Access items by ['attributeName']
    cursor = conn.cursor() #Connect to our db

    cursor.execute(f"""
        SELECT password FROM userPass where username='{username}'
    """)
    password = cursor.fetchall() #Fetches all usernames in a list
    if len(password) == 1: #If this username exists
        cursor.execute(f"""
            UPDATE userPass SET isAdmin = {False} WHERE username = '{username}'
        """)
        cursor.close()
        conn.commit()
        #The user was made an admin, but we want to display true. mods don't have the power to unmod people
        return "False"#f"{username} was made an admin: {adminInfo.makeAdmin}"
    else:
        cursor.close()
        return "Username not in DB"

    








@app.post("/modifyVal")
def modifyPlayer(plrRequest: ChangePlayerRequest):
    conn = sqlite3.connect("hvz.db")
    conn.row_factory = sqlite3.Row #Make data indexable rows
    cursor = conn.cursor() #Write to the db
    # cursor.execute("""
    #     SELECT * FROM hvzPlayers;
    # """)

    # players = cursor.fetchall()
    # for player in players:
    #     print(player['name'])
    
    #For the given id (will be auto recieved from clicking on a row, and filling in a value)
    """
    Accessing by ID which will be called appropiately for the table click (readjustingId =  tableRow)
    If the request contains a value that's not our specified nonevalue, UPDATE it in the SQL database. 
    """
    if plrRequest.name != noneVal:
        cursor.execute(f"""
            UPDATE hvzPlayers SET name = '{plrRequest.name}' WHERE readjustingId =  {plrRequest.id};
        """)
        
    if plrRequest.team != noneVal:
        cursor.execute(f"""
            UPDATE hvzPlayers SET team = '{plrRequest.team}' WHERE readjustingId = {plrRequest.id};
        """)
        
        
    if plrRequest.taggedBy != noneVal:
        cursor.execute(f"""
            UPDATE hvzPlayers SET taggedBy = '{plrRequest.taggedBy}' WHERE readjustingId =  {plrRequest.id};
        """)
    if plrRequest.tags != tagsBad:
        cursor.execute(f"""
            UPDATE hvzPlayers SET tags = '{plrRequest.tags}' WHERE readjustingId =  {plrRequest.id};
        """)

    # cursor.execute("""
    #     SELECT * FROM hvzPlayers;
    # """)

    # players = cursor.fetchall()
    # for player in players:
    #     print(player['name'])

    # if team != noneVal:
    #     plr.team = team
    # if taggedBy != noneVal:
    #     plr.taggedBy = taggedBy
    # if tags != noneVal:
    #     plr.tags = tags
    cursor.close() #Commit it to
    conn.commit()
    
    return plrRequest.taggedBy


def addPlayerToTable(plrRequest, db):
    conn = sqlite3.connect("userPass.db")
    conn.row_factory = sqlite3.Row #Access items by ['attributeName']
    cursor = conn.cursor() #Connect to our db

    #A registered username has a password recorded within our db
    cursor.execute(f""" 
        SELECT password FROM userPass where username='{plrRequest.name}'
    """)

    password = cursor.fetchall() #Fetches all usernames in a list
    if len(password) == 1: #If this username exists
        #Also check if the username is ALREADY added on the table
        #List all usernames in table
        
        #Load all players from db (db.query(hvzPlayer)) and get their names
        playersList = [] #Have all the usernames in a list
        for player in db.query(hvzPlayer):
            playersList.append(player.name) #Get all their names O(n)

        #Only if the user we're trying to add to the table isn't in the playersList
        if plrRequest.name not in playersList: 

        

            plr = hvzPlayer() #Our player object (model)
            plr.name = plrRequest.name #The objects name is the incoming name in the request
            #Forcing their name to be their username
            
            #Fill in some defaults
            plr.tags = 0
            plr.team = "Human" #Initialize them to be a human



            db.add(plr)
            db.commit()

            return {
                "code": "success",
                "message": "Player Created"
            }
        else:
            print("userAlreadyInTable - tried to add from search")
            return "userAlreadyInTable"
    else:
        print("usernameNotRegistered - tried to add from search")
        return "usernameNotRegistered"

#db connects to our actual db
@app.post("/addPlayer")
def createPlayer(plrRequest: AddPlayerRequest, db: Session = Depends(get_db)):
    """
    Insert a new player. First verify if the name is an exact match within the username list
    """
    plrRequest.name = plrRequest.name.strip() #Remove spaces (No spaces are allowed anyways, javascript will add spaces when scraping it from the table)
    conn = sqlite3.connect("userPass.db")
    conn.row_factory = sqlite3.Row #Access items by ['attributeName']
    cursor = conn.cursor() #Connect to our db

    

    cursor.execute(f"""
        UPDATE userPass SET signedUp = {False} WHERE username = '{plrRequest.name}'
    """)
    conn.commit()

    #A registered username has a password recorded within our db
    cursor.execute(f""" 
        SELECT password FROM userPass where username='{plrRequest.name}'
    """)
    

    password = cursor.fetchall() #Fetches all usernames in a list
    if len(password) == 1: #If this username exists
        #Also check if the username is ALREADY added on the table
        #List all usernames in table
        
        #Load all players from db (db.query(hvzPlayer)) and get their names
        playersList = [] #Have all the usernames in a list
        for player in db.query(hvzPlayer):
            playersList.append(player.name) #Get all their names O(n)

        #Only if the user we're trying to add to the table isn't in the playersList
        if plrRequest.name not in playersList: 

        

            plr = hvzPlayer() #Our player object (model)
            plr.name = plrRequest.name #The objects name is the incoming name in the request
            #Forcing their name to be their username
            
            #Fill in some defaults
            plr.tags = 0
            plr.team = "Human" #Initialize them to be a human




            db.add(plr)
            db.commit()

            return {
                "code": "success",
                "message": "Player Created"
            }
        else:
            print("userAlreadyInTable - tried to add from search")
            return "userAlreadyInTable"
    else:
        print("usernameNotRegistered - tried to add from search")
        return "usernameNotRegistered"


#We'll at least send a password here to verify
@app.post("/deleteAll")
def deleteAllPlayers(plrReq: deleteAll):
    """
    Removes all players from the dataset
    """
    if plrReq.webPass != config.webMasterPass:
        return {
            "code": "failed",
            "message": "Wrong password"
        }
    else:
        conn = sqlite3.connect("hvz.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor() #Connect to our db

        # Just delete the whole database (not the table itself, just the data)
        cursor.execute("""
            DELETE FROM hvzPlayers;
        """)

        cursor.close() #Close the connection and commit our changes
        conn.commit()

        return {
            "code": "success",
            "message": "Deleted all players"
        }

class adminInfo(BaseModel):
    username: str 
    webPass: str #At least have a password for this
    makeAdmin: bool #False, REVOKE admin, True, MAKE admin



@app.post("/makeAdmin")
def makeAdmin(adminInfo: adminInfo):
    """
    This apicall should be called by the webhost (LilGubbins) only to make others admins
    """
    if adminInfo.webPass != config.webMasterPass:
        return invalidPassMessage
    conn = sqlite3.connect("userPass.db")
    conn.row_factory = sqlite3.Row #Access items by ['attributeName']
    cursor = conn.cursor() #Connect to our db

    cursor.execute(f"""
        SELECT password FROM userPass where username='{adminInfo.username}'
    """)
    password = cursor.fetchall() #Fetches all usernames in a list
    if len(password) == 1: #If this username exists
        cursor.execute(f"""
            UPDATE userPass SET isAdmin = {adminInfo.makeAdmin} WHERE username = '{adminInfo.username}'
        """)
        cursor.close()
        conn.commit()
        return f"{adminInfo.username} was made an admin: {adminInfo.makeAdmin}"
    else:
        cursor.close()
        return "Username not in DB"

@app.post("/makePresidentOrVP")
def makeAdmin(adminInfo: adminInfo):
    """
    This apicall should be called by the webhost (LilGubbins) only to make others admins
    """
    if adminInfo.webPass != config.webMasterPass:
        return invalidPassMessage
    conn = sqlite3.connect("userPass.db")
    conn.row_factory = sqlite3.Row #Access items by ['attributeName']
    cursor = conn.cursor() #Connect to our db

    cursor.execute(f"""
        SELECT password FROM userPass where username='{adminInfo.username}'
    """)
    password = cursor.fetchall() #Fetches all usernames in a list
    if len(password) == 1: #If this username exists
        cursor.execute(f"""
            UPDATE userPass SET presidentOrVP = {adminInfo.makeAdmin} WHERE username = '{adminInfo.username}'
        """)
        cursor.close()
        conn.commit()
        return f"{adminInfo.username} was made the president: {adminInfo.makeAdmin}"
    else:
        cursor.close()
        return "Username not in DB"


@app.post("/addDay")
def addDay(changeAttribute: changeAttribute):
    """
    Increments a player's days alive
    
    """
    conn = sqlite3.connect("hvz.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor() #Connect to our db

    cursor.execute(f"""
        SELECT daysAliveCount FROM hvzPlayers WHERE name = '{changeAttribute.username}'
    """)
    days = cursor.fetchone()[0]
    if days == None:
        days = 0
    else:
        days = int(days)

    playerTags = days + 1 #Get the current value there and just sub 1
    print(playerTags)
    cursor.execute(f"""
        UPDATE hvzPlayers SET daysAliveCount = '{playerTags}' WHERE name = '{changeAttribute.username}'
    """)
    cursor.close() #Close our connection, then COMMIT (push) everything onto the db
    conn.commit()

    return playerTags

@app.post("/decDay")
def decDay(changeAttribute: changeAttribute): 
    """
    Decrements a player's days alive
    
    """
    conn = sqlite3.connect("hvz.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor() #Connect to our db

    cursor.execute(f"""
        SELECT daysAliveCount FROM hvzPlayers WHERE name =  '{changeAttribute.username}'
    """)

    days = cursor.fetchone()[0]
    if days == None:
        days = 0
    else:
        days = int(days)
    playerTags = days - 1 #Get the current value there and just sub 1
    print(playerTags)
    cursor.execute(f"""
        UPDATE hvzPlayers SET daysAliveCount = '{playerTags}' WHERE name =  '{changeAttribute.username}'
    """)
    cursor.close() #Close our connection, then COMMIT (push) everything onto the db
    conn.commit()

    return playerTags

#Adds 1 day to every human (we just want the webpass)
@app.post("/addAllDays")
def addDayToAllHumans(webPassReq : deleteAll):
    """
    Add 1 to all human days. This endpoint should be hit automatically everyday (just send a python post request to a webhook the same way it is for discord)
    """

    if webPassReq.webPass != config.webMasterPass:
        return invalidPassMessage
    
    conn = sqlite3.connect("hvz.db") 
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    #Select all id's
    cursor.execute("""
        SELECT id from hvzPlayers
    """)
    allIds = cursor.fetchall() #
    for id in allIds:
        #With all ids, select their current days alive
        cursor.execute(f"""
            SELECT daysAliveCount FROM hvzPlayers WHERE readjustingId =  {id['id']}
        """)

        #Turn days into an int
        days = cursor.fetchone()[0]
        if days == None:
            days = 0
        else:
            days = int(days)

        #Select the team from the id
        cursor.execute(f"""
            SELECT team FROM hvzPlayers WHERE readjustingId =  {id['id']}
        """)

        team = cursor.fetchone()['team']
        if team == "Human": #Only if they're a human
            playerTags = days + 1 #Get the current value there and just add 1
            cursor.execute(f"""
                UPDATE hvzPlayers SET daysAliveCount = '{playerTags}' WHERE readjustingId =  {id['id']}
            """)
    conn.commit()
    cursor.close()
    return "Updated human days"




@app.post("/delPlayer")
def delPlayer(changeAttribute: changeAttribute):

    """
    Within the table, delete a player
    """
    
    conn = sqlite3.connect("hvz.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor() #Connect to our db

    cursor.execute(f"""
        DELETE FROM hvzPlayers WHERE name = '{changeAttribute.username}'
    """)
    cursor.close()
    conn.commit()
    return "deletedPlayer"



@app.post("/scrapeUsernameList") 
def scrapeUsernameList(changeAttribute: deleteAll, db: Session = Depends(get_userPass_db)): #Using a deleteAll request template here since we should just verify the password
    if changeAttribute.webPass != config.webMasterPass:
        return invalidPassMessage
    
    #Query (get) all info from db
    users = db.query(userPass)
    usernames = []
    for user in users:
        usernames.append(user.username) #Get all the usernames
    
    return usernames
    




    



# app.run()  

# RUN THIS
uvicorn.run(app, port=8000)


# uvicorn main:app --reload  (run it locally)

# Browna29@newpaltz.edu


"""
Dummy payload & SQL stuff to re-look at

"id": 1,
    "name": "charlie",
		"team": "Zombie",
		"status": "none",
		"taggedBy": "none",
		"tags": 0


    SELECT symbol FROM stock where readjustingId =  2;
    SELECT id, symbol FROM stock;
    INSERT INTO stock (symbol, company) VALUES ('AAPL', 'Apple');
    DELETE FROM hvzPlayers WHERE readjustingId = {changeAttribute.id}

    UPDATE hvzPlayers SET name = 'Jordan' WHERE readjustingId =  1;
"""
