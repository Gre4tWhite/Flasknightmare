from flask import render_template, request, redirect, url_for, Response, session, stream_with_context
from app import app
from itertools import chain
import subprocess
import urllib
import urllib2
import json
import time
from pprint import pprint

MUTALISK_DATA = 'http://mutalisk.battle.net/api/data?'
MUTALISK_EC = 'http://mutalisk.battle.net/api/eventConfirm?'
GUARDIAN_VIEW = 'http://guardian.battle.net/view?'
GUARDIAN_FILTERS = json.load(open("filters.json"))


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
    def restart_wrapper(region):

        yield "---Performing WoW Rolling Restarts for " + region + "---" + '<br><br>'
        yield 'Starting in: '
        for i in reversed(range(1,6)):
            yield str(i) + "    "
            time.sleep(1)
            yield "      "
        yield '<br><br>'
        for i in range(1, len(GUARDIAN_FILTERS[region]['Restart']) + 1):
            for filter in GUARDIAN_FILTERS[region]['Restart']["Batch " + str(i)]:
                yield restart(i, filter)
            if i < (len(GUARDIAN_FILTERS[region]['Restart'])):
                if region == 'CN':
                    yield "Waiting 10 minutes <br><br>"
                else:
                    yield "Waiting 5 minutes <br><br>"
                time.sleep(5)
            if region == 'CN':
                yield "5 minutes remaining <br><br>"
                time.sleep(5)


    def restart(batch_num ,filter):
            query = {'filter': filter,'type': 'Entities', 'event':'Restart', 'to':'Service', 'location':'false'}
            mutalisk_url = MUTALISK_EC + urllib.urlencode(query)
            result = json.load(urllib2.urlopen(urllib2.Request(url=mutalisk_url, headers=session['cookie'])))
            return  "---Performing WoW Rolling Restarts for batch " + str(batch_num) + ": " +  filter + "---" + '<br>' + '<br>'


    def gen_links(region):

        yield '---BE SURE TO CHECK SERVER STATUS--- <br> <br>'

        for i in range(1, len(GUARDIAN_FILTERS[region]['Restart']) + 1):
            for filter in GUARDIAN_FILTERS[region]['Restart']['Batch ' + str(i)]:
                query = {'filter':filter,'type':'Entities'}
                guardian_url = GUARDIAN_VIEW + urllib.urlencode(query)
                yield '<a href="' + guardian_url + '">Batch ' + str(i) +': ' + filter + '</a>' + '<br>' + '<br>'
#<a href="/index">Home</a>

    if request.form.get('option') == 'US':
        def stream():
            return chain(restart_wrapper('US'), gen_links('US'))
#        output = restart_wrapper('US') + '<br>'
#        links = gen_links('US') + '<br>'
#        output += gen_links('US')
    elif request.form.get('option') == 'EU':
        def stream():
            return chain(restart_wrapper('EU'), gen_links('EU'))
#        output = restart_wrapper('EU')
#        output += gen_links('EU') + '<br>'
#        output = print_filters('EU')
    elif request.form.get('option') == 'KR/TW':
        def stream():
            return chain(restart_wrapper('KR/TW'), gen_links('KR/TW'))
#        output = restart_wrapper('KR/TW')
#        output += gen_links('KR/TW') + '<br>'
#        output = print_filters('KR/TW')
    elif request.form.get('option') == 'KR':
        def stream():
            return chain(restart_wrapper('KR'), gen_links('KR'))
#        output = restart_wrapper('KR')
#        output += gen_links('KR') + '<br>'
#        output = print_filters('KR')
    elif request.form.get('option') == 'TW':
        def stream():
            return chain(restart_wrapper('TW'), gen_links('TW'))
#        output = restart_wrapper('TW')
#        output += gen_links('TW') + '<br>'
#        output = print_filters('TW')
    else:
        def stream():
            return chain(restart_wrapper('CN'), gen_links('CN'))
#        output = restart_wrapper('CN')
#        output += gen_links('CN') + '<br>'
#        output = print_filters('CN')

    return Response(stream_with_context(stream()))

'''
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
'''
