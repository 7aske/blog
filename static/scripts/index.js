const postApiUrl = new URL(location);
postApiUrl.pathname = "/api/v1/posts";
postApiUrl.port = location.port == 0 ? 80 : location.port;
const postsUrl = new URL(location);
postsUrl.pathname = "/posts";
postsUrl.port = location.port == 0 ? 80 : location.port;

const postContainer = document.querySelector("#posts-container");
const footer = document.querySelector("footer");

let startIndex = 0;
let postCount = 5;
let fetch = true;
let done = false;

window.onload = ev => {
    fetchPosts();
};

document.addEventListener("scroll", ev => {
    const footerPos = footer.offsetTop;
    const scrollPos = window.pageYOffset + window.innerHeight;

    if (scrollPos > footerPos && fetch === true && !done){
        fetchPosts();
    }
    console.log(footerPos);
    console.log(scrollPos)
});

function fetchPosts() {
    fetch = false;
    axios.get(postApiUrl.href + `?count=${postCount}&start=${startIndex}`).then(res => {
        const data = res.data;
        if (data.posts.length === 0) {
            done = true;
            return;
        }
        data.posts.forEach(post => {
            postContainer.innerHTML += postTemplate(post);
        });
        startIndex += postCount;
        fetch = true;
    }).catch(err => console.error(err))
}

function postTemplate(post) {
    return `
    <div class="row">
        <div class="col s12 m12">
            <div class="card grey darken-4">
                <div class="card-content white-text">
                    <div class="card-title row">
                        <a class="white-text" href="/posts/${post.id}">
                            <h3 class="col m10 s12 p-2 mt-1 mb-1">
                                ${post.title}
                            </h3>       
                            <h6 class="orange-text col m2 s12 mt-0 pt-2 right-align"><small>${post.category}</small></h6>
                        </a>             
                    </div>
                    <p>${post.description}</p>
                </div>
                <div class="card-action white-text">
                    <div class="row mb-1">
                        <div class="col s12 m6 black-text p-1">
                            <a href="${postsUrl.href + "/" + post.id}" class="right-align mr-2">Read More</a>
                            <a href="${postsUrl.href + "/" + post.id}" class="right-align mr-2">${post.comments.length} comments</a>
                            <a href="${postsUrl.href + "/" + post.id}" class="right-align mr-0">${post.votes} votes</a>
                        </div>
                        <div class="col s12 m6 grey-text right-align date-posted-container p-1">
                            Posted at <span class="orange-text">${post.date_posted}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>`
}
