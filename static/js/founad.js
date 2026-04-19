// FOUNAD - JavaScript para interactividad
// Desarrollado por Daniel Grisales - 2025

// Esperar a que cargue todo el HTML antes de ejecutar
document.addEventListener("DOMContentLoaded", function () {
  // ===== SISTEMA DE ESTRELLAS =====
  const stars = document.querySelectorAll(".stars span");
  let currentRating = 0;

  stars.forEach((star) => {
    // Cuando paso el mouse por encima
    star.addEventListener("mouseover", function () {
      const rating = parseInt(this.getAttribute("data-rating"));
      highlightStars(rating);
    });

    // Cuando le doy click
    star.addEventListener("click", function () {
      currentRating = parseInt(this.getAttribute("data-rating"));
      highlightStars(currentRating);
      console.log("Calificación seleccionada:", currentRating);
      // Acá después voy a agregar el código para guardar en la base de datos
    });
  });

  // Cuando saco el mouse de las estrellas
  const starContainer = document.querySelector(".stars");
  if (starContainer) {
    starContainer.addEventListener("mouseleave", function () {
      highlightStars(currentRating);
    });
  }

  // Función para pintar las estrellas
  function highlightStars(rating) {
    stars.forEach((star, index) => {
      if (index < rating) {
        star.classList.add("filled");
        star.textContent = "★";
      } else {
        star.classList.remove("filled");
        star.textContent = "☆";
      }
    });
  }

  // ===== FORMULARIO DE DONACIÓN =====
  const donationForm = document.getElementById("donationForm");
  if (donationForm) {
    donationForm.addEventListener("submit", function (e) {
      e.preventDefault(); // Evito que recargue la página

      // Obtengo los valores del formulario
      const nombre = document.getElementById("nombre").value;
      const email = document.getElementById("email").value;
      const monto = document.getElementById("monto").value;
      const mensaje = document.getElementById("mensaje").value;

      // Valido que el monto sea mínimo 5000
      if (monto < 5000) {
        alert("El monto mínimo de donación es $5,000 COP");
        return;
      }

      // Muestro un mensaje de confirmación
      alert(
        `¡Gracias ${nombre}! Tu intención de donar $${parseInt(monto).toLocaleString()} COP ha sido registrada.\n\nPróximamente podrás completar el pago a través de nuestra pasarela.`
      );

      // Limpio el formulario
      donationForm.reset();

      // Acá después voy a agregar el código para enviar a Flask
      console.log("Donación:", { nombre, email, monto, mensaje });
    });
  }

  // ===== FORMULARIO DE SUBIR PROYECTO =====
  const uploadForm = document.getElementById("uploadForm");
  if (uploadForm) {
    uploadForm.addEventListener("submit", function (e) {
      e.preventDefault();

      // Validación básica de archivos
      const imagen = document.getElementById("imagen").files[0];
      const archivo = document.getElementById("archivo").files[0];

      // Verifico el tamaño de la imagen (máximo 5MB)
      if (imagen && imagen.size > 5 * 1024 * 1024) {
        alert("La imagen es muy pesada. El tamaño máximo es 5MB");
        return;
      }

      // Verifico el formato de la imagen
      if (imagen) {
        const validFormats = ["image/jpeg", "image/jpg", "image/png"];
        if (!validFormats.includes(imagen.type)) {
          alert("Solo se permiten imágenes JPG o PNG");
          return;
        }
      }

      alert(
        "¡Proyecto enviado exitosamente!\n\nPróximamente lo vas a poder ver publicado en la galería."
      );

      // Acá después voy a enviar el formulario real a Flask
      console.log("Proyecto enviado");
    });
  }

  // ===== FORMULARIO DE CONTACTO =====
  const contactForm = document.getElementById("contactForm");
  if (contactForm) {
    contactForm.addEventListener("submit", function (e) {
      e.preventDefault();

      const nombre = document.getElementById("nombre").value;
      const email = document.getElementById("email").value;
      const asunto = document.getElementById("asunto").value;
      const mensaje = document.getElementById("mensaje").value;

      alert(
        `¡Gracias ${nombre}!\n\nTu mensaje ha sido enviado. Te vamos a responder a ${email} lo más pronto posible.`
      );

      contactForm.reset();

      console.log("Contacto:", { nombre, email, asunto, mensaje });
    });
  }

  // ===== ANIMACIÓN DE LA BARRA DE PROGRESO =====
  const progressBar = document.getElementById("progressBar");
  if (progressBar) {
    // Animación suave al cargar la página
    setTimeout(() => {
      progressBar.style.width = progressBar.style.width || "30%";
    }, 100);
  }

  // ===== VALIDACIÓN EN TIEMPO REAL =====
  // Para el campo de monto en donaciones
  const montoInput = document.getElementById("monto");
  if (montoInput) {
    montoInput.addEventListener("input", function () {
      const valor = parseInt(this.value);
      if (valor < 5000 && valor > 0) {
        this.style.borderColor = "#e74c3c";
      } else {
        this.style.borderColor = "#4635b7";
      }
    });
  }

  // ===== CONFIRMACIÓN ANTES DE SALIR CON FORMULARIO LLENO =====
  let formChanged = false;
  const allForms = document.querySelectorAll("form");

  allForms.forEach((form) => {
    const inputs = form.querySelectorAll("input, textarea, select");
    inputs.forEach((input) => {
      input.addEventListener("change", function () {
        formChanged = true;
      });
    });

    form.addEventListener("submit", function () {
      formChanged = false;
    });
  });

  window.addEventListener("beforeunload", function (e) {
    if (formChanged) {
      e.preventDefault();
      e.returnValue = "";
      return "";
    }
  });

  console.log("FOUNAD cargado exitosamente ✓");
});
