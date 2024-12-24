import os
import sys
import pandas as pd
from src.exception import CustomException
from src.utils import load_object
from src.logger import logging


class PredictPipeline:
    def __init__(self):
        pass

    def predict(self,features):
        try:
            # Load the trained model
            model_path = os.path.join("artifacts", "model.pkl")
            if not os.path.exists(model_path):
                raise CustomException("Model file not found")
            self.model = load_object(model_path)
            logging.info("Model loaded successfully")

            # Load scaler and label encoder
            scaler_path = os.path.join("artifacts", "scaler.pkl")
            label_encoder_path = os.path.join("artifacts", "label_encoder.pkl")
            if not os.path.exists(scaler_path) or not os.path.exists(label_encoder_path):
                raise CustomException("Scaler or Label Encoder file not found")
            self.scaler = load_object(scaler_path)
            self.label_encoder = load_object(label_encoder_path)
            logging.info("Scaler and Label Encoder loaded successfully")

            # Scale numerical columns
            logging.info("Scaler start")
            numerical_columns = ["ColonneNiveau", "ColonneExperience"]
            features[numerical_columns] = self.scaler.transform(features[numerical_columns])
            logging.info("Scaler end success")
            # Encode categorical columns
            logging.info("encode start")
            features['Domain'] = self.label_encoder.transform(features['Domaine'])
            features['Gender'] = self.label_encoder.transform(features['Gender'])
            logging.info("encode end success")
            # Drop unnecessary columns
            features=features.drop(['Domaine'], axis=1, inplace=True)
            logging.info(f"features: {features}")

            
            preds = self.model.predict(features)
            logging.info(f"preds: {preds}")
            return preds
        
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            raise CustomException(e,sys)

class CustomData:
    def __init__(  self,
        Gender: str,
        Domain: str,
        ColonneExperience: int,
        ColonneNiveau: int):

        self.Gender = Gender

        self.Domain = Domain

        self.ColonneExperience = ColonneExperience

        self.ColonneNiveau = ColonneNiveau

    def get_data_as_data_frame(self):
        try:
            custom_data_input_dict = {
                "Gender": [self.Gender],
                "Domain": [self.Domain],
                "ColonneExperience": [self.ColonneExperience],
                "ColonneNiveau": [self.ColonneNiveau],
            }

            return pd.DataFrame(custom_data_input_dict)

        except Exception as e:
            logging.error(f"Error occurred: {e}")
            raise CustomException(e, sys)