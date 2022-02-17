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
    console.log('button clicked');
};

const displayComments = comments => {
    let result = '<div class="comments">';
    if (comments.length > 1) {
        result += `
            <p><button class="link"> View all ${comments.length} comments </button></p>
        `
    }
    if (comments && comments.length > 0) {
        const lastComment = comments[comments.length - 1];
        result += `
            <p>
                <strong> ${ lastComment.user.username } </strong>
                ${ lastComment.text }
                <p class="timestamp"> ${ lastComment.display_time } </p>
            </p>
        `
    }
    result += '</div>'
    return result;
};

// 1. Get the post data from the api endpoint which is /api/posts?limit=10
// 2. When that data arrives when the promises resolve,
//    we're going to build a bunch of HTML cards (ie) a big long string
// 3. Update the container with the HTML and put on the inside of it

const post2HTML = post => {
    return `
        <section class="card">
            <div class="header">
                <h3>${post.user.username}</h3>
                <i class="fa fa-dots"></i>
            </div>
            <img src=${post.image_url} alt="Image posted by ${post.user.username}" width="300" height="300">
            <div class="info">
                <div class="buttons">
                    <div>
                        <button onclick="likeUnlike(event)">
                            <i class="fa${post.current_user_like_id ? 's' : 'r'} fa-heart"></i>
                        </button>
                        <i class="far fa-comment"></i>
                        <i class="far fa-paper-plane"></i>
                    </div>
                    <div>
                        <i class="fa${ post.current_user_bookmark_id ? 's' : 'r' } fa-bookmark"></i>
                    </div>
                </div>
                <p class="likes"><strong>${ post.likes.length } like${ post.likes.length !== 1 ? 's' : ''}</strong></p>
                <div class="caption">
                    <p>
                        <strong>${ post.user.username }</strong> 
                        ${ post.caption }
                    </p>
                </div>
                ${ displayComments(post.comments) }
                <div class="add-comment">
                    <div class="input-holder">
                        <input type="text" aria-label="Add a comment" placeholder="Add a comment...">
                    </div>
                    <button class="link">Post</button>
                 </div>
            </div>
        </section>
    `;
};

/* 
<div class="comments">
                ${post.comments.length > 1 ? 
                    '<p><button class="link">View all ${post.comments.length} comments</button></p>'
                    : ''
                }
                
                {% for comment in post.get('comments')[:1] %}
                    <p>
                        <strong>{{ comment.get('user').get('username') }}</strong> 
                        {{ comment.get('text') }}
                    </p>
                {% endfor %}
                <p class="timestamp">{{ post.get('display_time') }}</p>
            </div>
        </div>
        <div class="add-comment">
            <div class="input-holder">
                <input type="text" aria-label="Add a comment" placeholder="Add a comment...">
            </div>
            <button class="link">Post</button>
        </div>
    </section>
*/
const displayPosts = () => {
    fetch('/api/posts?limit=10')
        .then(response => response.json())
        .then(posts => {
            const html = posts.map(post2HTML).join('\n');
            document.querySelector('#posts').innerHTML = html;
        })
};



const initPage = () => {
    displayStories();
    displayPosts();
};

// invoke init page to display stories:
initPage();