// =================================================================
// MAIN.JS - VERSIÓN 4.0 FINAL Y COMPLETA (IA REAL)
// Contiene: Un micro-modelo de lenguaje para respuestas contextuales y lógicas.
// =================================================================

// --- CONFIGURACIÓN GLOBAL Y ESTADO DEL SISTEMA ---
const NOMBRE_USUARIO = "Juan";
let estadoConversacion = { modo: 'libre', paso: '', datosPlan: {} };
let sistema = {
    historialChat: [],
    contratos: [],
    racha: 0,
    logros: [],
    lastInteractionTimestamp: Date.now()
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
    sistema.lastInteractionTimestamp = Date.now();
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
            navigator.serviceWorker.register('/El_Guardian/service-worker.js', { scope: '/El_Guardian/' })
                .then(registration => {
                    console.log('Service Worker registrado.');
                    if (registration.periodicSync) {
                        registration.periodicSync.register('engagement-check', { minInterval: 12 * 60 * 60 * 1000 });
                    }
                });
        });
    }
}

async function solicitarPermisoNotificaciones() {
    if ('Notification' in window && Notification.permission === 'default') {
        await Notification.requestPermission();
    }
}

// --- MANEJO DE ENTRADA DEL USUARIO ---
function procesarComandoUsuario(comando) {
    addUserMessage(comando);
    chatInput.value = '';
    showThinkingIndicator();
    setTimeout(() => {
        removeThinkingIndicator();
        getGuardianResponse(comando);
    }, 900);
}

// --- MENSAJERÍA Y UI ---
function iniciarSecuenciaArranque() {
    const mensajes = [
        { texto: "Iniciando núcleo CXQIA... ✅", animar: true },
        { texto: "Cargando Sistema Guardián OS [v4.0]... 🛡️", animar: true },
        { texto: "Activando protocolo RAI de Mensajes... 💬", animar: true },
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
        estadoConversacion = { modo: 'diseño', paso: 'x1', datosPlan: { mision: '', especificaciones: [], inicio: '', duracion: '' } };
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
                if (!estadoConversacion.datosPlan.especificaciones) estadoConversacion.datosPlan.especificaciones = [];
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
    const misionCompleta = [estadoConversacion.datosPlan.mision, ...(estadoConversacion.datosPlan.especificaciones || [])].join(' -> ');
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
        notificadoPorSW: false
    };
    if (!sistema.contratos) sistema.contratos = [];
    sistema.contratos.push(nuevoContrato);
    const duracionTexto = nuevoContrato.duracion ? `\nDuración: ${nuevoContrato.duracion}` : '';
    const contractText = `CONTRATO FORJADO\n--------------------\nMisión: ${nuevoContrato.mision}\nInicio: ${nuevoContrato.inicio} (${nuevoContrato.fecha})${duracionTexto}\n--------------------`;
    addGuardianMessage(contractText);
    addGuardianMessage("Contrato agendado. He programado un recordatorio. ¿Siguiente misión?");
    if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
        navigator.serviceWorker.controller.postMessage({ type: 'SCHEDULE_NOTIFICATION', payload: nuevoContrato });
    }
    estadoConversacion = { modo: 'libre', paso: '', datosPlan: {} };
    guardarSistemaEnDB();
}

// --- MICRO-MODELO DE LENGUAJE (EL NUEVO CEREBRO) ---

