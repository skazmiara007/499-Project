# -*- coding: utf-8 -*-
"""Ensemble (AdaBoost, XGBoost) techniques. Explainable AI with Lime and Shapash frameworks are applied to interpret the results

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1yUZelAImMwmLw5IGszD_MWTMf4re9pMF
"""

from google.colab import drive
drive.mount('/content/drive')

!pip install pandas

#necessary libraries
import pandas as pd
import numpy as np

#reading the dataset into a dataframe and showing first 5 rows
dataframe = pd.read_csv("/content/drive/MyDrive/data/corona_tested_individuals_ver_0083.english.csv", low_memory=False)
# dataframe = pd.read_csv("corona_tested_individuals_ver_0083_english.csv", low_memory=False)
dataframe.head(5)

#shape of the dataset
dataframe.shape

#null values in the dataset
dataframe.isnull().sum()

#drop the null values
dataframe.dropna(inplace=True)

#null values in the dataset after dropping null values
dataframe.isnull().sum()

#shape of the dataset after dropping null values
dataframe.shape

#dropping the date and age column
dataframe.drop('test_date', inplace=True, axis=1)
dataframe.drop('age_60_and_above', inplace=True, axis=1)
dataframe.head(5)

#number of unique values in each column
dataframe.nunique()

#unique values in each column
for col in dataframe:
    print(col, ': ', dataframe[col].unique())

#dropping the rows with other corona results
dataframe = dataframe[dataframe.corona_result != 'other']
dataframe['corona_result'].value_counts()

#checking the final shape of the dataset
dataframe.shape

#corona_result in term of cough feature
import seaborn as sns
import matplotlib.pyplot as plt

sns.set_theme(style="darkgrid")
sns.set(rc={'figure.figsize':(16,8)})
fig, ax = plt.subplots(2,4)
sns.countplot(x="cough", hue="corona_result", data=dataframe, ax=ax[0,0])
sns.countplot(x="fever", hue="corona_result", data=dataframe, ax=ax[0,1])
sns.countplot(x="sore_throat", hue="corona_result", data=dataframe, ax=ax[0,2])
sns.countplot(x="shortness_of_breath", hue="corona_result", data=dataframe, ax=ax[0,3])
sns.countplot(x="head_ache", hue="corona_result", data=dataframe, ax=ax[1,0])
#sns.countplot(x="age_60_and_above", hue="corona_result", data=dataframe, ax=ax[1,1])
sns.countplot(x="gender", hue="corona_result", data=dataframe, ax=ax[1,1])
sns.countplot(x="test_indication", hue="corona_result", data=dataframe, ax=ax[1,2])
plt.tight_layout()

#convreting the cetegorical values into numerical values
pd.options.mode.chained_assignment = None
dataframe['corona_result'].replace(['negative', 'positive'], [0, 1], inplace=True)
#dataframe['age_60_and_above'].replace(['No', 'Yes'], [0, 1], inplace=True)
dataframe['gender'].replace(['male', 'female'], [1, 0], inplace=True)
dataframe['test_indication'].replace(['Other', 'Contact with confirmed', 'Abroad'], [0, 1, 2], inplace=True)

dataframe.head()

#ploting a heatmap showing the coorelation
plt.figure(figsize=(18, 16))
cmap = sns.diverging_palette(230, 20, as_cmap=True)
sns.heatmap(dataframe.corr(), cmap=cmap, annot=True)

"""# Model Training

### Spliting data into test and train set
"""

#features
X = dataframe.drop('corona_result',axis=1)

#target variable
y = dataframe['corona_result']

#count of positive and negative case in the dataset
from collections import Counter

print('Dataset shape %s' % Counter(y))

#plot it for a better visualization
class_distribution = pd.Series(y).value_counts(normalize=True)
my_colors = ['b', 'r', 'g', 'y', 'k']
ax = class_distribution.plot.bar(color=my_colors)

#undersampling data to balance it
from imblearn.under_sampling import RandomUnderSampler

rus = RandomUnderSampler(sampling_strategy=0.8, random_state=42)
X_res, y_res = rus.fit_resample(X, y)
print('Resampled dataset shape %s' % Counter(y_res))

#plot it for a better visualization
class_distribution = pd.Series(y_res).value_counts(normalize=True)
my_colors = ['b', 'r', 'g', 'y', 'k']
ax = class_distribution.plot.bar(color=my_colors)

