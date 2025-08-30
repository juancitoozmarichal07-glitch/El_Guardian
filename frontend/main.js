// =================================================================
// MAIN.JS - CEREBRO DEL CLIENTE GUARDIÁN (v9.0 - Arquitectura A.L.E.)
// Este archivo solo se encarga de la interfaz y la comunicación.
// Toda la inteligencia reside en el servidor Python.
// =================================================================

// --- CONFIGURACIÓN GLOBAL Y ESTADO DEL CLIENTE ---
const NOMBRE_USUARIO = "Juan";
// ¡LA ÚNICA LÍNEA A CAMBIAR!
const API_URL = '/execute';
let estadoConversacion = { modo: 'libre' }; // Estado inicial simple

// --- REFERENCIAS AL DOM (se asignan al arrancar) ---
let bootContainer, bootMessage, appContainer, history, chatInput, sendButton, navBar, screens;

// --- SETUP INICIAL DE LA APLICACIÓN ---
document.addEventListener('DOMContentLoaded', () => {
    // 1. Vinculamos los elementos de la interfaz
    bootContainer = document.getElementById('boot-container');
    bootMessage = document.getElementById('boot-message');
    appContainer = document.getElementById('app-container');
    history = document.getElementById('history');
    chatInput = document.getElementById('chat-input');
    sendButton = document.getElementById('send-button');
    navBar = document.getElementById('nav-bar');
    screens = document.querySelectorAll('.screen');

    // 2. Configuramos los botones y eventos
    setupEventListeners();
    
    // 3. Iniciamos la secuencia de arranque visual
    iniciarSecuenciaArranque();
});

function setupEventListeners() {
    // Evento para el botón de enviar
    sendButton.addEventListener('click', () => {
        const comando = chatInput.value.trim();
        if (comando) {
            procesarComandoUsuario(comando);
        }
    });

    // Evento para la tecla "Enter" en el input
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            sendButton.click();
        }
    });
    
    // Evento para la barra de navegación inferior
    navBar.addEventListener('click', (e) => {
        const targetButton = e.target.closest('.nav-button');
        if (!targetButton) return;
        
        const targetScreenId = targetButton.dataset.target;
        
        screens.forEach(screen => screen.classList.toggle('active', screen.id === targetScreenId));
        document.querySelectorAll('.nav-button').forEach(button => button.classList.remove('active'));
        targetButton.classList.add('active');
    });
}

// --- SECUENCIA DE ARRANQUE VISUAL ---
function iniciarSecuenciaArranque() {
    const mensajes = [
        "Iniciando Guardian OS...",
        "Estableciendo conexión con A.L.E. Core...",
        `Listo para la acción.`
    ];
    let i = 0;

    function siguienteMensaje() {
        if (i < mensajes.length) {
            bootMessage.textContent = mensajes[i];
            i++;
            setTimeout(siguienteMensaje, 1200);
        } else {
            // Transición de la pantalla de arranque a la app principal
            bootContainer.classList.add('hidden');
            appContainer.classList.remove('hidden');
            chatInput.focus();
            // Pedimos el saludo inicial al cerebro A.L.E.
            llamarALE("_SALUDO_INICIAL_");
        }
    }
    siguienteMensaje();
}

// --- PROCESAMIENTO DE ENTRADA DEL USUARIO ---
function procesarComandoUsuario(comando) {
    // Añade el mensaje del usuario a la pantalla
    addUserMessage(comando);
    // Llama al cerebro A.L.E. para obtener una respuesta
    llamarALE(comando);
    // Limpia el input
    chatInput.value = '';
}

