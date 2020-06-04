from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.core.mail import send_mail
from .forms import EmailPostForm, CommentForm
from .models import Post, Comment
from taggit.models import Tag

#class PostListView(ListView):
#    queryset = Post.published.all()
#    context_object_name = 'posts'
#    paginate_by = 2
#    template_name = 'blog/post/list.html'

def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None
    paginator = Paginator(object_list, 3)           # 3 posts in each page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])
    
    return render(request, 'blog/post/list.html', {'page': page, 'posts': posts, 'tag':tag})


def post_share(request, post_id):
    #retrieve post by id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)                 #form is being submitted
        if form.is_valid():
            cd = form.cleaned_data                          #Form fields pass validation
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read " f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'admin@myblog.com', [cd['to']])
            sent = True                           
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post':post, 'form':form, 'sent':sent})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published', publish__year=year, publish__month=month, publish__day=day)
    comments  = post.comments.filter(active = True)       #List of active comments for this post
    new_comment = None
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False) #Create Comment object but dont save to database yet
            new_comment.post = post                        #assign the current post to the comment
            new_comment.save()
    else:
        comment_form = CommentForm()                    #creating an instance of the CommentForm class in forms.py

    return render(request, 'blog/post/detail.html', {'post':post, 'comments':comments, 'new_comment':new_comment, 'comment_form':comment_form})


#signup view here
def signup(request):
    #signup view here
    return render(request, 'blog/Signup/signup.html')