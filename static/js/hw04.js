const story2Html = story => {
    return `
        <div>
            <img src="${ story.user.thumb_url }" class="pic" alt="profile pic for ${ story.user.username }" />
            <p>${ story.user.username }</p>
        </div>
    `;
};

// fetch data from your API endpoint:
const displayStories = () => {
    fetch('/api/stories')
        .then(response => response.json())
        .then(stories => {
            const html = stories.map(story2Html).join('\n');
            document.querySelector('.stories').innerHTML = html;
        })
};

const likeUnlike = ev => {
    // console.log('button clicked');
    const elem = ev.currentTarget;
    if (elem.innerHTML.includes('far')) {
        createLike(elem.dataset.postId, elem);
    } else {
        deleteLike(elem.dataset.likeId, elem.dataset.postId, elem);
    }
};

const createLike = (postId, elem) => {
    // console.log('creating like');
    var likes = ++elem.dataset.likesLength;
    // can create a separate id for the like number with post id or 
    // should try using fetch right now
    fetch(`/api/posts/${ postId }/likes`, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-TOKEN': '036cde10-1164-4da8-872a-1d53a634538b'
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        elem.setAttribute('data-like-id', data.id);
        elem.setAttribute('aria-checked', 'true');
        elem.innerHTML = "<i class='fas fa-heart'></i>";
        document.querySelector(`#s${ postId }`).innerHTML = `<strong>${ likes } like${ likes !== 1 ? 's' : ''}</strong>`;
    });
};

const deleteLike = (likeId, postId, elem, ) => {
    // console.log('deleting like');
    var likes = --elem.dataset.likesLength;
    const deleteURL = `/api/posts/${ postId }/likes/${ likeId }`;
    fetch(deleteURL, {
        method: "DELETE"
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        // elem.innerHTML.replace('fas', 'far');
        elem.innerHTML = "<i class='far fa-heart'></i>";
        elem.setAttribute('aria-checked', 'false');
        elem.removeAttribute('data-like-id');
        document.querySelector(`#s${ postId }`).innerHTML = `<strong>${ likes } like${ likes !== 1 ? 's' : ''}</strong>`;
    });
};

const destroyModal = postID => {
    document.querySelector('#modal-container').innerHTML = '';
    document.getElementById(`openModal-${postID}`).focus();
};

const showPostDetail = ev => {
    const postID = ev.currentTarget.dataset.postId;
    fetch(`/api/posts/${postID}`)
        .then(response => response.json())
        .then(post => {
            const html=`
                <div class="modal-bg">
                    <button onclick="destroyModal(event)" id="closeModal">
                        <i class="fas fa-times"></i>
                    </button>
                    <div class="modal">
                        <img src="${post.image_url}" />
                        <div class="modal-text">
                            <div class="modal-user-info">
                                <img src="${ post.user.thumb_url }" class="pic" alt="Profile pic for ${ post.user.username }"/>
                                <h2>${ post.user.username }</h2>
                            </div>
                            <div class="modal-comments">${displayModalComments(post.comments)}</div>
                        </div>
                    </div>
                </div>`;
        document.querySelector('#modal-container').innerHTML = html;
        document.getElementById("closeModal").focus();
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                destroyModal(postID);
            }
        })
        });
};

const displayModalComments = comments => {
    let html = ``;
    for (let comment of comments) {
        html += `
            <div class="modal-comment">
                <img src="${ comment.user.thumb_url }" alt="Profile pic for ${ comment.user.username }" />
                <p class="modal-comment-text">
                    <strong> ${ comment.user.username } </strong>
                    ${ comment.text }
                </p>
            </div>
            <p class="timestamp"> ${ comment.display_time } </p>
        `;
    }
    return html;
};

const displayComments = (comments, postID) => {
    let result = `<div class="comments">`;
    if (comments.length > 1) {
        result += `
            <p>
                <button class="link" data-post-id="${ postID }" onclick="showPostDetail(event)" id="openModal-${postID}"> 
                    View all ${comments.length} comments 
                </button>
            </p>
        `;
    }
    if (comments && comments.length > 0) {
        const lastComment = comments[comments.length - 1];
        result += `
            <p>
                <strong> ${ lastComment.user.username } </strong>
                ${ lastComment.text }
                <p class="timestamp"> ${ lastComment.display_time } </p>
            </p>
        `;
    }
    result += '</div>'
    return result;
};

const toggleBookmark = ev => {
    // console.log('bookmark clicked');
    const elem = ev.currentTarget;
    if (elem.innerHTML.includes('far')) {
        createBookmark(elem.dataset.postId, elem);
    } else {
        deleteBookmark(elem.dataset.bookmarkId, elem);
    }
};

const createBookmark = (postId, elem) => {
    const bookmarkData = {
        "post_id": postId
    }
    console.log(postId);
    fetch('/api/bookmarks/', {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-TOKEN': '036cde10-1164-4da8-872a-1d53a634538b'
        },
        body: JSON.stringify(bookmarkData)
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        elem.innerHTML = '<i class="fas fa-bookmark"></i>';
        elem.setAttribute('data-bookmark-id', data.id);
        elem.setAttribute('aria-checked', 'true');
    })
};

const deleteBookmark = (bookmarkId, elem) => {
    fetch(`/api/bookmarks/${ bookmarkId }`, {
        method: "DELETE"
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        elem.innerHTML = '<i class="far fa-bookmark"></i>';
        elem.setAttribute('aria-checked', 'false');
        elem.removeAttribute('data-bookmark-id');
    })
};

