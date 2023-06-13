function validateForm(event) {
    event.preventDefault(); // Impede o envio do formulário por padrão

    var form = document.getElementById("form");
    var cpfInput = document.getElementById("cpf");
    var emailInput = document.getElementById("email");
    var passwordInput = document.getElementById("password");

    var isValid = true; // Variável para rastrear a validade do formulário

    // Verificar se o campo de cpf tem menos que 11 caracteres
    if (cpfInput.length === "" || !isValidCPF(cpfInput.value)) {
        cpfInput.classList.add("error"); // Adicionar classe CSS para destacar o campo inválido
        isValid = false;
      } else {
        cpfInput.classList.remove("error"); // Remover a classe CSS se o campo for válido
      }

    // Verificar se o campo de e-mail está vazio ou não é válido
    if (emailInput.value === "" || !isValidEmail(emailInput.value)) {
      emailInput.classList.add("error"); // Adicionar classe CSS para destacar o campo inválido
      isValid = false;
    } else {
      emailInput.classList.remove("error"); // Remover a classe CSS se o campo for válido
    }

    // Verificar se o campo de senha tem menos que 8 caracteres
    if (passwordInput.length < 8) {
        passwordInput.classList.add("error"); // Adicionar classe CSS para destacar o campo inválido
        isValid = false;
      } else {
        passwordInput.classList.remove("error"); // Remover a classe CSS se o campo for válido
      }

    // Exibir mensagem de erro se o formulário não for válido
    if (!isValid) {
      var errorElement = document.createElement("div");
      errorElement.classList.add("error");
      errorElement.textContent = "Por favor, preencha os dados válidos.";
      form.appendChild(errorElement);
      console.log("Erro formulario nao e valido")
    } else {
      // O formulário é válido, pode ser enviado ou processado aqui
      form.submit();
      console.log("Enviado");
    }
  }

  // Função auxiliar para verificar o formato de e-mail usando uma expressão regular
  function isValidEmail(email) {
    var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  // Função verificar CPF
  function isValidCPF(cpf) {
    cpf = cpf.replace(/\D/g, ''); // Remove todos os caracteres não numéricos
  
    if (cpf.length !== 11) {
      return false; // Retorna falso se o CPF não tiver 11 dígitos
    }
  
    // Verifica se todos os dígitos são iguais
    if (/^(\d)\1+$/.test(cpf)) {
      return false;
    }
  
    // Calcula o primeiro dígito verificador
    var sum = 0;
    for (var i = 0; i < 9; i++) {
      sum += parseInt(cpf.charAt(i)) * (10 - i);
    }
    var mod = sum % 11;
    var digit1 = mod < 2 ? 0 : 11 - mod;
  
    // Calcula o segundo dígito verificador
    sum = 0;
    for (var j = 0; j < 10; j++) {
      sum += parseInt(cpf.charAt(j)) * (11 - j);
    }
    mod = sum % 11;
    var digit2 = mod < 2 ? 0 : 11 - mod;
  
    // Verifica se os dígitos verificadores estão corretos
    return (
      parseInt(cpf.charAt(9)) === digit1 &&
      parseInt(cpf.charAt(10)) === digit2
    );
  }

  // Função formatar CPF
  function formatCPF(cpf) {
    cpf = cpf.replace(/\D/g, ''); // Remove todos os caracteres não numéricos
  
    if (cpf.length !== 11) {
      return cpf; // Retorna o CPF sem formatação se não tiver 11 dígitos
    }
  
    // Insere os pontos e o traço nos lugares corretos
    return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
}