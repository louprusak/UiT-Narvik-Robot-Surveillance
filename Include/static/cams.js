var camList = document.getElementById("cam-list");
var camsAside = document.querySelector(".cams-aside");

var camTitle = document.getElementById("cam-title");
var camStatus = document.getElementById("cam-status");
var camVideo = document.getElementById("cam-video");

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

// Récupérer la liste des caméras
//const camList = document.getElementById('cam-list').children;
//
//// Ajouter un écouteur d'événement "click" pour chaque caméra
//for (let i = 0; i < camList.length; i++) {
//  camList[i].addEventListener('click', function(event) {
//    // Empêcher le lien d'être suivi
//    event.preventDefault();
//
//    // Récupérer les données de la caméra sélectionnée
//    const camData = JSON.parse(this.dataset.cam);
//
//    // Mettre à jour l'affichage avec les données de la caméra sélectionnée
//    document.getElementById('cam-title').textContent = camData.name;
//    document.getElementById('cam-status').className = camData.status === 'true' ? 'dot cam-active' : 'dot cam-inactive';
//    document.getElementById('cam-video').src = camData.src;
//    document.getElementById('cam-date').textContent = camData.date;
//    document.getElementById('cam-hour').textContent = camData.hour;
//  });
//}

//var camList = document.getElementById('cam-list');
//var camItems = camList.getElementsByClassName('cam-item');
//
//for (var i = 0; i < camItems.length; i++) {
//  camItems[i].addEventListener('click', function() {
//    var camData = this.getAttribute('data-cam');
//    console.log(camData);
//    var camObj = JSON.parse(camData);
//    console.log(camObj.name);
//  });
//}
