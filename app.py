from flask import Flask, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash

app = Flask(__name__,static_folder='frontend/Static',template_folder='frontend/Templates')

client = MongoClient("mongodb://localhost:27017/")
db = client["mybase"]

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = db.admin.find_one({"email": email})        
        
        if user and user['password'] == password:  # Utilisez une comparaison simple si les mots de passe ne sont pas hachés
            return redirect(url_for('home'))

        else:
            error = "Email ou mot de passe invalide"

    return render_template('Login.html', error=error)

@app.route('/dashboard')
def home():
    total_abonnes = db.abonne.count_documents({}) 
    total_Catalogues = db.Catalogues.count_documents({}) 
    total_Emprunts = db.Emprunts.count_documents({}) 
    return render_template('Dashboard.html' , total_abonnes=total_abonnes ,  total_Catalogues=total_Catalogues ,  total_Emprunts=total_Emprunts)


# **************************** Abonnees  ****************************** 

@app.route('/abonnees')
def abonnees():
    abonnes = list(db.abonne.find({}, {"_id": 0}))
    print("Abonnés récupérés :", abonnes)

    tous_les_emprunts = list(db.Emprunts.find({}, {"_id": 0}))
    print("Tous les emprunts récupérés :", tous_les_emprunts)

    emprunts_par_abonne = {}
    for emprunt in tous_les_emprunts:
        abonne = emprunt.get("abonne", {})
        abonne_nom = f"{abonne.get('nom', '').strip()} {abonne.get('prenom', '').strip()}"
        
        if abonne_nom:
            if abonne_nom not in emprunts_par_abonne:
                emprunts_par_abonne[abonne_nom] = {"en_cours": [], "tous": []}

            emprunt_data = {
                "document_emprunte": emprunt.get("document_emprunte"),
                "date_emprunt": emprunt.get("date_emprunt"),
                "date_retour": emprunt.get("date_retour"),
                "statut_emprunt": emprunt.get("statut_emprunt"),
            }
            emprunts_par_abonne[abonne_nom]["tous"].append(emprunt_data)

            if emprunt.get("statut_emprunt") == "En cours":
                emprunts_par_abonne[abonne_nom]["en_cours"].append(emprunt_data)

    for abonne in abonnes:
        nom_complet = f"{abonne['nom']} {abonne['prenom']}"
        emprunts = emprunts_par_abonne.get(nom_complet, {"en_cours": [], "tous": []})
        abonne["emprunts_en_cours"] = emprunts["en_cours"]
        abonne["tous_les_emprunts"] = emprunts["tous"]
        print(f"Emprunts pour {nom_complet} - En cours : {abonne['emprunts_en_cours']} - Tous : {abonne['tous_les_emprunts']}")

    document_emprunte = request.args.get('document_emprunte')
    emprunt_details = db.Emprunts.find_one({"document_emprunte": document_emprunte}) if document_emprunte else None

    return render_template('Abonnees.html', abonnes=abonnes, emprunt_details=emprunt_details)


@app.route('/delete_abonne/<email>', methods=['POST'])
def delete_abonne(email):
    result = db.abonne.delete_one({"email": email})
    
    if result.deleted_count == 0:
        return "Aucun abonné trouvé avec cet email.", 404
    return redirect(url_for('abonnees'))

@app.route('/addabonnees', methods=['GET', 'POST'])
def addAbonnees():
    if request.method == 'POST':
        data = {
            "nom": request.form.get("nom"),
            "prenom": request.form.get("prenom"),
            "email": request.form.get("email"),
            "adresse": request.form.get("adresse"),
            "liste_emprunt_cours": request.form.get("liste_emprunt_cours"),
            "historique_emprunt": request.form.get("historique_emprunt"),
            "date_inscription": request.form.get("date_inscription")
        }
        
        db.abonne.insert_one(data)
        
        return redirect(url_for('abonnees'))    
    return render_template('AddAbonnees.html')

