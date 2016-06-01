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

function createElementWithContent(name, content) {
    let elem = document.createElement(name);
    elem.innerHTML = content;
    return elem;
}

function jsonPromise(method, url, data) {
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

class Popup {
    constructor(element) {
        this.content = element;
    }

    show() {
        let outerDiv = document.createElement("div");
        this.outerDiv = outerDiv;
        let exit = createElementWithContent("p", "Proszę kliknąć na zewnątrz okienka, aby wyjść");
        exit.classList.add("modal-popup-exit");
        outerDiv.appendChild(exit);
        outerDiv.classList.add("modal-popup-container");
        let popup = this;
        outerDiv.onclick = function() {
            popup.close();
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

    close() {
        if (this.hasOwnProperty("outerDiv")) {
            document.body.removeChild(this.outerDiv);
            delete this.outerDiv;
        }
    }

}

function createInput(name, type, value) {
    let communeInput = document.createElement("input");
    communeInput.type = type;
    communeInput.name = name;
    communeInput.value = value;
    communeInput.required = true;
    return communeInput;
}
