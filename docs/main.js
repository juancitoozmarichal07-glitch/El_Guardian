// =================================================================
// MAIN.JS - VERSIÓN 9.0 "PUESTA A PUNTO"
// Basado en tu "Victoria Final", con IA, Flujo y Notificaciones mejoradas.
// =================================================================

// --- CONFIGURACIÓN GLOBAL Y ESTADO DEL SISTEMA ---
const NOMBRE_USUARIO = "Juan";
let estadoConversacion = { modo: 'libre', paso: '', datosPlan: {} };
let sistema = {
    historialChat: [],
    contratos: [],
    racha: 0,
    logros: []
};

// --- REFERENCIAS AL DOM ---
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
    solicitarPermisoNotificaciones();
});

function setupEventListeners() {
    sendButton.addEventListener('click', () => {
        if (chatInput.value.trim() !== '') procesarComandoUsuario(chatInput.value.trim());
    });
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && chatInput.value.trim() !== '') {
            e.preventDefault();
            sendButton.click();
        }
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
            if (e.target.dataset.id) manejarAccionesContrato(e);
            if (e.target.classList.contains('fecha-titulo')) e.target.parentElement.classList.toggle('abierto');
        });
    }

    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register('./service-worker.js')
                .then(registration => console.log('Service Worker registrado con éxito.'))
                .catch(error => console.log('Fallo en el registro del SW:', error));
        });
    }
}

async function solicitarPermisoNotificaciones() {
    if ('Notification' in window && Notification.permission === 'default') {
        await Notification.requestPermission();
    }
}

function procesarComandoUsuario(comando) {
    addUserMessage(comando);
    chatInput.value = '';
    showThinkingIndicator();
    setTimeout(() => {
        removeThinkingIndicator();
        getGuardianResponse(comando);
    }, 800);
}

