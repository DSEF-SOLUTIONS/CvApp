from flask import Flask
from flask_wtf import FlaskForm
from wtforms import IntegerField, IntegerRangeField, SelectField, SelectField, StringField , SubmitField ,PasswordField, TextAreaField
from wtforms.validators import NumberRange,InputRequired,Length, Email


class SearchForm(FlaskForm):
    search = StringField('Entrer la recherche :')
    domain = SelectField('Séléctioner le Domaine :', choices=[
        ('all', 'Tous les Domaines'), 
        ('1', 'Ingénieur Qualité'),
        ('2', 'Economie et Gestion'),
        ('3', 'Technicien Spécialisé'),
        ('4', 'Ingénieur'),
        ('5', 'Ingénieur Industriel'),
        ('6', 'Chargé de Développement'),
        ('7', 'Concepteur ou Dessinateur'),
        ('8', 'Logistique'),
        ('9', 'Ingénieur Mécanique'),
        ('10', 'Ingénieur Process')
    ])
    niveau = IntegerRangeField('Séléctioner niveau', default=-1, validators=[NumberRange(min=-1, max=20)])
    experience = IntegerRangeField('Séléctioner experience', default=-1, validators=[NumberRange(min=-1, max=35)])
    prediction_status = SelectField('Prédiction Statut :', choices=[
        ('all', 'Tous'),
        ('1', 'Adéquat'),
        ('0', 'Non Adéquat')
    ])
    searchsubmit = SubmitField('Rechercher')

class TestForm(FlaskForm):
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    username = StringField("Nom d'utilisateur",validators=[InputRequired(),Length(min=4,max=20)],render_kw={"placeholder":"Entrer votre nom d'utilisateur :"})
    password = PasswordField('Mot de Passe',validators=[InputRequired(),Length(min=4,max=20)],render_kw={"placeholder":"Entrer votre MDP :"})
    submit = SubmitField('Se Connecter')

class AddCVForm(FlaskForm):
    ID = IntegerField('ID', validators=[])
    Nom = StringField('Nom')
    Prenom = StringField('Prénom')
    Gender = SelectField('Genre', choices=[
        ('M', 'Masculin'),
        ('F', 'Féminin')
    ])
    Fonction = StringField('Fonction', validators=[Length(max=100)])
    Domaine = SelectField('Séléctioner le Domaine :', choices=[
        ('1', 'Ingénieur Qualité'),
        ('2', 'Economie et Gestion'),
        ('3', 'Technicien Spécialisé'),
        ('4', 'Ingénieur'),
        ('5', 'Ingénieur Industriel'),
        ('6', 'Chargé de Développement'),
        ('7', 'Concepteur ou Dessinateur'),
        ('8', 'Logistique'),
        ('9', 'Ingénieur Mécanique'),
        ('10', 'Ingénieur Process')
    ])
    Niveau = SelectField('Niveau', choices=[
        ('BAC ', 'BAC '), 
        ('BAC + 1', 'BAC + 1'),
        ('BAC + 2', 'BAC + 2'),
        ('BAC + 3', 'BAC + 3'),
        ('BAC + 4', 'BAC + 4'),
        ('BAC + 5', 'BAC + 5'),
        ('BAC + 6', 'BAC + 6'),
        ('BAC + 7', 'BAC + 7'),
        ('BAC + 8', 'BAC + 8'),
        ('BAC + 9', 'BAC + 9'),
        ('BAC + 10', 'BAC + 10'),
        ('BAC + 11', 'BAC + 11'),
        ('BAC + 12', 'BAC + 12'),
        ('BAC + 13', 'BAC + 13'),
        ('BAC + 14', 'BAC + 14'),
        ('BAC + 15', 'BAC + 15'),
        ('BAC + 16', 'BAC + 16'),
        ('BAC + 17', 'BAC + 17'),
        ('BAC + 18', 'BAC + 18'),
        ('BAC + 19', 'BAC + 19'),
        ('BAC + 20', 'BAC + 20'),
    ])
    ColonneExperience = SelectField('Experience', choices=[
         ('0', "Moins d'un an"), 
        ('1', '1 an'),
        ('2', '2 ans'),
        ('3', '3 ans'),
        ('4', '4 ans'),
        ('5', '5 ans'),
        ('6', '6 ans'),
        ('7', '7 ans'),
        ('8', '8 ans'),
        ('9', '9 ans'),
        ('10', '10 ans'),
        ('11', '11 ans'),
        ('12', '12 ans'),
        ('13', '13 ans'),
        ('14', '14 ans'),
        ('15', '15 ans'),
        ('16', '16 ans'),
        ('17', '17 ans'),
        ('18', '18 ans'),
        ('19', '19 ans'),
        ('20', '20 ans'),
        ('21', '21 ans'),
        ('22', '22 ans'),
        ('23', '23 ans'),
        ('24', '24 ans'),
        ('25', '25 ans'),
        ('26', '26 ans'),
        ('27', '27 ans'),
        ('28', '28 ans'),
        ('29', '29 ans'),
        ('30', '30 ans'),
    ])
    Localisation = StringField('Localisation')
    Source = StringField('Source')
    Url = StringField('URL')
    addcvsubmit = SubmitField('Ajouter')

