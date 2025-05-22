document.addEventListener("DOMContentLoaded", function () {

    // Sincroniza el desplegable de OID con el campo editable
    document.getElementById("oid_select").addEventListener("change", function () {
        document.getElementById("oid_input").value = this.value;
    });

    const versionSelect = document.getElementById("version_select");
    const communityContainer = document.getElementById("community_container");
    const v3Fields = document.getElementById("v3_fields");
    const v3ModeSelect = document.getElementById("v3_mode_select");
    const authFields = document.getElementById("auth_fields");
    const privFields = document.getElementById("priv_fields");
    const encryptFields = document.getElementById("encrypt_fields");

    // Función para ajustar el formulario según la versión SNMP seleccionada
    function adjustFormByVersion() {
        if (versionSelect.value === "v3") {
            // Mostrar campos SNMPv3 y ocultar los de community
            v3Fields.style.display = "block";
            communityContainer.style.display = "none";
        } else {
            // Volver a los campos tradicionales para v1 y v2c
            v3Fields.style.display = "none";
            communityContainer.style.display = "block";
        }
    }

    // Función para ajustar los campos de autenticación en SNMPv3
    function adjustV3Fields() {
        const mode = v3ModeSelect.value;
        if (mode === "noauth") {
            authFields.style.display = "none";
            privFields.style.display = "none";
            encryptFields.style.display = "none";
        } else if (mode === "auth") {
            // Muestra el campo de autenticación y el método de encriptado
            authFields.style.display = "block";
            privFields.style.display = "none";
            encryptFields.style.display = "block";
        } else if (mode === "priv") {
            // Muestra autenticación, privacidad y el método de encriptado
            authFields.style.display = "block";
            privFields.style.display = "block";
            encryptFields.style.display = "block";
        }
    }

    versionSelect.addEventListener("change", adjustFormByVersion);
    v3ModeSelect.addEventListener("change", adjustV3Fields);

    // Inicializar formulario
    adjustFormByVersion();
    adjustV3Fields();
});