// --- SECUENCIA DE ARRANQUE Y MENSAJERÍA ---
function iniciarSecuenciaArranque() {
    const mensajes = [
        { texto: "Iniciando Guardian OS...", animar: true },
        { texto: "Protocolo 'Filo de Navaja' online.", animar: false },
        { texto: "Conectando con IA Central...", animar: true },
        { texto: `Bienvenido de nuevo, ${NOMBRE_USUARIO}.`, animar: false }
    ];
    let i = 0;
    function siguienteMensaje() {
        if (i < mensajes.length) {
            bootMessage.innerHTML = mensajes[i].texto + (mensajes[i].animar ? ' <span class="loading-dots"><span>.</span><span>.</span><span>.</span></span>' : '');
            i++;
            setTimeout(siguienteMensaje, 1200);
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
    if (sistema.historialChat && sistema.historialChat.length > 0) {
        sistema.historialChat.forEach(msg => {
            if (msg.role === 'user') addUserMessage(msg.content, false);
            else if (msg.role === 'assistant') addGuardianMessage(msg.content, false);
        });
    } else {
        addGuardianMessage(`Sistema cargado, ${NOMBRE_USUARIO}. ¿Forjamos un Contrato o prefieres conversar?`);
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
        if (!sistema.historialChat) sistema.historialChat = [];
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
        if (!sistema.historialChat) sistema.historialChat = [];
        sistema.historialChat.push({ role: 'assistant', content: texto });
        guardarSistemaEnDB();
    }
}

function showThinkingIndicator() {
    if (document.getElementById('thinking-bubble')) return;
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

// --- CEREBRO PRINCIPAL Y LÓGICA DE MODOS ---

function getGuardianResponse(command) {
    if (estadoConversacion.modo === 'diseño') {
        procesarPasoDiseño(command);
        return;
    }
    const comandoNormalizado = command.toLowerCase();
    const palabrasClaveDiseño = ['diseñar contrato', 'crear contrato', 'forjar pacto', 'modo diseño'];
    if (palabrasClaveDiseño.some(palabra => comandoNormalizado.includes(palabra))) {
        estadoConversacion = { modo: 'diseño', paso: 'x1', datosPlan: { mision: '', especificaciones: [] } };
        addGuardianMessage("Entendido. Entrando en Modo Diseño.\n\n**Paso 1: La Misión.**\nDime la opción u opciones para la primera ruleta (X1), separadas por comas.");
    } else {
        llamarAGrok(command);
    }
}

function procesarPasoDiseño(entrada) {
    const { paso } = estadoConversacion;
    const pasosDeRuleta = ['x1', 'xn', 'inicio', 'duracion'];
    if (pasosDeRuleta.includes(paso)) {
        const opciones = entrada.split(',').map(s => s.trim()).filter(Boolean);
        const comandosEspeciales = ['listo', 'borrar', 'ninguna', 'cancelar'];
        const esComando = opciones.length === 1 && comandosEspeciales.includes(opciones[0].toLowerCase());
        if (opciones.length > 0 && !esComando) {
            mostrarRuleta(opciones);
            return;
        }
    }
    const eleccion = entrada;
    if (eleccion.toLowerCase() === 'cancelar') {
        estadoConversacion = { modo: 'libre', paso: '', datosPlan: {} };
        addGuardianMessage("Modo Diseño cancelado. Volvemos a la conversación normal.");
        return;
    }
    switch (paso) {
        case 'x1':
            estadoConversacion.datosPlan.mision = eleccion;
            estadoConversacion.paso = 'xn';
            addGuardianMessage(`Misión principal: **${eleccion}**.\n\n**Siguiente Paso (X2):**\n¿Añadir especificación? Introduce opciones para la ruleta, o escribe 'listo' para continuar.`);
            break;
        case 'xn':
            if (eleccion.toLowerCase() === 'listo') {
                estadoConversacion.paso = 'inicio';
                addGuardianMessage(`Especificaciones completadas.\n\n**Hora de Arranque:**\nDime la hora o las posibles horas de inicio (ej: 14:00, 15:00).`);
            } else {
                estadoConversacion.datosPlan.especificaciones.push(eleccion);
                const misionCompleta = [estadoConversacion.datosPlan.mision, ...estadoConversacion.datosPlan.especificaciones].join(' -> ');
                addGuardianMessage(`Entendido: **${misionCompleta}**.\n\n¿Otra capa más (Xn)? ¿Opciones, 'listo' o 'cancelar'?`);
            }
            break;
        case 'inicio':
            estadoConversacion.datosPlan.inicio = eleccion;
            estadoConversacion.paso = 'duracion';
            addGuardianMessage(`Hora de inicio: **${eleccion}**.\n\n**Límite de Tiempo:**\nDime la duración (ej: 30 min) o escribe 'ninguna'.`);
            break;
        case 'duracion':
            estadoConversacion.datosPlan.duracion = (eleccion.toLowerCase() !== 'ninguna') ? eleccion : '';
            sellarContrato();
            break;
    }
}

function sellarContrato() {
    const misionCompleta = [estadoConversacion.datosPlan.mision, ...estadoConversacion.datosPlan.especificaciones].join(' -> ');
    const [horas, minutos] = estadoConversacion.datosPlan.inicio.split(':').map(Number);
    const fechaInicio = new Date();
    fechaInicio.setHours(horas, minutos, 0, 0);
    if (fechaInicio < new Date()) fechaInicio.setDate(fechaInicio.getDate() + 1);
    const nuevoContrato = {
        id: Date.now(),
        mision: misionCompleta,
        inicio: estadoConversacion.datosPlan.inicio,
        duracion: estadoConversacion.datosPlan.duracion,
        fecha: fechaInicio.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' }),
        timestampInicio: fechaInicio.getTime(),
        estado: 'agendado',
        notificado: false
    };
    sistema.contratos.push(nuevoContrato);
    const duracionTexto = nuevoContrato.duracion ? `\nDuración: ${nuevoContrato.duracion}` : '';
    const contractText = `CONTRATO FORJADO\n--------------------\nMisión: ${nuevoContrato.mision}\nInicio: ${nuevoContrato.inicio} (${nuevoContrato.fecha})${duracionTexto}\n--------------------`;
    addGuardianMessage(contractText);
    addGuardianMessage("Contrato agendado. He programado un recordatorio. ¿Siguiente misión?");
    if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
        navigator.serviceWorker.controller.postMessage({ type: 'SCHEDULE_NOTIFICATION', payload: nuevoContrato });
    }
    estadoConversacion = { modo: 'libre', paso: '', datosPlan: { mision: '', especificaciones: [] } };
    guardarSistemaEnDB();
}

function llamarAGrok(textoUsuario) {
    const texto = textoUsuario.toLowerCase();
    if (texto.includes('hola')) {
        addGuardianMessage("Hola, ¿cómo estás? Estoy listo para lo que necesites.");
        return;
    }
    if (texto.includes('cómo estás') || texto.includes('que tal')) {
        addGuardianMessage("Funcionando a pleno rendimiento. ¿Y tú? ¿Cómo va todo?");
        return;
    }
    if (texto.includes('gracias')) {
        addGuardianMessage("No hay de qué. Para eso estoy.");
        return;
    }
    const palabrasNegativas = ['problema', 'mal', 'cansado', 'triste', 'odio', 'preocupado'];
    const palabrasPositivas = ['bien', 'genial', 'feliz', 'increíble', 'motivado'];
    if (palabrasNegativas.some(p => texto.includes(p))) {
        addGuardianMessage("Entiendo. Suena como una situación complicada. ¿Quieres hablar de ello? A veces ponerlo en palabras ayuda.");
        return;
    }
    if (palabrasPositivas.some(p => texto.includes(p))) {
        addGuardianMessage("¡Me alegra escuchar eso! Esa es la actitud. ¿Qué ha provocado esa buena energía?");
        return;
    }
    if (texto.includes('fui a')) {
        const lugar = texto.split('fui a')[1].trim();
        addGuardianMessage(`¿Ah, sí? ¿Y qué tal por ${lugar}? Cuéntame qué tal la experiencia.`);
        return;
    }
    const respuestasGenericas = [
        "Entendido. ¿Y qué opinas tú sobre eso?",
        "Interesante. ¿Cómo llegaste a esa conclusión?",
        "Te sigo. ¿Hay algo más que debería saber para entender el contexto completo?",
        "Vale, eso aclara las cosas. ¿Y cuál sería el siguiente paso ideal según tú?"
    ];
    addGuardianMessage(respuestasGenericas[Math.floor(Math.random() * respuestasGenericas.length)]);
}

// --- LÓGICA DE PANTALLAS ADICIONALES ---
function renderizarLogros() {
    if (!rachaContainer) return;
    rachaContainer.innerHTML = `<div class="racha-valor">${sistema.racha}</div><div class="racha-texto">DÍAS DE RACHA</div>`;
}

function renderizarListaContratos() {
    if (!listaContratosContainer) return;
    listaContratosContainer.innerHTML = '';
    if (!sistema.contratos || sistema.contratos.length === 0) {
        listaContratosContainer.innerHTML = '<p>No hay contratos agendados.</p>';
        return;
    }
    const contratosOrdenados = [...sistema.contratos].reverse();
    contratosOrdenados.forEach(contrato => {
        const contratoEl = document.createElement('div');
        contratoEl.className = `contrato-item estado-${contrato.estado}`;
        contratoEl.innerHTML = `
            <div class="contrato-mision">${contrato.mision}</div>
            <div class="contrato-detalles">
                <span>📅 ${contrato.fecha}</span>
                <span>⏰ ${contrato.inicio}</span>
                ${contrato.duracion ? `<span>⏱️ ${contrato.duracion}</span>` : ''}
            </div>
            ${contrato.estado === 'agendado' ? `
            <div class="contrato-acciones">
                <button class="cumplir-btn" data-id="${contrato.id}">¡CUMPLIDO!</button>
                <button class="romper-btn" data-id="${contrato.id}">ROTO</button>
            </div>` : ''}
        `;
        listaContratosContainer.appendChild(contratoEl);
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
        addGuardianMessage("¡Excelente! Contrato cumplido. Tu racha aumenta.");
    } else if (e.target.classList.contains('romper-btn')) {
        sistema.contratos[contratoIndex].estado = 'roto';
        sistema.racha = 0;
        addGuardianMessage("Contrato roto. La racha se reinicia. No es un fracaso, es un dato.");
    }
    guardarSistemaEnDB();
    renderizarListaContratos();
}
