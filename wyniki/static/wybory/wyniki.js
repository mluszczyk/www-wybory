class Wyniki {   // should this be wrapped in an anonymous function?
    constructor() {
        this.mapLinks();
    }

    static showPopup(text) {
        let div = document.createElement("div");
        div.classList.add("modal-popup");
        div.innerHTML = text;
        document.body.appendChild(div);
    }

    mapLinks() {
        let wyniki = this;
        let elements = document.getElementsByClassName("row-link");

        for (let i = 0; i < elements.length; ++i) {   // why for ... of doesn't work?
            let element = elements[i];
            element.onclick = function() {
                wyniki.openCommuneListPopup(
                    element.getAttribute("data-category"),
                    element.getAttribute("data-code"));
            };
        }
    }

    jsonPromise(url) {
        return new Promise(function (resolve, reject) {
            let request = new XMLHttpRequest();
            request.open('GET', url);
            request.addEventListener("load", function () {
                if (request.status == 200) {
                    resolve(JSON.parse(request.responseText));
                } else {
                    reject("Status code " + request.status)
                }
            });
            request.send();
        });
    }

    fetchCommuneList(category, code) {
        return this.jsonPromise("/commune-list/" + category + "/" + code + "/");
    }

    openCommuneListPopup(category, code) {
        let dataPromise = this.fetchCommuneList(category, code);
        dataPromise.then(function(data) {
            console.log(data);
        }).catch(function(message) {
            console.log(message);
        });
    }
}
