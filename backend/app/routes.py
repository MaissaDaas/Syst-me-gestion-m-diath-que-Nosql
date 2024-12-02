from flask import Blueprint, request, jsonify
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["mybase"]

abonne_bp = Blueprint('abonne', __name__)

# @abonne_bp.route('/addabonnees', methods=['POST'])
# def create_abonne():
#     data = {
#         "nom": request.form.get("nom"),
#         "prenom": request.form.get("prenom"),
#         "email": request.form.get("email"),
#         "adresse": request.form.get("adresse"),
#         "liste_emprunt_cours": request.form.get("liste_emprunt_cours"),
#         "historique_emprunt": request.form.get("historique_emprunt"),
#         "date_inscription": request.form.get("date_inscription")
#     }

#     if not data["email"]:
#         return jsonify({"error": "L'email est requis."}), 400

#     existing_abonne = db.abonne.find_one({"email": data["email"]})
#     if existing_abonne:
#         return jsonify({"error": "Un abonné avec cet email existe déjà."}), 409

#     db.abonne.insert_one(data)
#     return redirect(url_for('abonnees'))  


@abonne_bp.route('/abonne', methods=['GET'])
def get_abonnes():
    abonnes = list(db.abonne.find({}, {"_id": 0}))
    return jsonify(abonnes), 200

@abonne_bp.route('/emprunt', methods=['GET'])
def get_Emprunts():
    Emprunts = list(db.Emprunts.find({}, {"_id": 0}))
    return jsonify(Emprunts), 200

@abonne_bp.route('/abonne/<email>', methods=['PUT'])
def update_abonne(email):
    data = request.json 
    if not data:
        return jsonify({"error": "Aucune donnée fournie"}), 400

    result = db.abonne.update_one({"email": email}, {"$set": data})

    if result.matched_count == 0:
        return jsonify({"error": f"Aucun abonné trouvé avec lemail '{email}'"}), 404

    return jsonify({"message": "Abonné mis à jour avec succès !"}), 200

@abonne_bp.route('/abonne/<email>', methods=['DELETE'])
def delete_abonne(email):
    db.abonne.delete_one({"email": email})
    return jsonify({"message": "Abonné supprimé avec succès !"}), 200



@abonne_bp.route('/abonne/delete', methods=['DELETE'])
def delete_all():
    try:
        # Suppression de tous les abonnés dans la collection
        result = db.abonne.delete_many({})

        # Vérifier si des abonnés ont été supprimés
        if result.deleted_count > 0:
            return jsonify({"message": f"{result.deleted_count} abonnés supprimés avec succès !"}), 200
        else:
            return jsonify({"message": "Aucun abonné trouvé à supprimer."}), 404

    except Exception as e:
        return jsonify({"error": f"Erreur lors de la suppression des abonnés: {str(e)}"}), 500