// --- FUNCIÓN PRINCIPAL DE COMUNICACIÓN CON EL CEREBRO A.L.E. ---
// =================================================================
// FUNCIÓN DE COMUNICACIÓN CON EL SERVIDOR (VERSIÓN FINAL Y ROBUSTA)
// =================================================================
async function llamarALE(comando, estadoActual) {
    // Muestra el indicador de "pensando" para que el usuario sepa que algo está pasando.
    showThinkingIndicator();

    try {
        // Intenta comunicarse con el servidor en la ruta /execute.
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                skillset_target: "guardian",
                comando: comando,
                estado_conversacion: estadoActual
            })
        });

        // Si la respuesta del servidor no es un "200 OK" (o similar),
        // significa que algo falló en el lado del servidor.
        if (!response.ok) {
            // Creamos un error con el código de estado para saber qué pasó.
            throw new Error(`Error del Servidor: ${response.status}`);
        }

        // Si todo fue bien, convierte la respuesta a formato JSON.
        const data = await response.json();
        
        // Quita el indicador de "pensando".
        removeThinkingIndicator();
        
        // Envía los datos a la función que los procesará.
        procesarRespuestaALE(data);

    } catch (error) {
        // Si CUALQUIER cosa en el bloque 'try' falla (la conexión, la conversión a JSON, etc.),
        // este bloque 'catch' se activará.
        console.error("Error crítico al llamar a A.L.E.:", error);
        
        // Quita el indicador de "pensando" para no dejarlo colgado.
        removeThinkingIndicator();
        
        // Muestra un mensaje de error claro y útil en la interfaz del chat.
        // Este es el mensaje que viste, pero ahora actualizado.
        addGuardianMessage(`Error de conexión. El núcleo en Render podría estar despertando. Por favor, espera un minuto y refresca la página. (Detalle: ${error.message})`);
    }
}


// --- FUNCIONES PARA MANEJAR LA INTERFAZ DE CHAT ---

function addUserMessage(texto) {
    const messageBubble = document.createElement('div');
    messageBubble.className = 'message-bubble user-message';
    messageBubble.textContent = texto;
    history.appendChild(messageBubble);
    history.scrollTop = history.scrollHeight;
}

function addGuardianMessage(texto, conTypewriter = true) {
    removeThinkingIndicator();
    const messageBubble = document.createElement('div');
    messageBubble.className = 'message-bubble guardian-message';
    history.appendChild(messageBubble);

    if (conTypewriter) {
        let i = 0;
        const speed = 20; // ms por caracter
        function typeWriter() {
            if (i < texto.length) {
                messageBubble.textContent += texto.charAt(i);
                i++;
                history.scrollTop = history.scrollHeight;
                setTimeout(typeWriter, speed);
            }
        }
        typeWriter();
    } else {
        messageBubble.textContent = texto;
    }
    history.scrollTop = history.scrollHeight;
}

function showThinkingIndicator() {
    if (document.getElementById('thinking-bubble')) return; // Evita duplicados
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

// --- FUNCIÓN PARA LA RULETA VISUAL ---
function mostrarRuletaVisual(opciones) {
    const ruletaContainer = document.createElement('div');
    ruletaContainer.className = 'ruleta-container';
    
    opciones.forEach(opcion => {
        const opcionEl = document.createElement('div');
        opcionEl.className = 'ruleta-opcion';
        opcionEl.textContent = opcion;
        ruletaContainer.appendChild(opcionEl);
    });
    
    history.appendChild(ruletaContainer);
    history.scrollTop = history.scrollHeight;

    const opcionesEl = ruletaContainer.querySelectorAll('.ruleta-opcion');
    let shuffleCount = 0;
    const maxShuffles = 20 + Math.floor(Math.random() * 10);
    const shuffleInterval = 100;

    const intervalId = setInterval(() => {
        opcionesEl.forEach(el => el.classList.remove('active'));
        const randomIndex = Math.floor(Math.random() * opcionesEl.length);
        opcionesEl[randomIndex].classList.add('active');
        shuffleCount++;
        
        if (shuffleCount >= maxShuffles) {
            clearInterval(intervalId);
            const eleccionFinal = opcionesEl[randomIndex].textContent;
            
            setTimeout(() => {
                // Enviamos la elección al cerebro para que continúe el flujo
                procesarComandoUsuario(eleccionFinal);
            }, 800);
        }
    }, shuffleInterval);
}
