from typing import Any, Dict
from django.db.models.query import QuerySet
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.views import View
from .models import Post, Comments
from .forms import CommentsForm



class StartinPageView(ListView):
    template_name = "blog/index.html"
    model = Post
    ordering = ["-date"]
    context_object_name = "posts"
    def get_queryset(self):
        queryset = super().get_queryset()  
        data = queryset[:3]
        return data     



class AllPostsView(ListView):
    template_name = "blog/all-posts.html"
    model = Post
    ordering = ["-date"]
    context_object_name = "all_posts"
    



class SinglePostView(View):

    def is_stored_post(self, request, post_id):
        stored_post = request.session.get("stored_post")
        if stored_post is not None:
            is_saved_for_later = post_id in stored_post
        else:
            is_saved_for_later = False
        return is_saved_for_later

    def get(self, request, slug):
        post = Post.objects.get(slug=slug)
        context = {
            "post" : post,
            "post_tags" : post.tag.all(),
            "comments_form": CommentsForm(),
            "comments" : post.comments.all().order_by("-id"),
            "saved_for_later" : self.is_stored_post(request, post.id)
        }
        print(context)
        return render(request, "blog/post-detail.html", context)

    def post(self, request, slug):
        comments = CommentsForm(request.POST)
        post = Post.objects.get(slug=slug)
        if comments.is_valid():
            comment=comments.save(commit=False)
            comment.post = post
            comment.save()
            return HttpResponseRedirect(reverse("post-detail-page", args=[slug]))
        context = {
                "post" : post,
                "post_tags" : post.tag.all(),
                "comments_form" : comments,
                "comments" : post.comments.all(),
                "saved_for_later" : self.is_stored_post(request, post.id)
            }
        return render(request, "blog/post-detail.html", context)



class ReadLaterView(View):
    def get(self, request):
        stored_post = request.session.get("stored_post")
        context = {}
        if stored_post is None or len(stored_post) == 0:
            context["posts"] = []
            context["has_posts"] = False
        else:
            posts = Post.objects.filter(id__in=stored_post)
            context["posts"] = posts
            context["has_posts"] = True
        return render(request, "blog/stored-posts.html", context)
    def post(self, request):
        stored_post = request.session.get("stored_post")
        if stored_post is None:
            stored_post = []
        post_id = int(request.POST["post_id"])
        if post_id not in stored_post:
            stored_post.append(post_id)
        else:
            stored_post.remove(post_id)
        request.session["stored_post"] = stored_post
        return HttpResponseRedirect("/")