from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__,static_folder='frontend/Static',template_folder='frontend/Templates')

client = MongoClient("mongodb://localhost:27017/")
db = client["mybase"]

@app.route('/dashboard')
def home():
    return render_template('Dashboard.html')

@app.route('/abonnees')
def abonnees():
    abonnes = list(db.abonne.find({}, {"_id": 0})) 
    return render_template('Abonnees.html', abonnes=abonnes) 

# @app.route('/addabonnees', methods=['POST'])
# def addAbonnees():
#     return render_template('AddAbonnees.html')
#     data = {
#         "nom": request.form.get("nom"),
#         "prenom": request.form.get("prenom"),
#         "email": request.form.get("email"),
#         "adresse": request.form.get("adresse"),
#         "liste_emprunt_cours": request.form.get("liste_emprunt_cours"),
#         "historique_emprunt": request.form.get("historique_emprunt"),
#         "date_inscription": request.form.get("date_inscription")
#     }

@app.route('/addabonnees', methods=['GET', 'POST'])
def addAbonnees():
    if request.method == 'POST':
        # Collecting data from the form
        data = {
            "nom": request.form.get("nom"),
            "prenom": request.form.get("prenom"),
            "email": request.form.get("email"),
            "adresse": request.form.get("adresse"),
            "liste_emprunt_cours": request.form.get("liste_emprunt_cours"),
            "historique_emprunt": request.form.get("historique_emprunt"),
            "date_inscription": request.form.get("date_inscription")
        }
        
        # Insert data into the MongoDB collection
        db.abonne.insert_one(data)
        
        # Redirect to the abonnes page after successfully adding the abonne
        return redirect(url_for('abonnees'))
    
    # If it's a GET request, just render the form
    return render_template('AddAbonnees.html')

@app.route('/catalogues')
def catalogues():
    return render_template('Catalogue.html')

@app.route('/addcatalogues')
def addCatalogues():
    return render_template('AddCatalogues.html') 

@app.route('/emprunts')
def emprunts():
    return render_template('Emprunts.html') 

@app.route('/addemprunts')
def addEmprunts():
    return render_template('AddEmprunts.html') 
 

if __name__ == "__main__":
    app.run(debug=True)