@app.route('/update_abonne/<email>', methods=['POST'])
def update_abonne(email):
    nom = request.form.get('nom')
    prenom = request.form.get('prenom')
    adresse = request.form.get('adresse')
    liste_emprunt_cours = request.form.get('liste_emprunt_cours')
    historique_emprunt = request.form.get('historique_emprunt')
    date_inscription = request.form.get('date_inscription')

    abonne = db.abonne.find_one({"email": email})
    
    if not abonne:
        return jsonify({"error": "Abonné introuvable"}), 404

    db.abonne.update_one(
        {"email": email},
        {"$set": {
            "nom": nom,
            "prenom": prenom,
            "adresse": adresse,
            "liste_emprunt_cours": liste_emprunt_cours,
            "historique_emprunt": historique_emprunt,
            "date_inscription": date_inscription
        }}
    )

    return redirect(url_for('abonnees'))  


# **************************** Catalogues  ******************************

@app.route('/catalogues')  
def catalogues():
    catalogues = list(db.Catalogues.find({}, {"_id": 0})) 
    return render_template('Catalogue.html', catalogues=catalogues)

@app.route('/delete_catalogue/<titre>', methods=['POST'])
def delete_catalogue(titre):
    result = db.Catalogues.delete_one({"titre": titre})
    
    if result.deleted_count == 0:
        return "Aucun abonné trouvé avec cet titre.", 404
    return redirect(url_for('catalogues'))

@app.route('/update_catalogue/<titre>', methods=['POST'])
def update_catalogue(titre):
    titre = request.form.get('titre')
    type = request.form.get('type')
    auteur = request.form.get('auteur')
    date_publication = request.form.get('date_publication')
    disponibilite = request.form.get('disponibilite')

    catalogue = db.Catalogues.find_one({"titre": titre})
    
    if not catalogue:
        return jsonify({"error": "Catalogue introuvable"}), 404

    db.Catalogues.update_one(
        {"titre": titre},
        {"$set": {
            "titre": titre,
            "type": type,
            "auteur": auteur,
            "date_publication": date_publication,
            "disponibilite": disponibilite,
        }}
    )
    return redirect(url_for('catalogues'))  

@app.route('/addcatalogues', methods=['GET', 'POST'])
def addCatalogues():
    if request.method == 'POST':
        data = {
            "titre": request.form.get("titre"),
            "type": request.form.get("type"),
            "auteur": request.form.get("auteur"),
            "date_publication": request.form.get("date_publication"),
            "disponibilite": request.form.get("disponibilite")
        }
        
        db.Catalogues.insert_one(data)
        
        return redirect(url_for('catalogues'))    
    return render_template('AddCatatogues.html')


# **************************** Emprunts  ******************************

@app.route('/emprunts')
def emprunts():
    date_filter = request.args.get('date_filter', None)

    emprunts = list(db.Emprunts.find({}, {"_id": 0}))
    emprunts = [e for e in emprunts if 'abonne' in e or 'document_emprunte' in e]
    
    if date_filter == 'asc':
        emprunts.sort(key=lambda x: x.get('date_emprunt', ''))
    elif date_filter == 'desc':
        emprunts.sort(key=lambda x: x.get('date_emprunt', ''), reverse=True)

    retour_filter = request.args.get('retour_filter', None)
    if retour_filter == 'asc':
        emprunts.sort(key=lambda x: x.get('date_retour_prevue', ''))
    elif retour_filter == 'desc':
        emprunts.sort(key=lambda x: x.get('date_retour_prevue', ''), reverse=True)

    # Récupérer les abonnés et les catalogues
    Abonne = list(db.abonne.find({}, {"_id": 1, "nom": 1, "prenom": 1}))
    Catalogue = list(db.Catalogues.find({}, {"_id": 1, "titre": 1, "disponibilite": 1}))
    
    # Ajouter les informations de document_emprunte si elles ne sont pas complètes
    for emprunt in emprunts:
        if 'document_emprunte' in emprunt:
            doc_id = emprunt['document_emprunte']['_id']
            document = db.Catalogues.find_one({"_id": doc_id}, {"_id": 1, "titre": 1})
            if document:
                emprunt['document_emprunte'] = document

    # Retourner le rendu du modèle avec les données nécessaires
    return render_template(
        'Emprunts.html', 
        emprunts=emprunts, 
        Abonnes=Abonne, 
        Catalogues=Catalogue,
        selected_filter=date_filter,
        selected_retour_filter=retour_filter
    )

