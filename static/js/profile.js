const sideMenu = document.querySelector('aside');
const menuBtn = document.getElementById('menu-btn');
const closeBtn = document.getElementById('close-btn');
const darkMode = document.querySelector('.dark-mode');

// Function to toggle dark mode
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode-variables');
    darkMode.querySelector('span:nth-child(1)').classList.toggle('active');
    darkMode.querySelector('span:nth-child(2)').classList.toggle('active');

    // Store the theme preference in local storage
    const isDarkMode = document.body.classList.contains('dark-mode-variables');
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
}

// Function to apply the stored theme preference
function applyStoredThemePreference() {
    const storedTheme = localStorage.getItem('theme');
    if (storedTheme === 'dark') {
        toggleDarkMode(); // Apply dark mode if stored preference is dark
    }
}

// Event listeners
menuBtn.addEventListener('click', () => {
    sideMenu.style.display = 'block';
});

closeBtn.addEventListener('click', () => {
    sideMenu.style.display = 'none';
});

darkMode.addEventListener('click', toggleDarkMode);

// Apply stored theme preference when the page loads
window.addEventListener('load', applyStoredThemePreference);