#splitting the data into 75% train data and 25% test data
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.25,random_state=101)

#number of training data
X_train.shape

#number of test data
X_test.shape

"""###Lime (Black Box)"""

from sklearn.ensemble import AdaBoostClassifier
classifier=AdaBoostClassifier()
classifier.fit(X_train,y_train)

#from sklearn.ensemble import RandomForestClassifier
#classifier=RandomForestClassifier()
#classifier.fit(X_train,y_train)

import pickle
pickle.dump(classifier, open("classifier.pkl", 'wb'))

!pip install lime

import lime
from lime import lime_tabular

interpretor = lime_tabular.LimeTabularExplainer(
    training_data=np.array(X_train),
    feature_names=X_train.columns,
    mode='classification'
)

X_test.iloc[14]

exp = interpretor.explain_instance(
    data_row=X_test.iloc[14], ##new data
    predict_fn=classifier.predict_proba
)

exp.show_in_notebook(show_table=True)

"""###Shapash"""

from sklearn.ensemble import RandomForestRegressor
regressor = RandomForestRegressor(n_estimators=200).fit(X_train,y_train)

!pip install shapash

pip install Werkzeug==2.0.0

from shapash.explainer.smart_explainer import SmartExplainer

xpl = SmartExplainer()

xpl.compile(
    x=X_test,
    model=regressor,
   
)

xpl

app = xpl.run_app(title_story='Dataset')

predictor = xpl.to_smartpredictor()

predictor.save('./corona_tested_individuals_ver_0083_english.csv')

from shapash.utils.load_smartpredictor import load_smartpredictor
predictor_load = load_smartpredictor('./corona_tested_individuals_ver_0083_english.csv')

"""Make a prediction with **SmartPredictor**"""

predictor_load.add_input(x=X, ypred=y)

detailed_contributions = predictor_load.detail_contributions()

detailed_contributions.head()

"""Summarize explanability of the **predictions**"""

predictor_load.modify_mask(max_contrib=3)

explanation = predictor_load.summarize()

explanation.head()

# Applying SMOTE

from imblearn.over_sampling import SMOTE 
sm = SMOTE(random_state=0) 
X_smote, y_smote = sm.fit_resample(X_train, y_train) 
 
np.bincount(y_smote)

"""###Ensemble

**Ada Boost**
"""

from sklearn import metrics
from sklearn.ensemble import AdaBoostClassifier
from sklearn.metrics import classification_report
adaBoostModel = AdaBoostClassifier(n_estimators=250, learning_rate=1)
ada = adaBoostModel.fit(X_smote, y_smote)

y_predict = ada.predict(X_test)

print("Accuracy: ", metrics.accuracy_score(y_test, y_predict))
print(classification_report(y_test, y_predict))

#showing the actual corona result and predicted corona result side by side
result = pd.DataFrame({'Actual': y_test, 'Predicted': y_predict})
result

#Evaluating ADABOOST model

#necessary library
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.metrics import confusion_matrix

#Classification Report
from sklearn.metrics import classification_report

print(classification_report(y_test, y_predict, target_names=['Negative', 'Positive']))

#confusion matrix

cm = confusion_matrix(y_test, y_predict)

plt.figure(figsize=(6,4))
sns.heatmap(cm, annot=True, square=True,  fmt='d',
           cmap=plt.cm.Blues, cbar=False)
plt.ylabel('True Labels', fontsize=12)
plt.xlabel('Predicted Labels', fontsize=12)
plt.show()

#mean squared error
mean_squared_error(y_test, y_predict)

#mean absolute error
mean_absolute_error(y_test, y_predict)

#r2 Score
r2_score(y_test, y_predict)

"""**XgBoost**"""

!pip install xgboost

import xgboost
# from xgboost.training import train

xgboosttrain = xgboost.DMatrix(X_smote, label=y_smote)
xgboosttest = xgboost.DMatrix(X_test, label=y_test)

param = {'max depth': 4, 'eta': 0.25, 'objective': 'multi:softmax', 'num_class': 10}
epochs = 15

from xgboost.training import train

xgboostModel = xgboost.train(param, xgboosttrain, epochs)
# xgbModel = train(param, xgbtrain, epochs)
xgboostPredict = xgboostModel.predict(xgboosttest)

print("Accuracy: ", metrics.accuracy_score(y_test, xgboostPredict))
print(classification_report(y_test, xgboostPredict))

