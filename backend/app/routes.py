from flask import Flask, Blueprint, request, jsonify
from pymongo import MongoClient
from datetime import datetime

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["testbase"]

# Flask App Instance
app = Flask(__name__)

# Define Blueprint
abonne_bp = Blueprint('abonne', __name__)

# Routes
@abonne_bp.route('/abonne', methods=['GET'])
def get_abonnes():
    nom = request.args.get('nom')  # Optional filter for 'nom'
    email = request.args.get('email')  # Optional filter for 'email'

    # Create the query filter
    query_filter = {}
    if nom:
        query_filter['nom'] = nom
    if email:
        query_filter['email'] = email

    # Fetch filtered abonnes from the database
    abonnes = list(db.abonne.find(query_filter, {"_id": 0}))

    return jsonify(abonnes), 200


# Route to update an abonne by email
@abonne_bp.route('/abonne/<email>', methods=['PUT'])
def update_abonne(email):
    data = request.json
    db.abonne.update_one({"email": email}, {"$set": data})
    return jsonify({"message": "Abonné mis à jour avec succès !"}), 200

# Route to delete an abonne by email
@abonne_bp.route('/deleteabonne/<email>', methods=['DELETE'])
def delete_abonne(email):
    db.abonne.delete_one({"email": email})
    return jsonify({"message": "Abonné supprimé avec succès !"}), 200

@abonne_bp.route('/addabonne', methods=['POST'])
def create_abonne():
    # Get the JSON data from the request
    data = request.json

    # Extract the required fields from the JSON data
    nom = data.get('nom')
    prenom = data.get('prenom')
    email = data.get('email')
    adresse = data.get('adresse')
    datedinscription = data.get('date_inscription') 
    historiquedemprunts = data.get('historique_emprunt')
    listedemprunts = data.get('liste_emprunt_cours')

    # Check if required fields are provided
    if not nom or not prenom or not email:
        return jsonify({"error": "Nom, prénom, and email are required fields."}), 400

    # If the 'datedinscription' is provided, convert it to a datetime object (optional)
    if datedinscription:
        try:
            datedinscription = datetime.strptime(datedinscription, '%Y-%m-%d')
        except ValueError:
            return jsonify({"error": "Invalid date format for 'datedinscription'. Use YYYY-MM-DD."}), 400

    # Prepare the data to insert into the database
    abonne_data = {
        "nom": nom,
        "prenom": prenom,
        "email": email,
        "adresse": adresse,
        "date_inscription": datedinscription,
        "historique_emprunt": historiquedemprunts,
        "liste_emprunt_cours": listedemprunts
    }

    # Insert into the MongoDB collection
    db.abonne.insert_one(abonne_data)

    # Return a success message
    return jsonify({"message": "Abonné créé avec succès !"}), 201


# Register the Blueprint with the Flask app
app.register_blueprint(abonne_bp)

if __name__ == "__main__":
    app.run(debug=True)
