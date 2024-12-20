from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

db_name = "testbase"
db = client[db_name]

db.abonne.insert_one({
    "nom": "maissa", 
    "prenom": "daas", 
    "adresse": "test", 
    "email": "test@gmail.com",
    "date_inscription": "19/11/2024", 
    "liste_emprunt_cours": "test", 
    "historique_emprunt": "test"
})

# db.Catalogues.insert_one({
#     "titre": "Test", 
#     "type": "Test", 
#     "auteur": "Test", 
#     "date_publication": "19/11/2024", 
#     "disponibilite": "Test"
# })

# db.Emprunts.insert_one({
#     "abonne": "Test", 
#     "document_emprunte": "test",  
#     "date_emprunt": "19/11/2024", 
#     "date_retour": "19/11/2024", 
#     "statut_emprunt": "Test"
# })

# db.admin.insert_one({
#     "email": "admin@gmail.com", 
#     "password": "admin"
# })

print(f"Database '{db_name}' created successfully with a sample documents.")