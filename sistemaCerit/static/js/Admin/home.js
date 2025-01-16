const containerCustom = document.getElementById('container-custom');
const contentWrapper = document.getElementById('content-wrapper');
const minimizeBtn = document.getElementById('minimize-btn');
const maximizeBtn = document.getElementById('maximize-btn');
const closeBtn = document.getElementById('close-btn');
const refreshBtn = document.getElementById('refresh-btn');


let isMinimized = false;
let isMaximized = false;
let originalStyle = {
    width: contentWrapper.style.width,
    height: contentWrapper.style.height
};

minimizeBtn.addEventListener('click', () => {
    if (!isMinimized) {
        contentWrapper.classList.add('minimized');
        isMinimized = true;
    } else {
        contentWrapper.classList.remove('minimized');
        isMinimized = false;
    }
});

maximizeBtn.addEventListener('click', () => {
    if (!isMaximized) {
        contentWrapper.classList.add('maximized');
        isMaximized = true;
    } else {
        contentWrapper.classList.remove('maximized');
        contentWrapper.style.width = originalStyle.width;
        contentWrapper.style.height = originalStyle.height;
        isMaximized = false;
    }
});

closeBtn.addEventListener('click', () => {
    contentWrapper.style.display = "none";
});

refreshBtn.addEventListener('click', () => {
    location.reload(); // Recargar la página
});
