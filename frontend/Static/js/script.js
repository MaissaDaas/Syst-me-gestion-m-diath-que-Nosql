const themeToggler = document.querySelector('.theme-toggler');

// *********Theme toggle
themeToggler.addEventListener('click', () => {
    document.body.classList.toggle('dark-theme-variables');
    themeToggler.querySelector('span:nth-child(1)').classList.toggle('active');
    themeToggler.querySelector('span:nth-child(2)').classList.toggle('active');
});

document.addEventListener('DOMContentLoaded', function () {
    const dateInput = document.getElementById('currentDate'); 
    const today = new Date();
    const yyyy = today.getFullYear();
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const dd = String(today.getDate()).padStart(2, '0');
    const formattedDate = `${yyyy}-${mm}-${dd}`;
    dateInput.value = formattedDate;
});

function closeAllPopups() {
    document.querySelectorAll('.popup').forEach(popup => {
        popup.classList.remove('active');
    });
}

document.querySelectorAll('.more-icon').forEach(icon => {
    icon.addEventListener('click', function (e) {
        e.stopPropagation();
        closeAllPopups();
        const popup = this.nextElementSibling;
        popup.classList.add('active');
    });
});

document.addEventListener('click', closeAllPopups);
document.addEventListener('DOMContentLoaded', function () {
    function closeAllPopups() {
        document.querySelectorAll('.popup').forEach(popup => {
            popup.classList.remove('active');
        });
        document.querySelectorAll('.modal-details').forEach(modal => {
            modal.style.display = "none"; // Ferme les modals
        });
    }

    const editButtons = document.querySelectorAll('.edit-button');
    editButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();  

            const email = this.getAttribute('data-email'); 
            const modal = document.getElementById('modal_' + email);  
            
            if (modal) {
                modal.style.display = "block";
            }
            closeAllPopups(); 
        });
    });


    const closeButtons = document.querySelectorAll('.close');
    closeButtons.forEach(button => {
        button.addEventListener('click', function () {
            const modal = this.closest('.modal');
            modal.style.display = "none";  
        });
    });


    window.addEventListener('click', function (event) {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            if (event.target === modal) {
                modal.style.display = "none"; 
            }
        });
    });
});


/****** search ***** */
document.getElementById("searchInput").addEventListener("input", function () {
    const searchValue = this.value.toLowerCase(); // Récupérer la valeur de recherche en minuscule
    const tableRows = document.querySelectorAll("#abonnesTable tbody tr"); // Sélectionner toutes les lignes du tableau

    tableRows.forEach((row) => {
        const cells = row.querySelectorAll("td"); // Récupérer toutes les cellules d'une ligne
        let rowText = "";

        // Concaténer le contenu des cellules pour chaque ligne
        cells.forEach((cell) => {
            rowText += cell.textContent.toLowerCase();
        });

        // Vérifier si la ligne contient le texte recherché
        if (rowText.includes(searchValue)) {
            row.style.display = ""; // Afficher la ligne
        } else {
            row.style.display = "none"; // Masquer la ligne
        }
    });
});





