// Navbar scroll effect
window.addEventListener('scroll', () => {
    document.querySelector('.navbar').classList.toggle('scrolled', window.scrollY > 20);
});

// Hamburger menu
const hamburger = document.getElementById('hamburger');
const navLinks = document.querySelector('.nav-links');
if (hamburger) {
    hamburger.addEventListener('click', () => {
        navLinks.classList.toggle('open');
    });
}

// Auto-dismiss flash messages
document.querySelectorAll('.flash').forEach(el => {
    setTimeout(() => el.remove(), 5000);
});

// Price calculator for booking page
const personsInput = document.getElementById('num_persons');
const totalDisplay = document.getElementById('total_price');
const pricePerPerson = window.PRICE_PER_PERSON;

if (personsInput && pricePerPerson) {
    personsInput.addEventListener('input', () => {
        const total = parseInt(personsInput.value || 1) * pricePerPerson;
        if (totalDisplay) {
            totalDisplay.textContent = '₹' + total.toLocaleString('en-IN');
        }
    });
}
