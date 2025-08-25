// =================================================================
// MAIN.JS - VERSIÓN MEJORADA (El Guardián 2.0)
// Incluye: Ruleta de 1 opción, Duración Opcional, Permiso de Notificaciones y Contratos Agrupados por Día.
// =================================================================

// --- CONFIGURACIÓN GLOBAL Y ESTADO DEL SISTEMA ---
const NOMBRE_USUARIO = "Juan";
let estadoConversacion = { modo: 'libre', paso: '', datosPlan: { mision: '', especificaciones: [], inicio: '', duracion: '' } };
let sistema = {
    historialChat: [],
    contratos: [],
    racha: 0,
    logros: []
};

// --- REFERENCIAS AL DOM (se asignan en DOMContentLoaded) ---
let bootContainer, bootMessage, appContainer, history, chatInput, micButton, sendButton, navBar, screens, listaContratosContainer, rachaContainer;

// --- LÓGICA DE BASE DE DATOS (IndexedDB) ---
function openDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('GuardianDB', 1);
        request.onerror = () => reject("Error abriendo DB");
        request.onsuccess = () => resolve(request.result);
        request.onupgradeneeded = event => {
            const db = event.target.result;
            if (!db.objectStoreNames.contains('sistema')) {
                db.createObjectStore('sistema', { keyPath: 'id' });
            }
        };
    });
}

async function guardarSistemaEnDB() {
    try {
        const db = await openDB();
        const transaction = db.transaction(['sistema'], 'readwrite');
        const store = transaction.objectStore('sistema');
        await store.put({ id: 'estado_actual', data: sistema });
    } catch (error) {
        console.error("Error al guardar en IndexedDB:", error);
    }
}

async function cargarSistemaDesdeDB() {
    try {
        const db = await openDB();
        const transaction = db.transaction(['sistema'], 'readonly');
        const store = transaction.objectStore('sistema');
        const request = store.get('estado_actual');
        return new Promise(resolve => {
            request.onsuccess = () => {
                if (request.result) {
                    sistema = request.result.data;
                    if (!sistema.historialChat) sistema.historialChat = [];
                    if (!sistema.contratos) sistema.contratos = [];
                    if (!sistema.racha) sistema.racha = 0;
                }
                resolve();
            };
            request.onerror = () => resolve();
        });
    } catch (error) {
        console.error("Error al cargar desde IndexedDB:", error);
    }
}

// --- SETUP INICIAL ---
document.addEventListener('DOMContentLoaded', async () => {
    // Vinculación de elementos
    bootContainer = document.getElementById('boot-container');
    bootMessage = document.getElementById('boot-message');
    appContainer = document.getElementById('app-container');
    history = document.getElementById('history');
    chatInput = document.getElementById('chat-input');
    micButton = document.getElementById('mic-button');
    sendButton = document.getElementById('send-button');
    navBar = document.getElementById('nav-bar');
    screens = document.querySelectorAll('.screen');
    listaContratosContainer = document.getElementById('lista-contratos-container');
    rachaContainer = document.getElementById('racha-container');

    await cargarSistemaDesdeDB();
    setupEventListeners();
    iniciarSecuenciaArranque();
    
    // NUEVO: Solicitar permiso de notificaciones al cargar la app
    solicitarPermisoNotificaciones();
});

