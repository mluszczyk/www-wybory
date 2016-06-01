class ResultEditPopup extends Popup {
    static createInputRow(name, type, value, label) {
        let labelElement = document.createElement("label");
        labelElement.innerHTML = label;

        let div = document.createElement("p");
        div.appendChild(labelElement);
        div.appendChild(document.createTextNode(" "));
        div.appendChild(createInput(name, type, value));
        return div;
    }

    static getContent(csrfToken, communePk, candidateA, candidateB, resultCandidateA, resultCandidateB, modification) {
        let header = createElementWithContent("h2", "Modyfikacja wyników");
        let form = document.createElement("form");

        var errorDiv = document.createElement("div");
        errorDiv.classList.add("error-div");
        form.appendChild(errorDiv);
        form.appendChild(createInput("commune", "hidden", communePk));
        form.appendChild(createInput("candidate_a", "hidden", candidateA.pk));
        form.appendChild(createInput("candidate_b", "hidden", candidateB.pk));
        form.appendChild(createInput("csrfmiddlewaretoken", "hidden", csrfToken));
        form.appendChild(createInput("modification", "hidden", modification));
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
        jsonPromise("POST", url, data).then(function(data) {
            if (data.status === "OK") {
                console.log("Success!");
                wyniki.refreshPage();
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
        var save = createInput("button", "button", "✓ Zapisz");
        save.onclick = function () {
            ResultEditPopup.submit(save.form);
        };
        return save;
    }

    constructor(csrfToken, communePk, candidateA, candidateB, resultCandidateA, resultCandidateB, modification) {
        super(ResultEditPopup.getContent(csrfToken, communePk, candidateA, candidateB, resultCandidateA, resultCandidateB, modification));
    }
}
