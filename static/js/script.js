document.addEventListener('DOMContentLoaded', function () {
    console.log("DOMContentLoaded ejecutado para script.js");

    const modalElement = document.getElementById('modalVencidos');
    const listaVencidos = document.getElementById('lista-vencidos');

    // Si en esta página no hay modal o no hay lista, no hacemos nada
    if (!modalElement || !listaVencidos) {
        console.log("No hay modal o lista de vencidos en esta página.");
        return;
    }

    // Buscar al menos un <li> que NO tenga data-empty="true"
    const loteReal = listaVencidos.querySelector('li:not([data-empty="true"])');

    if (!loteReal) {
        console.log("No hay lotes vencidos reales. No se muestra el modal.");
        return;
    }

    console.log("Se encontraron lotes vencidos. Mostrando modal...");

    // Crear (o reutilizar) la instancia de Bootstrap Modal y mostrarla
    const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
    modal.show();
});