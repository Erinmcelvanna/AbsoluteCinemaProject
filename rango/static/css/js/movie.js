function getCookie(name) {

    let cookieValue = null;

    if (document.cookie && document.cookie !== '') {

        const cookies = document.cookie.split(';');

        for (let i = 0; i < cookies.length; i++) {

            const cookie = cookies[i].trim();

            if (cookie.substring(0, name.length + 1) === (name + '=')) {

                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );

                break;

            }

        }

    }

    return cookieValue;

}
const roses = document.querySelectorAll(".rose");

roses.forEach((rose, index) => {

    rose.addEventListener("click", function () {

        roses.forEach(r => r.classList.remove("active"));

        for (let i = 0; i <= index; i++) {

            roses[i].classList.add("active");

        }

    });

});


document.querySelectorAll(".fav-btn").forEach(button => {

    button.addEventListener("click", function () {

        const movieId = this.dataset.movie;

        fetch(`/add_favourite/${movieId}/`, {

            method: "POST",

            headers: {
                "X-CSRFToken": getCookie("csrftoken")
            }

        })

        .then(response => response.json())

        .then(data => {

            this.textContent = "✓ Added to Favourites";

        });

    });

});