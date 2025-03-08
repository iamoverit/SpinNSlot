window.addEventListener('load', function() {
    // Находим все элементы с классом participants_lists
    const collapseElements = document.querySelectorAll('.participants_lists');

    // Добавляем обработчик клика на всю страницу
    document.addEventListener('click', function(event) {
        // Проверяем, был ли клик вне элементов participants_lists
        let isClickInside = false;
        collapseElements.forEach(element => {
            if (element.contains(event.target)) {
                isClickInside = true;
            }
        });

        // Если клик был вне элементов participants_lists, сворачиваем их
        if (!isClickInside) {
            collapseElements.forEach(element => {
                const collapseInstance = bootstrap.Collapse.getInstance(element);
                if (collapseInstance && collapseInstance._isShown) {
                    collapseInstance.hide();
                }
            });
        }
    });
});