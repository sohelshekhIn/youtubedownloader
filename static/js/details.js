
var stream_links = document.getElementsByClassName("stream-link")
var mainWindow = document.getElementById("main")
var loading = document.getElementById("loading")
var loading_text = document.getElementsByClassName("loadingTxt")
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

for (i=0; i<stream_links.length; i++){
    stream_links[i].addEventListener("click",downloadLoading)
}

function changeLoadingText(text, ms){
    setTimeout(function(){
        loading_text[0].innerText = text
    }, ms)
}


function downloadLoading(j) {
    document.getElementById("loading").style.display = "flex";
    disableScroll()
    changeLoadingText("Processing the video... ", 10000)
    changeLoadingText("Hooo Ha", 20000)
    changeLoadingText("Asking youtube kaka to do his work phast!", 30000)
    changeLoadingText("Lagta hai video thoda bada hai, ya fir us me kuch locha hai", 40000)
    changeLoadingText("Youtube dead, Youtube dead, So we are taking huge huge huge huge time!", 50000)
}
