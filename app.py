from flask import Flask, request, url_for, redirect, render_template,session
import pickle
import numpy as np
import pyrebase

app = Flask(__name__)
app.secret_key = "hai"



config = {
  "apiKey": "AIzaSyDZ4GU0X0KznmK3gCx8mVQqwZFjHKi46jE",
  "authDomain": "first-flask-app-7b882.firebaseapp.com",
  "projectId": "first-flask-app-7b882",
  "storageBucket": "first-flask-app-7b882.appspot.com",
  "messagingSenderId": "297760772258",
 "appId": "1:297760772258:web:8b4e08199b6571226f07fb",
  "measurementId": "G-NC80NQW7C2",
  "databaseURL": "https://first-flask-app-7b882-default-rtdb.firebaseio.com/"
}

firebase=pyrebase.initialize_app(config)
auth=firebase.auth()

db = firebase.database()

model = pickle.load(open('model.pkl', 'rb'))
heart_model = pickle.load(open('model1.pkl', 'rb'))

@app.route("/")
def home():
    return render_template("index.html")


@app.route('/signup', methods=['GET', 'POST'])
def signup():

    session.pop('user', None)
    error = None

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']  # Capture username from the form
        
        try:
            # Create user with email and password
            user = auth.create_user_with_email_and_password(email, password)
            session['user'] = user['localId']
            # user_data = {
            #     'username': username,
            #     'email': email,
            #     'password': password
                
            # }
            # db.child('users').child(session['user']).set(user_data)
            # Update profile with display name
            auth.update_profile(user['idToken'], {'displayName': username})
            return redirect(url_for('dashboard'))
        except Exception as e:
            error = "An error occurred while creating your account."
            return redirect(url_for('dashboard',error=error))
    return render_template('login-signup.html')


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    # Clear session when user visits sign-in page
    session.pop('user', None)
    error = None

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session['user'] = user['localId']
            
            # Retrieve user data
            user_info = auth.get_account_info(user['idToken'])
            # Extract username
            username = user_info['users'][0].get('displayName', "Guest")


            # Store the username in the session
            session['username'] = username

            # Redirect to the dashboard
            return redirect(url_for('dashboard'))
        except Exception as e:
            error = "Authentication failed. Please check your email and password."
            return render_template('error.html', error=error)
    return render_template('login-signup.html')



@app.route("/dashboard")
def dashboard():
    if 'user' in session:
        user_id = session['user']
        username = session.get('username','Guest')
        print("Username from session:", username)
        
        return render_template('dashboard.html', username=username)
    else:
        # If user is not in session, redirect to sign-in page
        return redirect(url_for('signin'))
    
@app.route('/logout')
def logout():
    # Clear the user's session
    session.pop('user', None)
    # Redirect to the signin page
    return redirect(url_for('signin'))
    
    
    

@app.route('/diabetes')
def diabetes():
    return render_template("diabetes.html")

@app.route('/heart')
def heart_disease():
    return render_template("heart.html")



@app.route('/predict', methods=['POST', 'GET'])
def predict():
    feature_names = ['pregnancies', 'glucose', 'blood-pressure', 'skin-thickness', 'insulin', 'bmi', 'diabetes-pedigree', 'age']
    features = {name: request.form.get(name) for name in feature_names}

    final = [np.array([float(value) if value is not None else 0.0 for value in features.values()])]

    prediction = model.predict(final)
    print(prediction)

    if prediction[0] == 0:
        result = "Probability of being diabetic is very less."
    else:
        result = "You are at high risk of being diabetic."

    user_id = session['user'] if 'user' in session else 'Guest'
    username = session.get('username', 'Guest')

    # Retrieve old values from the database
   

    # Store new values in the database
    data = {
        'user_id': user_id,
        'username': username,
        'features': features,
        'prediction': result
    }
    db.child('diabetes_predictions').push(data)

    
    old_values = db.child('diabetes_predictions').order_by_child('user_id').equal_to(user_id).get()
    print(old_values)
    
    # Compare old and new values and provide feedback
    feedback, conclusion = compare_values(old_values, data)

    return render_template('diabetes.html', pred=result, feedback=feedback, conclusion=conclusion)



