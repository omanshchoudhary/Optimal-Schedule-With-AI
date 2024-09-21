document.addEventListener('DOMContentLoaded', function() {
    const addDataForm = document.getElementById('add-data-form');
    const generateScheduleBtn = document.getElementById('generate-schedule');
    const getTimetableForm = document.getElementById('get-timetable-form');
    const scheduleDisplay = document.getElementById('schedule-display');

    if (addDataForm) {
        addDataForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(addDataForm);
            fetch('/add_data', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Data added successfully and schedule updated');
                    addDataForm.reset();
                } else {
                    alert('Error adding data: ' + (data.error || 'Unknown error'));
                }
            });
        });
    }

    if (generateScheduleBtn) {
        generateScheduleBtn.addEventListener('click', function() {
            fetch('/generate_schedule', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                } else {
                    alert('Error generating schedule: ' + (data.error || 'Unknown error'));
                }
            });
        });
    }

    if (getTimetableForm) {
        getTimetableForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(getTimetableForm);
            fetch('/get_timetable', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                } else {
                    displaySchedule(data.timetable);
                }
            });
        });
    }

    function displaySchedule(schedule) {
        let html = '<table class="min-w-full divide-y divide-gray-200">';
        html += '<thead class="bg-gray-50"><tr><th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Day</th><th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th><th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Class</th><th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Faculty</th><th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Venue</th></tr></thead>';
        html += '<tbody class="bg-white divide-y divide-gray-200">';
        schedule.forEach(item => {
            html += `<tr>
                <td class="px-6 py-4 whitespace-nowrap">${item.day}</td>
                <td class="px-6 py-4 whitespace-nowrap">${item.start_time} - ${item.end_time}</td>
                <td class="px-6 py-4 whitespace-nowrap">${item.class}</td>
                <td class="px-6 py-4 whitespace-nowrap">${item.faculty}</td>
                <td class="px-6 py-4 whitespace-nowrap">${item.venue}</td>
            </tr>`;
        });
        html += '</tbody></table>';
        scheduleDisplay.innerHTML = html;
    }
});
