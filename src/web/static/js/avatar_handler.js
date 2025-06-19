document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('img.avatar').forEach(img => {
        img.onload = () => handleAvatarLoad(img, img.dataset.id);
    });

    function handleAvatarLoad(imgEl, id) {
        if(imgEl.complete){
            if (imgEl.naturalWidth > 1 && imgEl.naturalHeight > 1) {
                handleAvatar(imgEl, id)
            }
        }
    }

    function handleAvatar(imgEl, id) {
        imgEl.classList.remove('d-none');
        document.querySelectorAll(`div.initials-badge-${id}`).forEach(el => {
            el.classList.add('d-none');
        });
    }
});