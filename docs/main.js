// =================================================================
// MAIN.JS - VERSIÓN FINAL CONSOLIDADA (El Guardián 2.5)
// Incluye: IA Conversacional, Flujo de Diseño Corregido y Notificaciones Precisas.
// =================================================================

// --- CONFIGURACIÓN GLOBAL Y ESTADO DEL SISTEMA ---
const NOMBRE_USUARIO = "Juan";
let estadoConversacion = { modo: 'libre', paso: '', datosPlan: { mision: '', especificaciones: [], inicio: '', duracion: '' } };
let contextoConversacion = null; // Para recordar de qué estamos hablando
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
                    // Asegurarse de que las propiedades existan para evitar errores
                    if (!sistema.historialChat) sistema.historialChat = [];
                    if (!sistema.contratos) sistema.contratos = [];
                    if (!sistema.racha) sistema.racha = 0;
                }
                resolve();
            };
            request.onerror = () => resolve(); // Resuelve incluso si hay error para que la app no se bloquee
        });
    } catch (error) {
        console.error("Error al cargar desde IndexedDB:", error);
    }
}

// --- SETUP INICIAL ---
document.addEventListener('DOMContentLoaded', async () => {
    // Vinculación de elementos del DOM
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
            e.preventDefault(); // Evita el comportamiento por defecto del Enter
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
                    console.log('Service Worker registrado con éxito.');
                    // Registrar la sincronización periódica para notificaciones de "agite"
                    if (registration.periodicSync) {
                        registration.periodicSync.register('check-contracts', { minInterval: 12 * 60 * 60 * 1000 })
                            .then(() => console.log('Sincronización periódica registrada.'))
                            .catch(e => console.log('Fallo en el registro de Sincronización Periódica:', e));
                    }
                })
                .catch(error => console.log('Fallo en el registro del SW:', error));
        });
    }
}

// --- LÓGICA DE NOTIFICACIONES ---
async function solicitarPermisoNotificaciones() {
    if (!('Notification' in window)) return;
    if (Notification.permission === 'default') {
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
    }, 800);
}

// --- SECUENCIA DE ARRANQUE Y MENSAJERÍA ---
function iniciarSecuenciaArranque() {
    const mensajes = [
        { texto: "Iniciando núcleo CXQIA... ✅", animar: true },
        { texto: "Cargando Sistema Guardián OS [v2.5]... 🛡️", animar: true },
        { texto: "Activando protocolo RAI de Mensajes... 💬", animar: true },
        { texto: "Verificación de Diario & Registro de Uso... 📖", animar: true },
        { texto: "Sistemas auxiliares en línea... 🌐", animar: true },
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
                    // En lugar de llamar a procesarComandoUsuario, llamamos directamente a la lógica de diseño
                    procesarPasoDiseño(eleccionFinal);
                }, 500);
            }
        }, 100);
    }, { once: true });
}

// --- CEREBRO PRINCIPAL Y LÓGICA DE DISEÑO ---

