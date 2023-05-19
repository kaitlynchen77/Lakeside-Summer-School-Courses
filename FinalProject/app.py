##IMPORTS/SETUP

from flask import Flask, render_template
from flask import Flask, render_template, request
import requests
from flask_mysqldb import MySQL
import numpy as np
app=Flask(__name__)  

##ROUTES

@app.route('/')
def index():
    return render_template('index.html.j2')


##FUNCTIONS