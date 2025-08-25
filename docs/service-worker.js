// =================================================================
// service-worker.js (Versión Puesta a Punto - Notificador Preciso)
// Contiene: Notificaciones precisas y manejo de clics.
// =================================================================

let scheduledNotifications = [];
let checkInterval = null;

self.addEventListener('install', () => {
    self.skipWaiting();
    console.log('SW: Service Worker instalado.');
});

self.addEventListener('activate', event => {
    event.waitUntil(clients.claim());
    console.log('SW: Service Worker activado y controlando clientes.');
});

self.addEventListener('message', event => {
    if (event.data && event.data.type === 'SCHEDULE_NOTIFICATION') {
        const contrato = event.data.payload;
        console.log('SW: Alarma de notificación recibida para:', contrato.mision);
        
        // Evita duplicados
        if (!scheduledNotifications.some(c => c.id === contrato.id)) {
            scheduledNotifications.push(contrato);
        }
        
        // Inicia el motor de comprobación si no está ya funcionando
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
                    tag: `contrato-${contrato.id}`, // Una etiqueta única para la notificación
                    data: { url: self.location.origin } // URL para abrir al hacer clic
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
    }, 60000); // Comprueba cada 60 segundos
}

// Listener para cuando el usuario hace clic en la notificación
self.addEventListener('notificationclick', event => {
    event.notification.close(); // Cierra la notificación
    
    // Intenta abrir la PWA o enfocar la pestaña si ya está abierta
    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true }).then(windowClients => {
            // Si ya hay una ventana abierta, la enfoca
            for (let client of windowClients) {
                if (client.url === event.notification.data.url && 'focus' in client) {
                    return client.focus();
                }
            }
            // Si no hay una ventana abierta, abre una nueva
            if (clients.openWindow) {
                return clients.openWindow(event.notification.data.url);
            }
        })
    );
});
