from django.shortcuts import render , get_object_or_404
from .models import Post , Comment
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.views.generic import ListView
from .forms import EmailPostForm , CommentForm , SearchForm
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import SearchVector , SearchQuery , SearchRank
from django.contrib.postgres.search import TrigramSimilarity




def post_list(request , tag_slug=None):
    posts = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag , slug=tag_slug)
        posts = posts.filter(tags__in=[tag])
    context ={
        'posts':posts,
        'tag':tag
    
    }
    return render(request , 'blog/list.html' , context)





def post_detail(request, year , month , day , post):
    post = Post.objects.filter(publish__year=year, publish__month=month, publish__day=day, status=Post.Status.PUBLISHED).first()
    comments = post.comments.filter(active=True)
    form = CommentForm()
    post_tags_ids = post.tags.values_list('id' , flat=True) # Retrieve a python list of IDs
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id) # You get all posts that contain any of these tags, excluding the current post itself
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:4]   
    context = {
        'post': post,
        'comments':comments,
        'form':form,
        'similar_posts':similar_posts,
    }
    return render(request,'blog/detail.html' , context)





def post_share(request , post_id):
    post = get_object_or_404(Post , id=post_id , status=Post.Status.PUBLISHED)
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read " \
            f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
            f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'motazfawzy73@gmail.com',
            [cd['to']])
            sent = True
    else:
        form = EmailPostForm()        
    

    context = {
        'post':post,
        'form':form,
        'sent':sent,
    }    
    return render(request , 'blog/share.html' , context)            





@require_POST
def post_comment(request , post_id):
    post = get_object_or_404(Post , id=post_id , status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    context = {
        'post':post,
        'form':form,
        'comment':comment
    }    
    return render(request , 'blog/comment.html' , context)    



def post_search(request):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Post.published.annotate(
            similarity=TrigramSimilarity('title', query),
            ).filter(similarity__gt=0.1).order_by('-similarity')
            
    context = {
        'form':form,
        'query':query,
        'results':results,

    }        
            
    return render(request , 'blog/post/search.html' , context)        