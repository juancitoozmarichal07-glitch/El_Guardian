// =================================================================
// MAIN.JS - v2.0 CON PERSISTENCIA LOCAL
// Guarda el historial del chat en el navegador para que no se
// pierda al cerrar la aplicación.
// =================================================================

// --- CONFIGURACIÓN GLOBAL Y ESTADO DEL CLIENTE ---
const NOMBRE_USUARIO = "Juan";
const URL_ALE_SERVER = 'https://el-guardian.onrender.com/execute';
let estadoConversacion = { modo: 'libre' };

// --- REFERENCIAS AL DOM ---
let bootContainer, bootMessage, appContainer, history, chatInput, sendButton, navBar, screens;

// --- SETUP INICIAL DE LA APLICACIÓN ---
document.addEventListener('DOMContentLoaded', () => {
    bootContainer = document.getElementById('boot-container');
    bootMessage = document.getElementById('boot-message');
    appContainer = document.getElementById('app-container');
    history = document.getElementById('history');
    chatInput = document.getElementById('chat-input');
    sendButton = document.getElementById('send-button');
    navBar = document.getElementById('nav-bar');
    screens = document.querySelectorAll('.screen');

    setupEventListeners();
    iniciarSecuenciaArranque();
});

function setupEventListeners() {
    sendButton.addEventListener('click', () => {
        const comando = chatInput.value.trim();
        if (comando) {
            procesarComandoUsuario(comando);
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

// --- NUEVAS FUNCIONES DE PERSISTENCIA CON LOCALSTORAGE ---
function guardarHistorial() {
    localStorage.setItem('guardian_chat_history', history.innerHTML);
    localStorage.setItem('guardian_chat_state', JSON.stringify(estadoConversacion));
}

function cargarHistorial() {
    const historialGuardado = localStorage.getItem('guardian_chat_history');
    const estadoGuardado = localStorage.getItem('guardian_chat_state');

    if (historialGuardado && estadoGuardado) {
        history.innerHTML = historialGuardado;
        estadoConversacion = JSON.parse(estadoGuardado);
        history.scrollTop = history.scrollHeight;
        return true; // Éxito: se cargó un historial.
    }
    
    return false; // Fracaso: no había nada que cargar.
}

// --- SECUENCIA DE ARRANQUE VISUAL (CON PERSISTENCIA) ---
function iniciarSecuenciaArranque() {
    const mensajes = [
        "Iniciando Guardian OS...",
        "Verificando memoria persistente...",
        `Listo para la acción.`
    ];
    let i = 0;

    function siguienteMensaje() {
        if (i < mensajes.length) {
            bootMessage.textContent = mensajes[i];
            i++;
            setTimeout(siguienteMensaje, 1200);
        } else {
            bootContainer.classList.add('hidden');
            appContainer.classList.remove('hidden');
            chatInput.focus();
            
            const historialCargado = cargarHistorial();
            
            if (!historialCargado) {
                llamarALE("_SALUDO_INICIAL_");
            }
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
    guardarHistorial(); // Guardamos después de añadir mensaje de usuario.
}

function addGuardianMessage(texto, conTypewriter = true) {
    const messageBubble = document.createElement('div');
    messageBubble.className = 'message-bubble guardian-message';
    history.appendChild(messageBubble);
    
    if (conTypewriter && texto) {
        let i = 0;
        const speed = 20;
        
        function typeWriter() {
            if (i < texto.length) {
                messageBubble.textContent += texto.charAt(i);
                i++;
                history.scrollTop = history.scrollHeight;
                setTimeout(typeWriter, speed);
            } else {
                guardarHistorial(); // Guardamos cuando termina de escribir.
            }
        }
        typeWriter();
    } else {
        messageBubble.textContent = texto;
        guardarHistorial(); // Guardamos para mensajes sin animación.
    }
    history.scrollTop = history.scrollHeight;
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
            
            llamarALE(eleccionFinal);

            setTimeout(() => {
                ruletaContainer.remove();
                chatInput.disabled = false;
                sendButton.disabled = false;
                chatInput.focus();
            }, 2500);
        }
    }, shuffleInterval);
}

// --- LÓGICA DE COMUNICACIÓN CON EL CEREBRO (A.L.E.) ---
async function llamarALE(comando) {
    showThinkingIndicator();

    try {
        const respuestaServidor = await fetch(URL_ALE_SERVER, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                comando: comando,
                skillset_target: 'guardian',
                estado_conversacion: estadoConversacion
            })
        });

        if (!respuestaServidor.ok) {
            throw new Error(`Error ${respuestaServidor.status} del servidor A.L.E.`);
        }

        const respuesta = await respuestaServidor.json();
        removeThinkingIndicator();

        if (respuesta.accion_ui) {
            if (respuesta.accion_ui === 'MOSTRAR_RULETA') {
                mostrarRuleta(respuesta.opciones_ruleta);
            }
        } 
        else if (respuesta.mensaje_para_ui) {
            addGuardianMessage(respuesta.mensaje_para_ui, true);
        }

        if (respuesta.nuevo_estado) {
            estadoConversacion = respuesta.nuevo_estado;
            // Guardamos el estado después de recibirlo del servidor.
            // Esto es importante para que el estado también sea persistente.
            guardarHistorial();
        }

    } catch (error) {
        console.error("Error en llamarALE:", error);
        removeThinkingIndicator();
        addGuardianMessage("Error de conexión con el núcleo A.L.E. Revisa la consola.", false);
    }
}
