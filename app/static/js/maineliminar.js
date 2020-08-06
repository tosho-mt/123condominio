const btntoggle = document.querySelector('.toggle-btn');

btntoggle.addEventListener('click',function(){
    document.getElementById('sidebar').classList.toggle('active');
    document.getElementById('main').classList.toggle('activa');
});




