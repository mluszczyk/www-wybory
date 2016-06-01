class Wyniki {   // should this be wrapped in an anonymous function?
    constructor(csrfToken, username) {
        this.csrfToken = csrfToken;
        this.username = username;
        this.loginBar = document.querySelector(".login-container");
        this.setLoginBar();
        this.refreshPage();
    }

    refreshPage() {
        let wyniki = this;
        Wyniki.retrieveStatistics().then(function (statistics) {
            wyniki.fillInPage(statistics);
        });
    }

    static retrieveStatistics() {
        return jsonPromise("GET", "/result-data/");
    }

    fillInPage(statistics) {
        this.candidateA = statistics.candidates[0];
        this.candidateB = statistics.candidates[1];

        fillInStatistics(document, statistics.general, "data-statistics", function(item, value) {item.innerHTML = value;});
        fillInStatistics(document, statistics.general, "data-width", function(item, value) {item.style.width = value + "%";});

        for (var key in statistics.tables) {
            if (!statistics.tables.hasOwnProperty(key)) {
                continue;
            }
            this.fillInTable(statistics.tables[key], key);
        }
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
        if (rowData['liczba_waznych_glosow'] > 0) {
            let meterContainer = row.querySelector("[data-meter]");
            meterContainer.innerHTML = `<div class="meter primary-secondary">
                <span style="width: ${rowData["procent_a_tekst"]}%"></span>
            </div>`;
        }

        return row;
    }

    fillInTable(data, category) {
        let selector = `[data-table='${category}']`;
        let tbody = document.querySelector(selector);
        while (tbody.firstChild) {
            tbody.removeChild(tbody.firstChild);
        }
        for (let i = 0; i < data.length; ++i) {
            let row = this.createRow(data[i]);
            tbody.appendChild(row);
        }

    }

    login(form) {
        let data = new FormData(form);
        let app = this;
        jsonPromise("POST", "/ajax-login/", data).then(function() {
            console.log("Logged in");
            app.username = form.username.value;
            app.setLoginBar();
        }).catch(function(error) {
            console.log(error);
        });
    }

    createLoginForm() {
        let csrf = ResultEditPopup.createInput("csrfmiddlewaretoken", "hidden", this.csrfToken);
        let usernameLabel = createElement("label", "Nazwa użytkownika");
        let username = ResultEditPopup.createInput("username", "username", "");
        let passwordLabel = createElement("label", "Hasło");
        let password = ResultEditPopup.createInput("password", "password", "");
        let loginForm = createElement("form");
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

    static fetchCommuneList(category, code) {
        return jsonPromise("GET", "/commune-list/" + category + "/" + code + "/");
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
