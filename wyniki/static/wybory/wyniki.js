class Popup {
    constructor(element) {
        this.content = element;
    }

    show() {
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
        div.appendChild(this.content);
        document.body.appendChild(outerDiv);
    }
}

class CommuneListPopup extends Popup {
    constructor(csrfToken, communeList) {
        super(CommuneListPopup.getContent(csrfToken, communeList));
    }

    static getContent(csrfToken, communeList) {
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
            let edit = Wyniki.createElement("span", "✎ Edycja");
            edit.classList.add("edit-results");
            edit.onclick = function() {
                let popup = new ResultEditPopup(csrfToken, record['communePk'], record['resultCandidateA'],
                    record['resultCandidateB'], record['previousModification']);
                popup.show();
            };
            var communeName = Wyniki.createElement("td", record['communeName']);
            communeName.appendChild(document.createTextNode(" "));
            communeName.appendChild(edit);
            row.appendChild(communeName);
            row.appendChild(Wyniki.createElement("td", record['resultCandidateA']));
            row.appendChild(Wyniki.createElement("td", record['resultCandidateB']));
        }
        div.appendChild(table);
        return div;
    }
}

class ResultEditPopup extends Popup {
    static createInput(name, type, value) {
        let communeInput = document.createElement("input");
        communeInput.type = type;
        communeInput.name = name;
        communeInput.value = value;
        communeInput.required = true;
        return communeInput;
    }

    static createInputRow(name, type, value, label) {
        let labelElement = document.createElement("label");
        labelElement.innerHTML = label;

        let div = document.createElement("p");
        div.appendChild(labelElement);
        div.appendChild(document.createTextNode(" "));
        div.appendChild(ResultEditPopup.createInput(name, type, value));
        return div;
    }

    static getContent(csrfToken, communePk, resultCandidateA, resultCandidateB, modification) {
        let header = Wyniki.createElement("h2", "Modyfikacja wyników");
        let form = document.createElement("form");

        var errorDiv = document.createElement("div");
        errorDiv.classList.add("error-div");
        form.appendChild(errorDiv);
        form.appendChild(ResultEditPopup.createInput("commune", "hidden", communePk));
        form.appendChild(ResultEditPopup.createInput("candidate_a", "hidden", 1));
        form.appendChild(ResultEditPopup.createInput("candidate_b", "hidden", 2));
        form.appendChild(ResultEditPopup.createInput("csrfmiddlewaretoken", "hidden", csrfToken));
        form.appendChild(ResultEditPopup.createInput("modification", "hidden", modification));
        form.appendChild(ResultEditPopup.createInputRow("result_a", "number", resultCandidateA, "Wynik kandydata A"));
        form.appendChild(ResultEditPopup.createInputRow("result_b", "number", resultCandidateB, "Wynik kandydata B"));
        form.appendChild(ResultEditPopup.saveButton());

        let div = document.createElement("div");
        div.appendChild(header);
        div.appendChild(form);
        return div;
    }

    static submit(form) {
        let url = "/change-results/";
        let data = new FormData(form);
        let errorDiv = form.querySelector(".error-div");
        errorDiv.innerHTML = '';
        if (!form.result_a.value || !form.result_b.value) {
            var errorNode = document.createTextNode("Proszę uzupełnić pola z wynikami.");
            errorDiv.appendChild(errorNode);
            return;
        }
        Wyniki.jsonPromise("POST", url, data).then(function(data) {
            if (data.status === "OK") {
                console.log("Success!");
                location.reload();
            } else if (data.status == "formError") {
                console.log(data['formErrors']);
            } else if (data.status == "outdatedModification") {
                let modification = data['modified'];
                errorDiv.innerHTML = `Wyniki zostały zmodyfikowane o ${modification}. Kliknij zapisz ponownie, by nadpisać.`;
                form.modification.value = modification;
            } else {
                console.log(data.status);
            }
        }).catch(function(error) {
            console.log(error);
        });
    }

    static saveButton() {
        var save = ResultEditPopup.createInput("button", "button", "✓ Zapisz");
        save.onclick = function () {
            ResultEditPopup.submit(save.form);
        };
        return save;
    }

    constructor(csrfToken, communePk, resultCandidateA, resultCandidateB, modification) {
        super(ResultEditPopup.getContent(csrfToken, communePk, resultCandidateA, resultCandidateB, modification));
    }
}

class Wyniki {   // should this be wrapped in an anonymous function?
    constructor(csrfToken) {
        this.csrfToken = csrfToken;
        this.mapLinks();
    }

    static createElement(name, content) {
        let elem = document.createElement(name);
        elem.innerHTML = content;
        return elem;
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

    static jsonPromise(method, url, data) {
        return new Promise(function (resolve, reject) {
            let request = new XMLHttpRequest();
            request.open(method, url);
            request.addEventListener("load", function () {
                if (request.status == 200) {
                    resolve(JSON.parse(request.responseText));
                } else {
                    reject("Status code " + request.status)
                }
            });
            if (!!data) {
                request.send(data);
            } else {
                request.send(data);
            }
        });
    }

    static fetchCommuneList(category, code) {
        return Wyniki.jsonPromise("GET", "/commune-list/" + category + "/" + code + "/");
    }

    openCommuneListPopup(category, code) {
        let dataPromise = Wyniki.fetchCommuneList(category, code);
        let app = this;
        dataPromise.then(function(data) {
            let popup = new CommuneListPopup(app.csrfToken, data['communeList']);
            popup.show();
        }).catch(function(message) {
            console.log(message);
        });
    }
}
