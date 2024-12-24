# =================================== Build app 4 (31/03/2024)===============================
# import pickle
import sys

from forms import SearchForm
from src.exception import CustomException
from src.logger import logging
from flask import Flask,request,render_template, flash
import numpy as np
import pandas as pd
from sklearn.preprocessing	import  MinMaxScaler
from src.pipeline.predict_pipeline import CustomData , PredictPipeline
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField , SubmitField
from wtforms.validators import DataRequired
from datetime import datetime
from models import db, CV

application = Flask(__name__)
app = application

app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_cv1'
mysql = MySQL(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/db_cv1'  
db.init_app(app)

@app.context_processor
def base():
    form=SearchForm()
    return dict(form=form)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/search', methods=('GET', 'POST'))
def search():
    form = SearchForm()
    search_term=None
    if request.method == 'POST' and form.validate_on_submit():
        search_term = request.form.get('domain')
        logging.info(f"search_term1: {search_term}")
        try:
            if search_term:
                    if search_term=='1':
                        search_term='ingénieu qualité'
                    elif search_term=='2':
                        search_term='économie / gestion'
                    elif search_term=='3':
                        search_term='technicien spécialisé'
                    elif search_term=='4':
                        search_term='ingénieur'
                    elif search_term=='5':
                        search_term='ingénieur industriel'
                    elif search_term=='6':
                        search_term='chargé de développement'
                    elif search_term=='7':
                        search_term='concepteur/ dessinateur'
                    elif search_term=='8':
                        search_term='logistique'
                    elif search_term=='9':
                        search_term='ingénieur mécanique'
                    elif search_term=='10':
                        search_term='ingénieur process'

                    cvs = CV.query.filter(CV.Domaine == search_term).all()
                    return render_template('search.html', cvs=cvs,search_term=search_term)
            else:
                cvs = CV.query.all()
                return render_template('search.html', cvs=cvs)
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            raise CustomException(e, sys)
    return render_template('search.html', form=form)


@app.route('/database', methods=['GET', 'POST'])
def database():
    form = SearchForm()

    if request.method == 'POST' and form.validate_on_submit():
        search_term = form.search.data
        try:
            if search_term:
                search_term = form.search.data
                cur = mysql.connection.cursor()
                cur.execute("SELECT * FROM `data_1` WHERE Nom LIKE %s OR `Prenom` LIKE %s ",
                            ('%' + search_term + '%', '%' + search_term + '%'))
                search_results = cur.fetchall()
                cur.close()
                data = []
                for row in search_results:
                    data_row = {
                        'ID': row[0],
                        'Nom': row[1],
                        'Prenom': row[2],
                        'Fonction': row[3],
                        'Niveau': row[5],
                        'ColonneNiveau': row[6],
                        'Experience': row[7],
                        'ColonneExperience': row[8],
                        'localisation': row[9],
                        'source': row[10],
                        'url': row[11],
                        'Gender': row[12],
                        'Domain': row[4]
                        }
                    data.append(data_row)
                    logging.info(f"data: {data}")
                if not data:
                    error = 'Invalid credentials'
                    logging.error(f"data: {data}")
                    logging.warning(f"No results found for search term: {search_term}")
                    flash('No results found for your search term.', 'warning')
                return render_template('Database.html', data=data, search=search_term)
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            raise CustomException(e, sys)
    else:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM `data_1` LIMIT 20")
        fetchdata = cur.fetchall()
        cur.close()
        
        data = []
        for row in fetchdata:
            data_row = {
                'ID': row[0],
                'Nom': row[1],
                'Prenom': row[2],
                'Fonction': row[3],
                'Niveau': row[5],
                'ColonneNiveau': row[6],
                'Experience': row[7],
                'ColonneExperience': row[8],
                'localisation': row[9],
                'source': row[10],
                'url': row[11],
                'Gender': row[12],
                'Domain': row[4]
            }
            pred_df = pd.DataFrame([data_row], columns=['ColonneNiveau', 'ColonneExperience', 'Gender', 'Domain'])
            pred_df['Domain'] = pred_df['Domain'].replace({'Ingénieur Industriel': 'ingenieur industriel', 'ingénieu qualité': 'ingenieur qualité'})
            pred_df['Domain'] = pred_df['Domain'].str.replace('é', 'e')
            predict_pipeline = PredictPipeline()
            prediction = predict_pipeline.predict(pred_df)[0]
            data_row['Prediction'] = prediction
            data_row['Domain'] = data_row['Domain'].replace('ingénieur', 'Ingénieur').replace('ingénieu qualité', 'Ingenieur Qualité').replace('économie / gestion', 'Economie et Gestion').replace('technicien spécialisé', 'Technicien Spécialisé').replace('ingénieur process', 'Ingénieur Process').replace('ingénieur process', 'Ingénieur Process').replace('chargé de développement', 'Chargé de Développement').replace('concepteur/ dessinateur', 'Concepteur ou Dessinateur').replace('logistique', 'Logistique').replace('ingénieur mécanique', 'Ingénieur Mécanique')
            data.append(data_row)
        return render_template('Database.html', data=data)
    # return render_template('Database.html', form=form, data=data, search=search_term)
    # except Exception as e:
    #     logging.error(f"Error occurred: {e}")
    #     raise CustomException(e, sys)
    #  # Add a default return statement outside of the try-except block
    # return render_template('Database.html', data=[])



@app.route('/predictdata',methods=['GET','POST'])
def predict_datapoint():
    if request.method == 'GET':
        return render_template("predict.html")
    else:
        data = CustomData(
            Gender=request.form.get('Gender'),
            Domain=request.form.get('Domain'),
            ColonneExperience=request.form.get('ColonneExperience'),
            ColonneNiveau=request.form.get('ColonneNiveau')
        )
        pred_df=data.get_data_as_data_frame()
        print(pred_df)
        predict_pipeline=PredictPipeline()
        results = predict_pipeline.predict(pred_df)
        return render_template('predict.html',results=results[0])

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)

# =================================== Build app 5 (01/04/2024)===============================

# import pickle
import sys

from forms import SearchForm, TestForm
from src.exception import CustomException
from src.logger import logging
from flask import Flask,request,render_template, flash
import numpy as np
import pandas as pd
from sklearn.preprocessing	import  MinMaxScaler
from src.pipeline.predict_pipeline import CustomData , PredictPipeline
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField , SubmitField
from wtforms.validators import DataRequired
from datetime import datetime
from models import db, CV, render_as_tuple

application = Flask(__name__)
app = application

app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_cv1'
mysql = MySQL(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/db_cv1'  
db.init_app(app)

@app.context_processor
def base():
    form=SearchForm()
    return dict(form=form)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/search', methods=('GET', 'POST'))
def search():
    form = TestForm()
    if request.method == 'POST' and form.validate_on_submit():
        try:
            new='Done'
            fetchdata = render_as_tuple()
            data = []
            for row in fetchdata:
                data_row = {
                    'ID': row[0],
                    'Nom': row[1],
                    'Prenom': row[2],
                    'Domain': row[3],
                    'Gender': row[4],
                    'Fonction': row[5],
                    'Niveau': row[6],
                    'ColonneNiveau': row[7],
                    'Annee_experience_en_conception': row[8],
                    'Prediction': row[13],
                    'ColonneExperience': row[9],
                    'localisation': row[10],
                    'source': row[11],
                    'url': row[12]
                }
                pred_df = pd.DataFrame([data_row], columns=['ColonneNiveau', 'ColonneExperience', 'Gender', 'Domain'])
                pred_df['Domain'] = pred_df['Domain'].replace({'Ingénieur Industriel': 'ingenieur industriel', 'ingénieu qualité': 'ingenieur qualité'})
                pred_df['Domain'] = pred_df['Domain'].str.replace('é', 'e')
                predict_pipeline = PredictPipeline()
                prediction = predict_pipeline.predict(pred_df)[0]
                cv_row = CV.query.filter_by(ID=row[0]).first()
                if cv_row:
                        cv_row.Prediction = prediction
                        db.session.commit()
            return render_template('search.html', new=new)
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            raise CustomException(e, sys)
    return render_template('search.html', form=form)

def fetch_all_data():
    fetchdata = render_as_tuple()
    logging.info(f"fetchdata : {fetchdata}")
    logging.info(f"fetchdata type: {type(fetchdata)}")
    data = []
    for row in fetchdata:
        data_row = {
            'ID': row[0],
            'Nom': row[1],
            'Prenom': row[2],
            'Domain': row[3],
            'Gender': row[4],
            'Fonction': row[5],
            'Niveau': row[6],
            'ColonneNiveau': row[7],
            'Annee_experience_en_conception': row[8],
            'ColonneExperience': row[9],
            'localisation': row[10],
            'source': row[11],
            'url': row[12]
        }
        pred_df = pd.DataFrame([data_row], columns=['ColonneNiveau', 'ColonneExperience', 'Gender', 'Domain'])
        pred_df['Domain'] = pred_df['Domain'].replace({'Ingénieur Industriel': 'ingenieur industriel', 'ingénieu qualité': 'ingenieur qualité'})
        pred_df['Domain'] = pred_df['Domain'].str.replace('é', 'e')
        predict_pipeline = PredictPipeline()
        prediction = predict_pipeline.predict(pred_df)[0]
        data_row['Prediction'] = prediction
        logging.info(f"prediction: {prediction}")
        data_row['Domain'] = data_row['Domain'].replace('ingénieur', 'Ingénieur').replace('ingénieu qualité', 'Ingenieur Qualité').replace('économie / gestion', 'Economie et Gestion').replace('technicien spécialisé', 'Technicien Spécialisé').replace('ingénieur process', 'Ingénieur Process').replace('ingénieur process', 'Ingénieur Process').replace('chargé de développement', 'Chargé de Développement').replace('concepteur/ dessinateur', 'Concepteur ou Dessinateur').replace('logistique', 'Logistique').replace('ingénieur mécanique', 'Ingénieur Mécanique')
        data.append(data_row)
    return data
@app.route('/database', methods=['GET', 'POST'])
def database():
    form = SearchForm()
    domain_selected_map = {
                        '1': 'ingénieu qualité',
                        '2': 'économie / gestion',
                        '3': 'technicien spécialisé',
                        '4': 'ingénieur',
                        '5': 'ingénieur industriel',
                        '6': 'chargé de développement',
                        '7': 'concepteur/ dessinateur',
                        '8': 'logistique',
                        '9': 'ingénieur mécanique',
                        '10': 'ingénieur process'
                    }
    if request.method == 'POST' and form.validate_on_submit():
        search_term = form.search.data
        domain_selected = request.form.get('domain')
        logging.info(f"search_term1: {search_term}")
        try:
            if search_term:
                search_term = form.search.data
                cur = mysql.connection.cursor()
                if domain_selected == 'all':
                    cur.execute("SELECT * FROM `data_1` WHERE Nom LIKE %s OR `Prenom` LIKE %s",
                                ('%' + search_term + '%', '%' + search_term + '%'))
                else:
                    domain_selected = domain_selected_map.get(domain_selected, '')
                    cur.execute("SELECT * FROM `data_1` WHERE (Nom LIKE %s OR `Prenom` LIKE %s) AND Domaine = %s",
                                ('%' + search_term + '%', '%' + search_term + '%', domain_selected))
                search_results = cur.fetchall()
                cur.close()
                data = []
                for row in search_results:
                    data_row = {
                        'ID': row[0],
                        'Nom': row[1],
                        'Prenom': row[2],
                        'Fonction': row[3],
                        'Niveau': row[5],
                        'ColonneNiveau': row[6],
                        'Annee_experience_en_conception': row[7],
                        'Prediction': row[13],
                        'ColonneExperience': row[8],
                        'localisation': row[9],
                        'source': row[10],
                        'url': row[11],
                        'Gender': row[12],
                        'Domain': row[4]
                    }
                    data.append(data_row)
                    logging.info(f"data: {data}")
                if not data:
                    logging.error(f"data: {data}")
                    logging.error(f"search_term: {search_term}")
                    logging.error(f"domain_selected: {domain_selected}")
                    logging.warning(f"No results found for search term: {search_term}")
                    flash('No results found for your search term.', 'warning')
                    return render_template('Database.html', data=data, search=search_term, domain_selected=domain_selected)
                else:
                    return render_template('Database.html', data=data, domain_selected=domain_selected)
            elif domain_selected:
                if domain_selected == 'all':
                    data=fetch_all_data()
                    return render_template('Database.html', data=data, domain_selected=domain_selected)
                else:
                    domain_selected = domain_selected_map.get(domain_selected, '')
                    data = CV.query.filter(CV.Domaine == domain_selected).all()
                    return render_template('Database.html', data=data, domain_selected=domain_selected)
            else:
                data=fetch_all_data()
                return render_template('Database.html', data=data)
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            raise CustomException(e, sys)
    else:
        try:
            data=fetch_all_data()
            return render_template('Database.html', data=data)
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            raise CustomException(e, sys)


@app.route('/predictdata',methods=['GET','POST'])
def predict_datapoint():
    if request.method == 'GET':
        return render_template("predict.html")
    else:
        data = CustomData(
            Gender=request.form.get('Gender'),
            Domain=request.form.get('Domain'),
            ColonneExperience=request.form.get('ColonneExperience'),
            ColonneNiveau=request.form.get('ColonneNiveau')
        )
        pred_df=data.get_data_as_data_frame()
        print(pred_df)
        predict_pipeline=PredictPipeline()
        results = predict_pipeline.predict(pred_df)
        return render_template('predict.html',results=results[0])

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)

# =================================== Build app 6 (03/04/2024 01:35)===============================

# import pickle
import sys

from forms import LoginForm, SearchForm, TestForm
from src.exception import CustomException
from src.logger import logging
from flask import Flask,request,render_template, flash ,redirect, url_for
import numpy as np
import pandas as pd
from sklearn.preprocessing	import  MinMaxScaler
from src.pipeline.predict_pipeline import CustomData , PredictPipeline
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField , SubmitField
from wtforms.validators import DataRequired
from datetime import datetime
from models import Users, db, CV, render_as_tuple, render_as_tuple_custom
from sqlalchemy import or_ , and_
from flask_login import login_user,LoginManager,login_required,logout_user,current_user
# from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt 
# from flask_bcrypt import check_password_hash
import bcrypt


application = Flask(__name__)
app = application

