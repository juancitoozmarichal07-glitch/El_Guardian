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

// Reemplaza tu función addGuardianMessage por esta:
function addGuardianMessage(texto, conTypewriter = true) {
    const messageBubble = document.createElement('div');
    messageBubble.className = 'message-bubble guardian-message';
    history.appendChild(messageBubble);
    
    if (conTypewriter && texto) { // Añadida comprobación de que 'texto' no sea nulo
        let i = 0;
        const speed = 20;
        
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
// En tu main.js, reemplaza la función mostrarRuleta por esta:

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
            clearInterval(intervalId); // Detenemos la animación, pero NO borramos la ruleta.
            
            const eleccionFinal = opcionesEl[randomIndex].textContent;
            
            // --- ¡AQUÍ ESTÁ LA NUEVA LÓGICA! ---

            // 1. Inmediatamente enviamos la elección al cerebro.
            // El cerebro responderá con el mensaje de confirmación ("Misión elegida: ...")
            // y ese mensaje aparecerá en pantalla MIENTRAS la ruleta todavía es visible.
            llamarALE(eleccionFinal);

            // 2. Esperamos un par de segundos para que el usuario vea todo junto.
            setTimeout(() => {
                // 3. Ahora sí, limpiamos la ruleta de la pantalla.
                ruletaContainer.remove();
                
                // 4. Y reactivamos la caja de texto para que el usuario pueda continuar.
                chatInput.disabled = false;
                sendButton.disabled = false;
                chatInput.focus();
            }, 2500); // Le damos 2.5 segundos. Puedes ajustar este tiempo.
        }
    }, shuffleInterval);
}


// --- LÓGICA DE COMUNICACIÓN CON EL CEREBRO (A.L.E.) ---
// En tu main.js, reemplaza la función llamarALE por esta:
async function llamarALE(comando) {
    showThinkingIndicator();

    try {
        const respuestaServidor = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                comando: comando,
                skillset_target: 'guardian',
                estado_conversacion: estadoConversacion
            })
        });

        if (!respuestaServidor.ok) {
            throw new Error('Error de red o del servidor A.L.E.');
        }

        const respuesta = await respuestaServidor.json();
        removeThinkingIndicator();

        // --- ¡AQUÍ ESTÁ LA LÓGICA CLAVE! ---

        // 1. Si el servidor nos manda un historial, es la carga inicial del día.
        if (respuesta.historial_para_ui && Array.isArray(respuesta.historial_para_ui)) {
            history.innerHTML = ''; // Limpiamos el chat.
            respuesta.historial_para_ui.forEach(mensaje => {
                if (mensaje.role === 'user') {
                    addUserMessage(mensaje.content);
                } else if (mensaje.role === 'assistant') {
                    addGuardianMessage(mensaje.content, false); // Sin efecto máquina de escribir
                }
            });
        }

        // 2. Si hay una acción UI (como la ruleta), la ejecutamos.
        if (respuesta.accion_ui) {
            if (respuesta.accion_ui === 'MOSTRAR_RULETA') {
                mostrarRuleta(respuesta.opciones_ruleta);
            }
        } 
        // 3. Si hay un mensaje nuevo, lo añadimos.
        else if (respuesta.mensaje_para_ui) {
            addGuardianMessage(respuesta.mensaje_para_ui, true); // Con efecto máquina de escribir
        }

        // 4. Actualizamos el estado de la conversación.
        if (respuesta.nuevo_estado) {
            estadoConversacion = respuesta.nuevo_estado;
        }

    } catch (error) {
        console.error("Error en llamarALE:", error);
        removeThinkingIndicator();
        addGuardianMessage("Error de conexión con el núcleo A.L.E. en Render.", false);
    }
}

