// =================================================================
// service-worker.js (La Versión que SÍ funciona con nuestra app)
// =================================================================

// --- PASO 1: FUNCIONES PARA ACCEDER A LA BASE DE DATOS (IndexedDB) ---

// Función para abrir la base de datos. Es como pedir la llave de la caja fuerte.
function openDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('GuardianDB', 1);
        request.onerror = () => reject("Error abriendo DB");
        request.onsuccess = () => resolve(request.result);
        // Si la DB no existe, la crea con nuestro "almacén" de sistema.
        request.onupgradeneeded = event => {
            const db = event.target.result;
            db.createObjectStore('sistema', { keyPath: 'id' });
        };
    });
}

// Función para leer los datos desde la base de datos.
async function getSistemaData() {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['sistema'], 'readonly');
        const store = transaction.objectStore('sistema');
        // Leemos el objeto que siempre guardamos con la misma clave: 'estado_actual'.
        const request = store.get('estado_actual');
        request.onerror = () => reject("Error leyendo datos");
        // Si lo encuentra, devuelve los datos; si no, devuelve null.
        request.onsuccess = () => resolve(request.result ? request.result.data : null);
    });
}

// --- PASO 2: LA LÓGICA DE NOTIFICACIÓN ---

// Esta es tu función 'checkAndNotifyMissions', pero adaptada y corregida.
async function checkAndNotifyContracts() {
    console.log('Service Worker despertó para chequear Contratos.');
    
    // Leemos los datos desde IndexedDB, no desde localStorage.
    const sistema = await getSistemaData();
    
    if (!sistema || !Array.isArray(sistema.contratos) || sistema.contratos.length === 0) {
        console.log('No hay sistema o no hay contratos para chequear.');
        return;
    }

    const ahora = new Date();

    sistema.contratos.forEach(contrato => {
        // Solo nos importan los contratos que están 'agendados'.
        if (contrato.estado !== 'agendado') return;

        // Convertimos la hora del contrato (ej: "22:30") a un objeto Date de hoy.
        const [horas, minutos] = contrato.inicio.split(':');
        const horaInicio = new Date();
        horaInicio.setHours(horas, minutos, 0, 0);

        // Si la hora del contrato ya pasó...
        if (horaInicio <= ahora) {
            console.log(`Notificando Contrato: ${contrato.mision}`);
            
            // Mostramos la notificación.
            self.registration.showNotification(`Guardián: ¡Es la hora!`, {
                body: `El Contrato '${contrato.mision}' ha comenzado.`,
                icon: 'icon-192.png', // Usa el ícono que definiste.
                badge: 'icon-192.png' // Ícono para la barra de notificaciones.
            });
            
            // Aquí podríamos añadir lógica para marcar el contrato como 'notificado',
            // pero por ahora, lo mantenemos simple.
        }
    });
}

// --- PASO 3: LOS "LISTENERS" DEL SERVICE WORKER ---

// Se activa cuando el SW se instala por primera vez.
self.addEventListener('install', event => {
    console.log('Service Worker instalado.');
    // Forzamos al nuevo SW a activarse inmediatamente.
    self.skipWaiting();
});

// Se activa cuando el SW toma el control.
self.addEventListener('activate', event => {
    console.log('Service Worker activado.');
});

// El evento que se dispara periódicamente en segundo plano.
self.addEventListener('periodicsync', event => {
    // Nos aseguramos de que es nuestra tarea programada.
    if (event.tag === 'check-contracts') {
        event.waitUntil(checkAndNotifyContracts());
    }
});

// Un listener para el evento 'fetch'. Es necesario para que la PWA sea 100% instalable.
// Por ahora, no hace nada, pero es crucial que esté aquí.
self.addEventListener('fetch', event => {
  // No intervenimos en las peticiones de red, simplemente las dejamos pasar.
  return;
});
