class CommuneListPopup extends Popup {
    constructor(csrfToken, isLoggedIn, candidateA, candidateB, communeList) {
        super(CommuneListPopup.getContent(csrfToken, isLoggedIn, candidateA, candidateB, communeList));
    }

    static getEditButton(csrfToken, candidateA, candidateB, record) {
        let edit = createElementWithContent("span", "✎ Edycja");
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
            div.appendChild(createElementWithContent("p", "Lista pusta"));
        }
        for (let record of communeList) {
            let row = document.createElement("tr");
            table.appendChild(row);
            var communeName = createElementWithContent("td", record['communeName']);
            if (isLoggedIn) {
                let edit = CommuneListPopup.getEditButton(csrfToken, candidateA, candidateB, record);
                communeName.appendChild(document.createTextNode(" "));
                communeName.appendChild(edit);
            }
            row.appendChild(communeName);
            row.appendChild(createElementWithContent("td", record['resultCandidateA']));
            row.appendChild(createElementWithContent("td", record['resultCandidateB']));
        }
        div.appendChild(table);
        return div;
    }
}
