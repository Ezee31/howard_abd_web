$(document).ready(function() {
  // valores por defecto
  $('#alumno-form').hide();
  $('#alumno-creado').hide();
  $('#todo-bien').hide();
  $('#todo-mal').hide();
  localStorage.setItem('tipos_pagos', JSON.stringify([]));

  // leyendo todos los tipos de pagos regresados por python
  document
    .querySelectorAll('.purpose-radio')
    .forEach(divTipoPago => {
      const tiposPagos = JSON.parse(localStorage.getItem('tipos_pagos'));
      const { tipoPagoId, tipoPagoNombre } = divTipoPago.dataset;
      localStorage.setItem('tipos_pagos', JSON.stringify([...tiposPagos, { id: tipoPagoId, nombre: tipoPagoNombre }]));
    });

  // inicializando los steps con jquery steps
  $("#wizard").steps({
    headerTag: "h3",
    bodyTag: "section",
    transitionEffect: "slideLeft",
    stepsOrientation: "vertical",
    labels: {
      finish: "Aceptar",
      next: "Siguiente",
      previous: "Regresar",
    },
    onStepChanging: function(e, currentIndex, newIndex) {
      const tipoPago = JSON.parse(localStorage.getItem('tipo_pago'));
      const tiposPagos = JSON.parse(localStorage.getItem('tipos_pagos'));

      // step 1 hacia el step 2
      if (currentIndex === 0 && newIndex > currentIndex) {
        if (tipoPago) {
          const tipoPagoSeleccionado = tiposPagos.find(tipo => +tipo.id === tipoPago)

          if (tipoPagoSeleccionado) {
            const { nombre } = tipoPagoSeleccionado;
            if (nombre.toLowerCase() === 'matricula') {
              $('#agregar-alumno').show();
              $('#agregar-alumno').on('click', () => {
                $('#alumno-form').show();
                $('#buscar-alumno').autocomplete('close').val('');
                localStorage.setItem('alumno', '');
              });
            } else {
              $('#agregar-alumno').hide();
            }
          }
        }
        return !!tipoPago;
      }

      // step 2 hacia el step 3
      if (currentIndex === 1 && newIndex > currentIndex) {
        const tipoPagoSeleccionado = tiposPagos.find(tipo => +tipo.id === tipoPago);
        const { nombre } = tipoPagoSeleccionado;
        const alumno = localStorage.getItem('alumno');

        // llenando campos seleccionados previamente
        $('#id_tipo_pago').val(nombre);
        if (alumno) {
          const { label } = JSON.parse(alumno);
          $('#id_alumno').val(label);
        }

        // revisando si es una mensualidad para mostrar solvencia mes
        nombre.toLowerCase() !== 'mensualidad' && $('#id_solvencia_mes').parent().hide();
        $('#id_solvencia_mes').attr('checked', true);
        return !!alumno;
      }

      // step 3 hacia el step final
      if (currentIndex === 2 && newIndex > currentIndex) {
        guardarPago();
      }

      // permitir regresar ó avanzar
      return true;
    },
    onFinished: function(e, currentIndex) {
      window.location.href = '/pago';
    }
  });

  // evento para seleccionar tipo de pago
  $('input[name="purpose"]').on("click", function() {
    const tipoPagoSeleccionado = $('input[name="purpose"]:checked').val();
    localStorage.setItem('tipo_pago', tipoPagoSeleccionado);
  });

  // auto complete de alumnos
  $("#buscar-alumno").autocomplete({
    minLength: 3,
    source: function(request, response) {
      $.ajax({
          url: '/pagos/alumnos',
          type: "GET",
          dataType: "json",
          data: {
            filtrar: request.term
          },
          success: function(data) {
            const { alumnos } = data;
            const listaAlumnos = JSON.parse(alumnos);
            response($.map(listaAlumnos, function ({ id, nombres, apellidos }) {
                return {
                  id: id,
                  value: `${nombres} ${apellidos}`
                }
            }))
          }
      })
    },
    select: function (_, selected) {
      $('#alumno-form').hide();
      const { item } = selected;
      localStorage.setItem('alumno', JSON.stringify(item));
    }
  });

  // revisar valores persistidos al recargar la pagina
  const tipoPagoPersistido = localStorage.getItem('tipo_pago')
  tipoPagoPersistido && $(`#${tipoPagoPersistido}_input_radio`).attr("checked", true);
  const alumnoPersistido = localStorage.getItem('alumno');
  alumnoPersistido && $('#buscar-alumno').autocomplete('close').val(JSON.parse(alumnoPersistido).value);
});

// guardar nuevo alumno
function guardarAlumno() {
  const alumnoForm = $("#alumno-form");
  const formData = new FormData(alumnoForm[0]);
  $.ajax({
    url: '/alumno_add/',
    type: "POST",
    processData: false,
    contentType: false,
    dataType: "json",
    beforeSend: function(request) {
      const csrftoken = getCookie('csrftoken');
      request.setRequestHeader("X-CSRF-TOKEN", csrftoken);
    },
    data: formData,
    success: function(response) {
      if (response.success) {
        $('#alumno-form').hide();
        Swal.fire({
          icon: 'success',
          title: 'Alumno creado exitosamente!',
          showConfirmButton: false,
          timer: 3000
        });
        // $("#alumno-creado").fadeTo(2000, 500).slideUp(500, function(){
        //   $("#alumno-creado").slideUp(500);
        // });
        // auto seleccionar nuevo estudiante creado
        const { id, nombres, apellidos } = response.alumno;
        const nombreCompleto = `${nombres} ${apellidos}`;
        $('#buscar-alumno').autocomplete('close').val(nombreCompleto);
        localStorage.setItem('alumno', JSON.stringify({id, label: nombreCompleto, value: nombreCompleto}));
      }
    }
  });
}

// guardar nuevo pago
function guardarPago() {
  const alumnoForm = $("#pago-form");
  const formData = new FormData(alumnoForm[0]);

  // sobrescribiendo valores que entienda el servidor
  const tipoPago = JSON.parse(localStorage.getItem('tipo_pago'));
  const alumno = JSON.parse(localStorage.getItem('alumno'));
  formData.append('tipo_pago', tipoPago);
  formData.append('alumno', alumno.id);
  // para revisar que lleva el form data
  // for (const pair of formData.entries()) {
  //   console.log(pair[0], pair[1]);
  // }

  $.ajax({
    url: '/pago_add/',
    type: "POST",
    processData: false,
    contentType: false,
    dataType: "json",
    beforeSend: function(request) {
      const csrftoken = getCookie('csrftoken');
      request.setRequestHeader("X-CSRF-TOKEN", csrftoken);
    },
    data: formData,
    success: function(response) {
      if (response.success) {
        Swal.fire({
          icon: 'success',
          title: 'Pago creado exitosamente!',
          showConfirmButton: false,
          timer: 3000
        });
      }
    }
  });
}