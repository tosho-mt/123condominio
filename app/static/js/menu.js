$(document).ready(function(){
    $('.menu li:has(ul)').click(function(e){
        /*e.preventDefault();*/


        if ($(this).hasClass('activado')){
            $(this).removeClass('activado');
            $(this).children('ul').slideUp();                      
        }else{
            $('.menu li ul').slideUp();
            $('.menu li').removeClass('activado');
            $(this).addClass('activado');
            $(this).children('ul').slideDown();
        }
    });

    // para menu de dispositivos no implementado
    $('.btn-menu').click(function(){
        $('.sidebar .menu').slideToggle();
    });

    $(window).resize(function(){
        if ($(document).width()>450){
            $('.sidebar .menu').css({'display': 'block'});
        }
        if ($(document).width()<=450){
            $('.sidebar .menu').css({'display': 'none'});
            $('.menu li ul').slideUp();
            $('.menu li').removeClass('activado');
        }
    });

    /* oculto el menu si preciono el icono menu amburguesa y cierro todo */
    $('.toggle-btn').click(function(){
        $('.menu li ul').slideUp();
        $('.menu li').removeClass('activado');
    });

    /* desliso el menu a la derecha */
    const btntoggle = document.querySelector('.toggle-btn');

    btntoggle.addEventListener('click',function(){
        document.getElementById('sidebar').classList.toggle('active');
        document.getElementById('main').classList.toggle('activa');
    });
});