const mdEditor = new SimpleMDE({
    autofocus: true,
    autosave: {
        enabled: false,
    },
    blockStyles: {
        bold: "__",
        italic: "_"
    },
    element: document.getElementById("mde-anchor"),
    forceSync: true,
    hideIcons: ["guide", "heading"],
    indentWithTabs: false,
    initialValue: "Hello world!",
    lineWrapping: false,
    parsingConfig: {
        allowAtxHeaderWithoutSpace: true,
        strikethrough: false,
        underscoresBreakWords: true,
    },
    placeholder: "Type here...",
    promptURLs: true,
    renderingConfig: {
        singleLineBreaks: false,
        codeSyntaxHighlighting: true,
    },
    shortcuts: {
        drawTable: "Cmd-Alt-T"
    },
    showIcons: ["code", "table"],
    spellChecker: false,
    status: ["autosave", "lines", "words", "cursor"],
    styleSelectedText: false,
    tabSize: 4,
    toolbarTips: true,
});


const postApiUrl = new URL(location);
postApiUrl.pathname = "/api/v1/posts";
postApiUrl.port = location.port;

const btnSubmit = document.querySelector("#btn-submit-post");
const btnReset = document.querySelector("#btn-reset");
const inpPostTitle = document.querySelector("#input-post-title");
const inpPostCategory = document.querySelector("#input-post-category");
const inpPostDescription = document.querySelector("#input-post-description");

let modalQuestion = null;
let modalInfo = null;
let modalConfirmed = false;
const btnModalConfirm = document.querySelector("#btn-modal-confirm");
const modalQuestionTitle = document.querySelector("#modal-question-title");
const modalQuestionBody = document.querySelector("#modal-question-body");
const modalInfoTitle = document.querySelector("#modal-info-title");
const modalInfoBody = document.querySelector("#modal-info-body");

btnModalConfirm.addEventListener("click", () => {
    modalConfirmed = true;
});

// document.addEventListener('DOMContentLoaded', function () {
//     modalInfo = M.Modal.init(document.querySelector('#modal-info'), null);
// });


btnSubmit.addEventListener("click", ev => {
    if (modalQuestion !== null) {
        modalQuestion.destroy();
    }
    modalQuestionTitle.innerText = "Warrning";
    modalQuestionBody.innerText = "Are you sure you want to submit this post?";
    modalQuestion = M.Modal.init(document.querySelector('#modal-question'), {onCloseEnd: _modalSubmitPost});
    modalQuestion.open();
});

btnReset.addEventListener("click", ev => {
    if (modalQuestion !== null) {
        modalQuestion.destroy();
    }
    modalQuestionTitle.innerText = "Warrning";
    modalQuestionBody.innerText = "Are you sure you want to reset your inputs?";
    modalQuestion = M.Modal.init(document.querySelector('#modal-question'), {onCloseEnd: _modalResetInputs});
    modalQuestion.open();
});

function _modalResetInputs() {
    if (modalConfirmed) {
        mdEditor.value("Hello world!");
        inpPostTitle.value = "Title";
        inpPostCategory.value = "Category";
        inpPostDescription.focus();
        inpPostDescription.value = "Description";
        inpPostDescription.blur();
        modalConfirmed = false;
    }
}

function _modalSubmitPost() {
    if (modalConfirmed) {
        const body = mdEditor.value();
        const title = inpPostTitle.value;
        const category = inpPostCategory.value;
        const description = inpPostDescription.value;

        if (body.length > 0 && title.length > 0 && category.length !== 0 && description.length !== 0) {
            axios.post(postApiUrl.href, {
                data: JSON.stringify({
                    body,
                    title,
                    category,
                    description
                })
            }).then(res => {
                console.log(res);
                const data = res.data;
                location.href = "/posts/" + data.id;

            }).then(err => console.error(err));
            console.log(title, body, category, description);
        } else {
            if (modalInfo !== null) {
                modalInfo.destroy();
            }
            modalInfoTitle.innerText = "Warrning";
            modalInfoBody.innerText = "Invalid input data";
            modalInfo = M.Modal.init(document.querySelector('#modal-info'), {});
            modalInfo.open();
        }
        modalConfirmed = false;
    }
}