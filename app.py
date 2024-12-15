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
        
        if user and user['password'] == password:  
            return redirect(url_for('home'))

        else:
            error = "Email ou mot de passe invalide"

    return render_template('Login.html', error=error)


# **************************** dashboard  ****************************** 

from collections import defaultdict
from datetime import datetime

@app.route('/dashboard')
def home():
    # Total Abonnés, Catalogues, Emprunts
    total_abonnes = db.abonne.count_documents({}) 
    total_Catalogues = db.Catalogues.count_documents({}) 
    total_Emprunts = db.Emprunts.count_documents({}) 

    # Calcul des abonnés par mois
    abonnés_mois = defaultdict(int)
    abonnés = db.abonne.find()
    for abonne in abonnés:
        mois_inscription = abonne.get('date_inscription')
        if mois_inscription:
            mois = datetime.strptime(mois_inscription, "%Y-%m-%d").month
            abonnés_mois[mois] += 1
    abonnés_mois = [abonnés_mois.get(i, 0) for i in range(1, 13)]  # Remplir avec 0 pour les mois non présents

    # Emprunts par statut
    emprunts_par_statut = defaultdict(int)
    emprunts = db.Emprunts.find()
    for emprunt in emprunts:
        statut = emprunt.get('statut_emprunt')
        if statut:
            emprunts_par_statut[statut] += 1
    # Re-organizing status data for pie/bar chart
    emprunts_par_statut = dict(emprunts_par_statut)

    # Calcul des livres les plus empruntés
    livres_empruntés = defaultdict(int)

    # Recherche des emprunts
    emprunts = db.Emprunts.find()
    for emprunt in emprunts:
        titre_livre = emprunt.get('document_emprunte', {}).get('titre')
        if titre_livre:
            livres_empruntés[titre_livre] += 1


    livres_les_plus_empruntes = sorted(livres_empruntés.items(), key=lambda x: x[1], reverse=True)

    top_livres = livres_les_plus_empruntes[:5]
    titres_livres = [livre[0] for livre in top_livres]
    emprunts_livres = [livre[1] for livre in top_livres]

    # Données des abonnés
    abonnés = db.abonne.find()

    # Liste pour stocker les résultats
    emprunts_par_abonne = []

    for abonne in abonnés:
        # Récupérer les emprunts de chaque abonné
        emprunts_count = db.Emprunts.count_documents({"abonne._id": abonne["_id"]})

        # Ajouter le résultat à la liste
        emprunts_par_abonne.append({
            'nom': abonne.get('nom', 'Nom Inconnu'),
            'emprunts_count': emprunts_count
        })

    # Affichage des résultats
    print(emprunts_par_abonne)

    livres_disponibles = defaultdict(int)  # Utilisation de int pour stocker des quantités disponibles
    for livre in db.Catalogues.find():
        titre_livre = livre.get('titre')
        disponibilite = livre.get('disponibilite', 'indisponible')  # Valeur par défaut si absente
        if disponibilite == "disponible":
            livres_disponibles[titre_livre] = 1  # Quantité disponible
        else:
            livres_disponibles[titre_livre] = 0  # Indisponible, donc quantité 0

    # Affichage de la variable livres_disponibles dans le terminal
    print("livres_disponibles:", livres_disponibles)
    print("emprunts_par_abonne:", emprunts_par_abonne)
    print("Titres des livres:", titres_livres)
    print("Emprunts des livres:", emprunts_livres)

    return render_template('Dashboard.html', total_abonnes=total_abonnes, 
                           total_Catalogues=total_Catalogues, total_Emprunts=total_Emprunts,
                           abonnés_mois=abonnés_mois, emprunts_par_statut=emprunts_par_statut,
                           titres_livres=titres_livres, emprunts_livres=emprunts_livres,
                           abonnés=emprunts_par_abonne, livres_disponibles=livres_disponibles)


# **************************** Abonnees  ****************************** 

