import numpy as np
import pandas as pd
import pickle
import warnings
from sklearn.model_selection import train_test_split
from sklearn import svm
from sklearn.metrics import accuracy_score
from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
warnings.filterwarnings("ignore")

diabetes_dataset = pd.read_csv('diabetes (1).csv')


X = diabetes_dataset.drop(columns = 'Outcome', axis=1)
Y = diabetes_dataset['Outcome']

Y = Y.astype('int')
X = X.astype('int')

X_train, X_test, Y_train, Y_test = train_test_split(X,Y, test_size = 0.2, stratify=Y, random_state=2)


base_estimator = DecisionTreeClassifier(max_depth=1)
classifier = AdaBoostClassifier(base_estimator=base_estimator, n_estimators=50, random_state=42)


classifier.fit(X_train, Y_train)







pickle.dump(classifier,open('model.pkl','wb'))
model=pickle.load(open('model.pkl','rb'))