# # import xgboost as xgb
# # from xgb.training import train
# # import xgboost
# # from xgboost.training import train
# # import xgboost
# # from xgboost.training import train

# import xgboost as xgb
# from xgb.training import train

# xgbtrain = xgb.DMatrix(X_smote, label=y_smote)
# xgbtest = xgb.DMatrix(X_test, label=y_test)

# param = {'max depth': 4, 'eta': 0.25, 'objective': 'multi:softmax', 'num_class': 10}
# epochs = 15

# xgbModel = xgb.train(param, xgbtrain, epochs)
# # xgbModel = train(param, xgbtrain, epochs)
# xgbPredict = xgbModel.predict(xgbtest)

# print("Accuracy: ", metrics.accuracy_score(y_test, xgbPredict))
# print(classification_report(y_test, xgbPredict))

#showing the actual corona result and predicted corona result side by side
result = pd.DataFrame({'Actual': y_test, 'Predicted': y_predict})
result

###Evaluating XGBOOST model

#necessary library
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.metrics import confusion_matrix

#Classification Report
from sklearn.metrics import classification_report

print(classification_report(y_test, y_predict, target_names=['Negative', 'Positive']))

#confusion matrix

cm = confusion_matrix(y_test, y_predict)

plt.figure(figsize=(6,4))
sns.heatmap(cm, annot=True, square=True,  fmt='d',
           cmap=plt.cm.Blues, cbar=False)
plt.ylabel('True Labels', fontsize=12)
plt.xlabel('Predicted Labels', fontsize=12)
plt.show()

#mean squared error
mean_squared_error(y_test, y_predict)

#mean absolute error
mean_absolute_error(y_test, y_predict)

#r2 Score
r2_score(y_test, y_predict)

#Model Performance Comparison`

#ROC & DET Curve

import xgboost
from sklearn.ensemble import AdaBoostClassifier
#N_SAMPLES = 1000

classifiers = {
    "adaBoostModel": AdaBoostClassifier(n_estimators=250, learning_rate=1),
    "xgboost": param(max_depth= 4, num_class= 10, eta= 0.25, objective= 'multi:softmax'),
    }


# prepare plots
fig, [ax_roc, ax_det] = plt.subplots(2, 1, figsize=(10, 10))

# from sklearn.metrics import DetCurveDisplay, RocCurveDisplay

# #N_SAMPLES = 1000

# classifiers = {
#     "Logistic Regression": LogisticRegression(),
#     "Decision Tree": DecisionTreeClassifier(criterion='entropy', random_state=100, max_depth=7),
#     "Random Forest": RandomForestClassifier(random_state=0),
#     "KNN": KNeighborsClassifier(n_neighbors=25, n_jobs=-1),
# }


# # prepare plots
# fig, [ax_roc, ax_det] = plt.subplots(2, 1, figsize=(10, 10))

# adaBoostModel = AdaBoostClassifier(n_estimators=250, learning_rate=1)
# param = {'max depth': 4, 'eta': 0.25, 'objective': 'multi:softmax', 'num_class': 10}
# epochs = 15

from sklearn.metrics import DetCurveDisplay, RocCurveDisplay
import xgboost
#N_SAMPLES = 1000

classifiers = {
    "adaBoostModel": AdaBoostClassifier(n_estimators=250, learning_rate=1),
    "xgboost": xgboost("max_depth"= 4, "eta"= 0.25, "objective"= "multi:softmax", "num_class"= 10),
    }


# prepare plots
fig, [ax_roc, ax_det] = plt.subplots(2, 1, figsize=(10, 10))

# for name, clf in classifiers.items():
#     clf.fit(X_train, y_train)

#     RocCurveDisplay.from_estimator(clf, X_test, y_test, ax=ax_roc, name=name)
#     DetCurveDisplay.from_estimator(clf, X_test, y_test, ax=ax_det, name=name)

# ax_roc.set_title("Receiver Operating Characteristic (ROC) curves")
# ax_det.set_title("Detection Error Tradeoff (DET) curves")

# ax_roc.grid(linestyle="--")
# ax_det.grid(linestyle="--")

# plt.legend()
# plt.show()

"""### Linear Regression Model"""

#necessary library
from sklearn.linear_model import LinearRegression

#training the model
model = LinearRegression()
model.fit(X_train, y_train)