function setupEventListeners() {
    sendButton.addEventListener('click', () => {
        if (chatInput.value.trim() !== '') procesarComandoUsuario(chatInput.value.trim());
    });
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && chatInput.value.trim() !== '') sendButton.click();
    });
    
    navBar.addEventListener('click', (e) => {
        const targetButton = e.target.closest('.nav-button');
        if (!targetButton) return;
        const targetScreenId = targetButton.dataset.target;
        
        if (targetScreenId === 'logros-screen') renderizarLogros();
        if (targetScreenId === 'calendario-screen') renderizarListaContratos();

        screens.forEach(screen => screen.classList.toggle('active', screen.id === targetScreenId));
        document.querySelectorAll('.nav-button').forEach(button => button.classList.remove('active'));
        targetButton.classList.add('active');
    });

    if(listaContratosContainer) {
        listaContratosContainer.addEventListener('click', (e) => {
            // Manejar acciones de botones (cumplir/romper)
            if (e.target.dataset.id) {
                manejarAccionesContrato(e);
            }
            // Manejar clics en los títulos de fecha para desplegar
            if (e.target.classList.contains('fecha-titulo')) {
                e.target.parentElement.classList.toggle('abierto');
            }
        });
    }

    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register('/El_Guardian/service-worker.js', { scope: '/El_Guardian/' })
                .then(registration => {
                    console.log('Service Worker registrado con éxito.');
                    if (registration.periodicSync) {
                        return registration.periodicSync.register('check-contracts', { minInterval: 12 * 60 * 60 * 1000 });
                    }
                })
                .then(() => console.log('Sincronización periódica registrada.'))
                .catch(error => console.log('Fallo en el registro del SW o Sincronización:', error));
        });
    }
}

// --- LÓGICA DE NOTIFICACIONES ---
async function solicitarPermisoNotificaciones() {
    if (!('Notification' in window)) {
        console.log("Este navegador no soporta notificaciones.");
        return;
    }
    if (Notification.permission === 'granted' || Notification.permission === 'denied') {
        return; // Si ya se decidió, no hacer nada.
    }
    if (Notification.permission === 'default') {
        const resultado = await Notification.requestPermission();
        if (resultado === 'granted') {
            console.log("¡Permiso de notificaciones concedido!");
            new Notification("Guardián Activado", {
                body: "¡Excelente! Ahora podré avisarte cuando un Contrato comience.",
                icon: "icon-192.png"
            });
        }
    }
}

function procesarComandoUsuario(comando) {
    addUserMessage(comando);
    chatInput.value = '';
    setTimeout(() => {
        showThinkingIndicator();
        setTimeout(() => {
            removeThinkingIndicator();
            getGuardianResponse(comando);
        }, 800);
    }, 200);
}

// --- SECUENCIA DE ARRANQUE Y MENSAJERÍA (Sin cambios) ---
function iniciarSecuenciaArranque() {
    const mensajes = [
        { texto: "Iniciando Guardian OS...", animar: true },
        { texto: "Protocolo 'Filo de Navaja' online.", animar: false },
        { texto: "Sistema de Ruletas listo.", animar: false },
        { texto: "Conectando con IA Central...", animar: true },
        { texto: `Bienvenido de nuevo, ${NOMBRE_USUARIO}.`, animar: false }
    ];
    let i = 0;
    function siguienteMensaje() {
        if (i < mensajes.length) {
            const mensajeActual = mensajes[i];
            bootMessage.innerHTML = mensajeActual.texto + (mensajeActual.animar ? ' <span class="loading-dots"><span>.</span><span>.</span><span>.</span></span>' : '');
            i++;
            setTimeout(siguienteMensaje, 1500);
        } else {
            bootContainer.classList.add('hidden');
            appContainer.classList.remove('hidden');
            chatInput.focus();
            gestionarSaludoInicial();
        }
    }
    siguienteMensaje();
}

function gestionarSaludoInicial() {
    history.innerHTML = '';
    if (sistema.historialChat.length > 0) {
        sistema.historialChat.forEach(msg => {
            if (msg.role === 'user') addUserMessage(msg.content, false);
            else if (msg.role === 'assistant') addGuardianMessage(msg.content, false);
        });
    } else {
        addGuardianMessage(`Sistema cargado, ${NOMBRE_USUARIO}. ¿Forjamos un Contrato o necesitas hablar primero?`);
    }
    history.scrollTop = history.scrollHeight;
}

function addUserMessage(texto, guardar = true) {
    const messageBubble = document.createElement('div');
    messageBubble.className = 'message-bubble user-message';
    messageBubble.textContent = texto;
    history.appendChild(messageBubble);
    history.scrollTop = history.scrollHeight;
    if (guardar) {
        sistema.historialChat.push({ role: 'user', content: texto });
        guardarSistemaEnDB();
    }
}

