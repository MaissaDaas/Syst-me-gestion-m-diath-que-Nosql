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