#prediction on test data
predictions = model.predict(X_test)

#showing the actual corona result and predicted corona result side by side
result = pd.DataFrame({'Actual': y_test, 'Predicted': predictions})
result

#model's accurary score
model.score(X_test, y_test)

#save the model
import pickle

filename = 'LinearRegression_model.sav'
pickle.dump(model, open(filename, 'wb'))

"""### Apply smote in Logistic Regression Model"""

#necessary library
from sklearn.linear_model import LogisticRegression

#training the model
log_model = LogisticRegression()
log_model.fit(X_smote, y_smote)

#prediction on test data
predictions = log_model.predict(X_test)

#showing the actual corona result and predicted corona result side by side
result = pd.DataFrame({'Actual': y_test, 'Predicted': predictions})
result

#model's accurary score
log_model.score(X_test, y_test)

#save the model
import pickle

filename = 'LogisticRegression_model.sav'
pickle.dump(log_model, open(filename, 'wb'))

"""#### Evaluating logistic regression model"""

#necessary library
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.metrics import confusion_matrix

#Classification Report
from sklearn.metrics import classification_report

print(classification_report(y_test, predictions, target_names=['Negative', 'Positive']))

#confusion matrix

cm = confusion_matrix(y_test, predictions)

plt.figure(figsize=(6,4))
sns.heatmap(cm, annot=True, square=True,  fmt='d',
           cmap=plt.cm.Blues, cbar=False)
plt.ylabel('True Labels', fontsize=12)
plt.xlabel('Predicted Labels', fontsize=12)
plt.show()

#mean squared error
mean_squared_error(y_test, predictions)

#mean absolute error
mean_absolute_error(y_test, predictions)

#r2 Score
r2_score(y_test, predictions)

"""### Apply Smote in Decision Tree Model"""

#finding optimum depth for decision tree
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

depth = []
for i in range(1, 10):
    d_tree = DecisionTreeClassifier(criterion='entropy', random_state=100, max_depth=i)
    d_tree.fit(X_smote, y_smote)
    y_predict = d_tree.predict(X_test)
    depth.append(accuracy_score(y_test, y_predict))
    print('Depth= ', i, ": ", accuracy_score(y_test, y_predict))

#ploting the accuracies for different tree depth
plt.figure(figsize=(12, 8))
plt.plot(range(1, 10), depth, marker='o')
plt.xlabel('Depth', fontsize=20)
plt.ylabel('Accuracy', fontsize=20)
plt.xticks(range(1, 10))
legend_prop = {'weight':'bold'}
plt.legend(prop=legend_prop)
plt.show()

#making model with depth=7 for prediction
d_tree = DecisionTreeClassifier(criterion='entropy', random_state=100, max_depth=7)
d_tree.fit(X_train, y_train)

#prediction on test data
predictions = d_tree.predict(X_test)

#showing the actual corona result and predicted corona result side by side
result = pd.DataFrame({'Actual': y_test, 'Predicted': predictions})
result

#model's accurary score
d_tree.score(X_test, y_test)

#save the model
import pickle

filename = 'DecisionTree_model.sav'
pickle.dump(d_tree, open(filename, 'wb'))

"""#### Evaluating Decision Tree model"""

#classification report for Decision Tree
print(classification_report(y_test, predictions, target_names=['Negative', 'Positive']))

#confusion matrix

cm = confusion_matrix(y_test, predictions)

plt.figure(figsize=(6,4))
sns.heatmap(cm, annot=True, square=True,  fmt='d',
           cmap=plt.cm.Blues, cbar=False)
plt.ylabel('True Labels', fontsize=12)
plt.xlabel('Predicted Labels', fontsize=12)
plt.show()

#mean squared error
mean_squared_error(y_test, predictions)

#mean absolute error
mean_absolute_error(y_test, predictions)

#r2 Score
r2_score(y_test, predictions)

"""### Apply Smote in Random Forest Model"""

#creating model and making predicton
from sklearn.ensemble import RandomForestClassifier

r_forest = RandomForestClassifier(random_state=0)
r_forest.fit(X_smote, y_smote)

#prediction on test data
predictions = r_forest.predict(X_test)

#showing the actual corona result and predicted corona result side by side
result = pd.DataFrame({'Actual': y_test, 'Predicted': predictions})
result

#model's accurary score
r_forest.score(X_test, y_test)

#save the model

