from flask import Blueprint, request, jsonify
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["testbase"]

abonne_bp = Blueprint('abonne', __name__)


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
