const searchBox = document.getElementById("search-box");

if (searchBox) {

    searchBox.addEventListener("keyup", function () {

        const query = searchBox.value;

        fetch(`/discover/?q=${encodeURIComponent(query)}`)

        .then(response => response.text())

        .then(html => {

            const parser = new DOMParser();

            const doc = parser.parseFromString(html, "text/html");

            const results = doc.querySelector("#movie-results");

            if (results) {

                document.querySelector("#movie-results").innerHTML =
                    results.innerHTML;

            }

        });

    });

}