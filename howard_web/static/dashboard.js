(function () {
  const currentPath = window.location.pathname;

  switch (currentPath) {
    case '/dashboard':
      const elementoRaiz = document.querySelector("#option-raiz");
      elementoRaiz.classList.add("selected");
      break;
    case '/grupo':
      const elementoGrupo = document.querySelector("#option-grupo");
      elementoGrupo.classList.add("selected");
      break;
    case '/alumno':
      const elementoAlumno = document.querySelector("#option-alumno");
      elementoAlumno.classList.add("selected");
      break;
    case '/profesor':
      const elementoProfesor = document.querySelector("#option-profesor");
      elementoProfesor.classList.add("selected");
      break;
    case '/horario':
      const elementoHorario = document.querySelector("#option-horario");
      elementoHorario.classList.add("selected");
      break;
    case '/tipo_turno':
      const elementoTipoTurno = document.querySelector("#option-tipo-turno");
      elementoTipoTurno.classList.add("selected");
      break;
    case '/pago':
      const elementoPago = document.querySelector("#option-pago");
      elementoPago.classList.add("selected");
      break;
    case '/tipo_pago':
      const elementoTipoPago = document.querySelector("#option-tipo-pago");
      elementoTipoPago.classList.add("selected");
      break;
  }
})();

//Ejecutar función en el evento click
document.getElementById("btn_open").addEventListener("click", open_close_menu);

//Declaramos variables
var side_menu = document.getElementById("menu_side");
var btn_open = document.getElementById("btn_open");
var body = document.getElementById("body");

//Evento para mostrar y ocultar menú
function open_close_menu(){
    body.classList.toggle("body_move");
    side_menu.classList.toggle("menu__side_move");
}

//Si el ancho de la página es menor a 760px, ocultará el menú al recargar la página
if (window.innerWidth < 760){
    body.classList.add("body_move");
    side_menu.classList.add("menu__side_move");
}

//Haciendo el menú responsive(adaptable)
window.addEventListener("resize", function() {
    if (window.innerWidth > 760){
        body.classList.remove("body_move");
        side_menu.classList.remove("menu__side_move");
    }

    if (window.innerWidth < 760){
        body.classList.add("body_move");
        side_menu.classList.add("menu__side_move");
    }
});
