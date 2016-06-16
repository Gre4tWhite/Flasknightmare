from flask import render_template, request, redirect, url_for, Response, session
from app import app
import subprocess
import urllib
import urllib2
import json
from pprint import pprint

MUTALISK_DATA = 'http://mutalisk.battle.net/api/data?'
MUTALISK_EC = 'http://mutalisk.battle.net/api/eventConfirm?'


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return redirect(url_for('auth', name=name, password=password), code=307)
    else:
        return render_template('index.html')

@app.route("/auth/", methods=['POST'])
def auth():

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

    session['cookie'] = cookie

    return render_template('realms.html')

@app.route("/realms/", methods=['POST'])
def realms():
    def print_filters(x):
        with open('app/static/filters.json') as data:
            json_data = json.load(data)
            for region in json_data:
                if region == x:
                    output_from_func = region + ' batches to be restarted:' + '<br>'
                    for i in range(1, len(json_data[x]['Restart']) + 1):
                        for filter in json_data[x]['Restart']['Batch ' + str(i)]:
                            y = "Batch " + str(i) + ": " + filter + '<br>'
                            output_from_func += y
                    return output_from_func

    if request.form.get('option') == 'US':
        output = print_filters('US')
    elif request.form.get('option') == 'EU':
        output = print_filters('EU')
    elif request.form.get('option') == 'KR/TW':
        output = print_filters('KR/TW')
    elif request.form.get('option') == 'KR':
        output = print_filters('KR')
    elif request.form.get('option') == 'TW':
        output = print_filters('TW')
    else:
        output = 'Idk man, try again'

    return render_template('realms.html', output=output)

'''    query = {'filter': filters,'type': 'Entities', 'event':'Restart', 'to':'Service', 'location':'false'}
    mutalisk_url = MUTALISK_EC + urllib.urlencode(query)
    result = json.load(urllib2.urlopen(urllib2.Request(url=mutalisk_url, headers=session['cookie'])))
    string = ''
    if result['errors'] and "Access Denied" in result['errors'][0]:
        string = str(result['errors'][0])
    else:
        string = str(result['result']['events'][0]['entity'])

    return string
'''