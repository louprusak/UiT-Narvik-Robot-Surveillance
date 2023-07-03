////////////////////////////////////////////////////////////////
////--------------------------------------------------------////
////   JS Script for cam page master detail for UiT Narvik  ////
////   Author : Loup RUSAK                                  ////
////--------------------------------------------------------////
////////////////////////////////////////////////////////////////

var camList = document.getElementById("cam-list");
var camsAside = document.querySelector(".cams-aside");
var camsHint = document.querySelector(".cams-hint");

var camTitle = document.getElementById("cam-title");
var camStatus = document.getElementById("cam-status");
var camVideo = document.getElementById("cam-video");

camsHint.style.display = 'block';
camsAside.style.display = 'none';

camList.addEventListener("click", function(event) {
    var target = event.target;

    //Remove previous cam status
    camStatus.classList.remove('cam-active');
    camStatus.classList.remove('cam-inactive');

    //Get element click
    if(target && target.nodeName == "A"){
        //Get data from element
        var item=JSON.parse(event.target.dataset.cam);
        //Display or not the detail div
        camsHint.style.display = item ? 'none' : 'block';
        camsAside.style.display = item ? 'block' : 'none';

        //Update detail informations
        camTitle.innerHTML = item.name;
        if(item.status === 'active'){
            camStatus.classList.add('cam-active');
        }else{
            camStatus.classList.add('cam-inactive');
        }
        camVideo.src = item.src;
    }
});