@app.route('/delete_emprunt/<code_emprunt>', methods=['POST'])
def delete_emprunt(code_emprunt):
    result = db.Emprunts.delete_one({"code_emprunt": code_emprunt})
    
    if result.deleted_count == 0:
        return "Aucun abonné trouvé avec cet document d'mprunte.", 404

    return redirect(url_for('emprunts'))

from bson import ObjectId

@app.route('/update_emprunt/<code_emprunt>', methods=['POST'])
def update_emprunt(code_emprunt):
    abonne_id = request.form.get("abonne")
    print(f"Received abonne_id: {abonne_id}")
    document_id = request.form.get('document_emprunte')
    date_emprunt = request.form.get('date_emprunt')
    date_retour = request.form.get('date_retour')
    statut_emprunt = request.form.get('statut_emprunt')

    print(f"Received code_emprunt: {code_emprunt}, abonne_id: {abonne_id}, document_id: {document_id}")

    if not abonne_id or not ObjectId.is_valid(abonne_id):
        return jsonify({"error": "Invalid or missing abonne ID"}), 400
    if not document_id or not ObjectId.is_valid(document_id):
        return jsonify({"error": "Invalid or missing document ID"}), 400

    emprunt = db.Emprunts.find_one({"code_emprunt": code_emprunt})
    print(f"Found emprunt: {emprunt}")

    if not emprunt:
        return jsonify({"error": "Emprunt introuvable"}), 404

    abonne = db.abonne.find_one({"_id": ObjectId(abonne_id)})
    document = db.Catalogues.find_one({"_id": ObjectId(document_id)})

    if not abonne:
        return jsonify({"error": "Abonne introuvable"}), 404
    if not document:
        return jsonify({"error": "Document introuvable"}), 404

    db.Emprunts.update_one(
        {"code_emprunt": code_emprunt},
        {"$set": {
            "abonne": {
                "_id": abonne["_id"],
                "nom": abonne["nom"], 
                "prenom": abonne["prenom"],  
            },
            "document_emprunte": {
                "_id": document["_id"],
                "titre": document["titre"]
            },          
            "date_emprunt": date_emprunt,
            "date_retour": date_retour,
            "statut_emprunt": statut_emprunt,
            "code_emprunt": code_emprunt
        }}
    )
    return redirect(url_for('emprunts'))


@app.route('/addemprunts', methods=['GET', 'POST'])
def addemprunts():
    if request.method == 'POST':
        code_emprunt = request.form.get("code_emprunt")
        abonne_id = request.form.get("abonne")
        document_id = request.form.get("document_emprunte")
        date_emprunt = request.form.get("date_emprunt")
        date_retour = request.form.get("date_retour")
        statut_emprunt = request.form.get("statut_emprunt")
        
        abonne = db.abonne.find_one({"_id": ObjectId(abonne_id)})
        document = db.Catalogues.find_one({"_id": ObjectId(document_id)})
            
        db.Emprunts.insert_one({
            "abonne": {
                "_id": abonne["_id"],
                "nom": abonne["nom"], 
                "prenom": abonne["prenom"],  
            },
            "document_emprunte": {
                "_id": document["_id"],
                "titre": document["titre"]
            },
            "date_emprunt": date_emprunt,
            "date_retour": date_retour,
            "statut_emprunt": statut_emprunt,
            "code_emprunt": code_emprunt
        })
        return redirect(url_for('emprunts'))

    abonnes = list(db.abonne.find({}, {"_id": 1, "nom": 1, "prenom": 1}))
    catalogues = list(db.Catalogues.find({}, {"_id": 1, "titre": 1, "disponibilite": 1}))

    return render_template('AddEmprunts.html', abonnes=abonnes, catalogues=catalogues)


if __name__ == "__main__":
    app.run(debug=True)