const postComment = ev => {
    var elem = ev.currentTarget;
    var postId = elem.dataset.postId;
    var text = document.querySelector(`#text-${postId}`).value;
    const postData = {
        "post_id": postId,
        "text": text
    };
    fetch("/api/comments", {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': '221abc1c-4365-4d8b-b302-81b5025064a1'
            },
            body: JSON.stringify(postData)
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            updatePost(postId);
        });
};

// 1. Get the post data from the api endpoint which is /api/posts?limit=10
// 2. When that data arrives when the promises resolve,
//    we're going to build a bunch of HTML cards (ie) a big long string
// 3. Update the container with the HTML and put on the inside of it

const post2HTML = post => {
    return `
        <section class="card" id="post-${post.id}">
            <div class="header">
                <h3>${post.user.username}</h3>
                <i class="fa fa-dots"></i>
            </div>
            <img src=${post.image_url} alt="Image posted by ${post.user.username}" width="300" height="300">
            <div class="info">
                <div class="buttons">
                    <div>
                        <button 
                            onclick="likeUnlike(event)" 
                            data-likes-length="${ post.likes.length }" 
                            data-post-id="${ post.id }" 
                            ${ post.current_user_like_id ? `data-like-id="${ post.current_user_like_id }"` : "" }
                            aria-label="like"
                            aria-checked= ${ post.current_user_like_id ? "true" : "false" }
                            >
                                <i class="fa${ post.current_user_like_id ? 's' : 'r' } fa-heart"></i>
                        </button>
                        <i class="far fa-comment"></i>
                        <i class="far fa-paper-plane"></i>
                    </div>
                    <div>
                        <button 
                            onclick="toggleBookmark(event)" 
                            data-post-id="${ post.id }" 
                            ${ post.current_user_bookmark_id ? `data-bookmark-id=${ post.current_user_bookmark_id}` : '' }
                            aria-label="bookmark"
                            aria-checked=${ post.current_user_bookmark_id ? "true" : "false" }>
                                <i class="fa${ post.current_user_bookmark_id ? 's' : 'r' } fa-bookmark"></i>
                        </button>
                    </div>
                </div>
                <p class="likes" id="s${ post.id }"><strong>${ post.likes.length } like${ post.likes.length !== 1 ? 's' : ''}</strong></p>
                <div class="caption">
                    <p>
                        <strong>${ post.user.username }</strong> 
                        ${ post.caption }
                        <p class="timestamp"> ${ post.display_time } </p>
                    </p>
                </div>
                ${ displayComments(post.comments, post.id) }
                <div class="add-comment">
                    <div class="input-holder">
                        <input id="text-${post.id}" type="text" aria-label="Add a comment" placeholder="Add a comment...">
                    </div>
                    <button onclick="postComment(event)" data-post-id="${ post.id }" data-post-comments="${ post.comments.length }" class="link">
                        Post
                    </button>
                 </div>
            </div>
        </section>
    `;
};

const updatePost = postId => {
    fetch(`/api/posts/${postId}`, {
        method: "GET",
    })
    .then(response => response.json())
    .then(post => {
        console.log(post);
        var html = post2HTML(post).replace(`<section class="card" id="post-${postId}">`, '').replace('</section>', '');
        document.querySelector(`#post-${postId}`).innerHTML = html;
    });
};

const displayPosts = () => {
    fetch('/api/posts?limit=10')
        .then(response => response.json())
        .then(posts => {
            const html = posts.map(post2HTML).join('\n');
            document.querySelector('#posts').innerHTML = html;
        })
};

const toggleFollow = ev => {
    const elem = ev.currentTarget;
    if (elem.innerHTML === 'follow') {
        // issue post request to UI for new follower
        createFollower(elem.dataset.userId, elem);
    } else {
        deleteFollower(elem.dataset.followingId, elem);
    }
}

const createFollower = (userId, elem) => {
    const postData = {
        "user_id": userId
    }
    // fetch documentation
    fetch('/api/following', {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-TOKEN': '036cde10-1164-4da8-872a-1d53a634538b'
        },
        body: JSON.stringify(postData)
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        // aria-label="Follow"
        // aria-checked="false"
        elem.setAttribute('aria-checked', 'true');
        
        elem.innerHTML = 'unfollow';
        elem.classList.add('active');
        // in the event that we want to unfollow this dude that we just followed
        elem.setAttribute('data-following-id', data.id)
    });

};

const deleteFollower = (followingId, elem) => {
    // issue a delete request
    const deleteURL = `/api/following/${ followingId }`;
    fetch(deleteURL, {
        method: "DELETE"
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        elem.innerHTML = 'follow';
        elem.classList.remove('active'); 
        elem.setAttribute('aria-checked', 'false');
        elem.removeAttribute('data-following-id');
    });
};

const user2HTML = user => {
    return `
        <section>
            <img src="${ user.thumb_url }" class="pic" alt="Profile pic for ${ user.username }" />
            <div>
                <p>${ user.username }</p>
                <p>suggested for you</p>
            </div>
            <div>
                <button 
                    class="link following" 
                    aria-label="Follow"
                    aria-checked="false"
                    data-user-id="${ user.id }" onclick="toggleFollow(event)">follow</button>
            </div>
        </section>
    `;
}

const displaySuggestions = () => {
    fetch('/api/profile')
        .then(response => response.json())
        .then(user => {
            document.querySelector('#you').innerHTML = `
                <img src="${ user.thumb_url }" class="pic" alt="Profile pic for ${ user.username }"/>
                <h2>${ user.username }</h2>
            `;
        });
    
    fetch('/api/suggestions')
        .then(response => response.json())
        .then(users => {
            // console.log(users);
            const html = users.map(user2HTML).join('\n');
            document.querySelector('#suggested-users').innerHTML = html;
        })
};

const initPage = () => {
    displayStories();
    displayPosts();
    displaySuggestions();
};

// invoke init page to display stories:
initPage();