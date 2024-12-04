from flask import Flask, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient

app = Flask(__name__,static_folder='frontend/Static',template_folder='frontend/Templates')

client = MongoClient("mongodb://localhost:27017/")
db = client["mybase"]

@app.route('/dashboard')
def home():
    total_abonnes = db.abonne.count_documents({}) 
    total_Catalogues = db.Catalogues.count_documents({}) 
    total_Emprunts = db.Emprunts.count_documents({}) 
    return render_template('Dashboard.html' , total_abonnes=total_abonnes ,  total_Catalogues=total_Catalogues ,  total_Emprunts=total_Emprunts)


# **************************** Abonnees  ****************************** 
@app.route('/abonnees')
def abonnees():
    # Récupérer tous les abonnés
    abonnes = list(db.abonne.find({}, {"_id": 0}))
    print("Abonnés récupérés :", abonnes)

    # Récupérer tous les emprunts
    tous_les_emprunts = list(db.Emprunts.find({}, {"_id": 0}))
    print("Tous les emprunts récupérés :", tous_les_emprunts)

    # Organiser les emprunts par abonné
    emprunts_par_abonne = {}
    for emprunt in tous_les_emprunts:
        abonne_complet = emprunt.get("abonne", "").strip()
        if abonne_complet:
            if abonne_complet not in emprunts_par_abonne:
                emprunts_par_abonne[abonne_complet] = {"en_cours": [], "tous": []}
            # Ajouter les emprunts en cours
            if emprunt.get("statut_emprunt") == "En cours":
                emprunts_par_abonne[abonne_complet]["en_cours"].append({
                    "document_emprunte": emprunt.get("document_emprunte"),
                    "date_emprunt": emprunt.get("date_emprunt"),
                    "date_retour": emprunt.get("date_retour"),
                    "statut_emprunt": emprunt.get("statut_emprunt"),
                })
            # Ajouter tous les emprunts
            emprunts_par_abonne[abonne_complet]["tous"].append({
                "document_emprunte": emprunt.get("document_emprunte"),
                "date_emprunt": emprunt.get("date_emprunt"),
                "date_retour": emprunt.get("date_retour"),
                "statut_emprunt": emprunt.get("statut_emprunt"),
            })

    # Associer les emprunts à chaque abonné
    for abonne in abonnes:
        nom_complet = f"{abonne['nom']} {abonne['prenom']}"
        emprunts = emprunts_par_abonne.get(nom_complet, {"en_cours": [], "tous": []})
        abonne["emprunts_en_cours"] = emprunts["en_cours"]
        abonne["tous_les_emprunts"] = emprunts["tous"]
        print(f"Emprunts pour {nom_complet} - En cours : {abonne['emprunts_en_cours']} - Tous : {abonne['tous_les_emprunts']}")

    # Détails d'un emprunt spécifique (si nécessaire)
    document_emprunte = request.args.get('document_emprunte')
    if document_emprunte:
        emprunt_details = db.Emprunts.find_one({"document_emprunte": document_emprunte})
    else:
        emprunt_details = None

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
    emprunts = list(db.Emprunts.find({}, {"_id": 0})) 
    abonnes = list(db.abonne.find({}, {"_id": 0, "nom": 1, "prenom": 1}))
    documents = list(db.Catalogues.find({}, {"_id": 0, "titre": 1}))
    return render_template('Emprunts.html', emprunts=emprunts, abonnes=abonnes, documents=documents)

@app.route('/delete_emprunt/<document_emprunte>', methods=['POST'])
def delete_emprunt(document_emprunte):
    result = db.Emprunts.delete_one({"document_emprunte": document_emprunte})
    
    if result.deleted_count == 0:
        return "Aucun abonné trouvé avec cet document d'mprunte.", 404

    return redirect(url_for('emprunts'))

@app.route('/update_emprunt/<document_emprunte>', methods=['POST'])
def update_emprunt(document_emprunte):
    abonne = request.form.get('abonne')
    document_emprunte = request.form.get('document_emprunte')
    date_emprunt = request.form.get('date_emprunt')
    date_retour = request.form.get('date_retour')
    statut_emprunt = request.form.get('statut_emprunt')
    emprunt = db.Emprunts.find_one({"document_emprunte": document_emprunte})
    
    if not emprunt:
        return jsonify({"error": "Emprunt introuvable"}), 404

    db.Emprunts.update_one(
        {"document_emprunte": document_emprunte},
        {"$set": {
            "abonne": abonne,
            "document_emprunte": document_emprunte,
            "date_emprunt": date_emprunt,
            "date_retour": date_retour,
            "statut_emprunt": statut_emprunt,
        }}
    )
    return redirect(url_for('emprunts'))  

@app.route('/addemprunts', methods=['GET', 'POST'])
def addEmprunts():
    if request.method == 'POST':
        data = {
            "abonne": request.form.get("abonne"),
            "document_emprunte": request.form.get("document_emprunte"),
            "date_emprunt": request.form.get("date_emprunt"),
            "date_retour": request.form.get("date_retour"),
            "statut_emprunt": request.form.get("statut_emprunt")
        }
        
        db.Emprunts.insert_one(data)
        
        return redirect(url_for('emprunts'))  

    abonnes = list(db.abonne.find({}, {"_id": 0, "nom": 1, "prenom": 1}))
    catalogues = list(db.Catalogues.find({}, {"_id": 0, "titre": 1}))
    return render_template('AddEmprunts.html', abonnes=abonnes , catalogues=catalogues)

 

if __name__ == "__main__":
    app.run(debug=True)
