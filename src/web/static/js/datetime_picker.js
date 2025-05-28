document.addEventListener('DOMContentLoaded', function() {
    const datePicker = document.getElementById('date-picker');
    
    // Update page when date changes
    datePicker.addEventListener('change', function() {
        const selectedDate = this.value;
        const baseUrl = this.dataset.url;
        const newUrl = baseUrl.replace('0000-00-00', selectedDate);
        window.location.href = newUrl;
    });
});