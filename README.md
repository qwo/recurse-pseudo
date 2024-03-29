# Recurse Center Pseudonyms.
Show automatically generated pseudonyms for Recursers' applications grabbed from the RC API. 

## [Check it out](http://pseudonyms.recurse.com/)
RC OAuth authentication necessary. 

Built on vanilla Python and Flask. Hosted on Heroku. 

## Development

```
virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Docker

docker build -t pseudo .

docker run -p 8080:8080 pseudo 


## ENV Vars
You will also need to set the following environment variables:

set them in the template from .env

```
RC_OAUTH_CLIENT_ID=<your app client id>

RC_OAUTH_CLIENT_SECRET=<your app client secret>

SESSION_SECRET=<generated random string>

# update to your production link where necessary
RC_OAUTH_REDIRECT_AUTH_URI=<http://localhost:6060/access_token>

PORT=6060
```