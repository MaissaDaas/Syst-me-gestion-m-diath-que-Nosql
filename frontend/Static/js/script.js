const themeToggler = document.querySelector('.theme-toggler');

// *********Theme toggle
themeToggler.addEventListener('click', () => {
    document.body.classList.toggle('dark-theme-variables');
    themeToggler.querySelector('span:nth-child(1)').classList.toggle('active');
    themeToggler.querySelector('span:nth-child(2)').classList.toggle('active');
});

document.addEventListener('DOMContentLoaded', function () {
    const dateInput = document.getElementById('currentDate'); // Assurez-vous que l'élément avec l'ID "currentDate" existe dans votre HTML
    const today = new Date();
    const yyyy = today.getFullYear();
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const dd = String(today.getDate()).padStart(2, '0');
    const formattedDate = `${yyyy}-${mm}-${dd}`;
    dateInput.value = formattedDate;
});
