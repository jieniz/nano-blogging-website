function populateList() {
    $.get("/grumblr/update")
      .done(function(data) {
          var list = $("#post-list");
          list.data('max-time', data['max-time']);
          list.html('')
          // call getUpdates() function
          getUpdates();
          for (var i = 0; i < data.posts.length; i++) {
              post = data.posts[i];
              var n_post = $(post.html);
              n_post.data("post-id", post.id);
              list.prepend(n_post);
          }
      });
}

function getUpdates() {
    var list = $("#post-list")
    var max_time = list.data("max-time")
    $.get("/grumblr/update/" + max_time)
      .done(function(data) {
          list.data('max-time', data['max-time']);
          // update the posts
          for (var i = 0; i < data.posts.length; i++) {
              var post = data.posts[i];
              var n_post = $(post.html);
              n_post.data("post-id", post.id);
              list.prepend(n_post);
          }
          // update the comments
          var posts = list.children("div.post-item");
          for (var j = 0; j < posts.length; j++) {
              post = posts[j];
              updateComments(post.id);
          }
      });
}

function updateComments(id) {
    var list = $("#comment-list" + id);
    var max_time = list.data("max-time")
    $.get("/grumblr/update-comments/" + max_time + "/" + id)
      .done(function(data) {
          list.data('max-time', data['max-time']);
          for (var i = 0; i < data.comments.length; i++) {
              var comment = data.comments[i];
              var n_comment = $(comment.html);
              var max_time = list.data("max-time");
              list.append(n_comment);
          }
      });
}

function addPost(){
    var field = $("#post-field");
    $.post("/grumblr/post", {post: field.val()})
      .done(function(data) {
          getUpdates();
          field.val("").focus();
      });
}

function addComment(post_id){
    var field = $("#comment-field"+post_id);
    $.post("/grumblr/add-comment/" + post_id, {comment: field.val()})
      .done(function(data) {
          getUpdates();
      });
}

// The boilerplate code below is copied from the Django 1.10 documentation.
// It establishes the necessary HTTP header fields and cookies to use
// Django CSRF protection with jQuery Ajax requests.
$(document).ready(function () {

  populateList();
  window.setInterval(getUpdates, 5000);// set the timer to 5 seconds

  // using jQuery
  // https://docs.djangoproject.com/en/1.10/ref/csrf/
  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
  }
  var csrftoken = getCookie('csrftoken');
  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
    }
  });
});