filename = 'RandomForest_model.sav'
pickle.dump(r_forest, open(filename, 'wb'))

"""#### Evaluating Random Forest model"""

#Classification Report

print(classification_report(y_test, predictions, target_names=['Negative', 'Positive']))

#confusion matrix

cm = confusion_matrix(y_test, predictions)

plt.figure(figsize=(6,4))
sns.heatmap(cm, annot=True, square=True,  fmt='d',
           cmap=plt.cm.Blues, cbar=False)
plt.ylabel('True Labels', fontsize=12)
plt.xlabel('Predicted Labels', fontsize=12)
plt.show()

#mean squared error
mean_squared_error(y_test, predictions)

#mean absolute error
mean_absolute_error(y_test, predictions)

#r2 Score
r2_score(y_test, predictions)

"""### Apply Smote in KNN Model

Creating a smaller subset of test data for KNN
"""

d_X_test = X_test.head(10000)
#d_X_test.value_counts()

d_y_test = y_test.head(10000)
d_y_test.value_counts()

"""Training the model"""

#necessary library
from sklearn.neighbors import KNeighborsClassifier

#making model with k=25 for prediction
KNN = KNeighborsClassifier(n_neighbors=25, n_jobs=-1)
KNN.fit(X_smote, y_smote)

#prediction on test data
predictions = KNN.predict(X_test)

#showing the actual corona result and predicted corona result side by side
result = pd.DataFrame({'Actual': y_test, 'Predicted': predictions})
result

#model's accurary score
KNN.score(X_test, y_test)

#save the model

filename = 'KNN_model.sav'
pickle.dump(KNN, open(filename, 'wb'))

"""#### Evaluating KNN model"""

#Classification Report

print(classification_report(y_test, predictions, target_names=['Negative', 'Positive']))

#confusion matrix

cm = confusion_matrix(y_test, predictions)

plt.figure(figsize=(6,4))
sns.heatmap(cm, annot=True, square=True,  fmt='d',
           cmap=plt.cm.Blues, cbar=False)
plt.ylabel('True Labels', fontsize=12)
plt.xlabel('Predicted Labels', fontsize=12)
plt.show()

#mean squared error
mean_squared_error(y_test, predictions)

#mean absolute error
mean_absolute_error(y_test, predictions)

#r2 Score
r2_score(y_test, predictions)

"""# Training ANN Model

### Creating the model
"""

#necessary library
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation,Dropout
from tensorflow.keras.constraints import max_norm

X_smote.shape

model = Sequential()

# input layer
model.add(Dense(60,  activation='relu'))
#model.add(Dropout(0.2))

# hidden layer
model.add(Dense(30, activation='relu'))
#model.add(Dropout(0.2))

# hidden layer
model.add(Dense(15, activation='relu'))
#model.add(Dropout(0.2))

# output layer
model.add(Dense(units=1,activation='sigmoid'))

# Compile model
model.compile(loss='binary_crossentropy', optimizer='adam')

#training the model
model.fit(x=X_train, y=y_train, epochs=25, validation_data=(X_test, y_test))

"""### Saving the model"""

#necessary library
from tensorflow.keras.models import load_model

model.save('ANN_model.h5')

"""### Evaluating the ANN Model"""

losses = pd.DataFrame(model.history.history)

losses[['loss','val_loss']].plot()

#predicting using ANN model
predictions = model.predict_classes(X_test)

print(classification_report(y_test,predictions))

#confusion matrix
cm = confusion_matrix(y_test, predictions)

plt.figure(figsize=(6,4))
sns.heatmap(cm, annot=True, square=True,  fmt='d',
           cmap=plt.cm.Blues, cbar=False)
plt.ylabel('True Labels', fontsize=12)
plt.xlabel('Predicted Labels', fontsize=12)
plt.show()

"""mean_squared_error(y_test, predictions)"""

#mean absolute error
mean_absolute_error(y_test, predictions)

#r2 Score
r2_score(y_test, predictions)

"""## SVM Model - Linear Kernel"""

from sklearn import svm

# model = svm.SVC(kernel='linear') # Linear Kernel
# model.fit(X_train, y_train)

#selecting a subset of dataset
X_train_x = X_train.iloc[:20000]
y_train_y = y_train.iloc[:20000]

model = svm.SVC(kernel='linear') # Linear Kernel

model.fit(X_train_x, y_train_y)

