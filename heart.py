import numpy as np
import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn import svm
from sklearn.metrics import accuracy_score
from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier


heart_data = pd.read_csv('heart (2).csv')

X = heart_data.drop(columns='target',axis=1)
Y = heart_data['target']


Y = Y.astype('int')
X = X.astype('int')

X_train,X_test,Y_train,Y_test = train_test_split(X,Y,test_size=0.2,stratify=Y,random_state=2)


base_estimator = DecisionTreeClassifier(max_depth=1)
classifier = AdaBoostClassifier(base_estimator=base_estimator, n_estimators=50, random_state=42)


classifier.fit(X_train,Y_train)


pickle.dump(classifier,open('model1.pkl','wb'))
heart_model=pickle.load(open('model1.pkl','rb'))