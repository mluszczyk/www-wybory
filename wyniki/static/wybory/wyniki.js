function fillInStatistics(context, data, attribute, func) {
    for (var key in data) {
        if (!data.hasOwnProperty(key)) {
            continue;
        }
        let selector = `[${attribute}='${key}']`;
        let elements = context.querySelectorAll(selector);
        for (let i = 0; i < elements.length; ++i) {
            let element = elements[i];
            func(element, data[key]);
        }
    }
}

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
    constructor(csrfToken, isLoggedIn, candidateA, candidateB, communeList) {
        super(CommuneListPopup.getContent(csrfToken, isLoggedIn, candidateA, candidateB, communeList));
    }

    static getEditButton(csrfToken, candidateA, candidateB, record) {
        let edit = Wyniki.createElement("span", "✎ Edycja");
        edit.classList.add("edit-results");
        edit.onclick = function() {
            let popup = new ResultEditPopup(csrfToken, record['communePk'], candidateA, candidateB, record['resultCandidateA'],
                record['resultCandidateB'], record['previousModification']);
            popup.show();
        };
        return edit;
    }

    static getContent(csrfToken, isLoggedIn, candidateA, candidateB, communeList) {
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
            var communeName = Wyniki.createElement("td", record['communeName']);
            if (isLoggedIn) {
                let edit = CommuneListPopup.getEditButton(csrfToken, candidateA, candidateB, record);
                communeName.appendChild(document.createTextNode(" "));
                communeName.appendChild(edit);
            }
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

    static getContent(csrfToken, communePk, candidateA, candidateB, resultCandidateA, resultCandidateB, modification) {
        let header = Wyniki.createElement("h2", "Modyfikacja wyników");
        let form = document.createElement("form");

        var errorDiv = document.createElement("div");
        errorDiv.classList.add("error-div");
        form.appendChild(errorDiv);
        form.appendChild(ResultEditPopup.createInput("commune", "hidden", communePk));
        form.appendChild(ResultEditPopup.createInput("candidate_a", "hidden", candidateA.pk));
        form.appendChild(ResultEditPopup.createInput("candidate_b", "hidden", candidateB.pk));
        form.appendChild(ResultEditPopup.createInput("csrfmiddlewaretoken", "hidden", csrfToken));
        form.appendChild(ResultEditPopup.createInput("modification", "hidden", modification));
        form.appendChild(ResultEditPopup.createInputRow("result_a", "number", resultCandidateA, `Wynik kandydata ${candidateA.name}`));
        form.appendChild(ResultEditPopup.createInputRow("result_b", "number", resultCandidateB, `Wynik kandydata ${candidateB.name}`));
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
                let user = data['user'];
                errorDiv.innerHTML = `Wyniki zostały zmodyfikowane o ${modification} przez ${user}. Kliknij zapisz ponownie, by nadpisać.`;
                form.modification.value = modification;
            } else if (data.status == "saveFailed") {
                errorDiv.innerHTML = `Suma głosów przekroczyła liczbę głosów oddanych.`;
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

    constructor(csrfToken, communePk, candidateA, candidateB, resultCandidateA, resultCandidateB, modification) {
        super(ResultEditPopup.getContent(csrfToken, communePk, candidateA, candidateB, resultCandidateA, resultCandidateB, modification));
    }
}

class Wyniki {   // should this be wrapped in an anonymous function?
    constructor(csrfToken, username, statistics) {
        this.csrfToken = csrfToken;
        this.username = username;
        this.loginBar = document.querySelector(".login-container");
        this.candidateA = statistics.candidates[0];
        this.candidateB = statistics.candidates[1];
        this.mapLinks();
        this.setLoginBar();

        fillInStatistics(document, statistics.general, "data-statistics", function(item, value) {item.innerHTML = value;});
        fillInStatistics(document, statistics.general, "data-width", function(item, value) {item.style.width = value + "%";});
        this.fillInTable(statistics.tables['voivodeship_statistics_table'], 'voivodeship-statistics-table');

    }


    createRow(rowData) {
        let rowTemplate = document.getElementById("row-template").content;
        let row = document.importNode(rowTemplate, true);
        fillInStatistics(row, rowData, "data-row-statistics", function(item, value) {item.innerHTML = value;});
        let link = row.querySelector("[data-row-link]");
        let wyniki = this;
        link.onclick = function() {
            wyniki.openCommuneListPopup(rowData['kategoria'], rowData['kod'])
        };
        if (rowData['liczba_waznych_glosow'] !== null) {
            let meterContainer = row.querySelector("[data-meter");
            meterContainer.innerHTML = `<div class="meter primary-secondary">
                <span style="width: ${rowData["procent_a_tekst"]}%"></span>
            </div>`;
        }

        return row;
    }

    fillInTable(data, tbodyId) {
        let tbody = document.getElementById(tbodyId);
        for (let i = 0; i < data.length; ++i) {
            let row = this.createRow(data[i]);
            tbody.appendChild(row);
        }

    }

    static createElement(name, content) {
        let elem = document.createElement(name);
        elem.innerHTML = content;
        return elem;
    }

    login(form) {
        let data = new FormData(form);
        let app = this;
        Wyniki.jsonPromise("POST", "/ajax-login/", data).then(function() {
            console.log("Logged in");
            app.username = form.username.value;
            app.setLoginBar();
        }).catch(function(error) {
            console.log(error);
        });
    }

    createLoginForm() {
        let csrf = ResultEditPopup.createInput("csrfmiddlewaretoken", "hidden", this.csrfToken);
        let usernameLabel = Wyniki.createElement("label", "Nazwa użytkownika");
        let username = ResultEditPopup.createInput("username", "username", "");
        let passwordLabel = Wyniki.createElement("label", "Hasło");
        let password = ResultEditPopup.createInput("password", "password", "");
        let loginForm = document.createElement("form");
        let submit = ResultEditPopup.createInput("submit", "button", "Zaloguj");
        let wyniki = this;
        submit.onclick = function() {
            let form = this.form;
            wyniki.login(form);
        };
        loginForm.appendChild(csrf);
        loginForm.appendChild(usernameLabel);
        loginForm.appendChild(document.createTextNode(" "));
        loginForm.appendChild(username);
        loginForm.appendChild(document.createTextNode(" "));
        loginForm.appendChild(passwordLabel);
        loginForm.appendChild(document.createTextNode(" "));
        loginForm.appendChild(password);
        loginForm.appendChild(submit);
        return loginForm;
    }

    setLoginBar() {
        if (this.username.length === 0) {
            this.loginBar.innerHTML = "";
            this.loginBar.appendChild(this.createLoginForm());
        } else {
            this.loginBar.innerHTML = `Dzień dobry, ${this.username}`;
        }
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
            let popup = new CommuneListPopup(app.csrfToken, app.username.length > 0,
                app.candidateA, app.candidateB, data['communeList']);
            popup.show();
        }).catch(function(message) {
            console.log(message);
        });
    }
}
