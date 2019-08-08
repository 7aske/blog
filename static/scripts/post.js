const postBodyMd = document.querySelector("#post-body-md");

const commentApiUrl = new URL(location);
const postApiUrl = new URL(location);
commentApiUrl.pathname = `/api/v1/posts/${commentApiUrl.pathname.split("/posts/")[1]}/comments`;
postApiUrl.pathname = `/api/v1/posts/${postApiUrl.pathname.split("/posts/")[1]}`;
commentApiUrl.port = location.port == 0 ? 80 : location.port;
postApiUrl.port = location.port == 0 ? 80 : location.port;

const commentTitle = "Leave a comment";
const commentForm = `<form class="col s12">
                    <div class="row">
                        <div class="input-field col s6">
                            <i class="material-icons prefix">account_circle</i>
                            <input id="reader-nickname" type="text" class="validate">
                            <label for="reader-nickname">Nickname</label>
                        </div>
                        <div class="input-field col s6">
                            <i class="material-icons prefix">email</i>
                            <input id="reader-email" type="email" class="validate">
                            <label for="reader-email">Email</label>
                        </div>
                    </div>
                    <div class="row">
                        <div class="input-field col s12 pl-3 pr-2">
                            <textarea id="reader-comment" class="materialize-textarea"></textarea>
                            <label for="reader-comment">Comment</label>
                        </div>
                    </div>
                </form>`;

function commentTemplate(comment) {
    return `<div class="row" id="comment-${comment.id}" data-id="${comment.id}">
            <div class="col s12">
                <div class="card white darken-1">
                    <div class="card-content black-text pt-3 pb-3">
                        <span class="card-title">${comment.author}</span>
                        <p>${comment.text}</p>
                    </div>
                </div>
            </div>
        </div>`
}


window.onload = () => {
    postBodyMd.innerHTML = marked(postBodyMd.innerHTML);
};

const btnModalFormConfirm = document.querySelector("#btn-modal-form-confirm");
const modalFormTitle = document.querySelector("#modal-form-title");
const modalFormBody = document.querySelector("#modal-form-body");

let modalForm = null;
let modalConfirmed = false;

document.addEventListener('DOMContentLoaded', function () {
    modalForm = M.Modal.init(document.querySelector('#modal-form'), {onCloseEnd: _handleFormSubmit});
    modalFormTitle.innerHTML = commentTitle;
    modalFormBody.innerHTML = commentForm;
});

btnModalFormConfirm.addEventListener("click", () => {
    modalConfirmed = true;
});

function _handleFormSubmit() {
    if (modalConfirmed === true) {
        const inpReaderNickname = document.querySelector("#reader-nickname");
        const inpReaderEmail = document.querySelector("#reader-email");
        const inpReaderComment = document.querySelector("#reader-comment");

        const author = inpReaderNickname.value;
        const email = inpReaderEmail.value;
        const text = inpReaderComment.value;

        if (author.length > 0 && email.length > 0 && text.length > 0) {
            axios.post(commentApiUrl.href, {
                data: JSON.stringify({
                    author,
                    email,
                    text
                })
            }).then(res => {
                console.log(res);
                location.reload();
            }).catch(err => console.error(err));
            modalConfirmed = false;
            modalForm.close();
        }
    }
}

function _voteHandler(ev) {
    ev.stopPropagation();
    const btn = ev.target.nodeName === "I" ? ev.target.parent : ev.target;
    const id = btn.attributes["data-id"].value;
    let delta = btn.attributes["data-delta"].value;
    if (!btn.classList.contains("disabled")) {
        btn.classList.add("disabled");
        if (delta === "1") {
            if (btn.nextElementSibling.classList.contains("disabled")) {
                btn.nextElementSibling.classList.remove("disabled");
                delta = "2";
            }
        } else if (delta === "-1") {
            if (btn.previousElementSibling.classList.contains("disabled")) {
                btn.previousElementSibling.classList.remove("disabled");
                delta = "-2";
            }
        }
    } else {
        btn.classList.remove("disabled");
        if (delta === "1") {
            delta = "-1";
        } else if (delta === "-1") {
            delta = "1";
        }
    }
    axios.post(commentApiUrl.protocol + "//" + commentApiUrl.host + commentApiUrl.pathname + "/" + id + "?" + `delta=${delta}`).then(res => {
        const data = res.data;
        console.log(data, data.votes);
        btn.parentElement.firstElementChild.firstElementChild.innerText = data.votes;

    }).catch(err => console.error(err));
}


function _votePostHandler(ev) {
    ev.stopPropagation();
    const btn = ev.target.nodeName === "I" ? ev.target.parent : ev.target;
    const id = btn.attributes["data-id"].value;
    let delta = btn.attributes["data-delta"].value;
    if (!btn.classList.contains("disabled")) {
        btn.classList.add("disabled");
        if (delta === "1") {
            if (btn.nextElementSibling.classList.contains("disabled")) {
                btn.nextElementSibling.classList.remove("disabled");
                delta = "2";
            }
        } else if (delta === "-1") {
            if (btn.previousElementSibling.classList.contains("disabled")) {
                btn.previousElementSibling.classList.remove("disabled");
                delta = "-2";
            }
        }
    } else {
        btn.classList.remove("disabled");
        if (delta === "1") {
            delta = "-1";
        } else if (delta === "-1") {
            delta = "1";
        }
    }
    axios.post(postApiUrl.protocol + "//" + postApiUrl.host + postApiUrl.pathname + "?" + `delta=${delta}`).then(res => {
        const data = res.data;
        console.log(data, data.votes);
        btn.parentElement.firstElementChild.firstElementChild.innerText = data.votes;

    }).catch(err => console.error(err));
}

