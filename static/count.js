if(!localStorage.getItem('counter')){
    localStorage.setItem('counter',0);
}

function count() {
    let counter = localStorage.getItem('counter')
    counter++;
    let cartItem = document.getElementById('cart-item')
    cartItem.innerHTML = counter;
    localStorage.setItem('counter',counter)
}

document.addEventListener('DOMContentLoaded',function(){
    document.getElementById('cart-item').innerHTML = localStorage.getItem('counter')
})