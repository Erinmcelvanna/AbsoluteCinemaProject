const roses = document.querySelectorAll(".rose");

roses.forEach((rose, index) => {

    rose.addEventListener("click", function(){

        roses.forEach(r => r.classList.remove("active"));

        for(let i = 0; i <= index; i++){
            roses[i].classList.add("active");
        }

    });

});