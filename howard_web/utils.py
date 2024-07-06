def agregar_icono_tipo_pago(tipo_pago):
  match tipo_pago.nombre.lower():
    case "matricula":
      tipo_pago.icono = 'fa-cash-register'
    case "mensualidad":
      tipo_pago.icono = 'fa-address-card'
    case "libros":
      tipo_pago.icono = 'fa-book'
    case _:
      tipo_pago.icono = 'fa-gear'
  return tipo_pago

def user_directory_path(instance, filename):
  return f'user_{instance.id}/{filename}'