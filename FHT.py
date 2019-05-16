import urllib3, requests, json, os
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, FloatField, IntegerField,SelectField
from wtforms.validators import Required, Length, NumberRange

#url = 'https://us-south.ml.cloud.ibm.com'
#username = 'c49a6e9c-185e-446f-98df-9c4f9fb9aebd'
#password = '766378de-306e-48eb-a191-d88b7115116a'

if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.getenv('VCAP_SERVICES'))
    print('Found VCAP_SERVICES')
    if 'pm-20' in vcap:
        creds = vcap['pm-20'][0]['credentials']
        username = creds['username']
        password = creds['password']
        url = creds['url']
scoring_endpoint = 'https://us-south.ml.cloud.ibm.com/v3/wml_instances/02eafab5-7bd2-4ac4-abb1-334f0cc6232c/deployments/cbea645b-68ed-435b-b0e3-dc2f87df4eaf/online'
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
  submit = SubmitField('Submit')
@app.route('/', methods=['GET', 'POST'])
def index():
  form = FHTForm()
  if form.is_submitted(): 
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
    payload = {"fields": ["COUNTRIES_VISITED_COUNT", "AGE","PASSPORT_COUNTRY", "Category"], "values": [[countries_visited_count,age,passport_country,category]]}
    scoring = requests.post(scoring_endpoint, json=payload, headers=scoring_header)

    scoringDICT = json.loads(scoring.text) 
    print ("scoringDICT: ",scoringDICT)
    scoringList = scoringDICT['values'].pop()[6:9]
    print (scoringList)
    score  = int(scoringList[2])
    probability = scoringList[0][int(scoringList[1])]
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
