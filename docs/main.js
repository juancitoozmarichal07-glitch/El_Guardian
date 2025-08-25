// =================================================================
// MAIN.JS - VERSIÓN 8.1 "LA VICTORIA FINAL"
// CEREBRO COMPLETO DEL GUARDIÁN CON LÓGICA PWA CORREGIDA
// =================================================================

// --- CONFIGURACIÓN GLOBAL Y ESTADO DEL SISTEMA ---
const NOMBRE_USUARIO = "Juan";
let estadoConversacion = { modo: 'libre', paso: '', datosPlan: { mision: '', especificaciones: [] } };
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
            request.onerror = () => resolve(); // Resuelve incluso si hay error para no bloquear la app
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
    setupEventListeners(navBar, screens);
    iniciarSecuenciaArranque();
});

function setupEventListeners(navBar, screens) {
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
        document.querySelectorAll('.nav-button').forEach(button => button.classList.remove('active');
        targetButton.classList.add('active');
    });

    if(listaContratosContainer) listaContratosContainer.addEventListener('click', manejarAccionesContrato);

    // --- CÓDIGO DE REGISTRO DE PWA ---
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            // RUTA CORREGIDA PARA GITHUB PAGES CON CARPETA /docs/
            navigator.serviceWorker.register('./service-worker.js')
                .then(registration => {
                    console.log('Service Worker registrado con éxito.');
                    // Lógica para pedir permisos de notificación y sincronización periódica
                    return registration.periodicSync.register('check-contracts', {
                        minInterval: 12 * 60 * 60 * 1000, // Mínimo 12 horas
                    });
                })
                .then(() => console.log('Sincronización periódica registrada.'))
                .catch(error => {
                    console.log('Fallo en el registro del Service Worker o la Sincronización:', error);
                });
        });
    }
}

function procesarComandoUsuario(comando) {
    addUserMessage(comando);
    setTimeout(() => {
        showThinkingIndicator();
        setTimeout(() => {
            removeThinkingIndicator();
            getGuardianResponse(comando);
        }, 800);
    }, 200);
}

// --- SECUENCIA DE ARRANQUE ---
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
            let html = mensajeActual.texto;
            if (mensajeActual.animar) {
                html += ' <span class="loading-dots"><span>.</span><span>.</span><span>.</span></span>';
            }
            bootMessage.innerHTML = html;
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
        const primerMensaje = `Sistema cargado, ${NOMBRE_USUARIO}. ¿Forjamos un Contrato o necesitas hablar primero?`;
        addGuardianMessage(primerMensaje);
    }
    history.scrollTop = history.scrollHeight;
}

// --- FUNCIONES DE MENSAJERÍA ---
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
    messageBubble.textContent = texto;
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

// --- LÓGICA DE RULETA ---
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

// --- CEREBRO CONVERSACIONAL Y LÓGICA DE DISEÑO ---
async function llamarAGrok(textoUsuario) {
    const systemPrompt = `Eres Guardian, un asistente de IA. Tu propósito es ser un compañero cognitivo para Juan. Eres empático, directo y motivador. Tu personalidad es la de un amigo sabio y un coach que entiende cómo funciona Juan. Tu objetivo es ayudarlo a mantenerse enfocado y a tomar acción.

MODO DE OPERACIÓN DUAL:
1.  MODO CONVERSACIÓN (por defecto): Habla libremente con Juan. Responde a sus preguntas, sigue sus conversaciones, actúa como un amigo. Sé natural.
2.  MODO DISEÑO (palabra clave): Si Juan menciona las palabras "contrato", "forjar", "ruleta" o cualquier sinónimo claro de iniciar un plan de acción, tu ÚNICA Y ABSOLUTA RESPUESTA debe ser la palabra clave 'MODO_DISEÑO'. No añadas NADA MÁS. No saludes, no confirmes, solo responde 'MODO_DISEÑO'.

Esta regla es inquebrantable. Es la transición entre ser un amigo y ser una herramienta de enfoque.`;
    
    const mensajesParaAPI = [
        { role: 'system', content: systemPrompt },
        ...sistema.historialChat.slice(-6),
        { role: 'user', content: textoUsuario }
    ];

    try {
        // Aquí iría el fetch a la API de Groq si la clave estuviera disponible
        // const response = await fetch(...)
        // const data = await response.json();
        // const respuestaIA = data.choices[0].message.content;

        // Simulación de respuesta para pruebas sin API
        const textoEnMinusculas = textoUsuario.toLowerCase();
        let respuestaIA = "Entendido. ¿En qué más puedo ayudarte hoy?";
        if (textoEnMinusculas.includes('contrato') || textoEnMinusculas.includes('forjar') || textoEnMinusculas.includes('ruleta')) {
            respuestaIA = 'MODO_DISEÑO';
        }

        if (respuestaIA.trim().toUpperCase() === 'MODO_DISEÑO') {
            estadoConversacion.modo = 'diseño';
            estadoConversacion.paso = 'x1';
            addGuardianMessage("Entendido. Entrando en Modo Diseño.\n\n**Paso 1: La Misión.**\nDime las opciones para la primera ruleta (X1), separadas por comas.", false);
        } else {
            addGuardianMessage(respuestaIA);
        }
    } catch (error) {
        console.error("Error al llamar a la IA:", error);
        addGuardianMessage("Error de conexión con la IA central. Intenta de nuevo.");
    }
}