app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_cv1'
mysql = MySQL(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/db_cv1'  
db.init_app(app)

bcrypt = Bcrypt(app) 


@app.context_processor
def base():
    form=SearchForm()
    return dict(form=form)

@app.route('/')
def index():

    return render_template('index.html')

@app.route('/home', methods=('GET', 'POST'))
def home():
    return render_template('home.html')

login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = Users.query.filter_by(username=username).first()
        if not user:
            flash("Nom d'uilisateur incorrect. Veuillez réessayer à nouveau.")
            return redirect(url_for('login'))
        if not bcrypt.check_password_hash(user.password, password):
            flash('Mot de passe incorrect . Veuillez réessayer à nouveau.')
            return redirect(url_for('login'))
        login_user(user)
        flash('Bienvenue , ' + user.username + '!')
        return redirect(url_for('database'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        user = Users.query.filter_by(username=username).first()

        if user:
            flash('Utilisateur existant.')
            return redirect(url_for('register'))

        # Hash the password before storing it in the database
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = Users(email=email, username=username, password=hashed_password)

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        flash('Enregistrement avec succès.Vous pouvez vous connecter')
        return redirect(url_for('login'))

    return render_template('register.html')  # Replace 'success' with the name of your success route


@app.route('/search', methods=('GET', 'POST'))
@login_required
def search():
    form = TestForm()
    if request.method == 'POST' and form.validate_on_submit():
        try:
            new='Done'
            fetchdata = render_as_tuple()
            data = []
            for row in fetchdata:
                data_row = {
            'ID': row[0],
            'Nom': row[1],
            'Prenom': row[2],
            'Domain': row[3],
            'Gender': row[4],
            'Fonction': row[5],
            'Niveau': row[6],
            'ColonneNiveau': row[7],
            'Annee_experience_en_conception': row[8],
            'Prediction': row[9],
            'ColonneExperience': row[10],
            'Localisation': row[11],
            'Source': row[12],
            'Url': row[13]
        }
                pred_df = pd.DataFrame([data_row], columns=['ColonneNiveau', 'ColonneExperience', 'Gender', 'Domain'])
                pred_df['Domain'] = pred_df['Domain'].replace({'Ingénieur Industriel': 'ingenieur industriel', 'ingénieu qualité': 'ingenieur qualité'})
                pred_df['Domain'] = pred_df['Domain'].str.replace('é', 'e')
                predict_pipeline = PredictPipeline()
                prediction = predict_pipeline.predict(pred_df)[0]
                cv_row = CV.query.filter_by(ID=row[0]).first()
                if cv_row:
                        cv_row.Prediction = prediction
                        db.session.commit()
            return render_template('search.html', new=new)
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            raise CustomException(e, sys)
    return render_template('search.html', form=form)

def fetch_filtered_data(query):
    fetchdata = render_as_tuple_custom(query)
    logging.info(f"fetchdata : {fetchdata}")
    logging.info(f"fetchdata type: {type(fetchdata)}")
    data = []
    for row in fetchdata:
        data_row = {
            'ID': row[0],
            'Nom': row[1],
            'Prenom': row[2],
            'Domain': row[3],
            'Gender': row[4],
            'Fonction': row[5],
            'Niveau': row[6],
            'ColonneNiveau': row[7],
            'Annee_experience_en_conception': row[8],
            'Prediction': row[9],
            'ColonneExperience': row[10],
            'Localisation': row[11],
            'Source': row[12],
            'Url': row[13]
        }
        data_row['Domain'] = data_row['Domain'].replace('ingénieur', 'Ingénieur').replace('ingénieu qualité', 'Ingénieur Qualité').replace('économie / gestion', 'Economie et Gestion').replace('technicien spécialisé', 'Technicien Spécialisé').replace('ingénieur process', 'Ingénieur Process').replace('ingénieur industriel', 'Ingénieur Industriel').replace('Ingénieur industriel', 'Ingénieur Industriel').replace('chargé de développement', 'Chargé de Développement').replace('concepteur/ dessinateur', 'Concepteur ou Dessinateur').replace('logistique', 'Logistique').replace('ingénieur mécanique', 'Ingénieur Mécanique')
        data.append(data_row)

    return data

def fetch_all_data():
    fetchdata = render_as_tuple()
    logging.info(f"fetchdata : {fetchdata}")
    logging.info(f"fetchdata type: {type(fetchdata)}")
    data = []
    for row in fetchdata:
        data_row = {
            'ID': row[0],
            'Nom': row[1],
            'Prenom': row[2],
            'Domain': row[3],
            'Gender': row[4],
            'Fonction': row[5],
            'Niveau': row[6],
            'ColonneNiveau': row[7],
            'Annee_experience_en_conception': row[8],
            'Prediction': row[9],
            'ColonneExperience': row[10],
            'Localisation': row[11],
            'Source': row[12],
            'Url': row[13]
        }
        pred_df = pd.DataFrame([data_row], columns=['ColonneNiveau', 'ColonneExperience', 'Gender', 'Domain'])
        pred_df['Domain'] = pred_df['Domain'].replace({'Ingénieur Industriel': 'ingénieur industriel', 'ingénieu qualité': 'ingenieur qualité'})
        pred_df['Domain'] = pred_df['Domain'].str.replace('é', 'e')
        predict_pipeline = PredictPipeline()
        prediction = predict_pipeline.predict(pred_df)[0]
        data_row['Prediction'] = prediction
        logging.info(f"prediction: {prediction}")
        data_row['Domain'] = data_row['Domain'].replace('ingénieur', 'Ingénieur').replace('ingénieu qualité', 'Ingénieur Qualité').replace('économie / gestion', 'Economie et Gestion').replace('technicien spécialisé', 'Technicien Spécialisé').replace('ingénieur process', 'Ingénieur Process').replace('ingénieur industriel', 'Ingénieur Industriel').replace('Ingénieur industriel', 'Ingénieur Industriel').replace('chargé de développement', 'Chargé de Développement').replace('concepteur/ dessinateur', 'Concepteur ou Dessinateur').replace('logistique', 'Logistique').replace('ingénieur mécanique', 'Ingénieur Mécanique')
        data.append(data_row)
    return data
@app.route('/database', methods=['GET', 'POST'])
@login_required
def database():
    form = SearchForm()
    domain_selected_map = {
                        '1': 'ingénieu qualité',
                        '2': 'économie / gestion',
                        '3': 'technicien spécialisé',
                        '4': 'ingénieur',
                        '5': 'ingénieur industriel',
                        '6': 'chargé de développement',
                        '7': 'concepteur/ dessinateur',
                        '8': 'logistique',
                        '9': 'ingénieur mécanique',
                        '10': 'ingénieur process'
                    }
     #  'all': 'Tous les Domaines', 
    #                     '1': 'Ingénieur Qualité',
    #                     '2': 'Economie et Gestion',
    #                     '3': 'Technicien Spécialisé',
    #                     '4': 'Ingénieur',
    #                     '5': 'Ingénieur Industriel',
    #                     '6': 'Chargé de Développement',
    #                     '7': 'Concepteur ou Dessinateur',
    #                     '8': 'Logistique',
    #                     '9': 'Ingénieur Mécanique',
    #                     '10': 'Ingénieur Process'
    if request.method == 'POST':
        ID = request.form['ID']
        Nom = request.form['Nom']
        Prenom = request.form['Prenom']
        Gender = request.form['Gender']
        Fonction = request.form['Fonction']
        Domaine = request.form['Domaine']
        Niveau = request.form['Niveau']
        Experience = request.form['Experience']
        Localisation = request.form['Localisation']
        Source = request.form['Source']
        Url = request.form['Url']
        new = CV(ID, Nom,Prenom,Gender,Fonction,Domaine,Niveau,Experience,Localisation,Source,Url)
        db.session.add(new)
        db.session.commit()
        return render_template('modal.html', ID=ID, Nom=Nom, Prenom=Prenom, Gender=Gender, Fonction=Fonction, Domaine=Domaine, Niveau=Niveau, Experience=Experience, Localisation=Localisation, Source=Source, Url=Url)
    if request.method == 'POST' and form.validate_on_submit():
        search_term = form.search.data
        domain_selected = request.form.get('domain')
        niveau=request.form.get('niveau')
        niveau=int(niveau)
        logging.info(f"niveau: {niveau}")
        logging.info(f"niveau type: {type(niveau)}")
        experience=request.form.get('experience')
        experience=int(experience)
        logging.info(f"experience: {experience}")
        logging.info(f"experience type: {type(experience)}")
        query=CV.query
        # logging.info(f"search_term1: {search_term}")
        try:
            if search_term:
                search_term = form.search.data
                if domain_selected == 'all':
                    if experience ==-1 and niveau ==-1:
                        query=CV.query.limit(20).all()
                    elif experience ==-1 and niveau !=-1:
                        query = CV.query.filter(and_(CV.ColonneNiveau == niveau,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience !=-1 and niveau ==-1:
                        query = CV.query.filter(and_(CV.ColonneExperience == experience,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience !=-1 and niveau !=-1:
                        query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                else:
                    domain_selected = domain_selected_map.get(domain_selected, '')
                    if experience ==-1 and niveau ==-1:
                        query=CV.query.limit(20).all()
                    elif experience ==-1 and niveau !=-1:
                        query = CV.query.filter(and_(CV.ColonneNiveau == niveau,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience !=-1 and niveau ==-1:
                        query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience !=-1 and niveau !=-1:
                        query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                data = fetch_filtered_data(query)
                if not data:
                    logging.error(f"data: {data}")
                    logging.error(f"search_term: {search_term}")
                    logging.error(f"domain_selected: {domain_selected}")
                    logging.warning(f"No results found for search term: {search_term}")
                    flash('No results found for your search term.', 'warning')
                    return render_template('Database.html', data=data, search=search_term, domain_selected=domain_selected,niveau=niveau,experience=experience)
                else:
                    return render_template('Database.html', data=data, domain_selected=domain_selected,niveau=niveau,experience=experience)
            elif domain_selected:
                if domain_selected == 'all':
                    if experience ==-1 and niveau ==-1:
                        query=CV.query.limit(20).all()
                    elif experience ==-1 and niveau !=-1:
                        query = CV.query.filter(or_(CV.ColonneNiveau == niveau))
                    elif experience !=-1 and niveau ==-1:
                        query = CV.query.filter(or_(CV.ColonneExperience == experience))
                    elif experience !=-1 and niveau !=-1:
                        query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.ColonneNiveau == niveau))
                    data = fetch_filtered_data(query)
                    return render_template('Database.html', data=data, domain_selected=domain_selected,niveau=niveau,experience=experience)
                else:
                    domain_selected = domain_selected_map.get(domain_selected, '')
                    if experience ==-1 and niveau ==-1:
                        query = CV.query.filter(CV.Domaine == domain_selected)
                    elif experience ==-1 and niveau !=-1:
                        query = CV.query.filter(and_(CV.ColonneNiveau == niveau,CV.Domaine == domain_selected))
                    elif experience !=-1 and niveau ==-1:
                        query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.Domaine == domain_selected))
                    elif experience !=-1 and niveau !=-1:
                        query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected))
                    data = fetch_filtered_data(query)
                    return render_template('Database.html', data=data, domain_selected=domain_selected,niveau=niveau,experience=experience)
            else:
                data=fetch_all_data()
                logging.info(f"data4: {data}")
                return render_template('Database.html', data=data,niveau=niveau,experience=experience)
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            raise CustomException(e, sys)
    else:
        try:
            data=fetch_all_data()
            return render_template('Database.html', data=data)
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            raise CustomException(e, sys)


@app.route('/predictdata',methods=['GET','POST'])
@login_required
def predict_datapoint():
    if request.method == 'GET':
        return render_template("predict.html")
    else:
        data = CustomData(
            Gender=request.form.get('Gender'),
            Domain=request.form.get('Domain'),
            ColonneExperience=request.form.get('ColonneExperience'),
            ColonneNiveau=request.form.get('ColonneNiveau')
        )
        pred_df=data.get_data_as_data_frame()
        print(pred_df)
        predict_pipeline=PredictPipeline()
        results = predict_pipeline.predict(pred_df)
        return render_template('predict.html',results=results[0])


@app.route('/modal', methods=('GET', 'POST'))
def modal():
    if request.method == 'POST':
        ID = request.form['ID']
        Nom = request.form['Nom']
        Prenom = request.form['Prenom']
        Gender = request.form['Gender']
        Fonction = request.form['Fonction']
        Domaine = request.form['Domaine']
        Niveau = request.form['Niveau']
        Experience = request.form['Experience']
        Localisation = request.form['Localisation']
        Source = request.form['Source']
        Url = request.form['Url']
        new = CV(ID, Nom,Prenom,Gender,Fonction,Domaine,Niveau,Experience,Localisation,Source,Url)
        db.session.add(new)
        db.session.commit()
        return render_template('modal.html', ID=ID, Nom=Nom, Prenom=Prenom, Gender=Gender, Fonction=Fonction, Domaine=Domaine, Niveau=Niveau, Experience=Experience, Localisation=Localisation, Source=Source, Url=Url)
    
    # Render form template
    return render_template('modal.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)
# =================================== Build app 7 (03/04/2024 15:30)===============================

# import pickle
import sys

from forms import LoginForm, SearchForm, TestForm,AddCVForm
from src.exception import CustomException
from src.logger import logging
from flask import Flask,request,render_template, flash ,redirect, url_for
import numpy as np
import pandas as pd
from sklearn.preprocessing	import  MinMaxScaler
from src.pipeline.predict_pipeline import CustomData , PredictPipeline
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField , SubmitField
from wtforms.validators import DataRequired
from datetime import datetime
from models import Users, db, CV, last_CV_ID, render_as_tuple, render_as_tuple_custom
from sqlalchemy import or_ , and_
from flask_login import login_user,LoginManager,login_required,logout_user,current_user
# from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt 
# from flask_bcrypt import check_password_hash
import bcrypt


application = Flask(__name__)
app = application

app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_cv1'
mysql = MySQL(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/db_cv1'  
db.init_app(app)

bcrypt = Bcrypt(app) 


@app.context_processor
def base():
    form=SearchForm()
    return dict(form=form)

@app.route('/')
def index():

    return render_template('index.html')

@app.route('/home', methods=('GET', 'POST'))
def home():
    return render_template('home.html')

login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = Users.query.filter_by(username=username).first()
        if not user:
            flash("Nom d'uilisateur incorrect. Veuillez réessayer à nouveau.")
            return redirect(url_for('login'))
        if not bcrypt.check_password_hash(user.password, password):
            flash('Mot de passe incorrect . Veuillez réessayer à nouveau.')
            return redirect(url_for('login'))
        login_user(user)
        flash('Bienvenue , ' + user.username + '!')
        return redirect(url_for('database'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        user = Users.query.filter_by(username=username).first()

        if user:
            flash('Utilisateur existant.')
            return redirect(url_for('register'))

        # Hash the password before storing it in the database
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = Users(email=email, username=username, password=hashed_password)

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        flash('Enregistrement avec succès.Vous pouvez vous connecter')
        return redirect(url_for('login'))

    return render_template('register.html')  # Replace 'success' with the name of your success route


@app.route('/search', methods=('GET', 'POST'))
@login_required
def search():
    form = TestForm()
    if request.method == 'POST' and form.validate_on_submit():
        try:
            new='Done'
            fetchdata = render_as_tuple()
            data = []
            for row in fetchdata:
                data_row = {
            'ID': row[0],
            'Nom': row[1],
            'Prenom': row[2],
            'Domain': row[3],
            'Gender': row[4],
            'Fonction': row[5],
            'Niveau': row[6],
            'ColonneNiveau': row[7],
            'Annee_experience_en_conception': row[8],
            'Prediction': row[9],
            'ColonneExperience': row[10],
            'Localisation': row[11],
            'Source': row[12],
            'Url': row[13]
        }
                pred_df = pd.DataFrame([data_row], columns=['ColonneNiveau', 'ColonneExperience', 'Gender', 'Domain'])
                pred_df['Domain'] = pred_df['Domain'].replace({'Ingénieur Industriel': 'ingenieur industriel', 'ingénieu qualité': 'ingenieur qualité'})
                pred_df['Domain'] = pred_df['Domain'].str.replace('é', 'e')
                predict_pipeline = PredictPipeline()
                prediction = predict_pipeline.predict(pred_df)[0]
                cv_row = CV.query.filter_by(ID=row[0]).first()
                if cv_row:
                        cv_row.Prediction = prediction
                        db.session.commit()
            return render_template('search.html', new=new)
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            raise CustomException(e, sys)
    return render_template('search.html', form=form)

def fetch_filtered_data(query):
    fetchdata = render_as_tuple_custom(query)
    logging.info(f"fetchdata : {fetchdata}")
    logging.info(f"fetchdata type: {type(fetchdata)}")
    data = []
    for row in fetchdata:
        data_row = {
            'ID': row[0],
            'Nom': row[1],
            'Prenom': row[2],
            'Domain': row[3],
            'Gender': row[4],
            'Fonction': row[5],
            'Niveau': row[6],
            'ColonneNiveau': row[7],
            'Annee_experience_en_conception': row[8],
            'Prediction': row[9],
            'ColonneExperience': row[10],
            'Localisation': row[11],
            'Source': row[12],
            'Url': row[13]
        }
        data_row['Domain'] = data_row['Domain'].replace('ingénieur', 'Ingénieur').replace('ingénieu qualité', 'Ingénieur Qualité').replace('économie / gestion', 'Economie et Gestion').replace('technicien spécialisé', 'Technicien Spécialisé').replace('ingénieur process', 'Ingénieur Process').replace('ingénieur industriel', 'Ingénieur Industriel').replace('Ingénieur industriel', 'Ingénieur Industriel').replace('chargé de développement', 'Chargé de Développement').replace('concepteur/ dessinateur', 'Concepteur ou Dessinateur').replace('logistique', 'Logistique').replace('ingénieur mécanique', 'Ingénieur Mécanique')
        data.append(data_row)

    return data

def fetch_all_data():
    fetchdata = render_as_tuple()
    logging.info(f"fetchdata : {fetchdata}")
    logging.info(f"fetchdata type: {type(fetchdata)}")
    data = []
    for row in fetchdata:
        data_row = {
            'ID': row[0],
            'Nom': row[1],
            'Prenom': row[2],
            'Domain': row[3],
            'Gender': row[4],
            'Fonction': row[5],
            'Niveau': row[6],
            'ColonneNiveau': row[7],
            'Annee_experience_en_conception': row[8],
            'Prediction': row[9],
            'ColonneExperience': row[10],
            'Localisation': row[11],
            'Source': row[12],
            'Url': row[13]
        }
        pred_df = pd.DataFrame([data_row], columns=['ColonneNiveau', 'ColonneExperience', 'Gender', 'Domain'])
        pred_df['Domain'] = pred_df['Domain'].replace({'Ingénieur Industriel': 'ingénieur industriel', 'ingénieu qualité': 'ingenieur qualité'})
        pred_df['Domain'] = pred_df['Domain'].str.replace('é', 'e')
        predict_pipeline = PredictPipeline()
        prediction = predict_pipeline.predict(pred_df)[0]
        data_row['Prediction'] = prediction
        logging.info(f"prediction: {prediction}")
        data_row['Domain'] = data_row['Domain'].replace('ingénieur', 'Ingénieur').replace('ingénieu qualité', 'Ingénieur Qualité').replace('économie / gestion', 'Economie et Gestion').replace('technicien spécialisé', 'Technicien Spécialisé').replace('ingénieur process', 'Ingénieur Process').replace('ingénieur industriel', 'Ingénieur Industriel').replace('Ingénieur industriel', 'Ingénieur Industriel').replace('chargé de développement', 'Chargé de Développement').replace('concepteur/ dessinateur', 'Concepteur ou Dessinateur').replace('logistique', 'Logistique').replace('ingénieur mécanique', 'Ingénieur Mécanique')
        data.append(data_row)
    return data
@app.route('/database', methods=['GET', 'POST'])
@login_required
def database():
    form = SearchForm()
    domain_selected_map = {
                        '1': 'ingénieu qualité',
                        '2': 'économie / gestion',
                        '3': 'technicien spécialisé',
                        '4': 'ingénieur',
                        '5': 'ingénieur industriel',
                        '6': 'chargé de développement',
                        '7': 'concepteur/ dessinateur',
                        '8': 'logistique',
                        '9': 'ingénieur mécanique',
                        '10': 'ingénieur process'
                    }
    if request.method == 'POST' and form.validate_on_submit():
        search_term = form.search.data
        domain_selected = request.form.get('domain')
        niveau=request.form.get('niveau')
        niveau=int(niveau)
        logging.info(f"niveau: {niveau}")
        logging.info(f"niveau type: {type(niveau)}")
        experience=request.form.get('experience')
        experience=int(experience)
        logging.info(f"experience: {experience}")
        logging.info(f"experience type: {type(experience)}")
        query=CV.query
        # logging.info(f"search_term1: {search_term}")
        try:
            if search_term:
                search_term = form.search.data
                if domain_selected == 'all':
                    if experience ==-1 and niveau ==-1:
                        query=CV.query.filter(or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%')))
                    elif experience ==-1 and niveau !=-1:
                        query = CV.query.filter(and_(CV.ColonneNiveau == niveau,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience !=-1 and niveau ==-1:
                        query = CV.query.filter(and_(CV.ColonneExperience == experience,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience !=-1 and niveau !=-1:
                        query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                else:
                    domain_selected = domain_selected_map.get(domain_selected, '')
                    if experience ==-1 and niveau ==-1:
                        query=CV.query.filter(and_(CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience ==-1 and niveau !=-1:
                        query = CV.query.filter(and_(CV.ColonneNiveau == niveau,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience !=-1 and niveau ==-1:
                        query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience !=-1 and niveau !=-1:
                        query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                data = fetch_filtered_data(query)
                if not data:
                    logging.error(f"data: {data}")
                    logging.error(f"search_term: {search_term}")
                    logging.error(f"domain_selected: {domain_selected}")
                    logging.warning(f"No results found for search term: {search_term}")
                    flash('No results found for your search term.', 'warning')
                    return render_template('Database.html', data=data, search=search_term, domain_selected=domain_selected,niveau=niveau,experience=experience)
                else:
                    return render_template('Database.html', data=data, domain_selected=domain_selected,niveau=niveau,experience=experience)
            elif domain_selected:
                if domain_selected == 'all':
                    if experience ==-1 and niveau ==-1:
                        query=CV.query.limit(20).all()
                    elif experience ==-1 and niveau !=-1:
                        query = CV.query.filter(or_(CV.ColonneNiveau == niveau))
                    elif experience !=-1 and niveau ==-1:
                        query = CV.query.filter(or_(CV.ColonneExperience == experience))
                    elif experience !=-1 and niveau !=-1:
                        query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.ColonneNiveau == niveau))
                    data = fetch_filtered_data(query)
                    return render_template('Database.html', data=data, domain_selected=domain_selected,niveau=niveau,experience=experience)
                else:
                    domain_selected = domain_selected_map.get(domain_selected, '')
                    if experience ==-1 and niveau ==-1:
                        query = CV.query.filter(CV.Domaine == domain_selected)
                    elif experience ==-1 and niveau !=-1:
                        query = CV.query.filter(and_(CV.ColonneNiveau == niveau,CV.Domaine == domain_selected))
                    elif experience !=-1 and niveau ==-1:
                        query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.Domaine == domain_selected))
                    elif experience !=-1 and niveau !=-1:
                        query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected))
                    data = fetch_filtered_data(query)
                    return render_template('Database.html', data=data, domain_selected=domain_selected,niveau=niveau,experience=experience)
            else:
                data=fetch_all_data()
                logging.info(f"data4: {data}")
                return render_template('Database.html', data=data,niveau=niveau,experience=experience)
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            raise CustomException(e, sys)
    else:
        try:
            data=fetch_all_data()
            return render_template('Database.html', data=data)
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            raise CustomException(e, sys)


@app.route('/predictdata',methods=['GET','POST'])
@login_required
def predict_datapoint():
    if request.method == 'GET':
        return render_template("predict.html")
    else:
        data = CustomData(
            Gender=request.form.get('Gender'),
            Domain=request.form.get('Domain'),
            ColonneExperience=request.form.get('ColonneExperience'),
            ColonneNiveau=request.form.get('ColonneNiveau')
        )
        pred_df=data.get_data_as_data_frame()
        print(pred_df)
        predict_pipeline=PredictPipeline()
        results = predict_pipeline.predict(pred_df)
        return render_template('predict.html',results=results[0])


@app.route('/modal', methods=('GET', 'POST'))
def modal():
    domain_selected_map = {
                        '1': 'ingénieu qualité',
                        '2': 'économie / gestion',
                        '3': 'technicien spécialisé',
                        '4': 'ingénieur',
                        '5': 'ingénieur industriel',
                        '6': 'chargé de développement',
                        '7': 'concepteur/ dessinateur',
                        '8': 'logistique',
                        '9': 'ingénieur mécanique',
                        '10': 'ingénieur process'
                    }
    niveau_selected_map = {
        'BAC ': '',
        'BAC + 1': '1',
        'BAC + 2': '2',
        'BAC + 3': '3',
        'BAC + 4': '4',
        'BAC + 5': '5',
        'BAC + 6': '6',
        'BAC + 7': '7',
        'BAC + 8': '8',
        'BAC + 9': '9',
        'BAC + 10': '10',
        'BAC + 11': '11',
        'BAC + 12': '12',
        'BAC + 13': '13',
        'BAC + 14': '14',
        'BAC + 15': '15',
        'BAC + 16': '16',
        'BAC + 17': '17',
        'BAC + 18': '18',
        'BAC + 19': '19',
        'BAC + 20': '20',
                    }
    experience_selected_map = {
        '0': "Moins d'un an", 
        '1': '1 an',
        '2': '2 ans',
        '3': '3 ans',
        '4': '4 ans',
        '5': '5 ans',
        '6': '6 ans',
        '7': '7 ans',
        '8': '8 ans',
        '9': '9 ans',
        '10': '10 ans',
        '11': '11 ans',
        '12': '12 ans',
        '13': '13 ans',
        '14': '14 ans',
        '15': '15 ans',
        '16': '16 ans',
        '17': '17 ans',
        '18': '18 ans',
        '19': '19 ans',
        '20': '20 ans',
        '21': '21 ans',
        '22': '22 ans',
        '23': '23 ans',
        '24': '24 ans',
        '25': '25 ans',
        '26': '26 ans',
        '27': '27 ans',
        '28': '28 ans',
        '29': '29 ans',
        '30': '30 ans'
    }
    add_cv_form = AddCVForm()
    last_id = last_CV_ID()
    if request.method == 'POST' : 
        ID = add_cv_form.ID.data
        Nom = add_cv_form.Nom.data
        Prenom = add_cv_form.Prenom.data
        Gender = add_cv_form.Gender.data
        Fonction = add_cv_form.Fonction.data
        Domaine = add_cv_form.Domaine.data
        Domaine = domain_selected_map.get(Domaine, '')
        Niveau_label = add_cv_form.Niveau.data
        Niveau_selected = int(niveau_selected_map.get(Niveau_label, ''))
        ColonneExperience = add_cv_form.ColonneExperience.data
        Annee_experience_en_conception = experience_selected_map.get(ColonneExperience, '')
        ColonneExperience = int(ColonneExperience)
        Localisation = add_cv_form.Localisation.data
        Source = add_cv_form.Source.data
        Url = add_cv_form.Url.data
        new = CV(ID=ID, Nom=Nom, Prenom=Prenom, Gender=Gender, Fonction=Fonction, Domaine=Domaine,
                    Niveau=Niveau_label,ColonneNiveau=Niveau_selected, Annee_experience_en_conception=Annee_experience_en_conception,
                      ColonneExperience=ColonneExperience, Localisation=Localisation, Source=Source, Url=Url)
        db.session.add(new)
        db.session.commit()
        flash('CV added successfully', 'success')
        logging.info(f'CV added successfully : {new}')
        return render_template('modal.html',add_cv_form=add_cv_form,last_id=last_id, ID=ID, Nom=Nom, Prenom=Prenom, 
                               Gender=Gender, Fonction=Fonction, Domaine=Domaine, Niveau=Niveau_label,
                                 Annee_experience_en_conception=Annee_experience_en_conception, Localisation=Localisation,
                                   Source=Source, Url=Url)
    return render_template('modal.html',last_id=last_id,add_cv_form=add_cv_form)

@app.route('/candidature')
def candidature():
    domain_selected_map = {
                        '1': 'ingénieu qualité',
                        '2': 'économie / gestion',
                        '3': 'technicien spécialisé',
                        '4': 'ingénieur',
                        '5': 'ingénieur industriel',
                        '6': 'chargé de développement',
                        '7': 'concepteur/ dessinateur',
                        '8': 'logistique',
                        '9': 'ingénieur mécanique',
                        '10': 'ingénieur process'
                    }
    niveau_selected_map = {
        'BAC ': '',
        'BAC + 1': '1',
        'BAC + 2': '2',
        'BAC + 3': '3',
        'BAC + 4': '4',
        'BAC + 5': '5',
        'BAC + 6': '6',
        'BAC + 7': '7',
        'BAC + 8': '8',
        'BAC + 9': '9',
        'BAC + 10': '10',
        'BAC + 11': '11',
        'BAC + 12': '12',
        'BAC + 13': '13',
        'BAC + 14': '14',
        'BAC + 15': '15',
        'BAC + 16': '16',
        'BAC + 17': '17',
        'BAC + 18': '18',
        'BAC + 19': '19',
        'BAC + 20': '20',
                    }
    experience_selected_map = {
        '0': "Moins d'un an", 
        '1': '1 an',
        '2': '2 ans',
        '3': '3 ans',
        '4': '4 ans',
        '5': '5 ans',
        '6': '6 ans',
        '7': '7 ans',
        '8': '8 ans',
        '9': '9 ans',
        '10': '10 ans',
        '11': '11 ans',
        '12': '12 ans',
        '13': '13 ans',
        '14': '14 ans',
        '15': '15 ans',
        '16': '16 ans',
        '17': '17 ans',
        '18': '18 ans',
        '19': '19 ans',
        '20': '20 ans',
        '21': '21 ans',
        '22': '22 ans',
        '23': '23 ans',
        '24': '24 ans',
        '25': '25 ans',
        '26': '26 ans',
        '27': '27 ans',
        '28': '28 ans',
        '29': '29 ans',
        '30': '30 ans'
    }
    add_cv_form = AddCVForm()
    last_id = last_CV_ID()
    if request.method == 'POST' : 
        add_cv_form = AddCVForm(request.form)
        ID = add_cv_form.ID.data
        Nom = add_cv_form.Nom.data
        Prenom = add_cv_form.Prenom.data
        Gender = add_cv_form.Gender.data
        Fonction = add_cv_form.Fonction.data
        Domaine = add_cv_form.Domaine.data
        Domaine = domain_selected_map.get(Domaine, '')
        Niveau_label = add_cv_form.Niveau.data
        Niveau_selected = int(niveau_selected_map.get(Niveau_label, ''))
        ColonneExperience = add_cv_form.ColonneExperience.data
        Annee_experience_en_conception = experience_selected_map.get(ColonneExperience, '')
        ColonneExperience = int(ColonneExperience)
        Localisation = add_cv_form.Localisation.data
        Source = add_cv_form.Source.data
        Url = add_cv_form.Url.data
        new = CV(ID=ID, Nom=Nom, Prenom=Prenom, Gender=Gender, Fonction=Fonction, Domaine=Domaine,
                    Niveau=Niveau_label,ColonneNiveau=Niveau_selected, Annee_experience_en_conception=Annee_experience_en_conception,
                      ColonneExperience=ColonneExperience, Localisation=Localisation, Source=Source, Url=Url)
        db.session.add(new)
        db.session.commit()
        flash('CV added successfully', 'success')
        logging.info(f'CV added successfully : {new}')
        return render_template('candidature.html',add_cv_form=add_cv_form,last_id=last_id, ID=ID, Nom=Nom, Prenom=Prenom, 
                               Gender=Gender, Fonction=Fonction, Domaine=Domaine, Niveau=Niveau_label,
                                 Annee_experience_en_conception=Annee_experience_en_conception, Localisation=Localisation,
                                   Source=Source, Url=Url)
    return render_template('candidature.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)

# =================================== Build app 8 (04/04/2024 15:22)===============================

# import pickle
import sys

from forms import LoginForm, ModifyCVForm, SearchForm, TestForm,AddCVForm
from src.exception import CustomException
from src.logger import logging
from flask import Flask,request,render_template, flash ,redirect, url_for
import numpy as np
import pandas as pd
from sklearn.preprocessing	import  MinMaxScaler
from src.pipeline.predict_pipeline import CustomData , PredictPipeline
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField , SubmitField
from wtforms.validators import DataRequired
from datetime import datetime
from models import Users, db, CV, last_CV_ID, render_as_tuple, render_as_tuple_custom
from sqlalchemy import or_ , and_
from flask_login import login_user,LoginManager,login_required,logout_user,current_user
# from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt 
# from flask_bcrypt import check_password_hash
import bcrypt


application = Flask(__name__)
app = application

app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_cv1'
mysql = MySQL(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/db_cv1'  
db.init_app(app)

bcrypt = Bcrypt(app) 


@app.context_processor
def base():
    form=SearchForm()
    return dict(form=form)

@app.route('/')
def index():

    return render_template('index.html')

@app.route('/home', methods=('GET', 'POST'))
def home():
    return render_template('home.html')

login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = Users.query.filter_by(username=username).first()
        if not user:
            flash("Nom d'uilisateur incorrect. Veuillez réessayer à nouveau.")
            return redirect(url_for('login'))
        if not bcrypt.check_password_hash(user.password, password):
            flash('Mot de passe incorrect . Veuillez réessayer à nouveau.')
            return redirect(url_for('login'))
        login_user(user)
        flash('Bienvenue , ' + user.username + '!')
        return redirect(url_for('database'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        user = Users.query.filter_by(username=username).first()

        if user:
            flash('Utilisateur existant.')
            return redirect(url_for('register'))

        # Hash the password before storing it in the database
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = Users(email=email, username=username, password=hashed_password)

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        flash('Enregistrement avec succès.Vous pouvez vous connecter')
        return redirect(url_for('login'))

    return render_template('register.html')  # Replace 'success' with the name of your success route


@app.route('/search', methods=('GET', 'POST'))
@login_required
def search():
    return render_template('search.html')

def fetch_filtered_data(query):
    fetchdata = render_as_tuple_custom(query)
    logging.info(f"fetchdata : {fetchdata}")
    logging.info(f"fetchdata type: {type(fetchdata)}")
    data = []
    for row in fetchdata:
        data_row = {
            'ID': row[0],
            'Nom': row[1],
            'Prenom': row[2],
            'Domain': row[3],
            'Gender': row[4],
            'Fonction': row[5],
            'Niveau': row[6],
            'ColonneNiveau': row[7],
            'Annee_experience_en_conception': row[8],
            'Prediction': row[9],
            'ColonneExperience': row[10],
            'Localisation': row[11],
            'Source': row[12],
            'Url': row[13]
        }
        data_row['Domain'] = data_row['Domain'].replace('ingénieur', 'Ingénieur').replace('ingénieu qualité', 'Ingénieur Qualité').replace('économie / gestion', 'Economie et Gestion').replace('technicien spécialisé', 'Technicien Spécialisé').replace('ingénieur process', 'Ingénieur Process').replace('ingénieur industriel', 'Ingénieur Industriel').replace('Ingénieur industriel', 'Ingénieur Industriel').replace('chargé de développement', 'Chargé de Développement').replace('concepteur/ dessinateur', 'Concepteur ou Dessinateur').replace('logistique', 'Logistique').replace('ingénieur mécanique', 'Ingénieur Mécanique')
        data.append(data_row)

    return data

def fetch_all_data():
    fetchdata = render_as_tuple()
    logging.info(f"fetchdata : {fetchdata}")
    logging.info(f"fetchdata type: {type(fetchdata)}")
    data = []
    for row in fetchdata:
        data_row = {
            'ID': row[0],
            'Nom': row[1],
            'Prenom': row[2],
            'Domain': row[3],
            'Gender': row[4],
            'Fonction': row[5],
            'Niveau': row[6],
            'ColonneNiveau': row[7],
            'Annee_experience_en_conception': row[8],
            'Prediction': row[9],
            'ColonneExperience': row[10],
            'Localisation': row[11],
            'Source': row[12],
            'Url': row[13]
        }
        pred_df = pd.DataFrame([data_row], columns=['ColonneNiveau', 'ColonneExperience', 'Gender', 'Domain'])
        pred_df['Domain'] = pred_df['Domain'].replace({'Ingénieur Industriel': 'ingénieur industriel', 'ingénieu qualité': 'ingenieur qualité'})
        pred_df['Domain'] = pred_df['Domain'].str.replace('é', 'e')
        predict_pipeline = PredictPipeline()
        prediction = predict_pipeline.predict(pred_df)[0]
        data_row['Prediction'] = prediction
        logging.info(f"prediction: {prediction}")
        data_row['Domain'] = data_row['Domain'].replace('ingénieur', 'Ingénieur')\
            .replace('ingénieu qualité', 'Ingénieur Qualité')\
            .replace('ingenieur qualite', 'Ingénieur Qualité')\
            .replace('économie / gestion', 'Economie et Gestion')\
            .replace('technicien spécialisé', 'Technicien Spécialisé')\
            .replace('ingénieur process', 'Ingénieur Process')\
            .replace('ingénieur industriel', 'Ingénieur Industriel')\
            .replace('Ingénieur industriel', 'Ingénieur Industriel')\
            .replace('chargé de développement', 'Chargé de Développement')\
            .replace('concepteur/ dessinateur', 'Concepteur ou Dessinateur')\
            .replace('logistique', 'Logistique')\
            .replace('ingénieur mécanique', 'Ingénieur Mécanique')\
            .replace('ingenieur qualite', 'Ingénieur Qualité')\
            .replace('economie / gestion', 'Economie et Gestion')\
            .replace('technicien specialise', 'Technicien Spécialisé')\
            .replace('ingenieur process', 'Ingénieur Process')\
            .replace('ingenieur industriel', 'Ingénieur Industriel')\
            .replace('charge de developpement', 'Chargé de Développement')\
            .replace('concepteur/ dessinateur', 'Concepteur ou Dessinateur')\
            .replace('ingenieur', 'Ingénieur')
        data.append(data_row)
    return data
@app.route('/database', methods=['GET', 'POST'])
@login_required
def database():
    form = SearchForm()
    domain_selected_map = {
                        '1': 'ingénieu qualité',
                        '2': 'économie / gestion',
                        '3': 'technicien spécialisé',
                        '4': 'ingénieur',
                        '5': 'ingénieur industriel',
                        '6': 'chargé de développement',
                        '7': 'concepteur/ dessinateur',
                        '8': 'logistique',
                        '9': 'ingénieur mécanique',
                        '10': 'ingénieur process'
                    }
    if request.method == 'POST' and form.validate_on_submit():
        search_term = form.search.data
        domain_selected = request.form.get('domain')
        niveau=request.form.get('niveau')
        niveau=int(niveau)
        logging.info(f"niveau: {niveau}")
        logging.info(f"niveau type: {type(niveau)}")
        experience=request.form.get('experience')
        experience=int(experience)
        logging.info(f"experience: {experience}")
        logging.info(f"experience type: {type(experience)}")
        query=CV.query
        # logging.info(f"search_term1: {search_term}")
        try:
            if search_term:
                search_term = form.search.data
                if domain_selected == 'all':
                    if experience ==-1 and niveau ==-1:
                        query=CV.query.filter(or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%')))
                    elif experience ==-1 and niveau !=-1:
                        query = CV.query.filter(and_(CV.ColonneNiveau == niveau,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience !=-1 and niveau ==-1:
                        query = CV.query.filter(and_(CV.ColonneExperience == experience,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience !=-1 and niveau !=-1:
                        query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                else:
                    domain_selected = domain_selected_map.get(domain_selected, '')
                    if experience ==-1 and niveau ==-1:
                        query=CV.query.filter(and_(CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience ==-1 and niveau !=-1:
                        query = CV.query.filter(and_(CV.ColonneNiveau == niveau,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience !=-1 and niveau ==-1:
                        query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience !=-1 and niveau !=-1:
                        query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                data = fetch_filtered_data(query)
                if not data:
                    logging.error(f"data: {data}")
                    logging.error(f"search_term: {search_term}")
                    logging.error(f"domain_selected: {domain_selected}")
                    logging.warning(f"No results found for search term: {search_term}")
                    flash('No results found for your search term.', 'warning')
                    return render_template('Database.html', data=data, search=search_term, domain_selected=domain_selected,niveau=niveau,experience=experience)
                else:
                    return render_template('Database.html', data=data, domain_selected=domain_selected,niveau=niveau,experience=experience)
            elif domain_selected:
                if domain_selected == 'all':
                    if experience ==-1 and niveau ==-1:
                        query=CV.query.limit(20).all()
                    elif experience ==-1 and niveau !=-1:
                        query = CV.query.filter(or_(CV.ColonneNiveau == niveau))
                    elif experience !=-1 and niveau ==-1:
                        query = CV.query.filter(or_(CV.ColonneExperience == experience))
                    elif experience !=-1 and niveau !=-1:
                        query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.ColonneNiveau == niveau))
                    data = fetch_filtered_data(query)
                    return render_template('Database.html', data=data, domain_selected=domain_selected,niveau=niveau,experience=experience)
                else:
                    domain_selected = domain_selected_map.get(domain_selected, '')
                    if experience ==-1 and niveau ==-1:
                        query = CV.query.filter(CV.Domaine == domain_selected)
                    elif experience ==-1 and niveau !=-1:
                        query = CV.query.filter(and_(CV.ColonneNiveau == niveau,CV.Domaine == domain_selected))
                    elif experience !=-1 and niveau ==-1:
                        query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.Domaine == domain_selected))
                    elif experience !=-1 and niveau !=-1:
                        query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected))
                    data = fetch_filtered_data(query)
                    return render_template('Database.html', data=data, domain_selected=domain_selected,niveau=niveau,experience=experience)
            else:
                data=fetch_all_data()
                logging.info(f"data4: {data}")
                return render_template('Database.html', data=data,niveau=niveau,experience=experience)
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            raise CustomException(e, sys)
    else:
        try:
            data=fetch_all_data()
            return render_template('Database.html', data=data)
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            raise CustomException(e, sys)


@app.route('/predictdata',methods=['GET','POST'])
@login_required
def predict_datapoint():
    if request.method == 'GET':
        return render_template("predict.html")
    else:
        data = CustomData(
            Gender=request.form.get('Gender'),
            Domain=request.form.get('Domain'),
            ColonneExperience=request.form.get('ColonneExperience'),
            ColonneNiveau=request.form.get('ColonneNiveau')
        )
        pred_df=data.get_data_as_data_frame()
        print(pred_df)
        predict_pipeline=PredictPipeline()
        results = predict_pipeline.predict(pred_df)
        return render_template('predict.html',results=results[0])


@app.route('/modal', methods=('GET', 'POST'))
@login_required
def modal():
    domain_selected_map = {
                        '1': 'ingenieur qualite',
                        '2': 'economie / gestion',
                        '3': 'technicien specialise',
                        '4': 'ingenieur',
                        '5': 'ingenieur industriel',
                        '6': 'charge de developpementt',
                        '7': 'concepteur/ dessinateur',
                        '8': 'logistique',
                        '9': 'ingenieur mecanique',
                        '10': 'ingenieur process'
                    }
    niveau_selected_map = {
        'BAC ': '',
        'BAC + 1': '1',
        'BAC + 2': '2',
        'BAC + 3': '3',
        'BAC + 4': '4',
        'BAC + 5': '5',
        'BAC + 6': '6',
        'BAC + 7': '7',
        'BAC + 8': '8',
        'BAC + 9': '9',
        'BAC + 10': '10',
        'BAC + 11': '11',
        'BAC + 12': '12',
        'BAC + 13': '13',
        'BAC + 14': '14',
        'BAC + 15': '15',
        'BAC + 16': '16',
        'BAC + 17': '17',
        'BAC + 18': '18',
        'BAC + 19': '19',
        'BAC + 20': '20',
                    }
    experience_selected_map = {
        '0': "Moins d'un an", 
        '1': '1 an',
        '2': '2 ans',
        '3': '3 ans',
        '4': '4 ans',
        '5': '5 ans',
        '6': '6 ans',
        '7': '7 ans',
        '8': '8 ans',
        '9': '9 ans',
        '10': '10 ans',
        '11': '11 ans',
        '12': '12 ans',
        '13': '13 ans',
        '14': '14 ans',
        '15': '15 ans',
        '16': '16 ans',
        '17': '17 ans',
        '18': '18 ans',
        '19': '19 ans',
        '20': '20 ans',
        '21': '21 ans',
        '22': '22 ans',
        '23': '23 ans',
        '24': '24 ans',
        '25': '25 ans',
        '26': '26 ans',
        '27': '27 ans',
        '28': '28 ans',
        '29': '29 ans',
        '30': '30 ans'
    }
    add_cv_form = AddCVForm()
    last_id = last_CV_ID()
    if request.method == 'POST' : 
        ID = add_cv_form.ID.data
        Nom = add_cv_form.Nom.data
        Prenom = add_cv_form.Prenom.data
        Gender = add_cv_form.Gender.data
        Fonction = add_cv_form.Fonction.data
        Domaine = add_cv_form.Domaine.data
        Domaine = domain_selected_map.get(Domaine, '')
        Niveau_label = add_cv_form.Niveau.data
        Niveau_selected = int(niveau_selected_map.get(Niveau_label, ''))
        ColonneExperience = add_cv_form.ColonneExperience.data
        Annee_experience_en_conception = experience_selected_map.get(ColonneExperience, '')
        ColonneExperience = int(ColonneExperience)
        Localisation = add_cv_form.Localisation.data
        Source = add_cv_form.Source.data
        Url = add_cv_form.Url.data
        new = CV(ID=ID, Nom=Nom, Prenom=Prenom, Gender=Gender, Fonction=Fonction, Domaine=Domaine,
                    Niveau=Niveau_label,ColonneNiveau=Niveau_selected, Annee_experience_en_conception=Annee_experience_en_conception,
                      ColonneExperience=ColonneExperience, Localisation=Localisation, Source=Source, Url=Url)
        db.session.add(new)
        db.session.commit()
        flash('CV added successfully', 'success')
        logging.info(f'CV added successfully : {new}')
        return render_template('modal.html',add_cv_form=add_cv_form,last_id=last_id, ID=ID, Nom=Nom, Prenom=Prenom, 
                               Gender=Gender, Fonction=Fonction, Domaine=Domaine, Niveau=Niveau_label,
                                 Annee_experience_en_conception=Annee_experience_en_conception, Localisation=Localisation,
                                   Source=Source, Url=Url)
    return render_template('modal.html',last_id=last_id,add_cv_form=add_cv_form)

@app.route('/candidature', methods=('GET', 'POST'))
def candidature():
    domain_selected_map = {
                        '1': 'ingenieur qualite',
                        '2': 'economie / gestion',
                        '3': 'technicien specialise',
                        '4': 'ingenieur',
                        '5': 'ingenieur industriel',
                        '6': 'charge de developpementt',
                        '7': 'concepteur/ dessinateur',
                        '8': 'logistique',
                        '9': 'ingenieur mecanique',
                        '10': 'ingenieur process'
                    }
    niveau_selected_map = {
        'BAC ': '',
        'BAC + 1': '1',
        'BAC + 2': '2',
        'BAC + 3': '3',
        'BAC + 4': '4',
        'BAC + 5': '5',
        'BAC + 6': '6',
        'BAC + 7': '7',
        'BAC + 8': '8',
        'BAC + 9': '9',
        'BAC + 10': '10',
        'BAC + 11': '11',
        'BAC + 12': '12',
        'BAC + 13': '13',
        'BAC + 14': '14',
        'BAC + 15': '15',
        'BAC + 16': '16',
        'BAC + 17': '17',
        'BAC + 18': '18',
        'BAC + 19': '19',
        'BAC + 20': '20',
                    }
    experience_selected_map = {
        '0': "Moins d'un an", 
        '1': '1 an',
        '2': '2 ans',
        '3': '3 ans',
        '4': '4 ans',
        '5': '5 ans',
        '6': '6 ans',
        '7': '7 ans',
        '8': '8 ans',
        '9': '9 ans',
        '10': '10 ans',
        '11': '11 ans',
        '12': '12 ans',
        '13': '13 ans',
        '14': '14 ans',
        '15': '15 ans',
        '16': '16 ans',
        '17': '17 ans',
        '18': '18 ans',
        '19': '19 ans',
        '20': '20 ans',
        '21': '21 ans',
        '22': '22 ans',
        '23': '23 ans',
        '24': '24 ans',
        '25': '25 ans',
        '26': '26 ans',
        '27': '27 ans',
        '28': '28 ans',
        '29': '29 ans',
        '30': '30 ans'
    }
    add_cv_form = AddCVForm()
    last_id = last_CV_ID()
    if request.method == 'POST' : 
        add_cv_form = AddCVForm(request.form)
        ID = add_cv_form.ID.data
        Nom = add_cv_form.Nom.data
        Prenom = add_cv_form.Prenom.data
        Gender = add_cv_form.Gender.data
        Fonction = add_cv_form.Fonction.data
        Domaine = add_cv_form.Domaine.data
        Domaine = domain_selected_map.get(Domaine, '')
        Niveau_label = add_cv_form.Niveau.data
        Niveau_selected = int(niveau_selected_map.get(Niveau_label, ''))
        ColonneExperience = add_cv_form.ColonneExperience.data
        Annee_experience_en_conception = experience_selected_map.get(ColonneExperience, '')
        ColonneExperience = int(ColonneExperience)
        Localisation = add_cv_form.Localisation.data
        Source = add_cv_form.Source.data
        Url = add_cv_form.Url.data
        new = CV(ID=ID, Nom=Nom, Prenom=Prenom, Gender=Gender, Fonction=Fonction, Domaine=Domaine,
                    Niveau=Niveau_label,ColonneNiveau=Niveau_selected, Annee_experience_en_conception=Annee_experience_en_conception,
                      ColonneExperience=ColonneExperience, Localisation=Localisation, Source=Source, Url=Url)
        db.session.add(new)
        db.session.commit()
        flash('CV added successfully', 'success')
        logging.info(f'CV added successfully : {new}')
        return render_template('candidature.html',add_cv_form=add_cv_form,last_id=last_id, ID=ID, Nom=Nom, Prenom=Prenom, 
                               Gender=Gender, Fonction=Fonction, Domaine=Domaine, Niveau=Niveau_label,
                                 Annee_experience_en_conception=Annee_experience_en_conception, Localisation=Localisation,
                                   Source=Source, Url=Url)
    return render_template('candidature.html',add_cv_form=add_cv_form,last_id=last_id)

@app.route('/modifiercv/<int:id>', methods=('GET', 'POST'))
@login_required
def modifiercv(id):
    cv = CV.query.get_or_404(id)
    mod_cv_form=ModifyCVForm()
    domain_selected_map = {
                        '1': 'ingenieur qualite',
                        '2': 'economie / gestion',
                        '3': 'technicien specialise',
                        '4': 'ingenieur',
                        '5': 'ingenieur industriel',
                        '6': 'charge de developpementt',
                        '7': 'concepteur/ dessinateur',
                        '8': 'logistique',
                        '9': 'ingenieur mecanique',
                        '10': 'ingenieur process'
                    }
    niveau_selected_map = {
        'BAC ': '',
        'BAC + 1': '1',
        'BAC + 2': '2',
        'BAC + 3': '3',
        'BAC + 4': '4',
        'BAC + 5': '5',
        'BAC + 6': '6',
        'BAC + 7': '7',
        'BAC + 8': '8',
        'BAC + 9': '9',
        'BAC + 10': '10',
        'BAC + 11': '11',
        'BAC + 12': '12',
        'BAC + 13': '13',
        'BAC + 14': '14',
        'BAC + 15': '15',
        'BAC + 16': '16',
        'BAC + 17': '17',
        'BAC + 18': '18',
        'BAC + 19': '19',
        'BAC + 20': '20',
                    }
    experience_selected_map = {
         "Moins d'un an":'0', 
         '1 an':'1',
         '2 ans':'2',
         '3 ans':'3',
         '4 ans':'4',
         '5 ans':'5',
         '6 ans':'6',
         '7 ans':'7',
         '8 ans':'8',
         '9 ans':'9',
         '10 ans':'10',
         '11 ans':'11',
         '12 ans':'12',
        '13 ans':'13',
         '14 ans':'14',
         '15 ans':'15',
         '16 ans':'16',
         '17 ans':'17',
         '18 ans':'18',
        '19 ans':'19',
         '20 ans':'20',
         '21 ans':'21',
         '22 ans':'22',
         '23 ans':'23',
         '24 ans':'24',
         '25 ans':'25',
         '26 ans':'26',
         '27 ans':'27',
         '28 ans':'28',
         '29 ans':'29',
         '30 ans':'30'
    }
    
    if request.method == 'POST' :
        ID = mod_cv_form.ID.data
        Nom = mod_cv_form.Nom.data
        Prenom = mod_cv_form.Prenom.data
        Gender = mod_cv_form.Gender.data
        Fonction = mod_cv_form.Fonction.data
        Domaine = mod_cv_form.Domaine.data.replace("é", "e")
        Niveau = mod_cv_form.Niveau.data
        ColonneNiveau = int(niveau_selected_map.get(Niveau, ''))
        Annee_experience_en_conception = mod_cv_form.ColonneExperience.data
        ColonneExperience= experience_selected_map.get(Annee_experience_en_conception, '')
        Localisation = mod_cv_form.Localisation.data
        Source = mod_cv_form.Source.data
        Url = mod_cv_form.Url.data

        cv.Nom=Nom
        cv.Prenom=Prenom
        cv.Gender=Gender
        cv.Fonction=Fonction
        cv.Domaine=Domaine
        cv.Niveau=Niveau
        cv.ColonneNiveau=ColonneNiveau
        cv.Annee_experience_en_conception=Annee_experience_en_conception
        cv.ColonneExperience=ColonneExperience
        cv.Localisation=Localisation
        cv.Source=Source
        cv.Url=Url

        db.session.commit()

        logging.info(f"cv:{cv.Nom , cv.Prenom , cv.Gender , cv.Fonction,cv.Domaine,cv.Niveau,cv.ColonneNiveau,cv.Annee_experience_en_conception,cv.ColonneExperience,cv.Localisation,cv.Source,cv.Url}")
        logging.info(f"les informations ont ete modifiees avec succes. ")
        return render_template("Database.html")
    return render_template('modifiercv.html',id=id ,cv=cv,mod_cv_form=mod_cv_form)

@app.route('/supprimercv/<int:id>', methods=('GET', 'POST'))
@login_required
def supprimercv(id):
    cv = CV.query.get_or_404(id)
    db.session.delete(cv)
    db.session.commit()
    return render_template('supprimercv.html',id=id)

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)

# =================================== Build app 9 (05/04/2024 11:04)===============================

# import pickle
import sys

from forms import LoginForm, ModifyCVForm, SearchForm, TestForm,AddCVForm
from src.exception import CustomException
from src.logger import logging
from flask import Flask,request,render_template, flash ,redirect, url_for
import numpy as np
import pandas as pd
from sklearn.preprocessing	import  MinMaxScaler
from src.pipeline.predict_pipeline import CustomData , PredictPipeline
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField , SubmitField
from wtforms.validators import DataRequired
from datetime import datetime
from models import Users, db, CV, last_CV_ID, render_as_tuple, render_as_tuple_custom
from sqlalchemy import or_ , and_,asc, desc
from flask_login import login_user,LoginManager,login_required,logout_user,current_user
# from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt 
# from flask_bcrypt import check_password_hash
import bcrypt


application = Flask(__name__)
app = application

app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_cv1'
mysql = MySQL(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/db_cv1'  
db.init_app(app)

bcrypt = Bcrypt(app) 


def fetch_filtered_data(query):
    fetchdata = render_as_tuple_custom(query)
    logging.info(f"fetchdata : {fetchdata}")
    logging.info(f"fetchdata type: {type(fetchdata)}")
    data = []
    for row in fetchdata:
        data_row = {
            'ID': row[0],
            'Nom': row[1],
            'Prenom': row[2],
            'Domain': row[3],
            'Gender': row[4],
            'Fonction': row[5],
            'Niveau': row[6],
            'ColonneNiveau': row[7],
            'Annee_experience_en_conception': row[8],
            'Prediction': row[9],
            'ColonneExperience': row[10],
            'Localisation': row[11],
            'Source': row[12],
            'Url': row[13]
        }
        data_row['Domain'] = data_row['Domain'].replace('ingénieur', 'Ingénieur').replace('ingénieu qualité', 'Ingénieur Qualité').replace('économie / gestion', 'Economie et Gestion').replace('technicien spécialisé', 'Technicien Spécialisé').replace('ingénieur process', 'Ingénieur Process').replace('ingénieur industriel', 'Ingénieur Industriel').replace('Ingénieur industriel', 'Ingénieur Industriel').replace('chargé de développement', 'Chargé de Développement').replace('concepteur/ dessinateur', 'Concepteur ou Dessinateur').replace('logistique', 'Logistique').replace('ingénieur mécanique', 'Ingénieur Mécanique')
        data.append(data_row)

    return data

def fetch_all_data():
    fetchdata = render_as_tuple()
    logging.info(f"fetchdata : {fetchdata}")
    logging.info(f"fetchdata type: {type(fetchdata)}")
    data = []
    for row in fetchdata:
        data_row = {
            'ID': row[0],
            'Nom': row[1],
            'Prenom': row[2],
            'Domain': row[3],
            'Gender': row[4],
            'Fonction': row[5],
            'Niveau': row[6],
            'ColonneNiveau': row[7],
            'Annee_experience_en_conception': row[8],
            'Prediction': row[9],
            'ColonneExperience': row[10],
            'Localisation': row[11],
            'Source': row[12],
            'Url': row[13]
        }
        pred_df = pd.DataFrame([data_row], columns=['ColonneNiveau', 'ColonneExperience', 'Gender', 'Domain'])
        pred_df['Domain'] = pred_df['Domain'].replace({'Ingénieur Industriel': 'ingénieur industriel', 'ingénieu qualité': 'ingenieur qualité'})
        pred_df['Domain'] = pred_df['Domain'].str.replace('é', 'e')
        predict_pipeline = PredictPipeline()
        prediction = predict_pipeline.predict(pred_df)[0]
        data_row['Prediction'] = prediction
        logging.info(f"prediction: {prediction}")
        data_row['Domain'] = data_row['Domain'].replace('ingénieur', 'Ingénieur')\
            .replace('ingénieu qualité', 'Ingénieur Qualité')\
            .replace('ingenieur qualite', 'Ingénieur Qualité')\
            .replace('économie / gestion', 'Economie et Gestion')\
            .replace('technicien spécialisé', 'Technicien Spécialisé')\
            .replace('ingénieur process', 'Ingénieur Process')\
            .replace('ingénieur industriel', 'Ingénieur Industriel')\
            .replace('Ingénieur industriel', 'Ingénieur Industriel')\
            .replace('chargé de développement', 'Chargé de Développement')\
            .replace('concepteur/ dessinateur', 'Concepteur ou Dessinateur')\
            .replace('logistique', 'Logistique')\
            .replace('ingénieur mécanique', 'Ingénieur Mécanique')\
            .replace('ingenieur qualite', 'Ingénieur Qualité')\
            .replace('economie / gestion', 'Economie et Gestion')\
            .replace('technicien specialise', 'Technicien Spécialisé')\
            .replace('ingenieur process', 'Ingénieur Process')\
            .replace('ingenieur industriel', 'Ingénieur Industriel')\
            .replace('charge de developpement', 'Chargé de Développement')\
            .replace('concepteur/ dessinateur', 'Concepteur ou Dessinateur')\
            .replace('ingenieur', 'Ingénieur')
        data.append(data_row)
    return data

@app.context_processor
def base():
    form=SearchForm()
    return dict(form=form)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home', methods=('GET', 'POST'))
def home():
    return render_template('home.html')

login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = Users.query.filter_by(username=username).first()
        if not user:
            flash("Nom d'uilisateur incorrect. Veuillez réessayer à nouveau.")
            return redirect(url_for('login'))
        if not bcrypt.check_password_hash(user.password, password):
            flash('Mot de passe incorrect . Veuillez réessayer à nouveau.')
            return redirect(url_for('login'))
        login_user(user)
        flash('Bienvenue , ' + user.username + '!')
        return redirect(url_for('database'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        user = Users.query.filter_by(username=username).first()

        if user:
            flash('Utilisateur existant.')
            return redirect(url_for('register'))

        # Hash the password before storing it in the database
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = Users(email=email, username=username, password=hashed_password)

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        flash('Enregistrement avec succès.Vous pouvez vous connecter')
        return redirect(url_for('login'))

    return render_template('register.html')  # Replace 'success' with the name of your success route


@app.route('/search', methods=('GET', 'POST'))
@login_required
def search():
    return render_template('search.html')

def fetch_data_sorted_by_column(column_name, order):
    # Replace this with your actual database query logic
    if column_name == 'Nom':
        return CV.query.order_by(order(CV.Nom)).all()
    elif column_name == 'Prenom':
        return CV.query.order_by(order(CV.Prenom)).all()
    elif column_name == 'ColonneNiveau':
        return CV.query.order_by(order(CV.ColonneNiveau)).all()
    elif column_name == 'ColonneExperience':
        return CV.query.order_by(order(CV.ColonneExperience)).all()
    else:
        return CV.query.all()
    
@app.route('/database', methods=['GET', 'POST'])
@login_required
def database():
    form = SearchForm()
    domain_selected_map = {
                        '1': 'ingénieu qualité',
                        '2': 'économie / gestion',
                        '3': 'technicien spécialisé',
                        '4': 'ingénieur',
                        '5': 'ingénieur industriel',
                        '6': 'chargé de développement',
                        '7': 'concepteur/ dessinateur',
                        '8': 'logistique',
                        '9': 'ingénieur mécanique',
                        '10': 'ingénieur process'
                    }
    if request.method == 'POST' and form.validate_on_submit():
        search_term = form.search.data
        domain_selected = request.form.get('domain')
        niveau=request.form.get('niveau')
        niveau=int(niveau)
        logging.info(f"niveau: {niveau}")
        logging.info(f"niveau type: {type(niveau)}")
        experience=request.form.get('experience')
        experience=int(experience)
        logging.info(f"experience: {experience}")
        logging.info(f"experience type: {type(experience)}")
        query=CV.query
        # logging.info(f"search_term1: {search_term}")
        try:
            if search_term:
                search_term = form.search.data
                if domain_selected == 'all':
                    if experience ==-1 and niveau ==-1:
                        query=CV.query.filter(or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%')))
                    elif experience ==-1 and niveau !=-1:
                        query = CV.query.filter(and_(CV.ColonneNiveau == niveau,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience !=-1 and niveau ==-1:
                        query = CV.query.filter(and_(CV.ColonneExperience == experience,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience !=-1 and niveau !=-1:
                        query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                else:
                    domain_selected = domain_selected_map.get(domain_selected, '')
                    if experience ==-1 and niveau ==-1:
                        query=CV.query.filter(and_(CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience ==-1 and niveau !=-1:
                        query = CV.query.filter(and_(CV.ColonneNiveau == niveau,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience !=-1 and niveau ==-1:
                        query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience !=-1 and niveau !=-1:
                        query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                data = fetch_filtered_data(query)
                if not data:
                    logging.error(f"data: {data}")
                    logging.error(f"search_term: {search_term}")
                    logging.error(f"domain_selected: {domain_selected}")
                    logging.warning(f"No results found for search term: {search_term}")
                    flash('No results found for your search term.', 'warning')
                    return render_template('Database.html', data=data, search=search_term, domain_selected=domain_selected,niveau=niveau,experience=experience)
                else:
                    return render_template('Database.html', data=data, domain_selected=domain_selected,niveau=niveau,experience=experience)
            elif domain_selected:
                if domain_selected == 'all':
                    if experience ==-1 and niveau ==-1:
                        query=CV.query.limit(20).all()
                    elif experience ==-1 and niveau !=-1:
                        query = CV.query.filter(or_(CV.ColonneNiveau == niveau))
                    elif experience !=-1 and niveau ==-1:
                        query = CV.query.filter(or_(CV.ColonneExperience == experience))
                    elif experience !=-1 and niveau !=-1:
                        query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.ColonneNiveau == niveau))
                    data = fetch_filtered_data(query)
                    return render_template('Database.html', data=data, domain_selected=domain_selected,niveau=niveau,experience=experience)
                else:
                    domain_selected = domain_selected_map.get(domain_selected, '')
                    if experience ==-1 and niveau ==-1:
                        query = CV.query.filter(CV.Domaine == domain_selected)
                    elif experience ==-1 and niveau !=-1:
                        query = CV.query.filter(and_(CV.ColonneNiveau == niveau,CV.Domaine == domain_selected))
                    elif experience !=-1 and niveau ==-1:
                        query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.Domaine == domain_selected))
                    elif experience !=-1 and niveau !=-1:
                        query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected))
                    data = fetch_filtered_data(query)
                    return render_template('Database.html', data=data, domain_selected=domain_selected,niveau=niveau,experience=experience)
            else:
                data=fetch_all_data()
                logging.info(f"data4: {data}")
                return render_template('Database.html', data=data,niveau=niveau,experience=experience)
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            raise CustomException(e, sys)
    else:
        try:
            data=fetch_all_data()
            sort_by = request.args.get('sort_by', 'ID')
            sort_order = request.args.get('sort_order', 'asc')
            if sort_by == 'Niveau':
                if sort_order == 'asc':
                    data = fetch_data_sorted_by_column('ColonneNiveau', asc)
                    sort_order = 'desc'
                else:
                    data = fetch_data_sorted_by_column('ColonneNiveau', desc)
                    sort_order = 'asc'
            elif sort_by == 'ColonneExperience':
                if sort_order == 'asc':
                    data = fetch_data_sorted_by_column('ColonneExperience', asc)
                    sort_order = 'desc'
                else:
                    data = fetch_data_sorted_by_column('ColonneExperience', desc)
                    sort_order = 'asc'
            else:
                if sort_order == 'asc':
                    data = fetch_data_sorted_by_column(sort_by, asc)
                else:
                    data = fetch_data_sorted_by_column(sort_by, desc)
            return render_template('Database.html', data=data, sort_by=sort_by, sort_order=sort_order)
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            raise CustomException(e, sys)


@app.route('/predictdata',methods=['GET','POST'])
@login_required
def predict_datapoint():
    if request.method == 'GET':
        return render_template("predict.html")
    else:
        data = CustomData(
            Gender=request.form.get('Gender'),
            Domain=request.form.get('Domain'),
            ColonneExperience=request.form.get('ColonneExperience'),
            ColonneNiveau=request.form.get('ColonneNiveau')
        )
        pred_df=data.get_data_as_data_frame()
        print(pred_df)
        predict_pipeline=PredictPipeline()
        results = predict_pipeline.predict(pred_df)
        return render_template('predict.html',results=results[0])


@app.route('/modal', methods=('GET', 'POST'))
@login_required
def modal():
    domain_selected_map = {
                        '1': 'ingenieur qualite',
                        '2': 'economie / gestion',
                        '3': 'technicien specialise',
                        '4': 'ingenieur',
                        '5': 'ingenieur industriel',
                        '6': 'charge de developpementt',
                        '7': 'concepteur/ dessinateur',
                        '8': 'logistique',
                        '9': 'ingenieur mecanique',
                        '10': 'ingenieur process'
                    }
    niveau_selected_map = {
        'BAC ': '',
        'BAC + 1': '1',
        'BAC + 2': '2',
        'BAC + 3': '3',
        'BAC + 4': '4',
        'BAC + 5': '5',
        'BAC + 6': '6',
        'BAC + 7': '7',
        'BAC + 8': '8',
        'BAC + 9': '9',
        'BAC + 10': '10',
        'BAC + 11': '11',
        'BAC + 12': '12',
        'BAC + 13': '13',
        'BAC + 14': '14',
        'BAC + 15': '15',
        'BAC + 16': '16',
        'BAC + 17': '17',
        'BAC + 18': '18',
        'BAC + 19': '19',
        'BAC + 20': '20',
                    }
    experience_selected_map = {
        '0': "Moins d'un an", 
        '1': '1 an',
        '2': '2 ans',
        '3': '3 ans',
        '4': '4 ans',
        '5': '5 ans',
        '6': '6 ans',
        '7': '7 ans',
        '8': '8 ans',
        '9': '9 ans',
        '10': '10 ans',
        '11': '11 ans',
        '12': '12 ans',
        '13': '13 ans',
        '14': '14 ans',
        '15': '15 ans',
        '16': '16 ans',
        '17': '17 ans',
        '18': '18 ans',
        '19': '19 ans',
        '20': '20 ans',
        '21': '21 ans',
        '22': '22 ans',
        '23': '23 ans',
        '24': '24 ans',
        '25': '25 ans',
        '26': '26 ans',
        '27': '27 ans',
        '28': '28 ans',
        '29': '29 ans',
        '30': '30 ans'
    }
    add_cv_form = AddCVForm()
    last_id = last_CV_ID()
    if request.method == 'POST' : 
        ID = add_cv_form.ID.data
        Nom = add_cv_form.Nom.data
        Prenom = add_cv_form.Prenom.data
        Gender = add_cv_form.Gender.data
        Fonction = add_cv_form.Fonction.data
        Domaine = add_cv_form.Domaine.data
        Domaine = domain_selected_map.get(Domaine, '')
        Niveau_label = add_cv_form.Niveau.data
        Niveau_selected = int(niveau_selected_map.get(Niveau_label, ''))
        ColonneExperience = add_cv_form.ColonneExperience.data
        Annee_experience_en_conception = experience_selected_map.get(ColonneExperience, '')
        ColonneExperience = int(ColonneExperience)
        Localisation = add_cv_form.Localisation.data
        Source = add_cv_form.Source.data
        Url = add_cv_form.Url.data
        new = CV(ID=ID, Nom=Nom, Prenom=Prenom, Gender=Gender, Fonction=Fonction, Domaine=Domaine,
                    Niveau=Niveau_label,ColonneNiveau=Niveau_selected, Annee_experience_en_conception=Annee_experience_en_conception,
                      ColonneExperience=ColonneExperience, Localisation=Localisation, Source=Source, Url=Url)
        db.session.add(new)
        db.session.commit()
        flash('CV added successfully', 'success')
        logging.info(f'CV added successfully : {new}')
        return render_template('modal.html',add_cv_form=add_cv_form,last_id=last_id, ID=ID, Nom=Nom, Prenom=Prenom, 
                               Gender=Gender, Fonction=Fonction, Domaine=Domaine, Niveau=Niveau_label,
                                 Annee_experience_en_conception=Annee_experience_en_conception, Localisation=Localisation,
                                   Source=Source, Url=Url)
    return render_template('modal.html',last_id=last_id,add_cv_form=add_cv_form)


@app.route('/candidature', methods=('GET', 'POST'))
def candidature():
    domain_selected_map = {
                        '1': 'ingenieur qualite',
                        '2': 'economie / gestion',
                        '3': 'technicien specialise',
                        '4': 'ingenieur',
                        '5': 'ingenieur industriel',
                        '6': 'charge de developpementt',
                        '7': 'concepteur/ dessinateur',
                        '8': 'logistique',
                        '9': 'ingenieur mecanique',
                        '10': 'ingenieur process'
                    }
    niveau_selected_map = {
        'BAC ': '',
        'BAC + 1': '1',
        'BAC + 2': '2',
        'BAC + 3': '3',
        'BAC + 4': '4',
        'BAC + 5': '5',
        'BAC + 6': '6',
        'BAC + 7': '7',
        'BAC + 8': '8',
        'BAC + 9': '9',
        'BAC + 10': '10',
        'BAC + 11': '11',
        'BAC + 12': '12',
        'BAC + 13': '13',
        'BAC + 14': '14',
        'BAC + 15': '15',
        'BAC + 16': '16',
        'BAC + 17': '17',
        'BAC + 18': '18',
        'BAC + 19': '19',
        'BAC + 20': '20',
                    }
    experience_selected_map = {
        '0': "Moins d'un an", 
        '1': '1 an',
        '2': '2 ans',
        '3': '3 ans',
        '4': '4 ans',
        '5': '5 ans',
        '6': '6 ans',
        '7': '7 ans',
        '8': '8 ans',
        '9': '9 ans',
        '10': '10 ans',
        '11': '11 ans',
        '12': '12 ans',
        '13': '13 ans',
        '14': '14 ans',
        '15': '15 ans',
        '16': '16 ans',
        '17': '17 ans',
        '18': '18 ans',
        '19': '19 ans',
        '20': '20 ans',
        '21': '21 ans',
        '22': '22 ans',
        '23': '23 ans',
        '24': '24 ans',
        '25': '25 ans',
        '26': '26 ans',
        '27': '27 ans',
        '28': '28 ans',
        '29': '29 ans',
        '30': '30 ans'
    }
    add_cv_form = AddCVForm()
    last_id = last_CV_ID()
    if request.method == 'POST' : 
        add_cv_form = AddCVForm(request.form)
        ID = add_cv_form.ID.data
        Nom = add_cv_form.Nom.data
        Prenom = add_cv_form.Prenom.data
        Gender = add_cv_form.Gender.data
        Fonction = add_cv_form.Fonction.data
        Domaine = add_cv_form.Domaine.data
        Domaine = domain_selected_map.get(Domaine, '')
        Niveau_label = add_cv_form.Niveau.data
        Niveau_selected = int(niveau_selected_map.get(Niveau_label, ''))
        ColonneExperience = add_cv_form.ColonneExperience.data
        Annee_experience_en_conception = experience_selected_map.get(ColonneExperience, '')
        ColonneExperience = int(ColonneExperience)
        Localisation = add_cv_form.Localisation.data
        Source = add_cv_form.Source.data
        Url = add_cv_form.Url.data
        new = CV(ID=ID, Nom=Nom, Prenom=Prenom, Gender=Gender, Fonction=Fonction, Domaine=Domaine,
                    Niveau=Niveau_label,ColonneNiveau=Niveau_selected, Annee_experience_en_conception=Annee_experience_en_conception,
                      ColonneExperience=ColonneExperience, Localisation=Localisation, Source=Source, Url=Url)
        db.session.add(new)
        db.session.commit()
        flash('CV added successfully', 'success')
        logging.info(f'CV added successfully : {new}')
        return render_template('candidature.html',add_cv_form=add_cv_form,last_id=last_id, ID=ID, Nom=Nom, Prenom=Prenom, 
                               Gender=Gender, Fonction=Fonction, Domaine=Domaine, Niveau=Niveau_label,
                                 Annee_experience_en_conception=Annee_experience_en_conception, Localisation=Localisation,
                                   Source=Source, Url=Url)
    return render_template('candidature.html',add_cv_form=add_cv_form,last_id=last_id)


@app.route('/modifiercv/<int:id>', methods=('GET', 'POST'))
@login_required
def modifiercv(id):
    cv = CV.query.get_or_404(id)
    mod_cv_form=ModifyCVForm()
    domain_selected_map = {
                        '1': 'ingenieur qualite',
                        '2': 'economie / gestion',
                        '3': 'technicien specialise',
                        '4': 'ingenieur',
                        '5': 'ingenieur industriel',
                        '6': 'charge de developpementt',
                        '7': 'concepteur/ dessinateur',
                        '8': 'logistique',
                        '9': 'ingenieur mecanique',
                        '10': 'ingenieur process'
                    }
    niveau_selected_map = {
        'BAC ': '',
        'BAC + 1': '1',
        'BAC + 2': '2',
        'BAC + 3': '3',
        'BAC + 4': '4',
        'BAC + 5': '5',
        'BAC + 6': '6',
        'BAC + 7': '7',
        'BAC + 8': '8',
        'BAC + 9': '9',
        'BAC + 10': '10',
        'BAC + 11': '11',
        'BAC + 12': '12',
        'BAC + 13': '13',
        'BAC + 14': '14',
        'BAC + 15': '15',
        'BAC + 16': '16',
        'BAC + 17': '17',
        'BAC + 18': '18',
        'BAC + 19': '19',
        'BAC + 20': '20',
                    }
    experience_selected_map = {
         "Moins d'un an":'0', 
         '1 an':'1',
         '2 ans':'2',
         '3 ans':'3',
         '4 ans':'4',
         '5 ans':'5',
         '6 ans':'6',
         '7 ans':'7',
         '8 ans':'8',
         '9 ans':'9',
         '10 ans':'10',
         '11 ans':'11',
         '12 ans':'12',
        '13 ans':'13',
         '14 ans':'14',
         '15 ans':'15',
         '16 ans':'16',
         '17 ans':'17',
         '18 ans':'18',
        '19 ans':'19',
         '20 ans':'20',
         '21 ans':'21',
         '22 ans':'22',
         '23 ans':'23',
         '24 ans':'24',
         '25 ans':'25',
         '26 ans':'26',
         '27 ans':'27',
         '28 ans':'28',
         '29 ans':'29',
         '30 ans':'30'
    }
    
    if request.method == 'POST' :
        ID = mod_cv_form.ID.data
        Nom = mod_cv_form.Nom.data
        Prenom = mod_cv_form.Prenom.data
        Gender = mod_cv_form.Gender.data
        Fonction = mod_cv_form.Fonction.data
        Domaine = mod_cv_form.Domaine.data.replace("é", "e")
        Niveau = mod_cv_form.Niveau.data
        ColonneNiveau = int(niveau_selected_map.get(Niveau, ''))
        Annee_experience_en_conception = mod_cv_form.ColonneExperience.data
        ColonneExperience= experience_selected_map.get(Annee_experience_en_conception, '')
        Localisation = mod_cv_form.Localisation.data
        Source = mod_cv_form.Source.data
        Url = mod_cv_form.Url.data

        cv.Nom=Nom
        cv.Prenom=Prenom
        cv.Gender=Gender
        cv.Fonction=Fonction
        cv.Domaine=Domaine
        cv.Niveau=Niveau
        cv.ColonneNiveau=ColonneNiveau
        cv.Annee_experience_en_conception=Annee_experience_en_conception
        cv.ColonneExperience=ColonneExperience
        cv.Localisation=Localisation
        cv.Source=Source
        cv.Url=Url

        db.session.commit()

        logging.info(f"cv:{cv.Nom , cv.Prenom , cv.Gender , cv.Fonction,cv.Domaine,cv.Niveau,cv.ColonneNiveau,cv.Annee_experience_en_conception,cv.ColonneExperience,cv.Localisation,cv.Source,cv.Url}")
        logging.info(f"les informations ont ete modifiees avec succes. ")
        return render_template("Database.html")
    return render_template('modifiercv.html',id=id ,cv=cv,mod_cv_form=mod_cv_form)


@app.route('/supprimercv/<int:id>', methods=('GET', 'POST'))
@login_required
def supprimercv(id):
    cv = CV.query.get_or_404(id)
    db.session.delete(cv)
    db.session.commit()
    return render_template('supprimercv.html',id=id)


if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)

# =================================== Build app 10 (05/04/2024 15:15)===============================

# import pickle
import sys

from forms import LoginForm, ModifyCVForm, SearchForm, TestForm,AddCVForm
from src.exception import CustomException
from src.logger import logging
from flask import Flask,request,render_template, flash ,redirect, url_for
import numpy as np
import pandas as pd
from sklearn.preprocessing	import  MinMaxScaler
from src.pipeline.predict_pipeline import CustomData , PredictPipeline
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField , SubmitField
from wtforms.validators import DataRequired
from datetime import datetime
from models import Users, db, CV, last_CV_ID, render_as_tuple, render_as_tuple_custom
from sqlalchemy import or_ , and_,asc, desc
from flask_login import login_user,LoginManager,login_required,logout_user,current_user
# from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt 
# from flask_bcrypt import check_password_hash
import bcrypt


application = Flask(__name__)
app = application

app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_cv1'
mysql = MySQL(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/db_cv1'  
db.init_app(app)

bcrypt = Bcrypt(app) 


def fetch_filtered_data(query):
    fetchdata = render_as_tuple_custom(query)
    # logging.info(f"fetchdata : {fetchdata}")
    logging.info(f"fetchdata type: {type(fetchdata)}")
    data = []
    for row in fetchdata:
        data_row = {
            'ID': row[0],
            'Nom': row[1],
            'Prenom': row[2],
            'Domain': row[3],
            'Gender': row[4],
            'Fonction': row[5],
            'Niveau': row[6],
            'ColonneNiveau': row[7],
            'Annee_experience_en_conception': row[8],
            'Prediction': row[9],
            'ColonneExperience': row[10],
            'Localisation': row[11],
            'Source': row[12],
            'Url': row[13]
        }
        data_row['Domain'] = data_row['Domain'].replace('ingénieur', 'Ingénieur').replace('ingénieu qualité', 'Ingénieur Qualité').replace('économie / gestion', 'Economie et Gestion').replace('technicien spécialisé', 'Technicien Spécialisé').replace('ingénieur process', 'Ingénieur Process').replace('ingénieur industriel', 'Ingénieur Industriel').replace('Ingénieur industriel', 'Ingénieur Industriel').replace('chargé de développement', 'Chargé de Développement').replace('concepteur/ dessinateur', 'Concepteur ou Dessinateur').replace('logistique', 'Logistique').replace('ingénieur mécanique', 'Ingénieur Mécanique')
        data.append(data_row)

    return data

def fetch_all_data():
    page = request.args.get('page', 1, type=int)
    fetchdata = render_as_tuple(page)
    data = []
    for row in fetchdata:
        data_row = {
            'ID': row[0],
            'Nom': row[1],
            'Prenom': row[2],
            'Domain': row[3],
            'Gender': row[4],
            'Fonction': row[5],
            'Niveau': row[6],
            'ColonneNiveau': row[7],
            'Annee_experience_en_conception': row[8],
            'Prediction': row[9],  # We'll update this later
            'ColonneExperience': row[10],
            'Localisation': row[11],
            'Source': row[12],
            'Url': row[13]
        }
        pred_df = pd.DataFrame([data_row], columns=['ColonneNiveau', 'ColonneExperience', 'Gender', 'Domain'])
        pred_df['Domain'] = pred_df['Domain'].replace({'Ingénieur Industriel': 'ingénieur industriel', 'ingénieu qualité': 'ingenieur qualité'})
        pred_df['Domain'] = pred_df['Domain'].str.replace('é', 'e')
        predict_pipeline = PredictPipeline()
        prediction = predict_pipeline.predict(pred_df)[0]
        data_row['Prediction'] = prediction  # Update the Prediction field in data_row
        # Update the Prediction in the database using SQLAlchemy
        cv_instance = CV.query.filter_by(ID=row[0]).first()
        if cv_instance:
            cv_instance.Prediction = prediction
            db.session.commit()  # Commit the changes to the database
        else:
            # Handle the case where the CV instance with the given ID is not found
            pass
        data_row['Domain'] = data_row['Domain'].replace('ingénieur', 'Ingénieur')\
            .replace('ingénieu qualité', 'Ingénieur Qualité')\
            .replace('ingenieur qualite', 'Ingénieur Qualité')\
            .replace('économie / gestion', 'Economie et Gestion')\
            .replace('technicien spécialisé', 'Technicien Spécialisé')\
            .replace('ingénieur process', 'Ingénieur Process')\
            .replace('ingénieur industriel', 'Ingénieur Industriel')\
            .replace('Ingénieur industriel', 'Ingénieur Industriel')\
            .replace('chargé de développement', 'Chargé de Développement')\
            .replace('concepteur/ dessinateur', 'Concepteur ou Dessinateur')\
            .replace('logistique', 'Logistique')\
            .replace('ingénieur mécanique', 'Ingénieur Mécanique')\
            .replace('ingenieur qualite', 'Ingénieur Qualité')\
            .replace('economie / gestion', 'Economie et Gestion')\
            .replace('technicien specialise', 'Technicien Spécialisé')\
            .replace('ingenieur process', 'Ingénieur Process')\
            .replace('ingenieur industriel', 'Ingénieur Industriel')\
            .replace('charge de developpement', 'Chargé de Développement')\
            .replace('concepteur/ dessinateur', 'Concepteur ou Dessinateur')\
            .replace('ingenieur', 'Ingénieur')
        data.append(data_row)
    return data

@app.context_processor
def base():
    form=SearchForm()
    return dict(form=form)

def get_records():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    return CV.query.order_by(asc(CV.ID)).paginate(page=page, per_page=per_page, error_out=False)
@app.route('/')
def index():
    # pagination = get_records()
    # records = pagination.items
    page = request.args.get('page', 1, type=int)
    per_page = 10
    records, pagination = render_as_tuple(page)
    return render_template('index.html', pagination=pagination, records=records)
@app.route('/home', methods=('GET', 'POST'))
def home():
    return render_template('home.html')

login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = Users.query.filter_by(username=username).first()
        if not user:
            flash("Nom d'uilisateur incorrect. Veuillez réessayer à nouveau.")
            return redirect(url_for('login'))
        if not bcrypt.check_password_hash(user.password, password):
            flash('Mot de passe incorrect . Veuillez réessayer à nouveau.')
            return redirect(url_for('login'))
        login_user(user)
        flash('Bienvenue , ' + user.username + '!')
        return redirect(url_for('database'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        user = Users.query.filter_by(username=username).first()

        if user:
            flash('Utilisateur existant.')
            return redirect(url_for('register'))

        # Hash the password before storing it in the database
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = Users(email=email, username=username, password=hashed_password)

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        flash('Enregistrement avec succès.Vous pouvez vous connecter')
        return redirect(url_for('login'))

    return render_template('register.html')  # Replace 'success' with the name of your success route


@app.route('/search', methods=('GET', 'POST'))
@login_required
def search():
    return render_template('search.html')

def fetch_data_sorted_by_column(column_name, order):
    if column_name == 'Nom':
        return CV.query.order_by(order(CV.Nom)).all()
    elif column_name == 'Prenom':
        return CV.query.order_by(order(CV.Prenom)).all()
    elif column_name == 'ColonneNiveau':
        return CV.query.order_by(order(CV.ColonneNiveau)).all()
    elif column_name == 'ColonneExperience':
        return CV.query.order_by(order(CV.ColonneExperience)).all()
    else:
        return CV.query.all()
    
@app.route('/database', methods=['GET', 'POST'])
@login_required
def database():
    form = SearchForm()
    domain_selected_map = {
                        '1': 'ingénieu qualité',
                        '2': 'économie / gestion',
                        '3': 'technicien spécialisé',
                        '4': 'ingénieur',
                        '5': 'ingénieur industriel',
                        '6': 'chargé de développement',
                        '7': 'concepteur/ dessinateur',
                        '8': 'logistique',
                        '9': 'ingénieur mécanique',
                        '10': 'ingénieur process'
                    }
    if request.method == 'POST' and form.validate_on_submit():
        search_term = form.search.data
        domain_selected = request.form.get('domain')
        niveau=request.form.get('niveau')
        niveau=int(niveau)
        logging.info(f"niveau: {niveau}")
        logging.info(f"niveau type: {type(niveau)}")
        experience=request.form.get('experience')
        experience=int(experience)
        logging.info(f"experience: {experience}")
        logging.info(f"experience type: {type(experience)}")
        prediction_status = request.form.get('prediction_status')
        if prediction_status != 'all':
            prediction_status = int(prediction_status)
        logging.info(f"prediction_status: {prediction_status}")
        query=CV.query
        logging.info(f"search_term: {search_term}")
        try:
            if search_term:
                search_term = form.search.data
                if domain_selected == 'all':
                    if experience ==-1 and niveau ==-1:
                        if prediction_status == 'all':
                            query=CV.query.filter(or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%')))
                        elif prediction_status == 1:
                            query = CV.query.filter(and_(CV.Prediction == 1,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 0:
                            query = CV.query.filter(and_(CV.Prediction == 0,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience ==-1 and niveau !=-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneNiveau == niveau,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 1:
                            query = CV.query.filter(and_(CV.Prediction == 1,CV.ColonneNiveau == niveau,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 0:
                            query = CV.query.filter(and_(CV.Prediction == 0,CV.ColonneNiveau == niveau,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience !=-1 and niveau ==-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneExperience == experience,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 1:
                            query = CV.query.filter(and_(CV.Prediction == 1,CV.ColonneExperience == experience,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 0:
                            query = CV.query.filter(and_(CV.Prediction == 0,CV.ColonneExperience == experience,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience !=-1 and niveau !=-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 1:
                            query = CV.query.filter(and_(CV.Prediction == 1,CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 0:
                            query = CV.query.filter(and_(CV.Prediction == 0,CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                else:
                    domain_selected = domain_selected_map.get(domain_selected, '')
                    if experience ==-1 and niveau ==-1:
                        if prediction_status == 'all':
                            query=CV.query.filter(and_(CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 1:
                            query=CV.query.filter(and_(CV.Prediction == 1,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 0:
                            query=CV.query.filter(and_(CV.Prediction == 0,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience ==-1 and niveau !=-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneNiveau == niveau,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 1:
                            query = CV.query.filter(and_(CV.Prediction == 1,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 0:
                            query = CV.query.filter(and_(CV.Prediction == 0,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience !=-1 and niveau ==-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 1:
                            query = CV.query.filter(and_(CV.Prediction == 1,CV.ColonneExperience == experience,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 0:
                            query = CV.query.filter(and_(CV.Prediction == 0,CV.ColonneExperience == experience,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience !=-1 and niveau !=-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 1:
                            query = CV.query.filter(and_(CV.Prediction == 1,CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 0:
                            query = CV.query.filter(and_(CV.Prediction == 0,CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                logging.info(f"query1: {query}")
                data = fetch_filtered_data(query)
                if not data:
                    logging.error(f"data: {data}")
                    logging.error(f"search_term: {search_term}")
                    logging.error(f"domain_selected: {domain_selected}")
                    logging.warning(f"No results found for search term: {search_term}")
                    flash('No results found for your search term.', 'warning')
                    return render_template('Database.html', data=data, search=search_term, domain_selected=domain_selected,niveau=niveau,experience=experience)
                else:
                    return render_template('Database.html', data=data, domain_selected=domain_selected,niveau=niveau,experience=experience)
            elif domain_selected:
                if domain_selected == 'all':
                    if experience ==-1 and niveau ==-1:
                        if prediction_status == 'all':
                            query=CV.query.limit(20).all()
                        elif prediction_status == 1:
                            query=CV.query.filter(CV.Prediction == 1)
                        elif prediction_status == 0:
                            query=CV.query.filter(CV.Prediction == 0)
                    elif experience ==-1 and niveau !=-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(CV.ColonneNiveau == niveau)
                        elif prediction_status == 1:
                            query=CV.query.filter(and_(CV.Prediction == 1,CV.ColonneNiveau == niveau))
                        elif prediction_status == 0:
                            query=CV.query.filter(and_(CV.Prediction == 0,CV.ColonneNiveau == niveau))
                    elif experience !=-1 and niveau ==-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(CV.ColonneExperience == experience)
                        elif prediction_status == 1:
                            query=CV.query.filter(and_(CV.Prediction == 1,CV.ColonneExperience == experience))
                        elif prediction_status == 0:
                            query=CV.query.filter(and_(CV.Prediction == 0,CV.ColonneExperience == experience))
                    elif experience !=-1 and niveau !=-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.ColonneNiveau == niveau))
                        elif prediction_status == 1:
                            query=CV.query.filter(and_(CV.Prediction == 1,CV.ColonneExperience == experience,CV.ColonneNiveau == niveau))
                        elif prediction_status == 0:
                            query=CV.query.filter(and_(CV.Prediction == 0,CV.ColonneExperience == experience,CV.ColonneNiveau == niveau))
                    logging.info(f"query2: {query}")
                    data = fetch_filtered_data(query)
                    return render_template('Database.html', data=data, domain_selected=domain_selected,niveau=niveau,experience=experience)
                else:
                    domain_selected = domain_selected_map.get(domain_selected, '')
                    if experience ==-1 and niveau ==-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(CV.Domaine == domain_selected)
                        elif prediction_status == 1:
                            query=CV.query.filter(and_(CV.Prediction == 1,CV.Domaine == domain_selected))
                        elif prediction_status == 0:
                            query=CV.query.filter(and_(CV.Prediction == 0,CV.Domaine == domain_selected))
                    elif experience ==-1 and niveau !=-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneNiveau == niveau,CV.Domaine == domain_selected))
                        elif prediction_status == 1:
                            query=CV.query.filter(and_(CV.Prediction == 1,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected))
                        elif prediction_status == 0:
                            query=CV.query.filter(and_(CV.Prediction == 0,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected))
                    elif experience !=-1 and niveau ==-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.Domaine == domain_selected))
                        elif prediction_status == 1:
                            query=CV.query.filter(and_(CV.Prediction == 1,CV.ColonneExperience == experience,CV.Domaine == domain_selected))
                        elif prediction_status == 0:
                            query=CV.query.filter(and_(CV.Prediction == 0,CV.ColonneExperience == experience,CV.Domaine == domain_selected))
                    elif experience !=-1 and niveau !=-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected))
                        elif prediction_status == 1:
                            query=CV.query.filter(and_(CV.Prediction == 1,CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected))
                        elif prediction_status == 0:
                            query=CV.query.filter(and_(CV.Prediction == 0,CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected))
                    logging.info(f"query3: {query}")
                    data = fetch_filtered_data(query)
                    return render_template('Database.html', data=data, domain_selected=domain_selected,niveau=niveau,experience=experience)
            elif prediction_status != 'all':
                if prediction_status == 1:
                    query = CV.query.filter(CV.Prediction == 1)
                elif prediction_status == 0:
                    query = CV.query.filter(CV.Prediction == 0)
                else:
                    query=CV.query.limit(20).all()
                logging.info(f"query4: {query}")
                data = fetch_filtered_data(query)
                return render_template('Database.html', data=data, domain_selected=domain_selected,niveau=niveau,experience=experience)
            else:
                data=fetch_all_data()
                logging.info(f"data4: {data}")
                return render_template('Database.html', data=data,niveau=niveau,experience=experience)
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            raise CustomException(e, sys)
    else:
        try:
            page = request.args.get('page', 1, type=int)
            per_page = 10
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            data = pagination.items
            data=fetch_all_data()
            sort_by = request.args.get('sort_by', 'ID')
            sort_order = request.args.get('sort_order', 'asc')
            if sort_by == 'Niveau':
                if sort_order == 'asc':
                    data = fetch_data_sorted_by_column('ColonneNiveau', asc)
                    sort_order = 'desc'
                else:
                    data = fetch_data_sorted_by_column('ColonneNiveau', desc)
                    sort_order = 'asc'
            elif sort_by == 'ColonneExperience':
                if sort_order == 'asc':
                    data = fetch_data_sorted_by_column('ColonneExperience', asc)
                    sort_order = 'desc'
                else:
                    data = fetch_data_sorted_by_column('ColonneExperience', desc)
                    sort_order = 'asc'
            else:
                if sort_order == 'asc':
                    data = fetch_data_sorted_by_column(sort_by, asc)
                else:
                    data = fetch_data_sorted_by_column(sort_by, desc)
            return render_template('Database.html', data=data, sort_by=sort_by, sort_order=sort_order)
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            raise CustomException(e, sys)


@app.route('/predictdata',methods=['GET','POST'])
@login_required
def predict_datapoint():
    if request.method == 'GET':
        return render_template("predict.html")
    else:
        data = CustomData(
            Gender=request.form.get('Gender'),
            Domain=request.form.get('Domain'),
            ColonneExperience=request.form.get('ColonneExperience'),
            ColonneNiveau=request.form.get('ColonneNiveau')
        )
        pred_df=data.get_data_as_data_frame()
        print(pred_df)
        predict_pipeline=PredictPipeline()
        results = predict_pipeline.predict(pred_df)
        return render_template('predict.html',results=results[0])


@app.route('/modal', methods=('GET', 'POST'))
@login_required
def modal():
    domain_selected_map = {
                        '1': 'ingenieur qualite',
                        '2': 'economie / gestion',
                        '3': 'technicien specialise',
                        '4': 'ingenieur',
                        '5': 'ingenieur industriel',
                        '6': 'charge de developpementt',
                        '7': 'concepteur/ dessinateur',
                        '8': 'logistique',
                        '9': 'ingenieur mecanique',
                        '10': 'ingenieur process'
                    }
    niveau_selected_map = {
        'BAC ': '',
        'BAC + 1': '1',
        'BAC + 2': '2',
        'BAC + 3': '3',
        'BAC + 4': '4',
        'BAC + 5': '5',
        'BAC + 6': '6',
        'BAC + 7': '7',
        'BAC + 8': '8',
        'BAC + 9': '9',
        'BAC + 10': '10',
        'BAC + 11': '11',
        'BAC + 12': '12',
        'BAC + 13': '13',
        'BAC + 14': '14',
        'BAC + 15': '15',
        'BAC + 16': '16',
        'BAC + 17': '17',
        'BAC + 18': '18',
        'BAC + 19': '19',
        'BAC + 20': '20',
                    }
    experience_selected_map = {
        '0': "Moins d'un an", 
        '1': '1 an',
        '2': '2 ans',
        '3': '3 ans',
        '4': '4 ans',
        '5': '5 ans',
        '6': '6 ans',
        '7': '7 ans',
        '8': '8 ans',
        '9': '9 ans',
        '10': '10 ans',
        '11': '11 ans',
        '12': '12 ans',
        '13': '13 ans',
        '14': '14 ans',
        '15': '15 ans',
        '16': '16 ans',
        '17': '17 ans',
        '18': '18 ans',
        '19': '19 ans',
        '20': '20 ans',
        '21': '21 ans',
        '22': '22 ans',
        '23': '23 ans',
        '24': '24 ans',
        '25': '25 ans',
        '26': '26 ans',
        '27': '27 ans',
        '28': '28 ans',
        '29': '29 ans',
        '30': '30 ans'
    }
    add_cv_form = AddCVForm()
    last_id = last_CV_ID()
    if request.method == 'POST' : 
        ID = add_cv_form.ID.data
        Nom = add_cv_form.Nom.data
        Prenom = add_cv_form.Prenom.data
        Gender = add_cv_form.Gender.data
        Fonction = add_cv_form.Fonction.data
        Domaine = add_cv_form.Domaine.data
        Domaine = domain_selected_map.get(Domaine, '')
        Niveau_label = add_cv_form.Niveau.data
        Niveau_selected = int(niveau_selected_map.get(Niveau_label, ''))
        ColonneExperience = add_cv_form.ColonneExperience.data
        Annee_experience_en_conception = experience_selected_map.get(ColonneExperience, '')
        ColonneExperience = int(ColonneExperience)
        Localisation = add_cv_form.Localisation.data
        Source = add_cv_form.Source.data
        Url = add_cv_form.Url.data
        new = CV(ID=ID, Nom=Nom, Prenom=Prenom, Gender=Gender, Fonction=Fonction, Domaine=Domaine,
                    Niveau=Niveau_label,ColonneNiveau=Niveau_selected, Annee_experience_en_conception=Annee_experience_en_conception,
                      ColonneExperience=ColonneExperience, Localisation=Localisation, Source=Source, Url=Url)
        db.session.add(new)
        db.session.commit()
        flash('CV added successfully', 'success')
        logging.info(f'CV added successfully : {new}')
        return render_template('modal.html',add_cv_form=add_cv_form,last_id=last_id, ID=ID, Nom=Nom, Prenom=Prenom, 
                               Gender=Gender, Fonction=Fonction, Domaine=Domaine, Niveau=Niveau_label,
                                 Annee_experience_en_conception=Annee_experience_en_conception, Localisation=Localisation,
                                   Source=Source, Url=Url)
    return render_template('modal.html',last_id=last_id,add_cv_form=add_cv_form)


@app.route('/candidature', methods=('GET', 'POST'))
def candidature():
    domain_selected_map = {
                        '1': 'ingenieur qualite',
                        '2': 'economie / gestion',
                        '3': 'technicien specialise',
                        '4': 'ingenieur',
                        '5': 'ingenieur industriel',
                        '6': 'charge de developpementt',
                        '7': 'concepteur/ dessinateur',
                        '8': 'logistique',
                        '9': 'ingenieur mecanique',
                        '10': 'ingenieur process'
                    }
    niveau_selected_map = {
        'BAC ': '',
        'BAC + 1': '1',
        'BAC + 2': '2',
        'BAC + 3': '3',
        'BAC + 4': '4',
        'BAC + 5': '5',
        'BAC + 6': '6',
        'BAC + 7': '7',
        'BAC + 8': '8',
        'BAC + 9': '9',
        'BAC + 10': '10',
        'BAC + 11': '11',
        'BAC + 12': '12',
        'BAC + 13': '13',
        'BAC + 14': '14',
        'BAC + 15': '15',
        'BAC + 16': '16',
        'BAC + 17': '17',
        'BAC + 18': '18',
        'BAC + 19': '19',
        'BAC + 20': '20',
                    }
    experience_selected_map = {
        '0': "Moins d'un an", 
        '1': '1 an',
        '2': '2 ans',
        '3': '3 ans',
        '4': '4 ans',
        '5': '5 ans',
        '6': '6 ans',
        '7': '7 ans',
        '8': '8 ans',
        '9': '9 ans',
        '10': '10 ans',
        '11': '11 ans',
        '12': '12 ans',
        '13': '13 ans',
        '14': '14 ans',
        '15': '15 ans',
        '16': '16 ans',
        '17': '17 ans',
        '18': '18 ans',
        '19': '19 ans',
        '20': '20 ans',
        '21': '21 ans',
        '22': '22 ans',
        '23': '23 ans',
        '24': '24 ans',
        '25': '25 ans',
        '26': '26 ans',
        '27': '27 ans',
        '28': '28 ans',
        '29': '29 ans',
        '30': '30 ans'
    }
    add_cv_form = AddCVForm()
    last_id = last_CV_ID()
    if request.method == 'POST' : 
        add_cv_form = AddCVForm(request.form)
        ID = add_cv_form.ID.data
        Nom = add_cv_form.Nom.data
        Prenom = add_cv_form.Prenom.data
        Gender = add_cv_form.Gender.data
        Fonction = add_cv_form.Fonction.data
        Domaine = add_cv_form.Domaine.data
        Domaine = domain_selected_map.get(Domaine, '')
        Niveau_label = add_cv_form.Niveau.data
        Niveau_selected = int(niveau_selected_map.get(Niveau_label, ''))
        ColonneExperience = add_cv_form.ColonneExperience.data
        Annee_experience_en_conception = experience_selected_map.get(ColonneExperience, '')
        ColonneExperience = int(ColonneExperience)
        Localisation = add_cv_form.Localisation.data
        Source = add_cv_form.Source.data
        Url = add_cv_form.Url.data
        new = CV(ID=ID, Nom=Nom, Prenom=Prenom, Gender=Gender, Fonction=Fonction, Domaine=Domaine,
                    Niveau=Niveau_label,ColonneNiveau=Niveau_selected, Annee_experience_en_conception=Annee_experience_en_conception,
                      ColonneExperience=ColonneExperience, Localisation=Localisation, Source=Source, Url=Url)
        db.session.add(new)
        db.session.commit()
        flash('CV added successfully', 'success')
        logging.info(f'CV added successfully : {new}')
        return render_template('candidature.html',add_cv_form=add_cv_form,last_id=last_id, ID=ID, Nom=Nom, Prenom=Prenom, 
                               Gender=Gender, Fonction=Fonction, Domaine=Domaine, Niveau=Niveau_label,
                                 Annee_experience_en_conception=Annee_experience_en_conception, Localisation=Localisation,
                                   Source=Source, Url=Url)
    return render_template('candidature.html',add_cv_form=add_cv_form,last_id=last_id)


@app.route('/modifiercv/<int:id>', methods=('GET', 'POST'))
@login_required
def modifiercv(id):
    cv = CV.query.get_or_404(id)
    mod_cv_form=ModifyCVForm()
    domain_selected_map = {
                        '1': 'ingenieur qualite',
                        '2': 'economie / gestion',
                        '3': 'technicien specialise',
                        '4': 'ingenieur',
                        '5': 'ingenieur industriel',
                        '6': 'charge de developpementt',
                        '7': 'concepteur/ dessinateur',
                        '8': 'logistique',
                        '9': 'ingenieur mecanique',
                        '10': 'ingenieur process'
                    }
    niveau_selected_map = {
        'BAC ': '',
        'BAC + 1': '1',
        'BAC + 2': '2',
        'BAC + 3': '3',
        'BAC + 4': '4',
        'BAC + 5': '5',
        'BAC + 6': '6',
        'BAC + 7': '7',
        'BAC + 8': '8',
        'BAC + 9': '9',
        'BAC + 10': '10',
        'BAC + 11': '11',
        'BAC + 12': '12',
        'BAC + 13': '13',
        'BAC + 14': '14',
        'BAC + 15': '15',
        'BAC + 16': '16',
        'BAC + 17': '17',
        'BAC + 18': '18',
        'BAC + 19': '19',
        'BAC + 20': '20',
                    }
    experience_selected_map = {
         "Moins d'un an":'0', 
         '1 an':'1',
         '2 ans':'2',
         '3 ans':'3',
         '4 ans':'4',
         '5 ans':'5',
         '6 ans':'6',
         '7 ans':'7',
         '8 ans':'8',
         '9 ans':'9',
         '10 ans':'10',
         '11 ans':'11',
         '12 ans':'12',
        '13 ans':'13',
         '14 ans':'14',
         '15 ans':'15',
         '16 ans':'16',
         '17 ans':'17',
         '18 ans':'18',
        '19 ans':'19',
         '20 ans':'20',
         '21 ans':'21',
         '22 ans':'22',
         '23 ans':'23',
         '24 ans':'24',
         '25 ans':'25',
         '26 ans':'26',
         '27 ans':'27',
         '28 ans':'28',
         '29 ans':'29',
         '30 ans':'30'
    }
    
    if request.method == 'POST' :
        ID = mod_cv_form.ID.data
        Nom = mod_cv_form.Nom.data
        Prenom = mod_cv_form.Prenom.data
        Gender = mod_cv_form.Gender.data
        Fonction = mod_cv_form.Fonction.data
        Domaine = mod_cv_form.Domaine.data.replace("é", "e")
        Niveau = mod_cv_form.Niveau.data
        ColonneNiveau = int(niveau_selected_map.get(Niveau, ''))
        Annee_experience_en_conception = mod_cv_form.ColonneExperience.data
        ColonneExperience= experience_selected_map.get(Annee_experience_en_conception, '')
        Localisation = mod_cv_form.Localisation.data
        Source = mod_cv_form.Source.data
        Url = mod_cv_form.Url.data

        cv.Nom=Nom
        cv.Prenom=Prenom
        cv.Gender=Gender
        cv.Fonction=Fonction
        cv.Domaine=Domaine
        cv.Niveau=Niveau
        cv.ColonneNiveau=ColonneNiveau
        cv.Annee_experience_en_conception=Annee_experience_en_conception
        cv.ColonneExperience=ColonneExperience
        cv.Localisation=Localisation
        cv.Source=Source
        cv.Url=Url

        db.session.commit()

        logging.info(f"cv:{cv.Nom , cv.Prenom , cv.Gender , cv.Fonction,cv.Domaine,cv.Niveau,cv.ColonneNiveau,cv.Annee_experience_en_conception,cv.ColonneExperience,cv.Localisation,cv.Source,cv.Url}")
        logging.info(f"les informations ont ete modifiees avec succes. ")
        return render_template("Database.html")
    return render_template('modifiercv.html',id=id ,cv=cv,mod_cv_form=mod_cv_form)


@app.route('/supprimercv/<int:id>', methods=('GET', 'POST'))
@login_required
def supprimercv(id):
    cv = CV.query.get_or_404(id)
    db.session.delete(cv)
    db.session.commit()
    return render_template('supprimercv.html',id=id)


if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)


# =================================== Build app 11 (07/04/2024 02:03)===============================

# import pickle
import sys

from forms import LoginForm, ModifyCVForm, SearchForm, TestForm,AddCVForm
from src.exception import CustomException
from src.logger import logging
from flask import Flask,request,render_template, flash ,redirect, url_for
import numpy as np
import pandas as pd
from sklearn.preprocessing	import  MinMaxScaler
from src.pipeline.predict_pipeline import CustomData , PredictPipeline
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField , SubmitField
from wtforms.validators import DataRequired
from datetime import datetime
from models import Users, db, CV, last_CV_ID, render_as_tuple, render_as_tuple_custom
from sqlalchemy import or_ , and_,asc, desc
from flask_login import login_user,LoginManager,login_required,logout_user,current_user
# from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt 
# from flask_bcrypt import check_password_hash
import bcrypt


application = Flask(__name__)
app = application

app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_cv1'
mysql = MySQL(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/db_cv1'  
db.init_app(app)

bcrypt = Bcrypt(app) 


def fetch_filtered_data(query):
    fetchdata = render_as_tuple_custom(query)
    # logging.info(f"fetchdata : {fetchdata}")
    logging.info(f"fetchdata type: {type(fetchdata)}")
    data = []
    for row in fetchdata:
        data_row = {
            'ID': row[0],
            'Nom': row[1],
            'Prenom': row[2],
            'Domain': row[3],
            'Gender': row[4],
            'Fonction': row[5],
            'Niveau': row[6],
            'ColonneNiveau': row[7],
            'Annee_experience_en_conception': row[8],
            'Prediction': row[9],
            'ColonneExperience': row[10],
            'Localisation': row[11],
            'Source': row[12],
            'Url': row[13]
        }
        data_row['Domain'] = data_row['Domain'].replace('ingénieur', 'Ingénieur').replace('ingénieu qualité', 'Ingénieur Qualité').replace('économie / gestion', 'Economie et Gestion').replace('technicien spécialisé', 'Technicien Spécialisé').replace('ingénieur process', 'Ingénieur Process').replace('ingénieur industriel', 'Ingénieur Industriel').replace('Ingénieur industriel', 'Ingénieur Industriel').replace('chargé de développement', 'Chargé de Développement').replace('concepteur/ dessinateur', 'Concepteur ou Dessinateur').replace('logistique', 'Logistique').replace('ingénieur mécanique', 'Ingénieur Mécanique')
        data.append(data_row)

    return data

def fetch_all_data():
    fetchdata = render_as_tuple()
    data = []
    for row in fetchdata:
        data_row = {
            'ID': row[0],
            'Nom': row[1],
            'Prenom': row[2],
            'Domain': row[3],
            'Gender': row[4],
            'Fonction': row[5],
            'Niveau': row[6],
            'ColonneNiveau': row[7],
            'Annee_experience_en_conception': row[8],
            'Prediction': row[9],  # We'll update this later
            'ColonneExperience': row[10],
            'Localisation': row[11],
            'Source': row[12],
            'Url': row[13]
        }
        pred_df = pd.DataFrame([data_row], columns=['ColonneNiveau', 'ColonneExperience', 'Gender', 'Domain'])
        pred_df['Domain'] = pred_df['Domain'].replace({'Ingénieur Industriel': 'ingénieur industriel', 'ingénieu qualité': 'ingenieur qualité'})
        pred_df['Domain'] = pred_df['Domain'].str.replace('é', 'e')
        predict_pipeline = PredictPipeline()
        prediction = predict_pipeline.predict(pred_df)[0]
        data_row['Prediction'] = prediction  # Update the Prediction field in data_row
        # Update the Prediction in the database using SQLAlchemy
        cv_instance = CV.query.filter_by(ID=row[0]).first()
        if cv_instance:
            cv_instance.Prediction = prediction
            db.session.commit()  # Commit the changes to the database
        else:
            # Handle the case where the CV instance with the given ID is not found
            pass
        data_row['Domain'] = data_row['Domain'].replace('ingénieur', 'Ingénieur')\
            .replace('ingénieu qualité', 'Ingénieur Qualité')\
            .replace('ingenieur qualite', 'Ingénieur Qualité')\
            .replace('économie / gestion', 'Economie et Gestion')\
            .replace('technicien spécialisé', 'Technicien Spécialisé')\
            .replace('ingénieur process', 'Ingénieur Process')\
            .replace('ingénieur industriel', 'Ingénieur Industriel')\
            .replace('Ingénieur industriel', 'Ingénieur Industriel')\
            .replace('chargé de développement', 'Chargé de Développement')\
            .replace('concepteur/ dessinateur', 'Concepteur ou Dessinateur')\
            .replace('logistique', 'Logistique')\
            .replace('ingénieur mécanique', 'Ingénieur Mécanique')\
            .replace('ingenieur qualite', 'Ingénieur Qualité')\
            .replace('economie / gestion', 'Economie et Gestion')\
            .replace('technicien specialise', 'Technicien Spécialisé')\
            .replace('ingenieur process', 'Ingénieur Process')\
            .replace('ingenieur industriel', 'Ingénieur Industriel')\
            .replace('charge de developpement', 'Chargé de Développement')\
            .replace('concepteur/ dessinateur', 'Concepteur ou Dessinateur')\
            .replace('ingenieur', 'Ingénieur')
        data.append(data_row)
    return data

@app.context_processor
def base():
    form=SearchForm()
    return dict(form=form)

def get_records():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    return CV.query.order_by(asc(CV.ID)).paginate(page=page, per_page=per_page, error_out=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home', methods=('GET', 'POST'))
def home():
    return render_template('home.html')

@app.route('/testdb')
def testdb():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = CV.query.order_by(asc(CV.ID)).paginate(page=page, per_page=per_page, error_out=False)
    records = pagination.items  
    return render_template('testdb.html', pagination=pagination, records=records)

login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = Users.query.filter_by(username=username).first()
        if not user:
            flash("Nom d'uilisateur incorrect. Veuillez réessayer à nouveau.")
            return redirect(url_for('login'))
        if not bcrypt.check_password_hash(user.password, password):
            flash('Mot de passe incorrect . Veuillez réessayer à nouveau.')
            return redirect(url_for('login'))
        login_user(user)
        flash('Bienvenue , ' + user.username + '!')
        return redirect(url_for('database'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        user = Users.query.filter_by(username=username).first()

        if user:
            flash('Utilisateur existant.')
            return redirect(url_for('register'))

        # Hash the password before storing it in the database
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = Users(email=email, username=username, password=hashed_password)

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        flash('Enregistrement avec succès.Vous pouvez vous connecter')
        return redirect(url_for('login'))

    return render_template('register.html')  # Replace 'success' with the name of your success route


@app.route('/search', methods=('GET', 'POST'))
@login_required
def search():
    return render_template('search.html')

def fetch_data_sorted_by_column(column_name, order,page, per_page):
    if column_name == 'Nom':
        return CV.query.order_by(order(CV.Nom)).paginate(page=page, per_page=per_page, error_out=False)
    elif column_name == 'ColonneNiveau':
        return CV.query.order_by(order(CV.ColonneNiveau)).paginate(page=page, per_page=per_page, error_out=False)
    elif column_name == 'ColonneExperience':
        return CV.query.order_by(order(CV.ColonneExperience)).paginate(page=page, per_page=per_page, error_out=False)
    else:
        return CV.query.order_by(order(CV.ID)).paginate(page=page, per_page=per_page, error_out=False)
    
@app.route('/database', methods=['GET', 'POST'])
@login_required
def database():
    form = SearchForm()
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = CV.query.paginate(page=page, per_page=per_page, error_out=False)
    domain_selected_map = {
                        '1': 'ingénieu qualité',
                        '2': 'économie / gestion',
                        '3': 'technicien spécialisé',
                        '4': 'ingénieur',
                        '5': 'ingénieur industriel',
                        '6': 'chargé de développement',
                        '7': 'concepteur/ dessinateur',
                        '8': 'logistique',
                        '9': 'ingénieur mécanique',
                        '10': 'ingénieur process'
                    }
    if request.method == 'POST' and form.validate_on_submit():
        search_term = form.search.data
        domain_selected = request.form.get('domain')
        niveau=request.form.get('niveau')
        niveau=int(niveau)
        logging.info(f"niveau: {niveau}")
        logging.info(f"niveau type: {type(niveau)}")
        experience=request.form.get('experience')
        experience=int(experience)
        logging.info(f"experience: {experience}")
        logging.info(f"experience type: {type(experience)}")
        prediction_status = request.form.get('prediction_status')
        if prediction_status != 'all':
            prediction_status = int(prediction_status)
        logging.info(f"prediction_status: {prediction_status}")
        query=CV.query
        logging.info(f"search_term: {search_term}")
        try:
            if search_term:
                search_term = form.search.data
                if domain_selected == 'all':
                    if experience ==-1 and niveau ==-1:
                        if prediction_status == 'all':
                            query=CV.query.filter(or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%')))
                        elif prediction_status == 1:
                            query = CV.query.filter(and_(CV.Prediction == 1,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 0:
                            query = CV.query.filter(and_(CV.Prediction == 0,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience ==-1 and niveau !=-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneNiveau == niveau,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 1:
                            query = CV.query.filter(and_(CV.Prediction == 1,CV.ColonneNiveau == niveau,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 0:
                            query = CV.query.filter(and_(CV.Prediction == 0,CV.ColonneNiveau == niveau,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience !=-1 and niveau ==-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneExperience == experience,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 1:
                            query = CV.query.filter(and_(CV.Prediction == 1,CV.ColonneExperience == experience,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 0:
                            query = CV.query.filter(and_(CV.Prediction == 0,CV.ColonneExperience == experience,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience !=-1 and niveau !=-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 1:
                            query = CV.query.filter(and_(CV.Prediction == 1,CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 0:
                            query = CV.query.filter(and_(CV.Prediction == 0,CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                else:
                    domain_selected = domain_selected_map.get(domain_selected, '')
                    if experience ==-1 and niveau ==-1:
                        if prediction_status == 'all':
                            query=CV.query.filter(and_(CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 1:
                            query=CV.query.filter(and_(CV.Prediction == 1,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 0:
                            query=CV.query.filter(and_(CV.Prediction == 0,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience ==-1 and niveau !=-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneNiveau == niveau,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 1:
                            query = CV.query.filter(and_(CV.Prediction == 1,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 0:
                            query = CV.query.filter(and_(CV.Prediction == 0,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience !=-1 and niveau ==-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 1:
                            query = CV.query.filter(and_(CV.Prediction == 1,CV.ColonneExperience == experience,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 0:
                            query = CV.query.filter(and_(CV.Prediction == 0,CV.ColonneExperience == experience,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience !=-1 and niveau !=-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 1:
                            query = CV.query.filter(and_(CV.Prediction == 1,CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 0:
                            query = CV.query.filter(and_(CV.Prediction == 0,CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                logging.info(f"query1: {query}")
                data = fetch_filtered_data(query)
                if not data:
                    logging.error(f"data: {data}")
                    logging.error(f"search_term: {search_term}")
                    logging.error(f"domain_selected: {domain_selected}")
                    logging.warning(f"No results found for search term: {search_term}")
                    flash('No results found for your search term.', 'warning')
                    return render_template('Database.html', data=data, search=search_term, domain_selected=domain_selected,niveau=niveau,experience=experience,pagination=pagination)
                else:
                    return render_template('Database.html', data=data, domain_selected=domain_selected,niveau=niveau,experience=experience,pagination=pagination)
            elif domain_selected:
                if domain_selected == 'all':
                    if experience ==-1 and niveau ==-1:
                        if prediction_status == 'all':
                            query=CV.query.limit(20).all()
                        elif prediction_status == 1:
                            query=CV.query.filter(CV.Prediction == 1)
                        elif prediction_status == 0:
                            query=CV.query.filter(CV.Prediction == 0)
                    elif experience ==-1 and niveau !=-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(CV.ColonneNiveau == niveau)
                        elif prediction_status == 1:
                            query=CV.query.filter(and_(CV.Prediction == 1,CV.ColonneNiveau == niveau))
                        elif prediction_status == 0:
                            query=CV.query.filter(and_(CV.Prediction == 0,CV.ColonneNiveau == niveau))
                    elif experience !=-1 and niveau ==-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(CV.ColonneExperience == experience)
                        elif prediction_status == 1:
                            query=CV.query.filter(and_(CV.Prediction == 1,CV.ColonneExperience == experience))
                        elif prediction_status == 0:
                            query=CV.query.filter(and_(CV.Prediction == 0,CV.ColonneExperience == experience))
                    elif experience !=-1 and niveau !=-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.ColonneNiveau == niveau))
                        elif prediction_status == 1:
                            query=CV.query.filter(and_(CV.Prediction == 1,CV.ColonneExperience == experience,CV.ColonneNiveau == niveau))
                        elif prediction_status == 0:
                            query=CV.query.filter(and_(CV.Prediction == 0,CV.ColonneExperience == experience,CV.ColonneNiveau == niveau))
                    logging.info(f"query2: {query}")
                    data = fetch_filtered_data(query)
                    return render_template('Database.html', data=data, domain_selected=domain_selected,niveau=niveau,experience=experience,pagination=pagination)
                else:
                    domain_selected = domain_selected_map.get(domain_selected, '')
                    if experience ==-1 and niveau ==-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(CV.Domaine == domain_selected)
                        elif prediction_status == 1:
                            query=CV.query.filter(and_(CV.Prediction == 1,CV.Domaine == domain_selected))
                        elif prediction_status == 0:
                            query=CV.query.filter(and_(CV.Prediction == 0,CV.Domaine == domain_selected))
                    elif experience ==-1 and niveau !=-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneNiveau == niveau,CV.Domaine == domain_selected))
                        elif prediction_status == 1:
                            query=CV.query.filter(and_(CV.Prediction == 1,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected))
                        elif prediction_status == 0:
                            query=CV.query.filter(and_(CV.Prediction == 0,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected))
                    elif experience !=-1 and niveau ==-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.Domaine == domain_selected))
                        elif prediction_status == 1:
                            query=CV.query.filter(and_(CV.Prediction == 1,CV.ColonneExperience == experience,CV.Domaine == domain_selected))
                        elif prediction_status == 0:
                            query=CV.query.filter(and_(CV.Prediction == 0,CV.ColonneExperience == experience,CV.Domaine == domain_selected))
                    elif experience !=-1 and niveau !=-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected))
                        elif prediction_status == 1:
                            query=CV.query.filter(and_(CV.Prediction == 1,CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected))
                        elif prediction_status == 0:
                            query=CV.query.filter(and_(CV.Prediction == 0,CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected))
                    logging.info(f"query3: {query}")
                    data = fetch_filtered_data(query)
                    return render_template('Database.html', data=data, domain_selected=domain_selected,niveau=niveau,experience=experience,pagination=pagination)
            elif prediction_status != 'all':
                if prediction_status == 1:
                    query = CV.query.filter(CV.Prediction == 1)
                elif prediction_status == 0:
                    query = CV.query.filter(CV.Prediction == 0)
                else:
                    query=CV.query.limit(20).all()
                logging.info(f"query4: {query}")
                data = fetch_filtered_data(query)
                return render_template('Database.html', data=data, domain_selected=domain_selected,niveau=niveau,experience=experience,pagination=pagination)
            else:
                data=fetch_all_data()
                logging.info(f"data4: {data}")
                return render_template('Database.html', data=data,niveau=niveau,experience=experience,pagination=pagination)
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            raise CustomException(e, sys)
    else:
        try:
            page = request.args.get('page', 1, type=int)
            per_page = 10
            pagination = CV.query.paginate(page=page, per_page=per_page, error_out=False)
            data = pagination.items
            # data=fetch_all_data()
            sort_by = request.args.get('sort_by', 'ID')
            sort_order = request.args.get('sort_order', 'desc')
            if sort_by == 'Nom':
                if sort_order == 'asc':
                    data = fetch_data_sorted_by_column('Nom', asc,page=page, per_page=per_page)
                    sort_order = 'desc'
                else:
                    data = fetch_data_sorted_by_column('Nom', desc,page=page, per_page=per_page)
                    sort_order = 'asc'
            elif sort_by == 'Niveau':
                if sort_order == 'asc':
                    data = fetch_data_sorted_by_column('ColonneNiveau', asc,page=page, per_page=per_page)
                    sort_order = 'desc'
                else:
                    data = fetch_data_sorted_by_column('ColonneNiveau', desc,page=page, per_page=per_page)
                    sort_order = 'asc'
            elif sort_by == 'ColonneExperience':
                if sort_order == 'asc':
                    data = fetch_data_sorted_by_column('ColonneExperience', asc,page=page, per_page=per_page)
                    sort_order = 'desc'
                else:
                    data = fetch_data_sorted_by_column('ColonneExperience', desc,page=page, per_page=per_page)
                    sort_order = 'asc'
            else:
                if sort_order == 'asc':
                    data = fetch_data_sorted_by_column(sort_by, asc,page=page, per_page=per_page)
                else:
                    data = fetch_data_sorted_by_column(sort_by, desc,page=page, per_page=per_page)
            return render_template('Database.html', data=data,pagination=pagination, sort_by=sort_by, sort_order=sort_order)
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            raise CustomException(e, sys)


@app.route('/predictdata',methods=['GET','POST'])
@login_required
def predict_datapoint():
    if request.method == 'GET':
        return render_template("predict.html")
    else:
        data = CustomData(
            Gender=request.form.get('Gender'),
            Domain=request.form.get('Domain'),
            ColonneExperience=request.form.get('ColonneExperience'),
            ColonneNiveau=request.form.get('ColonneNiveau')
        )
        pred_df=data.get_data_as_data_frame()
        print(pred_df)
        predict_pipeline=PredictPipeline()
        results = predict_pipeline.predict(pred_df)
        return render_template('predict.html',results=results[0])


@app.route('/modal', methods=('GET', 'POST'))
@login_required
def modal():
    domain_selected_map = {
                        '1': 'ingenieur qualite',
                        '2': 'economie / gestion',
                        '3': 'technicien specialise',
                        '4': 'ingenieur',
                        '5': 'ingenieur industriel',
                        '6': 'charge de developpementt',
                        '7': 'concepteur/ dessinateur',
                        '8': 'logistique',
                        '9': 'ingenieur mecanique',
                        '10': 'ingenieur process'
                    }
    niveau_selected_map = {
        'BAC ': '',
        'BAC + 1': '1',
        'BAC + 2': '2',
        'BAC + 3': '3',
        'BAC + 4': '4',
        'BAC + 5': '5',
        'BAC + 6': '6',
        'BAC + 7': '7',
        'BAC + 8': '8',
        'BAC + 9': '9',
        'BAC + 10': '10',
        'BAC + 11': '11',
        'BAC + 12': '12',
        'BAC + 13': '13',
        'BAC + 14': '14',
        'BAC + 15': '15',
        'BAC + 16': '16',
        'BAC + 17': '17',
        'BAC + 18': '18',
        'BAC + 19': '19',
        'BAC + 20': '20',
                    }
    experience_selected_map = {
        '0': "Moins d'un an", 
        '1': '1 an',
        '2': '2 ans',
        '3': '3 ans',
        '4': '4 ans',
        '5': '5 ans',
        '6': '6 ans',
        '7': '7 ans',
        '8': '8 ans',
        '9': '9 ans',
        '10': '10 ans',
        '11': '11 ans',
        '12': '12 ans',
        '13': '13 ans',
        '14': '14 ans',
        '15': '15 ans',
        '16': '16 ans',
        '17': '17 ans',
        '18': '18 ans',
        '19': '19 ans',
        '20': '20 ans',
        '21': '21 ans',
        '22': '22 ans',
        '23': '23 ans',
        '24': '24 ans',
        '25': '25 ans',
        '26': '26 ans',
        '27': '27 ans',
        '28': '28 ans',
        '29': '29 ans',
        '30': '30 ans'
    }
    add_cv_form = AddCVForm()
    last_id = last_CV_ID()
    if request.method == 'POST' : 
        ID = add_cv_form.ID.data
        Nom = add_cv_form.Nom.data
        Prenom = add_cv_form.Prenom.data
        Gender = add_cv_form.Gender.data
        Fonction = add_cv_form.Fonction.data
        Domaine = add_cv_form.Domaine.data
        Domaine = domain_selected_map.get(Domaine, '')
        Niveau_label = add_cv_form.Niveau.data
        Niveau_selected = int(niveau_selected_map.get(Niveau_label, ''))
        ColonneExperience = add_cv_form.ColonneExperience.data
        Annee_experience_en_conception = experience_selected_map.get(ColonneExperience, '')
        ColonneExperience = int(ColonneExperience)
        Localisation = add_cv_form.Localisation.data
        Source = add_cv_form.Source.data
        Url = add_cv_form.Url.data
        new = CV(ID=ID, Nom=Nom, Prenom=Prenom, Gender=Gender, Fonction=Fonction, Domaine=Domaine,
                    Niveau=Niveau_label,ColonneNiveau=Niveau_selected, Annee_experience_en_conception=Annee_experience_en_conception,
                      ColonneExperience=ColonneExperience, Localisation=Localisation, Source=Source, Url=Url)
        db.session.add(new)
        db.session.commit()
        flash('CV added successfully', 'success')
        logging.info(f'CV added successfully : {new}')
        return render_template('modal.html',add_cv_form=add_cv_form,last_id=last_id, ID=ID, Nom=Nom, Prenom=Prenom, 
                               Gender=Gender, Fonction=Fonction, Domaine=Domaine, Niveau=Niveau_label,
                                 Annee_experience_en_conception=Annee_experience_en_conception, Localisation=Localisation,
                                   Source=Source, Url=Url)
    return render_template('modal.html',last_id=last_id,add_cv_form=add_cv_form)


@app.route('/candidature', methods=('GET', 'POST'))
def candidature():
    domain_selected_map = {
                        '1': 'ingenieur qualite',
                        '2': 'economie / gestion',
                        '3': 'technicien specialise',
                        '4': 'ingenieur',
                        '5': 'ingenieur industriel',
                        '6': 'charge de developpementt',
                        '7': 'concepteur/ dessinateur',
                        '8': 'logistique',
                        '9': 'ingenieur mecanique',
                        '10': 'ingenieur process'
                    }
    niveau_selected_map = {
        'BAC ': '',
        'BAC + 1': '1',
        'BAC + 2': '2',
        'BAC + 3': '3',
        'BAC + 4': '4',
        'BAC + 5': '5',
        'BAC + 6': '6',
        'BAC + 7': '7',
        'BAC + 8': '8',
        'BAC + 9': '9',
        'BAC + 10': '10',
        'BAC + 11': '11',
        'BAC + 12': '12',
        'BAC + 13': '13',
        'BAC + 14': '14',
        'BAC + 15': '15',
        'BAC + 16': '16',
        'BAC + 17': '17',
        'BAC + 18': '18',
        'BAC + 19': '19',
        'BAC + 20': '20',
                    }
    experience_selected_map = {
        '0': "Moins d'un an", 
        '1': '1 an',
        '2': '2 ans',
        '3': '3 ans',
        '4': '4 ans',
        '5': '5 ans',
        '6': '6 ans',
        '7': '7 ans',
        '8': '8 ans',
        '9': '9 ans',
        '10': '10 ans',
        '11': '11 ans',
        '12': '12 ans',
        '13': '13 ans',
        '14': '14 ans',
        '15': '15 ans',
        '16': '16 ans',
        '17': '17 ans',
        '18': '18 ans',
        '19': '19 ans',
        '20': '20 ans',
        '21': '21 ans',
        '22': '22 ans',
        '23': '23 ans',
        '24': '24 ans',
        '25': '25 ans',
        '26': '26 ans',
        '27': '27 ans',
        '28': '28 ans',
        '29': '29 ans',
        '30': '30 ans'
    }
    add_cv_form = AddCVForm()
    last_id = last_CV_ID()
    if request.method == 'POST' : 
        add_cv_form = AddCVForm(request.form)
        ID = add_cv_form.ID.data
        Nom = add_cv_form.Nom.data
        Prenom = add_cv_form.Prenom.data
        Gender = add_cv_form.Gender.data
        Fonction = add_cv_form.Fonction.data
        Domaine = add_cv_form.Domaine.data
        Domaine = domain_selected_map.get(Domaine, '')
        Niveau_label = add_cv_form.Niveau.data
        Niveau_selected = int(niveau_selected_map.get(Niveau_label, ''))
        ColonneExperience = add_cv_form.ColonneExperience.data
        Annee_experience_en_conception = experience_selected_map.get(ColonneExperience, '')
        ColonneExperience = int(ColonneExperience)
        Localisation = add_cv_form.Localisation.data
        Source = add_cv_form.Source.data
        Url = add_cv_form.Url.data
        new = CV(ID=ID, Nom=Nom, Prenom=Prenom, Gender=Gender, Fonction=Fonction, Domaine=Domaine,
                    Niveau=Niveau_label,ColonneNiveau=Niveau_selected, Annee_experience_en_conception=Annee_experience_en_conception,
                      ColonneExperience=ColonneExperience, Localisation=Localisation, Source=Source, Url=Url)
        db.session.add(new)
        db.session.commit()
        flash('CV added successfully', 'success')
        logging.info(f'CV added successfully : {new}')
        return render_template('candidature.html',add_cv_form=add_cv_form,last_id=last_id, ID=ID, Nom=Nom, Prenom=Prenom, 
                               Gender=Gender, Fonction=Fonction, Domaine=Domaine, Niveau=Niveau_label,
                                 Annee_experience_en_conception=Annee_experience_en_conception, Localisation=Localisation,
                                   Source=Source, Url=Url)
    return render_template('candidature.html',add_cv_form=add_cv_form,last_id=last_id)


@app.route('/modifiercv/<int:id>', methods=('GET', 'POST'))
@login_required
def modifiercv(id):
    cv = CV.query.get_or_404(id)
    mod_cv_form=ModifyCVForm()
    domain_selected_map = {
                        '1': 'ingenieur qualite',
                        '2': 'economie / gestion',
                        '3': 'technicien specialise',
                        '4': 'ingenieur',
                        '5': 'ingenieur industriel',
                        '6': 'charge de developpementt',
                        '7': 'concepteur/ dessinateur',
                        '8': 'logistique',
                        '9': 'ingenieur mecanique',
                        '10': 'ingenieur process'
                    }
    niveau_selected_map = {
        'BAC ': '',
        'BAC + 1': '1',
        'BAC + 2': '2',
        'BAC + 3': '3',
        'BAC + 4': '4',
        'BAC + 5': '5',
        'BAC + 6': '6',
        'BAC + 7': '7',
        'BAC + 8': '8',
        'BAC + 9': '9',
        'BAC + 10': '10',
        'BAC + 11': '11',
        'BAC + 12': '12',
        'BAC + 13': '13',
        'BAC + 14': '14',
        'BAC + 15': '15',
        'BAC + 16': '16',
        'BAC + 17': '17',
        'BAC + 18': '18',
        'BAC + 19': '19',
        'BAC + 20': '20',
                    }
    experience_selected_map = {
         "Moins d'un an":'0', 
         '1 an':'1',
         '2 ans':'2',
         '3 ans':'3',
         '4 ans':'4',
         '5 ans':'5',
         '6 ans':'6',
         '7 ans':'7',
         '8 ans':'8',
         '9 ans':'9',
         '10 ans':'10',
         '11 ans':'11',
         '12 ans':'12',
        '13 ans':'13',
         '14 ans':'14',
         '15 ans':'15',
         '16 ans':'16',
         '17 ans':'17',
         '18 ans':'18',
        '19 ans':'19',
         '20 ans':'20',
         '21 ans':'21',
         '22 ans':'22',
         '23 ans':'23',
         '24 ans':'24',
         '25 ans':'25',
         '26 ans':'26',
         '27 ans':'27',
         '28 ans':'28',
         '29 ans':'29',
         '30 ans':'30'
    }
    
    if request.method == 'POST' :
        ID = mod_cv_form.ID.data
        Nom = mod_cv_form.Nom.data
        Prenom = mod_cv_form.Prenom.data
        Gender = mod_cv_form.Gender.data
        Fonction = mod_cv_form.Fonction.data
        Domaine = mod_cv_form.Domaine.data.replace("é", "e")
        Niveau = mod_cv_form.Niveau.data
        ColonneNiveau = int(niveau_selected_map.get(Niveau, ''))
        Annee_experience_en_conception = mod_cv_form.ColonneExperience.data
        ColonneExperience= experience_selected_map.get(Annee_experience_en_conception, '')
        Localisation = mod_cv_form.Localisation.data
        Source = mod_cv_form.Source.data
        Url = mod_cv_form.Url.data

        cv.Nom=Nom
        cv.Prenom=Prenom
        cv.Gender=Gender
        cv.Fonction=Fonction
        cv.Domaine=Domaine
        cv.Niveau=Niveau
        cv.ColonneNiveau=ColonneNiveau
        cv.Annee_experience_en_conception=Annee_experience_en_conception
        cv.ColonneExperience=ColonneExperience
        cv.Localisation=Localisation
        cv.Source=Source
        cv.Url=Url

        db.session.commit()

        logging.info(f"cv:{cv.Nom , cv.Prenom , cv.Gender , cv.Fonction,cv.Domaine,cv.Niveau,cv.ColonneNiveau,cv.Annee_experience_en_conception,cv.ColonneExperience,cv.Localisation,cv.Source,cv.Url}")
        logging.info(f"les informations ont ete modifiees avec succes. ")
        # return render_template("Database.html")
    return render_template('modifiercv.html',id=id ,cv=cv,mod_cv_form=mod_cv_form)


@app.route('/supprimercv/<int:id>', methods=('GET', 'POST'))
@login_required
def supprimercv(id):
    cv = CV.query.get_or_404(id)
    db.session.delete(cv)
    db.session.commit()
    return render_template('supprimercv.html',id=id)


if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)


# =================================== Build app 12 (07/04/2024 23:53)===============================
# import pickle
import sys

from forms import LoginForm, ModifyCVForm, SearchForm, TestForm,AddCVForm
from src.exception import CustomException
from src.logger import logging
from flask import Flask,request,render_template, flash ,redirect, url_for
import numpy as np
import pandas as pd
from sklearn.preprocessing	import  MinMaxScaler
from src.pipeline.predict_pipeline import CustomData , PredictPipeline
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField , SubmitField
from wtforms.validators import DataRequired
from datetime import datetime
from models import Users, db, CV, last_CV_ID, render_as_tuple, render_as_tuple_custom
from sqlalchemy import or_ , and_,asc, desc
from flask_login import login_user,LoginManager,login_required,logout_user,current_user
# from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt 
# from flask_bcrypt import check_password_hash
import bcrypt


application = Flask(__name__)
app = application

app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_cv1'
mysql = MySQL(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/db_cv1'  
db.init_app(app)

bcrypt = Bcrypt(app) 


def fetch_filtered_data(query):
    fetchdata = render_as_tuple_custom(query)
    # logging.info(f"fetchdata : {fetchdata}")
    logging.info(f"fetchdata type: {type(fetchdata)}")
    data = []
    for row in fetchdata:
        data_row = {
            'ID': row[0],
            'Nom': row[1],
            'Prenom': row[2],
            'Domain': row[3],
            'Gender': row[4],
            'Fonction': row[5],
            'Niveau': row[6],
            'ColonneNiveau': row[7],
            'Annee_experience_en_conception': row[8],
            'Prediction': row[9],
            'ColonneExperience': row[10],
            'Localisation': row[11],
            'Source': row[12],
            'Url': row[13]
        }
        data_row['Domain'] = data_row['Domain'].replace('ingénieur', 'Ingénieur').replace('ingénieu qualité', 'Ingénieur Qualité').replace('économie / gestion', 'Economie et Gestion').replace('technicien spécialisé', 'Technicien Spécialisé').replace('ingénieur process', 'Ingénieur Process').replace('ingénieur industriel', 'Ingénieur Industriel').replace('Ingénieur industriel', 'Ingénieur Industriel').replace('chargé de développement', 'Chargé de Développement').replace('concepteur/ dessinateur', 'Concepteur ou Dessinateur').replace('logistique', 'Logistique').replace('ingénieur mécanique', 'Ingénieur Mécanique')
        data.append(data_row)

    return data

def fetch_all_data():
    fetchdata = render_as_tuple()
    data = []
    for row in fetchdata:
        data_row = {
            'ID': row[0],
            'Nom': row[1],
            'Prenom': row[2],
            'Domain': row[3],
            'Gender': row[4],
            'Fonction': row[5],
            'Niveau': row[6],
            'ColonneNiveau': row[7],
            'Annee_experience_en_conception': row[8],
            'Prediction': row[9],  # We'll update this later
            'ColonneExperience': row[10],
            'Localisation': row[11],
            'Source': row[12],
            'Url': row[13]
        }
        pred_df = pd.DataFrame([data_row], columns=['ColonneNiveau', 'ColonneExperience', 'Gender', 'Domain'])
        pred_df['Domain'] = pred_df['Domain'].replace({'Ingénieur Industriel': 'ingénieur industriel', 'ingénieu qualité': 'ingenieur qualité'})
        pred_df['Domain'] = pred_df['Domain'].str.replace('é', 'e')
        predict_pipeline = PredictPipeline()
        prediction = predict_pipeline.predict(pred_df)[0]
        data_row['Prediction'] = prediction  # Update the Prediction field in data_row
        # Update the Prediction in the database using SQLAlchemy
        cv_instance = CV.query.filter_by(ID=row[0]).first()
        if cv_instance:
            cv_instance.Prediction = prediction
            db.session.commit()  # Commit the changes to the database
        else:
            # Handle the case where the CV instance with the given ID is not found
            pass
        data_row['Domain'] = data_row['Domain'].replace('ingénieur', 'Ingénieur')\
            .replace('ingénieu qualité', 'Ingénieur Qualité')\
            .replace('ingenieur qualite', 'Ingénieur Qualité')\
            .replace('économie / gestion', 'Economie et Gestion')\
            .replace('technicien spécialisé', 'Technicien Spécialisé')\
            .replace('ingénieur process', 'Ingénieur Process')\
            .replace('ingénieur industriel', 'Ingénieur Industriel')\
            .replace('Ingénieur industriel', 'Ingénieur Industriel')\
            .replace('chargé de développement', 'Chargé de Développement')\
            .replace('concepteur/ dessinateur', 'Concepteur ou Dessinateur')\
            .replace('logistique', 'Logistique')\
            .replace('ingénieur mécanique', 'Ingénieur Mécanique')\
            .replace('ingenieur qualite', 'Ingénieur Qualité')\
            .replace('economie / gestion', 'Economie et Gestion')\
            .replace('technicien specialise', 'Technicien Spécialisé')\
            .replace('ingenieur process', 'Ingénieur Process')\
            .replace('ingenieur industriel', 'Ingénieur Industriel')\
            .replace('charge de developpement', 'Chargé de Développement')\
            .replace('concepteur/ dessinateur', 'Concepteur ou Dessinateur')\
            .replace('ingenieur', 'Ingénieur')
        data.append(data_row)
    return data

@app.context_processor
def base():
    form=SearchForm()
    return dict(form=form)

def get_records():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    return CV.query.order_by(asc(CV.ID)).paginate(page=page, per_page=per_page, error_out=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home', methods=('GET', 'POST'))
def home():
    return render_template('home.html')

@app.route('/testdb')
def testdb():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = CV.query.order_by(asc(CV.ID)).paginate(page=page, per_page=per_page, error_out=False)
    records = pagination.items  
    return render_template('testdb.html', pagination=pagination, records=records)

login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = Users.query.filter_by(username=username).first()
        if not user:
            flash("Nom d'uilisateur incorrect. Veuillez réessayer à nouveau.")
            return redirect(url_for('login'))
        if not bcrypt.check_password_hash(user.password, password):
            flash('Mot de passe incorrect . Veuillez réessayer à nouveau.')
            return redirect(url_for('login'))
        login_user(user)
        flash('Bienvenue , ' + user.username + '!')
        return redirect(url_for('database'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        user = Users.query.filter_by(username=username).first()

        if user:
            flash('Utilisateur existant.')
            return redirect(url_for('register'))

        # Hash the password before storing it in the database
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = Users(email=email, username=username, password=hashed_password)

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        flash('Enregistrement avec succès.Vous pouvez vous connecter')
        return redirect(url_for('login'))

    return render_template('register.html')  # Replace 'success' with the name of your success route


@app.route('/search', methods=('GET', 'POST'))
@login_required
def search():
    return render_template('search.html')

def fetch_data_sorted_by_column(column_name, order,page, per_page):
    if column_name == 'Nom':
        return CV.query.order_by(order(CV.Nom)).paginate(page=page, per_page=per_page, error_out=False)
    elif column_name == 'ColonneNiveau':
        return CV.query.order_by(order(CV.ColonneNiveau)).paginate(page=page, per_page=per_page, error_out=False)
    elif column_name == 'ColonneExperience':
        return CV.query.order_by(order(CV.ColonneExperience)).paginate(page=page, per_page=per_page, error_out=False)
    else:
        return CV.query.order_by(order(CV.ID)).paginate(page=page, per_page=per_page, error_out=False)
    
@app.route('/database', methods=['GET', 'POST'])
@login_required
def database():
    form = SearchForm()
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = CV.query.paginate(page=page, per_page=per_page, error_out=False)
    domain_selected_map = {
                        '1': 'ingénieu qualité',
                        '2': 'économie / gestion',
                        '3': 'technicien spécialisé',
                        '4': 'ingénieur',
                        '5': 'ingénieur industriel',
                        '6': 'chargé de développement',
                        '7': 'concepteur/ dessinateur',
                        '8': 'logistique',
                        '9': 'ingénieur mécanique',
                        '10': 'ingénieur process'
                    }
    if request.method == 'POST' and form.validate_on_submit():
        search_term = form.search.data
        domain_selected = request.form.get('domain')
        niveau=request.form.get('niveau')
        niveau=int(niveau)
        logging.info(f"niveau: {niveau}")
        logging.info(f"niveau type: {type(niveau)}")
        experience=request.form.get('experience')
        experience=int(experience)
        logging.info(f"experience: {experience}")
        logging.info(f"experience type: {type(experience)}")
        prediction_status = request.form.get('prediction_status')
        if prediction_status != 'all':
            prediction_status = int(prediction_status)
        logging.info(f"prediction_status: {prediction_status}")
        query=CV.query
        logging.info(f"search_term: {search_term}")
        try:
            if search_term:
                search_term = form.search.data
                if domain_selected == 'all':
                    if experience ==-1 and niveau ==-1:
                        if prediction_status == 'all':
                            query=CV.query.filter(or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%')))
                        elif prediction_status == 1:
                            query = CV.query.filter(and_(CV.Prediction == 1,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 0:
                            query = CV.query.filter(and_(CV.Prediction == 0,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience ==-1 and niveau !=-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneNiveau == niveau,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 1:
                            query = CV.query.filter(and_(CV.Prediction == 1,CV.ColonneNiveau == niveau,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 0:
                            query = CV.query.filter(and_(CV.Prediction == 0,CV.ColonneNiveau == niveau,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience !=-1 and niveau ==-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneExperience == experience,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 1:
                            query = CV.query.filter(and_(CV.Prediction == 1,CV.ColonneExperience == experience,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 0:
                            query = CV.query.filter(and_(CV.Prediction == 0,CV.ColonneExperience == experience,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience !=-1 and niveau !=-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 1:
                            query = CV.query.filter(and_(CV.Prediction == 1,CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 0:
                            query = CV.query.filter(and_(CV.Prediction == 0,CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                else:
                    domain_selected = domain_selected_map.get(domain_selected, '')
                    if experience ==-1 and niveau ==-1:
                        if prediction_status == 'all':
                            query=CV.query.filter(and_(CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 1:
                            query=CV.query.filter(and_(CV.Prediction == 1,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 0:
                            query=CV.query.filter(and_(CV.Prediction == 0,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience ==-1 and niveau !=-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneNiveau == niveau,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 1:
                            query = CV.query.filter(and_(CV.Prediction == 1,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 0:
                            query = CV.query.filter(and_(CV.Prediction == 0,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience !=-1 and niveau ==-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 1:
                            query = CV.query.filter(and_(CV.Prediction == 1,CV.ColonneExperience == experience,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 0:
                            query = CV.query.filter(and_(CV.Prediction == 0,CV.ColonneExperience == experience,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience !=-1 and niveau !=-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 1:
                            query = CV.query.filter(and_(CV.Prediction == 1,CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 0:
                            query = CV.query.filter(and_(CV.Prediction == 0,CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                logging.info(f"query1: {query}")
                data = fetch_filtered_data(query)
                if not data:
                    logging.error(f"data: {data}")
                    logging.error(f"search_term: {search_term}")
                    logging.error(f"domain_selected: {domain_selected}")
                    logging.warning(f"No results found for search term: {search_term}")
                    flash('No results found for your search term.', 'warning')
                    return render_template('Database.html', data=data, search=search_term, domain_selected=domain_selected,niveau=niveau,experience=experience,pagination=pagination)
                else:
                    return render_template('Database.html', data=data, domain_selected=domain_selected,niveau=niveau,experience=experience,pagination=pagination)
            elif domain_selected:
                if domain_selected == 'all':
                    if experience ==-1 and niveau ==-1:
                        if prediction_status == 'all':
                            query=CV.query.limit(20).all()
                        elif prediction_status == 1:
                            query=CV.query.filter(CV.Prediction == 1)
                        elif prediction_status == 0:
                            query=CV.query.filter(CV.Prediction == 0)
                    elif experience ==-1 and niveau !=-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(CV.ColonneNiveau == niveau)
                        elif prediction_status == 1:
                            query=CV.query.filter(and_(CV.Prediction == 1,CV.ColonneNiveau == niveau))
                        elif prediction_status == 0:
                            query=CV.query.filter(and_(CV.Prediction == 0,CV.ColonneNiveau == niveau))
                    elif experience !=-1 and niveau ==-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(CV.ColonneExperience == experience)
                        elif prediction_status == 1:
                            query=CV.query.filter(and_(CV.Prediction == 1,CV.ColonneExperience == experience))
                        elif prediction_status == 0:
                            query=CV.query.filter(and_(CV.Prediction == 0,CV.ColonneExperience == experience))
                    elif experience !=-1 and niveau !=-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.ColonneNiveau == niveau))
                        elif prediction_status == 1:
                            query=CV.query.filter(and_(CV.Prediction == 1,CV.ColonneExperience == experience,CV.ColonneNiveau == niveau))
                        elif prediction_status == 0:
                            query=CV.query.filter(and_(CV.Prediction == 0,CV.ColonneExperience == experience,CV.ColonneNiveau == niveau))
                    logging.info(f"query2: {query}")
                    data = fetch_filtered_data(query)
                    return render_template('Database.html', data=data, domain_selected=domain_selected,niveau=niveau,experience=experience,pagination=pagination)
                else:
                    domain_selected = domain_selected_map.get(domain_selected, '')
                    if experience ==-1 and niveau ==-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(CV.Domaine == domain_selected)
                        elif prediction_status == 1:
                            query=CV.query.filter(and_(CV.Prediction == 1,CV.Domaine == domain_selected))
                        elif prediction_status == 0:
                            query=CV.query.filter(and_(CV.Prediction == 0,CV.Domaine == domain_selected))
                    elif experience ==-1 and niveau !=-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneNiveau == niveau,CV.Domaine == domain_selected))
                        elif prediction_status == 1:
                            query=CV.query.filter(and_(CV.Prediction == 1,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected))
                        elif prediction_status == 0:
                            query=CV.query.filter(and_(CV.Prediction == 0,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected))
                    elif experience !=-1 and niveau ==-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.Domaine == domain_selected))
                        elif prediction_status == 1:
                            query=CV.query.filter(and_(CV.Prediction == 1,CV.ColonneExperience == experience,CV.Domaine == domain_selected))
                        elif prediction_status == 0:
                            query=CV.query.filter(and_(CV.Prediction == 0,CV.ColonneExperience == experience,CV.Domaine == domain_selected))
                    elif experience !=-1 and niveau !=-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected))
                        elif prediction_status == 1:
                            query=CV.query.filter(and_(CV.Prediction == 1,CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected))
                        elif prediction_status == 0:
                            query=CV.query.filter(and_(CV.Prediction == 0,CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected))
                    logging.info(f"query3: {query}")
                    data = fetch_filtered_data(query)
                    return render_template('Database.html', data=data, domain_selected=domain_selected,niveau=niveau,experience=experience,pagination=pagination)
            elif prediction_status != 'all':
                if prediction_status == 1:
                    query = CV.query.filter(CV.Prediction == 1)
                elif prediction_status == 0:
                    query = CV.query.filter(CV.Prediction == 0)
                else:
                    query=CV.query.limit(20).all()
                logging.info(f"query4: {query}")
                data = fetch_filtered_data(query)
                return render_template('Database.html', data=data, domain_selected=domain_selected,niveau=niveau,experience=experience,pagination=pagination)
            else:
                data=fetch_all_data()
                logging.info(f"data4: {data}")
                return render_template('Database.html', data=data,niveau=niveau,experience=experience,pagination=pagination)
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            raise CustomException(e, sys)
    else:
        try:
            page = request.args.get('page', 1, type=int)
            per_page = 10
            pagination = CV.query.paginate(page=page, per_page=per_page, error_out=False)
            data = pagination.items
            # data=fetch_all_data()
            sort_by = request.args.get('sort_by', 'ID')
            sort_order = request.args.get('sort_order', 'desc')
            if sort_by == 'Nom':
                if sort_order == 'asc':
                    data = fetch_data_sorted_by_column('Nom', asc,page=page, per_page=per_page)
                    sort_order = 'desc'
                else:
                    data = fetch_data_sorted_by_column('Nom', desc,page=page, per_page=per_page)
                    sort_order = 'asc'
            elif sort_by == 'Niveau':
                if sort_order == 'asc':
                    data = fetch_data_sorted_by_column('ColonneNiveau', asc,page=page, per_page=per_page)
                    sort_order = 'desc'
                else:
                    data = fetch_data_sorted_by_column('ColonneNiveau', desc,page=page, per_page=per_page)
                    sort_order = 'asc'
            elif sort_by == 'ColonneExperience':
                if sort_order == 'asc':
                    data = fetch_data_sorted_by_column('ColonneExperience', asc,page=page, per_page=per_page)
                    sort_order = 'desc'
                else:
                    data = fetch_data_sorted_by_column('ColonneExperience', desc,page=page, per_page=per_page)
                    sort_order = 'asc'
            else:
                if sort_order == 'asc':
                    data = fetch_data_sorted_by_column(sort_by, asc,page=page, per_page=per_page)
                else:
                    data = fetch_data_sorted_by_column(sort_by, desc,page=page, per_page=per_page)
            return render_template('Database.html', data=data,pagination=pagination, sort_by=sort_by, sort_order=sort_order)
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            raise CustomException(e, sys)


@app.route('/predictdata',methods=['GET','POST'])
@login_required
def predict_datapoint():
    if request.method == 'GET':
        return render_template("predict.html")
    else:
        data = CustomData(
            Gender=request.form.get('Gender'),
            Domain=request.form.get('Domain'),
            ColonneExperience=request.form.get('ColonneExperience'),
            ColonneNiveau=request.form.get('ColonneNiveau')
        )
        pred_df=data.get_data_as_data_frame()
        print(pred_df)
        predict_pipeline=PredictPipeline()
        results = predict_pipeline.predict(pred_df)
        return render_template('predict.html',results=results[0])


@app.route('/modal', methods=('GET', 'POST'))
@login_required
def modal():
    domain_selected_map = {
                        '1': 'ingenieur qualite',
                        '2': 'economie / gestion',
                        '3': 'technicien specialise',
                        '4': 'ingenieur',
                        '5': 'ingenieur industriel',
                        '6': 'charge de developpementt',
                        '7': 'concepteur/ dessinateur',
                        '8': 'logistique',
                        '9': 'ingenieur mecanique',
                        '10': 'ingenieur process'
                    }
    niveau_selected_map = {
        'BAC ': '',
        'BAC + 1': '1',
        'BAC + 2': '2',
        'BAC + 3': '3',
        'BAC + 4': '4',
        'BAC + 5': '5',
        'BAC + 6': '6',
        'BAC + 7': '7',
        'BAC + 8': '8',
        'BAC + 9': '9',
        'BAC + 10': '10',
        'BAC + 11': '11',
        'BAC + 12': '12',
        'BAC + 13': '13',
        'BAC + 14': '14',
        'BAC + 15': '15',
        'BAC + 16': '16',
        'BAC + 17': '17',
        'BAC + 18': '18',
        'BAC + 19': '19',
        'BAC + 20': '20',
                    }
    experience_selected_map = {
        '0': "Moins d'un an", 
        '1': '1 an',
        '2': '2 ans',
        '3': '3 ans',
        '4': '4 ans',
        '5': '5 ans',
        '6': '6 ans',
        '7': '7 ans',
        '8': '8 ans',
        '9': '9 ans',
        '10': '10 ans',
        '11': '11 ans',
        '12': '12 ans',
        '13': '13 ans',
        '14': '14 ans',
        '15': '15 ans',
        '16': '16 ans',
        '17': '17 ans',
        '18': '18 ans',
        '19': '19 ans',
        '20': '20 ans',
        '21': '21 ans',
        '22': '22 ans',
        '23': '23 ans',
        '24': '24 ans',
        '25': '25 ans',
        '26': '26 ans',
        '27': '27 ans',
        '28': '28 ans',
        '29': '29 ans',
        '30': '30 ans'
    }
    add_cv_form = AddCVForm()
    last_id = last_CV_ID()
    if request.method == 'POST' : 
        ID = add_cv_form.ID.data
        Nom = add_cv_form.Nom.data
        Prenom = add_cv_form.Prenom.data
        Gender = add_cv_form.Gender.data
        Fonction = add_cv_form.Fonction.data
        Domaine = add_cv_form.Domaine.data
        Domaine = domain_selected_map.get(Domaine, '')
        Niveau_label = add_cv_form.Niveau.data
        Niveau_selected = int(niveau_selected_map.get(Niveau_label, ''))
        ColonneExperience = add_cv_form.ColonneExperience.data
        Annee_experience_en_conception = experience_selected_map.get(ColonneExperience, '')
        ColonneExperience = int(ColonneExperience)
        Localisation = add_cv_form.Localisation.data
        Source = add_cv_form.Source.data
        Url = add_cv_form.Url.data
        new = CV(ID=ID, Nom=Nom, Prenom=Prenom, Gender=Gender, Fonction=Fonction, Domaine=Domaine,
                    Niveau=Niveau_label,ColonneNiveau=Niveau_selected, Annee_experience_en_conception=Annee_experience_en_conception,
                      ColonneExperience=ColonneExperience, Localisation=Localisation, Source=Source, Url=Url)
        db.session.add(new)
        db.session.commit()
        flash('CV added successfully', 'success')
        logging.info(f'CV added successfully : {new}')
        return render_template('modal.html',add_cv_form=add_cv_form,last_id=last_id, ID=ID, Nom=Nom, Prenom=Prenom, 
                               Gender=Gender, Fonction=Fonction, Domaine=Domaine, Niveau=Niveau_label,
                                 Annee_experience_en_conception=Annee_experience_en_conception, Localisation=Localisation,
                                   Source=Source, Url=Url)
    return render_template('modal.html',last_id=last_id,add_cv_form=add_cv_form)


@app.route('/candidature', methods=('GET', 'POST'))
def candidature():
    domain_selected_map = {
                        '1': 'ingenieur qualite',
                        '2': 'economie / gestion',
                        '3': 'technicien specialise',
                        '4': 'ingenieur',
                        '5': 'ingenieur industriel',
                        '6': 'charge de developpementt',
                        '7': 'concepteur/ dessinateur',
                        '8': 'logistique',
                        '9': 'ingenieur mecanique',
                        '10': 'ingenieur process'
                    }
    niveau_selected_map = {
        'BAC ': '',
        'BAC + 1': '1',
        'BAC + 2': '2',
        'BAC + 3': '3',
        'BAC + 4': '4',
        'BAC + 5': '5',
        'BAC + 6': '6',
        'BAC + 7': '7',
        'BAC + 8': '8',
        'BAC + 9': '9',
        'BAC + 10': '10',
        'BAC + 11': '11',
        'BAC + 12': '12',
        'BAC + 13': '13',
        'BAC + 14': '14',
        'BAC + 15': '15',
        'BAC + 16': '16',
        'BAC + 17': '17',
        'BAC + 18': '18',
        'BAC + 19': '19',
        'BAC + 20': '20',
                    }
    experience_selected_map = {
        '0': "Moins d'un an", 
        '1': '1 an',
        '2': '2 ans',
        '3': '3 ans',
        '4': '4 ans',
        '5': '5 ans',
        '6': '6 ans',
        '7': '7 ans',
        '8': '8 ans',
        '9': '9 ans',
        '10': '10 ans',
        '11': '11 ans',
        '12': '12 ans',
        '13': '13 ans',
        '14': '14 ans',
        '15': '15 ans',
        '16': '16 ans',
        '17': '17 ans',
        '18': '18 ans',
        '19': '19 ans',
        '20': '20 ans',
        '21': '21 ans',
        '22': '22 ans',
        '23': '23 ans',
        '24': '24 ans',
        '25': '25 ans',
        '26': '26 ans',
        '27': '27 ans',
        '28': '28 ans',
        '29': '29 ans',
        '30': '30 ans'
    }
    add_cv_form = AddCVForm()
    last_id = last_CV_ID()
    if request.method == 'POST' : 
        add_cv_form = AddCVForm(request.form)
        ID = add_cv_form.ID.data
        Nom = add_cv_form.Nom.data
        Prenom = add_cv_form.Prenom.data
        Gender = add_cv_form.Gender.data
        Fonction = add_cv_form.Fonction.data
        Domaine = add_cv_form.Domaine.data
        Domaine = domain_selected_map.get(Domaine, '')
        Niveau_label = add_cv_form.Niveau.data
        Niveau_selected = int(niveau_selected_map.get(Niveau_label, ''))
        ColonneExperience = add_cv_form.ColonneExperience.data
        Annee_experience_en_conception = experience_selected_map.get(ColonneExperience, '')
        ColonneExperience = int(ColonneExperience)
        Localisation = add_cv_form.Localisation.data
        Source = add_cv_form.Source.data
        Url = add_cv_form.Url.data
        new = CV(ID=ID, Nom=Nom, Prenom=Prenom, Gender=Gender, Fonction=Fonction, Domaine=Domaine,
                    Niveau=Niveau_label,ColonneNiveau=Niveau_selected, Annee_experience_en_conception=Annee_experience_en_conception,
                      ColonneExperience=ColonneExperience, Localisation=Localisation, Source=Source, Url=Url)
        db.session.add(new)
        db.session.commit()
        flash('CV added successfully', 'success')
        logging.info(f'CV added successfully : {new}')
        return render_template('candidature.html',add_cv_form=add_cv_form,last_id=last_id, ID=ID, Nom=Nom, Prenom=Prenom, 
                               Gender=Gender, Fonction=Fonction, Domaine=Domaine, Niveau=Niveau_label,
                                 Annee_experience_en_conception=Annee_experience_en_conception, Localisation=Localisation,
                                   Source=Source, Url=Url)
    return render_template('candidature.html',add_cv_form=add_cv_form,last_id=last_id)


@app.route('/modifiercv/<int:id>', methods=('GET', 'POST'))
@login_required
def modifiercv(id):
    cv = CV.query.get_or_404(id)
    mod_cv_form=ModifyCVForm()
    domain_selected_map = {
                        '1': 'ingenieur qualite',
                        '2': 'economie / gestion',
                        '3': 'technicien specialise',
                        '4': 'ingenieur',
                        '5': 'ingenieur industriel',
                        '6': 'charge de developpementt',
                        '7': 'concepteur/ dessinateur',
                        '8': 'logistique',
                        '9': 'ingenieur mecanique',
                        '10': 'ingenieur process'
                    }
    niveau_selected_map = {
        'BAC ': '',
        'BAC + 1': '1',
        'BAC + 2': '2',
        'BAC + 3': '3',
        'BAC + 4': '4',
        'BAC + 5': '5',
        'BAC + 6': '6',
        'BAC + 7': '7',
        'BAC + 8': '8',
        'BAC + 9': '9',
        'BAC + 10': '10',
        'BAC + 11': '11',
        'BAC + 12': '12',
        'BAC + 13': '13',
        'BAC + 14': '14',
        'BAC + 15': '15',
        'BAC + 16': '16',
        'BAC + 17': '17',
        'BAC + 18': '18',
        'BAC + 19': '19',
        'BAC + 20': '20',
                    }
    experience_selected_map = {
         "Moins d'un an":'0', 
         '1 an':'1',
         '2 ans':'2',
         '3 ans':'3',
         '4 ans':'4',
         '5 ans':'5',
         '6 ans':'6',
         '7 ans':'7',
         '8 ans':'8',
         '9 ans':'9',
         '10 ans':'10',
         '11 ans':'11',
         '12 ans':'12',
        '13 ans':'13',
         '14 ans':'14',
         '15 ans':'15',
         '16 ans':'16',
         '17 ans':'17',
         '18 ans':'18',
        '19 ans':'19',
         '20 ans':'20',
         '21 ans':'21',
         '22 ans':'22',
         '23 ans':'23',
         '24 ans':'24',
         '25 ans':'25',
         '26 ans':'26',
         '27 ans':'27',
         '28 ans':'28',
         '29 ans':'29',
         '30 ans':'30'
    }
    
    if request.method == 'POST' :
        ID = mod_cv_form.ID.data
        Nom = mod_cv_form.Nom.data
        Prenom = mod_cv_form.Prenom.data
        Gender = mod_cv_form.Gender.data
        Fonction = mod_cv_form.Fonction.data
        Domaine = mod_cv_form.Domaine.data.replace("é", "e")
        Niveau = mod_cv_form.Niveau.data
        ColonneNiveau = int(niveau_selected_map.get(Niveau, ''))
        Annee_experience_en_conception = mod_cv_form.ColonneExperience.data
        ColonneExperience= experience_selected_map.get(Annee_experience_en_conception, '')
        Localisation = mod_cv_form.Localisation.data
        Source = mod_cv_form.Source.data
        Url = mod_cv_form.Url.data

        cv.Nom=Nom
        cv.Prenom=Prenom
        cv.Gender=Gender
        cv.Fonction=Fonction
        cv.Domaine=Domaine
        cv.Niveau=Niveau
        cv.ColonneNiveau=ColonneNiveau
        cv.Annee_experience_en_conception=Annee_experience_en_conception
        cv.ColonneExperience=ColonneExperience
        cv.Localisation=Localisation
        cv.Source=Source
        cv.Url=Url

        db.session.commit()

        logging.info(f"cv:{cv.Nom , cv.Prenom , cv.Gender , cv.Fonction,cv.Domaine,cv.Niveau,cv.ColonneNiveau,cv.Annee_experience_en_conception,cv.ColonneExperience,cv.Localisation,cv.Source,cv.Url}")
        logging.info(f"les informations ont ete modifiees avec succes. ")
        # return render_template("Database.html")
    return render_template('modifiercv.html',id=id ,cv=cv,mod_cv_form=mod_cv_form)


@app.route('/supprimercv/<int:id>', methods=('GET', 'POST'))
@login_required
def supprimercv(id):
    cv = CV.query.get_or_404(id)
    db.session.delete(cv)
    db.session.commit()
    return render_template('supprimercv.html',id=id)


if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)

# =================================== Build app 13 (08/04/2024 12:35)===============================
# import pickle
import sys

from forms import ContactForm, LoginForm, ModifyCVForm, SearchForm, TestForm,AddCVForm
from src.exception import CustomException
from src.logger import logging
from flask import Flask,request,render_template, flash ,redirect, url_for
import numpy as np
import pandas as pd
from sklearn.preprocessing	import  MinMaxScaler
from src.pipeline.predict_pipeline import CustomData , PredictPipeline
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField , SubmitField, TextAreaField
from wtforms.validators import DataRequired
from datetime import datetime
from models import ContactUs, Users, db, CV, last_CV_ID, render_as_tuple, render_as_tuple_custom
from sqlalchemy import or_ , and_,asc, desc
from flask_login import login_user,LoginManager,login_required,logout_user,current_user
# from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt 
# from flask_bcrypt import check_password_hash
import bcrypt


application = Flask(__name__)
app = application

app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_cv1'
mysql = MySQL(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/db_cv1'  
db.init_app(app)

bcrypt = Bcrypt(app) 


def fetch_filtered_data(query):
    fetchdata = render_as_tuple_custom(query)
    # logging.info(f"fetchdata : {fetchdata}")
    logging.info(f"fetchdata type: {type(fetchdata)}")
    data = []
    for row in fetchdata:
        data_row = {
            'ID': row[0],
            'Nom': row[1],
            'Prenom': row[2],
            'Domain': row[3],
            'Gender': row[4],
            'Fonction': row[5],
            'Niveau': row[6],
            'ColonneNiveau': row[7],
            'Annee_experience_en_conception': row[8],
            'Prediction': row[9],
            'ColonneExperience': row[10],
            'Localisation': row[11],
            'Source': row[12],
            'Url': row[13]
        }
        data_row['Domain'] = data_row['Domain'].replace('ingénieur', 'Ingénieur').replace('ingénieu qualité', 'Ingénieur Qualité').replace('économie / gestion', 'Economie et Gestion').replace('technicien spécialisé', 'Technicien Spécialisé').replace('ingénieur process', 'Ingénieur Process').replace('ingénieur industriel', 'Ingénieur Industriel').replace('Ingénieur industriel', 'Ingénieur Industriel').replace('chargé de développement', 'Chargé de Développement').replace('concepteur/ dessinateur', 'Concepteur ou Dessinateur').replace('logistique', 'Logistique').replace('ingénieur mécanique', 'Ingénieur Mécanique')
        data.append(data_row)

    return data

def fetch_all_data():
    fetchdata = render_as_tuple()
    data = []
    for row in fetchdata:
        data_row = {
            'ID': row[0],
            'Nom': row[1],
            'Prenom': row[2],
            'Domain': row[3],
            'Gender': row[4],
            'Fonction': row[5],
            'Niveau': row[6],
            'ColonneNiveau': row[7],
            'Annee_experience_en_conception': row[8],
            'Prediction': row[9],  # We'll update this later
            'ColonneExperience': row[10],
            'Localisation': row[11],
            'Source': row[12],
            'Url': row[13]
        }
        pred_df = pd.DataFrame([data_row], columns=['ColonneNiveau', 'ColonneExperience', 'Gender', 'Domain'])
        pred_df['Domain'] = pred_df['Domain'].replace({'Ingénieur Industriel': 'ingénieur industriel', 'ingénieu qualité': 'ingenieur qualité'})
        pred_df['Domain'] = pred_df['Domain'].str.replace('é', 'e')
        predict_pipeline = PredictPipeline()
        prediction = predict_pipeline.predict(pred_df)[0]
        data_row['Prediction'] = prediction  # Update the Prediction field in data_row
        # Update the Prediction in the database using SQLAlchemy
        cv_instance = CV.query.filter_by(ID=row[0]).first()
        if cv_instance:
            cv_instance.Prediction = prediction
            db.session.commit()  # Commit the changes to the database
        else:
            # Handle the case where the CV instance with the given ID is not found
            pass
        data_row['Domain'] = data_row['Domain'].replace('ingénieur', 'Ingénieur')\
            .replace('ingénieu qualité', 'Ingénieur Qualité')\
            .replace('ingenieur qualite', 'Ingénieur Qualité')\
            .replace('économie / gestion', 'Economie et Gestion')\
            .replace('technicien spécialisé', 'Technicien Spécialisé')\
            .replace('ingénieur process', 'Ingénieur Process')\
            .replace('ingénieur industriel', 'Ingénieur Industriel')\
            .replace('Ingénieur industriel', 'Ingénieur Industriel')\
            .replace('chargé de développement', 'Chargé de Développement')\
            .replace('concepteur/ dessinateur', 'Concepteur ou Dessinateur')\
            .replace('logistique', 'Logistique')\
            .replace('ingénieur mécanique', 'Ingénieur Mécanique')\
            .replace('ingenieur qualite', 'Ingénieur Qualité')\
            .replace('economie / gestion', 'Economie et Gestion')\
            .replace('technicien specialise', 'Technicien Spécialisé')\
            .replace('ingenieur process', 'Ingénieur Process')\
            .replace('ingenieur industriel', 'Ingénieur Industriel')\
            .replace('charge de developpement', 'Chargé de Développement')\
            .replace('concepteur/ dessinateur', 'Concepteur ou Dessinateur')\
            .replace('ingenieur', 'Ingénieur')
        data.append(data_row)
    return data

@app.context_processor
def base():
    form=SearchForm()
    return dict(form=form)

def get_records():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    return CV.query.order_by(asc(CV.ID)).paginate(page=page, per_page=per_page, error_out=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home', methods=('GET', 'POST'))
def home():
    contactform=ContactForm()
    if request.method == 'POST' :
        if contactform.validate_on_submit():
            contactform=ContactForm(request.form)
            new_contact = ContactUs(
                name = contactform.name.data,
                email = contactform.email.data,
                subject = contactform.subject.data,
                message = contactform.message.data
            )
            db.session.add(new_contact)
            db.session.commit()
            flash('Votre message a été envoyé avec succès!', 'success')
            logging.info(f'contactus added successfully : {new_contact}')
            return redirect(url_for('home'))
    return render_template('home.html', contactform=contactform)

@app.route('/testdb')
def testdb():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = CV.query.order_by(asc(CV.ID)).paginate(page=page, per_page=per_page, error_out=False)
    records = pagination.items  
    return render_template('testdb.html', pagination=pagination, records=records)

login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = Users.query.filter_by(username=username).first()
        if not user:
            flash("Nom d'uilisateur incorrect. Veuillez réessayer à nouveau.")
            return redirect(url_for('login'))
        if not bcrypt.check_password_hash(user.password, password):
            flash('Mot de passe incorrect . Veuillez réessayer à nouveau.')
            return redirect(url_for('login'))
        login_user(user)
        flash('Bienvenue , ' + user.username + '!')
        return redirect(url_for('database'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        user = Users.query.filter_by(username=username).first()

        if user:
            flash('Utilisateur existant.')
            return redirect(url_for('register'))

        # Hash the password before storing it in the database
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = Users(email=email, username=username, password=hashed_password)

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        flash('Enregistrement avec succès.Vous pouvez vous connecter')
        return redirect(url_for('login'))

    return render_template('register.html')  # Replace 'success' with the name of your success route


@app.route('/search', methods=('GET', 'POST'))
@login_required
def search():
    return render_template('search.html')

def fetch_data_sorted_by_column(column_name, order,page, per_page):
    if column_name == 'Nom':
        return CV.query.order_by(order(CV.Nom)).paginate(page=page, per_page=per_page, error_out=False)
    elif column_name == 'ColonneNiveau':
        return CV.query.order_by(order(CV.ColonneNiveau)).paginate(page=page, per_page=per_page, error_out=False)
    elif column_name == 'ColonneExperience':
        return CV.query.order_by(order(CV.ColonneExperience)).paginate(page=page, per_page=per_page, error_out=False)
    else:
        return CV.query.order_by(order(CV.ID)).paginate(page=page, per_page=per_page, error_out=False)
    
@app.route('/database', methods=['GET', 'POST'])
@login_required
def database():
    form = SearchForm()
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = CV.query.paginate(page=page, per_page=per_page, error_out=False)
    domain_selected_map = {
                        '1': 'ingénieu qualité',
                        '2': 'économie / gestion',
                        '3': 'technicien spécialisé',
                        '4': 'ingénieur',
                        '5': 'ingénieur industriel',
                        '6': 'chargé de développement',
                        '7': 'concepteur/ dessinateur',
                        '8': 'logistique',
                        '9': 'ingénieur mécanique',
                        '10': 'ingénieur process'
                    }
    if request.method == 'POST' and form.validate_on_submit():
        search_term = form.search.data
        domain_selected = request.form.get('domain')
        niveau=request.form.get('niveau')
        niveau=int(niveau)
        logging.info(f"niveau: {niveau}")
        logging.info(f"niveau type: {type(niveau)}")
        experience=request.form.get('experience')
        experience=int(experience)
        logging.info(f"experience: {experience}")
        logging.info(f"experience type: {type(experience)}")
        prediction_status = request.form.get('prediction_status')
        if prediction_status != 'all':
            prediction_status = int(prediction_status)
        logging.info(f"prediction_status: {prediction_status}")
        query=CV.query
        logging.info(f"search_term: {search_term}")
        try:
            if search_term:
                search_term = form.search.data
                if domain_selected == 'all':
                    if experience ==-1 and niveau ==-1:
                        if prediction_status == 'all':
                            query=CV.query.filter(or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%')))
                        elif prediction_status == 1:
                            query = CV.query.filter(and_(CV.Prediction == 1,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 0:
                            query = CV.query.filter(and_(CV.Prediction == 0,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience ==-1 and niveau !=-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneNiveau == niveau,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 1:
                            query = CV.query.filter(and_(CV.Prediction == 1,CV.ColonneNiveau == niveau,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 0:
                            query = CV.query.filter(and_(CV.Prediction == 0,CV.ColonneNiveau == niveau,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience !=-1 and niveau ==-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneExperience == experience,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 1:
                            query = CV.query.filter(and_(CV.Prediction == 1,CV.ColonneExperience == experience,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 0:
                            query = CV.query.filter(and_(CV.Prediction == 0,CV.ColonneExperience == experience,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience !=-1 and niveau !=-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 1:
                            query = CV.query.filter(and_(CV.Prediction == 1,CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 0:
                            query = CV.query.filter(and_(CV.Prediction == 0,CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                else:
                    domain_selected = domain_selected_map.get(domain_selected, '')
                    if experience ==-1 and niveau ==-1:
                        if prediction_status == 'all':
                            query=CV.query.filter(and_(CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 1:
                            query=CV.query.filter(and_(CV.Prediction == 1,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 0:
                            query=CV.query.filter(and_(CV.Prediction == 0,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience ==-1 and niveau !=-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneNiveau == niveau,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 1:
                            query = CV.query.filter(and_(CV.Prediction == 1,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 0:
                            query = CV.query.filter(and_(CV.Prediction == 0,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience !=-1 and niveau ==-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 1:
                            query = CV.query.filter(and_(CV.Prediction == 1,CV.ColonneExperience == experience,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 0:
                            query = CV.query.filter(and_(CV.Prediction == 0,CV.ColonneExperience == experience,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                    elif experience !=-1 and niveau !=-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 1:
                            query = CV.query.filter(and_(CV.Prediction == 1,CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                        elif prediction_status == 0:
                            query = CV.query.filter(and_(CV.Prediction == 0,CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected,or_(CV.Nom.like(f'%{search_term}%'), CV.Prenom.like(f'%{search_term}%'))))
                logging.info(f"query1: {query}")
                data = fetch_filtered_data(query)
                if not data:
                    logging.error(f"data: {data}")
                    logging.error(f"search_term: {search_term}")
                    logging.error(f"domain_selected: {domain_selected}")
                    logging.warning(f"No results found for search term: {search_term}")
                    flash('No results found for your search term.', 'warning')
                    return render_template('Database.html', data=data, search=search_term, domain_selected=domain_selected,niveau=niveau,experience=experience,pagination=pagination)
                else:
                    return render_template('Database.html', data=data, domain_selected=domain_selected,niveau=niveau,experience=experience,pagination=pagination)
            elif domain_selected:
                if domain_selected == 'all':
                    if experience ==-1 and niveau ==-1:
                        if prediction_status == 'all':
                            query=CV.query.limit(20).all()
                        elif prediction_status == 1:
                            query=CV.query.filter(CV.Prediction == 1)
                        elif prediction_status == 0:
                            query=CV.query.filter(CV.Prediction == 0)
                    elif experience ==-1 and niveau !=-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(CV.ColonneNiveau == niveau)
                        elif prediction_status == 1:
                            query=CV.query.filter(and_(CV.Prediction == 1,CV.ColonneNiveau == niveau))
                        elif prediction_status == 0:
                            query=CV.query.filter(and_(CV.Prediction == 0,CV.ColonneNiveau == niveau))
                    elif experience !=-1 and niveau ==-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(CV.ColonneExperience == experience)
                        elif prediction_status == 1:
                            query=CV.query.filter(and_(CV.Prediction == 1,CV.ColonneExperience == experience))
                        elif prediction_status == 0:
                            query=CV.query.filter(and_(CV.Prediction == 0,CV.ColonneExperience == experience))
                    elif experience !=-1 and niveau !=-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.ColonneNiveau == niveau))
                        elif prediction_status == 1:
                            query=CV.query.filter(and_(CV.Prediction == 1,CV.ColonneExperience == experience,CV.ColonneNiveau == niveau))
                        elif prediction_status == 0:
                            query=CV.query.filter(and_(CV.Prediction == 0,CV.ColonneExperience == experience,CV.ColonneNiveau == niveau))
                    logging.info(f"query2: {query}")
                    data = fetch_filtered_data(query)
                    return render_template('Database.html', data=data, domain_selected=domain_selected,niveau=niveau,experience=experience,pagination=pagination)
                else:
                    domain_selected = domain_selected_map.get(domain_selected, '')
                    if experience ==-1 and niveau ==-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(CV.Domaine == domain_selected)
                        elif prediction_status == 1:
                            query=CV.query.filter(and_(CV.Prediction == 1,CV.Domaine == domain_selected))
                        elif prediction_status == 0:
                            query=CV.query.filter(and_(CV.Prediction == 0,CV.Domaine == domain_selected))
                    elif experience ==-1 and niveau !=-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneNiveau == niveau,CV.Domaine == domain_selected))
                        elif prediction_status == 1:
                            query=CV.query.filter(and_(CV.Prediction == 1,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected))
                        elif prediction_status == 0:
                            query=CV.query.filter(and_(CV.Prediction == 0,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected))
                    elif experience !=-1 and niveau ==-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.Domaine == domain_selected))
                        elif prediction_status == 1:
                            query=CV.query.filter(and_(CV.Prediction == 1,CV.ColonneExperience == experience,CV.Domaine == domain_selected))
                        elif prediction_status == 0:
                            query=CV.query.filter(and_(CV.Prediction == 0,CV.ColonneExperience == experience,CV.Domaine == domain_selected))
                    elif experience !=-1 and niveau !=-1:
                        if prediction_status == 'all':
                            query = CV.query.filter(and_(CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected))
                        elif prediction_status == 1:
                            query=CV.query.filter(and_(CV.Prediction == 1,CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected))
                        elif prediction_status == 0:
                            query=CV.query.filter(and_(CV.Prediction == 0,CV.ColonneExperience == experience,CV.ColonneNiveau == niveau,CV.Domaine == domain_selected))
                    logging.info(f"query3: {query}")
                    data = fetch_filtered_data(query)
                    return render_template('Database.html', data=data, domain_selected=domain_selected,niveau=niveau,experience=experience,pagination=pagination)
            elif prediction_status != 'all':
                if prediction_status == 1:
                    query = CV.query.filter(CV.Prediction == 1)
                elif prediction_status == 0:
                    query = CV.query.filter(CV.Prediction == 0)
                else:
                    query=CV.query.limit(20).all()
                logging.info(f"query4: {query}")
                data = fetch_filtered_data(query)
                return render_template('Database.html', data=data, domain_selected=domain_selected,niveau=niveau,experience=experience,pagination=pagination)
            else:
                data=fetch_all_data()
                logging.info(f"data4: {data}")
                return render_template('Database.html', data=data,niveau=niveau,experience=experience,pagination=pagination)
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            raise CustomException(e, sys)
    else:
        try:
            page = request.args.get('page', 1, type=int)
            per_page = 10
            pagination = CV.query.paginate(page=page, per_page=per_page, error_out=False)
            data = pagination.items
            # data=fetch_all_data()
            sort_by = request.args.get('sort_by', 'ID')
            sort_order = request.args.get('sort_order', 'desc')
            if sort_by == 'Nom':
                if sort_order == 'asc':
                    data = fetch_data_sorted_by_column('Nom', asc,page=page, per_page=per_page)
                    sort_order = 'desc'
                else:
                    data = fetch_data_sorted_by_column('Nom', desc,page=page, per_page=per_page)
                    sort_order = 'asc'
            elif sort_by == 'Niveau':
                if sort_order == 'asc':
                    data = fetch_data_sorted_by_column('ColonneNiveau', asc,page=page, per_page=per_page)
                    sort_order = 'desc'
                else:
                    data = fetch_data_sorted_by_column('ColonneNiveau', desc,page=page, per_page=per_page)
                    sort_order = 'asc'
            elif sort_by == 'ColonneExperience':
                if sort_order == 'asc':
                    data = fetch_data_sorted_by_column('ColonneExperience', asc,page=page, per_page=per_page)
                    sort_order = 'desc'
                else:
                    data = fetch_data_sorted_by_column('ColonneExperience', desc,page=page, per_page=per_page)
                    sort_order = 'asc'
            else:
                if sort_order == 'asc':
                    data = fetch_data_sorted_by_column(sort_by, asc,page=page, per_page=per_page)
                else:
                    data = fetch_data_sorted_by_column(sort_by, desc,page=page, per_page=per_page)
            return render_template('Database.html', data=data,pagination=pagination, sort_by=sort_by, sort_order=sort_order)
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            raise CustomException(e, sys)


@app.route('/predictdata',methods=['GET','POST'])
@login_required
def predict_datapoint():
    if request.method == 'GET':
        return render_template("predict.html")
    else:
        data = CustomData(
            Gender=request.form.get('Gender'),
            Domain=request.form.get('Domain'),
            ColonneExperience=request.form.get('ColonneExperience'),
            ColonneNiveau=request.form.get('ColonneNiveau')
        )
        pred_df=data.get_data_as_data_frame()
        print(pred_df)
        predict_pipeline=PredictPipeline()
        results = predict_pipeline.predict(pred_df)
        return render_template('predict.html',results=results[0])


@app.route('/modal', methods=('GET', 'POST'))
@login_required
def modal():
    domain_selected_map = {
                        '1': 'ingenieur qualite',
                        '2': 'economie / gestion',
                        '3': 'technicien specialise',
                        '4': 'ingenieur',
                        '5': 'ingenieur industriel',
                        '6': 'charge de developpementt',
                        '7': 'concepteur/ dessinateur',
                        '8': 'logistique',
                        '9': 'ingenieur mecanique',
                        '10': 'ingenieur process'
                    }
    niveau_selected_map = {
        'BAC ': '',
        'BAC + 1': '1',
        'BAC + 2': '2',
        'BAC + 3': '3',
        'BAC + 4': '4',
        'BAC + 5': '5',
        'BAC + 6': '6',
        'BAC + 7': '7',
        'BAC + 8': '8',
        'BAC + 9': '9',
        'BAC + 10': '10',
        'BAC + 11': '11',
        'BAC + 12': '12',
        'BAC + 13': '13',
        'BAC + 14': '14',
        'BAC + 15': '15',
        'BAC + 16': '16',
        'BAC + 17': '17',
        'BAC + 18': '18',
        'BAC + 19': '19',
        'BAC + 20': '20',
                    }
    experience_selected_map = {
        '0': "Moins d'un an", 
        '1': '1 an',
        '2': '2 ans',
        '3': '3 ans',
        '4': '4 ans',
        '5': '5 ans',
        '6': '6 ans',
        '7': '7 ans',
        '8': '8 ans',
        '9': '9 ans',
        '10': '10 ans',
        '11': '11 ans',
        '12': '12 ans',
        '13': '13 ans',
        '14': '14 ans',
        '15': '15 ans',
        '16': '16 ans',
        '17': '17 ans',
        '18': '18 ans',
        '19': '19 ans',
        '20': '20 ans',
        '21': '21 ans',
        '22': '22 ans',
        '23': '23 ans',
        '24': '24 ans',
        '25': '25 ans',
        '26': '26 ans',
        '27': '27 ans',
        '28': '28 ans',
        '29': '29 ans',
        '30': '30 ans'
    }
    add_cv_form = AddCVForm()
    last_id = last_CV_ID()
    if request.method == 'POST' : 
        ID = add_cv_form.ID.data
        Nom = add_cv_form.Nom.data
        Prenom = add_cv_form.Prenom.data
        Gender = add_cv_form.Gender.data
        Fonction = add_cv_form.Fonction.data
        Domaine = add_cv_form.Domaine.data
        Domaine = domain_selected_map.get(Domaine, '')
        Niveau_label = add_cv_form.Niveau.data
        Niveau_selected = int(niveau_selected_map.get(Niveau_label, ''))
        ColonneExperience = add_cv_form.ColonneExperience.data
        Annee_experience_en_conception = experience_selected_map.get(ColonneExperience, '')
        ColonneExperience = int(ColonneExperience)
        Localisation = add_cv_form.Localisation.data
        Source = add_cv_form.Source.data
        Url = add_cv_form.Url.data
        new = CV(ID=ID, Nom=Nom, Prenom=Prenom, Gender=Gender, Fonction=Fonction, Domaine=Domaine,
                    Niveau=Niveau_label,ColonneNiveau=Niveau_selected, Annee_experience_en_conception=Annee_experience_en_conception,
                      ColonneExperience=ColonneExperience, Localisation=Localisation, Source=Source, Url=Url)
        db.session.add(new)
        db.session.commit()
        flash('CV added successfully', 'success')
        logging.info(f'CV added successfully : {new}')
        return render_template('modal.html',add_cv_form=add_cv_form,last_id=last_id, ID=ID, Nom=Nom, Prenom=Prenom, 
                               Gender=Gender, Fonction=Fonction, Domaine=Domaine, Niveau=Niveau_label,
                                 Annee_experience_en_conception=Annee_experience_en_conception, Localisation=Localisation,
                                   Source=Source, Url=Url)
    return render_template('modal.html',last_id=last_id,add_cv_form=add_cv_form)


@app.route('/candidature', methods=('GET', 'POST'))
def candidature():
    domain_selected_map = {
                        '1': 'ingenieur qualite',
                        '2': 'economie / gestion',
                        '3': 'technicien specialise',
                        '4': 'ingenieur',
                        '5': 'ingenieur industriel',
                        '6': 'charge de developpementt',
                        '7': 'concepteur/ dessinateur',
                        '8': 'logistique',
                        '9': 'ingenieur mecanique',
                        '10': 'ingenieur process'
                    }
    niveau_selected_map = {
        'BAC ': '',
        'BAC + 1': '1',
        'BAC + 2': '2',
        'BAC + 3': '3',
        'BAC + 4': '4',
        'BAC + 5': '5',
        'BAC + 6': '6',
        'BAC + 7': '7',
        'BAC + 8': '8',
        'BAC + 9': '9',
        'BAC + 10': '10',
        'BAC + 11': '11',
        'BAC + 12': '12',
        'BAC + 13': '13',
        'BAC + 14': '14',
        'BAC + 15': '15',
        'BAC + 16': '16',
        'BAC + 17': '17',
        'BAC + 18': '18',
        'BAC + 19': '19',
        'BAC + 20': '20',
                    }
    experience_selected_map = {
        '0': "Moins d'un an", 
        '1': '1 an',
        '2': '2 ans',
        '3': '3 ans',
        '4': '4 ans',
        '5': '5 ans',
        '6': '6 ans',
        '7': '7 ans',
        '8': '8 ans',
        '9': '9 ans',
        '10': '10 ans',
        '11': '11 ans',
        '12': '12 ans',
        '13': '13 ans',
        '14': '14 ans',
        '15': '15 ans',
        '16': '16 ans',
        '17': '17 ans',
        '18': '18 ans',
        '19': '19 ans',
        '20': '20 ans',
        '21': '21 ans',
        '22': '22 ans',
        '23': '23 ans',
        '24': '24 ans',
        '25': '25 ans',
        '26': '26 ans',
        '27': '27 ans',
        '28': '28 ans',
        '29': '29 ans',
        '30': '30 ans'
    }
    add_cv_form = AddCVForm()
    last_id = last_CV_ID()
    if request.method == 'POST' : 
        add_cv_form = AddCVForm(request.form)
        ID = add_cv_form.ID.data
        Nom = add_cv_form.Nom.data
        Prenom = add_cv_form.Prenom.data
        Gender = add_cv_form.Gender.data
        Fonction = add_cv_form.Fonction.data
        Domaine = add_cv_form.Domaine.data
        Domaine = domain_selected_map.get(Domaine, '')
        Niveau_label = add_cv_form.Niveau.data
        Niveau_selected = int(niveau_selected_map.get(Niveau_label, ''))
        ColonneExperience = add_cv_form.ColonneExperience.data
        Annee_experience_en_conception = experience_selected_map.get(ColonneExperience, '')
        ColonneExperience = int(ColonneExperience)
        Localisation = add_cv_form.Localisation.data
        Source = add_cv_form.Source.data
        Url = add_cv_form.Url.data
        new = CV(ID=ID, Nom=Nom, Prenom=Prenom, Gender=Gender, Fonction=Fonction, Domaine=Domaine,
                    Niveau=Niveau_label,ColonneNiveau=Niveau_selected, Annee_experience_en_conception=Annee_experience_en_conception,
                      ColonneExperience=ColonneExperience, Localisation=Localisation, Source=Source, Url=Url)
        db.session.add(new)
        db.session.commit()
        flash('CV added successfully', 'success')
        logging.info(f'CV added successfully : {new}')
        return render_template('candidature.html',add_cv_form=add_cv_form,last_id=last_id, ID=ID, Nom=Nom, Prenom=Prenom, 
                               Gender=Gender, Fonction=Fonction, Domaine=Domaine, Niveau=Niveau_label,
                                 Annee_experience_en_conception=Annee_experience_en_conception, Localisation=Localisation,
                                   Source=Source, Url=Url)
    return render_template('candidature.html',add_cv_form=add_cv_form,last_id=last_id)


@app.route('/modifiercv/<int:id>', methods=('GET', 'POST'))
@login_required
def modifiercv(id):
    cv = CV.query.get_or_404(id)
    mod_cv_form=ModifyCVForm()
    domain_selected_map = {
                        '1': 'ingenieur qualite',
                        '2': 'economie / gestion',
                        '3': 'technicien specialise',
                        '4': 'ingenieur',
                        '5': 'ingenieur industriel',
                        '6': 'charge de developpementt',
                        '7': 'concepteur/ dessinateur',
                        '8': 'logistique',
                        '9': 'ingenieur mecanique',
                        '10': 'ingenieur process'
                    }
    niveau_selected_map = {
        'BAC ': '',
        'BAC + 1': '1',
        'BAC + 2': '2',
        'BAC + 3': '3',
        'BAC + 4': '4',
        'BAC + 5': '5',
        'BAC + 6': '6',
        'BAC + 7': '7',
        'BAC + 8': '8',
        'BAC + 9': '9',
        'BAC + 10': '10',
        'BAC + 11': '11',
        'BAC + 12': '12',
        'BAC + 13': '13',
        'BAC + 14': '14',
        'BAC + 15': '15',
        'BAC + 16': '16',
        'BAC + 17': '17',
        'BAC + 18': '18',
        'BAC + 19': '19',
        'BAC + 20': '20',
                    }
    experience_selected_map = {
         "Moins d'un an":'0', 
         '1 an':'1',
         '2 ans':'2',
         '3 ans':'3',
         '4 ans':'4',
         '5 ans':'5',
         '6 ans':'6',
         '7 ans':'7',
         '8 ans':'8',
         '9 ans':'9',
         '10 ans':'10',
         '11 ans':'11',
         '12 ans':'12',
        '13 ans':'13',
         '14 ans':'14',
         '15 ans':'15',
         '16 ans':'16',
         '17 ans':'17',
         '18 ans':'18',
        '19 ans':'19',
         '20 ans':'20',
         '21 ans':'21',
         '22 ans':'22',
         '23 ans':'23',
         '24 ans':'24',
         '25 ans':'25',
         '26 ans':'26',
         '27 ans':'27',
         '28 ans':'28',
         '29 ans':'29',
         '30 ans':'30'
    }
    
    if request.method == 'POST' :
        ID = mod_cv_form.ID.data
        Nom = mod_cv_form.Nom.data
        Prenom = mod_cv_form.Prenom.data
        Gender = mod_cv_form.Gender.data
        Fonction = mod_cv_form.Fonction.data
        Domaine = mod_cv_form.Domaine.data.replace("é", "e")
        Niveau = mod_cv_form.Niveau.data
        ColonneNiveau = int(niveau_selected_map.get(Niveau, ''))
        Annee_experience_en_conception = mod_cv_form.ColonneExperience.data
        ColonneExperience= experience_selected_map.get(Annee_experience_en_conception, '')
        Localisation = mod_cv_form.Localisation.data
        Source = mod_cv_form.Source.data
        Url = mod_cv_form.Url.data

        cv.Nom=Nom
        cv.Prenom=Prenom
        cv.Gender=Gender
        cv.Fonction=Fonction
        cv.Domaine=Domaine
        cv.Niveau=Niveau
        cv.ColonneNiveau=ColonneNiveau
        cv.Annee_experience_en_conception=Annee_experience_en_conception
        cv.ColonneExperience=ColonneExperience
        cv.Localisation=Localisation
        cv.Source=Source
        cv.Url=Url

        db.session.commit()

        logging.info(f"cv:{cv.Nom , cv.Prenom , cv.Gender , cv.Fonction,cv.Domaine,cv.Niveau,cv.ColonneNiveau,cv.Annee_experience_en_conception,cv.ColonneExperience,cv.Localisation,cv.Source,cv.Url}")
        logging.info(f"les informations ont ete modifiees avec succes. ")
        # return render_template("Database.html")
    return render_template('modifiercv.html',id=id ,cv=cv,mod_cv_form=mod_cv_form)


@app.route('/supprimercv/<int:id>', methods=('GET', 'POST'))
@login_required
def supprimercv(id):
    cv = CV.query.get_or_404(id)
    db.session.delete(cv)
    db.session.commit()
    return render_template('supprimercv.html',id=id)

@app.route('/contactusdb', methods=('GET', 'POST'))
def contactusdb():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = ContactUs.query.order_by(asc(ContactUs.ID)).paginate(page=page, per_page=per_page, error_out=False)
    records = pagination.items 
    return render_template('contactusdb.html', pagination=pagination, records=records)

@app.route('/supprimercontactus/<int:id>', methods=('GET', 'POST'))
@login_required
def supprimercontactus(id):
    contactus = ContactUs.query.get_or_404(id)
    db.session.delete(contactus)
    db.session.commit()
    return redirect(url_for('contactusdb'))







if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)
