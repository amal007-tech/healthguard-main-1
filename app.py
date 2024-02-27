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
    return render_template("heart.html")


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
    feature_names = ['pregnancies', 'glucose', 'blood-pressure', 'skin-thickness', 'insulin','bmi','diabetes-pedigree','age']
    features = {name: request.form.get(name) for name in feature_names}
    
    
    final = [np.array([float(value) if value is not None else 0.0 for value in features.values()])]

    prediction = model.predict(final)
    print(prediction)

    if prediction[0] == 0:
        result = "The person is not diabetic"
    else:
        result = "The person is diabetic"

    
    data = {
        'features': features,
        'prediction': result
    }
    db.child('diabetes_predictions').push(data)

    return render_template('diabetes-form.html', pred=result)

@app.route('/calculate', methods=["POST", "GET"])
def calculate():
    feature_names = ['age','sex','cp','trestbps','chol','fbs','restecg','thalach','exang','oldpeak','slope','ca','thal']
    features = {name: request.form.get(name) for name in feature_names}
    if(features['sex']=='Male'):
        features['sex'] = '1'
    elif(features['sex'] == 'Female'):
        features['sex'] = '0'
        
        
    final = [np.array([float(features[name]) for name in feature_names])]

    prediction = heart_model.predict(final)
    print(prediction)

    if prediction[0] == 0:
        result = "You have no heart disease"
    else:
        result = " You have heart disease"

    data = {
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
