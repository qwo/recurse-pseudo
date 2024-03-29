from flask import Flask, request, redirect, url_for, jsonify, session, render_template
import requests
import urllib.parse
import os
import json 

from google.cloud import firestore
db = firestore.Client(project="we-heart-rc")
doc_ref = db.collection(u'cache').document('cache')


### Load Env
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)

app.debug = True
app.secret_key = os.environ.get('SECRET_SESSION') or "foobar"
port = int(os.environ.get('PORT'))

app.config['RC_API_URI'] = 'http://www.recurse.com/api/v1'
app.config['RC_OAUTH_AUTH_URI'] = 'https://www.recurse.com/oauth/authorize'
app.config['RC_OAUTH_TOKEN_URI'] = 'https://www.recurse.com/oauth/token'
app.config['RC_OAUTH_REDIRECT_AUTH_URI'] = os.environ.get('RC_OAUTH_REDIRECT_AUTH_URI')

app.config['RC_OAUTH_CLIENT_ID'] = os.environ.get('RC_OAUTH_CLIENT_ID')
app.config['RC_OAUTH_CLIENT_SECRET'] = os.environ.get('RC_OAUTH_CLIENT_SECRET')
app.config['SESSION_SECRET'] = os.environ.get('SESSION_SECRET')

sessions = {}

@app.route('/', methods=['GET'])
def index():
    # if user already exists
    if 'user' in session and session['user'] in sessions:
        return redirect(url_for('pseudonyms'))
    else:
        params = {
            "client_id": app.config['RC_OAUTH_CLIENT_ID'],
            "redirect_uri": app.config['RC_OAUTH_REDIRECT_AUTH_URI'],
            "response_type": 'code'
        }

        url_params = urllib.parse.urlencode(params)
        oauth_url = "%s?%s" % (app.config['RC_OAUTH_AUTH_URI'], url_params)
        return redirect(oauth_url)


@app.route('/access_token', methods=['GET', 'POST'])
def access_token():
    code = request.args.get('code')
    params = {
        'client_id': app.config['RC_OAUTH_CLIENT_ID'],
        'client_secret': app.config['RC_OAUTH_CLIENT_SECRET'],
        'redirect_uri': app.config['RC_OAUTH_REDIRECT_AUTH_URI'],
        'grant_type': 'authorization_code',
        'code': code
    }

    req = requests.post(app.config['RC_OAUTH_TOKEN_URI'], data=params)
    data = json.loads(req.text)
    if 'access_token' in data: 

        token = data['access_token']
        user = get_user(token)

        # save user session
        user_email = user['email']

        session['user'] = user_email
        sessions[user_email] = token 

        return redirect(url_for('pseudonyms'))
    else:
        return req.text


@app.route('/pseudonyms', methods=['GET'])
def pseudonyms():
    if 'user' not in session or session['user'] not in sessions:
        return redirect(url_for('index'))

    user = session['user']
    token = sessions[user]
    if user in sessions:
        # get user
        u = get_user(token)
        if request.args.get('update') is None:
            batch_people = get_cached_batches()
        else:
            batches = get_batches(token)
            # get people from all batches
            batch_people = [(batch["name"],get_batch(token, batch["id"])) for batch in batches]
            background_job(batch_people)

        return render_template('pseudonym.html', batches=batch_people, user=u)
    else:
        return redirect(url_for('index'))

def make_header(access_token):
    headers = {
        'Authorization': 'Bearer %s' % access_token,
        'Accepts' : 'application/json'
    }
    return headers 

def get_batch(access_token, batch_id):
    headers = make_header(access_token)
    req = requests.get("%s/batches/%d/people" % (app.config['RC_API_URI'], batch_id), headers=headers)
    return req.json()


def get_cached_batches():
    """Datastore trimmed down result """
    doc_ref = db.collection(u'cache').document('cache')
    result = doc_ref.get(['cache']).to_dict()['cache']
    return json.loads(result)

def background_job(batches):
    """ Mimics the same bactch formatting """
    result = []
    for key, batch in batches:
        batchlings = []
        for r in batch:
            attribs = ["first_name", "last_name", "pseudonym", "image"]
            slim = {i: r.get(i) for i  in attribs}
            batchlings.append(slim)
        s = list([key,batchlings])
        result.append(s)
    
    doc_ref.set({"cache": json.dumps(result)})

def get_batches(access_token):
    headers = make_header(access_token)
    req = requests.get("%s/batches" % app.config['RC_API_URI'], headers=headers)
    return json.loads(req.text)
    

def get_user(access_token):
    headers = make_header(access_token)
    req = requests.get("%s/people/me" % app.config['RC_API_URI'], headers=headers)
    return json.loads(req.text)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
