import sys
from forms import ContactForm, ModifyCVForm, SearchForm,AddCVForm
from src.exception import CustomException
from src.logger import logging
from flask import Flask,request,render_template, flash ,redirect, url_for
import pandas as pd
from src.pipeline.predict_pipeline import  PredictPipeline
from flask_mysqldb import MySQL
from models import ContactUs, Users, db, CV, last_CV_ID, render_as_tuple, render_as_tuple_custom
from sqlalchemy import or_ , and_,asc, desc
from flask_login import login_user,LoginManager,login_required,logout_user # type: ignore
from werkzeug.security import  check_password_hash
from flask_bcrypt import Bcrypt ,check_password_hash # type: ignore
import bcrypt # type: ignore

application = Flask(__name__)
app = application
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://serverkaouthar:Kaouthar2001@serverkaouthar.database.windows.net/serverkaouthar?driver=ODBC+Driver+17+for+SQL+Server'
db.init_app(app)

bcrypt = Bcrypt(app) 

def fetch_filtered_data(query):
    fetchdata = render_as_tuple_custom(query)
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
            'Prediction': row[9], 
            'ColonneExperience': row[10],
            'Localisation': row[11],
            'Source': row[12],
            'Url': row[13]
        }
        pred_df = pd.DataFrame([data_row], columns=['ColonneNiveau', 'ColonneExperience', 'Gender', 'Domain'])
        pred_df['Domain'] = pred_df['Domain'].replace({'Ingénieur Industriel': 'ingénieur industriel', 'ingénieu qualité': 'ingenieur qualite'})
        pred_df['Domain'] = pred_df['Domain'].str.replace('é', 'e')
        predict_pipeline = PredictPipeline()
        prediction = predict_pipeline.predict(pred_df)[0]
        data_row['Prediction'] = prediction  
        # Update the Prediction column
        cv_instance = CV.query.filter_by(ID=row[0]).first()
        if cv_instance:
            cv_instance.Prediction = prediction
            db.session.commit()  
        else:
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

@app.route('/')
def index():
    return redirect(url_for('home'))

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

login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