class ModifyCVForm(FlaskForm):
    ID = IntegerField('ID', validators=[])
    Nom = StringField('Nom')
    Prenom = StringField('Prénom')
    Gender = SelectField('Genre', choices=[
        ('M', 'Masculin'),
        ('F', 'Féminin')
    ])
    Fonction = StringField('Fonction')
    Domaine = SelectField('Séléctioner le Domaine :', choices=[
        ('1', 'Ingénieur Qualité'),
        ('2', 'Economie et Gestion'),
        ('3', 'Technicien Spécialisé'),
        ('4', 'Ingénieur'),
        ('5', 'Ingénieur Industriel'),
        ('6', 'Chargé de Développement'),
        ('7', 'Concepteur ou Dessinateur'),
        ('8', 'Logistique'),
        ('9', 'Ingénieur Mécanique'),
        ('10', 'Ingénieur Process')
    ])
    Niveau = SelectField('Niveau', choices=[
        ('BAC ', 'BAC '), 
        ('BAC + 1', 'BAC + 1'),
        ('BAC + 2', 'BAC + 2'),
        ('BAC + 3', 'BAC + 3'),
        ('BAC + 4', 'BAC + 4'),
        ('BAC + 5', 'BAC + 5'),
        ('BAC + 6', 'BAC + 6'),
        ('BAC + 7', 'BAC + 7'),
        ('BAC + 8', 'BAC + 8'),
        ('BAC + 9', 'BAC + 9'),
        ('BAC + 10', 'BAC + 10'),
        ('BAC + 11', 'BAC + 11'),
        ('BAC + 12', 'BAC + 12'),
        ('BAC + 13', 'BAC + 13'),
        ('BAC + 14', 'BAC + 14'),
        ('BAC + 15', 'BAC + 15'),
        ('BAC + 16', 'BAC + 16'),
        ('BAC + 17', 'BAC + 17'),
        ('BAC + 18', 'BAC + 18'),
        ('BAC + 19', 'BAC + 19'),
        ('BAC + 20', 'BAC + 20'),
    ])
    ColonneExperience = SelectField('Experience', choices=[
         ('0', "Moins d'un an"), 
        ('1', '1 an'),
        ('2', '2 ans'),
        ('3', '3 ans'),
        ('4', '4 ans'),
        ('5', '5 ans'),
        ('6', '6 ans'),
        ('7', '7 ans'),
        ('8', '8 ans'),
        ('9', '9 ans'),
        ('10', '10 ans'),
        ('11', '11 ans'),
        ('12', '12 ans'),
        ('13', '13 ans'),
        ('14', '14 ans'),
        ('15', '15 ans'),
        ('16', '16 ans'),
        ('17', '17 ans'),
        ('18', '18 ans'),
        ('19', '19 ans'),
        ('20', '20 ans'),
        ('21', '21 ans'),
        ('22', '22 ans'),
        ('23', '23 ans'),
        ('24', '24 ans'),
        ('25', '25 ans'),
        ('26', '26 ans'),
        ('27', '27 ans'),
        ('28', '28 ans'),
        ('29', '29 ans'),
        ('30', '30 ans'),
    ])
    Localisation = StringField('Localisation')
    Source = StringField('Source')
    Url = StringField('URL')
    modifycvsubmit = SubmitField('Modifier')
    
class ContactForm(FlaskForm):
    name = StringField('Nom et Prénom', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired()])
    subject = StringField('Sujet')
    message = TextAreaField('Message')
    contactformsubmit = SubmitField('Envoyer')
