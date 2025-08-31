// =================================================================
// MAIN.JS - VERSIÓN FINAL MONOLITO (COMPLETA Y CORRECTA)
// =================================================================

// ... (al principio de tu main.js)

// --- CONFIGURACIÓN GLOBAL Y ESTADO DEL CLIENTE ---
const NOMBRE_USUARIO = "Juan";

// ESTA ES LA LÍNEA QUE DEBES CAMBIAR:
const URL_ALE_SERVER = 'https://el-guardian.onrender.com/execute';

let estadoConversacion = { modo: 'libre' }; // Estado inicial simple

// ... (el resto del archivo se queda exactamente igual)


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

// --- FUNCIÓN PARA LA RULETA VISUAL ---
// Pega esta función completa en tu archivo main.js

function mostrarRuleta(opciones) {
    // 1. Creamos el contenedor visual de la ruleta en el chat.
    const ruletaContainer = document.createElement('div');
    ruletaContainer.className = 'ruleta-container'; // Usa los estilos que ya tienes en style.css
    
    // 2. Creamos un "botón" de texto para cada opción.
    opciones.forEach(opcion => {
        const opcionEl = document.createElement('div');
        opcionEl.className = 'ruleta-opcion';
        opcionEl.textContent = opcion;
        ruletaContainer.appendChild(opcionEl);
    });
    
    // 3. Añadimos el contenedor completo al historial del chat.
    history.appendChild(ruletaContainer);
    history.scrollTop = history.scrollHeight;

    // 4. Desactivamos el input del usuario para que no pueda escribir mientras la ruleta "gira".
    chatInput.disabled = true;
    sendButton.disabled = true;

    // 5. Iniciamos la animación de selección.
    const opcionesEl = ruletaContainer.querySelectorAll('.ruleta-opcion');
    let shuffleCount = 0;
    const maxShuffles = 20 + Math.floor(Math.random() * 10);
    const shuffleInterval = 100;

    const intervalId = setInterval(() => {
        opcionesEl.forEach(el => el.classList.remove('active'));
        const randomIndex = Math.floor(Math.random() * opcionesEl.length);
        opcionesEl[randomIndex].classList.add('active');
        shuffleCount++;
        
        // 6. Comprobamos si la animación ha terminado.
        if (shuffleCount >= maxShuffles) {
            clearInterval(intervalId);
            const eleccionFinal = opcionesEl[randomIndex].textContent;
            
            // 7. Devolvemos el resultado al cerebro.
            setTimeout(() => {
                ruletaContainer.remove();
                chatInput.disabled = false;
                sendButton.disabled = false;
                chatInput.focus();
                
                // Llamamos a la función principal con la elección final.
                procesarComandoUsuario(eleccionFinal); 
            }, 1200);
        }
    }, shuffleInterval);
}


// (Aquí arriba estaría tu función mostrarRuleta que ya pegaste)


// --- LÓGICA DE COMUNICACIÓN CON EL CEREBRO (A.L.E.) ---
// REEMPLAZA TU FUNCIÓN ACTUAL CON ESTA:
async function llamarALE(comando) {
    showThinkingIndicator();

    // Asegúrate de que esta URL es la correcta de tu servidor en Render
    const API_URL = 'https://el-guardian.onrender.com/execute';

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                skillset_target: "guardian",
                comando: comando,
                // Enviamos el estado de conversación actual, que es una variable global
                estado_conversacion: estadoConversacion 
            })
        });

        if (!response.ok) {
            throw new Error(`Error del servidor: ${response.status}`);
        }

        const respuesta = await response.json();

        // Actualizamos el estado de la conversación para la próxima llamada
        if (respuesta.nuevo_estado) {
            estadoConversacion = respuesta.nuevo_estado;
        }

        // Decidimos qué hacer con la respuesta del cerebro
        if (respuesta.accion_ui && respuesta.accion_ui === 'MOSTRAR_RULETA') {
            removeThinkingIndicator();
            // El cerebro nos pide mostrar la ruleta, así que llamamos a la función que está justo arriba
            mostrarRuleta(respuesta.opciones_ruleta);
        } else if (respuesta.mensaje_para_ui) {
            // Es un mensaje de texto normal
            addGuardianMessage(respuesta.mensaje_para_ui);
        } else {
            // Si la respuesta no es clara, lo indicamos y lo logueamos
            removeThinkingIndicator();
            console.log("Respuesta del servidor no reconocida:", respuesta);
        }

    } catch (error) {
        console.error("Error en llamarALE:", error);
        removeThinkingIndicator();
        addGuardianMessage("Error de conexión con el núcleo A.L.E. en Render.", false);
    }
}


// (Aquí abajo estaría tu función removeThinkingIndicator y el resto del código)

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
