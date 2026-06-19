/**
 * Collapsible Sections - Material 3 Style
 */

function setupCollapsible() {
    const collapsibles = document.querySelectorAll('.collapsible');

    collapsibles.forEach(fieldset => {
        const header = fieldset.querySelector('.collapsible-header');
        const content = fieldset.querySelector('.fieldset-content');

        if (!header || !content) return;

        header.addEventListener('click', () => {
            toggleCollapsible(fieldset);
        });
    });
}

function toggleCollapsible(fieldset) {
    const content = fieldset.querySelector('.fieldset-content');
    const icon = fieldset.querySelector('.collapse-icon');
    const isCollapsed = fieldset.classList.contains('collapsed');

    if (isCollapsed) {
        fieldset.classList.remove('collapsed');
        fieldset.classList.add('expanded');
        content.classList.remove('hidden');
    } else {
        fieldset.classList.add('collapsed');
        fieldset.classList.remove('expanded');
        content.classList.add('hidden');
    }

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
            const content = fieldset.querySelector('.fieldset-content');
            fieldset.classList.add('collapsed');
            fieldset.classList.remove('expanded');
            content.classList.add('hidden');
        }
    });
}
