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

window.addEventListener("resize", function(){

    if (window.innerWidth > 760){

        body.classList.remove("body_move");
        side_menu.classList.remove("menu__side_move");
    }

    if (window.innerWidth < 760){

        body.classList.add("body_move");
        side_menu.classList.add("menu__side_move");
    }

});

document.addEventListener("DOMContentLoaded", () => {
    // Obtener las opciones del menú
    const options = document.querySelectorAll(".options__menu a");

    // Recorrer cada opción y agregar un listener de evento de clic
    options.forEach(option => {
        option.addEventListener("click", function (event) {
            event.preventDefault(); // Prevenir la acción predeterminada del enlace
            
            // Remover la clase "selected" de la opción previamente seleccionada
            const prevSelected = document.querySelector(".options__menu .selected");
            if (prevSelected) {
                prevSelected.classList.remove("selected");
            }

            // Agregar la clase "selected" a la opción actualmente seleccionada
            option.classList.add("selected");

            // Mover la barra seleccionada a la opción actualmente seleccionada
            // Ajustar la posición de la barra si existe
            const selectedBar = document.querySelector(".selected-bar");
            if (selectedBar) {
                selectedBar.style.top = `${option.offsetTop}px`; // Ajustar la posición de la barra
            }

            // Redirigir a la URL del enlace después de aplicar la selección
            window.location.href = option.href;
        });
    });
});