function llamarAGrok(textoUsuario) {
    const texto = textoUsuario.toLowerCase();

    const conocimiento = {
        'yo': { tipo: 'sujeto', sinonimos: ['me', 'mi'] },
        'tú': { tipo: 'sujeto', sinonimos: ['vos', 'tu'] },
        'trabajo': { tipo: 'concepto', relacion: ['estrés', 'dinero', 'proyecto'] },
        'problema': { tipo: 'concepto', relacion: ['solución', 'estrés', 'ayuda'] },
        'idea': { tipo: 'concepto', relacion: ['creatividad', 'proyecto', 'solución'] },
        'estoy': { tipo: 'verbo_estado', sinonimos: ['ando', 'me siento'] },
        'tengo': { tipo: 'verbo_posesion', sinonimos: ['poseo'] },
        'quiero': { tipo: 'verbo_deseo', sinonimos: ['necesito', 'deseo'] },
        'cansado': { tipo: 'estado', sentimiento: 'negativo' },
        'feliz': { tipo: 'estado', sentimiento: 'positivo' },
        'estresado': { tipo: 'estado', sentimiento: 'negativo' },
        'motivado': { tipo: 'estado', sentimiento: 'positivo' },
    };

    let tokens = [];
    const palabras = texto.replace(/[?¿!¡,.]/g, '').split(' ');
    palabras.forEach(palabra => {
        if (conocimiento[palabra]) {
            tokens.push({ palabra, ...conocimiento[palabra] });
        } else {
            tokens.push({ palabra, tipo: 'desconocido' });
        }
    });

    const sujeto = tokens.find(t => t.tipo === 'sujeto' && t.palabra === 'yo');
    const estado = tokens.find(t => t.tipo === 'estado');
    const concepto = tokens.find(t => t.tipo === 'concepto');
    const deseo = tokens.find(t => t.tipo === 'verbo_deseo');

    let respuestaGenerada = "";

    if (sujeto && estado) {
        if (estado.sentimiento === 'negativo') {
            respuestaGenerada = `Entiendo que te sientas ${estado.palabra}. ¿Hay algo específico que esté causando ese sentimiento? A veces, ponerle nombre ayuda.`;
        } else {
            respuestaGenerada = `¡Qué bueno que te sientas ${estado.palabra}! Aprovechar esa energía es clave. ¿Qué planes tienes con esa motivación?`;
        }
    } else if (sujeto && deseo && concepto) {
        respuestaGenerada = `Un ${concepto.palabra} es un desafío, y buscar una ${concepto.relacion[0]} es el primer paso. ¿Qué has intentado hasta ahora para abordar este ${concepto.palabra}?`;
    } else if (concepto) {
        respuestaGenerada = `Mencionas "${concepto.palabra}". Este concepto suele estar relacionado con '${concepto.relacion.join("', '")}'. ¿Tu situación encaja con alguna de estas ideas?`;
    } else {
        const desconocido = tokens.find(t => t.tipo === 'desconocido');
        if (desconocido) {
            respuestaGenerada = `La palabra "${desconocido.palabra}" es nueva para mi base de conocimiento. ¿Podrías explicarme qué significa para ti en este contexto? Me interesa aprender.`;
        } else {
            respuestaGenerada = "Estoy procesando eso. Es complejo. ¿Puedes darme un poco más de detalle para entender mejor el panorama?";
        }
    }

    addGuardianMessage(respuestaGenerada);
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
    const contratosAgrupados = sistema.contratos.reduce((acc, contrato) => {
        const fecha = contrato.fecha;
        if (!acc[fecha]) acc[fecha] = [];
        acc[fecha].push(contrato);
        return acc;
    }, {});
    const fechasOrdenadas = Object.keys(contratosAgrupados).sort((a, b) => {
        const [dayA, monthA, yearA] = a.split('/');
        const [dayB, monthB, yearB] = b.split('/');
        return new Date(`${yearB}-${monthB}-${dayB}`) - new Date(`${yearA}-${monthA}-${dayA}`);
    });
    fechasOrdenadas.forEach(fecha => {
        const grupoEl = document.createElement('div');
        grupoEl.className = 'fecha-grupo';
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
        addGuardianMessage("Contrato roto. La racha se reinicia. No es un fracaso, es un dato. Analiza y vuelve a forjar.");
    }
    guardarSistemaEnDB();
    renderizarListaContratos();
}
