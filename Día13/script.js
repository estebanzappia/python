document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.querySelector('form');
  const usuarioInput = document.getElementById('usuario');
  const claveInput = document.getElementById('clave');

  loginForm.addEventListener('submit', (event) => {

    event.preventDefault();

    const usuario = usuarioInput.value.trim();
    const clave = claveInput.value.trim();


    if (!usuario || !clave) {
      alert('Por favor, completa todos los campos.');
      return;
    }


    alert(`¡Bienvenido de nuevo, ${usuario}! Redirigiendo a Orkut...`);


    loginForm.reset();
  });
});