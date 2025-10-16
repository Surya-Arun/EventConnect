const searchInput = document.getElementById('searchBar');
const cards = document.querySelectorAll('.cards .card');

searchInput.addEventListener('input', function() {
    const filter = this.value.toLowerCase(); // lowercase for case-insensitive

    cards.forEach(card => {
        const title = card.querySelector('.hd').textContent.toLowerCase();
        const dateP = card.querySelector('.datte').textContent.toLowerCase(); 

        if (title.includes(filter) || dateP.includes(filter)) {
            card.style.display = 'inline-block';
        } else {
            card.style.display = 'none'; 
        }
    });
});
