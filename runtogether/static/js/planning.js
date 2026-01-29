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

        eventSources: [
            // SOURCE 1 : Vos absences via l'API (dynamique)
            {
                url: fetchUrl,
            }
        ],
        
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
    loadLocalData();
});

function onCalendarTabShown() {
    loadLocalData();
}

function loadLocalData() {
    if (!calendar) {
        return;
    }

    // 1. Récupération et formatage
    const geoElement = document.getElementById('geo-data');
    if (!geoElement) return;

    const coursesData = JSON.parse(geoElement.textContent);
    
    const formattedEvents = coursesData.points.map(course => ({
        title: course.title,
        start: course.date,
        allDay: true, // Recommandé pour les dates sans heure
        extendedProps: { 
            type: course.type, 
            source: 'course' 
        }
    }));

    // 2. Mise à jour du calendrier
    // On commence par supprimer les anciennes sources "statiques" pour éviter les doublons
    const oldSources = calendar.getEventSources();
    oldSources.forEach(source => {
        // On ne supprime que la source qui n'a pas d'URL (donc notre source JSON)
        if (source.id === 'course-source') {
            source.remove();
        }
    });

    // 3. On ajoute la nouvelle source
    calendar.addEventSource({
        id: 'course-source',
        events: formattedEvents,
        className: 'event-course'
    });

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