window.addEventListener('load', function () {
    var customerField = document.querySelector('#id_customer');
    let startTime = document.getElementById('id_start_time'); // Поле времени
    let endTime = document.getElementById('id_end_time'); // Поле времени

    let apiUrl = window.TIMESLOT_CHOICES_URL || '/admin/get_timeslot_choices/'; // Берём URL из шаблона или используем fallback

    if (customerField && startTime && endTime && typeof DateTimeShortcuts !== 'undefined') {
        DateTimeShortcuts.handleClockQuicklink = function(num, val) {
            let d;
            if (val === -1) {
                d = DateTimeShortcuts.now();
            }
            else {
                d = new Date(1970, 1, 1, 0, val*60, 0, 0);
            }
            DateTimeShortcuts.clockInputs[num].value = d.strftime(get_format('TIME_INPUT_FORMATS')[0]);
            DateTimeShortcuts.clockInputs[num].focus();
            DateTimeShortcuts.dismissClock(num);
        }
        // Функция для обновления значений start_time и end_time
        function updateTimeSlots() {
            var customerId = customerField.value;
            if (customerId) {
                // let apiUrl = `${window.TIMESLOT_CHOICES_URL}?date=${encodeURIComponent(selectedDate)}`; // Добавляем параметр
                // Отправляем AJAX-запрос для получения временных слотов
                fetch(`${apiUrl}?customer_id=${customerId}`)
                    .then(response => response.json())
                    .then(data => {
                        // Преобразуем JSON в нужный формат
                        DateTimeShortcuts.clockHours.start_time = data.time_slots.map(item => [item.time, timeToFloat(item.id)]);
                        DateTimeShortcuts.clockHours.end_time = data.time_slots.map(item => [item.time, timeToFloat(item.id)]);
                        removeTimeWidget(startTime);
                        removeTimeWidget(endTime);
                        DateTimeShortcuts.addClock(startTime);
                        DateTimeShortcuts.addClock(endTime);
                    })
                    .catch(error => {
                        console.error('Error fetching time slots:', error);
                    });
            }
        }

        function removeTimeWidget(input) {
            let widgetContainer = input.nextElementSibling; // Найдем контейнер виджета
            if (widgetContainer.matches(".datetimeshortcuts")) {
                widgetContainer.remove(); // Удаляем сам виджет (или его контейнер)
            }
        }

        function timeToFloat(timeString) {
            // Разделяем строку на часы и минуты
            const [hours, minutes] = timeString.split(':').map(Number);
            const fractionalHour = minutes / 60;
            return hours + fractionalHour;
        }

        // Обновляем start_time и end_time при изменении customer
        customerField.addEventListener('change', updateTimeSlots);

        // Обновляем start_time и end_time при загрузке страницы
        updateTimeSlots();
    }
});

