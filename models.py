from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from flask_login import UserMixin
from sqlalchemy import desc
db = SQLAlchemy()

class CV(db.Model):
    __tablename__ = 'data_1'

    ID = db.Column(db.Integer, primary_key=True)
    Nom = db.Column(db.String(100))
    Prenom = db.Column(db.String(100))
    Fonction = db.Column(db.String(100))
    Domaine = db.Column(db.String(100))
    Niveau = db.Column(db.String(100))
    ColonneNiveau = db.Column(db.Integer)
    Annee_experience_en_conception = db.Column(db.String(100))
    ColonneExperience = db.Column(db.Integer)
    Localisation = db.Column(db.String(100))
    Source = db.Column(db.String(100))
    Url = db.Column(db.String(300))
    Gender = db.Column(db.String(100))
    Prediction = db.Column(db.Integer)

    def __init__(self, ID, Nom, Prenom, Gender, Fonction, Domaine, Niveau ,ColonneNiveau, Annee_experience_en_conception,ColonneExperience, Localisation, Source, Url, Prediction):
        self.ID = ID
        self.Nom = Nom
        self.Prenom = Prenom
        self.Gender = Gender
        self.Fonction = Fonction
        self.Domaine = Domaine
        self.Niveau = Niveau
        self.ColonneNiveau = ColonneNiveau
        self.Annee_experience_en_conception = Annee_experience_en_conception
        self.ColonneExperience = ColonneExperience
        self.Localisation = Localisation
        self.Source = Source
        self.Url = Url
        self.Prediction=Prediction
        
def __repr__(self):
        return f"<CV(ID={self.ID}, Nom={self.Nom}, Prénom={self.Prenom}, Fonction={self.Fonction}, Niveau={self.Niveau}, ...)>"  
def render_as_tuple():
    datasqlalchemy = CV.query.all()
    data = ()
    for row in datasqlalchemy:
        data_row = (
            row.ID,
            row.Nom,
            row.Prenom,
            row.Domaine,
            row.Gender,
            row.Fonction,
            row.Niveau,
            row.ColonneNiveau,
            row.Annee_experience_en_conception,
            row.Prediction,
            row.ColonneExperience,
            row.Localisation,
            row.Source,
            row.Url
        )
        data += (data_row,)
    return data

def render_as_dataframe():
    query_result = CV.query.all()
    data = []
    for row in query_result:
        data.append({
            'ID': row.ID,
            'Nom': row.Nom,
            'Prenom': row.Prenom,
            'Fonction': row.Fonction,
            'Domaine': row.Domaine,
            'Niveau': row.Niveau,
            'ColonneNiveau': row.ColonneNiveau,
            'Annee_experience_en_conception': row.Annee_experience_en_conception,
            'ColonneExperience': row.ColonneExperience,
            'Localisation': row.Localisation,
            'Source': row.Source,
            'Url': row.Url,
            'Gender': row.Gender
        })
    df = pd.DataFrame(data)
    return df

def render_as_tuple_custom(query):
    datasqlalchemy = query
    data = ()
    for row in datasqlalchemy:
        data_row = (
            row.ID,
            row.Nom,
            row.Prenom,
            row.Domaine,
            row.Gender,
            row.Fonction,
            row.Niveau,
            row.ColonneNiveau,
            row.Annee_experience_en_conception,
            row.Prediction,
            row.ColonneExperience,
            row.Localisation,
            row.Source,
            row.Url
        )
        data += (data_row,)
    return data

def last_CV_ID():
     last_id = CV.query.order_by(desc(CV.ID)).first().ID
     return last_id

class Users(db.Model,UserMixin):
    __tablename__ = 'users'

    ID = db.Column(db.Integer, primary_key=True)
    username  = db.Column(db.String(20),nullable=False)
    password = db.Column(db.String(80),nullable=False)
    email = db.Column(db.String(50))
    
    def get_id(self):
        return str(self.ID)
    
    def __repr__(self):
        return f"<Users(ID={self.ID}, Username={self.Username}, Email={self.Email})>"

class ContactUs(db.Model):
    __tablename__ = 'contactus'

    ID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Contact {self.ID}: {self.name} - {self.email} - {self.subject} - {self.message} >'