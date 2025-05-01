document.addEventListener('DOMContentLoaded', function() {
    console.log('Recipe app initialized successfully');

    // Check if elements are loading
    const mainContent = document.querySelector('main');
    if (mainContent) {
        console.log('Main content found:', mainContent.innerHTML.length, 'characters');
    } else {
        console.error('Main content not found');
    }
});