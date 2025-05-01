// Función para inicializar tooltips de Bootstrap
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto fade-out para alertas
    setTimeout(function() {
        var alertList = document.querySelectorAll('.alert');
        alertList.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000); // 5 segundos

    // Animación de entrada para los elementos de la cuadrícula de productos
    const productoCards = document.querySelectorAll('.producto-card');
    if (productoCards.length > 0) {
        productoCards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';

            setTimeout(() => {
                card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 100 * index); // Efecto escalonado
        });
    }

    // Configurar previsualizaciones de imágenes en formularios de carga
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const previewId = this.dataset.preview;
            if (previewId && this.files && this.files[0]) {
                const previewElement = document.getElementById(previewId);
                if (previewElement) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        previewElement.src = e.target.result;
                        previewElement.style.display = 'block';
                    };
                    reader.readAsDataURL(this.files[0]);
                }
            }
        });
    });
});

// Función para manejar los botones de like/dislike
// Función para manejar los botones de like/dislike
function interactuar(tipo, productoId) {
    // Obtener el token CSRF de la página
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    fetch(`/producto/${productoId}/interaccion`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken
        },
        body: `tipo=${tipo}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Actualizar elementos visuales de la página
            const likeBtn = document.getElementById('like-btn');
            const dislikeBtn = document.getElementById('dislike-btn');
            const likesCount = document.getElementById('likes-count');
            const dislikesCount = document.getElementById('dislikes-count');

            // Actualizar contadores con los valores devueltos
            likesCount.textContent = data.likes;
            dislikesCount.textContent = data.dislikes;

            if (tipo === 'like') {
                if (data.action === 'added' || data.action === 'changed') {
                    likeBtn.classList.add('active-like');
                    dislikeBtn.classList.remove('active-dislike');
                } else if (data.action === 'removed') {
                    likeBtn.classList.remove('active-like');
                }
            } else if (tipo === 'dislike') {
                if (data.action === 'added' || data.action === 'changed') {
                    dislikeBtn.classList.add('active-dislike');
                    likeBtn.classList.remove('active-like');
                } else if (data.action === 'removed') {
                    dislikeBtn.classList.remove('active-dislike');
                }
            }
        }
    })
    .catch(error => {
        console.error('Error al procesar la interacción:', error);
    });
}

// Función para añadir/quitar producto de favoritos
function toggleFavorito(productoId) {
    // Obtener el token CSRF de la página
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    fetch(`/producto/${productoId}/favorito`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const favoriteBtn = document.getElementById('favorite-btn');

            if (data.action === 'added') {
                favoriteBtn.classList.add('active-favorite');
                // Mostrar mensaje de éxito temporal
                showToast('Producto añadido a favoritos');
            } else {
                favoriteBtn.classList.remove('active-favorite');
                // Mostrar mensaje de éxito temporal
                showToast('Producto eliminado de favoritos');
            }
        }
    })
    .catch(error => {
        console.error('Error al procesar favorito:', error);
    });
}

// Función para mostrar un mensaje toast
function showToast(message) {
    // Verificar si ya existe un contenedor de toasts
    let toastContainer = document.querySelector('.toast-container');

    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }

    // Crear el elemento toast
    const toastElement = document.createElement('div');
    toastElement.className = 'toast';
    toastElement.setAttribute('role', 'alert');
    toastElement.setAttribute('aria-live', 'assertive');
    toastElement.setAttribute('aria-atomic', 'true');

    toastElement.innerHTML = `
        <div class="toast-header">
            <strong class="me-auto">PinProducts</strong>
            <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;

    toastContainer.appendChild(toastElement);

    // Inicializar y mostrar el toast
    const toast = new bootstrap.Toast(toastElement, {
        delay: 3000
    });
    toast.show();

    // Eliminar el toast del DOM cuando se oculta
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

// Función para cambiar imagen principal en detalle de producto
function cambiarImagen(rutaImagen) {
    const imagenPrincipal = document.getElementById('imagen-principal');

    // Si hay un video activo, reemplazarlo con la imagen
    const contenedorMedia = imagenPrincipal.parentElement;
    const videoContainer = contenedorMedia.querySelector('.video-container');

    if (videoContainer) {
        // Crear nueva imagen
        const nuevaImagen = document.createElement('img');
        nuevaImagen.src = rutaImagen;
        nuevaImagen.id = 'imagen-principal';
        nuevaImagen.className = 'producto-imagen mb-3';
        nuevaImagen.alt = 'Imagen del producto';

        // Reemplazar video con imagen
        contenedorMedia.replaceChild(nuevaImagen, videoContainer);
    } else {
        // Solo actualizar la src de la imagen existente
        imagenPrincipal.src = rutaImagen;
    }
}

// Función para mostrar video en detalle de producto
function mostrarVideo(rutaVideo) {
    const imagenPrincipal = document.getElementById('imagen-principal');
    const contenedorMedia = imagenPrincipal.parentElement;

    // Crear contenedor de video
    const videoContainer = document.createElement('div');
    videoContainer.className = 'video-container mb-3';

    // Crear elemento de video
    const video = document.createElement('video');
    video.controls = true;
    video.autoplay = true;

    // Crear source para el video
    const source = document.createElement('source');
    source.src = rutaVideo;
    source.type = 'video/mp4';

    // Mensaje de fallback
    const fallback = document.createTextNode('Tu navegador no soporta videos HTML5.');

    // Estructurar elementos
    video.appendChild(source);
    video.appendChild(fallback);
    videoContainer.appendChild(video);

    // Reemplazar imagen con video
    contenedorMedia.replaceChild(videoContainer, imagenPrincipal);
}

// Función para previsualizar imagen antes de subirla
function previewImage(input, previewElement) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();

        reader.onload = function(e) {
            document.getElementById(previewElement).src = e.target.result;
            document.getElementById(previewElement).style.display = 'block';
        };

        reader.readAsDataURL(input.files[0]);
    }
}