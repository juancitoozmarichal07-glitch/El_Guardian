// =================================================================
// MAIN.JS - VERSIÓN FINAL MONOLITO (COMPLETA Y CORRECTA)
// =================================================================

// --- CONFIGURACIÓN GLOBAL Y ESTADO ---
const NOMBRE_USUARIO = "Juan";
// La API_URL ahora es una ruta relativa, porque el frontend y el backend viven en el mismo servidor.
const API_URL = '/execute';
let estadoConversacion = { modo: 'libre' };

// --- REFERENCIAS AL DOM ---
let bootContainer, bootMessage, appContainer, history, chatInput, sendButton, navBar, screens;

// --- INICIO DE LA APLICACIÓN ---
document.addEventListener('DOMContentLoaded', () => {
    // 1. Vinculamos todos los elementos de la interfaz
    bootContainer = document.getElementById('boot-container');
    bootMessage = document.getElementById('boot-message');
    appContainer = document.getElementById('app-container');
    history = document.getElementById('history');
    chatInput = document.getElementById('chat-input');
    sendButton = document.getElementById('send-button');
    navBar = document.getElementById('nav-bar');
    screens = document.querySelectorAll('.screen');

    // 2. Configuramos los listeners de los botones
    setupEventListeners();

    // 3. Iniciamos la secuencia de arranque
    iniciarSecuenciaArranque();
});

function setupEventListeners() {
    sendButton.addEventListener('click', () => {
        const comando = chatInput.value.trim();
        if (comando) {
            addUserMessage(comando);
            llamarALE(comando, estadoConversacion);
            chatInput.value = '';
        }
    });

    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            sendButton.click();
        }
    });
    
    navBar.addEventListener('click', (e) => {
        const targetButton = e.target.closest('.nav-button');
        if (!targetButton) return;
        const targetScreenId = targetButton.dataset.target;
        
        screens.forEach(screen => screen.classList.toggle('active', screen.id === targetScreenId));
        document.querySelectorAll('.nav-button').forEach(button => button.classList.remove('active'));
        targetButton.classList.add('active');
    });
}

// --- SECUENCIA DE ARRANQUE ---
function iniciarSecuenciaArranque() {
    const mensajes = [
        "Iniciando Guardian OS...",
        "Estableciendo conexión con el núcleo...",
        `Bienvenido de nuevo, ${NOMBRE_USUARIO}.`
    ];
    let i = 0;

    function mostrarSiguienteMensaje() {
        if (i < mensajes.length) {
            bootMessage.textContent = mensajes[i];
            i++;
            setTimeout(mostrarSiguienteMensaje, 1200);
        } else {
            // Cuando termina la animación, pide el saludo al cerebro
            llamarALE("_SALUDO_INICIAL_", estadoConversacion);
        }
    }
    mostrarSiguienteMensaje();
}

// --- LÓGICA DE COMUNICACIÓN CON EL CEREBRO (A.L.E.) ---
async function llamarALE(comando, estadoActual) {
    showThinkingIndicator();
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                skillset_target: "guardian",
                comando: comando,
                estado_conversacion: estadoActual
            })
        });
        if (!response.ok) {
            throw new Error(`Error del Servidor: ${response.status}`);
        }
        const data = await response.json();
        removeThinkingIndicator();
        // ¡LA FUNCIÓN QUE FALTABA!
        procesarRespuestaALE(data);
    } catch (error) {
        console.error("Error crítico al llamar a A.L.E.:", error);
        removeThinkingIndicator();
        addGuardianMessage(`Error de conexión. El núcleo en Render podría estar despertando. Por favor, espera un minuto y refresca la página. (Detalle: ${error.message})`);
    }
}

// --- PROCESAMIENTO DE RESPUESTAS Y RENDERIZADO ---

// ¡¡¡ ESTA ES LA FUNCIÓN QUE FALTABA !!!
function procesarRespuestaALE(data) {
    if (data.error) {
        addGuardianMessage(`Error del núcleo: ${data.error}`);
        return;
    }

    // Actualizamos el estado de la conversación con lo que nos mande el cerebro
    if (data.nuevo_estado) {
        estadoConversacion = data.nuevo_estado;
    }

    // Si el cerebro nos manda un mensaje para la UI, lo mostramos
    if (data.mensaje_para_ui) {
        addGuardianMessage(data.mensaje_para_ui);
    }
    
    // Si la secuencia de arranque ha terminado, mostramos la app
    if (bootContainer.style.display !== 'none') {
        bootContainer.classList.add('hidden');
        appContainer.classList.remove('hidden');
        chatInput.focus();
    }
}

function addUserMessage(texto) {
    const messageBubble = document.createElement('div');
    messageBubble.className = 'message-bubble user-message';
    messageBubble.textContent = texto;
    history.appendChild(messageBubble);
    history.scrollTop = history.scrollHeight;
}

function addGuardianMessage(texto) {
    const messageBubble = document.createElement('div');
    messageBubble.className = 'message-bubble guardian-message';
    
    history.appendChild(messageBubble);
    
    // Efecto Typewriter
    let i = 0;
    function typeWriter() {
        if (i < texto.length) {
            messageBubble.innerHTML += texto.charAt(i);
            i++;
            history.scrollTop = history.scrollHeight;
            setTimeout(typeWriter, 20); // Velocidad de escritura
        }
    }
    typeWriter();
}

function showThinkingIndicator() {
    // Evita añadir múltiples indicadores
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
    if (thinkingBubble) {
        thinkingBubble.remove();
    }
}
