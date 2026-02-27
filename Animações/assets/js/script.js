// script.js
const universe = document.getElementById('universe');
const starCount = 400; // Quantidade de estrelas

// Paleta de cores para as estrelas
const colors = ['#ffffff', '#ffe9c4', '#d4fbff', '#e3e3ff', '#ffcbcb'];

function createStar() {
    const star = document.createElement('div');
    star.className = 'star';

    // Posições aleatórias em X e Y
    const x = Math.random() * window.innerWidth;
    const y = Math.random() * window.innerHeight;
    
    // Tamanhos variados para dar realismo
    const size = Math.random() * 3 + 'px';
    
    // Delay aleatório para as estrelas não virem todas juntas
    const delay = Math.random() * 4 + 's';
    
    // Escolhe uma cor aleatória da nossa paleta
    const randomColor = colors[Math.floor(Math.random() * colors.length)];

    star.style.left = `${x}px`;
    star.style.top = `${y}px`;
    star.style.width = size;
    star.style.height = size;
    star.style.animationDelay = delay;
    
    // Aplica a cor sorteada e o brilho (box-shadow)
    star.style.backgroundColor = randomColor;
    star.style.boxShadow = `0 0 6px ${randomColor}`;

    universe.appendChild(star);
}

// Gerar as estrelas
for (let i = 0; i < starCount; i++) {
    createStar();
}