const mdEditor = new SimpleMDE({
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

const mdEditorEdit = new SimpleMDE({
    autosave: {
        enabled: false,
    },
    blockStyles: {
        bold: "__",
        italic: "_"
    },
    element: document.getElementById("mde-anchor-edit"),
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
    placeholder: "",
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
postApiUrl.port = location.port == 0 ? 80 : location.port;

let startPost = 0;
let postCount = 10;

const btnSubmit = document.querySelector("#btn-submit-post");
const btnReset = document.querySelector("#btn-reset");
const inpPostTitle = document.querySelector("#input-post-title");
const inpPostCategory = document.querySelector("#input-post-category");
const inpPostDescription = document.querySelector("#input-post-description");

const btnSubmitEdit = document.querySelector("#btn-submit-post-edit");
const btnResetEdit = document.querySelector("#btn-reset-edit");
const inpPostTitleEdit = document.querySelector("#input-post-title-edit");
const inpPostCategoryEdit = document.querySelector("#input-post-category-edit");
const inpPostDescriptionEdit = document.querySelector("#input-post-description-edit");

const postList = document.querySelector("#edit-posts ul");

let modalQuestion = null;
let modalInfo = null;
let modalConfirmed = false;

const btnModalConfirm = document.querySelector("#btn-modal-confirm");
const modalQuestionTitle = document.querySelector("#modal-question-title");
const modalQuestionBody = document.querySelector("#modal-question-body");
const modalInfoTitle = document.querySelector("#modal-info-title");
const modalInfoBody = document.querySelector("#modal-info-body");

let postsState = [];
let currentPost = null;
let fetch = true;
let done = false;

let tabs = null;
document.addEventListener('DOMContentLoaded', function () {
    tabs = M.Tabs.init(document.querySelector("#creator-tabs"), null);
    fetchPosts();
});

postList.addEventListener("scroll", ev => {
    if (postList.offsetHeight + postList.scrollTop >= postList.scrollHeight) {
        fetchPosts();
    }
});

btnSubmitEdit.addEventListener("click", () => {
    if (modalQuestion !== null) {
        modalQuestion.destroy();
    }
    modalQuestionTitle.innerText = "Warning";
    modalQuestionBody.innerText = "Are you sure you want to save changes to this post?";
    modalQuestion = M.Modal.init(document.querySelector('#modal-question'), {onCloseEnd: _modalEditPost});
    modalQuestion.open();
});

btnModalConfirm.addEventListener("click", () => {
    modalConfirmed = true;
});

btnSubmit.addEventListener("click", ev => {
    if (modalQuestion !== null) {
        modalQuestion.destroy();
    }
    modalQuestionTitle.innerText = "Warning";
    modalQuestionBody.innerText = "Are you sure you want to submit this post?";
    modalQuestion = M.Modal.init(document.querySelector('#modal-question'), {onCloseEnd: _modalSubmitPost});
    modalQuestion.open();
});

btnReset.addEventListener("click", ev => {
    if (modalQuestion !== null) {
        modalQuestion.destroy();
    }
    modalQuestionTitle.innerText = "Warning";
    modalQuestionBody.innerText = "Are you sure you want to reset your inputs?";
    modalQuestion = M.Modal.init(document.querySelector('#modal-question'), {onCloseEnd: _modalResetInputs});
    modalQuestion.open();
});

btnResetEdit.addEventListener("click", ev => {
    if (modalQuestion !== null) {
        modalQuestion.destroy();
    }
    modalQuestionTitle.innerText = "Warning";
    modalQuestionBody.innerText = "Are you sure you want to reset your inputs?";
    modalQuestion = M.Modal.init(document.querySelector('#modal-question'), {onCloseEnd: _modalResetInputsEdit});
    modalQuestion.open();
});

function fetchPosts() {
    fetch = false;
    axios.get(postApiUrl.protocol + "//" + postApiUrl.host + postApiUrl.pathname + `?start=${startPost}&count=${postCount}`).then(res => {
        if (res.status === 200) {
            if (startPost === 0) {
                postList.innerHTML = "";
            }
            console.log(res);
            if (res.data.posts.length === 0) {
                done = true;
                return;
            }
            res.data.posts.forEach(post => {
                postList.innerHTML += listItemTemplate(post);
                postsState.push(post);
            });
            startPost += postCount;
        }
        fetch = true;
    }).catch(err => console.error(err));
}

function listItemTemplate(post) {
    return `<li class="collection-item avatar pr-5 pl-2">
                <span class="title truncate">${post.title}</span>
                <p class="truncate m-0">${post.description}<br>${post.id}</p>
                <div class="secondary-content">
                    <a data-id="${post.id}" onclick="_editPost(event)" class=""><i class="material-icons">edit</i></a><br>
                    <a data-id="${post.id}" onclick="_deletePost(event)" class=""><i class="material-icons">delete</i></a>
                </div>
            </li>`
}

function _editPost(ev) {
    const target = ev.target.nodeName === "I" ? ev.target.parentElement : ev.target;
    const id = target.attributes["data-id"].value;
    const post = postsState.find(p => p.id === id);
    inpPostTitleEdit.value = post.title;
    inpPostCategoryEdit.value = post.category;
    inpPostDescriptionEdit.value = post.description;
    mdEditorEdit.value(post.body);
    currentPost = post;
}

function _deletePost(ev) {
    const target = ev.target.nodeName === "I" ? ev.target.parentElement : ev.target;
    const id = target.attributes["data-id"].value;
    if (modalQuestion !== null) {
        modalQuestion.destroy();
    }
    currentPost = postsState.find(p => p.id === id);
    modalQuestionTitle.innerText = "Warning";
    modalQuestionBody.innerText = `Are you sure you want delete post with id '${id}'`;
    modalQuestion = M.Modal.init(document.querySelector('#modal-question'), {onCloseEnd: _modalDeletePost});
    modalQuestion.open();

}

function _modalEditPost() {
    if (modalConfirmed && currentPost !== null) {
        const body = mdEditorEdit.value();
        const title = inpPostTitleEdit.value;
        const category = inpPostCategoryEdit.value;
        const description = inpPostDescriptionEdit.value;

        if (body.length > 0 && title.length > 0 && category.length !== 0 && description.length !== 0) {
            axios.put(postApiUrl.protocol + "//" + postApiUrl.host + postApiUrl.pathname + "/" + currentPost.id, {
                data: JSON.stringify({
                    body,
                    title,
                    category,
                    description
                })
            }).then(res => {
                if (res.status === 201) {
                    location.reload();
                }
            }).catch(err => console.error(err));
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

function _modalResetInputsEdit() {
    if (modalConfirmed) {
        mdEditorEdit.value("Hello world!");
        inpPostTitleEdit.value = "Title";
        inpPostCategoryEdit.value = "Category";
        inpPostDescriptionEdit.focus();
        inpPostDescriptionEdit.value = "Description";
        inpPostDescriptionEdit.blur();
        modalConfirmed = false;
        currentPost = null;
    }
}

function _modalDeletePost() {
    axios.delete(postApiUrl.protocol + "//" + postApiUrl.host + postApiUrl.pathname + "/" + currentPost.id).then(res => {
        if (res.status === 200) {
            location.reload();
        }
    }).catch(err => console.error(err));
}

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
                const data = res.data;
                if (res.status === 201) {
                    location.href = "/posts/" + data.id;
                }
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
