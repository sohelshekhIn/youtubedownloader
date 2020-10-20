
var mainWindow = document.getElementById("main")
var loading = document.getElementById("loading")
var windowHeight = mainWindow.offsetHeight;
loading.style.height =  windowHeight + "px"

function disableScroll() { 
    // Get the current page scroll position 
    scrollTop = window.pageYOffset || document.documentElement.scrollTop; 
    scrollLeft = window.pageXOffset || document.documentElement.scrollLeft, 
  
        // if any scroll is attempted, set this to the previous value 
        window.onscroll = function() { 
            window.scrollTo(scrollLeft, scrollTop); 
        }; 
} 

function enableScroll() { 
    window.onscroll = function() {}; 
} 

function navigateLoading() {
    document.getElementById("loading").style.display = "flex";
    disableScroll()
}