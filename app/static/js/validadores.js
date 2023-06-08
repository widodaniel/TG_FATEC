function formatarCPF(cpf) {
    cpf = cpf.replace(/\D/g, ''); // Remove caracteres não numéricos

    if (cpf.length > 11) {
      cpf = cpf.slice(0, 11); // Limita o tamanho do CPF em 11 dígitos
    }

    cpf = cpf.replace(/(\d{3})(\d)/, '$1.$2'); // Adiciona o primeiro ponto
    cpf = cpf.replace(/(\d{3})(\d)/, '$1.$2'); // Adiciona o segundo ponto
    cpf = cpf.replace(/(\d{3})(\d{1,2})$/, '$1-$2'); // Adiciona o traço

    return cpf;
  }

function validarEmail() {
  var email = document.getElementById("email").value;
  var regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  
  if (!regex.test(email)) {
    Swal.fire({
      icon: 'error',
      title: 'Oops...',
      text: `Email inválido`
  });
  }
}

function formularioEnviado() {
  Swal.fire({
    icon: 'sucess',
    title: 'Boaaa...',
    text: `E-mail alterado`
});
}
