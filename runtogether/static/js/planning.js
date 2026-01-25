// https://fullcalendar.io/docs

let calendar; // Variable globale pour accéder au calendrier
let selectedStart;
let selectedEnd;

document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    const fetchUrl = calendarEl.dataset.fetchUrl;
    
    // Initialisation des éléments du modal
    const modal = document.getElementById('absence_modal');
    const toggle = document.getElementById('absence_mode_toggle');
    const reasonContainer = document.getElementById('reason_container');
    const confirmBtn = document.getElementById('confirm_absence_btn');
    const reasonInput = document.getElementById('absence_reason');
    
    // Form Elements for Slider
    const minInput = document.getElementById('range-min');
    const maxInput = document.getElementById('range-max');
    const minHidden = document.getElementById('min-distance');
    const maxHidden = document.getElementById('max-distance');
    const range = document.getElementById('slider-range');
    const minDisplay = document.getElementById('min-display');
    const maxDisplay = document.getElementById('max-display');
    
    // --- Slider Logic ---
    function updateSlider() {
        let min = parseInt(minInput.value);
        let max = parseInt(maxInput.value);

        const percentMin = (min / minInput.max) * 100;
        const percentMax = (max / maxInput.max) * 100;

        range.style.left = percentMin + "%";
        range.style.width = (percentMax - percentMin) + "%";
        
        minDisplay.textContent = min;
        maxDisplay.textContent = max;

        // Update hidden inputs
        if (minHidden.value != min) minHidden.value = min;
        if (maxHidden.value != max) maxHidden.value = max;
    }

    minInput.addEventListener('input', function() {
        let min = parseInt(this.value);
        let max = parseInt(maxInput.value);
        if (min > max) {
            this.value = max;
            min = max;
        }
        updateSlider();
        minHidden.dispatchEvent(new Event('change', { bubbles: true }));
    });

    maxInput.addEventListener('input', function() {
        let min = parseInt(minInput.value);
        let max = parseInt(this.value);
        if (max < min) {
            this.value = min;
            max = min;
        }
        updateSlider();
        maxHidden.dispatchEvent(new Event('change', { bubbles: true }));
    });
    
    // Initial update of slider
    updateSlider();

    // --- Filter Form Logic ---
    const filterForm = document.getElementById('filter-form');
    filterForm.addEventListener('submit', function(e) {
        e.preventDefault();
        calendar.refetchEvents();
    });
    
    // Optional: Auto-refresh on change (debounced could be better but sticking to Apply button for now is safer)
    // But users expect "Apply" button to work.

    // --- Calendar Logic ---

    // Gestion de l'affichage du champ "Raison" selon le toggle
    toggle.addEventListener('change', function() {
        if(this.checked) {
            // Mode Retirer -> Cacher la raison
            reasonContainer.classList.add('hidden');
        } else {
            // Mode Ajouter -> Afficher la raison
            reasonContainer.classList.remove('hidden');
        }
    });

    // Gestion du bouton Confirmer
    confirmBtn.addEventListener('click', function(e) {
        e.preventDefault(); // Empêcher la fermeture immédiate du form dialog si on veut gérer l'async
        
        const urlRemove = this.dataset.urlRemove;
        const urlAdd = this.dataset.urlAdd;

        const isRemoveMode = toggle.checked;
        const reason = reasonInput.value;

        if (isRemoveMode) {
            remove_absences(urlRemove, selectedStart, selectedEnd);
        } else {
            set_absences(urlAdd, selectedStart, selectedEnd, reason);
        }
        
        modal.close();
    });

    calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'fr',
        firstDay: 1, // Monday first
        height: 'auto',
        selectable: true,

        // URL qui renvoie tes événements
        events: {
            url: fetchUrl,
            extraParams: function() {
                const formData = new FormData(filterForm);
                const params = {};
                
                // Convert FormData to object, handling multiple values
                for (const [key, value] of formData.entries()) {
                        if (params[key]) {
                        if (!Array.isArray(params[key])) {
                            params[key] = [params[key]];
                        }
                        params[key].push(value);
                    } else {
                        params[key] = value;
                    }
                }
                
                return params;
            }
        },
        
        // Style des événements
        eventDidMount: function(info) {
            if (info.event.extendedProps.type === 'trail') {
                info.el.classList.add('bg-green-500', 'border-none');
            }
        },

        select: function(info) {
            selectedStart = info.start;
            selectedEnd = info.end;
            
            // Reset UI state
            toggle.checked = false; // Default to Add
            reasonContainer.classList.remove('hidden');

            modal.showModal();
        }
    });
    calendar.render();
});

function onCalendarTabShown() {
    calendar.render();
}

function set_absences(url, dateStart, dateEnd, reason) {
    const data = {
        "dateStart": formattedDate(dateStart),
        "dateEnd": formattedDate(dateEnd),
        "reason": reason
    }
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (response.ok) {
            console.log("Absence ajoutée");
            // alert("Absence ajoutée avec succès!");
            calendar.refetchEvents(); // Rafraichir le calendrier
        } else {
            alert("Erreur lors de l'ajout.");
        }
    })
    .catch(error => {
        console.error("Erreur:", error);
        alert("Erreur lors de la communication avec le serveur");
    });
};

function remove_absences(url, dateStart, dateEnd) {
    const data = {
        "dateStart": formattedDate(dateStart),
        "dateEnd": formattedDate(dateEnd)
    }
    fetch(url, {
        method: 'POST', // Ou DELETE selon ton implémentation backend, mais souvent POST en Django simple sans DRF spécifique
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (response.ok) {
            console.log("Absence retirée");
            // alert("Absence retirée avec succès!");
            calendar.refetchEvents(); // Rafraichir le calendrier
        } else {
            alert("Erreur lors du retrait.");
        }
    })
    .catch(error => {
        console.error("Erreur:", error);
        alert("Erreur lors de la communication avec le serveur");
    });
}

function formattedDate(date) {
    const yyyy = date.getFullYear();
    let mm = date.getMonth() + 1; // Months start at 0!
    let dd = date.getDate();

    if (dd < 10) dd = '0' + dd;
    if (mm < 10) mm = '0' + mm;

    return yyyy + '-' + mm + '-' + dd;
}