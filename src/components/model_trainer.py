import os
import sys
from dataclasses import dataclass

from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, GradientBoostingClassifier,StackingClassifier , BaggingClassifier
from xgboost import XGBClassifier

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC

from sklearn.metrics import accuracy_score,classification_report,confusion_matrix,f1_score, roc_auc_score, roc_curve, auc,precision_score,recall_score

from src.exception import CustomException
from src.logger import logging
from src.utils import evaluate_models, save_object

@dataclass
class ModelTrainerConfig:
    trained_model_file_path = os.path.join('artifacts','model.pkl')

class ModelTrainer:
    def __init__(self):
        self.model_trainer_config = ModelTrainerConfig()

    def initiate_model_trainer(self,train_arr,test_arr):
        try:
            logging.info('Split train and test data')
            X_train = train_arr.drop(['Output', 'Weighted_Score'], axis=1)
            X_test = test_arr.drop(['Output', 'Weighted_Score'], axis=1)
            y_train = train_arr['Output']
            y_test = test_arr['Output']
            
            estimators=[('Logistic Regression', LogisticRegression()), ('Linear Discriminant Analysis(LDA)', LinearDiscriminantAnalysis()), ('KNN', KNeighborsClassifier()), ('NB', GaussianNB()), ('SVM', SVC(probability=True)), ('Decision Tree', DecisionTreeClassifier())]
            models = {
                'Logistic Regression': LogisticRegression(),
                'Linear Discriminant Analysis(LDA)': LinearDiscriminantAnalysis(),
                'KNN': KNeighborsClassifier(),
                'NB': GaussianNB(),
                'SVM': SVC(probability=True),
                'Decision Tree': DecisionTreeClassifier(),
                'Stacking Classifier' : StackingClassifier(estimators=estimators),
                'Bagging Classifier' : BaggingClassifier(),
                'AdaBoost' : AdaBoostClassifier(algorithm='SAMME'),
                'Gradient Boosting' : GradientBoostingClassifier(),
                'Random Forest' : RandomForestClassifier(),
                'XG Boosting' : XGBClassifier()
            }

            params={
                'Logistic Regression': {
                    'penalty': ['l1', 'l2', 'elasticnet'],
                    'C': [0.001, 0.01, 0.1, 1, 10, 100],
                    'solver': ['newton-cg', 'lbfgs', 'liblinear', 'sag', 'saga'],
                    'max_iter': [100, 200, 300]
                },
                'Linear Discriminant Analysis(LDA)':{
                    'shrinkage': ['auto', 0.1, 0.2, 0.5, 0.8, 1.0],
                    'solver': ['lsqr', 'eigen']
                },
                'KNN':{
                    'n_neighbors': [1,2,3,4,5,6,7,8,9,10],
                    'weights': ['uniform', 'distance'],
                    'algorithm': ['auto', 'ball_tree', 'kd_tree', 'brute'],
                    'p': [1,2,3,4]
                },
                'NB':{},
                'SVM':{
                    'C': [0.001, 0.01, 0.1, 1, 10, 100],
                    'kernel': ['linear', 'poly', 'rbf', 'sigmoid'],
                    'gamma': ['scale', 'auto'],
                    'max_iter': [100, 200, 300]
                },
                'Decision Tree':{
                    'criterion': ['gini', 'entropy', 'log_loss'],
                    'splitter': ['best' , 'random'],
                    'max_depth': [100, 200, 300,None],
                    'min_samples_split': [2,3,4,5,6,7,8,9,10]
                },
                'Stacking Classifier':{
                    'stack_method': ['auto', 'predict_proba']
                },
                'Bagging Classifier':{
                    'n_estimators': [10, 50, 100],
                    'max_samples': [0.5, 1.0]
                },
                'AdaBoost':{
                    'n_estimators': [50, 100, 200],
                    'learning_rate': [0.01, 0.1, 1.0]
                },
                'Gradient Boosting':{
                    'n_estimators': [50, 100, 200],
                    'learning_rate': [0.01, 0.1, 1.0],
                    'max_depth': [3, 5, 7]
                },
                'Random Forest':{
                    'n_estimators': [50, 100, 200],
                    'max_depth': [None, 5, 10]
                },
                'XG Boosting':{
                    'n_estimators': [50, 100, 200],
                    'learning_rate': [0.01, 0.1, 1.0],
                    'max_depth': [3, 5, 7]
                },
            }

            model_report:dict=evaluate_models(X_train=X_train,y_train=y_train,X_test=X_test,y_test=y_test,
                                             models=models,param=params)
            best_model_score = max(sorted(model_report.values()))
            best_model_name = list(model_report.keys())[
                list(model_report.values()).index(best_model_score)
            ]
            best_model = models[best_model_name]
            logging.info(f"Best model {best_model}")
            if best_model_score<0.6:
                raise CustomException("No best model found")
            logging.info(f"Best found model on both training and testing dataset")


            save_object(
                file_path=self.model_trainer_config.trained_model_file_path,
                obj=best_model
            )
            predicted=best_model.predict(X_test)

            accuracy_score_value = accuracy_score(y_test, predicted)
            return accuracy_score_value
        
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            raise CustomException(e, sys)