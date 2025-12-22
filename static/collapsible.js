/**
 * Collapsible Sections
 */

function setupCollapsible() {
    const collapsibles = document.querySelectorAll('.collapsible');
    
    collapsibles.forEach(fieldset => {
        const header = fieldset.querySelector('.collapsible-header');
        const content = fieldset.querySelector('.fieldset-content');
        
        if (!header || !content) return;
        
        // Add click handler to header
        header.addEventListener('click', () => {
            toggleCollapsible(fieldset);
        });
    });
}

function toggleCollapsible(fieldset) {
    const content = fieldset.querySelector('.fieldset-content');
    const isCollapsed = fieldset.classList.contains('collapsed');
    
    if (isCollapsed) {
        // Expand
        fieldset.classList.remove('collapsed');
        fieldset.classList.add('expanded');
        content.classList.remove('hidden');
    } else {
        // Collapse
        fieldset.classList.add('collapsed');
        fieldset.classList.remove('expanded');
        content.classList.add('hidden');
    }
    
    // Save state to localStorage
    const section = fieldset.dataset.section;
    if (section) {
        const collapsibleState = JSON.parse(localStorage.getItem('collapsibleState') || '{}');
        collapsibleState[section] = fieldset.classList.contains('collapsed');
        localStorage.setItem('collapsibleState', JSON.stringify(collapsibleState));
    }
}

function restoreCollapsibleState() {
    const collapsibleState = JSON.parse(localStorage.getItem('collapsibleState') || '{}');
    const collapsibles = document.querySelectorAll('.collapsible');
    
    collapsibles.forEach(fieldset => {
        const section = fieldset.dataset.section;
        if (section && collapsibleState[section]) {
            // Collapse this section
            const content = fieldset.querySelector('.fieldset-content');
            fieldset.classList.add('collapsed');
            fieldset.classList.remove('expanded');
            content.classList.add('hidden');
        }
    });
}
