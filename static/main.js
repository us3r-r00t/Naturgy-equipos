let equipoSeleccionado = "";

// Enlaces oficiales de Canva por equipo
const CANVA_URLS = {
    "NATURGY ENERGIA SAN JUAN": "https://www.canva.com/design/DAHXwZUnr0k/JvD_ZzvuYPamtZx-xmNVXA/view?embed",
    "NATURGY BAN CAU": "https://www.canva.com/design/DAHXvwwRNs8/HhYMcTWKdey1NQEEBDMCsA/view?embed",
    "NATURGY NOA CAU": "https://www.canva.com/design/DAHXwQ2dCFQ/tFmXhbv0Zhq2woI_AlnmkA/view?embed"
};

// Carga de la Nómina con "Líder:"
function cargarNomina(equipo) {
    const container = document.getElementById("nomina-container");
    if (!container) return;

    if (equipo === "NATURGY BAN CAU") {
        container.innerHTML = `
            <div class="nomina-header">
                <img src="/static/naturgy.png" alt="Logo Naturgy" class="logo-naturgy" onerror="this.style.display='none'">
                <h2>Nómina Oficial - Naturgy BAN CAU</h2>
            </div>

            <div class="nomina-grid">
                <!-- Nómina Karina Parra -->
                <div class="nomina-card">
                    <div class="supervisor-title">
                        <svg class="tab-icon" viewBox="0 0 24 24"><path fill="currentColor" d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>
                        Líder: Karina Parra
                    </div>
                    <table class="tabla-nomina">
                        <thead>
                            <tr>
                                <th>Legajo</th>
                                <th>Apellido</th>
                                <th>Nombre</th>
                                <th>Turno</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td>22432</td><td>Escobar</td><td>Ariana Lucia</td><td><span class="badge-turno tt">TT</span></td></tr>
                            <tr><td>20436</td><td>Herbas</td><td>Alejandra</td><td><span class="badge-turno tt">TT</span></td></tr>
                            <tr><td>21740</td><td>Quintana</td><td>Melisa</td><td><span class="badge-turno tm">TM</span></td></tr>
                            <tr><td>22438</td><td>Rios</td><td>Gian Franco Gabriel</td><td><span class="badge-turno tm">TM</span></td></tr>
                        </tbody>
                    </table>
                </div>

                <!-- Nómina Leila Herrera -->
                <div class="nomina-card">
                    <div class="supervisor-title">
                        <svg class="tab-icon" viewBox="0 0 24 24"><path fill="currentColor" d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>
                        Líder: Leila Herrera
                    </div>
                    <table class="tabla-nomina">
                        <thead>
                            <tr>
                                <th>Legajo</th>
                                <th>Apellido</th>
                                <th>Nombre</th>
                                <th>Turno</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td>22434</td><td>Ganino</td><td>Luciano Ian</td><td><span class="badge-turno tm">TM</span></td></tr>
                            <tr><td>22439</td><td>Arce</td><td>Candela</td><td><span class="badge-turno tm">TM</span></td></tr>
                            <tr><td>22440</td><td>Rios</td><td>Axel Rodrigo</td><td><span class="badge-turno tm">TM</span></td></tr>
                            <tr><td>22441</td><td>Ruiz Dominguez</td><td>Florencia Azul</td><td><span class="badge-turno tt">TT</span></td></tr>
                            <tr><td>22442</td><td>Garcia</td><td>Victoria Maria</td><td><span class="badge-turno tt">TT</span></td></tr>
                            <tr><td>23827</td><td>Gonzalez</td><td>Vanesa</td><td><span class="badge-turno tm">TM</span></td></tr>
                            <tr><td>23759</td><td>Bogado Barreto</td><td>Nadia Noemi</td><td><span class="badge-turno tm">TM</span></td></tr>
                            <tr><td>311198</td><td>Gonzalez</td><td>Sandra</td><td><span class="badge-turno tm">TM</span></td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    } else {
        container.innerHTML = `
            <div class="placeholder-box">
                <p>Nómina de personal para <strong>${equipo}</strong> en proceso de carga.</p>
            </div>
        `;
    }
}

// Función ejecutada al cambiar el mes en Logueos, Calidad o Métricas
function cambiarMes(pestana, valorMes) {
    console.log(`Cambio de mes en la pestaña ${pestana}: ${valorMes}`);
    if (pestana === 'logueos') {
        cargarReporte();
    }
}

function cambiarPestana(nombrePestana, event) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

    const tabTarget = document.getElementById('tab-' + nombrePestana);
    if (tabTarget) {
        tabTarget.classList.add('active');
    }

    if (event && event.currentTarget) {
        event.currentTarget.classList.add('active');
    }
}

function cargarInfoCampana(equipo) {
    const container = document.getElementById("canva-container");
    const title = document.getElementById("campana-title");
    
    const urlCanva = CANVA_URLS[equipo] || CANVA_URLS["NATURGY BAN CAU"];
    title.innerText = "📢 Información de Campaña - " + equipo;
    
    container.innerHTML = `
        <div class="canva-responsive-wrapper">
            <iframe loading="lazy" src="${urlCanva}" allowfullscreen="allowfullscreen" allow="fullscreen"></iframe>
        </div>
    `;
}

function abrirLogin(nombreEquipo) {
    equipoSeleccionado = nombreEquipo;
    document.getElementById("modalTitle").innerText = "Acceso a " + nombreEquipo;
    document.getElementById("loginModal").style.display = "block";
    document.getElementById("usuario").focus();
}

function cerrarLogin() {
    document.getElementById("loginModal").style.display = "none";
    document.getElementById("usuario").value = "";
    document.getElementById("password").value = "";
}

// Activar paneles de Líder en todas las pestañas al iniciar sesión
function actualizarPanelesLider(rol) {
    const esLider = (rol === "lider");
    
    const paneles = [
        document.getElementById("leader-panel"),
        document.getElementById("leader-panel-calidad-resumen"),
        document.getElementById("leader-panel-calidad-detalle")
    ];

    paneles.forEach(panel => {
        if (panel) {
            panel.style.display = esLider ? "block" : "none";
        }
    });
}

// En la función validarAcceso(event), agregar la llamada a actualizarPanelesLider:
function validarAcceso(event) {
    event.preventDefault();

    const usuarioInput = document.getElementById("usuario").value.trim();
    const passwordInput = document.getElementById("password").value.trim();

    fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            usuario: usuarioInput,
            password: passwordInput,
            equipo: equipoSeleccionado
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            cerrarLogin();

            document.getElementById("equipo-section").style.display = "none";
            document.getElementById("dashboard-section").style.display = "block";

            document.getElementById("user-display").innerText = data.usuario;
            document.getElementById("team-display").innerText = data.equipo;
            document.getElementById("role-display").innerText = data.rol.toUpperCase();

            // 🎯 Muestra u oculta los paneles de subida según el ROL
            actualizarPanelesLider(data.rol);

            const firstTabBtn = document.querySelector('.tab-btn');
            cambiarPestana('nomina', { currentTarget: firstTabBtn });

            cargarNomina(data.equipo);
            cargarReporte();
            cargarInfoCampana(data.equipo);
        } else {
            alert("❌ Error: " + data.message);
        }
    });
}



function cargarReporte() {
    const tableContainer = document.getElementById("table-container");
    if (!tableContainer) return;

    tableContainer.innerHTML = "<p>Cargando información de logueos del equipo...</p>";

    fetch("/obtener_reporte")
    .then(response => response.json())
    .then(data => {
        if (data.success && data.html_tabla) {
            tableContainer.innerHTML = data.html_tabla;
        } else {
            tableContainer.innerHTML = `<p>${data.message || "No hay reportes cargados aún para este equipo."}</p>`;
        }
    })
    .catch(error => {
        console.error("Error al obtener el reporte:", error);
        tableContainer.innerHTML = "<p>Ocurrió un error al cargar la información.</p>";
    });
}

function subirArchivo() {
    const fileInput = document.getElementById("excelFile");

    if (!fileInput || fileInput.files.length === 0) {
        alert("⚠️ Por favor selecciona un archivo (.xlsx, .xls o .csv) antes de presionar subir.");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    fetch("/upload", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("✅ " + data.message);
            fileInput.value = "";
            cargarReporte();
        } else {
            alert("❌ Error: " + data.message);
        }
    })
    .catch(error => {
        console.error("Error al subir archivo:", error);
        alert("❌ Error de comunicación al intentar subir el archivo.");
    });
}

function cerrarSesion() {
    fetch("/logout", { method: "POST" })
    .then(() => {
        document.getElementById("dashboard-section").style.display = "none";
        document.getElementById("equipo-section").style.display = "flex";
        alert("Sesión cerrada correctamente.");
    })
    .catch(error => {
        console.error("Error al cerrar sesión:", error);
        document.getElementById("dashboard-section").style.display = "none";
        document.getElementById("equipo-section").style.display = "flex";
    });
}
// ==========================================
// CONTROL DEL MODO OSCURO (DARK MODE)
// ==========================================

function aplicarTema(esOscuro) {
    const sunIcon = document.getElementById("theme-icon-sun");
    const moonIcon = document.getElementById("theme-icon-moon");
    const themeText = document.getElementById("theme-toggle-text");

    if (esOscuro) {
        document.body.classList.add("dark-mode");
        if (sunIcon) sunIcon.style.display = "inline";
        if (moonIcon) moonIcon.style.display = "none";
        if (themeText) themeText.innerText = "Modo Claro";
        localStorage.setItem("naturgy_theme", "dark");
    } else {
        document.body.classList.remove("dark-mode");
        if (sunIcon) sunIcon.style.display = "none";
        if (moonIcon) moonIcon.style.display = "inline";
        if (themeText) themeText.innerText = "Modo Oscuro";
        localStorage.setItem("naturgy_theme", "light");
    }
}

function toggleDarkMode() {
    const esOscuroActual = document.body.classList.contains("dark-mode");
    aplicarTema(!esOscuroActual);
}

// Cargar preferencia guardada al iniciar la página
document.addEventListener("DOMContentLoaded", () => {
    const temaGuardado = localStorage.getItem("naturgy_theme");
    if (temaGuardado === "dark") {
        aplicarTema(true);
    } else {
        aplicarTema(false);
    }
});
// Control de sub-pestañas internas en el módulo de Calidad
function cambiarSubpestanaCalidad(subpestana, event) {
    document.querySelectorAll('#tab-calidad .subtab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('#tab-calidad .subtab-content').forEach(content => content.classList.remove('active'));

    const subtabTarget = document.getElementById('subtab-calidad-' + subpestana);
    if (subtabTarget) {
        subtabTarget.classList.add('active');
    }

    if (event && event.currentTarget) {
        event.currentTarget.classList.add('active');
    }
}

// Carga del archivo Excel de Detalle de Calidad
function subirArchivoCalidad() {
    const fileInput = document.getElementById("excelCalidadFile");

    if (!fileInput || fileInput.files.length === 0) {
        alert("⚠️ Por favor selecciona un archivo Excel de Calidad antes de presionar subir.");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    fetch("/upload_calidad", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("✅ " + data.message);
            fileInput.value = "";
            const container = document.getElementById("table-calidad-detalle-container");
            if (container && data.html_tabla) {
                container.innerHTML = data.html_tabla;
            }
        } else {
            alert("❌ Error: " + data.message);
        }
    })
    .catch(error => {
        console.error("Error al subir planilla de calidad:", error);
        alert("❌ Ocurrió un error de comunicación al subir la planilla.");
    });
}

// Mostrar el panel de líder en calidad si el usuario tiene rol 'lider'
function actualizarPanelesLider(rol) {
    const leaderPanelLogueos = document.getElementById("leader-panel");
    const leaderPanelCalidad = document.getElementById("leader-panel-calidad");
    
    if (rol === "lider") {
        if (leaderPanelLogueos) leaderPanelLogueos.style.display = "block";
        if (leaderPanelCalidad) leaderPanelCalidad.style.display = "block";
    } else {
        if (leaderPanelLogueos) leaderPanelLogueos.style.display = "none";
        if (leaderPanelCalidad) leaderPanelCalidad.style.display = "none";
    }
}
// Subida de Planilla Resumen de Calidad
function subirArchivoCalidadResumen() {
    const fileInput = document.getElementById("excelCalidadResumenFile");

    if (!fileInput || fileInput.files.length === 0) {
        alert("⚠️ Por favor selecciona un archivo Excel para el Resumen de Calidad.");
        return;
    }

    const formData = new FormData();
    // 🎯 CORREGIDO: Enviar el primer archivo seleccionado (índice 0)
    formData.append("file", fileInput.files[0]);

    fetch("/upload_calidad_resumen", {
        method: "POST",
        body: formData
    })
    .then(async response => {
        const data = await response.json();
        if (!response.ok || !data.success) {
            throw new Error(data.message || "Error en el servidor al procesar el archivo.");
        }
        return data;
    })
    .then(data => {
        alert("✅ " + data.message);
        fileInput.value = "";
        const container = document.getElementById("table-calidad-resumen-container");
        if (container && data.html_tabla) {
            container.innerHTML = data.html_tabla;
        }
    })
    .catch(error => {
        console.error("Error al subir planilla resumen:", error);
        alert("❌ Error: " + error.message);
    });
}

function subirArchivoCalidadResumen() {
    const fileInput = document.getElementById("excelCalidadResumenFile");

    if (!fileInput || fileInput.files.length === 0) {
        alert("⚠️ Por favor selecciona un archivo Excel para el Resumen de Calidad.");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    fetch("/upload_calidad_resumen", {
        method: "POST",
        body: formData
    })
    .then(async response => {
        const text = await response.text(); // Lee la respuesta como texto primero
        try {
            const data = JSON.parse(text);
            if (!response.ok || !data.success) {
                throw new Error(data.message || "Error en el servidor.");
            }
            return data;
        } catch (e) {
            // Si no era un JSON válido, muestra el mensaje HTML de error
            console.error("Respuesta completa del servidor:", text);
            throw new Error("El servidor devolvió un error (Código " + response.status + "). Revisa la consola de Python.");
        }
    })
    .then(data => {
        alert("✅ " + data.message);
        fileInput.value = "";
        const container = document.getElementById("table-calidad-resumen-container");
        if (container && data.html_tabla) {
            container.innerHTML = data.html_tabla;
        }
    })
    .catch(error => {
        console.error("Error al subir planilla resumen:", error);
        alert("❌ Error: " + error.message);
    });
}

// Mostrar los paneles de carga si el rol es 'lider'
function actualizarPanelesLider(rol) {
    const panelesLider = [
        document.getElementById("leader-panel"),
        document.getElementById("leader-panel-calidad-resumen"),
        document.getElementById("leader-panel-calidad-detalle")
    ];

    panelesLider.forEach(panel => {
        if (panel) {
            panel.style.display = (rol === "lider") ? "block" : "none";
        }
    });
}