function addGuardianMessage(texto, guardar = true) {
    const messageBubble = document.createElement('div');
    messageBubble.className = 'message-bubble guardian-message';
    messageBubble.innerHTML = texto.replace(/\n/g, '<br>');
    history.appendChild(messageBubble);
    history.scrollTop = history.scrollHeight;
    if (guardar) {
        sistema.historialChat.push({ role: 'assistant', content: texto });
        guardarSistemaEnDB();
    }
}

function showThinkingIndicator() {
    const thinkingBubble = document.createElement('div');
    thinkingBubble.id = 'thinking-bubble';
    thinkingBubble.className = 'message-bubble guardian-message';
    thinkingBubble.innerHTML = '<div class="thinking-indicator"><span>.</span><span>.</span><span>.</span></div>';
    history.appendChild(thinkingBubble);
    history.scrollTop = history.scrollHeight;
}

function removeThinkingIndicator() {
    const thinkingBubble = document.getElementById('thinking-bubble');
    if (thinkingBubble) thinkingBubble.remove();
}

// --- LÓGICA DE RULETA (Sin cambios) ---
function mostrarRuleta(opciones) {
    const ruletaContainer = document.createElement('div');
    ruletaContainer.className = 'ruleta-container';
    opciones.forEach(opcion => {
        const opcionEl = document.createElement('div');
        opcionEl.className = 'ruleta-opcion';
        opcionEl.textContent = opcion;
        ruletaContainer.appendChild(opcionEl);
    });
    const botonGirar = document.createElement('button');
    botonGirar.className = 'ruleta-boton';
    botonGirar.textContent = 'GIRAR RULETA';
    ruletaContainer.appendChild(botonGirar);
    history.appendChild(ruletaContainer);
    history.scrollTop = history.scrollHeight;

    botonGirar.addEventListener('click', () => {
        botonGirar.disabled = true;
        botonGirar.textContent = 'GIRANDO...';
        const opcionesEl = ruletaContainer.querySelectorAll('.ruleta-opcion');
        let shuffleCount = 0;
        const maxShuffles = 20 + Math.floor(Math.random() * 10);
        const shuffleInterval = setInterval(() => {
            opcionesEl.forEach(el => el.classList.remove('active'));
            const randomIndex = Math.floor(Math.random() * opcionesEl.length);
            opcionesEl[randomIndex].classList.add('active');
            shuffleCount++;
            if (shuffleCount >= maxShuffles) {
                clearInterval(shuffleInterval);
                const eleccionFinal = opcionesEl[randomIndex].textContent;
                setTimeout(() => {
                    ruletaContainer.remove();
                    procesarPasoDiseño(eleccionFinal);
                }, 500);
            }
        }, 100);
    }, { once: true });
}

// --- CEREBRO CONVERSACIONAL Y LÓGICA DE DISEÑO (ACTUALIZADO) ---
async function llamarAGrok(textoUsuario) {
    // ... (La lógica interna de llamar a una IA externa no cambia)
    const textoEnMinusculas = textoUsuario.toLowerCase();
    let respuestaIA = "Entendido. ¿En qué más puedo ayudarte hoy?";
    if (textoEnMinusculas.includes('contrato') || textoEnMinusculas.includes('forjar') || textoEnMinusculas.includes('ruleta')) {
        respuestaIA = 'MODO_DISEÑO';
    }

    if (respuestaIA.trim().toUpperCase() === 'MODO_DISEÑO') {
        estadoConversacion = { modo: 'diseño', paso: 'x1', datosPlan: { mision: '', especificaciones: [], inicio: '', duracion: '' } };
        addGuardianMessage("Entendido. Entrando en Modo Diseño.\n\n**Paso 1: La Misión.**\nDime la opción u opciones para la primera ruleta (X1), separadas por comas.", false);
    } else {
        addGuardianMessage(respuestaIA);
    }
}

