import urllib3, requests, json, os
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, FloatField, IntegerField,SelectField,TextField
from wtforms.validators import Required, Length, NumberRange

url = 'https://us-south.ml.cloud.ibm.com'
username = '261cda05-8b26-4bec-ad4f-d4bb811c8dad'
password = '00f7cbc9-08ea-4fa6-bcbb-b7762daa7785'

#if 'VCAP_SERVICES' in os.environ:
#    vcap = json.loads(os.getenv('VCAP_SERVICES'))
#    print('Found VCAP_SERVICES')
#    if 'pm-20' in vcap:
#        creds = vcap['pm-20'][0]['credentials']
#        username = creds['username']
#        password = creds['password']
#        url = creds['url']
scoring_endpoint = 'https://us-south.ml.cloud.ibm.com/v4/deployments/48ea36dd-0780-49c1-a0c8-f73f20546784/predictions'
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
    
    
    headers = urllib3.util.make_headers(basic_auth='{}:{}'.format(username, password))
    path = '{}/v3/identity/token'.format(url)
    response = requests.get(path, headers=headers)
    mltoken = json.loads(response.text).get('token')
    scoring_header = {'Content-Type': 'application/json', 'Authorization': 'Bearer' + mltoken}
    payload = {"input_data": [{"fields": ["PASSPORT_COUNTRY","COUNTRIES_VISITED_COUNT","ARRIVAL_STATE","DEPARTURE_AIRPORT_COUNTRY_CODE","AGE","Category",], "values": [[passport_country,countries_visited_count,arrival_state,departure_country,age,category]]}]}
    print("payload:",payload)
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
