const postApiUrl = new URL(location);
postApiUrl.pathname = "/api/v1/posts";
postApiUrl.port = "5000";
const postsUrl = new URL(location);
postsUrl.pathname = "/posts";
postsUrl.port = "5000";

const postContainer = document.querySelector("#posts-container");



window.onload = ev => {
    axios.get(postApiUrl.href).then(res => {
        const data = res.data;
        
        postContainer.innerHTML = "";
        data.posts.forEach(post => {
            postContainer.innerHTML += postTemplate(post);
        });
    }).catch(err => console.error(err))
}


function postTemplate(post) {
    return `
    <div class="row">
        <div class="col s12 m12">
            <div class="card grey darken-4">
                <div class="card-content white-text">
                    <div class="card-title row">
                        <h3 class="col m10 s12 p-2 mt-1 mb-1">
                            ${post.title}
                        </h3>       
                        <h6 class="orange-text col m2 s12 mt-0 pt-2 right-align"><small>${post.category}</small></h6>             
                    </div>
                    <p>${post.description}</p>
                </div>
                <div class="card-action white-text">
                    <div class="row mb-1">
                        <div class="col s12 m8 black-text p-1">
                            <a href="${postsUrl.href + "/" + post.id}" class="right-align">Read More</a>
                            <a href="${postsUrl.href + "/" + post.id}" class="right-align mr-0">${ post.comments.length } comments</a>
                        </div>
                        <div class="col s12 m4 white-text p-1">
                            Posted at <span class="orange-text">${post.date_posted}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>`
}