function procesarPasoDiseño(entrada) {
    const { paso } = estadoConversacion;
    const opciones = entrada.split(',').map(s => s.trim()).filter(Boolean);

    // MEJORA: Ruleta para 1 o más opciones, ignorando comandos
    if (opciones.length >= 1) {
        const comandosEspeciales = ['listo', 'borrar', 'ninguna'];
        if (opciones.length === 1 && comandosEspeciales.includes(opciones[0].toLowerCase())) {
            // Es un comando, no una opción de ruleta, así que continuamos.
        } else {
            mostrarRuleta(opciones);
            return; // Esperamos el resultado de la ruleta
        }
    }

    const eleccion = entrada;

    if (paso === 'x1') {
        estadoConversacion.datosPlan.mision = eleccion;
        estadoConversacion.paso = 'xn';
        addGuardianMessage(`Misión aceptada: **${eleccion}**.\n\n**Siguiente Paso: Especificación.**\n¿Añadir otra capa de ruleta (X2)? Dime las opciones, o escribe 'listo' para continuar.`);
    } else if (paso === 'xn') {
        if (eleccion.toLowerCase() === 'listo') {
            estadoConversacion.paso = 'inicio';
            addGuardianMessage(`Perfecto. Misión definida.\n\n**Paso Final: El Sello.**\nDime los posibles horarios de inicio (ej: 14:00, 15:00).`);
        } else if (eleccion.toLowerCase() === 'borrar') {
            if (estadoConversacion.datosPlan.especificaciones.length > 0) {
                const borrada = estadoConversacion.datosPlan.especificaciones.pop();
                addGuardianMessage(`Última especificación ('${borrada}') eliminada. ¿Nuevas opciones o 'listo'?`);
            } else {
                addGuardianMessage(`No hay especificaciones que borrar. ¿Opciones o 'listo'?`);
            }
        } else {
            estadoConversacion.datosPlan.especificaciones.push(eleccion);
            const misionCompleta = [estadoConversacion.datosPlan.mision, ...estadoConversacion.datosPlan.especificaciones].join(' -> ');
            addGuardianMessage(`Entendido: **${misionCompleta}**.\n\n¿Otra capa más (Xn)? ¿Opciones, 'listo' o 'borrar'?`);
        }
    } else if (paso === 'inicio') {
        estadoConversacion.datosPlan.inicio = eleccion;
        estadoConversacion.paso = 'duracion';
        // MEJORA: Preguntar por duración opcional
        addGuardianMessage(`Hora de inicio: **${eleccion}**.\n\nAhora, la duración. Dime las opciones (ej: 30 min, 1 hora) o escribe 'ninguna' si no aplica.`);
    } else if (paso === 'duracion') {
        // MEJORA: Manejar duración opcional
        if (eleccion.toLowerCase() !== 'ninguna') {
            estadoConversacion.datosPlan.duracion = eleccion;
        } else {
            estadoConversacion.datosPlan.duracion = ''; // Duración vacía si es 'ninguna'
        }
        sellarContrato();
    }
    guardarSistemaEnDB();
}

function sellarContrato() {
    const misionCompleta = [estadoConversacion.datosPlan.mision, ...estadoConversacion.datosPlan.especificaciones].join(' -> ');
    const nuevoContrato = {
        id: Date.now(),
        mision: misionCompleta,
        inicio: estadoConversacion.datosPlan.inicio,
        duracion: estadoConversacion.datosPlan.duracion,
        fecha: new Date().toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' }),
        estado: 'agendado'
    };
    sistema.contratos.push(nuevoContrato);
    
    // MEJORA: Mostrar duración solo si existe
    const duracionTexto = nuevoContrato.duracion ? `\nDuración: ${nuevoContrato.duracion}` : '';
    const contractText = `CONTRATO FORJADO\n--------------------\nMisión: ${nuevoContrato.mision}\nInicio: ${nuevoContrato.inicio}${duracionTexto}\nFecha: ${nuevoContrato.fecha}\n--------------------`;
    addGuardianMessage(contractText, false);
    addGuardianMessage("Contrato agendado en tu calendario. Yo te aviso para arrancar. ¿Siguiente misión?");

    estadoConversacion = { modo: 'libre', paso: '', datosPlan: { mision: '', especificaciones: [], inicio: '', duracion: '' } };
    guardarSistemaEnDB();
}