@app.route('/abonnees')
def abonnees():
    abonnes = list(db.abonne.find({}, {"_id": 0}))
    print("Abonnés récupérés :", abonnes)

    tous_les_emprunts = list(db.Emprunts.find({}, {"_id": 0}))
    print("Tous les emprunts récupérés :", tous_les_emprunts)

    Inscription_filter = request.args.get('Inscription_filter', None)

    print("Inscription_filter:", Inscription_filter)
    if Inscription_filter == 'asc':
        abonnes.sort(key=lambda x: x.get('date_inscription', ''))
    elif Inscription_filter == 'desc':
        abonnes.sort(key=lambda x: x.get('date_inscription', ''), reverse=True)

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

    return render_template('Abonnees.html', abonnes=abonnes, emprunt_details=emprunt_details, selected_Inscription_filter=Inscription_filter)


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

    publication_filter = request.args.get('publication_filter', None)
    disponible_filter = request.args.get('disponible_filter', None)

    if disponible_filter:
        if disponible_filter == 'disponible':
            # Filtrer les catalogues disponibles (exemple : ceux qui ne sont pas en retard)
            catalogues = [doc for doc in catalogues if doc.get('disponibilite') == 'disponible']
        elif disponible_filter == 'indisponible':
            # Filtrer les catalogues indisponibles (en retard)
            catalogues = [doc for doc in catalogues if doc.get('disponibilite') == 'indisponible']
    
    print("publication_filter:", publication_filter)
    if publication_filter == 'asc':
        catalogues.sort(key=lambda x: x.get('date_publication', ''))
    elif publication_filter == 'desc':
        catalogues.sort(key=lambda x: x.get('date_publication', ''), reverse=True)

    
    return render_template('Catalogue.html', catalogues=catalogues, selected_publication_filter=publication_filter,selected_disponible=disponible_filter)

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
    retour_filter = request.args.get('retour_filter', None)
    statut_filter = request.args.get('statut_filter')
    abonne_filter = request.args.get('abonne_filter', '').strip().lower() 
    document_filter = request.args.get('document_filter', '').strip().lower()

    emprunts = list(db.Emprunts.find({}, {"_id": 0}))
    emprunts = [e for e in emprunts if 'abonne' in e or 'document_emprunte' in e]
    
    if abonne_filter:
        emprunts = [e for e in emprunts if e.get('abonne', {}).get('nom', '').strip().lower().find(abonne_filter) != -1 or e.get('abonne', {}).get('prenom', '').strip().lower().find(abonne_filter) != -1]
    
    if document_filter:
        emprunts = [e for e in emprunts if e.get('document_emprunte', {}).get('titre', '').strip().lower().find(document_filter) != -1]


    print("date_filter:", retour_filter)
    if date_filter == 'asc':
        emprunts.sort(key=lambda x: x.get('date_emprunt', ''))
    elif date_filter == 'desc':
        emprunts.sort(key=lambda x: x.get('date_emprunt', ''), reverse=True)

    print("retour_filter:", retour_filter)
    if retour_filter == 'asc':
        emprunts.sort(key=lambda x: x.get('date_retour', ''))
    elif retour_filter == 'desc':
        emprunts.sort(key=lambda x: x.get('date_retour', ''), reverse=True)

    if statut_filter:
        statut_filter = statut_filter.strip().lower()
        emprunts = [e for e in emprunts if e.get('statut_emprunt', '').strip().lower() == statut_filter]


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
        selected_retour_filter=retour_filter,
        selected_statut=statut_filter,
        selected_abonne_filter=abonne_filter,  
        selected_document_filter=document_filter 
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

    if date_retour:
        try:
            date_retour_obj = datetime.strptime(date_retour, "%Y-%m-%d")  # Formatez la date selon votre format
        except ValueError:
            return jsonify({"error": "Invalid date format"}), 400
    else:
        date_retour_obj = None

    # Comparer la date de retour avec la date actuelle
    current_date = datetime.now()

    # Si la date de retour est dans le passé, mettre à jour le statut
    if date_retour_obj and date_retour_obj < current_date:
        statut_emprunt = "Retardé"
    else:
        statut_emprunt = "En cours"

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
