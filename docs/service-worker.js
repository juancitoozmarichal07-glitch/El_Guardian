// =================================================================
// service-worker.js (Tu Versión, MEJORADA para notificaciones precisas)
// =================================================================

// --- PASO 1: TUS FUNCIONES DE BASE DE DATOS (Sin cambios) ---

function openDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('GuardianDB', 1);
        request.onerror = () => reject("Error abriendo DB");
        request.onsuccess = () => resolve(request.result);
        request.onupgradeneeded = event => {
            const db = event.target.result;
            db.createObjectStore('sistema', { keyPath: 'id' });
        };
    });
}

async function getSistemaData() {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['sistema'], 'readonly');
        const store = transaction.objectStore('sistema');
        const request = store.get('estado_actual');
        request.onerror = () => reject("Error leyendo datos");
        request.onsuccess = () => resolve(request.result ? request.result.data : null);
    });
}

// --- PASO 2: LA NUEVA LÓGICA DE NOTIFICACIONES PRECISAS ---

let scheduledNotifications = [];
let checkInterval = null;

// Esta función se activa cuando la app le manda una "alarma"
function scheduleNotification(contrato) {
    console.log('SW: Alarma de notificación recibida y guardada.', contrato);
    // Evitar duplicados si la alarma ya existe
    if (!scheduledNotifications.some(c => c.id === contrato.id)) {
        scheduledNotifications.push(contrato);
    }
    
    // Si el motor de comprobación no está corriendo, lo iniciamos.
    if (!checkInterval) {
        startChecking();
    }
}

// Este es el motor que comprueba cada minuto si debe notificar
function startChecking() {
    if (checkInterval) clearInterval(checkInterval); // Limpiamos cualquier motor anterior
    
    console.log('SW: Iniciando comprobación de notificaciones cada minuto.');
    checkInterval = setInterval(() => {
        const now = Date.now();

        scheduledNotifications = scheduledNotifications.filter(contrato => {
            // Usamos el timestamp que guardamos desde main.js
            if (contrato.timestampInicio <= now) {
                console.log(`SW: ¡Hora de notificar! Misión: ${contrato.mision}`);
                
                self.registration.showNotification(`Guardián: ¡Es la hora!`, {
                    body: `Tu Contrato '${contrato.mision}' ha comenzado.`,
                    icon: 'icon-192.png',
                    tag: `contrato-${contrato.id}`, // Un tag único para la notificación
                    data: { url: self.location.origin + '/El_Guardian/' } // URL para abrir al hacer clic
                });
                
                // La devolvemos como 'false' para eliminarla de la lista de pendientes.
                return false;
            }
            // Si aún no es la hora, la mantenemos en la lista.
            return true;
        });

        // Si ya no hay notificaciones pendientes, detenemos el motor para ahorrar batería.
        if (scheduledNotifications.length === 0) {
            console.log('SW: No hay más notificaciones pendientes. Deteniendo el motor de comprobación.');
            clearInterval(checkInterval);
            checkInterval = null;
        }

    }, 60000); // 60000 milisegundos = 1 minuto
}


// --- PASO 3: LOS "LISTENERS" DEL SERVICE WORKER (ACTUALIZADOS) ---

self.addEventListener('install', event => {
    console.log('Service Worker instalado.');
    self.skipWaiting();
});

self.addEventListener('activate', event => {
    console.log('Service Worker activado.');
    event.waitUntil(clients.claim()); // Asegura que el SW tome control inmediato
});

// ¡NUEVO! Listener para recibir las "alarmas" desde main.js
self.addEventListener('message', event => {
    if (event.data && event.data.type === 'SCHEDULE_NOTIFICATION') {
        scheduleNotification(event.data.payload);
    }
});

// TU listener de 'periodicsync' para las notificaciones de "agite"
self.addEventListener('periodicsync', event => {
    if (event.tag === 'check-contracts' || event.tag === 'engagement-check') {
        console.log(`SW: Despertado por PeriodicSync con tag: ${event.tag}`);
        // Aquí puedes poner la lógica de "agite" si quieres, usando getSistemaData()
        // Por ejemplo: event.waitUntil(checkAndNotifyForEngagement());
    }
});

// ¡NUEVO! Listener para cuando se hace clic en una notificación
self.addEventListener('notificationclick', event => {
    event.notification.close();
    const targetUrl = event.notification.data.url;
    event.waitUntil(
        clients.matchAll({ type: 'window' }).then(clientList => {
            for (const client of clientList) {
                if (client.url.startsWith(targetUrl) && 'focus' in client) {
                    return client.focus();
                }
            }
            if (clients.openWindow) {
                return clients.openWindow(targetUrl);
            }
        })
    );
});

// Tu listener 'fetch', sin cambios.
self.addEventListener('fetch', event => {
  return;
});