function getGuardianResponse(command) {
    if (estadoConversacion.modo === 'libre') {
        llamarAGrok(command);
    } else {
        procesarPasoDiseño(command);
    }
}

// --- LÓGICA DE PANTALLAS ADICIONALES (ACTUALIZADO) ---
function renderizarLogros() {
    if (!rachaContainer) return;
    rachaContainer.innerHTML = `
        <div class="racha-valor">${sistema.racha}</div>
        <div class="racha-texto">DÍAS DE RACHA</div>
    `;
}

function renderizarListaContratos() {
    if (!listaContratosContainer) return;
    listaContratosContainer.innerHTML = '';
    if (sistema.contratos.length === 0) {
        listaContratosContainer.innerHTML = '<p>No hay contratos agendados.</p>';
        return;
    }
    
    // MEJORA: Agrupar contratos por fecha
    const contratosAgrupados = sistema.contratos.reduce((acc, contrato) => {
        const fecha = contrato.fecha;
        if (!acc[fecha]) {
            acc[fecha] = [];
        }
        acc[fecha].push(contrato);
        return acc;
    }, {});

    // Ordenar fechas de más reciente a más antigua
    const fechasOrdenadas = Object.keys(contratosAgrupados).sort((a, b) => {
        const [dayA, monthA, yearA] = a.split('/');
        const [dayB, monthB, yearB] = b.split('/');
        return new Date(`${yearB}-${monthB}-${dayB}`) - new Date(`${yearA}-${monthA}-${dayA}`);
    });

    fechasOrdenadas.forEach(fecha => {
        const grupoEl = document.createElement('div');
        grupoEl.className = 'fecha-grupo';
        // El primer grupo (hoy) empieza abierto
        if (fecha === new Date().toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' })) {
            grupoEl.classList.add('abierto');
        }

        const tituloEl = document.createElement('h2');
        tituloEl.className = 'fecha-titulo';
        tituloEl.textContent = fecha;
        grupoEl.appendChild(tituloEl);

        const listaContratosEl = document.createElement('div');
        listaContratosEl.className = 'contratos-lista-interna';
        
        contratosAgrupados[fecha].forEach(contrato => {
            const contratoEl = document.createElement('div');
            contratoEl.className = `contrato-item estado-${contrato.estado}`;
            contratoEl.innerHTML = `
                <div class="contrato-mision">${contrato.mision}</div>
                <div class="contrato-detalles">
                    <span>⏰ ${contrato.inicio}</span>
                    ${contrato.duracion ? `<span>⏱️ ${contrato.duracion}</span>` : ''}
                </div>
                ${contrato.estado === 'agendado' ? `
                <div class="contrato-acciones">
                    <button class="cumplir-btn" data-id="${contrato.id}">¡CUMPLIDO!</button>
                    <button class="romper-btn" data-id="${contrato.id}">ROTO</button>
                </div>` : ''}
            `;
            listaContratosEl.appendChild(contratoEl);
        });
        
        grupoEl.appendChild(listaContratosEl);
        listaContratosContainer.appendChild(grupoEl);
    });
}

function manejarAccionesContrato(e) {
    const id = e.target.dataset.id;
    if (!id) return;

    const contratoIndex = sistema.contratos.findIndex(c => c.id == id);
    if (contratoIndex === -1) return;

    if (e.target.classList.contains('cumplir-btn')) {
        sistema.contratos[contratoIndex].estado = 'cumplido';
        sistema.racha++;
        addGuardianMessage("¡Excelente! Contrato cumplido. Tu racha aumenta. La disciplina es la forja del carácter.");
    } else if (e.target.classList.contains('romper-btn')) {
        sistema.contratos[contratoIndex].estado = 'roto';
        sistema.racha = 0;
        addGuardianMessage("Contrato roto. La racha se reinicia. No es un fracaso, es un dato. Analiza, aprende y vuelve a forjar. La voluntad es tuya.");
    }
    
    guardarSistemaEnDB();
    renderizarListaContratos(); // Re-renderizar para mostrar el cambio de estado
}
