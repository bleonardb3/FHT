import urllib3, requests, json, os
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, FloatField, IntegerField,SelectField,TextField
from wtforms.validators import Required, Length, NumberRange

#url = 'https://us-south.ml.cloud.ibm.com'
#wml_apikey = 'r5XhQCe1iuBXrSzGKy5zTm7M0dMEp8ZISL1NvJHdM2oY'
#ml_instance_id = '083ff2e8-0201-41c7-8796-e3c6bdd77010'

if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.getenv('VCAP_SERVICES'))
    print('Found VCAP_SERVICES')
    if 'pm-20' in vcap:
        print('Found pm-20')
        creds = vcap['pm-20'][0]['credentials']
        wml_apikey = creds['apikey']
        print('wml_apikey')
        print(wml_apikey)
        ml_instance_id = creds['instance_id']
        url = creds['url']
scoring_endpoint = 'https://us-south.ml.cloud.ibm.com/v4/deployments/4cbc62f6-b882-4d29-87a0-ee1291c9f89e/predictions'
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretpassw0rd'
bootstrap = Bootstrap(app)

class FHTForm(FlaskForm):
  categories = SelectField('Categories', choices=[('Sports/Travel','Sports/Travel'),('Engineering','Engineering'),('Information Technology','Information Technology'),
  ('Journalism','Journalism'),('Government','Government'),('Medical','Medical'), ('Science','Science'),('Arts','Arts'),('Advertising','Advertising'),('Legal','Legal'),
  ('Construction','Construction'),('Retail','Retail'),('Education','Education'),('Finance','Finance'),('Other','Other')])
  age = IntegerField('Age:')
  countries_visited_count = IntegerField('Number of countries visited:')
  passport_country = RadioField('Passport Country', choices=[('Ghana', 'Ghana'), ('Brazil', 'Brazil'), ('Pakistan', 'Pakistan'),('Bangladesh','Bangladesh'),('Haiti','Haiti'),('India','India')])
  arrival_state = StringField('Arrival State:')
  departure_country = StringField('Departure Country:')  
  submit = SubmitField('Submit')
@app.route('/', methods=['GET', 'POST'])
def index():
  form = FHTForm()
  if form.is_submitted(): 
    arrival_state = form.arrival_state.data
    form.arrival_state.data=''
    departure_country = form.departure_country.data
    form.departure_country.data =''
    category = form.categories.data
    print (category)
    form.categories.data = ''
    age = form.age.data
    print (age)
    form.age.data = ''
    countries_visited_count = form.countries_visited_count.data
    form.countries_visited_count.data = ''
    passport_country = form.passport_country.data
    form.passport_country.data=''
    # get iam_token
    iam_url = "https://iam.bluemix.net/oidc/token"
    headers = { "Content-Type" : "application/x-www-form-urlencoded" }
    data    = "apikey=" + wml_apikey + "&grant_type=urn:ibm:params:oauth:grant-type:apikey"
    IBM_cloud_IAM_uid = "bx"
    IBM_cloud_IAM_pwd = "bx"
    print('submitting token request')
    response  = requests.post( iam_url, headers=headers, data=data, auth=( IBM_cloud_IAM_uid, IBM_cloud_IAM_pwd ) )
    iam_token = response.json()["access_token"]
    print(iam_token)
    
    auth = 'Bearer ' + iam_token
    scoring_header = {'Content-Type': 'application/json', 'Authorization': auth, 'ML-Instance-ID': ml_instance_id}
    payload = {"input_data": [{"fields": ["PASSPORT_COUNTRY","COUNTRIES_VISITED_COUNT","ARRIVAL_STATE","DEPARTURE_AIRPORT_COUNTRY_CODE","AGE","Category",], "values": [[passport_country,countries_visited_count,arrival_state,departure_country,age,category]]}]}
    print(payload)
    print('submitting scoring request')
    scoring = requests.post(scoring_endpoint, json=payload, headers=scoring_header)

    scoringDICT = json.loads(scoring.text) 
    print ("scoringDICT: ",scoringDICT)
    scoringList = scoringDICT['predictions'][0]['values']
    print ("scoringList: ",scoringList)
    score  =  int(scoringList[0][0])
    probability = max(scoringList[0][1])
   # score = scoringList[1:].pop()
   # probability_died = scoringList[0:1].pop()[0:1].pop()
   # print (probability_died)
   # probability_survived = scoringList[0:1].pop()[1:].pop()
    if (score == 10) :
      score_str = "high risk"
    elif (score == 20) :
      score_str = "medium risk"	   
    else:
      score_str = "low risk"
    return render_template('score.html', form=form, scoring=score_str,probability=probability)
  return render_template('index.html', form=form)
port = os.getenv('PORT', '5000')
if __name__ == "__main__":
  app.run(host='0.0.0.0', port=int(port))
