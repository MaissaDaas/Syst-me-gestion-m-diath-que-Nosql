from flask import Flask, render_template

app = Flask(__name__,static_folder='frontend/Static',template_folder='frontend/Templates')

@app.route('/dashboard')
def home():
    return render_template('Dashboard.html')

@app.route('/abonnees')
def abonnees():
    return render_template('Abonnees.html') 

@app.route('/addabonnees')
def addAbonnees():
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
