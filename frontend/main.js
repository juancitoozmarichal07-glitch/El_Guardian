// =================================================================
// MAIN.JS - VERSIÓN FINAL Y FUNCIONAL
// Conecta con Render, maneja la ruleta y la transición de arranque.
// =================================================================

// --- CONFIGURACIÓN GLOBAL Y ESTADO DEL CLIENTE ---
const NOMBRE_USUARIO = "Juan";
// La URL de tu cerebro en Render. ¡Esta es la conexión clave!
const URL_ALE_SERVER = 'https://el-guardian.onrender.com/execute';
let estadoConversacion = { modo: 'libre' }; // El estado inicial del diálogo.

// --- REFERENCIAS AL DOM (se asignan al arrancar) ---
let bootContainer, bootMessage, appContainer, history, chatInput, sendButton, navBar, screens;

// --- SETUP INICIAL DE LA APLICACIÓN ---
document.addEventListener('DOMContentLoaded', () => {
    // 1. Vinculamos los elementos de la interfaz del index.html
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
    
    // 3. Iniciamos la secuencia de arranque visual (LA VERSIÓN CORREGIDA)
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

// --- SECUENCIA DE ARRANQUE VISUAL (¡CORREGIDA!) ---
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
            // --- ¡LA TRANSICIÓN QUE FALTABA! ---
            // 1. Ocultamos la pantalla de arranque.
            bootContainer.classList.add('hidden');
            
            // 2. Mostramos el contenedor principal de la aplicación con el chat.
            appContainer.classList.remove('hidden');
            
            // 3. Ponemos el foco en el campo de texto para que puedas escribir.
            chatInput.focus();
            
            // 4. Pedimos el saludo inicial para que aparezca DENTRO del chat.
            llamarALE("_SALUDO_INICIAL_");
        }
    }
    siguienteMensaje();
}

// --- PROCESAMIENTO DE ENTRADA DEL USUARIO ---
function procesarComandoUsuario(comando) {
    addUserMessage(comando);
    llamarALE(comando);
    chatInput.value = '';
}

// --- FUNCIONES PARA MANEJAR LA INTERFAZ DE CHAT ---
function addUserMessage(texto) {
    const messageBubble = document.createElement('div');
    messageBubble.className = 'message-bubble user-message';
    messageBubble.textContent = texto;
    history.appendChild(messageBubble);
    history.scrollTop = history.scrollHeight;
}

// En tu main.js, reemplaza la función addGuardianMessage por esta:

function addGuardianMessage(texto) {
    removeThinkingIndicator();

    // 1. Creamos la burbuja de mensaje, pero la dejamos vacía.
    const messageBubble = document.createElement('div');
    messageBubble.className = 'message-bubble guardian-message';
    history.appendChild(messageBubble);

    // 2. Iniciamos la animación de máquina de escribir.
    let i = 0;
    const speed = 25; // Velocidad en milisegundos por caracter. Puedes ajustarla.

    function typeWriter() {
        if (i < texto.length) {
            // Añadimos la siguiente letra al contenido de la burbuja.
            messageBubble.textContent += texto.charAt(i);
            i++;
            
            // Hacemos scroll para que siempre se vea la última línea.
            history.scrollTop = history.scrollHeight;
            
            // Esperamos un poquito antes de escribir la siguiente letra.
            setTimeout(typeWriter, speed);
        }
    }

    // ¡Iniciamos el efecto!
    typeWriter();
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

// --- FUNCIÓN PARA LA RULETA VISUAL ---
function mostrarRuleta(opciones) {
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

    chatInput.disabled = true;
    sendButton.disabled = true;

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
                ruletaContainer.remove();
                chatInput.disabled = false;
                sendButton.disabled = false;
                chatInput.focus();
                procesarComandoUsuario(eleccionFinal); 
            }, 1200);
        }
    }, shuffleInterval);
}

// --- LÓGICA DE COMUNICACIÓN CON EL CEREBRO (A.L.E.) ---
async function llamarALE(comando) {
    showThinkingIndicator();

    try {
        const response = await fetch(URL_ALE_SERVER, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                skillset_target: "guardian",
                comando: comando,
                estado_conversacion: estadoConversacion 
            })
        });

        if (!response.ok) throw new Error(`Error del servidor: ${response.status}`);

        const respuesta = await response.json();

        if (respuesta.nuevo_estado) {
            estadoConversacion = respuesta.nuevo_estado;
        }

        if (respuesta.accion_ui && respuesta.accion_ui === 'MOSTRAR_RULETA') {
            removeThinkingIndicator();
            mostrarRuleta(respuesta.opciones_ruleta);
        } else if (respuesta.mensaje_para_ui) {
            addGuardianMessage(respuesta.mensaje_para_ui);
        } else {
            removeThinkingIndicator();
            console.log("Respuesta del servidor no reconocida:", respuesta);
        }

    } catch (error) {
        console.error("Error en llamarALE:", error);
        removeThinkingIndicator();
        addGuardianMessage("Error de conexión con el núcleo A.L.E. en Render.", false);
    }
}