function procesarPasoDiseño(entrada) {
    const { paso } = estadoConversacion;
    const opciones = entrada.split(',').map(s => s.trim()).filter(Boolean);

    if (opciones.length > 1) {
        mostrarRuleta(opciones);
        return;
    }

    const eleccion = entrada;

    if (paso === 'x1') {
        estadoConversacion.datosPlan.mision = eleccion;
        estadoConversacion.paso = 'xn';
        addGuardianMessage(`Misión aceptada: **${eleccion}**.\n\n**Siguiente Paso: Especificación.**\n¿Quieres añadir otra capa de ruleta para especificar más? Dime las opciones (X2) o escribe 'listo' para continuar.`);
    } else if (paso === 'xn') {
        if (eleccion.toLowerCase() === 'listo') {
            estadoConversacion.paso = 'inicio';
            addGuardianMessage(`Perfecto. Misión definida.\n\n**Paso Final: El Sello.**\nDime los posibles horarios de inicio (ej: 14:00, 15:00).`);
        } else if (eleccion.toLowerCase() === 'borrar') {
            if (estadoConversacion.datosPlan.especificaciones.length > 0) {
                const borrada = estadoConversacion.datosPlan.especificaciones.pop();
                addGuardianMessage(`Última especificación ('${borrada}') eliminada. ¿Nuevas opciones para esta capa o 'listo'?`);
            } else {
                addGuardianMessage(`No hay especificaciones que borrar. ¿Opciones para la siguiente capa o 'listo'?`);
            }
        } else {
            estadoConversacion.datosPlan.especificaciones.push(eleccion);
            const misionCompleta = [estadoConversacion.datosPlan.mision, ...estadoConversacion.datosPlan.especificaciones].join(' -> ');
            addGuardianMessage(`Entendido: **${misionCompleta}**.\n\n¿Otra capa más (Xn)? ¿Opciones o 'listo'? También puedes decir 'borrar' para eliminar la última capa.`);
        }
    } else if (paso === 'inicio') {
        estadoConversacion.datosPlan.inicio = eleccion;
        estadoConversacion.paso = 'duracion';
        addGuardianMessage(`Hora de inicio: **${eleccion}**.\n\nAhora, dime las opciones para la duración (ej: 30 min, 45 min, 1 hora).`);
    } else if (paso === 'duracion') {
        estadoConversacion.datosPlan.duracion = eleccion;
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
        fecha: new Date().toLocaleDateString('es-ES'),
        estado: 'agendado' // agendado, cumplido, roto
    };
    sistema.contratos.push(nuevoContrato);
    
    const contractText = `CONTRATO FORJADO\n--------------------\nMisión: ${nuevoContrato.mision}\nInicio: ${nuevoContrato.inicio}\nDuración: ${nuevoContrato.duracion}\nFecha: ${nuevoContrato.fecha}\n--------------------`;
    addGuardianMessage(contractText, false);
    addGuardianMessage("Contrato agendado en tu calendario. Yo te aviso para arrancar. ¿Siguiente misión?");

    estadoConversacion = { modo: 'libre', paso: '', datosPlan: { mision: '', especificaciones: [] } };
    guardarSistemaEnDB();
}

function getGuardianResponse(command) {
    if (estadoConversacion.modo === 'libre') {
        llamarAGrok(command);
    } else {
        procesarPasoDiseño(command);
    }
}

// --- LÓGICA DE PANTALLAS ADICIONALES ---
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
    
    const contratosOrdenados = [...sistema.contratos].reverse();
    contratosOrdenados.forEach(contrato => {
        const contratoEl = document.createElement('div');
        contratoEl.className = `contrato-item estado-${contrato.estado}`;
        contratoEl.innerHTML = `
            <div class="contrato-mision">${contrato.mision}</div>
            <div class="contrato-detalles">
                <span>📅 ${contrato.fecha}</span>
                <span>⏰ ${contrato.inicio}</span>
                <span>⏱️ ${contrato.duracion}</span>
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
        // Lógica de racha: Si el último contrato cumplido no fue hoy, se resetea y se suma 1.
        // (Simplificado por ahora: solo suma)
        sistema.racha++;
        addGuardianMessage("¡Excelente! Contrato cumplido. Tu racha aumenta. La disciplina es la forja del carácter.");
    } else if (e.target.classList.contains('romper-btn')) {
        sistema.contratos[contratoIndex].estado = 'roto';
        sistema.racha = 0;
        addGuardianMessage("Contrato roto. La racha se reinicia. No es un fracaso, es un dato. Analiza, aprende y vuelve a forjar. La voluntad es tuya.");
    }
    
    guardarSistemaEnDB();
    renderizarListaContratos();
}
