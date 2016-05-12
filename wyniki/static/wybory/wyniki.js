class Wyniki {   // should this be wrapped in an anonymous function?
    constructor() {
        this.mapLinks();
    }

    static showPopup(element) {
        let outerDiv = document.createElement("div");
        let exit = Wyniki.createElement("p", "Proszę kliknąć na zewnątrz okienka, aby wyjść");
        exit.classList.add("modal-popup-exit");
        outerDiv.appendChild(exit);
        outerDiv.classList.add("modal-popup-container");
        outerDiv.onclick = function() {
            document.body.removeChild(outerDiv);
        };
        let div = document.createElement("div");
        outerDiv.appendChild(div);
        div.onclick = function(e) {
            e.stopPropagation();
        };
        div.classList.add("modal-popup-content");
        div.appendChild(element);
        document.body.appendChild(outerDiv);
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

    static createElement(name, content) {
        let elem = document.createElement(name);
        elem.innerHTML = content;
        return elem;
    }

    static showCommuneListPopup(communeList) {
        let div = document.createElement("div");
        let header = document.createElement("h2");
        header.innerHTML = "Wyniki w wybranych gminach ";
        div.appendChild(header);
        let table = document.createElement("table");
        if (communeList.length === 0) {
            div.appendChild(Wyniki.createElement("p", "Lista pusta"));
        }
        for (let record of communeList) {
            let row = document.createElement("tr");
            table.appendChild(row);
            row.appendChild(Wyniki.createElement("td", record['communeName']));
            row.appendChild(Wyniki.createElement("td", record['resultCandidateA']));
            row.appendChild(Wyniki.createElement("td", record['resultCandidateB']));
        }
        div.appendChild(table);
        Wyniki.showPopup(div);
    }

    openCommuneListPopup(category, code) {
        let dataPromise = this.fetchCommuneList(category, code);
        dataPromise.then(function(data) {
            Wyniki.showCommuneListPopup(data['communeList']);
        }).catch(function(message) {
            console.log(message);
        });
    }
}
