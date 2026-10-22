
var btnSignin=document.querySelector("#signin");
var btnSignup=document.querySelector("#signup");
var body = document.querySelector("body");

btnSignin.addEventListener("click",function(){
    body.className="sign-in-js"; //Aqui estou configurando meu botão qndo ele clicar em entrar ele muda de parametro
});

btnSignup.addEventListener("click",function(){
 body.className="sign-up-js";
}); //Configuração do botão qndo eu clicar em cadastrar ele muda para a tela de cadastro

//Mensagem de cadastro "Seu cadastro foi realizado com sucesso"

var formCadastro=document.getElementById("form-cadastro");
var mensagem=document.getElementById("mensagem");

formCadastro.addEventListener("submit",function(event){
    event.preventDefault(); //Evita que a página seja recarregada ao enviar o formulário
    var campos = formCadastro.querySelectorAll("input");
    var tudoPreenchido = true;

    for(var i=0;i<campos.length; i++){
        if(campos[i].value.trim()===""){
            tudoPreenchido=false;
        }
    }
    if(tudoPreenchido){ //Aqui ele vai mostrar a minha mensagem, dependendo da ação do meu usuário
        mensagem.textContent="Usuário cadastrado";
        mensagem.style.color="green";
    }else{
        mensagem.textContent="Preencha todos os campos";
        mensagem.style.color="red";
    }
});