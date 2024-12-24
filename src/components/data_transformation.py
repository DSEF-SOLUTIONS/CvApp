import os
import sys
from dataclasses import dataclass
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder,MinMaxScaler,StandardScaler
from sklearn.model_selection import train_test_split

from src.exception import CustomException
from src.logger import logging
from src.utils import save_object

@dataclass
class DataTransformationConfig:
    scaler_obj_file = os.path.join("artifacts","scaler.pkl")
    label_encoder_obj_file = os.path.join("artifacts","label_encoder.pkl")
    domain_encoded_file=os.path.join("artifacts","domain_encoded.xlsx")

class DataTransformation:
    def __init__(self) :
        self.data_transformation_config=DataTransformationConfig()

    def get_data_transformer_object(self):
        try:
            numerical_columns = ["ColonneNiveau", "ColonneExperience"]
            categorical_columns = ["Gender","Domaine"]

            num_pipeline= Pipeline(
                steps=[
                ("scaler",MinMaxScaler())
                ]
            )
            logging.info("Numerical columns min max scaling completed")
            logging.info(f"Numerical columns: {numerical_columns}")

            cat_pipeline=Pipeline(
                steps=[
                ("label_encoder",LabelEncoder()),
                ]
            )
            logging.info(f"Categorical columns encoding completed")
            logging.info(f"Categorical columns: {categorical_columns}")

            preprocessor=ColumnTransformer(
                [
                    ('num_pipeline',num_pipeline,numerical_columns),
                    ('cat_pipeline',cat_pipeline,categorical_columns)
                ]
            )
            return preprocessor
        except Exception as e :
            logging.error(f"Error occurred: {e}")
            raise CustomException(e,sys)
    
    def initiate_data_transformation(self,raw_data_path,train_path,test_path):
        try:
            df=pd.read_csv(raw_data_path)
            train_df=pd.read_csv(train_path)
            test_df=pd.read_csv(test_path)
            logging.info("Read train and test data completed")

            logging.info("Drop unnecessary columns")
            df=df.drop(['ID','Nom','Prénom','Fonction','Niveau',
                        "Niveau d'experience en conception",
                        'Localisation','Salaire Actuel','Prétention','Préavis',
                        'Commentaire','TJM','target','Source','Url','Colonne1','ID2'],axis=1)
            
            logging.info("Drop outliers and misspelling errors")
            df = df[df['Domaine'] != 'technicien']
            df = df[df['Domaine'] != 'opérateur']
            df = df[df['Domaine'] != 'autres']
            df['Domaine'] = df['Domaine'].replace('Ingénieur Industriel', 'ingénieur industriel')
            df['Domaine'] = df['Domaine'].replace('ingénieu qualité', 'ingénieur qualité')
            df['Domaine'] = df['Domaine'].str.replace('é', 'e')
            logging.info("Start Labelling")

            weights = {'ColonneExperience': 0.6, 'ColonneNiveau': 0.4}
            df['Weighted_Score'] = sum(df[col] * weights[col] for col in weights)
            threshold=df['Weighted_Score'].mean()
            logging.info(f"threshold {threshold}")

            for i, row in df.iterrows():
                if row['Weighted_Score']>=(threshold):
                    df.at[i, 'Output'] = 1
                else:
                    df.at[i, 'Output'] = 0

            logging.info("End Labelling")

            logging.info("Start scaling numerical_columns")

            numerical_columns = ["ColonneNiveau", "ColonneExperience"]
            categorical_columns = ["Gender","Domaine"]

            scaler = MinMaxScaler()
            df[numerical_columns] = scaler.fit_transform(df[numerical_columns])
            logging.info(f"Numerical columns after scaling: {numerical_columns}")
            logging.info("End scaling numerical_columns")


            logging.info("Encode columns")
            logging.info(f"Categorical columns before encode: {categorical_columns}")
            label_encoder = LabelEncoder()
            df['Domain_encoded'] = label_encoder.fit_transform(df['Domaine'])
            unique_domain_encoded = df[['Domaine', 'Domain_encoded']].drop_duplicates()
            logging.info(f"{unique_domain_encoded}")
            unique_domain_encoded.to_excel(self.data_transformation_config.domain_encoded_file , index=False)

            df=df.drop('Domaine',axis=1)
            df.rename(columns = {'Domain_encoded':'Domain'}, inplace = True) 

            df['Gender'] = label_encoder.fit_transform(df['Gender'])
            logging.info(f"Categorical columns after encode: {categorical_columns}")
            logging.info("Rename columns")
            df.rename(columns = {'ColonneExperience':'Experience'}, inplace = True) 
            df.rename(columns = {'ColonneNiveau':'Niveau'}, inplace = True) 
       
            logging.info("Splitting train and test sets ")

            train_set,test_set=train_test_split(df,test_size=0.2,random_state=42)

            logging.info(f"model columns : {train_set.columns}")
            print(f"model columns : {train_set.columns}")
            logging.info(f"Saved preprocessing object.")
            
            save_object(
                file_path = self.data_transformation_config.scaler_obj_file,
                obj =  scaler
            )
            save_object(
                file_path = self.data_transformation_config.label_encoder_obj_file,
                obj =  label_encoder
            )
            return (
                train_set,
                test_set,
                self.data_transformation_config.label_encoder_obj_file ,
                self.data_transformation_config.scaler_obj_file 
           )

        except Exception as e:
            logging.error(f"Error occurred: {e}")
            raise CustomException(e,sys)
