from flask import render_template, request, redirect, url_for, Response
from app import app
import subprocess
import urllib
import urllib2
import json

MUTALISK_DATA = 'http://mutalisk.battle.net/api/data?'
MUTALISK_EC = 'http://mutalisk.battle.net/api/eventConfirm?'

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return redirect(url_for('test', name=name, password=password), code=307)
    else:
        return render_template('index.html')


@app.route("/test/", methods=['POST'])
def test():

    name = request.form['login']
    password = request.form['password']
    cookie = ""
    realm = 'Battle.net'
    logon_url = 'http://admin.battle.net/logon'
    authhandler = urllib2.HTTPDigestAuthHandler()
    authhandler.add_password(realm, logon_url, name, password)
    opener=urllib2.build_opener(authhandler)
    urllib2.install_opener(opener)

    try:
        socket = opener.open(logon_url, timeout=5)
    except urllib2.HTTPError:
        try:
            s = urllib2.urlopen(logon_url, timeout=5)
        except urllib2.HTTPError:
            return "apache.HTTP_UNAUTHORIZED"
        else:
            cookie = {'Cookie':s.headers['Set-Cookie']}
        finally:
            try:
                s.close()
            except:
                pass
    except urllib2.URLError, err:
        return "apache.HTTP_REQUEST_TIME_OUT"
    else:
        cookie = {'Cookie':socket.headers['Set-Cookie']}
    finally:
        try:
            socket.close()
        except:
            pass

    query = {'filter':'^US1-WOW-60-GAME01$','type': 'Entities', 'event':'Restart', 'to':'Service', 'location':'false'}
    mutalisk_url = MUTALISK_EC + urllib.urlencode(query)
    result = json.load(urllib2.urlopen(urllib2.Request(url=mutalisk_url, headers=cookie)))
    #print result
    string = ""
    if result['errors'] and "Access Denied" in result['errors'][0]:
        string = str(result['errors'][0])
    else:
        string = name + " successfully rebooted US1-WOW-60-GAME01"
    return string
