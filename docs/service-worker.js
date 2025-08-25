// =================================================================
// service-worker.js (Versión Puesta a Punto)
// Contiene: Notificaciones precisas y manejo de clics.
// =================================================================

let scheduledNotifications = [];
let checkInterval = null;

self.addEventListener('install', () => {
    self.skipWaiting();
    console.log('Service Worker instalado.');
});

self.addEventListener('activate', event => {
    event.waitUntil(clients.claim());
    console.log('Service Worker activado y controlando clientes.');
});

self.addEventListener('message', event => {
    if (event.data && event.data.type === 'SCHEDULE_NOTIFICATION') {
        const contrato = event.data.payload;
        console.log('SW: Alarma de notificación recibida para:', contrato.mision);
        if (!scheduledNotifications.some(c => c.id === contrato.id)) {
            scheduledNotifications.push(contrato);
        }
        if (!checkInterval) {
            startChecking();
        }
    }
});

function startChecking() {
    if (checkInterval) clearInterval(checkInterval);
    console.log('SW: Iniciando motor de comprobación de notificaciones (cada minuto).');
    checkInterval = setInterval(() => {
        const now = Date.now();
        scheduledNotifications = scheduledNotifications.filter(contrato => {
            if (contrato.timestampInicio <= now) {
                console.log(`SW: ¡Hora de notificar! Misión: ${contrato.mision}`);
                self.registration.showNotification(`Guardián: ¡Es la hora!`, {
                    body: `Tu Contrato '${contrato.mision}' ha comenzado.`,
                    icon: './icon-192.png',
                    tag: `contrato-${contrato.id}`,
                    data: { url: self.location.origin }
                });
                return false; // Eliminar de la lista de pendientes
            }
            return true; // Mantener en la lista
        });
        if (scheduledNotifications.length === 0) {
            console.log('SW: No hay más notificaciones pendientes. Deteniendo motor.');
            clearInterval(checkInterval);
            checkInterval = null;
        }
    }, 60000);
}
