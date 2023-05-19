##IMPORTS/SETUP

from flask import Flask, render_template
from flask import Flask, render_template, request
import requests
from flask_mysqldb import MySQL
import numpy as np
app=Flask(__name__) 
app.config['MYSQL_HOST']='mysql.2223.lakeside-cs.org'
app.config['MYSQL_USER']='student2223'
app.config['MYSQL_PASSWORD']='m545CS42223'
app.config['MYSQL_DB']='2223project_1'
app.config['MYSQL_CURSORCLASS']='DictCursor'
mysql=MySQL(app)                               

##ROUTES

@app.route('/')
def index():
    return render_template('index.html.j2')

@app.route('/auctions')
def auctions():
    response=requests.get("https://api.hypixel.net/skyblock/auctions")
    jsonResponse=response.json()
    auctions=jsonResponse["auctions"]
    return render_template('auctions.html.j2', auctions=auctions)

@app.route('/trending')
def trending():
    cursor=mysql.connection.cursor()
    query="SELECT * FROM evantran_views"
    cursor.execute(query)
    mysql.connection.commit()
    data=cursor.fetchall()
    sort=sorted(data, key=lambda i: i['views'], reverse=True) #Sorts the views from biggest to smallest
    return render_template('trending.html.j2', data=sort)

@app.route('/about')
def about():
        return render_template('about.html.j2')

@app.route('/item', methods=['GET'])
def item():
    searchName=request.values.get("name").title()
    error=False 
    item=[0 for x in range(5)]
    cache=[0 for x in range(5)]
    i=0
    while i < 5:
        item[i]=processing(i, searchName)[0]
        i+=1

    j=0
    while j < 5:
        if processing(j, searchName)[1]==True: 
            views(searchName)
            j+=1
            break
        else:
            error=True
            break

    return render_template('item.html.j2', item=item, name=searchName, error=error, debug=processing(i, searchName)[1]==True)

##FUNCTIONS

#Fuction takes a user's search query and pulls all entries from the API that matches the user's search
def processing(page,name): 
    response=requests.get("https://api.hypixel.net/skyblock/auctions?page="+str(page))
    jsonResponse=response.json()
    auctions=jsonResponse["auctions"]
    h=len(auctions)
    auc1=[0 for x in range(h)]
    i=0
    j=0
    k=0
    found=False
    while i < h:
        if name in auctions[i].get("item_name").title():
            auc1[j]=auctions[i]
            num=price(auctions[i]["highest_bid_amount"], math=True)
            auc1[j]["highest_bid_amount"]=f"{num:,}"
            num=price(auctions[i]["starting_bid"], math=False)
            auc1[j]["starting_bid"]=f"{num:,}"
            colors(auc1,j)
            i+=1
            j+=1
            k+=1
            found=True
        else:
            auc1[i]="del"
            i+=1
    l=0
    auc2=[0 for x in range(k)]
    while l < k:
        auc2[l]=auc1[l]
        l+=1

    return auc2, found

#Fuction modifies the SQL-table evantran_views
def views(name):
    cursor=mysql.connection.cursor()
    query="SELECT * FROM evantran_views WHERE item_name=%s;"
    queryVars=(name,)
    cursor.execute(query, queryVars)
    mysql.connection.commit()
    data=cursor.fetchall()
     #Checks to see if the user's query is already in the table
    if len(data)==0: #If it is not in the table, it creates a new entry
        input="INSERT INTO evantran_views (item_name, views) VALUES (%s, %s)"
        inputVars=(name,1)
        cursor.execute(input, inputVars)
        mysql.connection.commit()

    elif len(data) > 0: #If it is in the table, it increases the views by one
        views="SELECT views FROM evantran_views WHERE item_name=%s;"
        viewsVars=(name,)
        cursor.execute(views, viewsVars)
        mysql.connection.commit()
        output=cursor.fetchall()
        count=output[0]["views"]+1
        input="UPDATE evantran_views SET views=%s WHERE item_name=%s"
        inputVars=(count, name)
        cursor.execute(input, inputVars)
        mysql.connection.commit()

# Calculates the min-bid price of an item (basically after someone bids on an item, the next person outbid them by a certain amount)
# forums paged used: https://hypixel.net/threads/how-do-ah-bids-work.4899947/post-35321472
def price(num, math):
    format=float(num)
    if math==True:
        if format < 100000:
            format=round(format*1.15,2)
        elif format < 1000000:
            format=round(format*1.1,2)
        elif format < 10000000:
            format=round(format*1.05,2)
        else:
            format=round(format*1.025,2)
        return format
    else:
        return format

# This is indeed a chunky block of code. Within the Hypixel Skyblock API, 
# there are section (§) symbols, which indicate some sort of change to text-color
# or font style (such as bolds or italics). I used 
# https://hypixel.net/threads/updated-all-skyblock-stat-skill-symbols-icons-%E2%80%94-for-item-ideas.4545219/
# to help me find out what the different sections meant, but was unable to figure 
# out what the last 4 meant (hence why they are replaced by nothing), and are not 
# listed in the forums page. I also checked in game to see what items with those tags looked like,
# and couldn't find any noticable differences. 

def colors(array,j): 
    array[j]["item_lore"]=array[j]["item_lore"].replace("\n", "<br> ") 
    array[j]["item_lore"]=array[j]["item_lore"].replace("§7", "</span></span>")
    array[j]["item_lore"]=array[j]["item_lore"].replace("§f", "</span><span class=common>")
    array[j]["item_lore"]=array[j]["item_lore"].replace("§8", "</span><span class=common>")
    array[j]["item_lore"]=array[j]["item_lore"].replace("§a", "</span><span class=uncommon>")
    array[j]["item_lore"]=array[j]["item_lore"].replace("§9", "</span><span class=rare>")
    array[j]["item_lore"]=array[j]["item_lore"].replace("§5", "</span><span class=epic>")
    array[j]["item_lore"]=array[j]["item_lore"].replace("§6", "</span><span class=legendary>")
    array[j]["item_lore"]=array[j]["item_lore"].replace("§d", "</span><span class=mythic>")
    array[j]["item_lore"]=array[j]["item_lore"].replace("§b", "</span><span class=divine>")
    array[j]["item_lore"]=array[j]["item_lore"].replace("§c", "</span><span class=special>")
    array[j]["item_lore"]=array[j]["item_lore"].replace("§c", "</span><span class=very_special>")
    array[j]["item_lore"]=array[j]["item_lore"].replace("§4", "</span><span class=supreme>")
    array[j]["item_lore"]=array[j]["item_lore"].replace("§e", "</span><span class=yellow>")
    array[j]["item_lore"]=array[j]["item_lore"].replace("§3", "</span><span class=aqua>")
    array[j]["item_lore"]=array[j]["item_lore"].replace("§l", "<span class=bold>")
    array[j]["item_lore"]=array[j]["item_lore"].replace("§o", "<span class=italics>")
    array[j]["item_lore"]=array[j]["item_lore"].replace("§2", "")
    array[j]["item_lore"]=array[j]["item_lore"].replace("§m", "")
    array[j]["item_lore"]=array[j]["item_lore"].replace("§ka", "")
    array[j]["item_lore"]=array[j]["item_lore"].replace("§r", "")
    return array[j]