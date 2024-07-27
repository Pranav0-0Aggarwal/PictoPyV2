document.addEventListener('DOMContentLoaded', () => {
    document.body.addEventListener('click', (event) => {
        const target = event.target;

        if (target.classList.contains('section')) {
            document.querySelectorAll('img.section').forEach(otherImg => {
                if (otherImg !== target) {
                    otherImg.classList.remove('clicked');
                }
            });
            target.classList.toggle('clicked');
        }

        if (target.classList.contains('toggle')) {
            target.classList.toggle('enabled');
        }

        if (target.classList.contains('button')) {
            target.classList.toggle('clicked');
        }
    });
});