def compare_values(old_values, new_value):
    old_features = []
    old_predictions = []

    # Extract old features and predictions from the retrieved data
    for entry in old_values.each():
        old_features.append(entry.val()['features'])
        old_predictions.append(entry.val()['prediction'])

    # Extract new features and prediction
    new_features = new_value['features']
    new_prediction = new_value['prediction']

    # Compare specific features (e.g., glucose levels, age) and provide feedback
    feedback = ""

    # Example: Compare glucose levels
    old_glucose = [float(entry['glucose']) for entry in old_features]
    new_glucose = float(new_features['glucose'])

    # Compare with the latest value
    if new_glucose >= old_glucose[-1]:
        feedback += "Your glucose levels have increased. "
    else:
        feedback += "Your glucose levels are stable. "

    # Example: Compare age
    old_age = [float(entry['age']) for entry in old_features]
    new_age = float(new_features['age'])

    # Compare with the latest value
    if new_age >= old_age[-1]:
        feedback += "Your age has increased. "
    else:
        feedback += "Your age is stable. "

    # Add more comparisons based on your specific features

    # Scoring system (adjust weights and thresholds as needed)
    glucose_score = 1 if new_glucose >= old_glucose[-1] else -1
    age_score = 1 if new_age >= old_age[-1] else -1

    total_score = glucose_score + age_score  # Add more scores as needed

    # Determine conclusion based on the total score
    if total_score >= 2:
        conclusion = "Your health is stable."
    elif -1 <= total_score <= 1:
        conclusion = "Your health is in a moderate state."
    else:
        conclusion = "Your health is in a critical condition."

    return feedback, conclusion




@app.route('/calculate', methods=["POST", "GET"])
def calculate():
    feature_names = ['age','sex','cp','trestbps','chol','fbs','restecg','thalach','exang','oldpeak','slope','ca','thal']
    features = {name: request.form.get(name) for name in feature_names}
    if(features['sex']=='Male'):
        features['sex'] = '1'                           #SEX
    elif(features['sex'] == 'Female'):
        features['sex'] = '0'
        
    if(features['cp']=="Typical Angina"):
        features['cp'] = '0'
    elif(features['cp'] == "Atypical Angina"):
        features['cp'] = '1'                              #CP
    elif(features['cp'] == "Non-Anginal Pain"):
        features['cp'] = '2'
    elif(features['cp'] == "Asymptomatic"):
        features['cp'] = '3'
        
       
    if(features['restecg']=="Normal"):                      #RESTECG
        features['restecg'] = '0'
    elif(features['restecg']=="ST-T abnormality"):
        features['restecg'] = '1'
    # elif(features['restecg']=="Probable or definite left ventricular hypertrophy "):
    #     features['restecg'] = '2'
    
    
    if(features['exang']=="No"):                      #EXANG
        features['exang'] = '0'
    elif(features['exang']=="Yes"):
        features['exang'] = '1'
        
    if(features['slope']=="Up Sloping"):                      #SLOPE
        features['slope'] = '0'
    elif(features['slope']=="Flat"):
        features['slope'] = '1'
    elif(features['slope']=="Down Sloping"):
        features['slope'] = '2'
        
    if(features['thal']=="No Disorder"):                      #THAL
        features['thal'] = '0'
    elif(features['thal']=="Normal Blood Flow"):
        features['thal'] = '1'
    elif(features['thal']=="Fixed Defect"):
        features['thal'] = '2'
    elif(features['thal']=="Reversible Defect"):
        features['thal'] = '3'

        
    final = [np.array([float(features[name]) for name in feature_names])]

    prediction = heart_model.predict(final)
    print(prediction)

    if prediction[0] == 0:
        result = "Probability of having heart disease is very less."
    else:
        result = " You are at high risk of havig heart disease."

    user_id = session['user'] if 'user' in session else 'Guest'
    username = session.get('username', 'Guest')

    data = {
        'user_id': user_id,
        'username': username,
        'features': features,
        'prediction': result
    }
    db.child('heart_disease_predictions').push(data)

    return render_template("heart.html", predict=result)


@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/profile")
def profile():
    return render_template("profile.html")

if __name__ == '__main__':
    app.run(debug=True)