login_manager.login_message = "Veuillez vous connecter pour accéder à cette page."
login_manager.login_message_category = "info" 

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
            flash("Nom d'uilisateur incorrect. Veuillez réessayer à nouveau.", 'danger')
            return redirect(url_for('login'))
        if not bcrypt.check_password_hash(user.password, password):
            flash('Mot de passe incorrect . Veuillez réessayer à nouveau.', 'danger')
            return redirect(url_for('login'))
        login_user(user)
        flash('Bienvenue , ' + user.username + '!', 'success')
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
            flash('Utilisateur existant.', 'danger')
            return redirect(url_for('register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = Users(email=email, username=username, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        flash('Enregistrement avec succès.Vous pouvez vous connecter', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')  

def fetch_data_sorted_by_column(column_name, order,page, per_page):
    if column_name == 'Nom':
        query = CV.query.order_by(order(CV.Nom)).paginate(page=page, per_page=per_page, error_out=False)
    elif column_name == 'ColonneNiveau':
        query = CV.query.order_by(order(CV.ColonneNiveau)).paginate(page=page, per_page=per_page, error_out=False)
    elif column_name == 'ColonneExperience':
        query = CV.query.order_by(order(CV.ColonneExperience)).paginate(page=page, per_page=per_page, error_out=False)
    else:
        query = CV.query.order_by(order(CV.ID)).paginate(page=page, per_page=per_page, error_out=False)
    fetchdata = render_as_tuple_custom(query)
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
        pred_df['Domain'] = pred_df['Domain'].replace({'Ingénieur Industriel': 'ingénieur industriel', 'ingénieu qualité': 'ingenieur qualite'})
        pred_df['Domain'] = pred_df['Domain'].str.replace('é', 'e')
        predict_pipeline = PredictPipeline()
        prediction = predict_pipeline.predict(pred_df)[0]
        data_row['Prediction'] = prediction  

        cv_instance = CV.query.filter_by(ID=row[0]).first()
        if cv_instance:
            cv_instance.Prediction = prediction
            db.session.commit()  
        else:
            pass
        data_row['Domain'] = data_row['Domain'].replace('ingénieur', 'Ingénieur').replace('ingénieu qualité', 'Ingénieur Qualité').replace('économie / gestion', 'Economie et Gestion').replace('technicien spécialisé', 'Technicien Spécialisé').replace('ingénieur process', 'Ingénieur Process').replace('ingénieur industriel', 'Ingénieur Industriel').replace('Ingénieur industriel', 'Ingénieur Industriel').replace('chargé de développement', 'Chargé de Développement').replace('concepteur/ dessinateur', 'Concepteur ou Dessinateur').replace('logistique', 'Logistique').replace('ingénieur mécanique', 'Ingénieur Mécanique')
        data.append(data_row)

    return data

@app.route('/database', methods=['GET', 'POST'])
@login_required
def database():
    form = SearchForm()
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = CV.query.order_by(CV.ID).paginate(page=page, per_page=per_page, error_out=False)
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
                    flash('Pas de résultats pour votre recherche.', 'primary')
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
            pagination = CV.query.order_by(CV.ID).paginate(page=page, per_page=per_page, error_out=False)
            data = pagination.items
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


@app.route('/modal', methods=('GET', 'POST'))
@login_required
def modal():
    domain_selected_map = {
                        '1': 'ingénieu qualité',
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
        'BAC ': '0',
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
        if not Source:
            Source = "Site Web BENGY.H"
        Url = add_cv_form.Url.data
        Prediction=2
        new = CV(ID=ID, Nom=Nom, Prenom=Prenom, Gender=Gender, Fonction=Fonction, Domaine=Domaine,
                    Niveau=Niveau_label,ColonneNiveau=Niveau_selected, Annee_experience_en_conception=Annee_experience_en_conception,
                      ColonneExperience=ColonneExperience, Localisation=Localisation, Source=Source, Url=Url,Prediction=Prediction)
        db.session.add(new)
        db.session.commit()
        flash('CV added successfully', 'success')
        logging.info(f'CV added successfully : {new}')
        logging.info(f'ID: {new.ID} , Prenom: {new.Prenom}, Nom: {new.Nom}, Gender: {new.Gender}, Fonction: {new.Fonction}, Domaine: {new.Domaine}, Niveau: {new.Niveau}, ColonneNiveau: {new.ColonneNiveau}, Annee_experience_en_conception: {new.Annee_experience_en_conception}, ColonneExperience: {new.ColonneExperience}, Prediction: {new.Prediction}')
        return render_template('modal.html',add_cv_form=add_cv_form,last_id=last_id, ID=ID, Nom=Nom, Prenom=Prenom, 
                               Gender=Gender, Fonction=Fonction, Domaine=Domaine, Niveau=Niveau_label,
                                 Annee_experience_en_conception=Annee_experience_en_conception, Localisation=Localisation,
                                   Source=Source, Url=Url)
    return render_template('modal.html',last_id=last_id,add_cv_form=add_cv_form)


@app.route('/candidature', methods=('GET', 'POST'))
def candidature():
    domain_selected_map = {
                        '1': 'ingénieu qualité',
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
        'BAC ': '0',
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
        Source = "Site Web BENGY.H"
        Url = add_cv_form.Url.data
        if not Url: 
            Url = " "
        Prediction=2
        new = CV(ID=ID, Nom=Nom, Prenom=Prenom, Gender=Gender, Fonction=Fonction, Domaine=Domaine,
                    Niveau=Niveau_label,ColonneNiveau=Niveau_selected, Annee_experience_en_conception=Annee_experience_en_conception,
                      ColonneExperience=ColonneExperience, Localisation=Localisation, Source=Source, Url=Url,Prediction=Prediction)
        db.session.add(new)
        db.session.commit()
        flash('CV added successfully', 'success')
        logging.info(f'CV added successfully : {new}')
        logging.info(f'ID: {new.ID} , Prenom: {new.Prenom}, Nom: {new.Nom}, Gender: {new.Gender}, Fonction: {new.Fonction}, Domaine: {new.Domaine}, Niveau: {new.Niveau}, ColonneNiveau: {new.ColonneNiveau}, Annee_experience_en_conception: {new.Annee_experience_en_conception}, ColonneExperience: {new.ColonneExperience}, Prediction: {new.Prediction}')
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
        'BAC ': '0',
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

@app.route('/profile/<int:id>', methods=('GET', 'POST'))
@login_required
def profile(id):
    user = Users.query.get_or_404(id)
    return render_template('profile.html',user=user)

@app.route('/modifierprofile/<int:id>', methods=('GET', 'POST'))
@login_required
def modifierprofile(id):
    user = Users.query.get_or_404(id)
    if request.method == 'POST':
        email = request.form.get('email')
        oldpassword = request.form.get('oldpassword')
        newpassword = request.form.get('newpassword')
        if not check_password_hash(user.password, oldpassword):
            flash('Mot de passe incorrect.', 'danger')
            return redirect(url_for('modifierprofile', id=id))
        else:
            hashed_newpassword = bcrypt.generate_password_hash(newpassword).decode('utf-8')
            user.email=email
            user.password=hashed_newpassword
            db.session.commit()
            flash('Modification avec succès.', 'success')

        return redirect(url_for('modifierprofile', id=id))

    return render_template('modifierprofile.html',user=user)  

@app.route('/delete_profile/<int:id>', methods=('GET', 'POST'))
@login_required
def delete_profile(id):
    user = Users.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect( url_for('home'))


if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)
