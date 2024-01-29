import markdown
from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords_html
from django.urls import reverse_lazy
from .models import Post



class LatestPostsFeed(Feed):
    title = 'My blog'
    link = reverse_lazy('blog:post_list') # this is URL
    description = 'New posts of my blog.'

    # retrieved the last five published
    def items(self):
        return Post.published.all()[:5]
    

    def item_title(self , item):
        return item.title
    
    def item_description(self , item):
        return truncatewords_html(markdown.markdown(item.body) , 30) #30 w function to cut the description of posts after

    def item_pubdate(self , item):
        return item.publish