function getGuardianResponse(command) {
    if (estadoConversacion.modo === 'diseño') {
        procesarPasoDiseño(command);
        return;
    }

    const comandoNormalizado = command.toLowerCase();
    const palabrasClaveDiseño = ['contrato', 'forjar', 'ruleta', 'crear', 'diseñar', 'pacto'];

    if (palabrasClaveDiseño.some(palabra => comandoNormalizado.includes(palabra))) {
        estadoConversacion = { modo: 'diseño', paso: 'x1', datosPlan: { mision: '', especificaciones: [], inicio: '', duracion: '' } };
        contextoConversacion = null;
        addGuardianMessage("Entendido. Entrando en Modo Diseño.\n\n**Paso 1: La Misión.**\nDime la opción u opciones para la primera ruleta (X1), separadas por comas.");
        guardarSistemaEnDB();
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
        contextoConversacion = null;
        addGuardianMessage("Modo Diseño cancelado. Volvemos a la conversación normal.");
        guardarSistemaEnDB();
        return;
    }

    switch (paso) {
        case 'x1':
            estadoConversacion.datosPlan.mision = eleccion;
            estadoConversacion.paso = 'xn';
            addGuardianMessage(`Misión principal establecida: **${eleccion}**.\n\n**Siguiente Paso: Especificación (X2).**\n¿Añadir otra capa? Introduce opciones, o escribe 'listo'.`);
            break;
        case 'xn':
            if (eleccion.toLowerCase() === 'listo') {
                estadoConversacion.paso = 'inicio';
                addGuardianMessage(`Especificaciones completadas.\n\n**Paso Final: El Sello.**\nAhora dime la hora de inicio (ej: 14:00, 15:00).`);
            } else if (eleccion.toLowerCase() === 'borrar') {
                if (estadoConversacion.datosPlan.especificaciones.length > 0) {
                    const borrada = estadoConversacion.datosPlan.especificaciones.pop();
                    addGuardianMessage(`Última especificación ('${borrada}') eliminada. ¿Nuevas opciones, 'listo' o 'borrar'?`);
                } else {
                    addGuardianMessage(`No hay especificaciones que borrar. ¿Opciones o 'listo'?`);
                }
            } else {
                estadoConversacion.datosPlan.especificaciones.push(eleccion);
                const misionCompleta = [estadoConversacion.datosPlan.mision, ...estadoConversacion.datosPlan.especificaciones].join(' -> ');
                addGuardianMessage(`Entendido: **${misionCompleta}**.\n\n¿Otra capa más (Xn)? ¿Opciones, 'listo', 'borrar' o 'cancelar'?`);
            }
            break;
        case 'inicio':
            estadoConversacion.datosPlan.inicio = eleccion;
            estadoConversacion.paso = 'duracion';
            addGuardianMessage(`Hora de inicio fijada: **${eleccion}**.\n\nPor último, la duración. Dime las opciones (ej: 30 min) o escribe 'ninguna'.`);
            break;
        case 'duracion':
            estadoConversacion.datosPlan.duracion = (eleccion.toLowerCase() !== 'ninguna') ? eleccion : '';
            sellarContrato();
            break;
    }
    guardarSistemaEnDB();
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
        notificadoPorSW: false
    };
    sistema.contratos.push(nuevoContrato);
    
    const duracionTexto = nuevoContrato.duracion ? `\nDuración: ${nuevoContrato.duracion}` : '';
    const contractText = `CONTRATO FORJADO\n--------------------\nMisión: ${nuevoContrato.mision}\nInicio: ${nuevoContrato.inicio} (${nuevoContrato.fecha})${duracionTexto}\n--------------------`;
    addGuardianMessage(contractText);
    addGuardianMessage("Contrato agendado. He programado un recordatorio. ¿Siguiente misión?");

    if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
        navigator.serviceWorker.controller.postMessage({
            type: 'SCHEDULE_NOTIFICATION',
            payload: nuevoContrato
        });
    }

    estadoConversacion = { modo: 'libre', paso: '', datosPlan: {} };
    guardarSistemaEnDB();
}

async function llamarAGrok(textoUsuario) {
    const texto = textoUsuario.toLowerCase();
    let respuestaIA = "";

    if (contextoConversacion) {
        if (contextoConversacion === 'productividad') {
            respuestaIA = `Continuando con la productividad, ${NOMBRE_USUARIO}, es clave la claridad en tus objetivos. ¿Sobre qué aspecto quieres que hablemos ahora?`;
            contextoConversacion = null;
        } else if (contextoConversacion === 'filosofia') {
            respuestaIA = "El estoicismo nos enseña a diferenciar entre lo que podemos controlar y lo que no. Aceptar esto es el camino a la tranquilidad. ¿Te interesa este enfoque?";
        }
        if (respuestaIA) { addGuardianMessage(respuestaIA); return; }
    }

    if (texto.includes('hola') || texto.includes('buenos días')) {
        respuestaIA = `Saludos, ${NOMBRE_USUARIO}. Estoy listo para asistirte. ¿Forjamos un Contrato o prefieres conversar?`;
    } else if (texto.includes('gracias')) {
        respuestaIA = "Es mi deber. La disciplina es el puente entre metas y logros. ¿Algo más?";
    } else if (texto.includes('ayuda')) {
        respuestaIA = "Mi propósito es ayudarte a forjar 'Contratos' para construir disciplina. Di 'crear contrato' para empezar. También podemos hablar sobre 'productividad' o 'filosofía'.";
    } else if (texto.includes('productividad')) {
        respuestaIA = "La productividad es un tema central. Podemos hablar sobre técnicas o sistemas. ¿Qué te interesa más?";
        contextoConversacion = 'productividad';
    } else if (texto.includes('filosofía') || texto.includes('estoicismo')) {
        respuestaIA = "Una excelente elección. El estoicismo es particularmente útil para la autodisciplina. ¿Quieres que exploremos sus principios?";
        contextoConversacion = 'filosofia';
    } else {
        respuestaIA = `No he comprendido del todo tu comando. Recuerda que puedes pedirme 'ayuda' para ver mis funciones.`;
    }
    addGuardianMessage(respuestaIA);
}

// --- LÓGICA DE PANTALLAS ADICIONALES ---
function renderizarLogros() {
    if (!rachaContainer) return;
    rachaContainer.innerHTML = `<div class="racha-valor">${sistema.racha}</div><div class="racha-texto">DÍAS DE RACHA</div>`;
}

function renderizarListaContratos() {
    if (!listaContratosContainer) return;
    listaContratosContainer.innerHTML = '';
    if (sistema.contratos.length === 0) {
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
