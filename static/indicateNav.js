document.addEventListener('DOMContentLoaded', () => {
    
    // Get default section value
    const defaultSectionValue = section

    // Highlight and display default navbar section upon page reload 
    requestAnimationFrame(() => {
        if(!defaultSectionValue) return 
        const defaultSection = document.getElementById(defaultSectionValue)
        defaultSection.click()
    })


    document.body.addEventListener('click', (event) => {
        const target = event.target;

        if (target.classList.contains('section')) {
            if (!target.classList.contains('clicked')) {
                document.querySelectorAll('img.section.clicked').forEach(clickedImg => {
                    clickedImg.classList.remove('clicked');
                });

                target.classList.add('clicked');
            }
        }

        if (target.classList.contains('toggle')) {
            target.classList.toggle('enabled');
        }

        if (target.classList.contains('button')) {
            target.classList.toggle('clicked');
        }
    });
});