#prediction on test data
predictions = model.predict(X_test)

#model's accurary score
model.score(X_test, y_test)

#save the model

filename = 'SVM_linear_model.sav'
#pickle.dump(model, open(filename, 'wb'))

###Evaluating SVM linear-kernel model

#Classification Report
print(classification_report(y_test, predictions, target_names=['Negative', 'Positive']))

#confusion matrix
cm = confusion_matrix(y_test, predictions)

plt.figure(figsize=(6,4))
sns.heatmap(cm, annot=True, square=True,  fmt='d',
           cmap=plt.cm.Blues, cbar=False)
plt.ylabel('True Labels', fontsize=12)
plt.xlabel('Predicted Labels', fontsize=12)
plt.show()

#mean squared error
mean_squared_error(y_test, predictions)

#mean absolute error
mean_absolute_error(y_test, predictions)

#r2 Score
r2_score(y_test, predictions)

"""### SVM Model - RBF Kernel"""

model = svm.SVC(kernel='rbf')

model.fit(X_train_x, y_train_y)

#prediction on test data
predictions = model.predict(X_test)

#model's accurary score
model.score(X_test, y_test)

#save the model
filename = 'SVM_rbf_model.sav'
pickle.dump(model, open(filename, 'wb'))

"""### Evaluating SVM rbf-kernel model"""

#Classification Report
print(classification_report(y_test, predictions, target_names=['Negative', 'Positive']))

#confusion matrix
cm = confusion_matrix(y_test, predictions)

plt.figure(figsize=(6,4))
sns.heatmap(cm, annot=True, square=True,  fmt='d',
           cmap=plt.cm.Blues, cbar=False)
plt.ylabel('True Labels', fontsize=12)
plt.xlabel('Predicted Labels', fontsize=12)
plt.show()

#mean squared error
mean_squared_error(y_test, predictions)

#mean absolute error
mean_absolute_error(y_test, predictions)

#r2 Score
r2_score(y_test, predictions)

"""### SVM Model polynomial-kernel"""

#finding optimum degree for svm polynomial kernel
degree = []
for i in range(1, 6):
    svm_model = svm.SVC(kernel='poly', degree=i)
    svm_model.fit(X_train_x, y_train_y)
    y_predict = svm_model.predict(X_test)
    degree.append(accuracy_score(y_test, y_predict))
    print('Degree= ', i, ": ", accuracy_score(y_test, y_predict))

#ploting the accuracies for different degree
plt.figure(figsize=(12, 8))
plt.plot(range(1, 6), degree, marker='o')
plt.xlabel('Degree', fontsize=20)
plt.ylabel('Accuracy', fontsize=20)
plt.xticks(range(1, 6))
legend_prop = {'weight':'bold'}
plt.legend(prop=legend_prop)
plt.show()

#training model with degree=4
model = svm.SVC(kernel='poly', degree=4)

model.fit(X_train_x, y_train_y)

#prediction on test data
predictions = model.predict(X_test)

#model's accurary score
model.score(X_test, y_test)

#save the model
filename = 'SVM_polynomial_model.sav'
pickle.dump(model, open(filename, 'wb'))

"""### Evaluating SVM polynomial-kernel model"""

#Classification Report
print(classification_report(y_test, predictions, target_names=['Negative', 'Positive']))

#confusion matrix
cm = confusion_matrix(y_test, predictions)

plt.figure(figsize=(6,4))
sns.heatmap(cm, annot=True, square=True,  fmt='d',
           cmap=plt.cm.Blues, cbar=False)
plt.ylabel('True Labels', fontsize=12)
plt.xlabel('Predicted Labels', fontsize=12)
plt.show()

#mean squared error
mean_squared_error(y_test, predictions)

#mean absolute error
mean_absolute_error(y_test, predictions)

#r2 Score
r2_score(y_test, predictions)

###Tuning the hyper-parameters

from sklearn.model_selection import GridSearchCV

param_grid = {'C': [0.1,1, 10, 100], 'gamma': [1,0.1,0.01,0.001],'kernel': ['rbf', 'poly', 'linear']}

grid = GridSearchCV(svm.SVC(),param_grid,refit=True,verbose=2)
grid.fit(X_train_x,y_train_y)

grid.best_params_

grid_predictions = grid.predict(X_test)
print(confusion_matrix(y_test,grid_predictions))
print(classification_report(y_test,grid_predictions))